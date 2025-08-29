const express = require('express');
const cors = require('cors');
const puppeteer = require('puppeteer');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({
    origin: ['https://ennead-architects-llp.github.io', 'http://localhost:3000'],
    credentials: false
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files (your website)
app.use(express.static('.'));

// Microsoft Forms configuration
const MS_FORMS_URL = 'https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAANAAQIpGjtUQ0wxN1NMMEgzN0pJTTc2MjE1M1hRU0RHNC4u';
const MS_FORMS_FIELD_ID = 'entry.red2b6b1ddca94d98b4fbac4518e17334';

// Browser automation for MS Forms submission
async function submitToMSFormsWithBrowser(employeeName) {
    let browser = null;
    try {
        console.log('🚀 Starting browser automation for MS Forms submission...');
        
        // Launch browser
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        
        // Set user agent to avoid detection
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
        
        console.log('📄 Loading MS Forms page...');
        
        // Navigate to MS Forms
        await page.goto(MS_FORMS_URL, { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });

        console.log('⏳ Waiting for form to load...');
        
        // Wait for the form to be fully loaded
        await page.waitForTimeout(5000);
        
        // Wait for the input field to be available
        await page.waitForSelector(`input[name="${MS_FORMS_FIELD_ID}"]`, { timeout: 15000 });
        
        console.log('✍️ Filling in employee name...');
        
        // Fill in the employee name
        await page.type(`input[name="${MS_FORMS_FIELD_ID}"]`, employeeName);
        
        console.log('🔍 Looking for submit button...');
        
        // Try different submit button selectors
        const submitSelectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            'button:contains("Submit")',
            'input[value="Submit"]',
            'button:contains("Send")',
            'input[value="Send"]',
            '[role="button"]',
            '.submit-button',
            '#submit-button'
        ];

        let submitButton = null;
        for (const selector of submitSelectors) {
            try {
                submitButton = await page.$(selector);
                if (submitButton) {
                    console.log(`✅ Found submit button with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                // Continue to next selector
            }
        }

        if (!submitButton) {
            // Try to find any clickable element that might be the submit button
            const buttons = await page.$$('button, input[type="submit"], input[type="button"]');
            if (buttons.length > 0) {
                submitButton = buttons[buttons.length - 1]; // Usually the last button is submit
                console.log('✅ Found submit button using fallback method');
            }
        }

        if (submitButton) {
            console.log('🚀 Clicking submit button...');
            await submitButton.click();
            
            // Wait for submission to complete
            await page.waitForTimeout(3000);
            
            // Check if submission was successful
            const pageContent = await page.content();
            const successIndicators = [
                'Thank you',
                'submitted successfully',
                'response recorded',
                'form submitted',
                'thank you for your response'
            ];

            const hasSuccessIndicator = successIndicators.some(indicator => 
                pageContent.toLowerCase().includes(indicator.toLowerCase())
            );

            if (hasSuccessIndicator) {
                console.log('✅ Form submitted successfully!');
                return { success: true, message: 'Form submitted successfully via browser automation' };
            } else {
                console.log('⚠️ Form may have been submitted, but no success indicator found');
                return { success: true, message: 'Form submitted (no success indicator detected)' };
            }
        } else {
            console.log('❌ Could not find submit button');
            return { success: false, message: 'Could not find submit button' };
        }

    } catch (error) {
        console.error('❌ Browser automation error:', error);
        return { 
            success: false, 
            message: 'Browser automation failed', 
            error: error.message 
        };
    } finally {
        if (browser) {
            await browser.close();
            console.log('🔒 Browser closed');
        }
    }
}

// Enhanced submission endpoint with browser automation
app.post('/api/submit-to-ms-forms', async (req, res) => {
    try {
        console.log('📝 Received submission request:', req.body);
        
        const { employeeName } = req.body;
        
        if (!employeeName) {
            return res.status(400).json({
                success: false,
                error: 'Employee name is required'
            });
        }

        console.log(`🤖 Starting browser automation for: ${employeeName}`);
        
        // Use browser automation to submit to MS Forms
        const result = await submitToMSFormsWithBrowser(employeeName);
        
        console.log('📊 Submission result:', result);
        
        res.json({
            success: result.success,
            message: result.message,
            method: 'browser-automation',
            employeeName: employeeName,
            error: result.error
        });

    } catch (error) {
        console.error('❌ Submission error:', error);
        
        res.status(500).json({
            success: false,
            error: error.message,
            method: 'browser-automation'
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        msFormsUrl: MS_FORMS_URL,
        fieldId: MS_FORMS_FIELD_ID,
        method: 'browser-automation'
    });
});

// Test endpoint to check MS Forms accessibility
app.get('/api/test-ms-forms', async (req, res) => {
    try {
        console.log('🧪 Testing MS Forms accessibility with browser...');
        
        let browser = null;
        try {
            browser = await puppeteer.launch({
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            });

            const page = await browser.newPage();
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
            
            await page.goto(MS_FORMS_URL, { waitUntil: 'networkidle2', timeout: 15000 });
            await page.waitForTimeout(3000);
            
            const pageContent = await page.content();
            const hasForm = pageContent.includes('form') || pageContent.includes('input');
            const hasField = pageContent.includes(MS_FORMS_FIELD_ID);
            
            res.json({
                success: true,
                message: 'MS Forms is accessible via browser',
                hasForm: hasForm,
                hasField: hasField,
                contentLength: pageContent.length
            });

        } finally {
            if (browser) await browser.close();
        }

    } catch (error) {
        console.error('🧪 Test error:', error);
        
        res.status(500).json({
            success: false,
            error: error.message,
            message: 'MS Forms test failed'
        });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Browser automation server running on port ${PORT}`);
    console.log(`📝 Microsoft Forms URL: ${MS_FORMS_URL}`);
    console.log(`🔑 Field ID: ${MS_FORMS_FIELD_ID}`);
    console.log(`🌐 Website: http://localhost:${PORT}`);
    console.log(`🔧 Health check: http://localhost:${PORT}/api/health`);
    console.log(`🧪 Test MS Forms: http://localhost:${PORT}/api/test-ms-forms`);
});
