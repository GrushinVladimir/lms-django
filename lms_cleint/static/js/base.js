// Инициализация всех модулей
document.addEventListener('DOMContentLoaded', () => {
    console.log('All modules initialized');
});

// Обработчик для кнопки "назад" в хлебных крошках
document.querySelectorAll('.arrow-left').forEach(arrow => {
    arrow.addEventListener('click', () => {
        history.back();
    });
});

function updateChatCounter() {
    fetch('/chat/unread_count/')
        .then(response => response.json())
        .then(data => {
            const counter = document.getElementById('chat-counter');
            if (data.unread_count > 0) {
                counter.textContent = data.unread_count;
                counter.style.display = 'inline-block';
            } else {
                counter.style.display = 'none';
            }
        });
}