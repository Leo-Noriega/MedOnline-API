function mostrarToastGlobal(options) {
    const { type = 'info', message = '', buttons = [] } = options;

    const toastContainer = document.createElement('div');
    toastContainer.className = `toast align-items-center bg-section text-${type} border-0 text-center position-fixed top-50 start-50 translate-middle zindex-toast`;
    toastContainer.setAttribute('role', 'alert');
    toastContainer.setAttribute('aria-live', 'assertive');
    toastContainer.setAttribute('aria-atomic', 'true');
    const buttonHtml = buttons.map((button) => `
        <button type="button" class="${button.className} mx-1" id="${button.id || ''}">${button.label}</button>
    `).join('');

    toastContainer.innerHTML = `
        <div class="toast-body">
            ${message}
            ${buttons.length > 0 ? `<div class="d-flex justify-content-end mt-2">${buttonHtml}</div>` : ''}
        </div>
    `;

    document.body.appendChild(toastContainer);

    const toastElement = new bootstrap.Toast(toastContainer);
    toastElement.show();

    buttons.forEach(button => {
        const btnElement = document.getElementById(button.id);
        if (btnElement && typeof button.onClick === 'function') {
            btnElement.addEventListener('click', () => {
                button.onClick();
                toastElement.hide();
                toastContainer.remove();
            });
        }
    });

    toastElement._element.addEventListener('hidden.bs.toast', () => {
        toastContainer.remove();
    });
}