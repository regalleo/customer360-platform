# 📊 Customer 360 Analytics Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Now-brightgreen?style=for-the-badge)](https://customer360-brxq.onrender.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/regalleo/customer360-platform)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🚀 Overview

A **production-grade big data analytics platform** that processes real-time customer data streams using **Apache Kafka**, **Apache Spark**, and **MongoDB**.  
This system demonstrates **enterprise-level data engineering** with real-time streaming, machine learning predictions, and an interactive dashboard.

**Perfect for:** Data Engineering portfolios | Big Data projects | Real-time Analytics systems

---

## ✨ Key Features

- 🔄 **Real-time Stream Processing** — Apache Kafka for event ingestion  
- ⚡ **Distributed Computing** — Apache Spark for scalable processing  
- 💾 **Document Database** — MongoDB for flexible storage  
- 🤖 **ML-Powered Predictions** — Churn prediction using scikit-learn  
- 📊 **Interactive Dashboard** — Live analytics with professional UI  
- 🐳 **Docker Ready** — Containerized and production-deployable  
- 📈 **Enterprise Grade** — Optimized for performance and scalability  

---

## 🏗️ Architecture

DATA SOURCES (Events, Transactions)
↓
APACHE KAFKA (Event Streaming)
↓
APACHE SPARK (Stream Processing)
↓
MONGODB (Data Storage)
↓
MACHINE LEARNING (Churn Predictions)
↓
FLASK DASHBOARD (Frontend UI)

---

## 📁 Project Structure

customer360-platform/
├── dashboard/ # Flask web application
│ ├── app.py # Main dashboard
│ └── templates/ # HTML templates
├── data-generator/ # Kafka producer
│ └── producer.py # Generates customer events
├── spark-streaming/ # Spark streaming jobs
│ ├── stream_processor.py # Real-time processing
│ └── requirements.txt # Spark dependencies
├── ml-model/ # Machine learning
│ ├── train_churn_model.py # Model training
│ ├── predict_api.py # Prediction API
│ └── churn_model.pkl # Trained model
├── docker-compose.yml # Multi-container orchestration
├── Dockerfile # Container image
├── requirements.txt # Python dependencies
└── README.md # Documentation


---

## 🛠️ Technology Stack

**Data Engineering**

- Apache Kafka 7.5.0  
- Apache Spark 3.5.0  
- MongoDB 7.0  

**Backend**

- Python 3.9  
- Flask 2.3.0  
- scikit-learn 1.3.0  

**Frontend**

- HTML5 / CSS3 / Chart.js  
- Responsive Netflix-style UI  

**DevOps**

- Docker & Docker Compose  
- Render (Cloud Deployment)  

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose  
- Python 3.9+  
- Git  
- 8GB+ RAM (for Spark)  

---

🔌 API Endpoints
🧭 Dashboard

GET / — Returns main analytics dashboard with charts and KPIs

🤖 ML API

POST /api/predict
Input: Customer features
Output: Churn score (0.0 - 1.0)

📈 Metrics API

GET /api/metrics — Returns real-time system metrics
⚙️ Performance Optimizations
✅ Database indexing — 10× faster queries
✅ Query caching — Reduced DB load
✅ Connection pooling — Concurrency handling
✅ Spark micro-batching — Efficient streaming
✅ ML model serialization — Fast inference

🎯 Learning Outcomes 
This project demonstrates:
✅ Big Data Engineering (Kafka, Spark, MongoDB)
✅ Real-time Stream Processing
✅ End-to-End Data Pipeline Design
✅ Machine Learning & Inference
✅ System Design & Architecture
✅ DevOps & Cloud Deployment
✅ Full-stack Integration

📊 Dashboard Features

Real-time KPIs & Charts
Customer Segmentation
Revenue & Churn Analytics
Engagement Tracking
Professional UI/UX
Mobile Responsive

🔐 Security & Best Practices

✅ Environment Variable Management
✅ Database Authentication
✅ Input Validation
✅ Error Handling
✅ Logging & Monitoring
✅ Dockerized Isolation

🎓 What's Next?

Planned Enhancements:
🔔 Real-time churn alerts
📊 RFM segmentation
🧪 A/B testing framework
⏱️ Time-series forecasting
🧠 GraphDB integration
☸️ Kubernetes orchestration
🖥️ 3D visualizations

👨‍💻 About

Software Developer & Data Engineer
📍 Bangalore, India
📧 rajsingh170901@gmail.com

Skills:

Java • Python • Kafka • Spark • MongoDB • Flask • React • AWS • Docker • Kubernetes • AI/ML

📞 Connect

🔗 GitHub: https://github.com/regalleo
💼 LinkedIn: https://www.linkedin.com/in/raj-shekhar-singh-aa16ab245/

📜 License
MIT License — Free to use for any purpose

⭐ Support
If this project helped you, please give it a star ⭐ on GitHub!




