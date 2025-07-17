document.addEventListener("DOMContentLoaded", function() {
    const calendarGrid = document.getElementById("calendar-grid");
    const currentMonthElement = document.getElementById("current-month");
    const prevMonthButton = document.getElementById("prev-month");
    const nextMonthButton = document.getElementById("next-month");
    const modal = document.getElementById("presentation-modal");
    const overlay = document.getElementById("modal-overlay");
    const closeModal = document.getElementById("close-modal");
    const selectedDateInput = document.getElementById("selected-date");
    const form = document.getElementById("presentation-form");

    let currentDate = new Date();

    function renderCalendar(date) {
        calendarGrid.innerHTML = "";
        const year = date.getFullYear();
        const month = date.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const firstDayOfMonth = new Date(year, month, 1).getDay();

        currentMonthElement.textContent = `${getMonthName(month)} ${year}`;

        // Rellenar los días vacíos al inicio del mes
        for (let i = 0; i < firstDayOfMonth; i++) {
            const emptyDay = document.createElement("div");
            calendarGrid.appendChild(emptyDay);
        }

        // Rellenar los días del mes
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement("div");
            dayElement.classList.add("calendar-day");
            dayElement.textContent = day;

            dayElement.addEventListener("click", () => {
                selectedDateInput.value = `${day}/${month + 1}/${year}`;
                modal.classList.add("active");
                overlay.classList.add("active");
            });

            calendarGrid.appendChild(dayElement);
        }
    }

    function getMonthName(monthIndex) {
        const months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ];
        return months[monthIndex];
    }

    prevMonthButton.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextMonthButton.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    closeModal.addEventListener("click", () => {
        modal.classList.remove("active");
        overlay.classList.remove("active");
    });

    form.addEventListener("submit", function(event) {
        const obraSocial = document.getElementById("obra-social").value;
        const quincena = document.getElementById("quincena").value;

        if (!obraSocial || !quincena) {
            alert("Por favor, complete todos los campos antes de guardar.");
            event.preventDefault();
        }
    });

    renderCalendar(currentDate);
});

// --- MODAL DE CONFIRMACIÓN DE ELIMINACIÓN ---
let presentacionIdAEliminar = null;

function showDeleteModal(presentacionId) {
    presentacionIdAEliminar = presentacionId;
    document.getElementById('delete-confirm-modal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('delete-confirm-modal').style.display = 'none';
    presentacionIdAEliminar = null;
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const presentacionId = this.getAttribute("data-id");
            showDeleteModal(presentacionId);
        });
    });

    document.getElementById('close-delete-modal').addEventListener('click', closeDeleteModal);
    document.getElementById('cancel-delete-btn').addEventListener('click', closeDeleteModal);
    document.getElementById('delete-confirm-backdrop').addEventListener('click', closeDeleteModal);
    document.getElementById('confirm-delete-btn').addEventListener('click', function () {
        if (!presentacionIdAEliminar) return;
        // Buscar el elemento de la fila a eliminar
        const button = document.querySelector(`.delete-btn[data-id="${presentacionIdAEliminar}"]`);
        const row = button ? button.closest('li') : null;
        fetch(`/eliminar_presentacion_calendario/${presentacionIdAEliminar}/`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
        .then(response => {
            if (response.ok) {
                if (row) row.remove();
                showNotification('La eliminación se ha realizado correctamente', 'success', 2000);
            } else {
                showNotification('Error al eliminar la presentación.', 'error');
            }
            closeDeleteModal();
        })
        .catch(error => {
            showNotification('Error de conexión', 'error');
            closeDeleteModal();
        });
    });

    function getCSRFToken() {
        const token = document.querySelector("[name=csrfmiddlewaretoken]");
        return token ? token.value : "";
    }
});

// --- NOTIFICACIÓN ESTILO FORO ---
function showNotification(message, type = 'info', duration = 2000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        max-width: 300px;
        word-wrap: break-word;
        margin-top: 50px;
        animation: slideIn 0.3s ease-out;
    `;
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#00a651';
            break;
        case 'error':
            notification.style.backgroundColor = '#e0245e';
            break;
        case 'warning':
            notification.style.backgroundColor = '#856404';
            break;
        default:
            notification.style.backgroundColor = '#1d9bf0';
    }
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, duration);
}
