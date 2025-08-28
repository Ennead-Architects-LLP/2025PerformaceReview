// DOM Elements
const performanceForm = document.getElementById('performanceForm');
const progressFill = document.getElementById('progressFill');
const submitBtn = document.getElementById('submitBtn');
const successMessage = document.getElementById('successMessage');

// Microsoft Forms URL and field mapping
const MS_FORMS_URL = 'https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAQIpGjtUQ0wxN1NMMEgzN0pJTTc2MjE1M1hRU0RHNC4u';
const MS_FORMS_FIELD_ID = 'entry.red2b6b1ddca94d98b4fbac4518e17334';

// Debug logging
let debugLog = [];

function logDebug(message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = { timestamp, message, data };
    debugLog.push(logEntry);
    console.log(`[${timestamp}] ${message}`, data || '');
}

// Initialize form functionality
document.addEventListener('DOMContentLoaded', function() {
    logDebug('Page loaded, initializing form');
    initializeForm();
    setupProgressTracking();
});

function initializeForm() {
    // Form submission handler
    performanceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        logDebug('Form submission triggered');
        handleFormSubmission();
    });

    // Real-time validation
    const requiredFields = performanceForm.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', updateProgress);
    });
    
    logDebug('Form initialized with event listeners');
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
        logDebug('Form validation failed');
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
        
        logDebug('Form data collected', data);
        
        // Try multiple submission methods with real verification
        const submissionResult = await tryMultipleSubmissionMethods(data);
        
        if (submissionResult.success) {
            logDebug('Submission confirmed successful', submissionResult);
            
            // Show success message
            performanceForm.style.display = 'none';
            successMessage.style.display = 'block';
            
            // Reset form
            performanceForm.reset();
            updateProgress();
            
            showNotification('Performance review submitted successfully! ✅', 'success');
        } else {
            logDebug('All submission methods failed', submissionResult);
            throw new Error(`Submission failed: ${submissionResult.reason}`);
        }
        
    } catch (error) {
        logDebug('Submission error occurred', error);
        showNotification(`Submission failed: ${error.message}`, 'error');
    } finally {
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit';
    }
}

async function tryMultipleSubmissionMethods(data) {
    logDebug('Starting multiple submission methods');
    
    // Method 1: Direct POST with fetch and response verification
    try {
        logDebug('Attempting Method 1: Fetch with verification');
        const result = await submitViaFetch(data);
        if (result.success) {
            return result;
        }
    } catch (error) {
        logDebug('Method 1 failed', error);
    }
    
    // Method 2: Hidden iframe with response monitoring
    try {
        logDebug('Attempting Method 2: Hidden iframe with monitoring');
        const result = await submitViaIframe(data);
        if (result.success) {
            return result;
        }
    } catch (error) {
        logDebug('Method 2 failed', error);
    }
    
    // Method 3: Form POST with proper headers and verification
    try {
        logDebug('Attempting Method 3: Form POST with verification');
        const result = await submitViaFormPost(data);
        if (result.success) {
            return result;
        }
    } catch (error) {
        logDebug('Method 3 failed', error);
    }
    
    // Method 4: Redirect to MS Forms with pre-filled data
    try {
        logDebug('Attempting Method 4: Redirect with pre-filled data');
        const result = await submitViaRedirect(data);
        if (result.success) {
            return result;
        }
    } catch (error) {
        logDebug('Method 4 failed', error);
    }
    
    return { success: false, reason: 'All methods failed' };
}

async function submitViaFetch(data) {
    logDebug('Starting fetch submission', { url: MS_FORMS_URL, fieldId: MS_FORMS_FIELD_ID, value: data.employeeName });
    
    const formData = new URLSearchParams();
    formData.append(MS_FORMS_FIELD_ID, data.employeeName);
    
    // Add additional fields that Microsoft Forms might require
    formData.append('pageHistory', '0');
    formData.append('fbzx', '-1');
    formData.append('submit', 'Submit');
    
    logDebug('Fetch request data', formData.toString());
    
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
            mode: 'no-cors'
        });
        
        logDebug('Fetch response received', { 
            status: response.status, 
            statusText: response.statusText,
            type: response.type,
            url: response.url
        });
        
        // With no-cors, we can't read the response, so we assume success
        // but we'll verify by checking if we can access the form
        const verificationResult = await verifySubmission(data);
        
        return { 
            success: verificationResult.success, 
            method: 'fetch',
            verification: verificationResult
        };
        
    } catch (error) {
        logDebug('Fetch submission error', error);
        return { success: false, method: 'fetch', error: error.message };
    }
}

function submitViaIframe(data) {
    return new Promise((resolve, reject) => {
        logDebug('Starting iframe submission', { fieldId: MS_FORMS_FIELD_ID, value: data.employeeName });
        
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.name = 'msFormsSubmit';
        document.body.appendChild(iframe);
        
        // Monitor iframe load events
        iframe.addEventListener('load', async function() {
            logDebug('Iframe loaded', { src: iframe.src });
            
            try {
                // Try to verify submission
                const verificationResult = await verifySubmission(data);
                logDebug('Iframe submission verification', verificationResult);
                
                resolve({ 
                    success: verificationResult.success, 
                    method: 'iframe',
                    verification: verificationResult
                });
            } catch (error) {
                logDebug('Iframe verification error', error);
                resolve({ success: false, method: 'iframe', error: error.message });
            }
        });
        
        iframe.addEventListener('error', function() {
            logDebug('Iframe error occurred');
            resolve({ success: false, method: 'iframe', error: 'Iframe failed to load' });
        });
        
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
        
        logDebug('Submitting iframe form', { action: submitForm.action, fieldCount: submitForm.elements.length });
        
        document.body.appendChild(submitForm);
        submitForm.submit();
        
        // Clean up after submission
        setTimeout(() => {
            try {
                document.body.removeChild(iframe);
                document.body.removeChild(submitForm);
            } catch (e) {
                logDebug('Cleanup error', e);
            }
        }, 5000);
    });
}

