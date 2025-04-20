function mostrarToastGlobal(options) {
    const { type = 'info', message = '', buttons = [] } = options;

    const toastContainer = document.createElement('div');
    toastContainer.className = `toast align-items-center bg-section text-${type} border-0 text-center position-fixed top-50 start-50 translate-middle`;
    toastContainer.setAttribute('role', 'alert');
    toastContainer.setAttribute('aria-live', 'assertive');
    toastContainer.setAttribute('aria-atomic', 'true');

    // Generar HTML para los botones
    const buttonHtml = buttons.map((button, index) => {
        const buttonId = button.id || `toast-button-${index}`; // Generar un id único si no se proporciona
        button._generatedId = buttonId; // Guardar el id generado en el objeto del botón
        return `
            <button type="button" class="${button.className} mx-1" id="${buttonId}">${button.label}</button>
        `;
    }).join('');

    // Crear el contenido del toast
    toastContainer.innerHTML = `
        <div class="toast-body">
            ${message}
            ${buttons.length > 0 ? `<div class="d-flex justify-content-end mt-2">${buttonHtml}</div>` : ''}
        </div>
    `;

    document.body.appendChild(toastContainer);

    const toastElement = new bootstrap.Toast(toastContainer);
    toastElement.show();

    // Vincular eventos onClick a los botones
    buttons.forEach(button => {
        const btnElement = document.getElementById(button._generatedId); // Usar el id generado
        if (btnElement && typeof button.onClick === 'function') {
            btnElement.addEventListener('click', () => {
                button.onClick();
                toastElement.hide();
                toastContainer.remove();
            });
        }
    });

    // Eliminar el toast del DOM cuando se oculta
    toastElement._element.addEventListener('hidden.bs.toast', () => {
        toastContainer.remove();
    });
}