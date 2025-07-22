// Mostrar/ocultar contraseña con animación de icono
const passwordInput = document.getElementById('id_password');
const togglePassword = document.getElementById('togglePassword');
const eyeIcon = document.getElementById('eyeIcon');

const eyeOpen = '/static/images/eye-open.png';
const eyeClosed = '/static/images/eye-closed.png';

let visible = false;

togglePassword.addEventListener('click', () => {
    visible = !visible;
    passwordInput.type = visible ? 'text' : 'password';
    // Animación de opacidad para el cambio de icono
    eyeIcon.style.opacity = 0.3;
    setTimeout(() => {
        eyeIcon.src = visible ? eyeOpen : eyeClosed;
        eyeIcon.alt = visible ? 'Ocultar contraseña' : 'Mostrar contraseña';
        eyeIcon.style.opacity = 1;
    }, 120);
});

togglePassword.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        togglePassword.click();
    }
});

// Accesibilidad: cambiar el icono si el usuario escribe manualmente
passwordInput.addEventListener('input', () => {
    if (passwordInput.value.length === 0 && visible) {
        visible = false;
        passwordInput.type = 'password';
        eyeIcon.src = eyeClosed;
        eyeIcon.alt = 'Mostrar contraseña';
    }
}); 