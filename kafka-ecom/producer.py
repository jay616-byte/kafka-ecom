import json
import random
import time
import uuid
from datetime import datetime
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = "host.docker.internal:29092"
TOPIC_NAME = "raw_events"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    key_serializer=lambda k: k.encode("utf-8") if k else None,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

EVENT_TYPES = ["PAGE_VIEW", "ADD_TO_CART", "PURCHASE"]
INVALID_EVENT_TYPES = ["CLICK", "VIEW", "PAY"]

def generate_event():
    is_invalid = random.random() < 0.25  # 25% invalid events

    customer_id = f"CUST_{random.randint(1, 5)}"
    event_type = random.choice(EVENT_TYPES)
    amount = round(random.uniform(10, 500), 2)
    currency = "USD"

    # Choose ONE column to corrupt if invalid
    invalid_field = None
    if is_invalid:
        invalid_field = random.choice([
            "customer_id",
            "event_type",
            "amount",
            "currency"
        ])

    event = {
        "event_id": str(uuid.uuid4()),
        "customer_id": None if invalid_field == "customer_id" else customer_id,
        "event_type": (
            random.choice(INVALID_EVENT_TYPES)
            if invalid_field == "event_type"
            else event_type
        ),
        "amount": (
            random.uniform(-500, -10)
            if invalid_field == "amount"
            else amount
        ),
        "currency": None if invalid_field == "currency" else currency,
        "event_timestamp": datetime.utcnow().isoformat(),
        "is_valid": not is_invalid,
        "invalid_field": invalid_field
    }

    return event["customer_id"], event


print("Starting Kafka event producer...")

while True:
    key, event = generate_event()

    producer.send(
        topic=TOPIC_NAME,
        key=key,
        value=event
    )

    print(f"Produced event | key={key} | valid={event['is_valid']}")

    time.sleep(1)

