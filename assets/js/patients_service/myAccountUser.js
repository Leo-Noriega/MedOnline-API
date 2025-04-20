let userId = document.getElementById('info-user').dataset.userId;

function fetchUserData(callback) {
    const endpoint = `/users/api/${userId}/`;
    fetch(endpoint, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo obtener la información del usuario');
            }
            return response.json();
        })
        .then(data => {
            callback(data);
            console.log(data);
        })
        .catch(error => {
            console.error(error);
            alert('Hubo un error al cargar la información del usuario');
        });
}

function renderUserInfo(data) {
    const mainContainer = document.getElementById('info-user');
    mainContainer.innerHTML = "";
    const userCard = `
        <div class="d-flex justify-content-between mb-3">
            <img id="photo-preview" src="${data.photo || '/media/default.png'}" class="rounded-circle" alt="foto de perfil" style="height: 50px; width: 50px;">
            <button class="button-edit" onclick='editUser()'>Editar</button>
        </div>
        <div class="text row">
            ${createField("Nombre", data.name)}
            ${createField("Apellidos", data.surnames)}
            ${createField("Teléfono", data.phone)}
            ${createField("Correo electrónico", data.email)}
        </div>`;
    mainContainer.innerHTML = userCard;
}

function createField(label, value) {
    return `<div class="col-md-4 col-sm-6 col-12"> 
                <p class="text-title fw-semibold mb-0">${label}:</p>
                <p>${value}</p>
            </div>`;
}

function editUser() {
    fetchUserData(renderEditForm);
}

function renderEditForm(data) {
    const mainContainer = document.getElementById('info-user');
    mainContainer.innerHTML = `
        <div class="d-flex justify-content-start mb-3 align-items-center">
            <img id="photo-preview" src="${data.photo || '/media/default.png'}" class="rounded-circle" alt="foto de perfil" style="height: 50px; width: 50px;">
            <input type="file" id="photo-input" style="display: none;" accept="image/*">
            <button class="button-edit" onclick="document.getElementById('photo-input').click()">Cambiar foto</button>
        </div>
        <div class="text row">
            ${createInputField("Nombre", data.name, "name")}
            ${createInputField("Apellidos", data.surnames, "surnames")}
            ${createInputField("Teléfono", data.phone, "phone")}
            ${createInputField("Correo electrónico", data.email, "email")}
            ${createInputField("Nueva contraseña", "", "password", "password")}
            ${createInputField("Confirmación de contraseña", "", "confirm_password", "password")}
            <div class="col-12 d-flex justify-content-end my-2">
                <button class="button-edit mx-3 fw-medium" onclick="fetchUserData(renderUserInfo)">Cancelar</button>
                <button type="submit" id="save-button" class="button-principal fw-medium" disabled onclick="updateUser()">Guardar</button>
            </div>
        </div>`;

    const photoInput = document.getElementById('photo-input');
    const photoPreview = document.getElementById('photo-preview');
    photoInput.addEventListener('change', () => {
        const file = photoInput.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                photoPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            alert('El archivo seleccionado no es una imagen válida.');
        }
    });

    validaciones();
    toggleSaveButton();
}

function createInputField(label, value, id, type = "text") {
    return `
        <div class="col-md-4 col-sm-6 col-12 my-2">
            <label class="text-title fw-semibold mb-0">${label}:</label>
            <input id="${id}" class="form-control" type="${type}" value="${value}" data-edited="false" />
            <div class="invalid-feedback">Este campo es inválido.</div>
        </div>`;
}

function validaciones() {
    const inputs = document.querySelectorAll('.form-control');

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            input.setAttribute('data-edited', 'true'); 
            validacionInput(input);
            toggleSaveButton();
        });
        input.addEventListener('blur', () => {
            validacionInput(input);
            toggleSaveButton();
        });
    });
}

