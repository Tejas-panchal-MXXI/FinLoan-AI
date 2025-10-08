import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

class LoanPredictor:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_and_preprocess_data(self, csv_path):
        """Load and preprocess the loan dataset"""
        print("=== LOADING DATASET ===")
        df = pd.read_csv(csv_path)
        print(f"Dataset shape: {df.shape}")
        
        # Handle missing values
        df['Gender'].fillna(df['Gender'].mode()[0], inplace=True)
        df['Married'].fillna(df['Married'].mode()[0], inplace=True)
        df['Dependents'].fillna(df['Dependents'].mode()[0], inplace=True)
        df['Self_Employed'].fillna(df['Self_Employed'].mode()[0], inplace=True)
        df['LoanAmount'].fillna(df['LoanAmount'].median(), inplace=True)
        df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].mode()[0], inplace=True)
        df['Credit_History'].fillna(df['Credit_History'].mode()[0], inplace=True)
        
        # Drop Loan_ID
        df = df.drop('Loan_ID', axis=1)
        
        # Feature Engineering
        df['Total_Income'] = df['ApplicantIncome'] + df['CoapplicantIncome']
        df['Loan_Income_Ratio'] = df['LoanAmount'] / df['Total_Income']
        df['Loan_Income_Ratio'].replace([np.inf, -np.inf], np.nan, inplace=True)
        df['Loan_Income_Ratio'].fillna(df['Loan_Income_Ratio'].median(), inplace=True)
        
        # Income per dependent
        df['Income_per_Dependent'] = df['Total_Income'] / (df['Dependents'].replace({'3+': '3'}).astype(int) + 1)
        
        return df
    
    def encode_features(self, df):
        """Encode categorical features"""
        print("=== ENCODING FEATURES ===")
        df_encoded = df.copy()
        
        # Categorical columns to encode
        categorical_cols = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'Property_Area']
        
        for col in categorical_cols:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col])
            self.encoders[col] = le
            
        # Encode target variable
        le_target = LabelEncoder()
        df_encoded['Loan_Status'] = le_target.fit_transform(df_encoded['Loan_Status'])
        self.encoders['Loan_Status'] = le_target
        
        print("Encoding completed!")
        return df_encoded
    
    def train_models(self, df_encoded):
        """Train multiple ML models"""
        print("=== TRAINING ML MODELS ===")
        
        # Prepare features and target
        X = df_encoded.drop('Loan_Status', axis=1)
        y = df_encoded['Loan_Status']
        self.feature_names = X.columns.tolist()
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize models
        models = {
            'logistic_regression': LogisticRegression(random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(kernel='rbf', probability=True, random_state=42)
        }
        
        results = {}
        
        # Train and evaluate each model
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Use scaled data for SVM and Logistic Regression, original for Random Forest
            if name in ['svm', 'logistic_regression']:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_prob = model.predict_proba(X_test_scaled)[:, 1]
                
                # Cross-validation with scaled data
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_prob = model.predict_proba(X_test)[:, 1]
                
                # Cross-validation with original data
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predictions': y_pred,
                'probabilities': y_prob
            }
            
            print(f"{name} - Accuracy: {accuracy:.4f}, CV: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
        self.models = models
        return results, X_test, y_test
    
    def get_feature_importance(self):
        """Get feature importance from Random Forest"""
        if 'random_forest' in self.models:
            rf_model = self.models['random_forest']
            importance = rf_model.feature_importances_
            feature_importance = list(zip(self.feature_names, importance))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            return feature_importance
        return []
    
    def predict_single(self, applicant_data):
        """Make prediction for a single applicant"""
        # Use the best performing model (typically Random Forest)
        model = self.models['random_forest']
        
        # Convert input to proper format
        input_df = pd.DataFrame([applicant_data])
        
        # Encode categorical features
        for col, encoder in self.encoders.items():
            if col != 'Loan_Status' and col in input_df.columns:
                input_df[col] = encoder.transform(input_df[col])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0]
        
        return {
            'approved': bool(prediction),
            'approval_probability': float(probability[1] * 100),
            'rejection_probability': float(probability[0] * 100)
        }
    
    def save_models(self, path=''):
        joblib.dump(self.models, 'loan_models.joblib')
        joblib.dump(self.encoders, 'encoders.joblib')
        joblib.dump(self.scaler, 'scaler.joblib')
        joblib.dump(self.feature_names, 'features.joblib')
        
        print("✅ Models saved successfully!")
        print(f"   Saved in: {os.getcwd()}")
        print("   Files: loan_models.joblib, encoders.joblib, scaler.joblib, features.joblib")


# Training script
if __name__ == "__main__":
    # Initialize predictor
    predictor = LoanPredictor()
    
    # Load and preprocess data
    df = predictor.load_and_preprocess_data('../../data/loan_dataset.csv')
    df_encoded = predictor.encode_features(df)
    
    # Train models
    results, X_test, y_test = predictor.train_models(df_encoded)
    
    # Display results
    print("\n=== FINAL RESULTS ===")
    for name, result in results.items():
        print(f"{name}: {result['accuracy']:.4f} accuracy")
    
    # Feature importance
    feature_importance = predictor.get_feature_importance()
    print("\n=== TOP 10 IMPORTANT FEATURES ===")
    for feature, importance in feature_importance[:10]:
        print(f"{feature}: {importance:.4f}")
    
    # Save models
    predictor.save_models()
    
    # Test prediction
    sample_data = {
        'Gender': 'Male',
        'Married': 'Yes',
        'Dependents': '1',
        'Education': 'Graduate',
        'Self_Employed': 'No',
        'ApplicantIncome': 5000,
        'CoapplicantIncome': 2000,
        'LoanAmount': 150,
        'Loan_Amount_Term': 360,
        'Credit_History': 1.0,
        'Property_Area': 'Urban',
        'Total_Income': 7000,
        'Loan_Income_Ratio': 0.0214,
        'Income_per_Dependent': 3500
    }
    
    result = predictor.predict_single(sample_data)
    print(f"\n=== SAMPLE PREDICTION ===")
    print(f"Approved: {result['approved']}")
    print(f"Approval Probability: {result['approval_probability']:.2f}%")
