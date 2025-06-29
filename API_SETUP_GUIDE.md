# 🚀 Easy API Setup Guide

## 🎯 **Option 1: Roboflow (Easiest)**

### Step 1: Sign Up (2 minutes)
1. Go to **[roboflow.com](https://roboflow.com)**
2. Click **"Sign Up"** (free account)
3. Verify your email

### Step 2: Get API Key (1 minute)
1. Go to **"Settings"** → **"API"**
2. Copy your **Private API Key**
3. It looks like: `rf_abc123def456...`

### Step 3: Find a Model (2 minutes)
1. Go to **"Universe"** tab
2. Search **"crop disease detection"**
3. Pick any model (e.g., "Plant Disease Detection")
4. Click **"Use via API"**
5. Copy the **endpoint URL**

### Step 4: Update Code (30 seconds)
In `src/services/aiModel.ts`, replace:
```typescript
roboflow: {
  key: 'YOUR_ROBOFLOW_KEY', // Replace with your key
  endpoint: 'https://detect.roboflow.com/crop-disease-detection/1', // Replace with your endpoint
  active: true
}
```

---

## 🌱 **Option 2: Plant.id (Good Accuracy)**

### Step 1: Get API Key
1. Go to **[web.plant.id](https://web.plant.id/)**
2. Click **"API"** → **"Get Started"**
3. Sign up and get your API key

### Step 2: Update Code
```typescript
plantid: {
  key: 'YOUR_PLANT_ID_KEY', // Your actual key
  endpoint: 'https://api.plant.id/v3/identification',
  active: true
}
```

---

## 🔧 **Option 3: Demo Mode (Always Works)**

No setup needed! The app works with realistic demo data if no API keys are provided.

---

## ✅ **Quick Test**

1. Update your API key in the code
2. Run `npm run dev`
3. Upload any plant/crop image
4. See real AI analysis!

---

## 🚀 **Deploy to Production**

### Render
1. Push to GitHub
2. Connect to Render
3. Set environment variable: `VITE_ROBOFLOW_KEY=your-key`

### Vercel
```bash
npm run build
vercel --prod
```

---

## 📊 **API Comparison**

| Service | Setup Time | Accuracy | Free Tier |
|---------|------------|----------|-----------|
| **Roboflow** | 5 minutes | 90%+ | 1000 requests/month |
| **Plant.id** | 3 minutes | 95%+ | 100 requests/month |
| **Demo Mode** | 0 minutes | Realistic | Unlimited |

---

## 🎯 **Recommended: Start with Roboflow**

1. Easiest setup
2. Great free tier
3. Many pre-trained models
4. Excellent documentation

**You'll have real AI working in under 10 minutes!** 🚀