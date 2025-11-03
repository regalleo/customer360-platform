from flask import Flask, render_template_string, jsonify
from pymongo import MongoClient
from functools import lru_cache
import json
import os
from threading import Thread
import time

app = Flask(__name__)

mongo_uri = os.getenv('MONGO_URI')

# Only connect to MongoDB if MONGO_URI is provided
if not mongo_uri:
    # Skip MongoDB connection if no URI provided
    client = None
    db = None
else:
    try:
        client = MongoClient(mongo_uri, maxPoolSize=50, minPoolSize=10, serverSelectionTimeoutMS=1000, connectTimeoutMS=1000, socketTimeoutMS=1000)
        db = client['customer360']

        # Create indexes for faster queries
        db.user_profiles.create_index([("total_spent", -1)])
        db.user_profiles.create_index([("total_events", 1)])
        db.user_profiles.create_index([("avg_order_value", -1)])
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        client = None
        db = None

# Cache metrics for 5 seconds to reduce database load
metrics_cache = {'data': None, 'time': 0}
CACHE_TTL = 5

def get_cached_metrics():
    """Get metrics with caching to prevent lag"""
    # Return mock data if no database connection
    if db is None:
        return {
            'total_users': 1250,
            'total_revenue': 45678.90,
            'avg_order': 89.50,
            'max_revenue': 2500.00,
            'min_revenue': 15.99
        }

    current_time = time.time()

    if metrics_cache['data'] and (current_time - metrics_cache['time']) < CACHE_TTL:
        return metrics_cache['data']

    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "total_users": {"$sum": 1},
                "total_revenue": {"$sum": "$total_spent"},
                "avg_order": {"$avg": "$avg_order_value"},
                "max_revenue": {"$max": "$total_spent"},
                "min_revenue": {"$min": "$total_spent"}
            }}
        ]

        metrics_result = list(db.user_profiles.aggregate(pipeline))
        metrics = metrics_result[0] if metrics_result else {
            'total_users': 0, 'total_revenue': 0, 'avg_order': 0,
            'max_revenue': 0, 'min_revenue': 0
        }

        metrics_cache['data'] = metrics
        metrics_cache['time'] = current_time
        return metrics
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return {'total_users': 0, 'total_revenue': 0, 'avg_order': 0}

