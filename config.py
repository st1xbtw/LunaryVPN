import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///lunary_vpn.db')
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8947878685:AAHFunrFmxquIeI8bFafce1Q002WGQ8WvTw')
    ADMIN_ID = int(os.environ.get('ADMIN_ID', '873067495'))
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # VLESS Configurations
    VLESS_CONFIGS = [
        "vless://f5f78ea0-1c46-49cc-b1dd-401495eee583@nld-0001.api.packet-drop-society.net:443?encryption=none&type=xhttp&path=%2Fassets%2Fv2%2Fpkg&mode=auto&security=reality&sni=sstats.vk-portal.net&fp=qq&pbk=mLmBhbVFfNuo2eUgBh6r9-5Koz9mUCn3aSzlR6IejUg&sid=8453e5fd9af927&spx=%2F#%F0%9F%87%B3%F0%9F%87%B1%20Netherlands",
        "vless://f5f78ea0-1c46-49cc-b1dd-401495eee583@gbr-0001.api.aiagentsbase.link:443?encryption=none&type=xhttp&path=%2Fassets%2Fv2%2Fpkg&mode=auto&security=reality&sni=sstats.vk-portal.net&fp=qq&pbk=mLmBhbVFfNuo2eUgBh6r9-5Koz9mUCn3aSzlR6IejUg&sid=8453e5fd9af927&spx=%2F#%F0%9F%87%AC%F0%9F%87%A7%20Great%20Britain%20Fast%20noP2P",
        "vless://f5f78ea0-1c46-49cc-b1dd-401495eee583@fin-0001.api.aiagentsbase.link:443?encryption=none&type=xhttp&path=%2Fassets%2Fv2%2Fpkg&mode=auto&security=reality&sni=sstats.vk-portal.net&fp=qq&pbk=mLmBhbVFfNuo2eUgBh6r9-5Koz9mUCn3aSzlR6IejUg&sid=175d&spx=%2F#%F0%9F%87%AB%F0%9F%87%AE%20Finland%20Fast%20noP2P",
        "vless://f5f78ea0-1c46-49cc-b1dd-401495eee583@est-0001-mke01.packet-drop-society.net:48002?encryption=none&type=kcp&security=none&fm=%7B%22udp%22%3A%5B%7B%22type%22%3A%22header-dns%22%2C%22settings%22%3A%7B%22domain%22%3A%22www.google.com%22%7D%7D%2C%7B%22type%22%3A%22mkcp-aes128gcm%22%2C%22settings%22%3A%7B%22password%22%3A%22QrzBboLHMKIz20mg3xkZPe5uC3aSfCbA%22%7D%7D%5D%7D#%F0%9F%87%AA%F0%9F%87%AA%20Estonia-MS",
        "vless://f5f78ea0-1c46-49cc-b1dd-401495eee583@che-0001-mk01.packet-drop-society.net:48001?encryption=none&type=kcp&security=none&fm=%7B%22udp%22%3A%5B%7B%22type%22%3A%22header-srtp%22%7D%5D%7D#%F0%9F%87%A8%F0%9F%87%AD%20Switzerland%20%7C%20mKCP",
        "vless://f31effa1-6e73-4e11-a1fb-f34112a13837@kaz-0001-mk01.packet-drop-society.net:48001?encryption=none&type=kcp&security=none&fm=%7B%22udp%22%3A%5B%7B%22type%22%3A%22header-srtp%22%7D%5D%7D#%F0%9F%87%B0%F0%9F%87%BF%20Kazakhstan-M",
        "vless://8cfc0185-89d1-4203-8494-1d711d37611b@85.198.83.51:443?flow=xtls-rprx-vision&type=tcp&headerType=none&security=reality&fp=chrome&sni=haharu4.xixihaha.it.com&pbk=HNC4xdL0kgaIcgnPtMyc21hxY6dk0zl_vAclmQZHigw&sid=0fd130e2#%F0%9F%87%B7%F0%9F%87%BAYT%20%D0%B1%D0%B5%D0%B7%20%D1%80%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D1%8B",
        "vless://99e57b69-1666-4d67-8696-bb9c11509caa@158.160.169.35:8443?flow=xtls-rprx-vision&type=tcp&headerType=none&security=reality&fp=chrome&sni=ads.x5.ru&pbk=sOpiBrQalOjwU2x6qteaIBFpmalPX5bLOim6ZyeYtmk&sid=e47d831c8c93a08c&spx=/#%F0%9F%87%AA%F0%9F%87%BA%D0%91%D0%B5%D0%BB%D1%8B%D0%B5%20%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B8%202",
        "vless://5bf6cbea-20fb-4959-bb47-a33c6f3ef399@158.160.169.35:443?flow=xtls-rprx-vision&type=tcp&headerType=none&security=reality&fp=chrome&sni=max.ru&pbk=9HPyivulmZuC6Ff0-CC1UxvouysUi6G8OVW22qGWwVs&sid=8e94850c1a025b50&spx=/#%F0%9F%87%AA%F0%9F%87%BA%D0%91%D0%B5%D0%BB%D1%8B%D0%B5%20%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B8%201"
    ]
    
    # Tariffs
    TARIFFS = {
        'trial': {'days': 3, 'price': 0, 'name': 'Пробный доступ', 'devices': 1},
        'daily': {'days': 1, 'price': 10, 'name': 'Суточный', 'devices': 1},
        'week': {'days': 7, 'price': 50, 'name': 'Неделя', 'devices': 3},
        'month': {'days': 30, 'price': 120, 'name': 'Месяц', 'devices': 3, 'popular': True},
        'year': {'days': 365, 'price': 500, 'name': 'Год', 'devices': 3, 'discount': '70%'}
    }
    
    # Payment
    CRYPTOBOT_LINK = "http://t.me/send?start=IVvpLFJweews"
    SUPPORT_LINK = "https://t.me/LunaryVPN"