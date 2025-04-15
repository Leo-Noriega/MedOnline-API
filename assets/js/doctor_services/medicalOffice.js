let doctorId = null;

const userId = document.getElementById('consultorios').dataset.userId;

async function fetchDoctorData(callback) {
    const endpoint = `/especialista/details/${userId}/`;

    try {
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (!response.ok) {
            throw new Error('No se pudo obtener la información del usuario');
        }

        const data = await response.json();
        callback(data);
        doctorId = data.doctor.id;
    } catch (error) {
        console.error('Error:', error);
        alert('Hubo un error al cargar la información del usuario');
    }
}

function renderUserInfo(data) {
    const consultorios = document.getElementById('consultorios');
    consultorios.innerHTML = '';

    if (data.addresses.length === 0) {
        consultorios.innerHTML = `
            <p class="text-center text mt-3">
                Agrega aquí los consultorios en los que puedes brindar consulta a tus pacientes 
                <i class="bi bi-hospital text-second"></i>
            </p>`;
        return;
    }

    data.addresses.forEach(address => {
        const div = document.createElement('div');
        div.classList.add('my-3', 'd-flex', 'bg-primary-color', 'py-2', 'px-2', 'rounded', 'justify-content-between', 'row', 'shadow-sm', 'align-items-center');
        div.innerHTML = `
            <div class="p-3 text row">
                <div class="col-12 col-md-6">
                    <div class="text-second fw-medium mb-3 d-inline-flex flex-column">
                        <h6>${address.clinic_name}</h6>
                        <hr class="borde-hr">
                    </div>
                    <div>${address.city}, ${address.street}</div>
                    <div>${address.postal_code}, ${address.state}</div>
                </div>
                <div class="d-flex row col-12 col-md-6 justify-content-end m-auto align-items-center p-2">
                    <button class="button-edit m-1 col-sm-12 col-md-7" onclick="openModal(${address.id})">Modificar dirección</button>
                    <button class="button-principal bg-secondary m-1 col-sm-12 col-md-3" onclick="deleteAddress(${address.id})">Eliminar</button>
                </div>
            </div>`;
        consultorios.appendChild(div);
    });
}

async function openModal(addressId = null) {
    const modal = document.getElementById('modal');
    modal.style.display = 'flex';

    const title = document.getElementById('modal-title');
    const form = document.getElementById('address-form');

    if (addressId) {
        title.innerText = 'Modificar dirección del consultorio';
        form.dataset.addressId = addressId;

        try {
            const response = await fetch(`/especialista/addresses/${addressId}/`, { method: 'GET' });

            if (!response.ok) throw new Error("No se pudo obtener la dirección");

            const address = await response.json();
            document.getElementById('clinic-name').value = address.clinic_name || '';
            document.getElementById('street').value = address.street || '';
            document.getElementById('city').value = address.city || '';
            document.getElementById('state').value = address.state || '';
            document.getElementById('postal-code').value = address.postal_code || '';
        } catch (error) {
            console.error('Error al cargar la dirección:', error);
            alert("Error al cargar la dirección.");
        }
    } else {
        title.innerText = '¿En dónde trabajas?';
        form.dataset.addressId = '';
        resetFormValidation();
    }
}

function validateInput(input) {
    const isValid = input.checkValidity();
    input.classList.toggle('is-valid', isValid);
    input.classList.toggle('is-invalid', !isValid);
    return isValid;
}

async function saveAddress(addressId = null) {
    const clinicName = document.getElementById('clinic-name').value.trim();
    const street = document.getElementById('street').value.trim();
    const city = document.getElementById('city').value.trim();
    const state = document.getElementById('state').value.trim();
    const postalCode = document.getElementById('postal-code').value.trim();

    if (!clinicName || !street || !city || !state || !postalCode) {
        mostrarToastGlobal({
            type: 'danger',
            message: 'Todos los campos son obligatorios.'
        });
        return;
    }

    const data = { clinic_name: clinicName, street, city, state, postal_code: postalCode, doctor: doctorId };
    const method = addressId ? "PUT" : "POST";
    const url = addressId ? `/especialista/addresses/${addressId}/` : `/especialista/addresses/`;

    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json; charset=UTF-8' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Error al guardar la dirección");
        }

        mostrarToastGlobal({ type: 'success', message: 'Dirección guardada exitosamente.' });
        closeModal();
    } catch (error) {
        console.error("Error al guardar la dirección:", error);
        mostrarToastGlobal({ type: 'danger', message: 'Hubo un problema al guardar la dirección.' });
    }
}

async function deleteAddress(addressId) {
    try {
        const response = await fetch(`/especialista/addresses/${addressId}/`, { method: "DELETE" });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Error al eliminar el consultorio");
        }

        mostrarToastGlobal({ type: 'success', message: 'Consultorio eliminado exitosamente.' });
        closeModal();
    } catch (error) {
        console.error("Error al eliminar el consultorio:", error);
        mostrarToastGlobal({ type: 'danger', message: 'Hubo un problema al eliminar la dirección.' });
    }
}

function resetFormValidation() {
    const form = document.getElementById('address-form');
    const inputs = form.querySelectorAll('input');

    inputs.forEach(input => {
        input.classList.remove('is-valid', 'is-invalid');
    });

    form.reset();
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
    resetFormValidation();
    fetchDoctorData(renderUserInfo);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchDoctorData(renderUserInfo);

    const form = document.getElementById('address-form');
    const inputs = form.querySelectorAll('input');

    inputs.forEach(input => {
        input.addEventListener('input', () => validateInput(input));
        input.addEventListener('blur', () => validateInput(input));
    });

    form.addEventListener('submit', event => {
        event.preventDefault();
        const isValid = Array.from(inputs).every(input => validateInput(input));
        if (isValid) saveAddress(form.dataset.addressId || null);
    });
});