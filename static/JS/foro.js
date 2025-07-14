// Funcionalidad del Foro
document.addEventListener('DOMContentLoaded', function() {
    // Formulario de publicación
    const publicationForm = document.getElementById('publication-form');
    if (publicationForm) {
        publicationForm.addEventListener('submit', handlePublicationSubmit);
    }

    // Manejo de archivos seleccionados
    setupFileInputs();
});

// Manejar envío del formulario de publicación
async function handlePublicationSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('.post-btn');
    
    // Deshabilitar botón durante el envío
    submitBtn.disabled = true;
    submitBtn.textContent = 'Publicando...';
    
    try {
        const response = await fetch('/foro/crear-publicacion/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Limpiar formulario
            form.reset();
            clearSelectedFiles();
            
            // Mostrar mensaje de éxito
            showNotification('Publicación creada exitosamente', 'success');
            
            // Recargar página para mostrar la nueva publicación
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Error al crear la publicación', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    } finally {
        // Restaurar botón
        submitBtn.disabled = false;
        submitBtn.textContent = 'Publicar';
    }
}

// Configurar inputs de archivos
function setupFileInputs() {
    const fileInputs = document.querySelectorAll('.file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                showSelectedFile(file, this.name);
            }
        });
    });
}

// Mostrar archivo seleccionado
function showSelectedFile(file, inputName) {
    const selectedFiles = document.querySelector('.selected-files');
    const fileElement = document.createElement('div');
    fileElement.className = 'selected-file';
    fileElement.innerHTML = `
        <span>${file.name}</span>
        <button type="button" onclick="removeSelectedFile(this)">×</button>
    `;
    selectedFiles.appendChild(fileElement);
}

// Remover archivo seleccionado
function removeSelectedFile(button) {
    const fileElement = button.parentElement;
    const inputName = fileElement.dataset.inputName;
    const input = document.querySelector(`input[name="${inputName}"]`);
    
    if (input) {
        input.value = '';
    }
    
    fileElement.remove();
}

// Limpiar archivos seleccionados
function clearSelectedFiles() {
    const selectedFiles = document.querySelector('.selected-files');
    selectedFiles.innerHTML = '';
}

