document.addEventListener("DOMContentLoaded", () => {
    const opinionesContainer = document.getElementById("opiniones");
    const url = opinionesContainer.dataset.url;

    // Cargar opiniones 
    async function cargarOpiniones() {
        try {
            const response = await fetch(url, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });

            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
            }

            const opiniones = await response.json();
            renderizarOpiniones(opiniones);
        } catch (error) {
            console.error("Error al cargar las opiniones:", error);
            mostrarError("Error al cargar las opiniones.");
        }
    }

    // Renderizar las opiniones
    function renderizarOpiniones(opiniones) {
        if (opiniones.length === 0) {
            opinionesContainer.innerHTML = `
                <p class="text-center text mt-3">
                    No hay opiniones disponibles. <i class="bi bi-chat-square-text text-second"></i>
                </p>`;
            return;
        }

        opinionesContainer.innerHTML = opiniones.map(opinion => crearOpinionHTML(opinion)).join("");
    }

    // Pintar la opinión 
    function crearOpinionHTML(opinion) {
        return `
            <div class="rounded shadow-sm bg-primary-color w-100 mb-3 text p-3">
                <div class="card-body">
                    <div class="justify-content-between d-flex row">
                        <div class="d-flex align-items-center mb-3 col-12 col-md-8">
                            <img src="${opinion.user.photo}" 
                                alt="Foto de ${opinion.user.name}" 
                                class="rounded-circle me-3" 
                                style="width: 50px; height: 50px;">
                            <div>
                                <h6 class="text-principal fw-medium mb-0">${opinion.user.name} ${opinion.user.surnames}</h6>
                                <small class="text-muted">${new Date(opinion.review_date).toLocaleDateString("es-ES")}</small>
                            </div>
                        </div>
                        <div class="col-12 col-md-4 text-start text-md-end">
                            <p class="mb-0">${'<i class="bi bi-star-fill text-warning px-1"></i>'.repeat(opinion.rating)}</p>
                        </div>
                    </div>
                    <p class="card-text">${opinion.comment}</p>
                </div>
            </div>`;
    }

    function mostrarError(mensaje) {
        opinionesContainer.innerHTML = `<p class='text-center text-danger'>${mensaje}</p>`;
    }

    cargarOpiniones();
});