# 🚀 Deployment Guide

This application can be deployed to multiple platforms automatically. Choose the option that best fits your needs:

## 📋 **Quick Deploy Options**

### **Option 1: Vercel (Recommended - Easiest)**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Follow the prompts** - Vercel will automatically detect your configuration and deploy.

**✅ Pros:** 
- Zero configuration needed
- Automatic HTTPS
- Global CDN
- Serverless functions included
- Free tier available

### **Option 2: Netlify**

1. **Connect your GitHub repository** to Netlify
2. **Build settings:**
   - Build command: `npm install`
   - Publish directory: `.`
3. **Deploy!**

**✅ Pros:**
- Easy GitHub integration
- Free tier available
- Good for static sites

### **Option 3: GitHub Pages + External Backend**

1. **Enable GitHub Pages** in your repository settings
2. **Deploy backend separately** (Vercel/Netlify)
3. **Update the backend URL** in `script.js`

## 🔧 **Manual Deployment Steps**

### **For GitHub Pages:**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` (will be created automatically)

3. **Your site will be available at:**
   `https://yourusername.github.io/2025PerformaceReview`

### **For Vercel:**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login and deploy:**
   ```bash
   vercel login
   vercel --prod
   ```

3. **Your site will be available at:**
   `https://your-project.vercel.app`

## 🌐 **Environment Configuration**

### **Backend URL Configuration**

The application automatically detects the environment and uses the appropriate backend URL:

- **Localhost:** `http://localhost:3000/api/submit-to-ms-forms`
- **Vercel:** `/api/submit-to-ms-forms`
- **Netlify:** `/.netlify/functions/server/api/submit-to-ms-forms`
- **GitHub Pages:** External API (you'll need to deploy backend separately)

### **MS Forms Configuration**

Update these values in `server.js` if needed:

```javascript
const MS_FORMS_URL = 'your-ms-forms-url';
const MS_FORMS_FIELD_ID = 'your-field-id';
```

## 🔒 **Security Considerations**

### **CORS Configuration**

The server is configured to allow requests from:
- `https://ennead-architects-llp.github.io`
- `http://localhost:3000`

Update the CORS settings in `server.js` for your domain:

```javascript
app.use(cors({
    origin: ['https://your-domain.com', 'http://localhost:3000'],
    credentials: false
}));
```

### **Environment Variables**

For production, consider using environment variables:

```javascript
const PORT = process.env.PORT || 3000;
const MS_FORMS_URL = process.env.MS_FORMS_URL || 'default-url';
```

## 📊 **Monitoring & Debugging**

### **Health Check Endpoint**

All deployments include a health check endpoint:
- **Local:** `http://localhost:3000/api/health`
- **Vercel:** `https://your-app.vercel.app/api/health`
- **Netlify:** `https://your-app.netlify.app/.netlify/functions/server/api/health`

### **Debug Panel**

In development mode, a debug panel shows:
- Form submission attempts
- Error messages
- Response details

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **CORS Errors:**
   - Update CORS origins in `server.js`
   - Ensure backend URL is correct

2. **MS Forms Not Working:**
   - Check field ID is correct
   - Verify MS Forms URL is accessible
   - Test with the diagnostic endpoints

3. **Deployment Fails:**
   - Check `package.json` has all dependencies
   - Verify Node.js version compatibility
   - Check platform-specific requirements

### **Testing Deployment:**

1. **Test the health endpoint:**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

2. **Test form submission:**
   ```bash
   curl -X POST https://your-app.vercel.app/api/submit-to-ms-forms \
     -H "Content-Type: application/json" \
     -d '{"employeeName": "test"}'
   ```

## 📈 **Performance Optimization**

### **For Production:**

1. **Enable compression:**
   ```javascript
   app.use(compression());
   ```

2. **Add caching headers:**
   ```javascript
   app.use(express.static('.', {
     maxAge: '1h'
   }));
   ```

3. **Rate limiting:**
   ```javascript
   const rateLimit = require('express-rate-limit');
   app.use('/api/', rateLimit({
     windowMs: 15 * 60 * 1000, // 15 minutes
     max: 100 // limit each IP to 100 requests per windowMs
   }));
   ```

## 🎯 **Next Steps**

After deployment:

1. **Test the application** thoroughly
2. **Monitor logs** for any errors
3. **Update documentation** with your live URL
4. **Set up monitoring** (optional)
5. **Configure custom domain** (optional)

---

**Need help?** Check the troubleshooting section or create an issue in the repository.
