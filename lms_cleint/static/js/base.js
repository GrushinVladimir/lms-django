 // Функция для проверки загрузки всех скриптов что бы закерыть лодер
function scriptsLoaded() {
    return new Promise((resolve) => {
        if (document.readyState === 'complete') {
            resolve();
        } else {
            window.addEventListener('load', resolve);
        }
    });
}


function imagesLoaded() {
            const images = document.querySelectorAll('img');
            let loadedCount = 0;
            
            return new Promise((resolve) => {
                if (images.length === 0) {
                    resolve();
                    return;
                }
                
                images.forEach(img => {
                    if (img.complete) {
                        loadedCount++;
                    } else {
                        img.addEventListener('load', () => {
                            loadedCount++;
                            if (loadedCount === images.length) resolve();
                        });
                        img.addEventListener('error', () => {
                            loadedCount++;
                            if (loadedCount === images.length) resolve();
                        });
                    }
                });
                
                if (loadedCount === images.length) resolve();
            });
        }
        // Ждем загрузки всех ресурсов
Promise.all([
    imagesLoaded(),
    scriptsLoaded(),
    new Promise(resolve => setTimeout(resolve, 800)) // Увеличено минимальное время показа
]).then(() => {
    const preloader = document.querySelector('.preloader');
    
    // Сначала плавно скрываем
    preloader.classList.add('hidden');
    
    // Удаляем только после завершения анимации
    preloader.addEventListener('transitionend', () => {
        preloader.remove();
    }, { once: true });
});
document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        // Закрытие при клике вне меню
        document.addEventListener('click', function() {
            dropdownMenu.classList.remove('show');
        });
    }
});

        $(document).ready(function() {
            $('.select-multiple').select2({
                placeholder: "Выберите варианты",
                allowClear: true,
                width: '100%'
            });
            
            // Добавляем title для элементов с информацией о преподавателе
            $('.teacher-info').each(function() {
                const teacherId = $(this).data('teacher-id');
                if (teacherId) {}
            });
        });
