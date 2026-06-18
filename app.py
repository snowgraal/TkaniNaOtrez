from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response
import json
import os
from datetime import datetime
import secrets
import requests

app = Flask(__name__)

# Настройки Telegram (замени на свои)
TELEGRAM_BOT_TOKEN = "8818412085:AAHtLmsWdYQ3yUQTlLWeAYZIpUxcFUOGM-c"  # Получить у @BotFather
TELEGRAM_CHAT_ID = "449804614"  # Узнать у @userinfobot
SITE_URL = os.environ.get('SITE_URL', 'https://tkaninaotrez.ru')
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))

app.secret_key = SECRET_KEY

def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def send_telegram_notification(order_data):
    """Отправляет уведомление о новом заказе в Telegram"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "ТВОЙ_ТОКЕН_БОТА":
        print("❌ Telegram токен не настроен")
        return

    if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "ТВОЙ_CHAT_ID":
        print("❌ Telegram Chat ID не настроен")
        return

    message = f"""
🔥 <b>НОВЫЙ ЗАКАЗ №{order_data['id']}</b>

📦 <b>Товар:</b> {order_data.get('product', 'Не указан')}
👤 <b>Клиент:</b> {order_data.get('name', 'Не указано')}
📞 <b>Телефон:</b> <code>{order_data.get('phone', 'Не указан')}</code>
📏 <b>Метраж:</b> {order_data.get('meters', '0')} м
💬 <b>Комментарий:</b> {order_data.get('comment', 'Нет')}

