from flask import Flask, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load model
model_path = os.getenv('MODEL_PATH', 'churn_model.pkl')
with open(model_path, 'rb') as f:
    model, scaler = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = np.array([[
        data['total_events'],
        data['total_spent'],
        data['avg_order_value']
    ]])
    
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][1]
    
    return jsonify({
        'churned': bool(prediction),
        'churn_probability': float(probability)
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
