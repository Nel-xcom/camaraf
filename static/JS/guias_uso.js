// Funcionalidad del carrusel de archivos
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('files-carousel');
    const prevBtn = document.getElementById('prev-files');
    const nextBtn = document.getElementById('next-files');
    let currentPosition = 0;
    const cardWidth = 280; // 250px + 30px margin

    function updateCarousel() {
        carousel.style.transform = `translateX(-${currentPosition}px)`;
    }

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPosition > 0) {
                currentPosition -= cardWidth;
                updateCarousel();
            }
        });

        nextBtn.addEventListener('click', () => {
            const maxPosition = (carousel.children.length - 1) * cardWidth;
            if (currentPosition < maxPosition) {
                currentPosition += cardWidth;
                updateCarousel();
            }
        });
    }

    // Funcionalidad de búsqueda de archivos
    const searchFiles = document.getElementById('search-files');
    if (searchFiles) {
        searchFiles.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const fileCards = document.querySelectorAll('.file-card');
            
            fileCards.forEach(card => {
                const title = card.getAttribute('data-title');
                if (title && title.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Funcionalidad de búsqueda de videos
    const searchVideos = document.getElementById('search-videos');
    if (searchVideos) {
        searchVideos.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const videoCards = document.querySelectorAll('.video-card');
            
            videoCards.forEach(card => {
                const title = card.getAttribute('data-title');
                if (title && title.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Los enlaces ya están configurados en el HTML para las funcionalidades reales
}); 