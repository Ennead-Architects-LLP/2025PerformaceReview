# Backend Proxy Setup Guide

This backend proxy server solves the CORS issue by acting as a middleman between your website and Microsoft Forms.

## How It Works

1. **Your Website** → Sends data to **Backend Server**
2. **Backend Server** → Submits to **Microsoft Forms**
3. **Backend Server** → Returns success/failure to **Your Website**

This bypasses CORS restrictions because the backend server can make requests to Microsoft Forms without browser security limitations.

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Server
```bash
npm start
```

### 3. Test the Setup
- Open: http://localhost:3000
- Health check: http://localhost:3000/api/health
- Test MS Forms: http://localhost:3000/api/test-ms-forms

## Deployment Options

### Option 1: Heroku (Recommended)
```bash
# Install Heroku CLI
npm install -g heroku

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Deploy
git add .
git commit -m "Add backend proxy"
git push heroku main

# Set environment variables
heroku config:set NODE_ENV=production
```

### Option 2: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway init
railway up
```

### Option 3: Render
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `npm install`
4. Set start command: `npm start`

### Option 4: Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

## Update Frontend Configuration

After deploying, update the backend URL in `script.js`:

```javascript
const backendUrl = isLocalhost 
    ? 'http://localhost:3000/api/submit-to-ms-forms'
    : 'https://your-deployed-backend.com/api/submit-to-ms-forms';
```

## Environment Variables

Create a `.env` file for local development:

```env
PORT=3000
NODE_ENV=development
MS_FORMS_URL=https://forms.office.com/Pages/ResponsePage.aspx?id=YOUR_FORM_ID
MS_FORMS_FIELD_ID=entry.YOUR_FIELD_ID
```

## Testing

### 1. Test Backend Health
```bash
curl http://localhost:3000/api/health
```

### 2. Test Microsoft Forms Access
```bash
curl http://localhost:3000/api/test-ms-forms
```

### 3. Test Form Submission
```bash
curl -X POST http://localhost:3000/api/submit-to-ms-forms \
  -H "Content-Type: application/json" \
  -d '{"employeeName":"John Doe"}'
```

## Troubleshooting

### Common Issues:

1. **CORS Error**: Make sure your domain is in the CORS whitelist
2. **MS Forms Not Accessible**: Check if the form URL is correct
3. **Port Already in Use**: Change PORT in .env file
4. **Dependencies Missing**: Run `npm install`

### Debug Mode:
The server logs all requests and responses. Check the console for detailed information.

## Security Considerations

1. **Rate Limiting**: Consider adding rate limiting for production
2. **Input Validation**: The server validates input but consider additional validation
3. **HTTPS**: Always use HTTPS in production
4. **Environment Variables**: Keep sensitive data in environment variables

## Monitoring

The server includes health check endpoints:
- `/api/health` - Basic health status
- `/api/test-ms-forms` - Test Microsoft Forms connectivity

## Support

If you encounter issues:
1. Check the server logs
2. Verify Microsoft Forms URL and field ID
3. Test the endpoints manually
4. Check CORS configuration