// Toggle like
async function toggleLike(publicationId) {
    try {
        const response = await fetch(`/foro/publicacion/${publicationId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const likeBtn = document.querySelector(`[data-publication-id="${publicationId}"] .like-btn`);
            const likeIcon = likeBtn.querySelector('i');
            const likeCount = likeBtn.querySelector('.interaction-count');
            
            // Actualizar estado visual
            if (data.liked) {
                likeBtn.classList.add('liked');
                likeIcon.className = 'fas fa-heart';
            } else {
                likeBtn.classList.remove('liked');
                likeIcon.className = 'far fa-heart';
            }
            
            // Actualizar contador
            likeCount.textContent = data.likes_count;
        } else {
            showNotification(data.error || 'Error al procesar el like', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    }
}

let currentModalPublicationId = null;

// Mostrar comentarios (abre el modal)
function mostrarComentarios(publicationId) {
    // Buscar el elemento de la publicación
    const pubElem = document.querySelector(`[data-publication-id="${publicationId}"]`);
    if (!pubElem) return;

    // Obtener datos
    const userName = pubElem.querySelector('.user-name')?.textContent || '';
    const pubTime = pubElem.querySelector('.publication-time')?.textContent || '';
    const description = pubElem.querySelector('.publication-text')?.textContent || '';
    const imageElem = pubElem.querySelector('.attachment-img');
    const imageUrl = imageElem ? imageElem.src : null;

    // Setear datos en el modal
    document.getElementById('modal-user-name').textContent = userName;
    document.getElementById('modal-publication-time').textContent = pubTime;
    document.getElementById('modal-publication-description').textContent = description;
    const modalImage = document.getElementById('modal-publication-image');
    if (imageUrl) {
        modalImage.innerHTML = `<img src="${imageUrl}" alt="Imagen publicación" class="attachment-img">`;
    } else {
        modalImage.innerHTML = '';
    }

    // Limpiar formulario
    const commentForm = document.getElementById('modal-comment-form');
    commentForm.reset();
    clearSelectedFilesModal();

    // Guardar el id de la publicación actual
    currentModalPublicationId = publicationId;

    // Mostrar modal
    document.getElementById('comment-modal').style.display = 'block';
    setTimeout(() => {
        document.getElementById('modal-comment-input').focus();
    }, 100);

    // Cargar comentarios
    cargarComentariosModal(publicationId);
}

// Cargar y mostrar comentarios en el modal (anidados, con eliminar y responder)
async function cargarComentariosModal(publicationId) {
    const commentsList = document.getElementById('modal-comments-list');
    commentsList.innerHTML = '<div style="text-align:center;color:#888;">Cargando comentarios...</div>';
    try {
        const response = await fetch(`/foro/publicacion/${publicationId}/comentarios/`);
        const data = await response.json();
        if (data.comentarios && data.comentarios.length > 0) {
            commentsList.innerHTML = renderCommentTree(data.comentarios);
        } else {
            commentsList.innerHTML = '<div style="text-align:center;color:#888;">No hay comentarios aún.</div>';
        }
    } catch (error) {
        commentsList.innerHTML = '<div style="text-align:center;color:#e0245e;">Error al cargar comentarios</div>';
    }
}

// Renderiza árbol de comentarios recursivamente
function renderCommentTree(comments, level = 0) {
    return comments.map(c => `
        <div class="modal-comment-item" style="margin-left:${level * 24}px;">
            <div class="modal-comment-header">
                <span class="modal-comment-user">${c.usuario}</span>
                <span class="modal-comment-date">${c.fecha}</span>
                ${c.puede_eliminar && !c.is_deleted ? `<button class="modal-comment-delete-btn" onclick="eliminarComentario(${c.id})" title="Eliminar comentario"><i class="fas fa-trash"></i></button>` : ''}
                ${!c.is_deleted ? `<button class="modal-comment-reply-btn" onclick="mostrarRespuestaForm(${c.id})" title="Responder"><i class="fas fa-reply"></i></button>` : ''}
            </div>
            <div class="modal-comment-content">${c.contenido}</div>
            <div id="reply-form-container-${c.id}"></div>
            ${c.replies && c.replies.length > 0 ? renderCommentTree(c.replies, level + 1) : ''}
        </div>
    `).join('');
}

// Mostrar formulario de respuesta inline
function mostrarRespuestaForm(commentId) {
    // Cerrar otros formularios
    document.querySelectorAll('.modal-reply-form').forEach(f => f.remove());
    const container = document.getElementById(`reply-form-container-${commentId}`);
    if (!container) return;
    container.innerHTML = `
        <form class="modal-reply-form" onsubmit="enviarRespuesta(event, ${commentId})">
            <textarea class="modal-reply-input" placeholder="Escribe tu respuesta..." required></textarea>
            <button type="submit" class="post-btn" style="margin-top:6px;">Responder</button>
            <button type="button" class="post-btn" style="background:#eee;color:#333;margin-left:8px;" onclick="this.closest('form').remove()">Cancelar</button>
        </form>
    `;
    container.querySelector('textarea').focus();
}

// Enviar respuesta a un comentario
async function enviarRespuesta(event, commentId) {
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const contenido = textarea.value.trim();
    if (!contenido) return;
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Enviando...';
    try {
        const response = await fetch(`/foro/comentario/${commentId}/responder/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `contenido=${encodeURIComponent(contenido)}`
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Respuesta publicada', 'success');
            cargarComentariosModal(currentModalPublicationId);
        } else {
            showNotification(data.error || 'Error al responder', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Responder';
    }
}

// Eliminar comentario
async function eliminarComentario(commentId) {
    if (!confirm('¿Eliminar este comentario?')) return;
    try {
        const response = await fetch(`/foro/comentario/${commentId}/eliminar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Comentario eliminado', 'success');
            cargarComentariosModal(currentModalPublicationId);
        } else {
            showNotification(data.error || 'Error al eliminar', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    }
}

function closeCommentModal() {
    document.getElementById('comment-modal').style.display = 'none';
    currentModalPublicationId = null;
}

// Manejo de archivos en el modal
function setupFileInputsModal() {
    const fileInputs = document.querySelectorAll('#modal-comment-form .file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                showSelectedFileModal(file, this.name);
            }
        });
    });
}

function showSelectedFileModal(file, inputName) {
    // Puedes implementar una vista de archivos seleccionados en el modal si lo deseas
}

function clearSelectedFilesModal() {
    // Si implementas vista de archivos seleccionados en el modal, límpiala aquí
}

// Enviar comentario desde el modal
const modalCommentForm = document.getElementById('modal-comment-form');
if (modalCommentForm) {
    modalCommentForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        if (!currentModalPublicationId) return;
        const formData = new FormData(modalCommentForm);
        const submitBtn = modalCommentForm.querySelector('.post-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';
        try {
            const response = await fetch(`/foro/publicacion/${currentModalPublicationId}/comentar/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });
            const data = await response.json();
            if (data.success) {
                showNotification('Comentario publicado', 'success');
                modalCommentForm.reset();
                // Recargar comentarios
                cargarComentariosModal(currentModalPublicationId);
            } else {
                showNotification(data.error || 'Error al comentar', 'error');
            }
        } catch (error) {
            showNotification('Error de conexión', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Responder';
        }
    });
    setupFileInputsModal();
}

