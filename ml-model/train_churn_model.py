import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os

# Connect to MongoDB
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['customer360']

# Fetch user profiles
profiles = list(db.user_profiles.find())
df = pd.DataFrame(profiles)

# Feature engineering
df['total_events'] = df['total_events'].fillna(0)
df['total_spent'] = df['total_spent'].fillna(0)
df['avg_order_value'] = df['avg_order_value'].fillna(0)

# Create synthetic churn labels (in real scenario, this comes from historical data)
df['churned'] = (df['total_events'] < 5).astype(int)

# Prepare features
features = ['total_events', 'total_spent', 'avg_order_value']
X = df[features]
y = df['churned']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train_scaled, y_train)

accuracy = model.score(X_test_scaled, y_test)
print(f"Model Accuracy: {accuracy:.2%}")

# Save model
with open('churn_model.pkl', 'wb') as f:
    pickle.dump((model, scaler), f)

print("Model saved successfully!")
