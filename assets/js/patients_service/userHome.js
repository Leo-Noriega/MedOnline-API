const weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
const { DateTime } = luxon;
let currentDoctorData = {};

function nanoToMinutes(nanoseconds) {
    return Math.floor(nanoseconds / 60000000000);
}

function formatTime(hours, minutes) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
}

function generateTimeSlots(startTime, endTime, durationMinutes) {
    const slots = [];
    const [startHour, startMinute] = startTime.split(':').map(Number);
    const [endHour, endMinute] = endTime.split(':').map(Number);

    let currentHour = startHour;
    let currentMinute = startMinute;

    while (currentHour < endHour || (currentHour === endHour && currentMinute < endMinute)) {
        slots.push(formatTime(currentHour, currentMinute));
        currentMinute += durationMinutes;

        if (currentMinute >= 60) {
            currentHour += Math.floor(currentMinute / 60);
            currentMinute = currentMinute % 60;
        }
    }

    return slots;
}

function renderSchedule(containerId, scheduleData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const today = new Date();
    const currentWeekday = scheduleData.current_weekday;
    const currentTime = scheduleData.current_time;

    const orderedDays = [];
    for (let i = currentWeekday; i <= 7; i++) {
        const dayData = scheduleData.schedule.find(d => d.weekday === i);
        if (dayData) orderedDays.push(dayData);
    }
    for (let i = 1; i < currentWeekday; i++) {
        const dayData = scheduleData.schedule.find(d => d.weekday === i);
        if (dayData) orderedDays.push(dayData);
    }

    let tabsHtml = '<div class="day-tabs">';
    let contentHtml = '';

    orderedDays.forEach((dayData, index) => {
        const isActive = index === 0;
        const isToday = dayData.weekday === currentWeekday;

        const dateParts = dayData.date.split('-');
        const year = parseInt(dateParts[0]);
        const month = parseInt(dateParts[1]);
        const day = parseInt(dateParts[2]);

        const dateStr = dayData.date;
        const dayName = isToday ? 'Hoy' : dayData.weekday_label;

        tabsHtml += `<div class="day-tab ${isActive ? 'active' : ''}" data-day="${dayData.weekday}">
    ${dayName} ${day}/${month}
</div>`;

        contentHtml += `
    <div class="day-content ${isActive ? 'active' : ''}" id="day-${dayData.weekday}-content">
        <div class="time-slots-container">
            ${dayData.slots.map(slot => {
            const isPast = isToday && slot.time <= currentTime;
            const isBooked = slot.status !== null;

            let slotClass = 'time-slot';
            if (isPast) slotClass += ' time-slot-past';
            if (isBooked) slotClass += ' time-slot-booked';

            let slotTitle = '';
            if (isPast) slotTitle = 'Este horario ya no está disponible';
            if (isBooked) slotTitle = 'Este horario está reservado';

            let slotIcon = '';
            if (isBooked) slotIcon = '<i class="fas fa-lock"></i> ';
            return `
                    <div class="${slotClass}" 
                         data-date="${dateStr}" 
                         data-time="${slot.time}"
                         data-day="${dayData.weekday}"
                         data-status="${slot.status || ''}"
                         ${slotTitle ? `title="${slotTitle}"` : ''}>
                        ${slotIcon}${slot.time}
                    </div>
                `;
        }).join('')}
        </div>
    </div>
`;
    });

    container.innerHTML = tabsHtml + '</div>' + contentHtml;

    container.querySelectorAll('.day-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            container.querySelectorAll('.day-tab').forEach(t => t.classList.remove('active'));
            container.querySelectorAll('.day-content').forEach(c => c.classList.remove('active'));

            this.classList.add('active');
            const day = this.getAttribute('data-day');
            document.getElementById(`day-${day}-content`).classList.add('active');
        });
    });

    container.querySelectorAll('.time-slot').forEach(slot => {
        const isPast = slot.classList.contains('time-slot-past');
        const isBooked = slot.classList.contains('time-slot-booked');

        if (!isPast && !isBooked) {
            slot.addEventListener('click', function () {
                const date = this.getAttribute('data-date');
                const time = this.getAttribute('data-time');
                const dayName = weekdays[this.getAttribute('data-day') - 1];
                handleTimeSlotSelection(scheduleData.doctor.id, date, time);
            });
        } else {
            slot.style.pointerEvents = 'none';

            if (isPast) {
                slot.style.opacity = '0.6';
            }
            if (isBooked) {
                slot.style.opacity = '0.8';
                slot.style.backgroundColor = '#f0f0f0';
                slot.style.borderColor = '#ccc';
                slot.style.color = '#666';
            }
        }
    });
}
function disablePastSlots(containerId, currentTime) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.querySelectorAll('.time-slot').forEach(slot => {
        const slotTime = slot.getAttribute('data-time');
        const slotDate = slot.getAttribute('data-date');
        const today = new Date().toISOString().split('T')[0];

        if (slotDate === today && slotTime <= currentTime) {
            slot.classList.add('time-slot-past');
            slot.title = 'Este horario ya no está disponible';
            slot.style.cursor = 'not-allowed';
            slot.style.opacity = '0.6';
            slot.onclick = null;
        }
    });
}

