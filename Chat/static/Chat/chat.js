const chatSocket = new WebSocket('wss://' + window.location.host + '/ws/chat/');

const messageInput = document.querySelector('.write_msg');
const sendButton = document.querySelector('.msg_send_btn');

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    const user = data['user_name'];
    const msgHistory = document.querySelector('.msg_history');
    let newMsg = "";

    if (currentUser === user) {
        newMsg = `
                    <div class="outgoing_msg d-flex justify-content-end mb-3">
                        <div class="sent_msg" style="max-width: 80%;">
                            <p>${message}</p>
                            <span class="time_date">${new Date().toLocaleTimeString()}</span>
                        </div>
                    </div>`;

    } else {
        newMsg = `
                    <div class="incoming_msg">
                            <div class="received_msg">
                                <div class="received_withd_msg">
                                    <span style="font-size: 12px; font-weight: bold; color: #05728f; display: block; margin-bottom: 3px;">
                                        ${user}
                                    </span>
                                    <p>${message}</p>
                                    <span class="time_date">${new Date().toLocaleTimeString()}</span>
                            </div>
                        </div>
                    </div>`;
    }

    msgHistory.innerHTML += newMsg;

    msgHistory.scrollTop = msgHistory.scrollHeight;
}

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexptedly');
}

function sendMessage(message) {
    chatSocket.send(JSON.stringify({
        'message': message,
        'user_name': currentUser
    }))
}

function handleSend() {
    const message = messageInput.value.trim();

    if (message !== "") {
        chatSocket.send(JSON.stringify({
            'message': message,
            'user_name': currentUser
        }));
    }

    messageInput.value = '';
}

sendButton.addEventListener('click', function (e) {
    handleSend();
});

messageInput.addEventListener('keyup', function (e) {
    if (e.key === 'Enter') {
        handleSend();
    }
});