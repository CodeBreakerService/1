// Ссылка на рабочий бэкенд Render
const API_URL = "https://one-1-zlsw.onrender.com"; 

let user = "Гость", role = "user", activeOrder = null, chatTimer = null;

const openM = id => document.getElementById(id).style.display = 'flex';
const closeM = id => document.getElementById(id).style.display = 'none';

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
        user = data.name; role = data.role;
        document.getElementById('n-disp').innerText = user;
        if(role === 'moderator') {
            document.getElementById('r-disp').innerText = 'MOD';
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
        alert("Ошибка подключения к серверу. Убедитесь, что сервер Render запущен.");
    }
}

async function sendO() {
    const text = document.getElementById('o-text').value;
    if(!text.trim()) return alert("Опишите заказ!");
    await fetch(`${API_URL}/api/order`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: user, text})
    });
    alert("Заказ успешно отправлен!"); 
    document.getElementById('o-text').value = '';
    closeM('oModal');
    if (role === 'moderator') refreshOrders();
}

async function refreshOrders() {
    const res = await fetch(`${API_URL}/api/orders`);
    const orders = await res.json();
    const box = document.getElementById('orders-box');
    if (orders.length === 0) {
        box.innerHTML = "<p>Заказов пока нет.</p>";
        return;
    }
    box.innerHTML = orders.map(o => `
        <div style="border:3px solid #000; padding:15px; margin-bottom:10px; background:#fff; text-align: left;">
            <b style="display:block; margin-bottom:5px;">Заказ #${o.id} (Клиент: ${o.customer})</b>
            <div style="margin-bottom:10px;">${o.text}</div>
            <button class="btn" style="padding:8px 15px; font-size:0.9rem;" onclick="openChat(${o.id})">Открыть чат</button>
        </div>
    `).join('');
}

function openOrderModal() {
    activeOrder = null;
    document.getElementById('chat-title').innerText = "Новый заказ";
    document.getElementById('order-ui').classList.remove('hidden');
    document.getElementById('chat-ui').classList.add('hidden');
    openM('oModal');
}

async function openChat(id) {
    activeOrder = id;
    document.getElementById('chat-title').innerText = `Чат (Заказ #${id})`;
    document.getElementById('order-ui').classList.add('hidden');
    document.getElementById('chat-ui').classList.remove('hidden');
    loadMsgs();
    if(chatTimer) clearInterval(chatTimer);
    chatTimer = setInterval(loadMsgs, 3000);
    openM('oModal');
}

function closeChatModal() { 
    closeM('oModal'); 
    if(chatTimer) clearInterval(chatTimer); 
}

async function loadMsgs() {
    if(!activeOrder) return;
    const res = await fetch(`${API_URL}/api/chat/${activeOrder}`);
    const msgs = await res.json();
    const chatBox = document.getElementById('chat-msgs');
    chatBox.innerHTML = msgs.map(m => `
        <div class="${m.role==='moderator'?'msg-mod':'msg-user'}">
            <small style="font-weight:bold; display:block; margin-bottom:2px;">${m.sender}:</small>
            ${m.text}
        </div>
    `).join('');
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMsg() {
    const input = document.getElementById('chat-input');
    if(!input.value.trim()) return;
    await fetch(`${API_URL}/api/chat/send`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({order_id: activeOrder, sender: user, text: input.value, role})
    });
    input.value = ""; 
    loadMsgs();
}
