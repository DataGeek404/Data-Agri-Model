# 🚀 Roboflow Setup - Complete Guide

## 📍 You're Here: https://universe.roboflow.com/lucky48121/leaf_disease_detection-yh7jo

## Step 1: Get Your API Key

### Option A: From the Model Page
1. **Look for "Use via API"** button on the model page
2. **Click it** - you'll see code examples
3. **Copy the API key** from the code example

### Option B: From Your Account Settings
1. **Click your profile picture** (top right)
2. Go to **"Settings"** → **"API"**
3. **Copy your Private API Key** (starts with `rf_`)

## Step 2: Update the Code

Replace this line in `src/services/aiModel.ts`:

```typescript
apiKey: 'YOUR_ROBOFLOW_API_KEY',
```

With your actual key:

```typescript
apiKey: 'rf_abc123def456ghi789...',  // Your actual key here
```

## Step 3: Test It!

```bash
npm run dev
```

Upload any plant/crop image and see **REAL AI analysis**!

## 🎯 What You'll Get

- **Real disease detection** from the Roboflow model
- **Confidence scores** for each prediction
- **Treatment recommendations** based on detected diseases
- **Yield estimates** adjusted for disease severity

## 🔧 Troubleshooting

### If you get "401 Unauthorized":
- Double-check your API key
- Make sure you copied the full key (starts with `rf_`)

### If you get "404 Not Found":
- The model endpoint might be different
- Try updating the endpoint in the code

### If you get "Rate Limited":
- You've hit the free tier limit
- Wait or upgrade your Roboflow plan

## 🚀 Ready for Production!

Once you have your API key working:

1. **Deploy to Render/Vercel/Netlify**
2. **Set environment variable**: `VITE_ROBOFLOW_API_KEY`
3. **Your app is live with real AI!**

## 📊 Free Tier Limits

- **1,000 API calls per month**
- **Perfect for testing and small deployments**
- **Upgrade for production use**

---

**You're 2 minutes away from real AI crop analysis!** 🌾