class Chat {
    constructor(sessionId, userId) {
        this.sessionId = sessionId;
        this.userId = userId;
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageForm = document.getElementById('message-form');
        this.messageInput = document.getElementById('id_content');
        this.fileInput = document.getElementById('id_file');
        this.lastMessageId = 0;
        this.isPolling = false;
        this.typingTimeout = null;
        this.isTyping = false;
        this.chatCounterElement = document.getElementById('chat-counter');
        this.updateChatCounterInterval = null;
        // Правильное имя метода - init
        this.init(); // Было this.init() но метод называется init(), а не initialize()
    }

    // Переименован метод initialize -> init
    init() {
        this.setupEventListeners();
        this.scrollToBottom();
        this.startPolling();
        this.loadLastMessageId();
        this.setupTypingIndicator();
        this.startChatCounterPolling(); // Добавьте это
    }
    startChatCounterPolling() {
        // Обновляем счетчик каждые 30 секунд
        this.updateChatCounter();
        this.updateChatCounterInterval = setInterval(() => this.updateChatCounter(), 30000);
    }
        stopChatCounterPolling() {
        if (this.updateChatCounterInterval) {
            clearInterval(this.updateChatCounterInterval);
        }
    }
    setupEventListeners() {
        if (this.messageForm) {
            this.messageForm.addEventListener('submit', (e) => this.sendMessage(e));
        }


        const completeBtn = document.getElementById('complete-chat');
        if (completeBtn) {
            completeBtn.addEventListener('click', () => this.completeChat());
        }

        const reopenBtn = document.getElementById('reopen-chat');
        if (reopenBtn) {
            reopenBtn.addEventListener('click', () => this.reopenChat());
        }

        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }
    async updateChatCounter() {
        try {
            const response = await fetch('/chat/unread_count/');
            if (response.ok) {
                const data = await response.json();
                this.updateChatCounterUI(data.unread_chat_count);
            }
        } catch (error) {
            console.error('Error updating chat counter:', error);
        }
    }

