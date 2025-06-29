import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Features from './components/Features';
import ImageUpload from './components/ImageUpload';
import LoadingSpinner from './components/LoadingSpinner';
import AnalysisResults from './components/AnalysisResults';
import { aiModel } from './services/aiModel';
import { CropAnalysis } from './types';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

function App() {
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<CropAnalysis | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadModels = async () => {
      try {
        setIsLoadingModels(true);
        await aiModel.loadModels();
        setIsModelLoaded(true);
        setError('');
      } catch (err) {
        setError('Failed to load AI models. Please refresh the page and try again.');
        console.error('Model loading error:', err);
      } finally {
        setIsLoadingModels(false);
      }
    };

    loadModels();
  }, []);

  const handleImageSelect = async (file: File) => {
    if (!isModelLoaded) {
      setError('AI models are still loading. Please wait a moment.');
      return;
    }

    setError('');
    setAnalysis(null);
    setIsAnalyzing(true);

    try {
      // Create image URL for display
      const url = URL.createObjectURL(file);
      setImageUrl(url);

      // Create image element for analysis
      const img = new Image();
      img.onload = async () => {
        try {
          const result = await aiModel.analyzeImage(img);
          setAnalysis(result);
        } catch (err) {
          setError('Failed to analyze image. Please try again with a clear crop image.');
          console.error('Analysis error:', err);
        } finally {
          setIsAnalyzing(false);
        }
      };
      img.onerror = () => {
        setError('Failed to load image. Please try a different image format (JPEG, PNG).');
        setIsAnalyzing(false);
      };
      img.src = url;
    } catch (err) {
      setError('Failed to process image. Please try again.');
      setIsAnalyzing(false);
      console.error('Image processing error:', err);
    }
  };

  const resetAnalysis = () => {
    setAnalysis(null);
    setImageUrl('');
    setError('');
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        {/* Model Loading Status */}
        {isLoadingModels && (
          <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <Loader2 className="animate-spin text-blue-600" size={24} />
              <span className="text-blue-800 font-medium text-lg">Initializing AI Models</span>
            </div>
            <p className="text-blue-600 mb-3">
              Loading computer vision models for crop analysis...
            </p>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${aiModel.getLoadingProgress()}%` }}
              />
            </div>
            <p className="text-sm text-blue-500 mt-2">
              This may take a few moments on first load.
            </p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle size={20} className="text-red-600" />
              <span className="text-red-800 font-medium">Error</span>
            </div>
            <p className="text-sm text-red-600 mt-1">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-sm text-red-700 underline hover:text-red-800"
            >
              Refresh Page
            </button>
          </div>
        )}

        {/* Success Status */}
        {isModelLoaded && !error && !analysis && !isLoadingModels && (
          <div className="mb-8 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle size={20} className="text-green-600" />
              <span className="text-green-800 font-medium">AI Models Ready</span>
            </div>
            <p className="text-sm text-green-600 mt-1">
              Upload a crop image to begin AI-powered analysis.
            </p>
          </div>
        )}

        {/* Main Content */}
        <div className="space-y-8">
          {!analysis && !isAnalyzing && !isLoadingModels && (
            <>
              <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-gray-900">
                  AI-Powered Crop Analysis
                </h1>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  Upload drone or field images to detect crop diseases, estimate yields, 
                  and receive expert recommendations powered by advanced computer vision.
                </p>
              </div>

              <ImageUpload 
                onImageSelect={handleImageSelect}
                isAnalyzing={isAnalyzing}
              />
            </>
          )}

          {isAnalyzing && (
            <LoadingSpinner message="Analyzing your crop image with AI..." />
          )}

          {analysis && imageUrl && (
            <div className="space-y-6">
              <AnalysisResults analysis={analysis} imageUrl={imageUrl} />
              <div className="text-center">
                <button
                  onClick={resetAnalysis}
                  className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-medium transition-colors duration-200"
                >
                  Analyze Another Image
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Features Section */}
      {!analysis && !isLoadingModels && <Features />}

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">AgriVision AI</h3>
              <p className="text-gray-300 text-sm">
                Empowering smallholder farmers with AI-powered crop monitoring 
                and disease detection technology.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Supported Crops</h3>
              <ul className="text-gray-300 text-sm space-y-1">
                <li>• Maize/Corn</li>
                <li>• Wheat</li>
                <li>• Rice</li>
                <li>• Tomatoes</li>
                <li>• Cotton</li>
                <li>• Soybeans</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <p className="text-gray-300 text-sm">
                For agricultural extension officers and farming cooperatives 
                interested in deploying this technology.
              </p>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              © 2024 AgriVision AI. Built for smallholder farmers worldwide.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;