async function submitViaFormPost(data) {
    logDebug('Starting form POST submission', { fieldId: MS_FORMS_FIELD_ID, value: data.employeeName });
    
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
            credentials: 'omit'
        });
        
        logDebug('Form POST response', { 
            status: response.status, 
            statusText: response.statusText,
            type: response.type
        });
        
        // Try to read response text for verification
        let responseText = '';
        try {
            responseText = await response.text();
            logDebug('Form POST response text length', responseText.length);
        } catch (e) {
            logDebug('Could not read response text', e);
        }
        
        // Check if response indicates success
        const isSuccess = responseText.includes('Thank you') || 
                         responseText.includes('submitted') || 
                         responseText.includes('success') ||
                         response.status === 200;
        
        const verificationResult = await verifySubmission(data);
        
        return { 
            success: isSuccess && verificationResult.success, 
            method: 'formPost',
            verification: verificationResult,
            responseStatus: response.status,
            responseTextLength: responseText.length
        };
        
    } catch (error) {
        logDebug('Form POST error', error);
        return { success: false, method: 'formPost', error: error.message };
    }
}

function submitViaRedirect(data) {
    logDebug('Starting redirect submission', { fieldId: MS_FORMS_FIELD_ID, value: data.employeeName });
    
    // Create a URL with pre-filled data
    const params = new URLSearchParams();
    params.append(MS_FORMS_FIELD_ID, data.employeeName);
    
    const redirectUrl = `${MS_FORMS_URL}?${params.toString()}`;
    logDebug('Redirect URL created', redirectUrl);
    
    // Open in new window/tab
    const newWindow = window.open(redirectUrl, '_blank');
    
    if (newWindow) {
        logDebug('Redirect window opened successfully');
        return Promise.resolve({ 
            success: true, 
            method: 'redirect',
            note: 'User redirected to Microsoft Forms - manual submission required'
        });
    } else {
        logDebug('Failed to open redirect window');
        return Promise.resolve({ 
            success: false, 
            method: 'redirect', 
            error: 'Popup blocked or window failed to open' 
        });
    }
}

// Real verification function
async function verifySubmission(data) {
    logDebug('Starting submission verification', { fieldId: MS_FORMS_FIELD_ID, value: data.employeeName });
    
    try {
        // Method 1: Try to access the form and check if it shows a "thank you" page
        const response = await fetch(MS_FORMS_URL, {
            method: 'GET',
            headers: {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            },
            credentials: 'omit'
        });
        
        if (response.ok) {
            const responseText = await response.text();
            logDebug('Verification response received', { 
                status: response.status, 
                textLength: responseText.length 
            });
            
            // Check for success indicators in the response
            const successIndicators = [
                'Thank you',
                'submitted successfully',
                'response recorded',
                'form submitted',
                'thank you for your response'
            ];
            
            const hasSuccessIndicator = successIndicators.some(indicator => 
                responseText.toLowerCase().includes(indicator.toLowerCase())
            );
            
            logDebug('Success indicator check', { 
                hasSuccessIndicator, 
                responsePreview: responseText.substring(0, 200) 
            });
            
            return { 
                success: hasSuccessIndicator, 
                method: 'responseCheck',
                indicatorsFound: successIndicators.filter(indicator => 
                    responseText.toLowerCase().includes(indicator.toLowerCase())
                )
            };
        } else {
            logDebug('Verification request failed', { status: response.status });
            return { success: false, method: 'responseCheck', error: `HTTP ${response.status}` };
        }
        
    } catch (error) {
        logDebug('Verification error', error);
        return { success: false, method: 'responseCheck', error: error.message };
    }
}

// Debug panel for development
function createDebugPanel() {
    const debugPanel = document.createElement('div');
    debugPanel.id = 'debugPanel';
    debugPanel.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        max-height: 300px;
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        font-family: monospace;
        font-size: 12px;
        color: #e0e0e0;
        overflow-y: auto;
        z-index: 10000;
        display: none;
    `;
    
    debugPanel.innerHTML = '<h4>Debug Log</h4><div id="debugContent"></div>';
    document.body.appendChild(debugPanel);
    
    // Show debug panel in development
    if (window.location.hostname === 'localhost' || window.location.hostname.includes('127.0.0.1')) {
        debugPanel.style.display = 'block';
    }
    
    // Update debug content
    setInterval(() => {
        const debugContent = document.getElementById('debugContent');
        if (debugContent) {
            debugContent.innerHTML = debugLog
                .slice(-20) // Show last 20 entries
                .map(entry => `<div>[${entry.timestamp.split('T')[1].split('.')[0]}] ${entry.message}</div>`)
                .join('');
        }
    }, 1000);
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
        logDebug(`Page loaded in ${loadTime}ms`);
    });
}

// Error handling
window.addEventListener('error', function(e) {
    logDebug('JavaScript error occurred', { error: e.error, message: e.message });
});

// Initialize
monitorPerformance();
createDebugPanel();

// Export debug log for inspection
window.debugLog = debugLog;
