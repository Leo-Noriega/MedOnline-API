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
    const calendarElement = document.getElementById("calendar");
    const scheduleElement = document.getElementById("schedule");
    const doctorId = calendarElement.dataset.doctorId;
    const doctorTime = calendarElement.dataset.doctorTime;

    if (!doctorId || !doctorTime) {
        console.error("El doctor_id o doctor_time no están definidos en el HTML.");
        return;
    }

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
                                backgroundColor = '#FFC300';
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

                        const title = (appointment.patient_name && appointment.patient_surnames)
                            ? `${appointment.patient_name} ${appointment.patient_surnames}`
                            : (appointment.user_full_name || (appointment.user ? `${appointment.user.name} ${appointment.user.surnames}` : 'Paciente'));

                        return {
                            id: appointment.id,
                            title: title,
                            start: startDate.toISOString(),
                            end: endDate.toISOString(),
                            allDay: false,
                            backgroundColor: backgroundColor,
                            borderColor: backgroundColor,
                            extendedProps: {
                                status: appointment.status,
                                note: appointment.note || 'Sin nota', 
                                phone: appointment.user && appointment.user.phone ? appointment.user.phone : 'No disponible',
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
        console.log("Renderizando horario editable con datos:", data);
    
        // Resto del código...
        
        const rows = weekdays.map((day, index) => {
            const dayData = data.find(schedule => schedule.weekday === index + 1);
            console.log(`Día ${day}, datos:`, dayData);
            
            // Día de la semana en nuestro formato (1-7)
            const weekday = index + 1;
            
            return `
            <tr data-availability-id="${dayData && dayData.availability_id ? dayData.availability_id : ''}" 
                data-weekday="${weekday}" 
                data-had-schedule="${dayData ? 'true' : 'false'}">
                <td><p class="m-0 text-second fw-medium">${day}</p></td>
                <td>
                    <input type="checkbox" name="workday" ${dayData ? "checked" : ""}>
                </td>
                <td>
                    <input type="time" class="form-control start-time" name="start_time" value="${dayData ? dayData.start_time : ''}">
                </td>
                <td>
                    <input type="time" class="form-control end-time" name="end_time" value="${dayData ? dayData.end_time : ''}">
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

        // Agregar event listeners para validar tiempo
        const endTimeInputs = scheduleElement.querySelectorAll('.end-time');
        endTimeInputs.forEach(endTimeInput => {
            endTimeInput.addEventListener('change', (e) => {
                const row = e.target.closest('tr');
                const startTime = row.querySelector('.start-time').value;
                const endTime = e.target.value;
                
                if (startTime && endTime && startTime >= endTime) {
                    mostrarToastGlobal({
                        type: 'error',
                        message: "La hora de fin debe ser mayor a la hora de inicio"
                    });
                    e.target.value = '';
                }
            });
        });

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
        let hasTimeError = false;

        console.log("Iniciando proceso de guardado del horario");

        // Primera pasada: solo validar tiempos
        Array.from(rows).forEach((row, index) => {
            const works = row.querySelector("input[name='workday']").checked;
            const startTime = row.querySelector("input[name='start_time']").value;
            const endTime = row.querySelector("input[name='end_time']").value;
            
            if (works && startTime && endTime && startTime >= endTime) {
                hasTimeError = true;
                mostrarToastGlobal({
                    type: 'error',
                    message: `Error en ${weekdays[index]}: La hora de fin debe ser mayor a la hora de inicio`
                });
            }
        });

        if (hasTimeError) {
            console.log("Proceso detenido por errores de tiempo");
            return;
        }

        // Segunda pasada: construir los arreglos
        Array.from(rows).forEach((row, index) => {
            const works = row.querySelector("input[name='workday']").checked;
            const startTime = row.querySelector("input[name='start_time']").value;
            const endTime = row.querySelector("input[name='end_time']").value;
            const availabilityId = row.getAttribute("data-availability-id");
            
            console.log(`Día ${weekdays[index]}:`);
            console.log(`- Trabaja: ${works ? "Sí" : "No"}`);
            console.log(`- ID: "${availabilityId}"`);
            console.log(`- Tipo de ID: ${typeof availabilityId}`);
            console.log(`- ¿ID vacío?: ${!availabilityId || availabilityId === ""}`);

            // Si el médico trabaja ese día
            if (works && startTime && endTime) {
                const scheduleItem = {
                    doctor_id: doctorId,
                    weekday: index + 1,
                    start_time: startTime,
                    end_time: endTime
                };
                
                if (availabilityId && availabilityId !== '') {
                    scheduleItem.id = availabilityId;
                    console.log(`- Actualizando ID: ${availabilityId}`);
                } else {
                    console.log(`- Nuevo registro`);
                }
                
                updatedSchedule.push(scheduleItem);
            } 
            // PUNTO CLAVE: Si no trabaja pero tiene un ID (existía antes)
            else if (!works && availabilityId && availabilityId !== '') {
                console.log(`- ELIMINANDO ID: ${availabilityId}`);
                deletedSchedule.push(availabilityId);
            }
        });

        console.log("Datos finales:");
        console.log("- updatedSchedule:", updatedSchedule);
        console.log("- deletedSchedule:", deletedSchedule);
        
        // Si no hay nada que actualizar ni eliminar, mostrar mensaje y salir
        if (updatedSchedule.length === 0 && deletedSchedule.length === 0) {
            mostrarToastGlobal({
                type: 'info',
                message: "No hay cambios para guardar en el horario."
            });
            isEditing = false;
            fetchSchedule();
            return;
        }
    
        // Resto del código para confirmar y procesar...
        mostrarToastGlobal({
            type: 'text',
            message: '¿Estás seguro de que deseas actualizar tu horario?',
            buttons: [
                {
                    label: 'Sí, confirmar',
                    className: 'button-principal',
                    onClick: () => {
                        // Primero procesar las actualizaciones
                        fetch(`/schedule/save_availability/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken(),
                                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                            },
                            body: JSON.stringify(updatedSchedule)
                        })
                        .then(response => {
                            if (!response.ok) throw new Error("Error al guardar el horario");
                            return response.json();
                        })
                        .then(data => {
                            console.log("Respuesta del servidor al guardar:", data);
                            
                            // Ahora procesar las eliminaciones si hay alguna
                            if (deletedSchedule.length > 0) {
                                console.log(`Procesando ${deletedSchedule.length} eliminaciones...`);
                                
                                // Procesar las eliminaciones una por una en secuencia para mejor control
                                return deletedSchedule.reduce((promise, id) => {
                                    return promise.then(() => {
                                        console.log(`Intentando eliminar ID: ${id}`);
                                        return fetch(`/schedule/availability/${id}/`, {
                                            method: 'DELETE',
                                            headers: {
                                                'X-CSRFToken': getCSRFToken(),
                                                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                                            }
                                        })
                                        .then(response => {
                                            console.log(`Respuesta para eliminar ID ${id}:`, response.status);
                                            if (!response.ok) {
                                                console.error(`Error al eliminar horario con ID ${id}`);
                                                throw new Error(`Error al eliminar el horario con ID ${id}`);
                                            }
                                            console.log(`Eliminado correctamente horario con ID ${id}`);
                                        });
                                    });
                                }, Promise.resolve());
                            }
                            return Promise.resolve();
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
                                message: `Error al actualizar el horario: ${error.message}`
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
            .then(data => {
                console.log("Datos recibidos del servidor:", data.schedule);
                renderSchedule(data.schedule);
            })
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
            'Authorization': `Bearer ${localStorage.getItem("access_token")}`
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
                        'Authorization': `Bearer ${localStorage.getItem("access_token")}`
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
