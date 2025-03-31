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

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const presentacionId = this.getAttribute("data-id");
            const row = this.closest("tr");  // Asegurar que se elimine la fila correcta

            if (confirm("¿Estás seguro de eliminar esta presentación?")) {
                fetch(`/eliminar_presentacion/${presentacionId}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json"
                    }
                })
                .then(response => {
                    if (response.ok) {
                        row.remove();  // Eliminar la fila correctamente
                    } else {
                        alert("Error al eliminar la presentación.");
                    }
                })
                .catch(error => console.error("Error:", error));
            }
        });
    });

    function getCSRFToken() {
        const token = document.querySelector("[name=csrfmiddlewaretoken]");
        return token ? token.value : "";
    }
});
