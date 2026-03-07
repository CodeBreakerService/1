from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- БАЗА ДАННЫХ В ПАМЯТИ ---
db = {
    "orders": [],
    "chats": {} # {order_id: [{"sender": "Name", "text": "Hi", "role": "user"}]}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeBreaker Service</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        :root { --bg: #f5f5dc; --accent: #f0e68c; --dark: #000; }
        * { box-sizing: border-box; }
        body { background: var(--bg); font-family: sans-serif; margin: 0; padding-bottom: 50px; }
        
        /* Профиль */
        .nav { display: flex; justify-content: space-between; padding: 10px; background: #fff; border-bottom: 3px solid #000; }
        .rank-mod { background: gold; color: #000; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; }

        /* Шапка с Логотипом */
        .hero { padding: 30px 20px; text-align: center; }
        .logo-img { width: 120px; height: 120px; object-fit: contain; margin-bottom: 10px; border-radius: 10px; }
        h1 { font-size: 2rem; text-transform: uppercase; margin: 10px 0; }
        .desc { font-size: 1.1rem; color: #333; margin-bottom: 25px; max-width: 500px; margin-left: auto; margin-right: auto; }
        .divider { height: 5px; background: #000; width: 100%; margin: 20px 0; }

        /* Кнопки */
        .btn { 
            display: inline-flex; align-items: center; justify-content: center;
            background: white; border: 3px solid #000; padding: 15px 30px; 
            font-size: 1.2rem; font-weight: bold; cursor: pointer; text-transform: uppercase;
        }
        .btn:active { background: #000; color: #fff; }

        /* Модалки */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 100; align-items: center; justify-content: center; }
        .modal-content { background: var(--bg); width: 95%; max-width: 450px; padding: 20px; border: 4px solid #000; }
        
        /* ЧАТ (стиль PlayerOK) */
        .chat-container { height: 250px; overflow-y: auto; border: 2px solid #000; background: #fff; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
        .msg { padding: 8px 12px; border-radius: 10px; max-width: 80%; font-size: 0.9rem; position: relative; }
        .msg-user { align-self: flex-start; background: #e1f5fe; border: 1px solid #01579b; }
        .msg-mod { align-self: flex-end; background: #fff9c4; border: 1px solid #fbc02d; }
        .msg-author { font-size: 0.7rem; font-weight: bold; margin-bottom: 3px; display: block; }

        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #000; }
        .hidden { display: none; }
    </style>
</head>
<body>

    <div class="nav">
        <div><span class="material-icons" style="vertical-align:bottom">person</span> <span id="n-disp">Гость</span> <span id="r-disp"></span></div>
        <button onclick="openM('pModal')"><span class="material-icons">settings</span></button>
    </div>

    <div class="hero">
        <img src="https://i.postimg.cc/nh49D3Kz/Picsart-26-03-07-16-24-17-930.png" class="logo-img" alt="CodeBreaker">
        <h1>CodeBreaker Service</h1>
        <p class="desc">Мы бренд производства бесплатных сайтов. Нажми на кнопку "Заказать сайт" и напиши о чем он будет и все твои пожелания.</p>
    </div>

    <div class="divider"></div>

    <div style="text-align:center">
        <button class="btn" onclick="openM('oModal')">
            <span class="material-icons" style="margin-right:10px">add_circle</span>ЗАКАЗАТЬ САЙТ
        </button>
    </div>

    <div id="mod-list" class="hidden" style="padding:20px">
        <hr>
        <h3><span class="material-icons">list_alt</span> Активные заказы:</h3>
        <div id="orders-box"></div>
    </div>

    <div id="pModal" class="modal">
        <div class="modal-content">
            <h3>Профиль</h3>
            <input type="text" id="in-name" placeholder="Ваше имя">
            <input type="password" id="in-code" placeholder="Секретный код">
            <button class="btn" style="width:100%" onclick="saveP()">Сохранить</button>
            <button onclick="closeM('pModal')" style="margin-top:10px">Закрыть</button>
        </div>
    </div>

    <div id="oModal" class="modal">
        <div class="modal-content">
            <h3 id="chat-title">Новый заказ</h3>
            <div id="chat-ui" class="hidden">
                <div class="chat-container" id="chat-msgs"></div>
                <input type="text" id="chat-input" placeholder="Введите сообщение...">
                <button class="btn" style="width:100%; font-size:1rem" onclick="sendMsg()">Отправить</button>
            </div>
            <div id="order-ui">
                <textarea id="o-text" rows="4" placeholder="Опишите сайт..."></textarea>
                <button class="btn" style="width:100%" onclick="sendO()">Отправить модератору</button>
            </div>
            <button onclick="closeM('oModal')" style="margin-top:10px">Закрыть</button>
        </div>
    </div>

    <script>
        let user = "Гость"; let role = "user"; let activeOrder = null;

        function openM(id) { document.getElementById(id).style.display = 'flex'; }
        function closeM(id) { document.getElementById(id).style.display = 'none'; }

        async function saveP() {
            const name = document.getElementById('in-name').value || "Аноним";
            const code = document.getElementById('in-code').value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, code})
            });
            const d = await res.json();
            user = d.name; role = d.role;
            document.getElementById('n-disp').innerText = user;
            if(role === 'moderator') {
                document.getElementById('r-disp').innerText = 'MOD';
                document.getElementById('r-disp').className = 'rank-mod';
                document.getElementById('mod-list').classList.remove('hidden');
                refreshOrders();
            }
            closeM('pModal');
        }

        async function sendO() {
            const text = document.getElementById('o-text').value;
            const res = await fetch('/api/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: user, text})
            });
            alert("Заказ создан!"); closeM('oModal');
        }

        async function refreshOrders() {
            const res = await fetch('/api/orders');
            const orders = await res.json();
            document.getElementById('orders-box').innerHTML = orders.map(o => `
                <div style="background:#fff; border:2px solid #000; margin:10px 0; padding:10px">
                    <b>#${o.id} от ${o.customer}</b>
                    <p>${o.text}</p>
                    <button onclick="openChat(${o.id})">Открыть Чат</button>
                </div>
            `).join('');
        }

        async function openChat(id) {
            activeOrder = id;
            document.getElementById('chat-title').innerText = "Чат по заказу #" + id;
            document.getElementById('order-ui').classList.add('hidden');
            document.getElementById('chat-ui').classList.remove('hidden');
            openM('oModal');
            loadMsgs();
        }

        async function loadMsgs() {
            if(!activeOrder) return;
            const res = await fetch('/api/chat/' + activeOrder);
            const msgs = await res.json();
            document.getElementById('chat-msgs').innerHTML = msgs.map(m => `
                <div class="msg ${m.role === 'moderator' ? 'msg-mod' : 'msg-user'}">
                    <span class="msg-author">${m.sender} [${m.role}]</span>
                    ${m.text}
                </div>
            `).join('');
            const c = document.getElementById('chat-msgs');
            c.scrollTop = c.scrollHeight;
        }

        async function sendMsg() {
            const text = document.getElementById('chat-input').value;
            await fetch('/api/chat/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({order_id: activeOrder, sender: user, text: text, role: role})
            });
            document.getElementById('chat-input').value = "";
            loadMsgs();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    role = "moderator" if d.get("code") == "Immoderator12" else "user"
    return jsonify({"name": d.get("name"), "role": role})

@app.route('/api/order', methods=['POST'])
def create_o():
    d = request.json
    oid = len(db["orders"]) + 1
    db["orders"].append({"id": oid, "customer": d.get("name"), "text": d.get("text")})
    db["chats"][oid] = []
    return jsonify({"status": "ok"})

@app.route('/api/orders')
def get_os(): return jsonify(db["orders"])

@app.route('/api/chat/<int:oid>')
def get_chat(oid): return jsonify(db["chats"].get(oid, []))

@app.route('/api/chat/send', methods=['POST'])
def send_m():
    d = request.json
    oid = d.get("order_id")
    if oid in db["chats"]:
        db["chats"][oid].append({"sender": d.get("sender"), "text": d.get("text"), "role": d.get("role")})
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
