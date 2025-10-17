# train_model_local.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import boto3
import os

# --- Configuration ---
bucket_name = 'sentinel-ops-data-lake-satya' # Your S3 bucket name
data_s3_key = 'data/server_disk_usage_sample.csv' # Path to your data in S3
model_local_path = 'disk_usage_predictor.joblib' # Local path to save model
model_s3_key = 'models/disk_usage_predictor.joblib' # S3 path to save model

# --- 1. Load Data from S3 ---
print(f"Downloading data from s3://{bucket_name}/{data_s3_key}...")
s3_client = boto3.client('s3')
s3_client.download_file(bucket_name, data_s3_key, 'server_disk_usage_sample.csv') # Download to current dir
df = pd.read_csv('server_disk_usage_sample.csv')
print("Data loaded successfully:")
print(df.head())

# --- 2. Preprocess Data & Create Target Variable ---
# Our CSV already has 'hour' and 'dayofweek'.
# Define the target: 1 if disk_usage_percent > 90, else 0
df['high_disk_usage'] = (df['disk_usage_percent'] > 90).astype(int)
print("\nTarget variable 'high_disk_usage' created.")

# Select features and target
features = ['hour', 'dayofweek', 'disk_usage_percent']
target = 'high_disk_usage'
X = df[features]
y = df[target]
print("Features (X) and Target (y) prepared.")

# --- 3. Train Model ---
print("\nTraining RandomForestClassifier model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
print("Model trained successfully.")

# --- 4. Evaluate Model (Optional but good practice) ---
y_pred = model.predict(X) # Evaluate on training data for simplicity
print("\nModel Evaluation (on training data):")
print(classification_report(y, y_pred))
print(f"Accuracy: {accuracy_score(y, y_pred):.2f}")

# --- 5. Save Model Locally ---
joblib.dump(model, model_local_path)
print(f"\nModel saved locally to {model_local_path}")

# --- 6. Upload Model to S3 ---
print(f"\nUploading model to s3://{bucket_name}/{model_s3_key}...")
s3_client.upload_file(model_local_path, bucket_name, model_s3_key)
print(f"Model uploaded to S3: s3://{bucket_name}/{model_s3_key}")

# Clean up local data file
os.remove('server_disk_usage_sample.csv')
print("Cleaned up local data file.")