// Eliminar publicación
async function eliminarPublicacion(publicationId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta publicación?')) {
        return;
    }
    
    try {
        const response = await fetch(`/foro/publicacion/${publicationId}/eliminar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Eliminar elemento del DOM
            const publicationElement = document.querySelector(`[data-publication-id="${publicationId}"]`);
            if (publicationElement) {
                publicationElement.remove();
            }
            
            showNotification('Publicación eliminada exitosamente', 'success');
        } else {
            showNotification(data.error || 'Error al eliminar la publicación', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Obtener token CSRF
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos básicos
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
    `;
    
    // Colores según tipo
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
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Animaciones para las publicaciones
function animatePublication(publicationElement) {
    publicationElement.style.opacity = '0';
    publicationElement.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        publicationElement.style.transition = 'all 0.3s ease';
        publicationElement.style.opacity = '1';
        publicationElement.style.transform = 'translateY(0)';
    }, 100);
}

// Inicializar animaciones para publicaciones existentes
document.addEventListener('DOMContentLoaded', function() {
    const publications = document.querySelectorAll('.publication-item');
    publications.forEach((pub, index) => {
        setTimeout(() => animatePublication(pub), index * 100);
    });
    
    // Inicializar event listeners para botones de publicaciones
    setupPublicationEventListeners();
});

// Configurar event listeners para botones de publicaciones
function setupPublicationEventListeners() {
    // Botones de eliminar publicación
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const publicationId = this.getAttribute('data-publication-id');
            if (publicationId) {
                eliminarPublicacion(parseInt(publicationId));
            }
        });
    });
    
    // Botones de comentarios
    document.querySelectorAll('.comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const publicationId = this.getAttribute('data-publication-id');
            if (publicationId) {
                mostrarComentarios(parseInt(publicationId));
            }
        });
    });
    
    // Botones de like
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const publicationId = this.getAttribute('data-publication-id');
            if (publicationId) {
                toggleLike(parseInt(publicationId));
            }
        });
    });
    
    // Botón de nueva solicitud
    const newComplaintBtn = document.getElementById('new-complaint-btn');
    if (newComplaintBtn) {
        newComplaintBtn.addEventListener('click', abrirModalReclamo);
    }
} 

// Reclamos: abrir/cerrar modal
function abrirModalReclamo() {
    document.getElementById('reclamo-modal').style.display = 'block';
    setTimeout(() => {
        document.querySelector('#reclamo-modal input[name="titulo"]').focus();
    }, 100);
}
function cerrarModalReclamo() {
    document.getElementById('reclamo-modal').style.display = 'none';
    document.getElementById('reclamo-form').reset();
}

// Enviar reclamo por AJAX
const reclamoForm = document.getElementById('reclamo-form');
if (reclamoForm) {
    reclamoForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(reclamoForm);
        const btn = reclamoForm.querySelector('.post-btn');
        btn.disabled = true;
        btn.textContent = 'Enviando...';
        try {
            const response = await fetch('/foro/reclamos/crear/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });
            const data = await response.json();
            if (data.success) {
                showNotification('Reclamo enviado', 'success');
                cerrarModalReclamo();
                cargarReclamosAside();
            } else {
                showNotification(data.error || 'Error al enviar reclamo', 'error');
            }
        } catch (error) {
            showNotification('Error de conexión', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Enviar reclamo';
        }
    });
}

