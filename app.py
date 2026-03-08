import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Разрешаем запросы с любых сайтов (важно для GitHub Pages)
CORS(app)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Создаем таблицы, если их нет
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, text TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, sender TEXT, text TEXT, role TEXT)''')
    conn.commit()
    conn.close()

# API для входа
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    name = data.get("name", "Гость")
    code = data.get("code", "")
    role = "moderator" if code == "Immoderator12" else "user"
    return jsonify({"name": name, "role": role})

# API для создания заказа
@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer, text) VALUES (?, ?)", 
                   (data.get("name"), data.get("text")))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# API для получения списка заказов
@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer, text FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    orders = [{"id": r[0], "customer": r[1], "text": r[2]} for r in rows]
    return jsonify(orders)

# API для получения сообщений чата по конкретному заказу
@app.route('/api/chat/<int:order_id>', methods=['GET'])
def get_chat(order_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sender, text, role FROM messages WHERE order_id = ? ORDER BY id ASC", (order_id,))
    rows = cursor.fetchall()
    conn.close()
    
    msgs = [{"sender": r[0], "text": r[1], "role": r[2]} for r in rows]
    return jsonify(msgs)

# API для отправки сообщения в чат
@app.route('/api/chat/send', methods=['POST'])
def send_msg():
    data = request.json
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (order_id, sender, text, role) VALUES (?, ?, ?, ?)", 
                   (data.get("order_id"), data.get("sender"), data.get("text"), data.get("role")))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    # Запуск сервера
    app.run(debug=True, host='0.0.0.0', port=5000)
