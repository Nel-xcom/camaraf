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