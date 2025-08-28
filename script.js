// DOM Elements
const openFormBtn = document.getElementById('openFormBtn');
const previewBtn = document.getElementById('previewBtn');
const formModal = document.getElementById('formModal');
const closeModal = document.getElementById('closeModal');

// Microsoft Forms URL
const FORMS_URL = 'https://forms.office.com/r/W58xLC1vuW';

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    addLoadingAnimations();
});

function initializeEventListeners() {
    // Open form in new tab
    openFormBtn.addEventListener('click', function() {
        openFormBtn.classList.add('success-animation');
        setTimeout(() => {
            window.open(FORMS_URL, '_blank');
            openFormBtn.classList.remove('success-animation');
        }, 300);
    });

    // Preview form in modal
    previewBtn.addEventListener('click', function() {
        formModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        closeModalModal();
    });

    // Close modal when clicking outside
    formModal.addEventListener('click', function(e) {
        if (e.target === formModal) {
            closeModalModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && formModal.style.display === 'block') {
            closeModalModal();
        }
    });
}

function closeModalModal() {
    formModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function addLoadingAnimations() {
    // Add staggered animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
    });

    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Analytics tracking (optional)
function trackFormOpen() {
    // You can add Google Analytics or other tracking here
    console.log('Form opened at:', new Date().toISOString());
}

// Form preview iframe loading handler
function handleIframeLoad() {
    const iframe = document.querySelector('#formModal iframe');
    if (iframe) {
        iframe.addEventListener('load', function() {
            console.log('Form iframe loaded successfully');
        });
    }
}

// Add smooth scrolling for better UX
function addSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Performance monitoring
function monitorPerformance() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
    });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    handleIframeLoad();
    addSmoothScrolling();
    monitorPerformance();
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Add some interactive feedback
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
