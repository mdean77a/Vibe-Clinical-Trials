# Vercel Deployment Guide - Kinde Authentication

This guide covers deploying the Clinical Trial Accelerator with Kinde authentication to Vercel.

## Prerequisites

- Vercel account connected to your GitHub repository
- Kinde account with application configured
- Access to Vercel environment variables

---

## 1. Vercel Environment Variables

Add these environment variables in your Vercel project dashboard:
**Settings → Environment Variables**

### Required Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `KINDE_CLIENT_ID` | `your_client_id` | From Kinde dashboard → Applications → Your App |
| `KINDE_CLIENT_SECRET` | `your_client_secret` | From Kinde dashboard → Applications → Your App |
| `KINDE_ISSUER_URL` | `https://yourdomain.kinde.com` | Your Kinde domain |
| `KINDE_SITE_URL` | `https://your-app.vercel.app` | Your Vercel deployment URL |
| `KINDE_POST_LOGOUT_REDIRECT_URL` | `https://your-app.vercel.app` | Where to redirect after logout |
| `KINDE_POST_LOGIN_REDIRECT_URL` | `https://your-app.vercel.app/` | Where to redirect after login |

### Important Notes

- Set these for **Production**, **Preview**, and **Development** environments
- Replace `your-app.vercel.app` with your actual Vercel URL
- Replace `yourdomain` with your actual Kinde domain name
- Keep `KINDE_CLIENT_SECRET` secure - never commit it to Git

---

## 2. Kinde Dashboard Configuration

Update your Kinde application settings:

### Allowed Callback URLs
Add your Vercel deployment URLs:
```
https://your-app.vercel.app/api/auth/kinde_callback
https://your-app-git-*.vercel.app/api/auth/kinde_callback (for preview deployments)
http://localhost:3000/api/auth/kinde_callback (for local development)
```

### Allowed Logout Redirect URLs
```
https://your-app.vercel.app
https://your-app-git-*.vercel.app (for preview deployments)
http://localhost:3000 (for local development)
```

### Where to Find This
1. Log in to [Kinde dashboard](https://app.kinde.com)
2. Go to **Applications** → Select your app
3. Scroll to **Callback URLs** section
4. Add the URLs listed above

---

## 3. Vercel Routing Configuration

The `vercel.json` file has been configured to handle the routing conflict between:
- Next.js Kinde auth routes (`/api/auth/*`)
- Python FastAPI backend routes (`/api/*`)

### Route Order (Critical!)
```json
{
  "routes": [
    {
      "src": "/api/auth/(.*)",          // ✅ Auth routes to Next.js (FIRST)
      "dest": "frontend/api/auth/$1"
    },
    {
      "src": "/api/(.*)",               // ✅ Other API routes to Python
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",                   // ✅ Everything else to Next.js
      "dest": "frontend/$1"
    }
  ]
}
```

**Why This Order Matters:**
- Routes are processed top-to-bottom
- `/api/auth/*` must be caught BEFORE `/api/*`
- Otherwise, auth routes get sent to Python backend (404 error)

---

## 4. Deployment Steps

### Initial Deployment
1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click **New Project**
4. Import your repository
5. Configure environment variables (see section 1)
6. Click **Deploy**

### Update Kinde After First Deploy
1. Note your Vercel URL (e.g., `https://your-app.vercel.app`)
2. Update Kinde callback URLs with actual Vercel URL
3. Update Vercel environment variables with actual URL
4. Redeploy in Vercel (Settings → Deployments → Redeploy)

---

## 5. Testing Checklist

After deployment, verify:

- [ ] Visit your Vercel app URL
- [ ] Should immediately redirect to Kinde login page
- [ ] Login with valid credentials
- [ ] Should redirect back to app homepage
- [ ] Can see protocol selection interface
- [ ] Can access protected routes (document-selection, informed-consent, site-checklist)
- [ ] Backend API calls work (protocol list loads)
- [ ] Logout button works
- [ ] After logout, redirected back to login

---

## 6. Troubleshooting

### Auth Routes Return 404
**Problem:** Login/logout buttons don't work
**Solution:** 
- Verify `vercel.json` has `/api/auth/*` route BEFORE `/api/*`
- Check Vercel build logs for errors
- Ensure environment variables are set

### Infinite Redirect Loop
**Problem:** App keeps redirecting to login
**Solution:**
- Check `KINDE_SITE_URL` matches your actual Vercel URL
- Verify callback URLs in Kinde match Vercel URL
- Check middleware.ts is not blocking auth routes

### Backend API Calls Fail
**Problem:** Can't load protocols or generate documents
**Solution:**
- Check Python backend logs in Vercel
- Verify `/api/*` routes (except `/api/auth/*`) go to Python
- Test backend endpoints directly

### Environment Variables Not Working
**Problem:** Auth fails with "missing configuration"
**Solution:**
- Verify all 6 required variables are set in Vercel
- Check for typos in variable names
- Ensure variables are set for correct environment (Production/Preview)
- Redeploy after adding variables

---

## 7. Local Development

Your local `.env.local` should have:
```bash
KINDE_CLIENT_ID=your_client_id
KINDE_CLIENT_SECRET=your_client_secret
KINDE_ISSUER_URL=https://yourdomain.kinde.com
KINDE_SITE_URL=http://localhost:3000
KINDE_POST_LOGOUT_REDIRECT_URL=http://localhost:3000
KINDE_POST_LOGIN_REDIRECT_URL=http://localhost:3000
```

**Note:** Use `http://localhost:3000` for local, `https://your-app.vercel.app` for production.

---

## 8. Preview Deployments

Vercel creates preview deployments for each pull request with URLs like:
`https://your-app-git-branch-name-username.vercel.app`

To support these:
1. Use wildcard in Kinde callback URLs: `https://your-app-git-*.vercel.app/api/auth/kinde_callback`
2. Set environment variables for "Preview" environment in Vercel
3. Each preview will work independently

---

## Summary

✅ **What We Fixed:**
- Added `/api/auth/*` routing before `/api/*` in vercel.json
- Prevents auth routes from being sent to Python backend
- Allows Kinde authentication to work on Vercel

✅ **What You Need To Do:**
1. Set 6 environment variables in Vercel dashboard
2. Update Kinde callback URLs with your Vercel URL
3. Redeploy and test

🎉 **Result:**
- Authentication works on Vercel
- Local development still works
- Backend API calls still work
- All routes are properly protected
