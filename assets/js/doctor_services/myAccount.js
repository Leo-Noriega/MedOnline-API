let doctor_id = null;
function fetchDoctorData(callback) {
    const userId = document.getElementById('info-user').dataset.userId;
    if (!userId) {
        console.error("El user_id no está definido en el HTML.");
        return;
    }

    const endpoint = `/especialista/details/${userId}/`;

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
            doctor_id = data.doctor.id;
        })
        .catch(error => {
            console.error(error);
            alert('Hubo un error al cargar la información del usuario');
        });
}

document.addEventListener('DOMContentLoaded', () => {
    fetchDoctorData(renderUserInfo);
});

function renderUserInfo(data) {
    const mainContainer = document.getElementById('info-user');
    mainContainer.innerHTML = "";
    const userCard = `
<div class="d-flex justify-content-between mb-3">
    <img src="${data.doctor.photo || 'img/profile_placeholder.png'}" class="rounded-circle" alt="foto de perfil" style="height: 50px; width: 50px;">
    <button class="button-edit" onclick='editDoctor()'>Editar</button>
</div>
<div class="text row">
    ${createField("Nombre", data.doctor.name)}
    ${createField("Apellidos", data.doctor.surnames)}
    ${createField("Telefono", data.doctor.phone || "--")}
    ${createField("Correo electrónico", data.doctor.email)}
    ${createField("Precio de consulta", data.doctor.consultation_fee !== null ? `$${data.doctor.consultation_fee}` : "--")}
    ${createField("Duración de consulta", data.doctor.consultation_time !== null ? data.doctor.consultation_time : "--")}
</div>`;
    mainContainer.innerHTML = userCard;

    const especialidadesContainer = document.getElementById('especialidades');
    especialidadesContainer.innerHTML = "";

    if (data.specialties.length === 0) {
        especialidadesContainer.innerHTML = `<p class="text text-center">Registra aquí tus especialidades <i class="bi bi-clipboard-heart text-second"></i></p>`;
    } else {
        data.specialties.forEach(especialidad => {
            const div = document.createElement('div');
            div.classList.add('my-3', 'd-flex', 'bg-primary-color', 'py-2', 'px-2', 'rounded', 'justify-content-between', 'row');
            div.innerHTML = `
                <div class="col-12 col-md-6">${especialidad.specialty}</div> 
                <div class="d-flex col-12 col-md-6 justify-content-start justify-content-md-end">
                    <p class="fw-medium mb-0">Cédula profesional:</p> ${especialidad.license_number}
                </div>`;
            especialidadesContainer.appendChild(div);
        });
    }
}

function createField(label, value) {
    return `<div class="col-md-4 col-sm-6 col-12"> <p class="text-title fw-semibold mb-0">${label}:</p><p>${value}</p></div>`;
}

function agregar_especialidad() {
    const especialidadesContainer = document.getElementById('especialidades');
    const button = document.getElementById('agregar');
    if (button) {
        button.remove();
    }
    fetch('/especialista/specialty/')
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener las especialidades");
            }
            return response.json();
        })
        .then(data => {
            const div = document.createElement('div');
            div.id = 'especialidad-input';
            div.innerHTML = `
        <div class="d-flex row justify-content-between">
            <div class="col-12 col-sm-8 me-3">
                <label class="text-title fw-semibold mb-0">Especialidad:</label>
                <input list="opciones" id="especialidad-nombre" name="especialidad-nombre" placeholder="Escribe o selecciona" class="form-control px-3">
                <div class="invalid-feedback">Este campo es inválido.</div>
                <datalist id="opciones">
                    ${data.map(especialidad => `<option value="${especialidad.name}">`).join('')}
                </datalist>
            </div>
            <div class="col-12 col-sm-3">
                <label class="text-title fw-semibold mb-0">Cédula profesional:</label>
                <input type="text" id="especialidad-cedula" class="form-control" placeholder="Cédula profesional">
                <div class="invalid-feedback">Este campo es inválido.</div>
            </div>
        </div>
        <div class="col-12 d-flex justify-content-end my-2">
            <button class="button-edit mx-3 fw-medium" onclick="cancelarEspecialidad()">Cancelar</button>
            <button type="submit" class="button-principal fw-medium" onclick="guardarEspecialidad()">Guardar</button>
        </div>`;
            especialidadesContainer.appendChild(div);
            validaciones();
        })
        .catch(error => {
            console.error('Hubo un problema al cargar las especialidades:', error);
        });
}

