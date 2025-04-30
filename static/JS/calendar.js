document.addEventListener("DOMContentLoaded", function () {
    const currentMonthElement = document.getElementById("current-month");
    const prevMonthButton = document.getElementById("prev-month");
    const nextMonthButton = document.getElementById("next-month");
    const calendarGrid = document.getElementById("calendar-grid");

    let currentDate = new Date();

    // Función para actualizar el encabezado del mes
    function updateMonthDisplay() {
        const options = { month: "long", year: "numeric" };
        currentMonthElement.textContent = currentDate.toLocaleDateString("es-ES", options);
    }

    // Función para regenerar los días del mes en la cuadrícula
    function generateCalendar() {
        calendarGrid.innerHTML = ""; // Limpiar calendario

        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const firstDay = new Date(year, month, 1).getDay();
        const lastDate = new Date(year, month + 1, 0).getDate();

        // Insertar días vacíos antes del primer día del mes
        for (let i = 0; i < firstDay; i++) {
            let emptyCell = document.createElement("div");
            emptyCell.classList.add("day", "empty");
            calendarGrid.appendChild(emptyCell);
        }

        // Insertar días del mes
        for (let day = 1; day <= lastDate; day++) {
            let dateString = `${year}-${(month + 1).toString().padStart(2, "0")}-${day.toString().padStart(2, "0")}`;

            let dayElement = document.createElement("div");
            dayElement.classList.add("day");
            dayElement.setAttribute("data-date", dateString);
            dayElement.textContent = day;

            calendarGrid.appendChild(dayElement);
        }

        loadCalendarData(); // Cargar datos de presentaciones
    }

    // Event listeners para cambiar de mes
    prevMonthButton.addEventListener("click", function() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        updateMonthDisplay();
        generateCalendar();
        loadCalendarData(); // Forzar recarga de datos
    });
    
    nextMonthButton.addEventListener("click", function() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        updateMonthDisplay();
        generateCalendar();
        loadCalendarData(); // Forzar recarga de datos
    });

    // Cargar presentaciones según el mes actual
    function loadCalendarData() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1;
        
        // 1. Actualiza el calendario (tu código existente)
        fetch(`/api/get_presentaciones/?year=${year}&month=${month}`)
            .then(response => response.json())
            .then(data => marcarDiasConPresentaciones(data));
        
        // 2. Nueva función para actualizar el listado de presentaciones
        fetch(`/get_presentaciones_listado/?year=${year}&month=${month}`)
            .then(response => response.json())
            .then(data => {
                const listContainer = document.getElementById('presentation-list');
                listContainer.innerHTML = data.length > 0 
                    ? data.map(p => `
                        <li class="presentation-item">
                            <div class="presentation-info">
                                <i class="fas fa-calendar-alt"></i>
                                <span class="presentation-date">${p.fecha}</span>
                                <span class="presentation-social">${p.obra_social}</span>
                                <span class="presentation-quincena">Periodo: ${p.quincena}</span>
                            </div>
                        </li>
                    `).join('')
                    : '<li class="no-presentations">No hay presentaciones este mes</li>';
            });
    }

    function marcarDiasConPresentaciones(presentaciones) {
        // Limpiar TODOS los tags existentes primero
        document.querySelectorAll('.evento').forEach(tag => tag.remove());
        
        presentaciones.forEach(presentacion => {
            const diaElemento = document.querySelector(`.day[data-date="${presentacion.fecha}"]`);

            if (diaElemento) {
                const etiqueta = document.createElement("div");
                etiqueta.className = "evento";
                etiqueta.textContent = presentacion.obra_social;
                diaElemento.appendChild(etiqueta);
            }
        });
    }

    // Inicializar el calendario con los datos actuales
    updateMonthDisplay();
    generateCalendar();
});
