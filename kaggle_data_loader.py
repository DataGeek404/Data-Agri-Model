#!/usr/bin/env python3
"""
Kaggle Dataset Loader for Agricultural AI Training
Handles the three specified datasets:
1. Corn Disease Drone Images
2. Agriculture Crop Images  
3. Aerial Crop Data for Image SR
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import shutil
import json
from sklearn.model_selection import train_test_split
import cv2
from PIL import Image
import kaggle

class KaggleAgriculturalDataLoader:
    def __init__(self, data_dir='datasets/'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Dataset configurations
        self.datasets = {
            'corn_disease': {
                'name': 'alexanderyevchenko/corn-disease-drone-images',
                'path': self.data_dir / 'corn-disease-drone-images',
                'type': 'disease_detection'
            },
            'crop_images': {
                'name': 'aman2000jaiswal/agriculture-crop-images',
                'path': self.data_dir / 'agriculture-crop-images',
                'type': 'crop_classification'
            },
            'aerial_yield': {
                'name': 'masiaslahi/aerial-crop-data-for-image-sr',
                'path': self.data_dir / 'aerial-crop-data-for-image-sr',
                'type': 'yield_estimation'
            }
        }
    
    def download_datasets(self):
        """Download all three Kaggle datasets"""
        print("🔄 Downloading Kaggle datasets...")
        
        for dataset_key, config in self.datasets.items():
            print(f"📥 Downloading {config['name']}...")
            try:
                kaggle.api.dataset_download_files(
                    config['name'],
                    path=str(config['path']),
                    unzip=True
                )
                print(f"✅ Downloaded {dataset_key}")
            except Exception as e:
                print(f"❌ Error downloading {dataset_key}: {e}")
                print("Make sure you have kaggle API configured:")
                print("1. pip install kaggle")
                print("2. Get API token from kaggle.com/account")
                print("3. Place kaggle.json in ~/.kaggle/")
    
    def process_corn_disease_dataset(self):
        """Process corn disease drone images dataset"""
        print("🌽 Processing corn disease dataset...")
        
        dataset_path = self.datasets['corn_disease']['path']
        processed_data = []
        
        # Expected structure: folders named by disease type
        disease_folders = [d for d in dataset_path.iterdir() if d.is_dir()]
        
        for disease_folder in disease_folders:
            disease_name = disease_folder.name.lower().replace('_', ' ')
            
            # Map folder names to standardized disease names
            disease_mapping = {
                'healthy': 'Healthy',
                'northern leaf blight': 'Northern Leaf Blight',
                'common rust': 'Common Rust',
                'gray leaf spot': 'Gray Leaf Spot',
                'southern rust': 'Southern Rust'
            }
            
            standardized_disease = disease_mapping.get(disease_name, disease_name.title())
            
            for image_file in disease_folder.glob('*.jpg'):
                processed_data.append({
                    'image_path': str(image_file),
                    'crop_type': 'Maize/Corn',
                    'disease': standardized_disease,
                    'severity': 'none' if standardized_disease == 'Healthy' else 'medium',
                    'dataset_source': 'corn_disease_drone',
                    'image_type': 'drone'
                })
        
        return processed_data
    
    def process_crop_images_dataset(self):
        """Process agriculture crop images dataset"""
        print("🌾 Processing crop images dataset...")
        
        dataset_path = self.datasets['crop_images']['path']
        processed_data = []
        
        # Expected structure: crop_type/disease_type/images
        for crop_folder in dataset_path.iterdir():
            if not crop_folder.is_dir():
                continue
                
            crop_name = crop_folder.name.replace('_', ' ').title()
            
            # Standardize crop names
            crop_mapping = {
                'Corn': 'Maize/Corn',
                'Maize': 'Maize/Corn',
                'Paddy': 'Rice',
                'Sugarcane': 'Sugarcane',
                'Wheat': 'Wheat',
                'Cotton': 'Cotton',
                'Tomato': 'Tomato',
                'Potato': 'Potato'
            }
            
            standardized_crop = crop_mapping.get(crop_name, crop_name)
            
            # Process disease folders within crop folder
            for disease_folder in crop_folder.iterdir():
                if not disease_folder.is_dir():
                    continue
                    
                disease_name = disease_folder.name.replace('_', ' ').title()
                
                for image_file in disease_folder.glob('*.jpg'):
                    severity = 'none' if 'healthy' in disease_name.lower() else 'medium'
                    
                    processed_data.append({
                        'image_path': str(image_file),
                        'crop_type': standardized_crop,
                        'disease': disease_name,
                        'severity': severity,
                        'dataset_source': 'crop_images',
                        'image_type': 'field'
                    })
        
        return processed_data
    
    def process_aerial_yield_dataset(self):
        """Process aerial crop data for yield estimation"""
        print("🛩️ Processing aerial yield dataset...")
        
        dataset_path = self.datasets['aerial_yield']['path']
        processed_data = []
        
        # Look for CSV files with yield data
        csv_files = list(dataset_path.glob('*.csv'))
        
        if csv_files:
            for csv_file in csv_files:
                df = pd.read_csv(csv_file)
                
                # Expected columns: image_path, yield, crop_type, etc.
                for _, row in df.iterrows():
                    # Estimate yield based on available data
                    yield_estimate = self.estimate_yield_from_row(row)
                    
                    processed_data.append({
                        'image_path': str(dataset_path / row.get('image_path', '')),
                        'crop_type': row.get('crop_type', 'Unknown'),
                        'disease': 'Healthy',  # Assume healthy for yield estimation
                        'severity': 'none',
                        'yield_estimate': yield_estimate,
                        'dataset_source': 'aerial_yield',
                        'image_type': 'aerial'
                    })
        else:
            # If no CSV, process image folders
            for image_file in dataset_path.glob('**/*.jpg'):
                # Extract yield info from filename or folder structure
                yield_estimate = self.estimate_yield_from_filename(image_file.name)
                
                processed_data.append({
                    'image_path': str(image_file),
                    'crop_type': 'Mixed',
                    'disease': 'Healthy',
                    'severity': 'none',
                    'yield_estimate': yield_estimate,
                    'dataset_source': 'aerial_yield',
                    'image_type': 'aerial'
                })
        
        return processed_data
    
    def estimate_yield_from_row(self, row):
        """Estimate yield from CSV row data"""
        # Look for yield-related columns
        yield_columns = ['yield', 'yield_per_acre', 'production', 'tons_per_hectare']
        
        for col in yield_columns:
            if col in row and pd.notna(row[col]):
                return float(row[col])
        
        # Default yield estimate based on crop type
        default_yields = {
            'Maize/Corn': 4.2,
            'Wheat': 3.1,
            'Rice': 4.8,
            'Soybean': 2.9
        }
        
        crop_type = row.get('crop_type', 'Unknown')
        return default_yields.get(crop_type, 3.5)
    
    def estimate_yield_from_filename(self, filename):
        """Extract yield estimate from filename patterns"""
        # Look for numeric patterns in filename
        import re
        numbers = re.findall(r'\d+\.?\d*', filename)
        
        if numbers:
            # Use first reasonable number as yield estimate
            for num in numbers:
                val = float(num)
                if 1.0 <= val <= 50.0:  # Reasonable yield range
                    return val
        
        # Random yield in typical range
        return np.random.uniform(2.5, 6.0)
    
    def create_unified_dataset(self):
        """Combine all datasets into unified training format"""
        print("🔄 Creating unified dataset...")
        
        all_data = []
        
        # Process each dataset
        corn_data = self.process_corn_disease_dataset()
        crop_data = self.process_crop_images_dataset()
        aerial_data = self.process_aerial_yield_dataset()
        
        all_data.extend(corn_data)
        all_data.extend(crop_data)
        all_data.extend(aerial_data)
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Add yield estimates for missing values
        df['yield_estimate'] = df.apply(self.add_yield_estimates, axis=1)
        
        # Clean and validate data
        df = self.clean_dataset(df)
        
        return df
    
    def add_yield_estimates(self, row):
        """Add yield estimates based on crop type and health"""
        if pd.notna(row['yield_estimate']):
            return row['yield_estimate']
        
        # Base yields by crop type (tons per acre)
        base_yields = {
            'Maize/Corn': 4.5,
            'Wheat': 3.2,
            'Rice': 5.1,
            'Sugarcane': 45.0,
            'Soybean': 2.8,
            'Cotton': 1.2,
            'Tomato': 25.0,
            'Potato': 18.0
        }
        
        base_yield = base_yields.get(row['crop_type'], 3.5)
        
        # Adjust based on disease severity
        severity_multipliers = {
            'none': 1.0,
            'low': 0.9,
            'medium': 0.75,
            'high': 0.6
        }
        
        multiplier = severity_multipliers.get(row['severity'], 0.8)
        
        # Add some randomness
        random_factor = np.random.uniform(0.85, 1.15)
        
        return round(base_yield * multiplier * random_factor, 2)
    
    def clean_dataset(self, df):
        """Clean and validate the dataset"""
        print("🧹 Cleaning dataset...")
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['image_path', 'crop_type', 'disease'])
        
        # Validate image files exist
        df = df[df['image_path'].apply(lambda x: os.path.exists(x))]
        
        # Standardize text fields
        df['crop_type'] = df['crop_type'].str.strip().str.title()
        df['disease'] = df['disease'].str.strip().str.title()
        
        # Ensure yield estimates are reasonable
        df['yield_estimate'] = df['yield_estimate'].clip(0.1, 100.0)
        
        print(f"✅ Dataset cleaned: {len(df)} samples")
        return df
    
    def split_dataset(self, df, test_size=0.2, val_size=0.1):
        """Split dataset into train/validation/test sets"""
        print("📊 Splitting dataset...")
        
        # Stratify by crop type and disease
        df['stratify_key'] = df['crop_type'] + '_' + df['disease']
        
        # First split: train+val vs test
        train_val_df, test_df = train_test_split(
            df, 
            test_size=test_size, 
            stratify=df['stratify_key'],
            random_state=42
        )
        
        # Second split: train vs val
        val_ratio = val_size / (1 - test_size)
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_ratio,
            stratify=train_val_df['stratify_key'],
            random_state=42
        )
        
        # Remove stratify column
        for split_df in [train_df, val_df, test_df]:
            split_df.drop('stratify_key', axis=1, inplace=True)
        
        print(f"📈 Dataset split:")
        print(f"  Train: {len(train_df)} samples")
        print(f"  Validation: {len(val_df)} samples") 
        print(f"  Test: {len(test_df)} samples")
        
        return train_df, val_df, test_df
    
    def save_processed_data(self, train_df, val_df, test_df, output_dir='processed_data/'):
        """Save processed datasets"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save CSV files
        train_df.to_csv(output_path / 'train.csv', index=False)
        val_df.to_csv(output_path / 'validation.csv', index=False)
        test_df.to_csv(output_path / 'test.csv', index=False)
        
        # Save dataset statistics
        stats = {
            'total_samples': len(train_df) + len(val_df) + len(test_df),
            'train_samples': len(train_df),
            'val_samples': len(val_df),
            'test_samples': len(test_df),
            'crop_types': sorted(train_df['crop_type'].unique().tolist()),
            'diseases': sorted(train_df['disease'].unique().tolist()),
            'dataset_sources': sorted(train_df['dataset_source'].unique().tolist())
        }
        
        with open(output_path / 'dataset_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"💾 Processed data saved to {output_dir}")
        return stats

def main():
    """Main execution function"""
    print("🚀 Starting Kaggle Agricultural AI Data Processing...")
    
    # Initialize data loader
    loader = KaggleAgriculturalDataLoader()
    
    # Download datasets
    loader.download_datasets()
    
    # Create unified dataset
    df = loader.create_unified_dataset()
    
    # Split dataset
    train_df, val_df, test_df = loader.split_dataset(df)
    
    # Save processed data
    stats = loader.save_processed_data(train_df, val_df, test_df)
    
    print("✅ Data processing completed!")
    print(f"📊 Dataset Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()