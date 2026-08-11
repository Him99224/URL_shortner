import json

from confluent_kafka import Producer

producer = Producer({
    "bootstrap.servers": "localhost:9092"
})

def publish_click_event(short_code:str)-> None:
    event={
        "event_type": "url_clicked",
        "short_code": short_code
    }
    producer.produce("url_clicks",
                    key=short_code,
                    value= json.dumps(event)
                    )
    producer.flush()