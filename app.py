from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import random
from database import init_db, get_db, User, VPNConfig, Payment
from config import Config
import os

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize database
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        db = next(get_db())
        user = db.query(User).filter_by(id=session['user_id']).first()
        db.close()
        if not user or not user.is_admin:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', tariffs=Config.TARIFFS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
    return render_template('support.html', support_link=Config.SUPPORT_LINK)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        referral_code = request.form.get('referral_code')
        
        db = next(get_db())
        
        # Check if user exists
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            flash('Пользователь уже существует', 'error')
            db.close()
            return render_template('register.html')
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        user.generate_referral_code()
        
        # Handle referral
        if referral_code:
            referrer = db.query(User).filter_by(referral_code=referral_code).first()
            if referrer:
                user.referred_by = referral_code
                referrer.referrals_count += 1
                # Add 3 days to referrer
                if referrer.subscription_end:
                    referrer.subscription_end += timedelta(days=3)
                else:
                    referrer.subscription_end = datetime.utcnow() + timedelta(days=3)
        
        db.add(user)
        db.commit()
        db.close()
        
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = next(get_db())
        user = db.query(User).filter_by(username=username).first()
        db.close()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = next(get_db())
    user = db.query(User).filter_by(id=session['user_id']).first()
    
    if not user:
        db.close()
        return redirect(url_for('logout'))
    
    configs = db.query(VPNConfig).filter_by(user_id=user.id).all()
    db.close()
    
    return render_template('dashboard.html', 
                         user=user, 
                         configs=configs, 
                         tariffs=Config.TARIFFS,
                         crypto_link=Config.CRYPTOBOT_LINK)

@app.route('/payment/<tariff>', methods=['GET', 'POST'])
@login_required
def payment(tariff):
    if tariff not in Config.TARIFFS:
        flash('Неверный тариф', 'error')
        return redirect(url_for('dashboard'))
    
    tariff_info = Config.TARIFFS[tariff]
    
    if request.method == 'POST':
        db = next(get_db())
        user = db.query(User).filter_by(id=session['user_id']).first()
        
        # Create payment record
        payment = Payment(
            user_id=user.id,
            amount=tariff_info['price'],
            tariff=tariff
        )
        db.add(payment)
        
        # Activate subscription
        if tariff == 'trial':
            user.subscription_end = datetime.utcnow() + timedelta(days=tariff_info['days'])
        else:
            # For paid subscriptions, extend from current or now
            if user.subscription_end and user.subscription_end > datetime.utcnow():
                user.subscription_end += timedelta(days=tariff_info['days'])
            else:
                user.subscription_end = datetime.utcnow() + timedelta(days=tariff_info['days'])
        
        user.tariff = tariff
        user.is_active = True
        
        # Generate VPN configs
        selected_configs = random.sample(Config.VLESS_CONFIGS, min(3, len(Config.VLESS_CONFIGS)))
        countries = ['🇳 Netherlands', '🇬🇧 Great Britain', '🇫🇮 Finland', 
                    '🇪🇪 Estonia', '🇨 Switzerland', '🇰 Kazakhstan', '🇷🇺 Russia']
        
        for i, config in enumerate(selected_configs):
            vpn_config = VPNConfig(
                user_id=user.id,
                config_name=f"Lunary VPN - {countries[i]}",
                vless_url=config,
                country=countries[i]
            )
            db.add(vpn_config)
        
        db.commit()
        db.close()
        
        flash('Подписка активирована! Проверьте раздел VPN конфигурации.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('payment.html', tariff=tariff, tariff_info=tariff_info, 
                         crypto_link=Config.CRYPTOBOT_LINK)

@app.route('/admin')
@admin_required
def admin_panel():
    db = next(get_db())
    users = db.query(User).all()
    payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(20).all()
    db.close()
    
    return render_template('admin.html', users=users, payments=payments)

@app.route('/api/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
    db.close()
    return jsonify({'success': True})

@app.route('/referral/<code>')
def referral(code):
    session['referral_code'] = code
    flash('Реферальный код применен! Зарегистрируйтесь, чтобы получить бонус.', 'success')
    return redirect(url_for('register'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)