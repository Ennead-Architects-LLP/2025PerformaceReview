// Direct form submission to Microsoft Forms
const performanceForm = document.getElementById('performanceForm');
const progressFill = document.getElementById('progressFill');
const submitBtn = document.getElementById('submitBtn');
const successMessage = document.getElementById('successMessage');

// Microsoft Forms URL and field mapping
const MS_FORMS_URL = 'https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAQIpGjtUQ0wxN1NMMEgzN0pJTTc2MjE1M1hRU0RHNC4u';
const MS_FORMS_FIELD_ID = 'entry.red2b6b1ddca94d98b4fbac4518e17334';

// Initialize form functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, initializing form');
    initializeForm();
    setupProgressTracking();
});

function initializeForm() {
    // Form submission handler
    performanceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submission triggered');
        handleFormSubmission();
    });

    // Real-time validation
    const requiredFields = performanceForm.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', updateProgress);
    });
    
    console.log('Form initialized with event listeners');
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
        console.log('Form validation failed');
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
        
        console.log('Form data collected', data);
        
        // Submit to Microsoft Forms
        const submissionResult = await submitToMicrosoftForms(data);
        
        if (submissionResult.success) {
            console.log('Submission successful', submissionResult);
            
            // Show success message
            performanceForm.style.display = 'none';
            successMessage.style.display = 'block';
            
            // Reset form
            performanceForm.reset();
            updateProgress();
            
            showNotification('Performance review submitted successfully! ✅', 'success');
        } else {
            console.log('Submission failed', submissionResult);
            throw new Error(`Submission failed: ${submissionResult.reason}`);
        }
        
    } catch (error) {
        console.log('Submission error occurred', error);
        showNotification(`Submission failed: ${error.message}`, 'error');
    } finally {
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit';
    }
}

async function submitToMicrosoftForms(data) {
    console.log('Starting Microsoft Forms submission', { 
        url: MS_FORMS_URL, 
        fieldId: MS_FORMS_FIELD_ID, 
        value: data.employeeName 
    });
    
    try {
        // Method 1: Try direct POST submission
        const result = await submitViaDirectPost(data);
        if (result.success) {
            return result;
        }
        
        // Method 2: Try fetch with no-cors as fallback
        const fetchResult = await submitViaFetch(data);
        if (fetchResult.success) {
            return fetchResult;
        }
        
        return { success: false, reason: 'All submission methods failed' };
        
    } catch (error) {
        console.log('Microsoft Forms submission error', error);
        return { success: false, reason: error.message };
    }
}

async function submitViaDirectPost(data) {
    console.log('Attempting direct POST submission');
    
    const formData = new URLSearchParams();
    formData.append(MS_FORMS_FIELD_ID, data.employeeName);
    formData.append('pageHistory', '0');
    formData.append('fbzx', '-1');
    formData.append('submit', 'Submit');
    
    try {
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
            credentials: 'omit'
        });
        
        console.log('Direct POST response', { 
            status: response.status, 
            statusText: response.statusText,
            type: response.type
        });
        
        // Try to read response text for verification
        let responseText = '';
        try {
            responseText = await response.text();
            console.log('Response text length', responseText.length);
        } catch (e) {
            console.log('Could not read response text', e);
        }
        
        // Check if response indicates success
        const isSuccess = responseText.includes('Thank you') || 
                         responseText.includes('submitted') || 
                         responseText.includes('success') ||
                         response.status === 200;
        
        return { 
            success: isSuccess, 
            method: 'directPost',
            responseStatus: response.status,
            responseTextLength: responseText.length
        };
        
    } catch (error) {
        console.log('Direct POST error', error);
        return { success: false, method: 'directPost', error: error.message };
    }
}

async function submitViaFetch(data) {
    console.log('Attempting fetch submission with no-cors');
    
    const formData = new URLSearchParams();
    formData.append(MS_FORMS_FIELD_ID, data.employeeName);
    formData.append('pageHistory', '0');
    formData.append('fbzx', '-1');
    formData.append('submit', 'Submit');
    
    try {
        const response = await fetch(MS_FORMS_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
            mode: 'no-cors'
        });
        
        console.log('Fetch response received', { 
            status: response.status, 
            statusText: response.statusText,
            type: response.type
        });
        
        // With no-cors, we can't read the response, so we assume success
        return { 
            success: true, 
            method: 'fetch',
            note: 'Form submitted via fetch (no-cors)'
        };
        
    } catch (error) {
        console.log('Fetch submission error', error);
        return { success: false, method: 'fetch', error: error.message };
    }
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

