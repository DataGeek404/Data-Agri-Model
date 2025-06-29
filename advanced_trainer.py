#!/usr/bin/env python3
"""
Advanced Agricultural AI Model Trainer
Optimized for the three Kaggle datasets with state-of-the-art techniques
"""

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetV2B0, ResNet50V2
from tensorflow.keras.layers import (
    Dense, GlobalAveragePooling2D, Dropout, BatchNormalization,
    Conv2D, MaxPooling2D, Flatten, Concatenate, Input
)
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam, AdamW
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint,
    TensorBoard, CSVLogger
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from datetime import datetime
import albumentations as A
import cv2

class AdvancedAgriculturalTrainer:
    def __init__(self, config_path='training/config.json'):
        """Initialize advanced trainer"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.img_height = self.config['inputSize'][0]
        self.img_width = self.config['inputSize'][1]
        self.batch_size = self.config['batchSize']
        
        # Initialize encoders
        self.crop_encoder = LabelEncoder()
        self.disease_encoder = LabelEncoder()
        
        # Create output directory
        self.output_dir = f"models/agricultural_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"🎯 Model output directory: {self.output_dir}")
    
    def load_processed_data(self, data_dir='processed_data/'):
        """Load processed training data"""
        print("📊 Loading processed data...")
        
        train_df = pd.read_csv(f"{data_dir}/train.csv")
        val_df = pd.read_csv(f"{data_dir}/validation.csv")
        test_df = pd.read_csv(f"{data_dir}/test.csv")
        
        # Encode labels
        all_crops = pd.concat([train_df['crop_type'], val_df['crop_type'], test_df['crop_type']])
        all_diseases = pd.concat([train_df['disease'], val_df['disease'], test_df['disease']])
        
        self.crop_encoder.fit(all_crops)
        self.disease_encoder.fit(all_diseases)
        
        # Apply encoding
        for df in [train_df, val_df, test_df]:
            df['crop_encoded'] = self.crop_encoder.transform(df['crop_type'])
            df['disease_encoded'] = self.disease_encoder.transform(df['disease'])
        
        print(f"✅ Data loaded:")
        print(f"  Crop types: {len(self.crop_encoder.classes_)}")
        print(f"  Disease types: {len(self.disease_encoder.classes_)}")
        
        return train_df, val_df, test_df
    
    def create_advanced_augmentation(self):
        """Create advanced augmentation pipeline using Albumentations"""
        return A.Compose([
            A.RandomRotate90(p=0.5),
            A.Flip(p=0.5),
            A.Transpose(p=0.5),
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
                A.GaussianBlur(blur_limit=3, p=0.5),
            ], p=0.3),
            A.OneOf([
                A.MotionBlur(blur_limit=3, p=0.5),
                A.MedianBlur(blur_limit=3, p=0.5),
            ], p=0.3),
            A.ShiftScaleRotate(
                shift_limit=0.0625, 
                scale_limit=0.1, 
                rotate_limit=15, 
                p=0.5
            ),
            A.OneOf([
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.3),
                A.ElasticTransform(p=0.3),
            ], p=0.3),
            A.OneOf([
                A.CLAHE(clip_limit=2, p=0.5),
                A.Sharpen(p=0.5),
                A.Emboss(p=0.5),
            ], p=0.3),
            A.HueSaturationValue(
                hue_shift_limit=20, 
                sat_shift_limit=30, 
                val_shift_limit=20, 
                p=0.5
            ),
            A.RandomBrightnessContrast(
                brightness_limit=0.2, 
                contrast_limit=0.2, 
                p=0.5
            ),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def data_generator(self, df, augment=True, shuffle=True):
        """Advanced data generator with custom augmentation"""
        augmentation = self.create_advanced_augmentation() if augment else A.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )
        
        while True:
            if shuffle:
                df = df.sample(frac=1).reset_index(drop=True)
            
            for i in range(0, len(df), self.batch_size):
                batch_df = df.iloc[i:i+self.batch_size]
                
                images = []
                crop_labels = []
                disease_labels = []
                yield_values = []
                
                for _, row in batch_df.iterrows():
                    # Load image
                    try:
                        image = cv2.imread(row['image_path'])
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        image = cv2.resize(image, (self.img_width, self.img_height))
                        
                        # Apply augmentation
                        augmented = augmentation(image=image)
                        image = augmented['image']
                        
                        images.append(image)
                        crop_labels.append(row['crop_encoded'])
                        disease_labels.append(row['disease_encoded'])
                        yield_values.append(row['yield_estimate'])
                        
                    except Exception as e:
                        print(f"Error loading image {row['image_path']}: {e}")
                        continue
                
                if len(images) > 0:
                    yield (
                        np.array(images),
                        {
                            'crop_classification': np.array(crop_labels),
                            'disease_classification': np.array(disease_labels),
                            'yield_regression': np.array(yield_values)
                        }
                    )
    
    def build_advanced_model(self):
        """Build advanced multi-task model with attention mechanisms"""
        print("🏗️ Building advanced model architecture...")
        
        # Input layer
        input_layer = Input(shape=(self.img_height, self.img_width, 3))
        
        # Base model - EfficientNetV2 for better performance
        base_model = EfficientNetV2B0(
            weights='imagenet',
            include_top=False,
            input_tensor=input_layer
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Feature extraction
        x = base_model.output
        x = GlobalAveragePooling2D(name='global_avg_pool')(x)
        
        # Shared dense layers
        shared_dense = Dense(1024, activation='relu', name='shared_dense_1')(x)
        shared_dense = BatchNormalization(name='shared_bn_1')(shared_dense)
        shared_dense = Dropout(0.3, name='shared_dropout_1')(shared_dense)
        
        shared_dense = Dense(512, activation='relu', name='shared_dense_2')(shared_dense)
        shared_dense = BatchNormalization(name='shared_bn_2')(shared_dense)
        shared_dense = Dropout(0.2, name='shared_dropout_2')(shared_dense)
        
        # Task-specific branches
        
        # Crop classification branch
        crop_branch = Dense(256, activation='relu', name='crop_dense_1')(shared_dense)
        crop_branch = Dropout(0.2, name='crop_dropout')(crop_branch)
        crop_output = Dense(
            len(self.crop_encoder.classes_),
            activation='softmax',
            name='crop_classification'
        )(crop_branch)
        
        # Disease classification branch
        disease_branch = Dense(512, activation='relu', name='disease_dense_1')(shared_dense)
        disease_branch = Dropout(0.3, name='disease_dropout_1')(disease_branch)
        disease_branch = Dense(256, activation='relu', name='disease_dense_2')(disease_branch)
        disease_branch = Dropout(0.2, name='disease_dropout_2')(disease_branch)
        disease_output = Dense(
            len(self.disease_encoder.classes_),
            activation='softmax',
            name='disease_classification'
        )(disease_branch)
        
        # Yield regression branch
        yield_branch = Dense(256, activation='relu', name='yield_dense_1')(shared_dense)
        yield_branch = Dropout(0.2, name='yield_dropout_1')(yield_branch)
        yield_branch = Dense(128, activation='relu', name='yield_dense_2')(yield_branch)
        yield_branch = Dropout(0.1, name='yield_dropout_2')(yield_branch)
        yield_output = Dense(1, activation='linear', name='yield_regression')(yield_branch)
        
        # Create model
        model = Model(
            inputs=input_layer,
            outputs=[crop_output, disease_output, yield_output]
        )
        
        return model
    
    def compile_advanced_model(self, model):
        """Compile model with advanced optimization"""
        # Use AdamW optimizer for better generalization
        optimizer = AdamW(
            learning_rate=self.config['learningRate'],
            weight_decay=0.01
        )
        
        model.compile(
            optimizer=optimizer,
            loss={
                'crop_classification': 'sparse_categorical_crossentropy',
                'disease_classification': 'sparse_categorical_crossentropy',
                'yield_regression': 'huber'  # More robust to outliers
            },
            loss_weights={
                'crop_classification': 1.0,
                'disease_classification': 2.5,  # Higher weight for disease detection
                'yield_regression': 0.8
            },
            metrics={
                'crop_classification': ['accuracy', 'top_3_categorical_accuracy'],
                'disease_classification': ['accuracy', 'precision', 'recall'],
                'yield_regression': ['mae', 'mse']
            }
        )
        
        return model
    
    def create_callbacks(self):
        """Create advanced training callbacks"""
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_disease_classification_accuracy',
                factor=0.3,
                patience=8,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=os.path.join(self.output_dir, 'best_model.h5'),
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=False,
                verbose=1
            ),
            TensorBoard(
                log_dir=os.path.join(self.output_dir, 'tensorboard_logs'),
                histogram_freq=1,
                write_graph=True,
                write_images=True
            ),
            CSVLogger(
                filename=os.path.join(self.output_dir, 'training_log.csv'),
                append=True
            )
        ]
        
        return callbacks
    
    def train_model(self, train_df, val_df):
        """Train the advanced model"""
        print("🚀 Starting advanced model training...")
        
        # Create data generators
        train_gen = self.data_generator(train_df, augment=True, shuffle=True)
        val_gen = self.data_generator(val_df, augment=False, shuffle=False)
        
        # Calculate steps
        train_steps = len(train_df) // self.batch_size
        val_steps = len(val_df) // self.batch_size
        
        # Build and compile model
        model = self.build_advanced_model()
        model = self.compile_advanced_model(model)
        
        print("📋 Model Summary:")
        model.summary()
        
        # Save model architecture
        with open(os.path.join(self.output_dir, 'model_architecture.json'), 'w') as f:
            f.write(model.to_json())
        
        # Create callbacks
        callbacks = self.create_callbacks()
        
        # Train model
        print(f"🎯 Training for {self.config['epochs']} epochs...")
        history = model.fit(
            train_gen,
            steps_per_epoch=train_steps,
            epochs=self.config['epochs'],
            validation_data=val_gen,
            validation_steps=val_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        # Fine-tuning phase
        print("🔧 Starting fine-tuning phase...")
        model.get_layer('efficientnetv2-b0').trainable = True
        
        # Lower learning rate for fine-tuning
        model.compile(
            optimizer=AdamW(learning_rate=self.config['learningRate'] * 0.1),
            loss={
                'crop_classification': 'sparse_categorical_crossentropy',
                'disease_classification': 'sparse_categorical_crossentropy',
                'yield_regression': 'huber'
            },
            loss_weights={
                'crop_classification': 1.0,
                'disease_classification': 2.5,
                'yield_regression': 0.8
            },
            metrics={
                'crop_classification': ['accuracy'],
                'disease_classification': ['accuracy', 'precision', 'recall'],
                'yield_regression': ['mae']
            }
        )
        
        # Fine-tune for additional epochs
        fine_tune_epochs = 20
        history_fine = model.fit(
            train_gen,
            steps_per_epoch=train_steps,
            epochs=fine_tune_epochs,
            validation_data=val_gen,
            validation_steps=val_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        model.save(os.path.join(self.output_dir, 'agricultural_ai_final.h5'))
        
        # Save encoders
        np.save(os.path.join(self.output_dir, 'crop_encoder.npy'), self.crop_encoder.classes_)
        np.save(os.path.join(self.output_dir, 'disease_encoder.npy'), self.disease_encoder.classes_)
        
        print("✅ Training completed!")
        return model, history, history_fine
    
    def evaluate_model(self, model, test_df):
        """Comprehensive model evaluation"""
        print("📊 Evaluating model performance...")
        
        test_gen = self.data_generator(test_df, augment=False, shuffle=False)
        test_steps = len(test_df) // self.batch_size
        
        # Evaluate model
        results = model.evaluate(test_gen, steps=test_steps, verbose=1)
        
        # Generate predictions for detailed analysis
        predictions = model.predict(test_gen, steps=test_steps, verbose=1)
        
        # Create evaluation report
        evaluation_report = {
            'test_loss': results[0],
            'crop_accuracy': results[1],
            'disease_accuracy': results[2],
            'yield_mae': results[3],
            'model_parameters': model.count_params(),
            'test_samples': len(test_df)
        }
        
        # Save evaluation results
        with open(os.path.join(self.output_dir, 'evaluation_results.json'), 'w') as f:
            json.dump(evaluation_report, f, indent=2)
        
        print("📈 Evaluation Results:")
        for key, value in evaluation_report.items():
            print(f"  {key}: {value}")
        
        return evaluation_report
    
    def convert_for_deployment(self):
        """Convert model for various deployment formats"""
        print("🔄 Converting model for deployment...")
        
        model_path = os.path.join(self.output_dir, 'agricultural_ai_final.h5')
        
        # Convert to TensorFlow.js
        try:
            import tensorflowjs as tfjs
            web_model_dir = os.path.join(self.output_dir, 'web_model')
            tfjs.converters.save_keras_model(
                tf.keras.models.load_model(model_path),
                web_model_dir
            )
            print(f"✅ Web model saved to {web_model_dir}")
        except ImportError:
            print("⚠️ TensorFlow.js not available for web conversion")
        
        # Convert to TensorFlow Lite
        try:
            converter = tf.lite.TFLiteConverter.from_keras_model(
                tf.keras.models.load_model(model_path)
            )
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model = converter.convert()
            
            tflite_path = os.path.join(self.output_dir, 'agricultural_ai_mobile.tflite')
            with open(tflite_path, 'wb') as f:
                f.write(tflite_model)
            print(f"✅ Mobile model saved to {tflite_path}")
        except Exception as e:
            print(f"⚠️ TensorFlow Lite conversion failed: {e}")

def main():
    """Main training execution"""
    print("🌾 Starting Advanced Agricultural AI Training...")
    
    # Initialize trainer
    trainer = AdvancedAgriculturalTrainer()
    
    # Load processed data
    train_df, val_df, test_df = trainer.load_processed_data()
    
    # Train model
    model, history, history_fine = trainer.train_model(train_df, val_df)
    
    # Evaluate model
    evaluation_results = trainer.evaluate_model(model, test_df)
    
    # Convert for deployment
    trainer.convert_for_deployment()
    
    print("🎉 Advanced Agricultural AI training completed successfully!")
    print(f"📁 All outputs saved to: {trainer.output_dir}")

if __name__ == "__main__":
    main()