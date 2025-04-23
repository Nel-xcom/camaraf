document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.approve-button');
  
    // Cargar filas pagadas desde localStorage
    const pagosGuardados = JSON.parse(localStorage.getItem('pagos_confirmados')) || [];
  
    // Aplicar visualización persistente
    document.querySelectorAll('tr[data-id]').forEach(row => {
      const id = row.getAttribute('data-id');
      if (pagosGuardados.includes(id)) {
        row.classList.add('paid-row');
  
        // ✅ Marcar el checkbox como activado
        const checkbox = row.querySelector('.styled-checkbox');
        if (checkbox) {
          checkbox.checked = true;
        }
      }
    });
  
    // Manejar clics en el botón de confirmación
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        const row = button.closest('tr');
        const checkbox = row.querySelector('.styled-checkbox');
        const id = row.getAttribute('data-id');
  
        if (checkbox.checked) {
          row.classList.add('paid-row');
  
          if (!pagosGuardados.includes(id)) {
            pagosGuardados.push(id);
            localStorage.setItem('pagos_confirmados', JSON.stringify(pagosGuardados));
          }
        } else {
          alert("Primero marcá la casilla antes de confirmar el pago.");
        }
      });
    });
  });
  