// Cargar reclamos en el aside
async function cargarReclamosAside() {
    const list = document.getElementById('complaints-list');
    if (!list) return;
    list.innerHTML = '<div style="text-align:center;color:#888;">Cargando reclamos...</div>';
    try {
        const response = await fetch('/foro/reclamos/listar/');
        const data = await response.json();
        if (data.reclamos && data.reclamos.length > 0) {
            list.innerHTML = data.reclamos.map(r => renderReclamoAside(r)).join('');
        } else {
            list.innerHTML = '<div style="text-align:center;color:#888;">No hay reclamos.</div>';
        }
    } catch (error) {
        list.innerHTML = '<div style="text-align:center;color:#e0245e;">Error al cargar reclamos</div>';
    }
}

// Renderiza un reclamo en el aside
function renderReclamoAside(r) {
    // Preparar información de usuarios asignados
    let asignadosHtml = '';
    if (r.usuarios_asignados && r.usuarios_asignados.length > 0) {
        asignadosHtml = `<span class="complaint-assigned">Asignado: ${r.usuarios_asignados.join(', ')}</span>`;
    }
    
    return `
    <article class="complaint-item" data-reclamo-id="${r.id}">
        <div class="complaint-header">
            <div class="complaint-user-info">
                <span class="complaint-creator">Creador: ${r.usuario_creador}</span>
                ${asignadosHtml}
                <span class="complaint-time">${r.tiempo_transcurrido}</span>
            </div>
            <div class="complaint-actions">
                <button class="complaint-btn solved-btn${r.estado === 'Resuelto' ? ' solved' : ''}" title="Marcar como solucionado" onclick="marcarReclamoResuelto(${r.id})">
                    <i class="fas fa-check"></i>
                </button>
                <button class="complaint-btn notification-btn${r.notificaciones_activas ? ' active' : ''}" title="Notificaciones" onclick="toggleNotificacionesReclamo(${r.id})">
                    <i class="fas fa-bell"></i>
                </button>
                <button class="complaint-btn delete-complaint-btn" title="Eliminar reclamo" onclick="eliminarReclamo(${r.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        <div class="complaint-content">
            <h3 class="complaint-title">Titulo del reclamo: ${r.titulo}</h3>
            <p class="complaint-description">Descripcion: ${r.descripcion}</p>
        </div>
        <div class="complaint-update">
            <span class="update-info">Última modificación: ${r.ultima_actualizacion_por || r.usuario_creador} · ${r.estado}</span>
        </div>
    </article>
    `;
}