async function showDoctors(specialtyId, state) {
    try {
        const apiUrl = `http://localhost:8000/users/search-doctors/?specialty_id=${specialtyId}&state=${state}`;
        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();

        const resultsContainer = document.querySelector('#results .row');
        resultsContainer.innerHTML = '';

        data.doctors.forEach(doctor => {
            const scheduleContainerId = `schedule-${doctor.id}`;

            const card = `
    <div class="col-12 mb-4">
        <div class="card card-light p-4 rounded-4">
            <div class="row">
                <!-- Columna izquierda: Información del doctor -->
                <div class="col-md-6">
                    <div class="d-flex align-items-center">
                        <img src="../../../media/${doctor.photo}" alt="Doctor" class="profile-img me-3">
                        <div>
                            <h6 class="mb-0 fw-bold">${doctor.name} ${doctor.surnames}</h6>
                            <p class="mb-1 text-muted">${doctor.specialty}</p>

                            <div class="rating-container" style="cursor: pointer;">
                                <span>
                                    <i class="fas fa-star"></i>
                                    <i class="fas fa-star"></i>
                                    <i class="fas fa-star"></i>
                                    <i class="fas fa-star"></i>
                                    <i class="fas fa-star"></i>
                                </span>
                                <span class="ms-2">0 opiniones</span>
                            </div>
                        </div>
                    </div>
                    <hr>
                    <h6 class="fw-bold">Dirección</h6>
                    <!-- Nombre de clínica integrado en la dirección -->
                    <p class="mb-0">${doctor.clinic_name}, ${doctor.street}, ${doctor.city}, ${doctor.state},
                        ${doctor.postal_code}</p>
                </div>

                <!-- Columna derecha: Horarios -->
                <div class="col-md-6">
                    <h6 class="fw-bold">Horarios disponibles</h6>
                    <div id="${scheduleContainerId}" class="schedule-container"></div>
                </div>
            </div>
        </div>
    </div>
             <div class="modal fade" id="commentsModal" tabindex="-1">
<div class="modal-dialog">
<div class="modal-content">
    <div class="modal-header">
        <h5 class="modal-title">Comentarios</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
    </div>
    <div class="modal-body" id="commentsModalBody">
        Cargando comentarios...
    </div>
</div>
</div>
</div>
    
    `;

            resultsContainer.insertAdjacentHTML('beforeend', card);
            loadDoctorSchedule(doctor.id);
            updateDoctorRating(doctor.id);
        });
    } catch (error) {
        console.error("Error al realizar la consulta:", error);
        alert("Ocurrió un error al realizar la consulta.");
    }
}
function calculateDateForWeekday(targetWeekday, currentWeekday) {
    const date = new Date();
    const diff = (targetWeekday - currentWeekday + 7) % 7;
    date.setDate(date.getDate() + diff);
    return date;
}

async function loadDoctorSchedule(doctorId) {
    try {
        const response = await fetch(`/schedule/get_schedule/${doctorId}/`);
        if (!response.ok) throw new Error("Error al cargar horario");

        const scheduleData = await response.json();
        renderSchedule(`schedule-${doctorId}`, scheduleData);
    } catch (error) {
        console.error(`Error cargando horario para doctor ${doctorId}:`, error);
        document.getElementById(`schedule-${doctorId}`).innerHTML =
            '<div class="alert alert-warning">Error cargando horarios</div>';
    }
}