function renderEditForm(data) {
    const mainContainer = document.getElementById('info-user');
    const userId = mainContainer.dataset.userId;

    mainContainer.innerHTML = `
    <div class="d-flex justify-content-start mb-3 align-items-center">
        <img id="photo-preview" src="${data.doctor.photo || '/media/user/default.png'}" class="rounded-circle" alt="foto de perfil" style="height: 50px; width: 50px;">
        <input type="file" id="photo-input" style="display: none;" accept="image/*">
        <button class="button-edit" onclick="document.getElementById('photo-input').click()">Cambiar foto</button>
    </div>
    <div class="text row">
        ${createInputField("Nombre", data.doctor.name, "name")}
        ${createInputField("Apellidos", data.doctor.surnames, "surnames")}
        ${createInputField("Teléfono", data.doctor.phone, "phone")}
        ${createInputField("Correo electrónico", data.doctor.email, "email")}
        ${createInputField("Precio de consulta", data.doctor.consultation_fee !== null ? data.doctor.consultation_fee : "", "consultation_fee")}
        ${createInputField("Duración de consulta", data.doctor.consultation_time !== null ? data.doctor.consultation_time : "", "consultation_time")}
        ${createInputField("Nueva contraseña", "", "password", "password")}
        ${createInputField("Confirmación de contraseña", "", "confirm_password", "password")}
        <div class="col-12 d-flex justify-content-end my-2">
            <button class="button-edit mx-3 fw-medium" onclick="fetchDoctorData(renderUserInfo)">Cancelar</button>
            <button type="submit" class="button-principal fw-medium" onclick="updateDoctor(${userId})">Guardar</button>
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
            mostrarToastGlobal({        
                type: 'danger',
                message: 'El archivo seleccionado no es una imagen válida.'
            });
        }
    });

    validaciones();
}

function createInputField(label, value, id, type = "text") {
    return `
<div class="col-md-4 col-sm-6 col-12 my-2">
    <label class="text-title fw-semibold mb-0">${label}:</label>
    <input id="${id}" class="form-control" type="${type}" value="${value}" />
    <div class="invalid-feedback">Este campo es inválido.</div>
</div>`;
}

function validaciones() {
    const inputs = document.querySelectorAll('.form-control');

    inputs.forEach(input => {
        input.addEventListener('input', () => validacionInput(input));
        input.addEventListener('blur', () => validacionInput(input));
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
        case 'consultation_fee':
            pattern = /^[1-9]\d*(\.\d{1,2})?$/;
            if (!pattern.test(input.value.trim())) {
                isValid = false;
                errorMessage = 'Debe ser un número positivo con hasta dos decimales.';
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
        case 'especialidad-nombre':
            pattern = /^[a-zA-ZÀ-ÿ\s]+$/;
            if (!pattern.test(input.value.trim())) {
                isValid = false;
                errorMessage = 'Solo puede incluir letras y espacios.';
            }
            break;
        case 'especialidad-cedula':
            pattern = /^[0-9]{7,8}$|^AESSA-[0-9]{7}$|^AE-[0-9]{7}$/;
            if (!pattern.test(input.value.trim())) {
                isValid = false;
                errorMessage = 'Debe ser un número de cédula válido (7-8 dígitos o con prefijos AESSA/AE).';
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

function editDoctor() { fetchDoctorData(renderEditForm); }

function getCSRFToken() {
    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}

function cancelarEspecialidad() {
    const especialidadesContainer = document.getElementById('especialidades');
    const div = document.getElementById('especialidad-input');
    if (div) {
        div.remove();
    }
    const agregarButton = document.createElement('button');
    agregarButton.className = 'button-edit';
    agregarButton.id = 'agregar';
    agregarButton.innerText = 'Agregar';
    agregarButton.onclick = agregar_especialidad;
    const parentContainer = document.getElementById('head-especialidades');
    parentContainer.appendChild(agregarButton);
}

function updateDoctor(userId) {
    mostrarToastGlobal({
        type: '',
        message: '¿Está seguro que desea actualizar la información del doctor?',
        buttons: [
            {
                id: 'confirmar',
                label: 'Confirmar',
                className: 'button-principal',
                onClick: () => {
                    realizarActualizacion(userId);
                }
            },
            {
                id: 'cancelar',
                label: 'Cancelar',
                className: 'button-edit',
                onClick: () => {
                    mostrarToastGlobal({
                        type: '',
                        message: 'Acción cancelada por el usuario'
                    });
                }
            }
        ]
    });
}

function realizarActualizacion(userId) {
    const data = new FormData();
    const fields = ["name", "surnames", "phone", "email", "consultation_fee", "consultation_time", "password", "confirm_password"];

    fields.forEach(field => {
        const value = document.getElementById(field)?.value;
        if (value) {
            data.append(field, value);
        }
    });

    if (data.get("password") && data.get("password") !== data.get("confirm_password")) {
        mostrarToastGlobal({
            type: 'danger',
            message: 'Las contraseñas no coinciden.'
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
                message: 'El archivo seleccionado no es una imagen válida.'
            });
            return;
        }
    }

    for (let pair of data.entries()) {
        console.log(pair[0] + ':', pair[1]);
    }

    const csrfToken = getCSRFToken();

    fetch(`/especialista/editar-doctor/${userId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: data
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            return response.json();
        })
        .then(result => {
            if (result.error) {
                mostrarToastGlobal({
                    type: 'danger',
                    message: `Error: ${result.error}`
                });
            } else {
                mostrarToastGlobal({
                    type: 'success',
                    message: 'Datos actualizados correctamente.'
                });
                fetchDoctorData(renderUserInfo);
            }
        })
        .catch(error => {
            console.error("Error en la actualización:", error);
            mostrarToastGlobal({
                type: 'danger',
                message: 'Ocurrió un error al actualizar la información.'
            });
        });
}

