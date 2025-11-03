from kafka import KafkaProducer
import json
import random
from datetime import datetime
import time

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Netflix genres
GENRES = ['Action', 'Drama', 'Comedy', 'Sci-Fi', 'Horror', 'Romance', 'Thriller']
REGIONS = ['US', 'IN', 'UK', 'BR', 'MX', 'CA', 'AU', 'JP']

print("Starting Netflix subscriber event generation... Press Ctrl+C to stop")

user_id = 0
while True:
    user_id += 1
    
    # Simulate Netflix watching events
    event = {
        'user_id': f'subscriber_{user_id % 500}',
        'event_type': random.choice(['watch', 'pause', 'rewatch', 'add_to_list']),
        'timestamp': datetime.now().isoformat(),
        'genre': random.choice(GENRES),
        'watch_minutes': random.randint(5, 300),
        'subscription_tier': random.choice(['Basic', 'Standard', 'Premium']),
        'region': random.choice(REGIONS),
        'revenue': round(random.uniform(0.99, 19.99), 2)  # Netflix revenue
    }
    
    producer.send('netflix_events', event)
    print(f"Event {user_id}: {event['user_id']} watched {event['genre']}")
    
    time.sleep(0.15)  # 6-7 events per second
