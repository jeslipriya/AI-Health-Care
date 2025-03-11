/**
 * Main JavaScript file for Health Assistant App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips and popovers
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Flash messages auto-close
    setTimeout(function() {
        const alertList = document.querySelectorAll('.alert.alert-dismissible');
        alertList.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Handle mobile navigation
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(event) {
            if (navbarCollapse.classList.contains('show') && 
                !navbarToggler.contains(event.target) && 
                !navbarCollapse.contains(event.target)) {
                navbarToggler.click();
            }
        });
    }
    
    // Handle back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }
    
    // Dark mode toggle (if exists)
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            
            // Update icon
            const icon = darkModeToggle.querySelector('i');
            if (isDarkMode) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });
        
        // Check for saved dark mode preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.body.classList.add('dark-mode');
            const icon = darkModeToggle.querySelector('i');
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
    
    // Health tip refresher (if exists)
    const refreshTipBtn = document.getElementById('refresh-tip');
    if (refreshTipBtn) {
        refreshTipBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = refreshTipBtn.getAttribute('href');
        });
    }
});

/**
 * Format date to a readable string
 * @param {Date} date - Date object to format
 * @return {string} Formatted date string
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Display loading spinner
 * @param {HTMLElement} element - Element to replace with spinner
 * @param {string} spinnerSize - Size of spinner (sm, md, lg)
 */
function showSpinner(element, spinnerSize = '') {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = `<span class="spinner-border spinner-border-${spinnerSize}" role="status" aria-hidden="true"></span> Loading...`;
    element.disabled = true;
}

/**
 * Remove loading spinner and restore original content
 * @param {HTMLElement} element - Element containing spinner
 */
function hideSpinner(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
    }
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message 
 * @return {boolean} True if confirmed, false otherwise
 */
function confirmAction(message) {
    return confirm(message);
}
