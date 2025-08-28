// DOM Elements
const performanceForm = document.getElementById('performanceForm');
const progressFill = document.getElementById('progressFill');
const submitBtn = document.getElementById('submitBtn');
const successMessage = document.getElementById('successMessage');
const ratingStars = document.querySelectorAll('.rating-star');
const ratingValue = document.getElementById('ratingValue');

// Form validation and progress tracking
let currentRating = 0;

// Initialize form functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupRatingSystem();
    setupProgressTracking();
});

function initializeForm() {
    // Form submission handler
    performanceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmission();
    });

    // Real-time validation
    const requiredFields = performanceForm.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', updateProgress);
    });
}

function setupRatingSystem() {
    ratingStars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            setRating(rating);
        });

        star.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            highlightStars(rating);
        });

        star.addEventListener('mouseleave', function() {
            highlightStars(currentRating);
        });
    });
}

function setRating(rating) {
    currentRating = rating;
    ratingValue.value = rating;
    highlightStars(rating);
    updateProgress();
}

function highlightStars(rating) {
    ratingStars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function setupProgressTracking() {
    const formFields = performanceForm.querySelectorAll('input, select, textarea');
    formFields.forEach(field => {
        field.addEventListener('input', updateProgress);
        field.addEventListener('change', updateProgress);
    });
}

function updateProgress() {
    const totalFields = performanceForm.querySelectorAll('input, select, textarea').length;
    let completedFields = 0;

    performanceForm.querySelectorAll('input, select, textarea').forEach(field => {
        if (field.type === 'radio' || field.type === 'checkbox') {
            if (field.checked) {
                completedFields++;
            }
        } else if (field.value.trim() !== '') {
            completedFields++;
        }
    });

    const progressPercentage = Math.min((completedFields / totalFields) * 100, 100);
    progressFill.style.width = progressPercentage + '%';
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    // Remove existing error styling
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Validate required fields
    if (field.hasAttribute('required') && value === '') {
        showFieldError(field, 'This field is required');
        return false;
    }

    // Specific field validations
    if (field.id === 'employeeId' && value !== '') {
        if (!/^\d+$/.test(value)) {
            showFieldError(field, 'Employee ID must contain only numbers');
            return false;
        }
    }

    if (field.id === 'employeeName' && value !== '') {
        if (value.length < 2) {
            showFieldError(field, 'Name must be at least 2 characters long');
            return false;
        }
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function validateForm() {
    let isValid = true;
    const requiredFields = performanceForm.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!validateField({ target: field })) {
            isValid = false;
        }
    });

    return isValid;
}

function handleFormSubmission() {
    if (!validateForm()) {
        showNotification('Please fill in all required fields correctly', 'error');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Submitting...';

    // Simulate form submission (replace with actual submission logic)
    setTimeout(() => {
        // Collect form data
        const formData = new FormData(performanceForm);
        const data = Object.fromEntries(formData);
        
        // Log the data (replace with actual submission)
        console.log('Form submitted:', data);
        
        // Show success message
        performanceForm.style.display = 'none';
        successMessage.style.display = 'block';
        
        // Reset form
        performanceForm.reset();
        currentRating = 0;
        highlightStars(0);
        updateProgress();
        
        showNotification('Performance review submitted successfully!', 'success');
        
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Performance Review';
        
    }, 2000);
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#1e3a2e' : type === 'error' ? '#3a1e1e' : '#1e2a3a'};
        color: ${type === 'success' ? '#4ade80' : type === 'error' ? '#ff6b6b' : '#60a5fa'};
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        border: 1px solid ${type === 'success' ? '#2d5a3d' : type === 'error' ? '#5a2d2d' : '#2d3a5a'};
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
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

// Auto-save functionality (optional)
function autoSave() {
    const formData = new FormData(performanceForm);
    const data = Object.fromEntries(formData);
    localStorage.setItem('performanceReviewDraft', JSON.stringify(data));
}

function loadDraft() {
    const draft = localStorage.getItem('performanceReviewDraft');
    if (draft) {
        const data = JSON.parse(draft);
        Object.keys(data).forEach(key => {
            const field = performanceForm.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key];
                if (key === 'rating') {
                    setRating(parseInt(data[key]));
                }
            }
        });
        updateProgress();
    }
}

// Auto-save every 30 seconds
setInterval(autoSave, 30000);

// Load draft on page load
document.addEventListener('DOMContentLoaded', loadDraft);

// Performance monitoring
function monitorPerformance() {
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Initialize performance monitoring
monitorPerformance();
