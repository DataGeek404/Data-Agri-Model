// Web Integration Script for Agricultural AI Model
// This script integrates the trained TensorFlow.js model into your web application

class AgriculturalAI {
    constructor() {
        this.model = null;
        this.cropEncoder = null;
        this.diseaseEncoder = null;
        this.isLoaded = false;
        this.loadingProgress = 0;
    }

    async loadModel(modelPath = '/web_model/model.json') {
        try {
            console.log('🔄 Loading Agricultural AI model...');
            this.loadingProgress = 10;

            // Load the TensorFlow.js model
            this.model = await tf.loadLayersModel(modelPath);
            this.loadingProgress = 60;

            // Load encoders
            await this.loadEncoders();
            this.loadingProgress = 90;

            // Warm up the model
            await this.warmUpModel();
            this.loadingProgress = 100;

            this.isLoaded = true;
            console.log('✅ Agricultural AI model loaded successfully!');
            
        } catch (error) {
            console.error('❌ Error loading model:', error);
            throw new Error('Failed to load Agricultural AI model');
        }
    }

    async loadEncoders() {
        // In a real implementation, you would load these from your server
        // For now, we'll use the mappings from our training
        this.cropEncoder = [
            'Cotton', 'Maize/Corn', 'Potato', 'Rice', 
            'Soybean', 'Sugarcane', 'Tomato', 'Wheat'
        ];

        this.diseaseEncoder = [
            'Bacterial Leaf Blight', 'Brown Spot', 'Common Rust',
            'Early Blight', 'Gray Leaf Spot', 'Healthy',
            'Late Blight', 'Leaf Mold', 'Leaf Rust',
            'Leaf Smut', 'Northern Leaf Blight', 'Powdery Mildew',
            'Rice Blast', 'Septoria Leaf Blotch', 'Septoria Leaf Spot',
            'Southern Rust', 'Stripe Rust'
        ];
    }

    async warmUpModel() {
        // Create a dummy input to warm up the model
        const dummyInput = tf.zeros([1, 224, 224, 3]);
        await this.model.predict(dummyInput);
        dummyInput.dispose();
    }

    preprocessImage(imageElement) {
        return tf.tidy(() => {
            // Convert image to tensor
            let tensor = tf.browser.fromPixels(imageElement);
            
            // Resize to model input size
            tensor = tf.image.resizeBilinear(tensor, [224, 224]);
            
            // Normalize pixel values to [0, 1]
            tensor = tensor.div(255.0);
            
            // Add batch dimension
            tensor = tensor.expandDims(0);
            
            return tensor;
        });
    }

    async analyzeImage(imageElement) {
        if (!this.isLoaded) {
            throw new Error('Model not loaded. Call loadModel() first.');
        }

        try {
            // Preprocess image
            const preprocessedImage = this.preprocessImage(imageElement);
            
            // Make prediction
            const predictions = await this.model.predict(preprocessedImage);
            
            // Extract predictions for each task
            const cropPrediction = predictions[0];
            const diseasePrediction = predictions[1];
            const yieldPrediction = predictions[2];
            
            // Get prediction data
            const cropProbs = await cropPrediction.data();
            const diseaseProbs = await diseasePrediction.data();
            const yieldValue = await yieldPrediction.data();
            
            // Find top predictions
            const cropIndex = cropProbs.indexOf(Math.max(...cropProbs));
            const diseaseIndex = diseaseProbs.indexOf(Math.max(...diseaseProbs));
            
            // Create analysis result
            const analysis = {
                cropType: this.cropEncoder[cropIndex],
                cropConfidence: Math.round(cropProbs[cropIndex] * 100),
                disease: this.diseaseEncoder[diseaseIndex],
                diseaseConfidence: Math.round(diseaseProbs[diseaseIndex] * 100),
                yieldEstimate: Math.round(yieldValue[0] * 100) / 100,
                yieldUnit: 'tons/acre',
                severity: this.calculateSeverity(this.diseaseEncoder[diseaseIndex], diseaseProbs[diseaseIndex]),
                recommendation: this.generateRecommendation(
                    this.cropEncoder[cropIndex],
                    this.diseaseEncoder[diseaseIndex],
                    diseaseProbs[diseaseIndex]
                ),
                timestamp: new Date().toISOString()
            };
            
            // Clean up tensors
            preprocessedImage.dispose();
            cropPrediction.dispose();
            diseasePrediction.dispose();
            yieldPrediction.dispose();
            
            return analysis;
            
        } catch (error) {
            console.error('Error analyzing image:', error);
            throw new Error('Failed to analyze image');
        }
    }

    calculateSeverity(disease, confidence) {
        if (disease === 'Healthy') return 'none';
        
        if (confidence > 0.85) return 'high';
        if (confidence > 0.70) return 'medium';
        return 'low';
    }

    generateRecommendation(crop, disease, confidence) {
        if (disease === 'Healthy') {
            return `Excellent! Your ${crop} crop shows no signs of disease. Continue with regular monitoring and maintain proper irrigation. Expected yield looks promising.`;
        }

        const treatmentMap = {
            'Northern Leaf Blight': 'Apply fungicide containing Mancozeb (2-3 lbs/acre) within 48 hours. Ensure good air circulation and avoid overhead irrigation.',
            'Common Rust': 'Use systemic fungicides with Propiconazole. Apply early morning or late evening. Remove infected debris.',
            'Leaf Rust': 'Apply Propiconazole-based fungicide immediately. Consider rust-resistant varieties for next season.',
            'Bacterial Leaf Blight': 'Use copper-based bactericides. Improve field drainage and avoid overhead watering.',
            'Early Blight': 'Apply Chlorothalonil or Mancozeb every 7-14 days. Remove affected lower leaves.',
            'Late Blight': 'URGENT: Apply systemic fungicide immediately. This disease spreads rapidly in humid conditions.'
        };

        const treatment = treatmentMap[disease] || 'Consult with local agricultural extension officer for specific treatment recommendations.';
        
        const urgency = confidence > 0.85 ? 'CRITICAL ACTION REQUIRED: ' : 
                        confidence > 0.70 ? 'IMPORTANT: ' : 'MONITOR CLOSELY: ';
        
        return `${urgency}${treatment}`;
    }

    getLoadingProgress() {
        return this.loadingProgress;
    }

    isModelLoaded() {
        return this.isLoaded;
    }
}

// Export for use in your application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgriculturalAI;
} else if (typeof window !== 'undefined') {
    window.AgriculturalAI = AgriculturalAI;
}

// Usage example:
/*
const aiModel = new AgriculturalAI();

// Load the model
await aiModel.loadModel('/path/to/web_model/model.json');

// Analyze an image
const imageElement = document.getElementById('crop-image');
const analysis = await aiModel.analyzeImage(imageElement);

console.log('Analysis result:', analysis);
*/