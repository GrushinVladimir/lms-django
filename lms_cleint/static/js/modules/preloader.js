// Функция для проверки загрузки всех ресурсов, включая стили
async function checkResourcesLoaded() {
    // Проверяем загрузку всех изображений и SVG
    const mediaLoaded = () => {
        const mediaElements = Array.from(document.querySelectorAll('img, svg, [style*="background-image"]'));
        if (!mediaElements.length) return Promise.resolve();

        return Promise.allSettled(
            mediaElements.map(el => {
                if (el.complete || el.tagName === 'SVG') {
                    // Для SVG дополнительно проверяем загрузку стилей
                    if (el.tagName === 'SVG') {
                        return new Promise(resolve => {
                            requestAnimationFrame(() => {
                                // Проверяем, применены ли стили
                                const styles = window.getComputedStyle(el);
                                if (styles.display !== 'none' && styles.opacity !== '0') {
                                    resolve();
                                } else {
                                    setTimeout(resolve, 100);
                                }
                            });
                        });
                    }
                    return Promise.resolve();
                }
                return new Promise(resolve => {
                    el.addEventListener('load', resolve, { once: true });
                    el.addEventListener('error', resolve, { once: true });
                });
            })
        );
    };

    // Проверяем загрузку всех стилей
    const stylesLoaded = () => {
        return new Promise(resolve => {
            const checkStyles = () => {
                // Проверяем конкретные SVG элементы, которые должны иметь стили
                const svgElements = document.querySelectorAll('svg.logo, svg.uv-tick, svg.uv-sms, svg.arrow-left');
                let allStyled = true;
                
                svgElements.forEach(svg => {
                    const styles = window.getComputedStyle(svg);
                    if (styles.display === 'inline' || styles.opacity === '0') {
                        allStyled = false;
                    }
                });
                
                if (allStyled || document.readyState === 'complete') {
                    resolve();
                } else {
                    setTimeout(checkStyles, 50);
                }
            };
            
            checkStyles();
        });
    };

    // Проверяем загрузку всех скриптов
    const scriptsLoaded = () => {
        return document.readyState === 'complete'
            ? Promise.resolve()
            : new Promise(resolve => window.addEventListener('load', resolve, { once: true }));
    };

    return Promise.all([mediaLoaded(), stylesLoaded(), scriptsLoaded()]);
}

// Инициализация прелоадера
checkResourcesLoaded().then(() => {
    const preloader = document.querySelector('.preloader');
    if (!preloader) return;
    
    // Добавляем небольшую задержку для гарантированного применения всех стилей
    setTimeout(() => {
        preloader.classList.add('hidden');
        preloader.addEventListener('transitionend', () => preloader.remove(), { once: true });
    }, 200);
});