import os
import json
import random
import time
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
project_id = os.environ.get('GCP_PROJECT')
topic_id = os.environ.get('PUBSUB_TOPIC', 'stock_prices')
topic_path = publisher.topic_path(project_id, topic_id)

stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

def publish_stock_data(request):
    record = {
        'symbol': random.choice(stocks),
        'price': round(random.uniform(100, 1500), 2),
        'timestamp': time.time()
    }
    data = json.dumps(record).encode('utf-8')
    publisher.publish(topic_path, data)
    return f"Published: {json.dumps(record)}\n"
