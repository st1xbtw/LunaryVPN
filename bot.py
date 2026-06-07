import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from database import init_db, get_db, User, VPNConfig
from config import Config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

# Initialize DB
init_db()

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="🔑 Мой VPN"), KeyboardButton(text="💳 Тарифы")],
        [KeyboardButton(text="📱 Инструкция"), KeyboardButton(text="💬 Поддержка")],
        [KeyboardButton(text="👥 Пригласить друга")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    
    if not user:
        # Create new user
        user = User(
            username=message.from_user.username or f"user_{message.from_user.id}",
            email=f"{message.from_user.id}@telegram.local",
            telegram_id=str(message.from_user.id)
        )
        user.generate_referral_code()
        db.add(user)
        db.commit()
    
    welcome_text = f"""
🌙 **Добро пожаловать в Lunary VPN!**

👤 Ваш ID: `{message.from_user.id}`
🔗 Реферальная ссылка: `https://t.me/{bot.username}?start={user.referral_code}`

Выберите действие:
"""
    db.close()
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(lambda message: message.text == "🔑 Мой VPN")
async def my_vpn(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    db.close()
    
    if not user:
        await message.answer("Пользователь не найден. Нажмите /start")
        return
    
    if not user.is_active or not user.subscription_end:
        await message.answer("❌ У вас нет активной подписки.\n\nВыберите тариф в меню 💳 Тарифы")
        return
    
    days_left = user.get_days_remaining()
    
    text = f"""
🌙 **Lunary VPN - Ваш профиль**

👤 Имя: {user.username}
📅 Подписка до: {user.subscription_end.strftime('%d.%m.%Y')}
⏳ Осталось дней: {days_left}
💎 Тариф: {Config.TARIFFS.get(user.tariff, {}).get('name', 'Unknown')}

📊 **Статус:** {'✅ Активен' if user.is_active else '❌ Неактивен'}
📡 Трафик: ♾️ Безлимитный
"""
    
    # Get VPN configs
    db = next(get_db())
    configs = db.query(VPNConfig).filter_by(user_id=user.id, is_active=True).all()
    db.close()
    
    if configs:
        text += f"\n🔌 **Доступные серверы:** {len(configs)}\n\n"
        for config in configs[:3]:
            text += f"• {config.config_name}\n"
        
        # Create inline keyboard with configs
        builder = InlineKeyboardBuilder()
        for config in configs:
            builder.button(text=f"🔗 {config.country}", callback_data=f"config_{config.id}")
        builder.adjust(1)
        
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

@dp.message(lambda message: message.text == "💳 Тарифы")
async def tariffs(message: types.Message):
    text = """
💎 **Тарифы Lunary VPN**

🆓 **Пробный доступ (3 дня)**
   Цена: Бесплатно!
   • Безлимитный трафик
   • Все серверы

⚡ **Суточный**
   Цена: 10₽
   • Безлимитный трафик
   • Все серверы

📅 **Неделя**
   Цена: 50₽
   • Безлимитный трафик
   • Все серверы
   • До 3 устройств

🔥 **Месяц** (Популярный!)
   Цена: 120₽
   • Безлимитный трафик
   • Все серверы
   • До 3 устройств
   • Лучшая цена!

💰 **Год** (Экономия ~70%)
   Цена: 500₽
   • Безлимитный трафик
   • Все серверы
   • До 3 устройств
   • Приоритетная поддержка

💳 Оплата: CryptoBot
🔗 Ссылка: {crypto_link}
""".format(crypto_link=Config.CRYPTOBOT_LINK)
    
    builder = InlineKeyboardBuilder()
    for tariff_key, tariff_info in Config.TARIFFS.items():
        price = "Бесплатно" if tariff_info['price'] == 0 else f"{tariff_info['price']}₽"
        builder.button(text=f"{tariff_info['name']} - {price}", 
                      callback_data=f"buy_{tariff_key}")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.message(lambda message: message.text == "📱 Инструкция")
async def instruction(message: types.Message):
    text = """
📱 **Как подключить VPN:**

1️⃣ **Купите подписку** на сайте или через бота
2️⃣ **Скачайте приложение Happ** 
   • iOS: App Store
   • Android: Google Play / APK

3️⃣ **Получите ссылку** в разделе "Мой VPN"
4️⃣ **Импортируйте** ссылку в Happ:
   • Нажмите "+" в приложении
   • Вставьте ссылку
   • Нажмите "Подключиться"

5️⃣ **Готово!** 🎉

💡 Советы:
• Используйте разные серверы для лучшей скорости
• При проблемах обратитесь в поддержку
"""
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda message: message.text == "💬 Поддержка")
async def support(message: types.Message):
    text = f"""
💬 **Техническая поддержка**

📞 Свяжитесь с нами:
• Telegram: {Config.SUPPORT_LINK}
• Время работы: 24/7

⚡ Среднее время ответа: 5-15 минут

📧 По вопросам:
• Оплаты
• Подключения
• Технических проблем
• Сотрудничества
"""
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda message: message.text == "👥 Пригласить друга")
async def referrals(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
    db.close()
    
    if not user:
        await message.answer("Пользователь не найден. Нажмите /start")
        return
    
    text = f"""
👥 **Реферальная программа**

🔗 Ваша ссылка:
`https://t.me/{bot.username}?start={user.referral_code}`

📊 Статистика:
• Приглашено друзей: {user.referrals_count}
• Бонусных дней: {user.referrals_count * 3}

🎁 **Бонусы:**
• +3 дня VPN за каждого друга
• Друг также получает бонус при регистрации

💡 Как это работает:
1. Отправьте ссылку другу
2. Друг регистрируется по ссылке
3. Вы оба получаете +3 дня!
"""
    await message.answer(text, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.startswith('buy_'))
async def buy_tariff(callback: types.CallbackQuery):
    tariff = callback.data.split('_')[1]
    tariff_info = Config.TARIFFS.get(tariff)
    
    if not tariff_info:
        await callback.answer("Неверный тариф", show_alert=True)
        return
    
    text = f"""
💳 **Покупка тарифа**

📦 Тариф: {tariff_info['name']}
💰 Цена: {tariff_info['price']}₽
⏳ Срок: {tariff_info['days']} дн.

💳 **Способ оплаты:**
1. Перейдите по ссылке:
{Config.CRYPTOBOT_LINK}

2. Оплатите {tariff_info['price']}₽

3. После оплаты подписка активируется автоматически!

⏱️ Активация: 1-5 минут
"""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить сейчас", url=Config.CRYPTOBOT_LINK)
    builder.button(text="🔙 Назад", callback_data="back_to_menu")
    builder.adjust(1)
    
    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith('config_'))
async def get_config(callback: types.CallbackQuery):
    config_id = int(callback.data.split('_')[1])
    
    db = next(get_db())
    config = db.query(VPNConfig).filter_by(id=config_id).first()
    db.close()
    
    if config:
        text = f"""
🔌 **Конфигурация VPN**

📍 {config.config_name}

🔗 **Ссылка для импорта:**
`{config.vless_url}`

📱 **Приложение:** Happ
"""
        await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == 'back_to_menu')
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_start(callback.message)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())