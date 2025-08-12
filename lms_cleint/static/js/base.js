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