document.addEventListener("DOMContentLoaded", function () {
    const availableSectors = document.getElementById("available-sectors");
    const assignedSectors = document.getElementById("assigned-sectors");
    const addSectorBtn = document.getElementById("add-sector-btn");
    const removeSectorBtn = document.getElementById("remove-sector-btn");

    let selectedSector = null;

    // Función para seleccionar un sector
    function selectSector(container, sector) {
        if (selectedSector) {
            selectedSector.classList.remove("selected");
        }
        selectedSector = sector;
        selectedSector.classList.add("selected");
    }

    // Asignar evento de selección a los sectores disponibles y asignados
    [availableSectors, assignedSectors].forEach((container) => {
        container.addEventListener("click", function (e) {
            if (e.target.tagName === "LI") {
                selectSector(container, e.target);
            }
        });
    });

    // Mover sector al contenedor de asignados
    addSectorBtn.addEventListener("click", function () {
        if (selectedSector && selectedSector.parentNode === availableSectors) {
            assignedSectors.appendChild(selectedSector);
            selectedSector.classList.remove("selected");
            selectedSector = null;
        }
    });

    // Mover sector al contenedor de disponibles
    removeSectorBtn.addEventListener("click", function () {
        if (selectedSector && selectedSector.parentNode === assignedSectors) {
            availableSectors.appendChild(selectedSector);
            selectedSector.classList.remove("selected");
            selectedSector = null;
        }
    });

    // Enviar los sectores seleccionados al backend
    const saveButton = document.getElementById("save-sectors-btn");
    saveButton.addEventListener("click", function () {
        const assignedSectorIds = Array.from(assignedSectors.children).map((li) =>
            li.getAttribute("data-sector-id")
        );

        fetch(window.location.href, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: JSON.stringify({ assigned_sector_ids: assignedSectorIds }),
        })
            .then((response) => {
                if (response.ok) {
                    alert("Sectores asignados actualizados correctamente.");
                } else {
                    alert("Hubo un error al actualizar los sectores.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });
});
