#!/usr/bin/env python3
"""
Agricultural AI Model Training Script
Trains a multi-task model for crop disease detection and yield estimation
"""

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import json

class AgriculturalAITrainer:
    def __init__(self, config_path='config.json'):
        """Initialize trainer with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.img_height = self.config['input_size'][0]
        self.img_width = self.config['input_size'][1]
        self.batch_size = self.config['batch_size']
        
        # Initialize label encoders
        self.crop_encoder = LabelEncoder()
        self.disease_encoder = LabelEncoder()
        
    def load_data(self, data_path):
        """Load and preprocess training data"""
        print("Loading training data...")
        
        # Load metadata
        df = pd.read_csv(data_path)
        
        # Encode labels
        df['crop_encoded'] = self.crop_encoder.fit_transform(df['crop_type'])
        df['disease_encoded'] = self.disease_encoder.fit_transform(df['disease'])
        
        # Convert severity to numeric
        severity_map = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        df['severity_numeric'] = df['severity'].map(severity_map)
        
        return df
    
    def create_data_generator(self, df, subset='training'):
        """Create data generator for training"""
        datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255,
            rotation_range=self.config['augmentation']['rotation'],
            zoom_range=self.config['augmentation']['zoom'],
            horizontal_flip=self.config['augmentation']['horizontalFlip'],
            brightness_range=[1-self.config['augmentation']['brightness'], 
                            1+self.config['augmentation']['brightness']],
            validation_split=0.2
        )
        
        # Create generator that returns multiple outputs
        generator = datagen.flow_from_dataframe(
            df,
            x_col='image_path',
            y_col=['crop_encoded', 'disease_encoded', 'yield_estimate'],
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='multi_output',
            subset=subset
        )
        
        return generator
    
    def build_model(self):
        """Build multi-task agricultural AI model"""
        print("Building model architecture...")
        
        # Base model
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(self.img_height, self.img_width, 3)
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Add custom layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.3)(x)
        
        # Multi-task outputs
        crop_output = Dense(
            len(self.crop_encoder.classes_),
            activation='softmax',
            name='crop_classification'
        )(x)
        
        disease_output = Dense(
            len(self.disease_encoder.classes_),
            activation='softmax',
            name='disease_classification'
        )(x)
        
        yield_output = Dense(
            1,
            activation='linear',
            name='yield_regression'
        )(x)
        
        # Create model
        model = Model(
            inputs=base_model.input,
            outputs=[crop_output, disease_output, yield_output]
        )
        
        return model
    
    def compile_model(self, model):
        """Compile model with appropriate losses and metrics"""
        model.compile(
            optimizer=Adam(learning_rate=self.config['learningRate']),
            loss={
                'crop_classification': 'sparse_categorical_crossentropy',
                'disease_classification': 'sparse_categorical_crossentropy',
                'yield_regression': 'mse'
            },
            loss_weights={
                'crop_classification': 1.0,
                'disease_classification': 2.0,  # Higher weight for disease detection
                'yield_regression': 0.5
            },
            metrics={
                'crop_classification': ['accuracy'],
                'disease_classification': ['accuracy', 'precision', 'recall'],
                'yield_regression': ['mae', 'mse']
            }
        )
        
        return model
    
    def train(self, data_path, output_dir='models/'):
        """Train the agricultural AI model"""
        # Load data
        df = self.load_data(data_path)
        
        # Create data generators
        train_generator = self.create_data_generator(df, 'training')
        val_generator = self.create_data_generator(df, 'validation')
        
        # Build and compile model
        model = self.build_model()
        model = self.compile_model(model)
        
        print(f"Model summary:")
        model.summary()
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=1e-7
            ),
            ModelCheckpoint(
                filepath=os.path.join(output_dir, 'best_model.h5'),
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Train model
        print("Starting training...")
        history = model.fit(
            train_generator,
            epochs=self.config['epochs'],
            validation_data=val_generator,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        model.save(os.path.join(output_dir, 'agricultural_ai_model.h5'))
        
        # Save encoders
        np.save(os.path.join(output_dir, 'crop_encoder.npy'), self.crop_encoder.classes_)
        np.save(os.path.join(output_dir, 'disease_encoder.npy'), self.disease_encoder.classes_)
        
        print("Training completed!")
        return model, history
    
    def convert_to_web(self, model_path, output_dir='web_model/'):
        """Convert trained model to TensorFlow.js format"""
        print("Converting model for web deployment...")
        
        import tensorflowjs as tfjs
        
        # Load model
        model = tf.keras.models.load_model(model_path)
        
        # Convert to TensorFlow.js
        tfjs.converters.save_keras_model(model, output_dir)
        
        print(f"Web model saved to {output_dir}")

if __name__ == "__main__":
    # Example usage
    trainer = AgriculturalAITrainer()
    
    # Train model
    model, history = trainer.train('data/training_data.csv')
    
    # Convert for web deployment
    trainer.convert_to_web('models/agricultural_ai_model.h5')