🕐 <i>{order_data['date']}</i>
    """

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        print(f"📤 Отправка в Telegram на chat_id: {TELEGRAM_CHAT_ID}")
        response = requests.post(url, json=payload, timeout=10)

        result = response.json()
        if result.get('ok'):
            print(f"✅ Уведомление отправлено в Telegram (заказ №{order_data['id']})")
        else:
            print(f"❌ Ошибка Telegram: {result.get('description')}")

    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")


def save_order(order_data):
    """Сохраняет заказ в JSON файл и отправляет в Telegram"""
    orders_file = 'orders.json'
    orders = []
    if os.path.exists(orders_file):
        with open(orders_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)

    order_data['id'] = len(orders) + 1
    order_data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order_data['status'] = 'Новый'
    orders.append(order_data)

    with open(orders_file, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

    send_telegram_notification(order_data)


# Главная страница
@app.route('/')
def index():
    data = load_data()
    popular_items = []
    for cat in data['categories'][:4]:
        for item in cat['items'][:2]:
            popular_items.append({
                'name': item['name'],
                'price': item['price'],
                'unit': item['unit'],
                'category': cat['name'],
                'density': item['density']
            })

    total_products = sum(len(cat['items']) for cat in data['categories'])

    return render_template('index.html',
                           data=data,
                           popular_items=popular_items,
                           total_products=total_products)


# Каталог
@app.route('/catalog')
def catalog():
    data = load_data()
    search = request.args.get('search', '').lower()
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'default')

    filtered_categories = []
    for cat in data['categories']:
        filtered_items = []
        for item in cat['items']:
            if search and search not in item['name'].lower():
                continue
            if category_filter and cat['name'] != category_filter:
                continue
            if min_price and item['price'] < min_price:
                continue
            if max_price and item['price'] > max_price:
                continue
            filtered_items.append(item)

        if filtered_items:
            filtered_categories.append({
                'name': cat['name'],
                'items': sorted(filtered_items,
                                key=lambda x: x['price'] if sort_by == 'price_asc' else -x[
                                    'price'] if sort_by == 'price_desc' else 0)
            })

    total_products = sum(len(cat['items']) for cat in data['categories'])

    return render_template('catalog.html',
                           data=data,
                           filtered_categories=filtered_categories,
                           search=search,
                           category_filter=category_filter,
                           total_products=total_products)


# Детальная страница товара
@app.route('/product/<category>/<item_name>')
def product(category, item_name):
    data = load_data()
    item = None
    related_items = []

    for cat in data['categories']:
        if cat['name'] == category:
            for it in cat['items']:
                if it['name'] == item_name:
                    item = it
                else:
                    related_items.append({**it, 'category': cat['name']})

    if not item:
        flash('Товар не найден')
        return redirect(url_for('catalog'))

    related_items = related_items[:4]

    return render_template('product.html',
                           item=item,
                           category=category,
                           related_items=related_items,
                           data=data)


# API быстрый просмотр
@app.route('/api/product/<category>/<item_name>')
def api_product(category, item_name):
    data = load_data()
    for cat in data['categories']:
        if cat['name'] == category:
            for it in cat['items']:
                if it['name'] == item_name:
                    return jsonify(it)
    return jsonify({'error': 'Not found'}), 404


# Контакты
@app.route('/contacts')
def contacts():
    data = load_data()
    return render_template('contacts.html', data=data)


# Доставка
@app.route('/delivery')
def delivery():
    data = load_data()
    return render_template('delivery.html', data=data)


# Ткани оптом (SEO страница)
@app.route('/opt')
def opt():
    data = load_data()
    return render_template('opt.html', data=data)


# API калькулятор
@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    price = float(data['price'])
    meters = float(data['meters'])
    total = price * meters
    discount = 0

    if meters >= 100:
        discount = total * 0.07
    elif meters >= 50:
        discount = total * 0.05
    elif meters >= 30:
        discount = total * 0.03

    total -= discount

    return jsonify({
        'total': round(total, 2),
        'discount': round(discount, 2),
        'discount_percent': 7 if meters >= 100 else 5 if meters >= 50 else 3 if meters >= 30 else 0,
        'meters': meters,
        'price_per_meter': price,
        'savings': round(discount, 2)
    })


# API отправка заявки
@app.route('/api/order', methods=['POST'])
def create_order():
    try:
        order = request.get_json()
        save_order(order)
        return jsonify({'success': True, 'message': 'Заявка принята! Мы перезвоним вам в ближайшее время.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# API поиск
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])

    data = load_data()
    results = []
    for cat in data['categories']:
        for item in cat['items']:
            if query in item['name'].lower():
                results.append({
                    'name': item['name'],
                    'category': cat['name'],
                    'price': item['price'],
                    'unit': item['unit']
                })

    return jsonify(results[:10])


# Админка
@app.route('/admin/orders')
def admin_orders():
    orders_file = 'orders.json'
    orders = []
    if os.path.exists(orders_file):
        with open(orders_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)

    orders.reverse()
    return render_template('admin_orders.html', orders=orders)


# Sitemap.xml
@app.route('/sitemap.xml')
def sitemap():
    data = load_data()
    base_url = SITE_URL

    pages = []

    # Основные страницы
    pages.append({'loc': f'{base_url}/', 'changefreq': 'daily', 'priority': '1.0'})
    pages.append({'loc': f'{base_url}/catalog', 'changefreq': 'daily', 'priority': '0.9'})
    pages.append({'loc': f'{base_url}/opt', 'changefreq': 'weekly', 'priority': '0.9'})
    pages.append({'loc': f'{base_url}/delivery', 'changefreq': 'weekly', 'priority': '0.7'})
    pages.append({'loc': f'{base_url}/contacts', 'changefreq': 'weekly', 'priority': '0.7'})

    # Категории
    for cat in data['categories']:
        pages.append({
            'loc': f'{base_url}/catalog?category={cat["name"]}',
            'changefreq': 'weekly',
            'priority': '0.8'
        })

    # Товары
    for cat in data['categories']:
        for item in cat['items']:
            pages.append({
                'loc': f'{base_url}/product/{cat["name"]}/{item["name"]}',
                'changefreq': 'weekly',
                'priority': '0.8'
            })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'

    xml += '</urlset>'

    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response


# Robots.txt
@app.route('/robots.txt')
def robots():
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api
Sitemap: {SITE_URL}/sitemap.xml
Host: {SITE_URL.replace('https://', '')}
"""
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response


# Спасибо
@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


# 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)