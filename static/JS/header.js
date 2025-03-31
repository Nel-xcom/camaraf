const menu = document.querySelector('.menu');
const openMenuButton = document.querySelector('.an-menu');
const closeMenuButton = document.querySelector('.close-menu');
const logo = document.querySelector('.menu-logo');

// 🔹 Establecer el estado inicial del menú como colapsado
document.addEventListener("DOMContentLoaded", () => {
    collapseMenu(); // Ahora el menú comienza colapsado
});

function collapseMenu() {
    menu.classList.add('collapsed');
    menu.classList.remove('active');
    logo.style.width = '50px';
    closeMenuButton.classList.remove('fa-times'); // Quitar el ícono de cerrar
}

function expandMenu() {
    menu.classList.remove('collapsed');
    menu.classList.add('active');
    logo.style.width = '110px';
    closeMenuButton.classList.remove('fa-bars');
    closeMenuButton.classList.add('fa-times'); // Cambiar ícono a 'times'
}

// Evento: abrir menú con el botón hamburguesa
openMenuButton.addEventListener('click', () => {
    if (menu.classList.contains('collapsed')) {
        expandMenu();
    } else {
        collapseMenu();
    }
});

// Evento: cerrar menú con la "X"
closeMenuButton.addEventListener('click', collapseMenu);
