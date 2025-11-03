from kafka import KafkaConsumer
import json
from pymongo import MongoClient
from datetime import datetime
import time

print("Connecting to MongoDB...")
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['netflix_analytics']
subscriber_collection = db['subscribers']

print("Connecting to Kafka...")
try:
    consumer = KafkaConsumer(
        'netflix_events',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='netflix-spark-group',
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000
    )
    
    print("Streaming query started. Writing to MongoDB...")
    
    subscriber_stats = {}
    batch_count = 0
    
    for message in consumer:
        try:
            event = message.value
            user_id = event.get('user_id')
            watch_minutes = event.get('watch_minutes')
            revenue = event.get('revenue')
            tier = event.get('subscription_tier')
            
            if user_id not in subscriber_stats:
                subscriber_stats[user_id] = {
                    'subscriber_id': user_id,
                    'total_watch_hours': 0.0,
                    'total_revenue': 0.0,
                    'total_events': 0,
                    'subscription_tier': tier,
                    'last_watched': datetime.now(),
                    'churn_risk': 'Low'
                }
            
            subscriber_stats[user_id]['total_watch_hours'] += watch_minutes / 60
            subscriber_stats[user_id]['total_revenue'] += revenue
            subscriber_stats[user_id]['total_events'] += 1
            
            # Calculate churn risk (low watch time = high risk)
            if subscriber_stats[user_id]['total_watch_hours'] < 5:
                subscriber_stats[user_id]['churn_risk'] = 'High'
            elif subscriber_stats[user_id]['total_watch_hours'] < 20:
                subscriber_stats[user_id]['churn_risk'] = 'Medium'
            else:
                subscriber_stats[user_id]['churn_risk'] = 'Low'
            
            batch_count += 1
            
            if batch_count % 10 == 0:
                for sid, stats in subscriber_stats.items():
                    subscriber_collection.update_one(
                        {'subscriber_id': sid},
                        {'$set': stats},
                        upsert=True
                    )
                print(f"Batch {batch_count}: Wrote {len(subscriber_stats)} subscriber profiles to MongoDB")
        
        except Exception as e:
            print(f"Error processing message: {e}")
            continue
    
except KeyboardInterrupt:
    print("\nStopping streaming...")
    consumer.close()
except Exception as e:
    print(f"Error: {e}")
