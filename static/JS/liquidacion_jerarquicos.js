document.addEventListener('DOMContentLoaded', () => {
    const optionIcons = document.querySelectorAll('.file-options');
  
    optionIcons.forEach(icon => {
      icon.addEventListener('click', (e) => {
        e.stopPropagation();
  
        // Cierra todos los demás menús abiertos
        document.querySelectorAll('.context-menu').forEach(menu => {
          menu.style.display = 'none';
        });
  
        // Muestra el menú del icono clickeado
        const menu = icon.nextElementSibling;
        menu.style.display = 'flex';
      });
    });
  
    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', () => {
      document.querySelectorAll('.context-menu').forEach(menu => {
        menu.style.display = 'none';
      });
    });
  });

  document.querySelectorAll('.eliminar-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      const archivoOrigen = this.closest('.file-card').dataset.archivo;
  
      if (confirm(`¿Estás seguro de que querés eliminar la liquidación "${archivoOrigen}"?`)) {
        fetch('/eliminar-liquidacion-jerarquicos/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          body: JSON.stringify({ archivo_origen: archivoOrigen }),
        })
        .then(response => {
          if (response.ok) {
            location.reload();
          } else {
            alert('❌ Error al eliminar la liquidación.');
          }
        });
      }
    });
  });
  
  
  // Función para obtener el CSRF desde las cookies
  function getCSRFToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue;
  }
  

  document.querySelectorAll('.editar-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const fileCard = this.closest('.file-card');
        const fileNameSpan = fileCard.querySelector('.file-name');
        const input = fileCard.querySelector('.edit-input');

        input.style.display = 'inline-block';
        fileNameSpan.style.display = 'none';
        input.focus();

        // Guardar al presionar Enter
        input.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                const nuevoNombre = input.value.trim();
                const archivoOriginal = fileCard.dataset.archivo;

                if (nuevoNombre && nuevoNombre !== archivoOriginal) {
                    fetch('/editar-titulo-liquidacion/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: JSON.stringify({
                            archivo_origen: archivoOriginal,
                            nuevo_titulo: nuevoNombre,
                        }),
                    })
                    .then(response => {
                        if (response.ok) {
                            location.reload();  // Recargamos para ver el nuevo título
                        } else {
                            alert('❌ Error al editar el título.');
                        }
                    });
                }

                // Ocultar input y mostrar texto original
                input.style.display = 'none';
                fileNameSpan.style.display = 'inline';
            }
        });
    });
});
