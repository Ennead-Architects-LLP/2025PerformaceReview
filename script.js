// DOM Elements
const performanceForm = document.getElementById('performanceForm');
const progressFill = document.getElementById('progressFill');
const submitBtn = document.getElementById('submitBtn');
const successMessage = document.getElementById('successMessage');

// Microsoft Forms URL and field mapping
const MS_FORMS_URL = 'https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAQIpGjtUQ0wxN1NMMEgzN0pJTTc2MjE1M1hRU0RHNC4u';
const MS_FORMS_FIELD_ID = 'entry.red2b6b1ddca94d98b4fbac4518e17334';

// Initialize form functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
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

function setupProgressTracking() {
    const formFields = performanceForm.querySelectorAll('input, textarea');
    formFields.forEach(field => {
        field.addEventListener('input', updateProgress);
        field.addEventListener('change', updateProgress);
    });
}

function updateProgress() {
    const totalFields = performanceForm.querySelectorAll('input, textarea').length;
    let completedFields = 0;

    performanceForm.querySelectorAll('input, textarea').forEach(field => {
        if (field.value.trim() !== '') {
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

async function handleFormSubmission() {
    if (!validateForm()) {
        showNotification('Please fill in all required fields correctly', 'error');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Submitting...';

    try {
        // Collect form data
        const formData = new FormData(performanceForm);
        const data = Object.fromEntries(formData);
        
        console.log('Form data to submit:', data);
        
        // Try multiple submission methods
        const submissionSuccess = await tryMultipleSubmissionMethods(data);
        
        if (submissionSuccess) {
            // Show success message
            performanceForm.style.display = 'none';
            successMessage.style.display = 'block';
            
            // Reset form
            performanceForm.reset();
            updateProgress();
            
            showNotification('Performance review submitted successfully!', 'success');
        } else {
            throw new Error('All submission methods failed');
        }
        
    } catch (error) {
        console.error('Submission error:', error);
        showNotification('There was an error submitting your form. Please try again.', 'error');
    } finally {
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit';
    }
}

async function tryMultipleSubmissionMethods(data) {
    console.log('Trying multiple submission methods...');
    
    // Method 1: Direct POST with fetch (no-cors)
    try {
        console.log('Attempting Method 1: Fetch with no-cors');
        await submitViaFetch(data);
        return true;
    } catch (error) {
        console.log('Method 1 failed:', error);
    }
    
    // Method 2: Hidden iframe submission
    try {
        console.log('Attempting Method 2: Hidden iframe');
        await submitViaIframe(data);
        return true;
    } catch (error) {
        console.log('Method 2 failed:', error);
    }
    
    // Method 3: Form POST with proper headers
    try {
        console.log('Attempting Method 3: Form POST with headers');
        await submitViaFormPost(data);
        return true;
    } catch (error) {
        console.log('Method 3 failed:', error);
    }
    
    // Method 4: Redirect to MS Forms with pre-filled data
    try {
        console.log('Attempting Method 4: Redirect with pre-filled data');
        await submitViaRedirect(data);
        return true;
    } catch (error) {
        console.log('Method 4 failed:', error);
    }
    
    return false;
}

async function submitViaFetch(data) {
    const formData = new URLSearchParams();
    formData.append(MS_FORMS_FIELD_ID, data.employeeName);
    
    // Add additional fields that Microsoft Forms might require
    formData.append('pageHistory', '0');
    formData.append('fbzx', '-1');
    formData.append('submit', 'Submit');
    
    const response = await fetch(MS_FORMS_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://forms.office.com',
            'Referer': MS_FORMS_URL,
        },
        body: formData,
        mode: 'no-cors'
    });
    
    console.log('Fetch response:', response);
    return response;
}

function submitViaIframe(data) {
    return new Promise((resolve, reject) => {
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.name = 'msFormsSubmit';
        document.body.appendChild(iframe);
        
        const submitForm = document.createElement('form');
        submitForm.method = 'POST';
        submitForm.action = MS_FORMS_URL;
        submitForm.target = 'msFormsSubmit';
        submitForm.style.display = 'none';
        
        // Add the employee name field
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = MS_FORMS_FIELD_ID;
        input.value = data.employeeName;
        submitForm.appendChild(input);
        
        // Add additional required fields
        const pageHistory = document.createElement('input');
        pageHistory.type = 'hidden';
        pageHistory.name = 'pageHistory';
        pageHistory.value = '0';
        submitForm.appendChild(pageHistory);
        
        const fbzx = document.createElement('input');
        fbzx.type = 'hidden';
        fbzx.name = 'fbzx';
        fbzx.value = '-1';
        submitForm.appendChild(fbzx);
        
        const submitBtn = document.createElement('input');
        submitBtn.type = 'hidden';
        submitBtn.name = 'submit';
        submitBtn.value = 'Submit';
        submitForm.appendChild(submitBtn);
        
        console.log(`Submitting via iframe: ${MS_FORMS_FIELD_ID} = ${data.employeeName}`);
        
        document.body.appendChild(submitForm);
        submitForm.submit();
        
        // Clean up after submission
        setTimeout(() => {
            try {
                document.body.removeChild(iframe);
                document.body.removeChild(submitForm);
            } catch (e) {
                console.log('Cleanup error:', e);
            }
            resolve();
        }, 3000);
    });
}

async function submitViaFormPost(data) {
    const formData = new URLSearchParams();
    formData.append(MS_FORMS_FIELD_ID, data.employeeName);
    formData.append('pageHistory', '0');
    formData.append('fbzx', '-1');
    formData.append('submit', 'Submit');
    
    const response = await fetch(MS_FORMS_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
        credentials: 'omit'
    });
    
    console.log('Form POST response:', response);
    return response;
}

function submitViaRedirect(data) {
    // Create a URL with pre-filled data
    const params = new URLSearchParams();
    params.append(MS_FORMS_FIELD_ID, data.employeeName);
    
    const redirectUrl = `${MS_FORMS_URL}?${params.toString()}`;
    
    // Open in new window/tab
    window.open(redirectUrl, '_blank');
    
    return Promise.resolve();
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
        color: ${type === 'success' ? '#4ade80' : type === 'error' ? '#ef4444' : '#3b82f6'};
        padding: 15px 20px;
        border-radius: 4px;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        border: 1px solid ${type === 'success' ? '#2d5a3d' : type === 'error' ? '#5a2d2d' : '#2d3a5a'};
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
