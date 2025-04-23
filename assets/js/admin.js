document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('usuariosTable');
    

    async function loadUsers() {
        try {
            const response = await fetch('/admin/users/');
            if (!response.ok) throw new Error('Error en la petición');
            const users = await response.json();
            const filteredUsers = users.filter(user => user.role !== 'Admin' && user.role !== 'SuperAdmin');
            const dataTable = new DataTable('#usuariosTable', {
                data: filteredUsers,
                columns: [
                    {
                        data: null,
                        render: (data, type, row, meta) => meta.row + 1
                    },
                    {
                        data: 'photo',
                        render: (data) => {
                            return `<img src="${data || '/static/img/default.png'}" 
                                    class="rounded-circle user-photo" 
                                    alt="User photo" 
                                    width="40" height="40">`;
                        }
                    },
                    {
                        data: null,
                        render: (data) => `${data.name} ${data.surnames}`
                    },
                    { data: 'email' },
                    { data: 'role' },
                    { data: 'username' },
                    { data: 'phone' },
                    {
                        data: 'status',
                        render: (data) => `
                            <div class="d-flex align-items-center">
                                <div class="status-indicator ${data ? 'active' : 'inactive'}"></div>
                                <span class="ms-2">${data ? 'Activo' : 'Inactivo'}</span>
                            </div>`
                    },
                    {
                        data: null,
                        render: (data) => `
                            <button class="button-edit mt-3" onclick="verUsuario('${data.id}')">
                                <i class="bi bi-eye"></i> Ver
                            </button>`
                    }
                ],
                language: {
                    "sProcessing": "Procesando...",
                    "sLengthMenu": "Mostrar _MENU_ registros",
                    "sZeroRecords": "No se encontraron resultados",
                    "sEmptyTable": "Ningún dato disponible en esta tabla",
                    "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
                    "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0",
                    "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
                    "sSearch": "Buscar:",
                    "oPaginate": {
                        "sFirst": "Primero",
                        "sLast": "Último",
                        "sNext": "Siguiente",
                        "sPrevious": "Anterior"
                    }
                }
            });
        } catch (error) {
            console.error('Error:', error);
        }
    }

    if (table) {
        loadUsers();
    }
});



function verUsuario(userId) {
   
    userId = parseInt(userId);

    const table = $('#usuariosTable').DataTable();
    
   
    const row = table.rows().eq(0).filter((idx) => {
        const data = table.row(idx).data();
        return parseInt(data.id) === userId;
    });

    if (row.length === 0) {
        mostrarToastGlobal({
            type: 'danger',
            message: 'No se encontró información del usuario'
        });
        return;
    }

    const userData = table.row(row[0]).data();

   
    
    sessionStorage.setItem('user_id', userId);

   
    switch(userData.role) {
        case 'Doctor':
            sessionStorage.setItem('user_id', userId);
            window.location.href = '/admin/gestion-especialistas/';
            break;
        case 'Patient':
            sessionStorage.setItem('user_id', userId);
            window.location.href = '/admin/gestion-pacientes/';
            break;
        default:
            console.error('Rol no reconocido:', userData.role);
            mostrarToastGlobal({
                type: 'danger',
                message: 'Rol de usuario no válido'
            });
    }
}

