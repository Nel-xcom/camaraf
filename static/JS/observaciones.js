const tabs = document.querySelectorAll('.tab-btn');
const rows = document.querySelectorAll('.clickable-row');
const modal = document.getElementById('detailsModal');
const closeModal = document.querySelector('.close-modal');

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const presentacionId = this.getAttribute('data-id');
            
            fetch(`/eliminar_presentacion/${presentacionId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') // Obtener token CSRF
                }
            })
            .then(response => {
                if (response.ok) {
                    this.closest('tr').remove(); // Elimina la fila de la tabla
                } else {
                    console.error('Error al eliminar la presentación');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Función para obtener el token CSRF de las cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            cookies.forEach(cookie => {
                const trimmedCookie = cookie.trim();
                if (trimmedCookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(trimmedCookie.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
});


document.addEventListener("DOMContentLoaded", () => {
    const userIsCamara = document.body.getAttribute('data-user-camara') === 'true';
    document.querySelectorAll(".editable-estado").forEach(cell => {
        const span = cell.querySelector(".estado-label");
        const select = cell.querySelector(".estado-select");
        const presentacionId = cell.dataset.id;

        // Solo permitir interacción si el usuario es Camara
        if (userIsCamara && select) {
            // Mostrar <select> al hacer clic
            span.addEventListener("click", () => {
                span.style.display = "none";
                select.style.display = "inline-block";
                select.focus();
            });

            // Guardar al presionar Enter
            select.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    const nuevoEstado = select.value;

                    fetch(`/actualizar_estado_presentacion/${presentacionId}/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken()
                        },
                        body: JSON.stringify({ estado: nuevoEstado })
                    })
                    .then(res => {
                        if (!res.ok) throw new Error("Error al actualizar estado");
                        return res.json();
                    })
                    .then(() => {
                        // ✅ Reemplazar el contenido con nuevo estado
                        span.innerHTML = `<i class="fas fa-circle icon-estado"></i> ${nuevoEstado}`;
                        span.style.display = "inline-block";
                        select.style.display = "none";
                    })
                    .catch(err => console.error("Error en actualización:", err));
                }
            });
        } else {
            // Si no es Camara, no hacer nada al click
            span.style.cursor = "default";
        }
    });

    function getCSRFToken() {
        const cookie = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }
});


