from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
from config import Config
import hashlib

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    telegram_id = Column(String(100))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Subscription
    subscription_end = Column(DateTime)
    tariff = Column(String(50))
    is_active = Column(Boolean, default=False)
    
    # Referrals
    referral_code = Column(String(50), unique=True)
    referred_by = Column(String(50))
    referrals_count = Column(Integer, default=0)
    
    # Profile
    vpn_configs = relationship('VPNConfig', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def get_days_remaining(self):
        if not self.subscription_end:
            return 0
        delta = self.subscription_end - datetime.utcnow()
        return max(0, delta.days)
    
    def generate_referral_code(self):
        import secrets
        self.referral_code = f"LUNARY{secrets.token_hex(4).upper()}"

class VPNConfig(Base):
    __tablename__ = 'vpn_configs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    config_name = Column(String(100))
    vless_url = Column(String(1000), nullable=False)
    country = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    tariff = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)

engine = create_engine(Config.DATABASE_URL, connect_args={'check_same_thread': False} if 'sqlite' in Config.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create admin if not exists
    db = SessionLocal()
    admin = db.query(User).filter_by(username=Config.ADMIN_USERNAME).first()
    if not admin:
        admin = User(
            username=Config.ADMIN_USERNAME,
            email='admin@lunaryvpn.ru',
            is_admin=True,
            subscription_end=datetime.utcnow() + timedelta(days=3650),
            tariff='lifetime',
            is_active=True
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        admin.generate_referral_code()
        db.add(admin)
        db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()