// Acciones reclamo
async function marcarReclamoResuelto(id) {
    await cambiarEstadoReclamo(id, 'resuelto');
}
async function cambiarEstadoReclamo(id, estado) {
    try {
        const response = await fetch(`/foro/reclamos/${id}/cambiar-estado/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `estado=${encodeURIComponent(estado)}`
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Estado actualizado', 'success');
            // Recargar reclamos y reconfigurar listeners
            await cargarReclamosAside();
            setTimeout(() => {
                setupComplaintModalClicks();
            }, 100);
        } else {
            showNotification(data.error || 'Error al actualizar estado', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    }
}
async function eliminarReclamo(id) {
    if (!confirm('¿Eliminar este reclamo?')) return;
    try {
        const response = await fetch(`/foro/reclamos/${id}/eliminar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Reclamo eliminado', 'success');
            // Recargar reclamos y reconfigurar listeners
            await cargarReclamosAside();
            setTimeout(() => {
                setupComplaintModalClicks();
            }, 100);
        } else {
            showNotification(data.error || 'Error al eliminar', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    }
}
async function toggleNotificacionesReclamo(id) {
    try {
        const response = await fetch(`/foro/reclamos/${id}/toggle-notificaciones/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            showNotification(data.notificaciones_activas ? 'Notificaciones activadas' : 'Notificaciones desactivadas', 'success');
            cargarReclamosAside();
        } else {
            showNotification(data.error || 'Error al cambiar notificaciones', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    }
}

// Inicializar reclamos al cargar la página
if (document.getElementById('complaints-list')) {
    cargarReclamosAside();
}

// Inicializar reclamos resueltos al cargar la página
if (document.getElementById('resolved-complaints-list')) {
    cargarReclamosResueltosAside();
    setupResolvedComplaintsSearch();
}

// Cargar reclamos resueltos en el aside
async function cargarReclamosResueltosAside(query = '') {
    const list = document.getElementById('resolved-complaints-list');
    if (!list) return;
    
    list.innerHTML = '<div style="text-align:center;color:#888;">Cargando reclamos resueltos...</div>';
    try {
        const url = query ? `/foro/reclamos/resueltos/?q=${encodeURIComponent(query)}` : '/foro/reclamos/resueltos/';
        const response = await fetch(url);
        const data = await response.json();
        if (data.reclamos && data.reclamos.length > 0) {
            list.innerHTML = data.reclamos.map(r => renderReclamoResueltoAside(r)).join('');
        } else {
            list.innerHTML = '<div style="text-align:center;color:#888;">No hay reclamos resueltos.</div>';
        }
    } catch (error) {
        list.innerHTML = '<div style="text-align:center;color:#e0245e;">Error al cargar reclamos resueltos</div>';
    }
}

// Renderiza un reclamo resuelto en el aside
function renderReclamoResueltoAside(r) {
    // Preparar información de usuarios asignados
    let asignadosHtml = '';
    if (r.usuarios_asignados && r.usuarios_asignados.length > 0) {
        asignadosHtml = `<span class="complaint-assigned">Asignado: ${r.usuarios_asignados.join(', ')}</span>`;
    }
    
    return `
    <article class="complaint-item resolved-complaint-item" data-reclamo-id="${r.id}">
        <div class="complaint-header">
            <div class="complaint-user-info">
                <span class="complaint-creator">Creador: ${r.usuario_creador}</span>
                ${asignadosHtml}
                <span class="complaint-time">${r.tiempo_transcurrido}</span>
            </div>
        </div>
        <div class="complaint-content">
            <h3 class="complaint-title">Titulo del reclamo: ${r.titulo}</h3>
            <p class="complaint-description">Descripcion: ${r.descripcion}</p>
        </div>
        <div class="complaint-update">
            <span class="update-info">Estado: ${r.estado}</span>
        </div>
    </article>
    `;
}

// Configurar búsqueda de reclamos resueltos
function setupResolvedComplaintsSearch() {
    const searchInput = document.getElementById('search-resolved-complaints');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            searchTimeout = setTimeout(() => {
                cargarReclamosResueltosAside(query);
            }, 300);
        });
    }
} 

// --- MODAL DE RECLAMO INTERACTIVO ---
let currentComplaintId = null;

// Abrir modal de reclamo al hacer click en un reclamo del aside
function setupComplaintModalClicks() {
    // Remover listeners existentes para evitar duplicados
    document.querySelectorAll('.complaint-item').forEach(item => {
        item.removeEventListener('click', handleComplaintClick);
    });
    
    // Agregar nuevos listeners
    document.querySelectorAll('.complaint-item').forEach(item => {
        item.addEventListener('click', handleComplaintClick);
    });
}

function handleComplaintClick(e) {
    // Evitar que los botones internos (eliminar, notificaciones, etc) abran el modal
    if (e.target.closest('.complaint-actions')) return;
    const complaintId = this.getAttribute('data-reclamo-id');
    openComplaintModal(complaintId);
}

async function openComplaintModal(complaintId) {
    if (!complaintId) return;
    
    currentComplaintId = complaintId;
    
    // Limpiar campos
    const modal = document.getElementById('complaint-modal');
    if (!modal) return;
    
    document.getElementById('complaint-modal-title').textContent = 'Reclamo';
    document.getElementById('complaint-modal-creator').textContent = '';
    document.getElementById('complaint-modal-date').textContent = '';
    document.getElementById('complaint-modal-status').textContent = '';
    document.getElementById('complaint-modal-description').textContent = '';
    document.getElementById('complaint-modal-attachments').innerHTML = '';
    document.getElementById('complaint-comments-list').innerHTML = '<div style="text-align:center;color:#888;">Cargando comentarios...</div>';
    document.getElementById('complaint-comment-form').reset();
    
    // Mostrar modal
    modal.style.display = 'block';
    
    try {
        // Cargar datos del reclamo
        await cargarDatosReclamo(complaintId);
        await cargarComentariosReclamo(complaintId);
        await cargarUsuariosAsignables(complaintId);
        await cargarEstadosReclamo(complaintId);
        
        // Inicializar formularios del modal
        setupComplaintModalForms();
    } catch (error) {
        console.error('Error al cargar datos del reclamo:', error);
        showNotification('Error al cargar el reclamo', 'error');
    }
}

function closeComplaintModal() {
    const modal = document.getElementById('complaint-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentComplaintId = null;
}

// Cargar detalles del reclamo
async function cargarDatosReclamo(complaintId) {
    try {
        const res = await fetch(`/foro/reclamos/${complaintId}/detalle/`);
        const data = await res.json();
        if (data.success) {
            document.getElementById('complaint-modal-title').textContent = data.titulo;
            document.getElementById('complaint-modal-creator').textContent = data.usuario_creador;
            document.getElementById('complaint-modal-date').textContent = data.fecha_creacion;
            document.getElementById('complaint-modal-status').textContent = data.estado_display;
            document.getElementById('complaint-modal-description').textContent = data.descripcion;
            // Adjuntos
            let attachments = '';
            if (data.imagen_url) {
                attachments += `<div style='margin-bottom:8px;'><img src='${data.imagen_url}' alt='Imagen' style='max-width:100%;border-radius:12px;'></div>`;
            }
            if (data.archivo_url) {
                attachments += `<div><a href='${data.archivo_url}' target='_blank' style='color:#1d9bf0;font-weight:500;'><i class='fas fa-file'></i> Descargar archivo</a></div>`;
            }
            document.getElementById('complaint-modal-attachments').innerHTML = attachments;
            // Asignados
            const select = document.getElementById('complaint-assign-users');
            if (select) {
                Array.from(select.options).forEach(opt => {
                    opt.selected = data.asignados_ids && data.asignados_ids.includes(parseInt(opt.value));
                });
            }
            // Estado
            const estadoSelect = document.getElementById('complaint-status-select');
            if (estadoSelect) {
                estadoSelect.value = data.estado;
            }
        }
    } catch (e) {
        document.getElementById('complaint-modal-description').textContent = 'Error al cargar el reclamo';
    }
}

// Cargar comentarios del reclamo
async function cargarComentariosReclamo(complaintId) {
    const commentsList = document.getElementById('complaint-comments-list');
    commentsList.innerHTML = '<div style="text-align:center;color:#888;">Cargando comentarios...</div>';
    try {
        const res = await fetch(`/foro/reclamos/${complaintId}/comentarios/`);
        const data = await res.json();
        console.log('Comentarios reclamo:', data); // DEBUG
        if (data.comentarios && data.comentarios.length > 0) {
            commentsList.innerHTML = renderComplaintCommentTree(data.comentarios);
        } else {
            commentsList.innerHTML = '<div style="text-align:center;color:#888;">No hay comentarios aún.</div>';
        }
    } catch (e) {
        commentsList.innerHTML = '<div style="text-align:center;color:#e0245e;">Error al cargar comentarios</div>';
    }
}

// Renderiza árbol de comentarios (puedes reutilizar renderCommentTree si es igual)
function renderComplaintCommentTree(comments, level = 0) {
    return comments.map(c => `
        <div class="modal-comment-item" style="margin-left:${level * 24}px;display:flex;gap:12px;align-items:flex-start;">
            <img src="/static/images/userProfile.jpg" alt="Usuario" class="avatar-img modal-avatar" style="width:40px;height:40px;object-fit:cover;border-radius:50%;flex-shrink:0;">
            <div style="flex:1;">
                <div class="modal-comment-header" style="display:flex;align-items:center;gap:8px;">
                    <span class="modal-comment-user">${c.usuario}</span>
                    <span class="modal-comment-date">${c.fecha}</span>
                    ${c.puede_eliminar && !c.is_deleted ? `<button class="modal-comment-delete-btn" onclick="eliminarComentarioReclamo(${c.id})" title="Eliminar comentario"><i class="fas fa-trash"></i></button>` : ''}
                    ${!c.is_deleted ? `<button class="modal-comment-reply-btn" onclick="mostrarRespuestaFormReclamo(${c.id})" title="Responder"><i class="fas fa-reply"></i></button>` : ''}
                </div>
                <div class="modal-comment-content">${c.contenido}</div>
                ${(c.imagen_url ? `<div style='margin:8px 0;'><img src='${c.imagen_url}' alt='Imagen' style='max-width:180px;max-height:120px;border-radius:8px;'></div>` : '')}
                ${(c.archivo_url ? `<div><a href='${c.archivo_url}' target='_blank' style='color:#1d9bf0;font-weight:500;'><i class='fas fa-file'></i> Descargar archivo</a></div>` : '')}
                <div id="reply-form-container-reclamo-${c.id}"></div>
                ${c.replies && c.replies.length > 0 ? renderComplaintCommentTree(c.replies, level + 1) : ''}
            </div>
        </div>
    `).join('');
}

// Mostrar formulario de respuesta inline para reclamo
function mostrarRespuestaFormReclamo(commentId) {
    document.querySelectorAll('.modal-reply-form').forEach(f => f.remove());
    const container = document.getElementById(`reply-form-container-reclamo-${commentId}`);
    if (!container) return;
    container.innerHTML = `
        <form class="modal-reply-form" onsubmit="enviarRespuestaReclamo(event, ${commentId})">
            <textarea class="modal-reply-input" placeholder="Escribe tu respuesta..." required></textarea>
            <button type="submit" class="post-btn" style="margin-top:6px;">Responder</button>
            <button type="button" class="post-btn" style="background:#eee;color:#333;margin-left:8px;" onclick="this.closest('form').remove()">Cancelar</button>
        </form>
    `;
    container.querySelector('textarea').focus();
}

// Enviar respuesta a un comentario de reclamo
async function enviarRespuestaReclamo(event, commentId) {
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const contenido = textarea.value.trim();
    if (!contenido) return;
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Enviando...';
    try {
        const response = await fetch(`/foro/reclamos/comentario/${commentId}/responder/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `contenido=${encodeURIComponent(contenido)}`
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Respuesta publicada', 'success');
            cargarComentariosReclamo(currentComplaintId);
        } else {
            showNotification(data.error || 'Error al responder', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Responder';
    }
}

// Eliminar comentario de reclamo
async function eliminarComentarioReclamo(commentId) {
    if (!confirm('¿Eliminar este comentario?')) return;
    try {
        const response = await fetch(`/foro/reclamos/comentario/${commentId}/eliminar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Comentario eliminado', 'success');
            cargarComentariosReclamo(currentComplaintId);
        } else {
            showNotification(data.error || 'Error al eliminar', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    }
}

// Cargar usuarios asignables
async function cargarUsuariosAsignables(complaintId) {
    const select = document.getElementById('complaint-assign-users');
    select.innerHTML = '<option>Cargando...</option>';
    try {
        const res = await fetch('/foro/reclamos/usuarios-asignables/');
        const data = await res.json();
        if (data.usuarios) {
            select.innerHTML = '';
            data.usuarios.forEach(u => {
                const opt = document.createElement('option');
                opt.value = u.id;
                opt.textContent = u.nombre;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        select.innerHTML = '<option>Error</option>';
    }
}

// Cargar estados posibles
async function cargarEstadosReclamo(complaintId) {
    const select = document.getElementById('complaint-status-select');
    select.innerHTML = '';
    try {
        const res = await fetch('/foro/reclamos/estados/');
        const data = await res.json();
        if (data.estados) {
            data.estados.forEach(e => {
                const opt = document.createElement('option');
                opt.value = e.value;
                opt.textContent = e.display;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        select.innerHTML = '<option>Error</option>';
    }
}



// Inicializar formularios del modal de reclamos
function setupComplaintModalForms() {
    console.log('Inicializando formularios del modal de reclamos...');
    
    // Formulario de comentarios
    const complaintCommentForm = document.getElementById('complaint-comment-form');
    if (complaintCommentForm) {
        console.log('Formulario de comentarios encontrado');
        // Remover listeners existentes para evitar duplicados
        complaintCommentForm.removeEventListener('submit', handleComplaintCommentSubmit);
        complaintCommentForm.addEventListener('submit', handleComplaintCommentSubmit);
    } else {
        console.error('No se encontró el formulario de comentarios');
    }
    
    // Formulario de estado
    const complaintStatusForm = document.getElementById('complaint-status-form');
    if (complaintStatusForm) {
        console.log('Formulario de estado encontrado');
        complaintStatusForm.removeEventListener('submit', handleComplaintStatusSubmit);
        complaintStatusForm.addEventListener('submit', handleComplaintStatusSubmit);
    } else {
        console.error('No se encontró el formulario de estado');
    }
    
    // Formulario de asignación
    const complaintAssignForm = document.getElementById('complaint-assign-form');
    if (complaintAssignForm) {
        console.log('Formulario de asignación encontrado');
        complaintAssignForm.removeEventListener('submit', handleComplaintAssignSubmit);
        complaintAssignForm.addEventListener('submit', handleComplaintAssignSubmit);
    } else {
        console.error('No se encontró el formulario de asignación');
    }
}

// Handlers para los formularios del modal
async function handleComplaintCommentSubmit(event) {
    event.preventDefault();
    if (!currentComplaintId) return;
    const formData = new FormData(event.target);
    const submitBtn = event.target.querySelector('.complaint-comment-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando...';
    try {
        const response = await fetch(`/foro/reclamos/${currentComplaintId}/comentar/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        const data = await response.json();
        if (data.success) {
            showNotification('Comentario publicado', 'success');
            event.target.reset();
            cargarComentariosReclamo(currentComplaintId);
        } else {
            showNotification(data.error || 'Error al comentar', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Comentar';
    }
}

async function handleComplaintStatusSubmit(event) {
    event.preventDefault();
    console.log('Enviando cambio de estado...');
    if (!currentComplaintId) {
        console.error('No hay currentComplaintId');
        return;
    }
    const estado = document.getElementById('complaint-status-select').value;
    console.log('Estado seleccionado:', estado);
    const btn = event.target.querySelector('.complaint-action-btn');
    btn.disabled = true;
    btn.textContent = 'Cambiando...';
    try {
        const response = await fetch(`/foro/reclamos/${currentComplaintId}/cambiar-estado/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `estado=${encodeURIComponent(estado)}`
        });
        console.log('Respuesta del servidor:', response.status);
        const data = await response.json();
        console.log('Datos de respuesta:', data);
        if (data.success) {
            showNotification('Estado actualizado', 'success');
            cargarDatosReclamo(currentComplaintId);
        } else {
            showNotification(data.error || 'Error al cambiar estado', 'error');
        }
    } catch (error) {
        console.error('Error al cambiar estado:', error);
        showNotification('Error de conexión', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Cambiar estado';
    }
}

async function handleComplaintAssignSubmit(event) {
    event.preventDefault();
    console.log('Enviando asignación de usuarios...');
    if (!currentComplaintId) {
        console.error('No hay currentComplaintId');
        return;
    }
    const select = document.getElementById('complaint-assign-users');
    const asignados = Array.from(select.selectedOptions).map(opt => opt.value);
    console.log('Usuarios seleccionados:', asignados);
    const btn = event.target.querySelector('.complaint-action-btn');
    btn.disabled = true;
    btn.textContent = 'Asignando...';
    try {
        const response = await fetch(`/foro/reclamos/${currentComplaintId}/asignar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ asignados })
        });
        console.log('Respuesta del servidor:', response.status);
        const data = await response.json();
        console.log('Datos de respuesta:', data);
        if (data.success) {
            showNotification('Usuarios asignados', 'success');
            cargarDatosReclamo(currentComplaintId);
        } else {
            showNotification(data.error || 'Error al asignar', 'error');
        }
    } catch (error) {
        console.error('Error al asignar usuarios:', error);
        showNotification('Error de conexión', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Asignar';
    }
}

// Inicializar listeners al cargar reclamos
if (document.getElementById('complaints-list')) {
    setTimeout(setupComplaintModalClicks, 500);
}

// Función para reinicializar todo después de cambios
function reinicializarReclamos() {
    if (document.getElementById('complaints-list')) {
        cargarReclamosAside();
        setTimeout(() => {
            setupComplaintModalClicks();
        }, 100);
    }
    if (document.getElementById('resolved-complaints-list')) {
        cargarReclamosResueltosAside();
        setupResolvedComplaintsSearch();
    }
} 
