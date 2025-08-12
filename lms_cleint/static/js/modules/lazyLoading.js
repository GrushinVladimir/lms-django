document.addEventListener('DOMContentLoaded', () => {
    // Функция для отметки SVG как загруженных
    const markSvgAsLoaded = (svg) => {
        svg.setAttribute('data-loaded', 'true');
    };

    // Обработка существующих SVG
    document.querySelectorAll('svg').forEach(svg => {
        markSvgAsLoaded(svg);
    });

    // MutationObserver для динамически добавляемых SVG
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    if (node.tagName === 'SVG') {
                        markSvgAsLoaded(node);
                    }
                    node.querySelectorAll('svg').forEach(svg => {
                        markSvgAsLoaded(svg);
                    });
                }
            });
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});