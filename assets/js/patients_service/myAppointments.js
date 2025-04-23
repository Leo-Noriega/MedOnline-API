function fetchAppointmentsUser() {
    const userId = document.getElementById("appointments").dataset.userId;
    if (!userId) {
        console.error("User ID not found in data attribute.");
        return;
    }
    const url = `/appointments/api/by-user/?user_id=${userId}`;
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('No se pudo obtener la información de las citas.');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        renderAppointments(data);
    })
    .catch(error => {
        console.error(error);
    });
}

function cancelAppointment(appointmentId) {
    mostrarToastGlobal({
        type: '',
        message: '¿Estás seguro de que deseas cancelar esta cita? Esta acción es irreversible.',
        buttons: [
            {
                label: 'Cancelar',
                className: 'button-edit',
                onClick: () => {
                    console.log('Acción cancelada por el usuario.');
                }
            },
            {
                label: 'Confirmar',
                className: 'button-principal',
                onClick: () => {
                    fetch(`/appointments/api/${appointmentId}/`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('No se pudo cancelar la cita.');
                        }
                        return response.text().then(text => text ? JSON.parse(text) : {});
                    })
                    .then(() => {
                        console.log('Cita cancelada exitosamente.');
                        mostrarToastGlobal({
                            type: 'success',
                            message: 'La cita ha sido cancelada exitosamente.'
                        });
                        fetchAppointmentsUser();
                    })
                    .catch(error => {
                        console.error(error);
                        mostrarToastGlobal({
                            type: 'danger',
                            message: 'Ocurrió un error al intentar cancelar la cita.'
                        });
                    });
                }
            }
        ]
    });
}

function renderAppointments(appointments) {
    const appointmentsContainer = document.getElementById("appointments");
    appointmentsContainer.innerHTML = "";

    const currentDate = new Date();

    const futureAppointments = appointments.filter(appointment => new Date(appointment.appointment_date) >= currentDate);
    const pastAppointments = appointments.filter(appointment => new Date(appointment.appointment_date) < currentDate);

    const renderAppointmentList = (appointmentList) => {
        appointmentList.forEach(appointment => {
            const address = appointment.address_details || {};
            const doctorPhoto = appointment.doctor_photo || "media/default.png";
            const appointmentDate = new Date(appointment.appointment_date);
            const isPastAppointment = appointmentDate < currentDate;

            const appointmentHTML = `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row justify-content-between align-items-center">
                            <div class="d-flex align-items-center col-lg-8 col-md-6 col-12">
                                <img id="photo-preview" src="${doctorPhoto}" class="rounded-circle" alt="foto de perfil" style="height: 50px; width: 50px;">
                                <h6 class="text-title">${appointment.doctor_name} ${appointment.doctor_surnames}</h6>
                            </div>
                            <div class="d-flex text-end text-title col-lg-4 col-md-6 col-12">
                                <p class="p-0 me-2">Fecha: ${appointmentDate.toLocaleDateString()}</p>
                                <p class="p-0 m-0">Hora: ${appointmentDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                            </div>
                        </div>
                        <div class="container text">
                            <div class="row justify-content-between">
                                <div class="col-lg-8 col-12">
                                    <p><strong>Consultorio:</strong> ${address.clinic_name || "No especificado"}, ${address.street || ""}, ${address.city || ""}, ${address.state || ""}, CP: ${address.postal_code || ""}</p>
                                </div>
                                <div class="col-lg-4 col-12">
                                    <p><strong>Precio de la consulta:</strong> $${appointment.consultation_fee || "No especificado"}</p>
                                </div>
                            </div>
                            <div class="row justify-content-between">
                                <div class="col-lg-8 col-12">
                                ${
                                    appointment.patient_name && appointment.patient_surnames
                                        ? `<p><strong>Cita agendada para:</strong> ${appointment.patient_name} ${appointment.patient_surnames}</p>`
                                        : ""
                                }
                                </div>
                                <div class="col-lg-4 col-12">
                                    <p><strong>Servicio de la cita:</strong> ${appointment.note || "No especificado"}</p>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex justify-content-end">
                            ${!isPastAppointment ? `<button class="button-edit" onclick="cancelAppointment(${appointment.id})">Cancelar</button>` : ""}
                        </div>
                    </div>
                </div>
            `;
            appointmentsContainer.innerHTML += appointmentHTML;
        });
    };

    renderAppointmentList(futureAppointments);
    renderAppointmentList(pastAppointments);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchAppointmentsUser();
});