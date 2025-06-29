# 🌱 Plant.id API Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Plant.id API Key
1. **Go to**: [web.plant.id](https://web.plant.id/)
2. **Click**: "API" → "Get Started"
3. **Sign up**: Free account (100 identifications/month)
4. **Copy**: Your API key from the dashboard

### Step 2: Update the Code
In `src/services/aiModel.ts`, replace:
```typescript
key: 'YOUR_PLANT_ID_API_KEY',
```

With your actual key:
```typescript
key: 'your-actual-plant-id-key-here',
```

### Step 3: Test It!
```bash
npm run dev
```
Upload a crop image and see **real Plant.id AI analysis**!

## 🎯 What Plant.id Provides

- **Plant Identification**: 95%+ accuracy
- **Disease Detection**: Health assessment with confidence scores
- **Treatment Suggestions**: Based on detected issues
- **Similar Images**: Visual references for comparison

## 📊 API Features

### Health Assessment
- Disease detection
- Pest identification
- Nutrient deficiency analysis
- Overall plant health score

### Plant Details
- Scientific names
- Common names
- Detailed descriptions
- Care instructions

## 🔧 API Configuration

The system is configured to use Plant.id as the **primary API** with Roboflow as backup:

```typescript
Priority 1: Plant.id (plant disease identification)
Priority 2: Roboflow (crop-specific models)
Priority 3: Demo mode (always works)
```

## 💰 Pricing

| Plan | Requests/Month | Price | Best For |
|------|----------------|-------|----------|
| **Free** | 100 | $0 | Testing |
| **Basic** | 1,000 | $9/month | Small farms |
| **Pro** | 10,000 | $49/month | Commercial |

## 🌐 Deploy to Production

### Environment Variables
```env
VITE_PLANT_ID_API_KEY=your-plant-id-key
VITE_ROBOFLOW_API_KEY=your-roboflow-key
```

### Render Deployment
1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy!

## ✅ Benefits of Multi-API System

1. **Higher Accuracy**: Best of both APIs
2. **Redundancy**: If one fails, other works
3. **Specialized Models**: Plant.id for diseases, Roboflow for crops
4. **Always Available**: Demo mode as final fallback

## 🎯 Ready for Production!

Your agricultural AI now uses **three powerful systems**:
- **Plant.id**: Professional plant disease identification
- **Roboflow**: Custom crop disease models  
- **Demo Mode**: Always-working fallback

**Real AI analysis in under 10 minutes!** 🚀