function validacionInput(input) {
    let pattern;
    let isValid = true;
    let errorMessage = '';
    switch (input.id) {
        case 'name':
        case 'surnames':
            pattern = /^[a-zA-ZÀ-ÿ\s]{3,100}$/;
            if (!pattern.test(input.value.trim())) {
                isValid = false;
                errorMessage = 'Debe contener entre 3 y 100 caracteres y solo incluir letras.';
            }
            break;
        case 'phone':
            pattern = /^(?:\+52\s?)?(\d{2,3})?\s?\d{10}$/;
            if (!pattern.test(input.value.trim())) {
                isValid = false;
                errorMessage = 'Debe ser un número válido, con 10 dígitos, opcionalmente incluyendo la lada (+52).';
            }
            break;
        case 'email':
            pattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
            if (!pattern.test(input.value.trim()) || input.value.length < 11 || input.value.length > 250) {
                isValid = false;
                errorMessage = 'Debe ser un correo electrónico válido y contener entre 11 y 250 caracteres.';
            }
            break;
        case 'password':
        case 'confirm_password':
            pattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/;
            if (!pattern.test(input.value.trim())) {
                isValid = false;
                errorMessage = 'Debe tener al menos 8 caracteres, incluyendo una letra mayúscula, un número y un carácter especial.';
            }
            break;
        default:
            break;
    }

    const feedbackElement = input.nextElementSibling;

    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        if (feedbackElement) {
            feedbackElement.textContent = '';
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        if (feedbackElement) {
            feedbackElement.textContent = errorMessage;
        }
    }

    return isValid;
}

function toggleSaveButton() {
    const inputs = document.querySelectorAll('.form-control');
    const saveButton = document.getElementById('save-button');
    let allValid = true;

    inputs.forEach(input => {
        if (input.getAttribute('data-edited') === 'true' && !input.classList.contains('is-valid')) {
            allValid = false;
        }
    });

    saveButton.disabled = !allValid;
}

function updateUser() {
    if (!userId) {
        mostrarToastGlobal({
            type: '',
            message: 'No se pudo obtener el ID del usuario.',
        });
        return;
    }

    mostrarToastGlobal({
        type: '',
        message: '¿Estás seguro de que deseas actualizar tu información?',
        buttons: [
            {
                label: 'Cancelar',
                className: 'button-edit',
                onClick: () => {
                    mostrarToastGlobal({
                        type: '',
                        message: 'La actualización fue cancelada.',
                    });
                },
            },
            {
                label: 'Confirmar',
                className: 'button-principal',
                onClick: () => {
                    const data = new FormData();
                    const fields = ["name", "surnames", "phone", "email", "password", "confirm_password"];

                    fields.forEach(field => {
                        const value = document.getElementById(field)?.value;
                        if (value) {
                            data.append(field, value);
                        }
                    });

                    if (data.get("password") && data.get("password") !== data.get("confirm_password")) {
                        mostrarToastGlobal({
                            type: 'danger',
                            message: 'Las contraseñas no coinciden.',
                        });
                        return;
                    }
                    data.delete("confirm_password");

                    const photoInput = document.getElementById('photo-input');
                    if (photoInput.files.length > 0) {
                        const file = photoInput.files[0];
                        if (file.type.startsWith('image/')) {
                            data.append('photo', file);
                        } else {
                            mostrarToastGlobal({
                                type: 'danger',
                                message: 'El archivo seleccionado no es una imagen válida.',
                            });
                            return;
                        }
                    }

                    const csrfToken = getCSRFToken();

                    fetch(`/users/api/${userId}/`, {
                        method: "PUT",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                        },
                        body: data
                    })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Error al actualizar la información del usuario');
                            }
                            return response.json();
                        })
                        .then(result => {
                            mostrarToastGlobal({
                                type: 'success',
                                message: 'La información del usuario se actualizó correctamente.',
                            });
                            fetchUserData(renderUserInfo);
                        })
                        .catch(error => {
                            console.error("Error en la actualización:", error);
                            mostrarToastGlobal({
                                type: 'danger',
                                message: 'Hubo un error al actualizar la información del usuario.',
                            });
                        });
                },
            },
        ],
    });
}

function getCSRFToken() {
    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}

document.addEventListener('DOMContentLoaded', () => {
    fetchUserData(renderUserInfo);
});