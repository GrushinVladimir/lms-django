
let isScrolling;
let hoverDisabled = false;

window.addEventListener('scroll', function() {
    // Отключаем hover при начале скролла
    if (!hoverDisabled) {
        document.body.classList.add('no-hover');
        hoverDisabled = true;
    }
    
    // Сбрасываем таймер при каждом событии скролла
    clearTimeout(isScrolling);
    
    // Включаем hover через 100мс после остановки скролла
    isScrolling = setTimeout(function() {
        document.body.classList.remove('no-hover');
        hoverDisabled = false;
    }, 100);
}, false);

SmoothScroll({
    animationTime: 500,  // Увеличиваем время анимации
    stepSize: 35,       // Уменьшаем шаг
    accelerationDelta: 10,
    accelerationMax: 12,
    keyboardSupport: true,
    arrowScroll: 30,
    pulseAlgorithm: true,
    pulseScale: 2,      // Уменьшаем масштаб пульсации
    pulseNormalize: 1,
    touchpadSupport: true
})

