// Notificaciones globales estilo X

document.addEventListener('DOMContentLoaded', function() {
    setupNotifications();
});

function setupNotifications() {
    const bell = document.getElementById('notification-bell');
    const badge = document.getElementById('notification-badge');
    const dropdown = document.getElementById('notification-dropdown');
    const list = document.getElementById('notification-list');
    if (!bell || !badge || !dropdown || !list) return;

    let notifications = [];
    let unreadCount = 0;

    async function fetchNotifications() {
        try {
            const res = await fetch('/notificaciones/');
            const data = await res.json();
            notifications = data.notificaciones || [];
            unreadCount = notifications.filter(n => !n.leido).length;
            updateBadge();
            renderDropdown();
        } catch (e) {
            // Silenciar error
        }
    }

    function updateBadge() {
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    function renderDropdown() {
        let html = `
        <div style="padding:10px 18px 6px 18px;display:flex;flex-direction:column;border-bottom:1px solid #e6ecf0;background:#fff;border-radius:18px 18px 0 0;">
            <span style="font-weight:700;font-size:1.08rem;color:#222;">Notificaciones</span>
            <button id="mark-all-read-btn" style="margin-top:10px;background:#f7fafd;border:none;color:#1d9bf0;font-weight:700;cursor:pointer;font-size:0.98rem;padding:8px 0;border-radius:999px;transition:background 0.18s;width:100%;box-shadow:0 1px 2px rgba(29,155,240,0.04);">Marcar todas como leídas</button>
        </div>
    `;
        if (notifications.length === 0) {
            html += '<div style="padding:18px;text-align:center;color:#888;">No hay notificaciones.</div>';
        } else {
            html += notifications.map(n => `
            <div class="notification-item${n.leido ? '' : ' unread'}" onclick="marcarNotificacionLeida(${n.id}, '${n.link || '#'}')">
                <div class="notif-main">${n.mensaje}</div>
                <div class="notif-date">${n.fecha}</div>
            </div>
        `).join('');
        }
        list.innerHTML = html;

        // Evento para marcar todas como leídas
        const markAllBtn = document.getElementById('mark-all-read-btn');
        if (markAllBtn) {
            markAllBtn.onclick = async function() {
                markAllBtn.disabled = true;
                markAllBtn.style.opacity = 0.6;
                await fetch('/notificaciones/marcar-todas-leidas/', { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } });
                // Marcar todas como leídas en el array local
                notifications = notifications.map(n => ({ ...n, leido: true }));
                unreadCount = 0;
                updateBadge();
                renderDropdown();
                markAllBtn.disabled = false;
                markAllBtn.style.opacity = 1;
            };
        }
    }

    bell.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', function() {
        dropdown.style.display = 'none';
    });
    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Inicial y cada 30s
    fetchNotifications();
    setInterval(fetchNotifications, 30000);
}

window.marcarNotificacionLeida = async function(id, link) {
    try {
        await fetch(`/notificaciones/${id}/leer/`, { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } });
        // Refrescar notificaciones
        const bell = document.getElementById('notification-bell');
        if (bell) bell.click(); // Cierra el dropdown
        setTimeout(() => { window.location.href = link; }, 100);
    } catch (e) {}
}; 