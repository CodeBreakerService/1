// ВАЖНО: Когда запустишь бэкенд в интернет (например, на Render), 
// замени "http://127.0.0.1:5000" на свою новую ссылку!
const API_URL = "https://one-1-zlsw.onrender.com"; 

let currentUser = "Гость";
let currentRole = "user";
let activeOrder = null;
let chatInterval = null;

// Управление окнами
function openM(id) { document.getElementById(id).style.display = 'flex'; }
function closeM(id) { document.getElementById(id).style.display = 'none'; }

// Сохранение профиля
async function saveP() {
    const name = document.getElementById('in-name').value || "Аноним";
    const code = document.getElementById('in-code').value;
    
    try {
        const res = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, code})
        });
        const data = await res.json();
        
        currentUser = data.name; 
        currentRole = data.role;
        document.getElementById('n-disp').innerText = currentUser;
        
        if(currentRole === 'moderator') {
            document.getElementById('r-disp').innerText = 'MODERATOR';
            document.getElementById('r-disp').className = 'rank-mod';
            document.getElementById('mod-list').classList.remove('hidden');
            refreshOrders();
        } else {
            document.getElementById('r-disp').innerText = '';
            document.getElementById('r-disp').className = '';
            document.getElementById('mod-list').classList.add('hidden');
        }
        closeM('pModal');
        alert("Профиль сохранен!");
    } catch (e) {
        alert("Ошибка подключения к серверу! Проверьте API_URL.");
    }
}

// Открытие окна для нового заказа
function openOrderModal() {
    activeOrder = null;
    document.getElementById('chat-title').innerHTML = '<span class="material-icons" style="vertical-align: middle;">rate_review</span> Напишите запрос';
    document.getElementById('order-ui').classList.remove('hidden');
    document.getElementById('chat-ui').classList.add('hidden');
    openM('oModal');
}

// Отправка заказа
async function sendO() {
    const text = document.getElementById('o-text').value;
    if(!text.trim()) return alert("Пожалуйста, опишите ваш сайт!");
    
    await fetch(`${API_URL}/api/order`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: currentUser, text})
    });
    
    alert("Заказ успешно отправлен модератору!");
    document.getElementById('o-text').value = '';
    closeM('oModal');
    if (currentRole === 'moderator') refreshOrders();
}

// Загрузка списка заказов (Для модератора)
async function refreshOrders() {
    const res = await fetch(`${API_URL}/api/orders`);
    const orders = await res.json();
    const box = document.getElementById('orders-box');
    
    if (orders.length === 0) {
        box.innerHTML = "<p>Пока нет новых заказов.</p>";
        return;
    }

    box.innerHTML = orders.map(o => `
        <div class="order-card">
            <div style="font-weight: bold; margin-bottom: 5px;">Заказ #${o.id} от: ${o.customer}</div>
            <div style="margin-bottom: 10px; color: #444;">${o.text}</div>
            <button class="btn" style="padding: 10px; font-size: 1rem;" onclick="openChat(${o.id})">
                <span class="material-icons">chat</span> Открыть чат
            </button>
        </div>
    `).join('');
}

// Открытие чата
async function openChat(id) {
    activeOrder = id;
    document.getElementById('chat-title').innerHTML = `<span class="material-icons" style="vertical-align: middle;">chat</span> Чат (Заказ #${id})`;
    document.getElementById('order-ui').classList.add('hidden');
    document.getElementById('chat-ui').classList.remove('hidden');
    openM('oModal');
    loadMsgs();
    
    // Включаем автообновление чата
    if (chatInterval) clearInterval(chatInterval);
    chatInterval = setInterval(loadMsgs, 3000);
}

// Закрытие модалки чата/заказа
function closeChatModal() {
    closeM('oModal');
    if (chatInterval) clearInterval(chatInterval);
}

// Загрузка сообщений
async function loadMsgs() {
    if(!activeOrder) return;
    const res = await fetch(`${API_URL}/api/chat/${activeOrder}`);
    const msgs = await res.json();
    
    const chatBox = document.getElementById('chat-msgs');
    chatBox.innerHTML = msgs.map(m => `
        <div class="msg ${m.role === 'moderator' ? 'msg-mod' : 'msg-user'}">
            <span class="msg-author">${m.sender} ${m.role === 'moderator' ? '[MOD]' : ''}</span>
            ${m.text}
        </div>
    `).join('');
    
    // Прокрутка вниз
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Отправка сообщения
async function sendMsg() {
    const input = document.getElementById('chat-input');
    const text = input.value;
    if(!text.trim()) return;
    
    await fetch(`${API_URL}/api/chat/send`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({order_id: activeOrder, sender: currentUser, text, role: currentRole})
    });
    
    input.value = "";
    loadMsgs();
      }
