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
    
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Update HTML attribute
            html.setAttribute('data-bs-theme', newTheme);
            
            // Update stylesheet reference
            const themeStyle = document.getElementById('theme-style');
            if (themeStyle) {
                if (newTheme === 'dark') {
                    themeStyle.href = 'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css';
                } else {
                    themeStyle.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css';
                }
            }
            
            // Show/hide appropriate icons and text
            const darkIcons = document.querySelectorAll('.theme-icon-dark');
            const lightIcons = document.querySelectorAll('.theme-icon-light');
            const darkText = document.querySelectorAll('.theme-text-dark');
            const lightText = document.querySelectorAll('.theme-text-light');
            
            if (newTheme === 'dark') {
                darkIcons.forEach(icon => icon.classList.remove('d-none'));
                lightIcons.forEach(icon => icon.classList.add('d-none'));
                darkText.forEach(text => text.classList.remove('d-none'));
                lightText.forEach(text => text.classList.add('d-none'));
            } else {
                darkIcons.forEach(icon => icon.classList.add('d-none'));
                lightIcons.forEach(icon => icon.classList.remove('d-none'));
                darkText.forEach(text => text.classList.add('d-none'));
                lightText.forEach(text => text.classList.remove('d-none'));
            }
            
            // Save preference to localStorage
            localStorage.setItem('theme', newTheme);
        });
        
        // Apply saved theme preference on page load
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            // We'll use dispatching a click event to use the same logic as the click handler
            if ((savedTheme === 'light' && document.documentElement.getAttribute('data-bs-theme') === 'dark') ||
                (savedTheme === 'dark' && document.documentElement.getAttribute('data-bs-theme') === 'light')) {
                themeToggle.click();
            }
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
