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
        
        // Submit to Microsoft Forms using the EI-Post approach
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
        // Method 1: Try fetch with no-cors (like EI-Post)
        const result = await submitViaFetch(data);
        if (result.success) {
            return result;
        }
        
        // Method 2: Try iframe fallback (like EI-Post fallback)
        const iframeResult = await submitViaIframe(data);
        if (iframeResult.success) {
            return iframeResult;
        }
        
        return { success: false, reason: 'All submission methods failed' };
        
    } catch (error) {
        console.log('Microsoft Forms submission error', error);
        return { success: false, reason: error.message };
    }
}

async function submitViaFetch(data) {
    console.log('Attempting fetch submission (EI-Post method)');
    
    // Prepare form data like EI-Post does
    const formDataObj = {};
    formDataObj[MS_FORMS_FIELD_ID] = data.employeeName;
    formDataObj['pageHistory'] = '0';
    formDataObj['fbzx'] = '-1';
    formDataObj['submit'] = 'Submit';
    
    console.log('Form data prepared:', formDataObj);
    
    try {
        // Use fetch API with no-cors like EI-Post
        const submitPromise = fetch(MS_FORMS_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(formDataObj),
            mode: 'no-cors' // Required for Microsoft Forms (like Google Forms)
        });
        
        // Set a timeout for the submission (like EI-Post)
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Submission timeout')), 5000);
        });
        
        // Race between submission and timeout
        await Promise.race([submitPromise, timeoutPromise]);
        
        console.log('Fetch submission completed successfully');
        return { 
            success: true, 
            method: 'fetch',
            note: 'Form submitted via fetch (no-cors)'
        };
        
    } catch (error) {
        console.log('Fetch submission failed:', error);
        return { success: false, method: 'fetch', error: error.message };
    }
}

function submitViaIframe(data) {
    return new Promise((resolve) => {
        console.log('Attempting iframe submission (EI-Post fallback method)');
        
        // Create hidden iframe like EI-Post does
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
        
        // Create hidden form like EI-Post does
        const hiddenForm = document.createElement('form');
        hiddenForm.method = 'POST';
        hiddenForm.action = MS_FORMS_URL;
        hiddenForm.target = iframe.name;
        
        // Add form fields like EI-Post does
        const formFields = {
            [MS_FORMS_FIELD_ID]: data.employeeName,
            'pageHistory': '0',
            'fbzx': '-1',
            'submit': 'Submit'
        };
        
        for (let [key, value] of Object.entries(formFields)) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = value;
            hiddenForm.appendChild(input);
        }
        
        document.body.appendChild(hiddenForm);
        hiddenForm.submit();
        
        // Clean up like EI-Post does
        setTimeout(() => {
            try {
                document.body.removeChild(hiddenForm);
                document.body.removeChild(iframe);
            } catch (e) {
                console.log('Cleanup error:', e);
            }
        }, 500);
        
        console.log('Iframe submission completed');
        resolve({ 
            success: true, 
            method: 'iframe',
            note: 'Form submitted via iframe fallback'
        });
    });
}

// Notification system (using EI-Post's improved version)
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;

    // Add animation keyframes
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            .notification-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
            }
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                line-height: 1;
            }
            .notification-close:hover {
                opacity: 0.8;
            }
        `;
        document.head.appendChild(style);
    }

    // Add to page
    document.body.appendChild(notification);

    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

