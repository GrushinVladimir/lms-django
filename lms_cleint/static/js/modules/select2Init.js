// Удаляем импорт jQuery, так как он уже загружен глобально через script tag
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, что jQuery и Select2 доступны
    if (typeof $ !== 'undefined' && $.fn.select2) {
        $('.select-multiple').select2({
            placeholder: "Выберите варианты",
            allowClear: true,
            width: '100%'
        });

        $('.teacher-info').each(function() {
            const teacherId = $(this).data('teacher-id');
            if (teacherId) {
                // Дополнительная логика обработки teacherId
            }
        });
    } else {
        console.error('jQuery или Select2 не загружены');
    }
});