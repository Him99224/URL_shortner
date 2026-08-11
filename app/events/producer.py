import json

from confluent_kafka import Producer

from app.core.config import settings

producer = Producer({
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS
})

def publish_click_event(short_code:str)-> None:
    event={
        "event_type": "url_clicked",
        "short_code": short_code
    }
    producer.produce(settings.KAFKA_CLICK_TOPIC,
                    key=short_code,
                    value= json.dumps(event)
                    )
    producer.flush()