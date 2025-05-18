import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import pickle

class BusynessPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def save_model(self, filepath='busyness_model.pkl'):
        """Save the trained model and scaler"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='busyness_model.pkl'):
        """Load a trained model and scaler"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        print(f"Model loaded from {filepath}")
        
    def prepare_features(self, df):
        """Prepare features from the dataset"""
        # Convert date to datetime if it's not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        df['quarter'] = df['date'].dt.quarter
        
        # Select features for training
        features = ['day_of_week', 'month', 'day', 'is_weekend', 
                   'is_month_start', 'is_month_end', 'quarter']
        return df[features]
    
    def train(self, data):
        """
        Train the model
        data: DataFrame with columns ['date', 'busyness_score']
        """
        X = self.prepare_features(data)
        y = data['busyness_score']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'mse': mse,
            'r2': r2,
            'feature_importance': dict(zip(X.columns, self.model.feature_importances_))
        }
    
    def predict(self, date):
        """
        Predict busyness for a given date
        date: datetime object or string that can be converted to datetime
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)
            
        # Create a single-row DataFrame
        df = pd.DataFrame({'date': [date]})
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict(X_scaled)[0]

# Example usage
if __name__ == "__main__":
    # Load the emergency visits data
    data = pd.read_csv('emergency_visits_realistic.csv')
    data = data.rename(columns={
        'date_time': 'date',
        'number_of_people': 'busyness_score'
    })
    
    # Initialize and train the model
    predictor = BusynessPredictor()
    metrics = predictor.train(data)
    
    # Save the trained model
    predictor.save_model()
    
    print("Model Performance:")
    print(f"Mean Squared Error: {metrics['mse']:.2f}")
    print(f"R² Score: {metrics['r2']:.2f}")
    print("\nFeature Importance:")
    for feature, importance in metrics['feature_importance'].items():
        print(f"{feature}: {importance:.3f}")
    
    # Make predictions for next week
    future_dates = pd.date_range(start='2024-12-01', end='2024-12-07', freq='D')
    print("\nPredictions for next week:")
    for date in future_dates:
        prediction = predictor.predict(date)
        print(f"{date.strftime('%Y-%m-%d')}: {prediction:.0f} people")