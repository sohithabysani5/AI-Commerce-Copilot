// State
let activeCustomerId = document.getElementById('customer-id-input')?.value || 'C001';
let currentLanguage = document.getElementById('language-select')?.value || 'en';
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

document.addEventListener('DOMContentLoaded', () => {
    loadCustomerOrders();
});

// ============================================================
// TABS & NAVIGATION
// ============================================================
function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

// ============================================================
// LOGOUT & CLEAR CONVERSATION
// ============================================================
async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/login';
}

async function clearConversation() {
    const res = await fetch('/api/chat/clear', { method: 'POST' });
    const data = await res.json();
    document.getElementById('chat-history').innerHTML = `
        <div class="chat-message assistant">
            <div class="avatar">🤖</div>
            <div class="bubble">👋 Conversation cleared. How can I help you today?</div>
        </div>
    `;
    updateOrderStateView(data.order_state || {});
}

// ============================================================
// CUSTOMER & ORDERS DATA
// ============================================================
async function updateCustomerId(newId) {
    activeCustomerId = newId.trim().toUpperCase() || 'C001';
    document.getElementById('orders-customer-label').textContent = activeCustomerId;
    await loadCustomerOrders();
}

async function changeLanguage(lang) {
    currentLanguage = lang;
    await clearConversation();
}

async function loadCustomerOrders() {
    const container = document.getElementById('orders-list-container');
    try {
        const res = await fetch(`/api/customer/orders?customer_id=${encodeURIComponent(activeCustomerId)}`);
        const data = await res.json();
        
        // Update Metrics
        document.getElementById('metric-total-orders').textContent = data.metrics.total;
        document.getElementById('metric-active-orders').textContent = data.metrics.active;
        document.getElementById('metric-cancelled-orders').textContent = data.metrics.cancelled;
        document.getElementById('metric-spending').textContent = `₹${data.metrics.spending.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        if (!data.orders || data.orders.length === 0) {
            container.innerHTML = `<div style="padding: 20px; text-align: center; background: white; border-radius: 12px; color: var(--text-muted);">No orders found for customer ID ${activeCustomerId}.</div>`;
            return;
        }

        container.innerHTML = data.orders.map(order => {
            let badgeClass = 'badge-placed';
            if (order.status === 'Shipped') badgeClass = 'badge-shipped';
            else if (order.status === 'Out for Delivery') badgeClass = 'badge-delivery';
            else if (order.status === 'Cancelled') badgeClass = 'badge-cancelled';
            else if (order.status === 'Delivered') badgeClass = 'badge-delivered';

            return `
                <div class="order-card">
                    <div>
                        <div class="order-id">${order.order_id}</div>
                        <div class="order-date">📅 ${order.created_at}</div>
                    </div>
                    <div>
                        <div class="product-title">${order.product}</div>
                        <div class="product-meta">Qty: ${order.quantity} | Amount: ₹${parseFloat(order.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
                    </div>
                    <div>
                        <span class="badge ${badgeClass}">${order.status}</span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        container.innerHTML = `<div style="color: #DC2626;">Error loading orders: ${err.message}</div>`;
    }
}

// ============================================================
// CHAT & AI ASSISTANT
// ============================================================
function sendSuggestion(text) {
    document.getElementById('chat-user-input').value = text;
    sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('chat-user-input');
    const msg = input.value.trim();
    if (!msg) return;

    const chatHistory = document.getElementById('chat-history');

    // Append User Message
    chatHistory.innerHTML += `
        <div class="chat-message user">
            <div class="avatar">👤</div>
            <div class="bubble">${escapeHtml(msg)}</div>
        </div>
    `;
    input.value = '';
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Show Loading
    const loadingId = 'loading-' + Date.now();
    chatHistory.innerHTML += `
        <div class="chat-message assistant" id="${loadingId}">
            <div class="avatar">🤖</div>
            <div class="bubble" style="font-style: italic; color: var(--text-muted);">Thinking...</div>
        </div>
    `;
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, language: currentLanguage })
        });
        const data = await res.json();

        document.getElementById(loadingId).remove();
        chatHistory.innerHTML += `
            <div class="chat-message assistant">
                <div class="avatar">🤖</div>
                <div class="bubble">${escapeHtml(data.response)}</div>
            </div>
        `;
        chatHistory.scrollTop = chatHistory.scrollHeight;

        updateOrderStateView(data.order_state);
        loadCustomerOrders(); // Refresh metrics if order was placed/cancelled
    } catch (err) {
        document.getElementById(loadingId).remove();
        chatHistory.innerHTML += `
            <div class="chat-message assistant">
                <div class="avatar">🤖</div>
                <div class="bubble" style="color: #DC2626;">Error sending message: ${err.message}</div>
            </div>
        `;
    }
}

function updateOrderStateView(orderState) {
    const box = document.getElementById('order-state-json');
    if (!orderState || Object.keys(orderState).length === 0) {
        box.textContent = "No active order process.";
    } else {
        box.textContent = JSON.stringify(orderState, null, 2);
    }
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// ============================================================
// VOICE AI & MICROPHONE
// ============================================================
async function toggleMicrophone() {
    const btn = document.getElementById('mic-toggle-btn');
    const label = document.getElementById('mic-status-label');

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = async () => {
                const blob = new Blob(audioChunks, { type: 'audio/wav' });
                await sendAudioToBackend(blob);
            };

            mediaRecorder.start();
            isRecording = true;
            btn.classList.add('recording');
            label.textContent = "Listening... Click to Stop";
        } catch (err) {
            alert("Microphone access failed: " + err.message);
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        btn.classList.remove('recording');
        label.textContent = "Processing audio...";
    }
}

async function sendAudioToBackend(audioBlob) {
    const label = document.getElementById('mic-status-label');
    const responseBox = document.getElementById('voice-response-container');
    const formData = new FormData();
    formData.append('audio', audioBlob, 'speech.wav');
    formData.append('language', currentLanguage);

    try {
        const res = await fetch('/api/voice/process', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        label.textContent = "Click to Speak";

        if (data.success) {
            responseBox.style.display = 'block';
            document.getElementById('voice-transcription').textContent = data.transcription || '(None)';
            document.getElementById('voice-reply').textContent = data.response_text || '(None)';

            if (data.audio_base64) {
                document.getElementById('voice-audio-wrapper').innerHTML = `
                    <audio autoplay controls src="data:audio/mp3;base64,${data.audio_base64}"></audio>
                `;
            }
            updateOrderStateView(data.order_state);
        } else {
            alert("Voice processing failed: " + data.message);
        }
    } catch (err) {
        label.textContent = "Click to Speak";
        alert("Error sending voice recording: " + err.message);
    }
}

// ============================================================
// OUTBOUND CALLING
// ============================================================
async function initiateCall() {
    const input = document.getElementById('phone-number-input');
    const status = document.getElementById('call-status');
    const phone = input.value.trim();

    if (!phone) {
        status.style.color = '#DC2626';
        status.textContent = 'Please enter a phone number.';
        return;
    }

    status.style.color = 'var(--text-navy)';
    status.textContent = 'Initiating AI Call...';

    try {
        const res = await fetch('/api/voice/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone })
        });
        const data = await res.json();

        if (data.success) {
            status.style.color = '#16A34A';
            status.textContent = `Call initiated successfully! Call SID: ${data.call_sid}`;
        } else {
            status.style.color = '#DC2626';
            status.textContent = `Failed to initiate call: ${data.message}`;
        }
    } catch (err) {
        status.style.color = '#DC2626';
        status.textContent = `Call error: ${err.message}`;
    }
}
