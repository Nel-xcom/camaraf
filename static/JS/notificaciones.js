// Notificaciones globales estilo X

document.addEventListener('DOMContentLoaded', function() {
    // Cargar notificaciones al abrir el menú
    const bell = document.getElementById('notification-bell');
    const dropdown = document.getElementById('notification-dropdown');
    const badge = document.getElementById('notification-badge');
    const list = document.getElementById('notification-list');

    if (!bell || !dropdown || !badge || !list) return;

    function fetchNotificaciones() {
        fetch('/notificaciones/')
            .then(res => res.json())
            .then(data => {
                let html = '';
                let unread = 0;
                data.notificaciones.forEach(n => {
                    if (!n.leido) unread++;
                    html += `<div class="notificacion-item${n.leido ? '' : ' notificacion-unread'}" data-id="${n.id}" data-link="${n.link||''}" style="padding:14px 18px;border-bottom:1px solid #f2f2f2;cursor:pointer;display:flex;align-items:center;gap:12px;">
                        <span style="flex:1;">${n.mensaje}</span>
                        <span style="font-size:0.85em;color:#888;">${n.fecha}</span>
                    </div>`;
                });
                list.innerHTML = html || '<div style="padding:24px;text-align:center;color:#aaa;">Sin notificaciones</div>';
                console.log('[NOTIF] Cantidad no leídas:', unread, data.notificaciones);
                if (unread > 0) {
                    badge.style.display = '';
                    badge.style.visibility = 'visible';
                    badge.style.background = '#e0245e';
                    badge.style.border = '2px solid #fff'; // Borde de depuración
                } else {
                    badge.style.display = 'none';
                }
                badge.textContent = unread;
            });
    }

    // Forzar recarga del badge al cargar la página
    fetchNotificaciones();

    bell.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        if (dropdown.style.display === 'block') {
            fetchNotificaciones();
        }
    });

    // Cerrar el dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target) && e.target !== bell) {
            dropdown.style.display = 'none';
        }
    });

    // Redirigir al link de la notificación y marcar como leída
    list.addEventListener('click', function(e) {
        let item = e.target.closest('.notificacion-item');
        if (!item) return;
        let id = item.getAttribute('data-id');
        let link = item.getAttribute('data-link');
        if (id) {
            fetch(`/notificacion/${id}/marcar_leida/`, {method:'POST',headers:{'X-Requested-With':'XMLHttpRequest'}})
                .then(()=>{
                    if(link && link !== '#') window.location.href = link;
                    else item.classList.remove('notificacion-unread');
                });
        }
    });

    // Marcar todas como leídas
    if (!document.getElementById('marcar-todas-leidas')) {
        let btn = document.createElement('button');
        btn.id = 'marcar-todas-leidas';
        btn.textContent = 'Marcar todas como leídas';
        btn.style = 'width:100%;background:none;border:none;color:#1d9bf0;font-weight:600;padding:12px 0;cursor:pointer;';
        btn.onclick = function() {
            fetch('/notificaciones/marcar_todas_leidas/', {method:'POST',headers:{'X-Requested-With':'XMLHttpRequest'}})
                .then(()=>fetchNotificaciones());
        };
        dropdown.appendChild(btn);
    }
}); 