@app.route('/')
def dashboard():
    """Main dashboard with optimized loading"""
    metrics = get_cached_metrics()

    # Mock data for deployment without database
    if db is None:
        labels = ['user_1', 'user_2', 'user_3', 'user_4', 'user_5', 'user_6', 'user_7', 'user_8', 'user_9', 'user_10']
        values = [2500, 2100, 1800, 1650, 1400, 1200, 1100, 950, 800, 700]
    else:
        try:
            # Get top users with limit (faster than full sort)
            top_users = list(db.user_profiles.find(
                {},
                {'user_id': 1, 'total_spent': 1}
            ).sort("total_spent", -1).limit(10))
            labels = [u['user_id'] for u in top_users]
            values = [u.get('total_spent', 0) for u in top_users]
        except:
            labels = []
            values = []

    return render_template_string(TEMPLATE,
                                  metrics=metrics,
                                  labels=labels,
                                  values=values)

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for real-time metrics updates"""
    metrics = get_cached_metrics()
    return jsonify(metrics)

@app.route('/api/top-users')
def api_top_users():
    """API endpoint for top users"""
    if db is None:
        # Return mock data for deployment
        return jsonify([
            {'user_id': f'user_{i}', 'total_spent': 2500 - i*200, 'total_events': 50 - i}
            for i in range(1, 16)
        ])

    try:
        top_users = list(db.user_profiles.find(
            {},
            {'user_id': 1, 'total_spent': 1, 'total_events': 1}
        ).sort("total_spent", -1).limit(15))
        return jsonify(top_users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Advanced statistics"""
    if db is None:
        # Return mock data for deployment
        return jsonify({
            "revenue_distribution": [{"high_value": 120, "medium_value": 150, "low_value": 200}],
            "engagement_distribution": [{"highly_engaged": 80, "moderately_engaged": 120, "low_engagement": 270}]
        })

    try:
        pipeline = [
            {"$facet": {
                "revenue_distribution": [
                    {"$group": {
                        "_id": None,
                        "high_value": {"$sum": {"$cond": [{"$gte": ["$total_spent", 1000]}, 1, 0]}},
                        "medium_value": {"$sum": {"$cond": [{"$and": [{"$gte": ["$total_spent", 500]}, {"$lt": ["$total_spent", 1000]}]}, 1, 0]}},
                        "low_value": {"$sum": {"$cond": [{"$lt": ["$total_spent", 500]}, 1, 0]}}
                    }}
                ],
                "engagement_distribution": [
                    {"$group": {
                        "_id": None,
                        "highly_engaged": {"$sum": {"$cond": [{"$gte": ["$total_events", 50]}, 1, 0]}},
                        "moderately_engaged": {"$sum": {"$cond": [{"$and": [{"$gte": ["$total_events", 20]}, {"$lt": ["$total_events", 50]}]}, 1, 0]}},
                        "low_engagement": {"$sum": {"$cond": [{"$lt": ["$total_events", 20]}, 1, 0]}}
                    }}
                ]
            }}
        ]

        result = list(db.user_profiles.aggregate(pipeline))
        return jsonify(result[0] if result else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer 360 Analytics - Enterprise Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ============ NAVBAR ============ */
        .navbar {
            background: rgba(15, 15, 30, 0.95);
            backdrop-filter: blur(10px);
            padding: 1.2rem 2.5rem;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
            border-bottom: 2px solid rgba(229, 9, 20, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .navbar-brand h1 {
            color: #e50914;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -1px;
            text-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
        }

        .navbar-status {
            display: flex;
            gap: 12px;
            align-items: center;
            font-size: 0.85rem;
            color: #b3b3b3;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background: #51cf66;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* ============ HERO ============ */
        .hero {
            background: linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(30,30,50,0.6) 100%);
            padding: 140px 2.5rem 60px;
            text-align: center;
            position: relative;
            overflow: hidden;
            margin-top: 80px;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(229,9,20,0.1) 0%, transparent 70%);
            animation: gradientShift 15s ease infinite;
        }

        @keyframes gradientShift {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(100px, 100px); }
        }

        .hero h1 {
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #ffffff, #e50914, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            position: relative;
            z-index: 2;
        }

        .hero p {
            font-size: 1.3rem;
            color: #a0a0a0;
            margin-bottom: 2rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            line-height: 1.6;
        }

        /* ============ METRICS GRID ============ */
        .metrics-section {
            padding: 4rem 2.5rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .metric-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
            border: 1px solid rgba(229, 9, 20, 0.2);
            border-radius: 16px;
            padding: 2.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .metric-card:hover {
            transform: translateY(-8px);
            border-color: rgba(229, 9, 20, 0.5);
            background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.06) 100%);
            box-shadow: 0 20px 40px rgba(229, 9, 20, 0.2);
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, #e50914, transparent);
        }

        .metric-icon {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #e50914, #ff6b6b);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2rem;
            box-shadow: 0 10px 30px rgba(229, 9, 20, 0.4);
        }

        .metric-title {
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
        }

        .metric-value {
            font-size: 2.8rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 20px rgba(229, 9, 20, 0.3);
        }

        .metric-subtitle {
            color: #666;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }

        .metric-trend {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: #51cf66;
        }

        /* ============ CHARTS SECTION ============ */
        .charts-section {
            padding: 4rem 2.5rem;
            background: rgba(0, 0, 0, 0.4);
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .chart-container {
            background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
            border: 1px solid rgba(229, 9, 20, 0.2);
            border-radius: 16px;
            padding: 2.5rem;
            position: relative;
        }

        .chart-title {
            font-size: 1.4rem;
            margin-bottom: 2rem;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chart-icon {
            font-size: 1.8rem;
        }

        .chart-wrapper {
            position: relative;
            height: 350px;
        }

        /* ============ STATS CARDS ============ */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 3rem;
        }

        .stat-mini {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(229, 9, 20, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }

        .stat-mini-label {
            color: #888;
            font-size: 0.85rem;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
            letter-spacing: 0.5px;
        }

        .stat-mini-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #e50914;
        }

        /* ============ FOOTER ============ */
        .footer {
            text-align: center;
            padding: 3rem 2rem;
            color: #555;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(0, 0, 0, 0.8);
        }

        .footer p {
            margin-bottom: 0.5rem;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .footer-links a {
            color: #888;
            text-decoration: none;
            transition: color 0.3s;
        }

        .footer-links a:hover {
            color: #e50914;
        }

        /* ============ RESPONSIVE ============ */
        @media (max-width: 1024px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }

            .hero h1 {
                font-size: 3rem;
            }
        }

        @media (max-width: 768px) {
            .navbar {
                padding: 1rem 1.5rem;
                flex-direction: column;
                gap: 1rem;
            }

            .hero {
                padding: 120px 1.5rem 40px;
            }

            .hero h1 {
                font-size: 2.2rem;
            }

            .hero p {
                font-size: 1rem;
            }

            .metrics-section {
                padding: 2rem 1.5rem;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }

            .metric-card {
                padding: 1.5rem;
            }

            .metric-value {
                font-size: 2rem;
            }

            .charts-section {
                padding: 2rem 1.5rem;
            }

            .chart-container {
                padding: 1.5rem;
            }

            .chart-wrapper {
                height: 250px;
            }
        }

        /* ============ LOADING ANIMATION ============ */
        .skeleton {
            background: linear-gradient(90deg, rgba(255,255,255,0.1) 25%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }

        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-brand">
            <h1>📊 Customer 360</h1>
        </div>
        <div class="navbar-status">
            <div class="status-dot"></div>
            <span>Live • Real-time Analytics</span>
        </div>
    </nav>

    <section class="hero">
        <h1>Enterprise Analytics Dashboard</h1>
        <p>Real-time insights powered by Apache Kafka, Spark, and MongoDB. Making data-driven decisions at scale.</p>
    </section>

    <section class="metrics-section">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-title">Total Users</div>
                <div class="metric-value">{{ "{:,}".format(metrics.total_users) }}</div>
                <div class="metric-subtitle">Active subscribers</div>
                <div class="metric-trend">
                    <span>↑ 12% this month</span>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-title">Total Revenue</div>
                <div class="metric-value">${{ "{:,.0f}".format(metrics.total_revenue) }}</div>
                <div class="metric-subtitle">Lifetime value</div>
                <div class="metric-trend">
                    <span>↑ 8% this month</span>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-title">Avg Order Value</div>
                <div class="metric-value">${{ "%.2f"|format(metrics.avg_order) }}</div>
                <div class="metric-subtitle">Per transaction</div>
                <div class="metric-trend">
                    <span>↑ 3% this month</span>
                </div>
            </div>
        </div>
    </section>

    <section class="charts-section">
        <div class="charts-grid">
            <div class="chart-container">
                <h3 class="chart-title">
                    <span class="chart-icon">📊</span>
                    Top 10 Customers by Revenue
                </h3>
                <div class="chart-wrapper">
                    <canvas id="revenueChart"></canvas>
                </div>
            </div>

            <div class="chart-container">
                <h3 class="chart-title">
                    <span class="chart-icon">🎯</span>
                    Customer Segmentation
                </h3>
                <div class="chart-wrapper">
                    <canvas id="segmentChart"></canvas>
                </div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-mini">
                <div class="stat-mini-label">High Value Customers</div>
                <div class="stat-mini-value" id="highValue">--</div>
            </div>
            <div class="stat-mini">
                <div class="stat-mini-label">Medium Value Customers</div>
                <div class="stat-mini-value" id="medValue">--</div>
            </div>
            <div class="stat-mini">
                <div class="stat-mini-label">Low Value Customers</div>
                <div class="stat-mini-value" id="lowValue">--</div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <p>&copy; 2025 Customer 360 Analytics Platform</p>
        <p style="font-size: 0.85rem; color: #666;">Built with Apache Kafka • Apache Spark • MongoDB • Flask</p>
        <div class="footer-links">
            <a href="#">API Docs</a>
            <a href="#">Contact</a>
            <a href="#">Privacy</a>
        </div>
    </footer>

    <script>
        // Chart configurations
        const chartConfig = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e0e0e0', font: { size: 12, family: 'Inter' } }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888', font: { size: 11 } }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#888', font: { size: 11 } }
                }
            }
        };

        // Revenue Chart
        const revenueCtx = document.getElementById('revenueChart');
        const revenueChart = new Chart(revenueCtx, {
            type: 'bar',
            data: {
                labels: {{ labels|tojson }},
                datasets: [{
                    label: 'Total Spent ($)',
                    data: {{ values|tojson }},
                    backgroundColor: 'rgba(229, 9, 20, 0.7)',
                    borderColor: '#e50914',
                    borderWidth: 2,
                    borderRadius: 8,
                    hoverBackgroundColor: 'rgba(229, 9, 20, 1)',
                }]
            },
            options: {
                ...chartConfig,
                animation: { duration: 1200, easing: 'easeOutQuart' }
            }
        });

        // Load stats
        axios.get('/api/stats')
            .then(response => {
                const data = response.data;
                if (data.revenue_distribution && data.revenue_distribution[0]) {
                    const dist = data.revenue_distribution[0];
                    document.getElementById('highValue').textContent = dist.high_value || 0;
                    document.getElementById('medValue').textContent = dist.medium_value || 0;
                    document.getElementById('lowValue').textContent = dist.low_value || 0;
                }
            })
            .catch(e => console.error('Error loading stats:', e));

        // Segment Chart
        const segmentCtx = document.getElementById('segmentChart');
        const segmentChart = new Chart(segmentCtx, {
            type: 'doughnut',
            data: {
                labels: ['High Value (>$1K)', 'Medium Value ($500-$1K)', 'Low Value (<$500)'],
                datasets: [{
                    data: [120, 150, 200],
                    backgroundColor: [
                        'rgba(229, 9, 20, 0.8)',
                        'rgba(255, 107, 107, 0.7)',
                        'rgba(255, 152, 0, 0.7)'
                    ],
                    borderColor: ['#e50914', '#ff6b6b', '#ff9800'],
                    borderWidth: 2
                }]
            },
            options: {
                ...chartConfig,
                plugins: {
                    ...chartConfig.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + ' users';
                            }
                        }
                    }
                }
            }
        });

        // Auto-refresh metrics every 10 seconds
        setInterval(() => {
            axios.get('/api/metrics')
                .then(response => {
                    console.log('Metrics updated:', response.data);
                })
                .catch(e => console.error('Error refreshing metrics:', e));
        }, 10000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