    updateChatCounterUI(count) {
        if (this.chatCounterElement) {
            if (count > 0) {
                this.chatCounterElement.textContent = count;
                this.chatCounterElement.style.display = 'inline';
            } else {
                this.chatCounterElement.style.display = 'none';
            }
        }
    }
    async sendMessage(e) {
        if (e) e.preventDefault();
        
        const content = this.messageInput ? this.messageInput.value.trim() : '';
        const file = this.fileInput ? this.fileInput.files[0] : null;

        if (!content && !file) return;

        const formData = new FormData();
        if (content) formData.append('content', content);
        if (file) formData.append('file', file);

        try {
            const csrfToken = this.getCSRFToken();
            const response = await fetch(`/chat/send/${this.sessionId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            // Проверяем статус ответа
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Проверяем, что ответ действительно JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new TypeError('Ожидался JSON, но получили: ' + contentType);
            }

            const data = await response.json();

            if (data.status === 'success') {
                this.addMessageToChat(data, true);
                if (this.messageInput) this.messageInput.value = '';
                if (this.fileInput) this.fileInput.value = '';
                this.scrollToBottom();
                this.lastMessageId = data.message_id;
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Ошибка отправки сообщения. Проверьте подключение и попробуйте снова.');
        }
    }
 async checkNewMessages() {
        try {
            const response = await fetch(`/chat/get_messages/${this.sessionId}/?last_id=${this.lastMessageId}`);
            
            if (!response.ok) {
                if (response.status === 403) {
                    console.error('Доступ запрещен к чату');
                    this.stopPolling();
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        this.addMessageToChat(msg, msg.sender_id === this.userId);
                        this.lastMessageId = Math.max(this.lastMessageId, msg.message_id);
                    });
                    this.scrollToBottom();
                    
                    // Обновляем счетчик при новых сообщениях
                    this.updateChatCounter();
                    
                    // Воспроизводим звук уведомления для новых сообщений не от текущего пользователя
                    const newMessagesFromOthers = data.messages.filter(msg => msg.sender_id !== this.userId);
                    if (newMessagesFromOthers.length > 0) {
                        this.playNotificationSound();
                    }
                }
            }
        } catch (error) {
            console.error('Error checking new messages:', error);
        }
    }
    addMessageToChat(data, isOwn = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isOwn ? 'own-message' : 'other-message'}`;
        messageDiv.dataset.messageId = data.message_id;
        
        let contentHtml = '';
        if (data.file_url) {
            contentHtml = `
                <div class="file-message">
                    <i class="fas fa-file"></i>
                    <a href="${data.file_url}" target="_blank">${data.file_name}</a>
                </div>
            `;
        } else {
            contentHtml = data.content.replace(/\n/g, '<br>');
        }

        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${isOwn ? 'Вы' : data.sender_name}</strong>
                <small class="text-muted">${data.created_at}</small>
            </div>
            <div class="message-content">${contentHtml}</div>
        `;

        this.messagesContainer.appendChild(messageDiv);
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    async loadLastMessageId() {
        if (this.messagesContainer) {
            const messages = this.messagesContainer.querySelectorAll('.message');
            if (messages.length > 0) {
                const lastMessage = messages[messages.length - 1];
                this.lastMessageId = parseInt(lastMessage.dataset.messageId) || 0;
            }
        }
    }

    startPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        this.pollInterval = setInterval(() => this.checkNewMessages(), 2000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.isPolling = false;
        }
    }

async checkNewMessages() {
    try {
        const response = await fetch(`/chat/get_messages/${this.sessionId}/?last_id=${this.lastMessageId}`);
        
        if (!response.ok) {
            if (response.status === 403) {
                console.error('Доступ запрещен к чату');
                this.stopPolling();
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new TypeError('Ожидался JSON, но получили: ' + contentType);
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    this.addMessageToChat(msg, msg.sender_id === this.userId);
                    this.lastMessageId = Math.max(this.lastMessageId, msg.message_id);
                });
                this.scrollToBottom();
                
                // Воспроизводим звук уведомления для новых сообщений не от текущего пользователя
                const newMessagesFromOthers = data.messages.filter(msg => msg.sender_id !== this.userId);
                if (newMessagesFromOthers.length > 0) {
                    this.playNotificationSound();
                }
            }
        } else if (data.status === 'error') {
            console.error('Ошибка сервера:', data.message);
        }
    } catch (error) {
        console.error('Error checking new messages:', error);
        // Не останавливаем polling при временных ошибках
    }
}

    playNotificationSound() {
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbVtfdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrLp6qtYFghDmN3xynovBiB9x/LRgjI');
            audio.volume = 0.3;
            audio.play().catch(() => {});
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    async completeChat() {
        if (confirm('Вы уверены, что хотите завершить сессию чата?')) {
            try {
                const csrfToken = this.getCSRFToken();
                const response = await fetch(`/chat/complete/${this.sessionId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();
                if (data.status === 'success') {
                    this.stopPolling();
                    window.location.reload();
                }
            } catch (error) {
                console.error('Error completing chat:', error);
            }
        }
    }

    async reopenChat() {
        try {
            const csrfToken = this.getCSRFToken();
            const response = await fetch(`/chat/reopen/${this.sessionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.startPolling();
                window.location.reload();
            }
        } catch (error) {
            console.error('Error reopening chat:', error);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            console.log('File selected:', file.name);
            
            if (this.messageInput && this.messageInput.value.trim() === '') {
                this.sendMessage(new Event('submit'));
            }
        }
    }

    setupTypingIndicator() {
        this.typingTimeout = null;
        this.isTyping = false;
        
        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => {
                this.handleTyping();
            });
        }
    }

    handleTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.sendTypingStatus(true);
        }
        
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
            this.sendTypingStatus(false);
        }, 1000);
    }

    async sendTypingStatus(isTyping) {
        try {
            const csrfToken = this.getCSRFToken();
            await fetch(`/chat/typing/${this.sessionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ typing: isTyping })
            });
        } catch (error) {
            console.error('Error sending typing status:', error);
        }
    }

    showTypingIndicator() {
        let indicator = this.messagesContainer.querySelector('.typing-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'typing-indicator';
            indicator.innerHTML = 'Собеседник печатает...';
            this.messagesContainer.appendChild(indicator);
        }
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = this.messagesContainer.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        
        if (!cookieValue) {
            const metaToken = document.querySelector('meta[name="csrf-token"]');
            if (metaToken) {
                cookieValue = metaToken.getAttribute('content');
            }
        }
        
        if (!cookieValue) {
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                cookieValue = csrfInput.value;
            }
        }
        
        return cookieValue || '';
    }
}

// Инициализация чата
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-messages');
    if (chatContainer) {
        const sessionId = chatContainer.dataset.sessionId;
        const userId = chatContainer.dataset.userId;
        
        if (sessionId && userId) {
            window.chat = new Chat(parseInt(sessionId), parseInt(userId));
        }
    }
    
    // Добавляем обработчик для всех textarea в чате
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
            e.preventDefault();
            const form = e.target.closest('form');
            if (form && window.chat) {
                window.chat.sendMessage(e);
            }
        }
    });
});