async function loadDoctorReviews(doctorId) {
    const modalBody = document.getElementById('commentsModalBody');
    modalBody.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary"></div></div>';
    try {
        const response = await fetch(`http://localhost:8000/reviews/api/?doctor_id=${doctorId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            }
        });
        if (!response.ok) throw new Error('Error al cargar comentarios');
        const reviews = await response.json();

        if (reviews.length === 0) {
            modalBody.innerHTML = '<div class="text-muted text-center py-3">Sin comentarios.</div>';
            return;
        }

        modalBody.innerHTML = reviews.map(review => {
            let starsHtml = '';
            for (let i = 1; i <= 5; i++) {
                starsHtml += i <= review.rating
                    ? '<i class="fas fa-star"></i>'
                    : '<i class="far fa-star"></i>';
            }
            return `
                <div class="mb-4 pb-2 border-bottom">
                    <div class="d-flex align-items-center mb-1">
                        ${starsHtml}
                        <span class="ms-2 text-secondary" style="font-size:0.95em;">${new Date(review.review_date).toLocaleDateString()}</span>
                    </div>
                    <div class="mb-1 fst-italic text-dark">${review.comment}</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        modalBody.innerHTML = '<div class="alert alert-warning">No se pudieron cargar los comentarios.</div>';
    }
}

function updateDoctorRating(doctorId) {
    fetch(`http://localhost:8000/reviews/api/?doctor_id=${doctorId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        }
    })
        .then(res => res.json())
        .then(reviews => {
            const card = document.getElementById(`schedule-${doctorId}`).closest('.card');
            if (!card) return;
            const ratingContainer = card.querySelector('.rating-container');
            if (!ratingContainer) return;

            const opinionsCount = reviews.length;
            let avgRating = 0;
            if (opinionsCount > 0) {
                avgRating = reviews.reduce((sum, r) => sum + r.rating, 0) / opinionsCount;
            }
            avgRating = Math.round(avgRating * 2) / 2;

            let starsHtml = '';
            for (let i = 1; i <= 5; i++) {
                if (i <= Math.floor(avgRating)) {
                    starsHtml += '<i class="fas fa-star"></i>';
                } else if (i - avgRating === 0.5) {
                    starsHtml += '<i class="fas fa-star-half-alt"></i>';
                } else {
                    starsHtml += '<i class="far fa-star"></i>';
                }
            }

            ratingContainer.innerHTML = `
                <span style="font-size:1.1em;">
                    ${starsHtml}
                </span>
                <span class="ms-2">${opinionsCount} opinion${opinionsCount === 1 ? '' : 'es'}</span>
            `;
        });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('.searchButton').addEventListener('click', () => {
        const specialtySelector = document.getElementById('specialtySelector');
        const stateSelector = document.getElementById('stateSelector');
        const specialtyId = specialtySelector.value;
        const state = stateSelector.value;

        if (specialtyId === "Especialidad" || state === "Estado") {
            alert("Por favor selecciona una especialidad y un estado.");
            return;
        }

        showDoctors(specialtyId, state);
    });
});

document.addEventListener('click', function (e) {
    const ratingContainer = e.target.closest('.rating-container');
    if (ratingContainer) {
        const card = ratingContainer.closest('.card');
        if (!card) return;

        const scheduleDiv = card.querySelector('[id^="schedule-"]');
        if (!scheduleDiv) return;
        const doctorId = scheduleDiv.id.replace('schedule-', '');
        loadDoctorReviews(doctorId);
        const modal = new bootstrap.Modal(document.getElementById('commentsModal'));
        modal.show();

    }
});

async function handleTimeSlotSelection(doctorId, date, time) {
    const selectedDateTime = `${date}T${time}:00`;
    const specialtyId = document.getElementById('specialtySelector').value;
    window.location.href = `/pacientes/reservar_cita/${doctorId}/${selectedDateTime}/${specialtyId}/`;
}

