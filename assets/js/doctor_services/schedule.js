function getStatusText(status) {
    const statusMap = {
        1: "Pendiente",
        2: "Confirmada",
        3: "Cancelada",
        4: "Completada"
    };
    return statusMap[status] || "Desconocido";
}

let calendar;

document.addEventListener("DOMContentLoaded", () => {
    // Obtener los valores de doctor_id y doctor_time desde los atributos data-*
    const calendarElement = document.getElementById("calendar");
    const scheduleElement = document.getElementById("schedule");
    const doctorId = calendarElement.dataset.doctorId;
    const doctorTime = calendarElement.dataset.doctorTime;

    if (!doctorId || !doctorTime) {
        console.error("El doctor_id o doctor_time no están definidos en el HTML.");
        return;
    }

    // Inicializar el calendario
    calendar = new FullCalendar.Calendar(calendarElement, {
        initialView: 'timeGridWeek',
        initialDate: new Date(),
        allDaySlot: false,
        locale: 'es',
        timeZone: 'local',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,timeGridDay'
        },
        editable: false,
        slotMinTime: "00:00:00",
        slotMaxTime: "23:00:00",
        events: function (fetchInfo, successCallback, failureCallback) {
            fetch(`/appointments/doctor/${doctorId}/appointments/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Error al obtener las citas");
                    }
                    return response.json();
                })
                .then(data => {
                    const timeParts = doctorTime.split(':');
                    const durationMinutes = parseInt(timeParts[0], 10) * 60 + parseInt(timeParts[1], 10);

                    const events = data.map(appointment => {
                        const startDate = new Date(appointment.appointment_date);
                        const endDate = new Date(startDate);
                        endDate.setMinutes(startDate.getMinutes() + durationMinutes);

                        let backgroundColor;
                        switch (appointment.status) {
                            case 1: // Pendiente
                                backgroundColor = '#f7dc6f';
                                break;
                            case 2: // Confirmada
                                backgroundColor = '#28a745';
                                break;
                            case 3: // Cancelada
                                backgroundColor = '#dc3545';
                                break;
                            case 4: // Completada
                                backgroundColor = '#2E5077';
                                break;
                            default:
                                backgroundColor = '#6c757d';
                        }

                        return {
                            id: appointment.id,
                            title: `${appointment.patient_name} ${appointment.patient_surnames}`,
                            start: startDate.toISOString(),
                            end: endDate.toISOString(),
                            allDay: false,
                            backgroundColor: backgroundColor,
                            borderColor: backgroundColor,
                            extendedProps: {
                                status: appointment.status,
                                note: appointment.note,
                                phone: appointment.phone
                            }
                        };
                    });

                    successCallback(events);
                })
                .catch(error => {
                    console.error("Error al cargar las citas:", error);
                    failureCallback(error);
                });
        },

        eventMouseEnter: function (info) {
            const tooltip = document.createElement('div');
            tooltip.className = 'event-tooltip';
            tooltip.style.position = 'absolute';
            tooltip.style.zIndex = '1000';
            tooltip.style.background = '#fff';
            tooltip.style.border = '1px solid #ccc';
            tooltip.style.padding = '10px';
            tooltip.style.borderRadius = '5px';
            tooltip.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.2)';
            tooltip.innerHTML = `
                <strong>Paciente:</strong> ${info.event.title}<br>
                <strong>Servicio:</strong> ${info.event.extendedProps.note}<br>
                <strong>Teléfono:</strong> ${info.event.extendedProps.phone}<br>
                <strong>Estado:</strong> ${getStatusText(info.event.extendedProps.status)}
            `;

            document.body.appendChild(tooltip);

            info.el.addEventListener('mousemove', function (e) {
                tooltip.style.top = e.pageY + 10 + 'px';
                tooltip.style.left = e.pageX + 10 + 'px';
            });

            info.el.tooltip = tooltip;
        },

        eventMouseLeave: function (info) {
            if (info.el.tooltip) {
                info.el.tooltip.remove();
                info.el.tooltip = null;
            }
        },

        eventClick: function (info) {
            const appointmentId = info.event.id;
            const appointmentStatus = info.event.extendedProps.status;
            const appointmentDate = new Date(info.event.start);
            const now = new Date();

            if (appointmentStatus === 4) {
                mostrarToastGlobal({
                    type: 'text',
                    message: 'Esta cita ya está completada y no se puede modificar.',
                    buttons: [
                        {
                            label: 'Cerrar',
                            className: 'button-edit',
                            onClick: () => cerrarToast()
                        }
                    ]
                });
                return;
            }

            if (appointmentDate < now) {
                mostrarToastGlobal({
                    type: 'text',
                    message: 'Esta cita ya pasó. Solo puedes marcarla como completada.',
                    buttons: [
                        {
                            label: 'Completar',
                            className: 'button-principal',
                            id: 'btn-complete',
                            onClick: () => confirmAppointmentStatus(appointmentId, 4, 'Completada')
                        },
                        {
                            label: 'Cerrar',
                            className: 'button-edit',
                            onClick: () => {
                                cerrarToast();
                            }
                        }
                    ]
                });
                return;
            }

            mostrarToastGlobal({
                type: 'text',
                message: '¿Qué acción deseas realizar con esta cita?',
                buttons: [
                    {
                        label: 'Confirmar',
                        className: 'button-principal',
                        id: 'btn-confirm',
                        onClick: () => confirmAppointmentStatus(appointmentId, 2, 'Confirmada')
                    },
                    {
                        label: 'Cancelar',
                        className: 'button-edit',
                        id: 'btn-cancel',
                        onClick: () => confirmAppointmentStatus(appointmentId, 3, 'Cancelada')
                    },

                ]
            });
        }
    });

    calendar.render();

    const weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
    let isEditing = false;

    const getCSRFToken = () => {
        const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    };

    const handleError = (message) => {
        console.error(message);
        alert(message);
    };

    const renderSchedule = (data = []) => {
        const rows = weekdays.map((day, index) => {
            const dayData = data.find(schedule => schedule.weekday === index + 1);
            return `
        <tr>
            <td><p class="text-second m-0 fw-medium">${day}</p></td>
            <td>${dayData ? dayData.start_time : '--'}</td>
            <td>${dayData ? dayData.end_time : '--'}</td>
        </tr>
    `;
        }).join('');

        scheduleElement.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h5 class="text-title">Horario de trabajo</h5>
            <button class="button-edit" id="editButton">Editar</button>
        </div>
            <table class="table">
                <thead>
                    <tr>
                        <th><p class="text-principal m-0">Día</p></th>
                        <th><p class="text-principal m-0">Hora de inicio</p></th>
                        <th><p class="text-principal m-0">Hora de fin</p></th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
            
        `;

        document.getElementById("editButton").addEventListener("click", () => {
            isEditing = true;
            renderEditableSchedule(data);
        });
    };

    const renderEditableSchedule = (data = []) => {
        const rows = weekdays.map((day, index) => {
            const dayData = data.find(schedule => schedule.weekday === index + 1);
            return `
        <tr data-availability-id="${dayData ? dayData.id : ''}">
            <td><p class="m-0 text-second fw-medium">${day}</p></td>
            <td>
                <input type="checkbox" name="workday" ${dayData ? "checked" : ""}>
            </td>
            <td>
                <input type="time" class="form-control" name="start_time" value="${dayData ? dayData.start_time : ''}">
            </td>
            <td>
                <input type="time" class="form-control" name="end_time" value="${dayData ? dayData.end_time : ''}">
            </td>
        </tr>
    `;
        }).join('');

        scheduleElement.innerHTML = `
    <h5>Editar horario</h5>
    <table class="table">
        <thead>
            <tr>
                <th><p class="text-principal m-0">Día</p></th>
                <th><p class="text-principal m-0">Trabaja</p></th>
                <th><p class="text-principal m-0">Hora de inicio</p></th>
                <th><p class="text-principal m-0">Hora de fin</p></th>
            </tr>
        </thead>
        <tbody>${rows}</tbody>
    </table>
    <div class="d-flex justify-content-end">
        <button class="button-edit mt-3 me-2" id="cancelButton">Cancelar</button>
        <button class="button-principal mt-3" id="saveButton">Guardar</button>
    </div>
`;

        document.getElementById("saveButton").addEventListener("click", saveSchedule);
        document.getElementById("cancelButton").addEventListener("click", () => {
            isEditing = false;
            fetchSchedule();
        });
    };

    const saveSchedule = () => {
        const rows = scheduleElement.querySelectorAll("tbody tr");
        const updatedSchedule = [];
        const deletedSchedule = [];

        Array.from(rows).forEach((row, index) => {
            const works = row.querySelector("input[name='workday']").checked;
            const startTime = row.querySelector("input[name='start_time']").value;
            const endTime = row.querySelector("input[name='end_time']").value;

            const availabilityId = row.getAttribute("data-availability-id");

            if (works) {
                updatedSchedule.push({
                    doctor_id: doctorId,
                    weekday: index + 1,
                    start_time: startTime,
                    end_time: endTime,
                });
            } else if (availabilityId) {
                deletedSchedule.push(availabilityId);
            }
        });

        mostrarToastGlobal({
            type: 'text',
            message: '¿Estás seguro de que deseas actualizar tu horario?',
            buttons: [
                {
                    label: 'Sí, confirmar',
                    className: 'button-principal',
                    onClick: () => {
                        fetch(`/schedule/save_availability/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken(),
                                "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                            },
                            body: JSON.stringify(updatedSchedule)
                        })
                            .then(response => {
                                if (!response.ok) throw new Error("Error al guardar el horario");
                                return response.json();
                            })
                            .then(() => {
                                const deletePromises = deletedSchedule.map(id =>
                                    fetch(`/schedule/availability/${id}/`, {
                                        method: 'DELETE',
                                        headers: {
                                            'X-CSRFToken': getCSRFToken(),
                                            "Authorization": `Bearer ${localStorage.getItem("accessToken")}`
                                        }
                                    })
                                        .then(response => {
                                            if (!response.ok) throw new Error(`Error al eliminar el horario con ID ${id}`);
                                        })
                                );

                                return Promise.all(deletePromises);
                            })
                            .then(() => {
                                mostrarToastGlobal({
                                    type: 'success',
                                    message: "Horario actualizado exitosamente."
                                });
                                isEditing = false;
                                fetchSchedule();
                            })
                            .catch(error => {
                                console.error("Error al guardar o eliminar el horario:", error);
                                mostrarToastGlobal({
                                    type: 'error',
                                    message: "Hubo un error al actualizar el horario."
                                });
                            });
                    }
                },
                {
                    label: 'No, cancelar',
                    className: 'button-edit',
                    onClick: () => {
                        isEditing = false;
                        fetchSchedule();
                        cerrarToast();
                    }
                }
            ]
        });
    };

    const fetchSchedule = () => {
        fetch(`/schedule/get_schedule/${doctorId}/`)
            .then(response => {
                if (!response.ok) throw new Error("Error al obtener el horario");
                return response.json();
            })
            .then(data => renderSchedule(data.schedule))
            .catch(() => renderSchedule());
    };
    fetchSchedule();
});

function confirmAppointmentStatus(appointmentId, newStatus, statusText) {
    mostrarToastGlobal({
        type: 'text',
        message: `¿Estás seguro de que deseas marcar esta cita como ${statusText}?`,
        buttons: [
            {
                label: 'Sí, confirmar',
                className: 'button-principal',
                onClick: () => {
                    updateAppointmentStatus(appointmentId, newStatus, statusText);
                    cerrarToast();
                }
            },
            {
                label: 'No, cancelar',
                className: 'button-edit',
                onClick: () => {
                    cerrarToast();
                }
            }
        ]
    });
}

function updateAppointmentStatus(appointmentId, newStatus, statusText) {
    fetch(`/appointments/api/${appointmentId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem("accessToken")}`
        },
        body: JSON.stringify({ status: newStatus })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al actualizar el estado de la cita.");
            }
            return response.json();
        })
        .then(() => {
            mostrarToastGlobal({
                type: 'success',
                message: `Cita ${statusText} exitosamente.`
            });

            if (newStatus === 3) {
                fetch(`/appointments/api/${appointmentId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem("accessToken")}`
                    }
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("Error al eliminar la cita.");
                        }
                        console.log(`Cita con ID ${appointmentId} eliminada exitosamente.`);
                        if (calendar) {
                            calendar.refetchEvents();
                        }
                    })
                    .catch(error => {
                        console.error("Error al eliminar la cita:", error);
                        mostrarToastGlobal({
                            type: 'error',
                            message: "Hubo un error al eliminar la cita."
                        });
                    });
            } else {
                if (calendar) {
                    calendar.refetchEvents();
                }
            }
        })
        .catch(error => {
            console.error("Error al actualizar el estado de la cita:", error);
            mostrarToastGlobal({
                type: 'error',
                message: "Hubo un error al actualizar el estado de la cita."
            });
        });
}

function cerrarToast() {
    const toast = document.querySelector('.toast');
    if (toast) {
        toast.remove();
    }
}