function guardarEspecialidad() {
    const specialtyName = document.getElementById("especialidad-nombre")?.value?.trim();
    const licenseNumber = document.getElementById("especialidad-cedula")?.value;

    if (!specialtyName || !licenseNumber) {
        mostrarToastGlobal({
            type: 'danger',
            message: 'Todos los campos son obligatorios'
        });
        return;
    }

    mostrarToastGlobal({
        type: '',
        message: '¿Está seguro que deseas registrar esta especialidad? Asegúrate de que la información es correcta.',
        buttons: [
            {
                id: 'confirmar',
                label: 'Confirmar',
                className: 'button-principal',
                onClick: () => {
                    const doctorId = doctor_id;
                    const data = {
                        doctor_id: doctorId,
                        specialty_name: specialtyName,
                        license_number: licenseNumber
                    };

                    const csrfToken = getCSRFToken();
                    fetch('/especialista/asociar-especialidad/', {
                        method: 'POST',
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken,
                            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                        },
                        body: JSON.stringify(data)
                    })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error("Error al asociar la especialidad");
                            }
                            return response.json();
                        })
                        .then(result => {
                            mostrarToastGlobal({
                                type: 'success',
                                message: 'Especialidad agregada correctamente'
                            });
                            fetchDoctorData(renderUserInfo);
                        })
                        .catch(error => {
                            console.error('Hubo un problema al asociar la especialidad:', error);
                            mostrarToastGlobal({
                                type: 'danger',
                                message: 'Hubo un problema al asociar la especialidad'
                            });
                        });

                    cancelarEspecialidad();
                }
            },
            {
                id: 'cancelar',
                label: 'Cancelar',
                className: 'button-edit',
                onClick: () => {
                    mostrarToastGlobal({
                        type: '',
                        message: 'Acción cancelada por el usuario'
                    });
                }
            }
        ]
    });
}
