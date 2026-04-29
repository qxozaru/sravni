"""
python manage.py seed
~90 реальных товаров с гарантированно работающими изображениями.

Для изображений используется DummyJSON Image API — генерирует
placeholder-картинку с названием товара. Изображения ГАРАНТИРОВАННО
загружаются в любом браузере без ключей и блокировок.

Если у вас есть реальные фото товаров — просто замените URL
в словаре IMAGES или загрузите через админку Django.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Category, Store, Product, Price, UserProfile
from decimal import Decimal
import random
import urllib.parse


def product_img(name, fg='333333', w=400, h=400):
    """Генерирует URL placeholder-изображения с названием товара на белом фоне."""
    text = urllib.parse.quote_plus(name[:40])
    return f'https://dummyjson.com/image/{w}x{h}/ffffff/{fg}?text={text}&fontSize=18&fontFamily=poppins'


class Command(BaseCommand):
    help = 'Наполнение БД ~90 реалистичными товарами'

    def handle(self, *args, **options):
        self.stdout.write('Создание данных...')

        # ── Категории ──────────────────────────
        cats = {}
        for name, slug, icon in [
            ('Смартфоны', 'smartphones', '📱'),
            ('Ноутбуки', 'laptops', '💻'),
            ('Телевизоры', 'tv', '📺'),
            ('Наушники', 'headphones', '🎧'),
            ('Планшеты', 'tablets', '📟'),
            ('Фотоаппараты', 'cameras', '📷'),
            ('Игровые консоли', 'consoles', '🎮'),
            ('Бытовая техника', 'appliances', '🏠'),
            ('Умные часы', 'smartwatches', '⌚'),
            ('Аксессуары', 'accessories', '🔌'),
        ]:
            obj, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})
            cats[slug] = obj

        # ── Магазины ───────────────────────────
        stores_data = [
            ('DNS', 'dns', 'https://www.dns-shop.ru', '#FF6600',
             'г. Красноярск, ул. Весны 1'),
            ('М.Видео', 'mvideo', 'https://www.mvideo.ru', '#E40046',
             'г. Красноярск, ул. 9 Мая 77'),
            ('Ситилинк', 'citilink', 'https://www.citilink.ru', '#00AEEF',
             'г. Красноярск, ул. Партизана Железняка 23'),
            ('Эльдорадо', 'eldorado', 'https://www.eldorado.ru', '#6B2D8B',
             'г. Красноярск, ТЦ Планета'),
        ]
        stores = []
        for name, slug, web, color, addr in stores_data:
            s, _ = Store.objects.get_or_create(slug=slug, defaults={
                'name': name, 'website': web, 'color': color,
                'logo_url': '',
                'address': addr,
                'description': f'Магазин электроники и бытовой техники {name}',
            })
            stores.append(s)

        # ── Товары ─────────────────────────────
        products_data = [
            # (name, slug, brand, category_slug, base_price, description)
            # === Смартфоны ===
            ('Apple iPhone 15 128GB', 'iphone-15-128gb', 'Apple', 'smartphones', 79990,
             'Дисплей 6.1" Super Retina XDR, чип A16 Bionic, камера 48 Мп, USB-C'),
            ('Apple iPhone 15 Pro 256GB', 'iphone-15-pro-256gb', 'Apple', 'smartphones', 119990,
             'Дисплей 6.1" OLED 120Hz, чип A17 Pro, камера 48+12+12 Мп, титан'),
            ('Apple iPhone 14 128GB', 'iphone-14-128gb', 'Apple', 'smartphones', 59990,
             'Дисплей 6.1" OLED, чип A15 Bionic, камера 12+12 Мп'),
            ('Samsung Galaxy S24 Ultra 256GB', 'samsung-s24-ultra', 'Samsung', 'smartphones', 109990,
             'Дисплей 6.8" Dynamic AMOLED 2X 120Hz, Snapdragon 8 Gen 3, камера 200 Мп, S-Pen'),
            ('Samsung Galaxy S24 128GB', 'samsung-s24-128gb', 'Samsung', 'smartphones', 69990,
             'Дисплей 6.2" AMOLED 120Hz, Exynos 2400, камера 50+12+10 Мп'),
            ('Samsung Galaxy A55 128GB', 'samsung-a55', 'Samsung', 'smartphones', 32990,
             'Дисплей 6.6" Super AMOLED 120Hz, Exynos 1480, камера 50+12+5 Мп'),
            ('Samsung Galaxy A35 128GB', 'samsung-a35', 'Samsung', 'smartphones', 24990,
             'Дисплей 6.6" Super AMOLED 120Hz, Exynos 1380, камера 50+8+5 Мп'),
            ('Xiaomi 14 256GB', 'xiaomi-14', 'Xiaomi', 'smartphones', 54990,
             'Дисплей 6.36" AMOLED 120Hz, Snapdragon 8 Gen 3, Leica 50+50+50 Мп'),
            ('Xiaomi Redmi Note 13 Pro', 'redmi-note-13-pro', 'Xiaomi', 'smartphones', 24990,
             'Дисплей 6.67" AMOLED 120Hz, Snapdragon 7s Gen 2, камера 200 Мп'),
            ('Xiaomi Redmi 13 128GB', 'redmi-13', 'Xiaomi', 'smartphones', 12990,
             'Дисплей 6.79" IPS 90Hz, Snapdragon 685, камера 108 Мп'),
            ('HONOR Magic6 Pro 512GB', 'honor-magic6-pro', 'HONOR', 'smartphones', 69990,
             'Дисплей 6.78" LTPO OLED 120Hz, Snapdragon 8 Gen 3'),
            ('Google Pixel 8 128GB', 'pixel-8', 'Google', 'smartphones', 54990,
             'Дисплей 6.2" OLED 120Hz, Tensor G3, камера 50+12 Мп'),
            ('realme 12 Pro+ 256GB', 'realme-12-pro-plus', 'realme', 'smartphones', 34990,
             'Дисплей 6.7" AMOLED 120Hz, перископная камера 64 Мп'),
            ('POCO X6 Pro 256GB', 'poco-x6-pro', 'POCO', 'smartphones', 27990,
             'Дисплей 6.67" AMOLED 120Hz, Dimensity 8300-Ultra'),
            ('Nothing Phone (2) 256GB', 'nothing-phone-2', 'Nothing', 'smartphones', 44990,
             'Дисплей 6.7" OLED 120Hz, Snapdragon 8+ Gen 1, Glyph Interface'),
            ('Xiaomi 14 Ultra 512GB', 'xiaomi-14-ultra', 'Xiaomi', 'smartphones', 89990,
             'Дисплей 6.73" AMOLED 120Hz, Leica Summilux, 5300 мАч'),

            # === Ноутбуки ===
            ('MacBook Air 13 M3 8/256', 'macbook-air-m3', 'Apple', 'laptops', 109990,
             '13.6" Liquid Retina, M3, 8 ГБ, SSD 256 ГБ, 18ч'),
            ('MacBook Pro 14 M3 Pro', 'macbook-pro-14-m3', 'Apple', 'laptops', 189990,
             '14.2" Liquid Retina XDR, M3 Pro, 18 ГБ, SSD 512 ГБ'),
            ('ASUS VivoBook 15 Ryzen 5', 'asus-vivobook-15', 'ASUS', 'laptops', 52990,
             '15.6" IPS FHD, Ryzen 5 7530U, 16 ГБ, SSD 512 ГБ'),
            ('ASUS ROG Strix G16 RTX 4060', 'asus-rog-strix-g16', 'ASUS', 'laptops', 119990,
             '16" IPS 165Hz, i7-13650HX, RTX 4060, 16 ГБ'),
            ('Lenovo IdeaPad 3 15 i5', 'lenovo-ideapad-3', 'Lenovo', 'laptops', 44990,
             '15.6" IPS FHD, i5-1235U, 8 ГБ, SSD 256 ГБ'),
            ('Lenovo Legion 5 16 RTX4060', 'lenovo-legion-5', 'Lenovo', 'laptops', 109990,
             '16" WQXGA 165Hz, Ryzen 7 7745H, RTX 4060'),
            ('HP Pavilion 15 Ryzen 7', 'hp-pavilion-15', 'HP', 'laptops', 59990,
             '15.6" IPS FHD, Ryzen 7 7730U, 16 ГБ, SSD 512 ГБ'),
            ('Acer Aspire 5 i5-1335U', 'acer-aspire-5', 'Acer', 'laptops', 46990,
             '15.6" IPS FHD, i5-1335U, 8 ГБ, SSD 512 ГБ'),
            ('MSI Katana 15 RTX 4050', 'msi-katana-15', 'MSI', 'laptops', 89990,
             '15.6" IPS 144Hz, i7-13620H, RTX 4050, 16 ГБ'),
            ('Huawei MateBook D16 i5', 'huawei-matebook-d16', 'Huawei', 'laptops', 54990,
             '16" IPS FHD+, i5-12450H, 8 ГБ, SSD 512 ГБ'),
            ('ASUS ZenBook 14 OLED', 'asus-zenbook-14-oled', 'ASUS', 'laptops', 79990,
             '14" 2.8K OLED 120Hz, Core Ultra 7, 16 ГБ'),

            # === Телевизоры ===
            ('Samsung UE55CU7100 55"', 'samsung-cu7100-55', 'Samsung', 'tv', 42990,
             '55" 4K UHD, Smart TV Tizen, HDR10+'),
            ('LG 55UR78006LK 55"', 'lg-55ur78', 'LG', 'tv', 44990,
             '55" 4K UHD, webOS, HDR10 Pro, α5 Gen6 AI'),
            ('Samsung QE65Q80C 65" QLED', 'samsung-q80c-65', 'Samsung', 'tv', 89990,
             '65" QLED 4K 120Hz, Quantum HDR+'),
            ('LG OLED55C3 55" OLED', 'lg-oled55c3', 'LG', 'tv', 99990,
             '55" OLED 4K 120Hz, Dolby Vision IQ, α9 Gen6'),
            ('Xiaomi TV A Pro 55"', 'xiaomi-tv-a-pro-55', 'Xiaomi', 'tv', 32990,
             '55" 4K UHD, Google TV, Dolby Vision'),
            ('Hisense 50A6K 50"', 'hisense-50a6k', 'Hisense', 'tv', 27990,
             '50" 4K UHD, VIDAA, Dolby Vision'),
            ('TCL 65C745 65" QLED', 'tcl-65c745', 'TCL', 'tv', 64990,
             '65" QLED 4K 144Hz, Google TV, Dolby Atmos'),
            ('Sony KD-55X85L 55"', 'sony-55x85l', 'Sony', 'tv', 69990,
             '55" 4K 120Hz, Triluminos Pro, Google TV'),
            ('LG 43UR78006LK 43"', 'lg-43ur78', 'LG', 'tv', 29990,
             '43" 4K UHD, webOS, HDR10 Pro'),

            # === Наушники ===
            ('Apple AirPods Pro 2', 'airpods-pro-2', 'Apple', 'headphones', 22990,
             'TWS, ANC, H2, адаптивный звук, USB-C, 6ч'),
            ('Sony WH-1000XM5', 'sony-wh1000xm5', 'Sony', 'headphones', 29990,
             'Полноразмерные, ANC, 30ч, LDAC, мультипоинт'),
            ('Galaxy Buds3 Pro', 'galaxy-buds3-pro', 'Samsung', 'headphones', 16990,
             'TWS, ANC, 360 Audio, 24-бит Hi-Fi, IP57'),
            ('JBL Tune 770NC', 'jbl-tune-770nc', 'JBL', 'headphones', 6990,
             'Полноразмерные, ANC, 44ч, JBL Pure Bass'),
            ('JBL Live Pro 2', 'jbl-live-pro-2', 'JBL', 'headphones', 9990,
             'TWS, ANC, Smart Ambient, 40ч (кейс), IPX5'),
            ('Xiaomi Buds 4 Pro', 'xiaomi-buds-4-pro', 'Xiaomi', 'headphones', 8990,
             'TWS, ANC 48 дБ, LDAC, 9ч, IP54'),
            ('Marshall Major IV', 'marshall-major-iv', 'Marshall', 'headphones', 8990,
             'Полноразмерные, 80+ч, беспроводная зарядка'),
            ('Sennheiser Momentum 4', 'sennheiser-momentum-4', 'Sennheiser', 'headphones', 27990,
             'Полноразмерные, ANC, 60ч, aptX Adaptive'),
            ('Apple AirPods 3', 'airpods-3', 'Apple', 'headphones', 14990,
             'TWS, пространственный звук, MagSafe, 6ч'),
            ('AirPods Max', 'airpods-max', 'Apple', 'headphones', 49990,
             'Полноразмерные, ANC, H1, 20ч, Digital Crown'),
            ('Sony WF-1000XM5', 'sony-wf1000xm5', 'Sony', 'headphones', 24990,
             'TWS, ANC, LDAC, Hi-Res, 8ч, IPX4'),

            # === Планшеты ===
            ('iPad 10.9 (2022) 64GB', 'ipad-10-2022', 'Apple', 'tablets', 39990,
             '10.9" Liquid Retina, A14 Bionic, 64 ГБ, USB-C'),
            ('iPad Air M2 11" 128GB', 'ipad-air-m2', 'Apple', 'tablets', 59990,
             '11" Liquid Retina, M2, 128 ГБ, Wi-Fi 6E'),
            ('Galaxy Tab S9 FE 128GB', 'galaxy-tab-s9-fe', 'Samsung', 'tablets', 34990,
             '10.9" TFT 90Hz, Exynos 1380, S Pen'),
            ('Xiaomi Pad 6 128GB', 'xiaomi-pad-6', 'Xiaomi', 'tablets', 24990,
             '11" IPS 144Hz, Snapdragon 870, 8/128 ГБ'),
            ('Lenovo Tab P12 128GB', 'lenovo-tab-p12', 'Lenovo', 'tablets', 29990,
             '12.7" 2K IPS, Dimensity 7050, JBL'),
            ('Huawei MatePad 11.5"', 'huawei-matepad-11', 'Huawei', 'tablets', 22990,
             '11.5" IPS 120Hz, Snapdragon 7 Gen 1'),
            ('iPad Pro M4 11" 256GB', 'ipad-pro-m4-11', 'Apple', 'tablets', 99990,
             '11" Tandem OLED, M4, 256 ГБ, Thunderbolt'),

            # === Фотоаппараты ===
            ('Canon EOS R50 Kit', 'canon-eos-r50', 'Canon', 'cameras', 74990,
             'Беззеркальная, 24.2 Мп, 4K 30fps, 375 г'),
            ('Sony Alpha a6400 Kit', 'sony-a6400', 'Sony', 'cameras', 79990,
             'Беззеркальная, 24.2 Мп, 4K, 425 точек АФ'),
            ('Nikon Z50 Kit', 'nikon-z50', 'Nikon', 'cameras', 69990,
             'Беззеркальная, 20.9 Мп, 4K, 209 точек АФ'),
            ('Fujifilm X-T30 II Kit', 'fujifilm-xt30-ii', 'Fujifilm', 'cameras', 84990,
             'Беззеркальная, 26.1 Мп, 4K, 18 симуляций'),
            ('Canon EOS R6 Mark II', 'canon-eos-r6-ii', 'Canon', 'cameras', 189990,
             'Полнокадр, 24.2 Мп, 4K 60fps, IBIS 8 ст.'),

            # === Консоли ===
            ('PlayStation 5', 'ps5', 'Sony', 'consoles', 54990,
             'Zen 2, RDNA 2, SSD 825 ГБ, 4K 120fps, Blu-ray'),
            ('PlayStation 5 Digital', 'ps5-digital', 'Sony', 'consoles', 44990,
             'Zen 2, RDNA 2, SSD 825 ГБ, без дисковода'),
            ('Xbox Series X', 'xbox-series-x', 'Microsoft', 'consoles', 49990,
             '12 TF, SSD 1 ТБ, 4K 120fps, Game Pass'),
            ('Xbox Series S', 'xbox-series-s', 'Microsoft', 'consoles', 27990,
             'Компактная, SSD 512 ГБ, 1440p 120fps'),
            ('Nintendo Switch OLED', 'nintendo-switch-oled', 'Nintendo', 'consoles', 29990,
             '7" OLED, 64 ГБ, гибрид портатив/ТВ'),
            ('Steam Deck 256GB', 'steam-deck-256', 'Valve', 'consoles', 49990,
             '7" IPS, AMD APU, SSD 256 ГБ, SteamOS'),

            # === Бытовая техника ===
            ('Samsung WW80T стиральная', 'samsung-ww80t', 'Samsung', 'appliances', 32990,
             '8 кг, 1200 об/мин, Digital Inverter'),
            ('LG F2J3NS стиральная', 'lg-f2j3ns', 'LG', 'appliances', 29990,
             '6 кг, Direct Drive, 13 программ'),
            ('Bosch WGA254 стиральная', 'bosch-wga254', 'Bosch', 'appliances', 42990,
             '10 кг, EcoSilence Drive, AntiVibration'),
            ('LG GA-B509 холодильник', 'lg-ga-b509', 'LG', 'appliances', 49990,
             'No Frost, 384 л, инверторный, Door Cooling+'),
            ('Samsung RB37 холодильник', 'samsung-rb37', 'Samsung', 'appliances', 44990,
             'No Frost, 387 л, Digital Inverter, SpaceMax'),
            ('Dyson V15 Detect пылесос', 'dyson-v15', 'Dyson', 'appliances', 54990,
             'Беспроводной, 60 мин, лазер, HEPA'),
            ('Xiaomi Robot Vacuum X10+', 'xiaomi-robot-x10', 'Xiaomi', 'appliances', 39990,
             'Робот-пылесос, LDS, влажная уборка'),
            ('DeLonghi ECAM 22 кофемашина', 'delonghi-ecam-22', 'DeLonghi', 'appliances', 34990,
             'Автоматическая, 15 бар, капучинатор, 1.8 л'),
            ('Dyson Supersonic HD15 фен', 'dyson-supersonic-hd15', 'Dyson', 'appliances', 36990,
             'Мотор V9, 5 насадок, 4 температуры'),

            # === Умные часы ===
            ('Apple Watch Series 9 45mm', 'apple-watch-s9', 'Apple', 'smartwatches', 39990,
             'OLED Always-On, S9, ЭКГ, SpO2, 50м'),
            ('Apple Watch SE 2 44mm', 'apple-watch-se2', 'Apple', 'smartwatches', 24990,
             'OLED, S8, пульс, обнаружение ДТП'),
            ('Galaxy Watch 6 44mm', 'galaxy-watch-6', 'Samsung', 'smartwatches', 22990,
             '1.5" Super AMOLED, BioActive, GPS'),
            ('Xiaomi Watch S3', 'xiaomi-watch-s3', 'Xiaomi', 'smartwatches', 12990,
             '1.43" AMOLED, GPS, 150+ режимов, 15 дней'),
            ('Huawei Watch GT 4 46mm', 'huawei-watch-gt4', 'Huawei', 'smartwatches', 19990,
             '1.43" AMOLED, GPS, TruSeen, 14 дней'),
            ('Garmin Venu 3', 'garmin-venu-3', 'Garmin', 'smartwatches', 39990,
             '1.4" AMOLED, GPS, Body Battery'),
            ('Galaxy Watch Ultra', 'galaxy-watch-ultra', 'Samsung', 'smartwatches', 49990,
             '1.47" AMOLED, Titanium, 10 ATM, 60ч'),

            # === Аксессуары ===
            ('Samsung 990 EVO 1TB SSD', 'samsung-990-evo-1tb', 'Samsung', 'accessories', 9990,
             'M.2 NVMe, 5000/4200 МБ/с'),
            ('Logitech MX Master 3S', 'logitech-mx-master-3s', 'Logitech', 'accessories', 7990,
             'Мышь, 8000 DPI, MagSpeed, USB-C'),
            ('Keychron K8 Pro клавиатура', 'keychron-k8-pro', 'Keychron', 'accessories', 8990,
             'Механическая TKL, Gateron, BT 5.1, RGB'),
            ('Anker PowerCore 26800', 'anker-powercore-26800', 'Anker', 'accessories', 4990,
             'Повербанк 26800 мАч, 3 USB-A, PowerIQ'),
            ('Apple MagSafe зарядка', 'apple-magsafe-charger', 'Apple', 'accessories', 3990,
             'Беспроводная 15 Вт, магнитная'),
            ('JBL Charge 5 колонка', 'jbl-charge-5', 'JBL', 'accessories', 12990,
             '30 Вт, IP67, 20ч, BT 5.1, PartyBoost'),
            ('Samsung T7 Shield 1TB', 'samsung-t7-shield-1tb', 'Samsung', 'accessories', 8990,
             'Внешний SSD, USB 3.2, 1050 МБ/с, IP65'),
            ('Яндекс Станция Макс', 'yandex-station-max', 'Яндекс', 'accessories', 19990,
             'Умная колонка, Алиса, LED, Zigbee, 65 Вт'),
        ]

        for name, slug, brand, cat_slug, base_price, desc in products_data:
            image_url = product_img(name)

            product, created = Product.objects.update_or_create(slug=slug, defaults={
                'name': name,
                'brand': brand,
                'category': cats[cat_slug],
                'description': desc,
                'image_url': image_url,
            })

            if created:
                selected = random.sample(stores, k=random.randint(3, 4))
                cheapest_store = random.choice(selected)

                for store in selected:
                    if store == cheapest_store:
                        variation = random.uniform(-0.08, -0.02)
                    else:
                        variation = random.uniform(0.0, 0.12)

                    p = round(base_price * (1 + variation), -1)

                    old_p = None
                    if random.random() < 0.3:
                        old_p = Decimal(str(round(p * random.uniform(1.08, 1.25), -1)))

                    avail = random.random() > 0.1

                    Price.objects.get_or_create(
                        product=product, store=store,
                        defaults={
                            'price': Decimal(str(p)),
                            'old_price': old_p,
                            'is_available': avail,
                            'product_url': f'{store.website}/product/{slug}',
                        }
                    )

        # Тестовый пользователь
        if not User.objects.filter(username='demo').exists():
            user = User.objects.create_user('demo', 'demo@example.com', 'demo1234')
            UserProfile.objects.create(user=user, city='Красноярск')
            self.stdout.write(self.style.WARNING('Пользователь: demo / demo1234'))

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Категорий: {Category.objects.count()}, '
            f'Магазинов: {Store.objects.count()}, '
            f'Товаров: {Product.objects.count()}, '
            f'Цен: {Price.objects.count()}'
        ))
