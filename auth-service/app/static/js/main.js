// Основные скрипты для админ-панели
document.addEventListener('DOMContentLoaded', function() {
    // Активация всплывающих подсказок
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Подтверждение действий
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });
    
    // Автофокус на поля форм
    const autofocusField = document.querySelector('[autofocus]');
    if (autofocusField) {
        autofocusField.focus();
    }
});