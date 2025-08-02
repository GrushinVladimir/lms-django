// Включаем lazy-loading для всех img
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('img').forEach(img => {
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }
    });
});

// Ожидание загрузки скриптов
function scriptsLoaded() {
    return document.readyState === 'complete'
        ? Promise.resolve()
        : new Promise(resolve => window.addEventListener('load', resolve, { once: true }));
}

// Ожидание загрузки картинок
function imagesLoaded() {
    const images = Array.from(document.querySelectorAll('img'));
    if (!images.length) return Promise.resolve();

    return Promise.allSettled(
        images.map(img => {
            if (img.complete) return Promise.resolve();
            return new Promise(res => {
                img.addEventListener('load', res, { once: true });
                img.addEventListener('error', res, { once: true });
            });
        })
    );
}

// Прелоадер
Promise.all([imagesLoaded(), scriptsLoaded()])
    .then(() => {
        const preloader = document.querySelector('.preloader');
        if (!preloader) return;
        preloader.classList.add('hidden');
        preloader.addEventListener('transitionend', () => preloader.remove(), { once: true });
    });

// Dropdown
document.addEventListener('DOMContentLoaded', () => {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', e => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        document.addEventListener('click', e => {
            if (!dropdownMenu.contains(e.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    }
});

// jQuery init (select2 и teacher-info)
$(function () {
    $('.select-multiple').select2({
        placeholder: "Выберите варианты",
        allowClear: true,
        width: '100%'
    });

    $('.teacher-info').each(function() {
        const teacherId = $(this).data('teacher-id');
        if (teacherId) {
            // Здесь можно добавить дополнительную логику работы с teacherId
        }
    });
});


// jQuery init (если нужна select2 и обработка teacher-info)
$(function () {
    $('.select-multiple').select2({
        placeholder: "Выберите варианты",
        allowClear: true,
        width: '100%'
    });

    // teacher-info как в оригинале, без изменений
    $('.teacher-info').each(function() {
        const teacherId = $(this).data('teacher-id');
        if (teacherId) {
            // если будет логика обработки teacherId - она останется
        }
    });
});


(function monitorFPS() {
    // Конфигурация
    const config = {
        updateInterval: 500, // Как часто обновлять FPS (мс)
        rollingAverage: 10,   // Количество кадров для усреднения
        warnThreshold: 45    // Порог для предупреждения о просадке
    };
    
    // Состояние
    let lastTime = performance.now();
    let frameCount = 0;
    let frameTimes = [];
    let isScrolling = false;
    
    // Элемент для вывода
    const fpsDisplay = document.createElement('div');
    fpsDisplay.style = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 10px;
        font-family: monospace;
        border-radius: 4px;
        z-index: 9999;
    `;
    document.body.appendChild(fpsDisplay);
    
    // Отслеживание скролла
    window.addEventListener('scroll', () => {
        isScrolling = true;
        clearTimeout(window.scrollEndTimer);
        window.scrollEndTimer = setTimeout(() => {
            isScrolling = false;
        }, 200);
    }, {passive: true});
    
    // Функция обновления
    function updateFPS() {
        const now = performance.now();
        const delta = now - lastTime;
        frameCount++;
        
        if (delta >= config.updateInterval) {
            // Рассчет текущего FPS
            const currentFPS = Math.round((frameCount * 1000) / delta);
            
            // Добавление в историю
            frameTimes.push(currentFPS);
            if (frameTimes.length > config.rollingAverage) {
                frameTimes.shift();
            }
            
            // Усредненное значение
            const avgFPS = Math.round(frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length);
            
            // Цвет в зависимости от значения
            let color = '#0f0'; // зеленый
            if (avgFPS < 30) color = '#f00'; // красный
            else if (avgFPS < 50) color = '#ff0'; // желтый
            
            // Обновление дисплея
            fpsDisplay.innerHTML = `
                <div>FPS: <span style="color:${color}">${avgFPS}</span></div>
                <div>Current: ${currentFPS}</div>
                <div>Scrolling: ${isScrolling ? 'YES' : 'no'}</div>
                ${avgFPS < config.warnThreshold && isScrolling ? 
                    '<div style="color:#f88">⚠️ Scroll lag detected!</div>' : ''}
            `;
            
            // Сброс счетчика
            frameCount = 0;
            lastTime = now;
        }
        
        requestAnimationFrame(updateFPS);
    }
    
    // Запуск мониторинга
    updateFPS();
})();