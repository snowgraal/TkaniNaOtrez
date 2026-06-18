// Живой поиск
function initLiveSearch() {
    const searchInput = document.querySelector('[name="search"]');
    if (!searchInput) return;

    let timeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            const form = document.getElementById('filterForm');
            if (form) form.submit();
        }, 500);
    });
}

// Закрытие алертов
document.addEventListener('DOMContentLoaded', function() {
    initLiveSearch();

    // Автозакрытие флеш-сообщений
    setTimeout(() => {
        document.querySelectorAll('.alert-dismissible').forEach(alert => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);

    // Закрытие мобильного меню при клике на ссылку
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse.classList.contains('show')) {
                bootstrap.Collapse.getInstance(navbarCollapse).hide();
            }
        });
    });

    // Добавляем активный класс текущей странице
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Плавный скролл для якорных ссылок
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Отслеживание касаний для мобильных
let touchStartY = 0;
document.addEventListener('touchstart', function(e) {
    touchStartY = e.touches[0].clientY;
}, { passive: true });

// Предотвращение двойного тапа на мобильных
let lastTap = 0;
document.addEventListener('touchend', function(e) {
    const currentTime = new Date().getTime();
    const tapLength = currentTime - lastTap;
    if (tapLength < 300 && tapLength > 0) {
        e.preventDefault();
    }
    lastTap = currentTime;
});