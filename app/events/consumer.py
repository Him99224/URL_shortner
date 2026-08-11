import json

from confluent_kafka import Consumer

from app.db.database import SessionLocal
from app.models import URL


consumer= Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "url_analytics",
    "auto.offset.reset": "earliest"
})

consumer.subscribe(["url_clicks"])

def process_click_event(event: dict) -> None:
    db = SessionLocal()

    try:
        short_code=event["short_code"]

        url=(db.query(URL).filter(URL.short_code==short_code).first())

        if url is None:
            print(f"No URL found for short code: {short_code}")
            return
        url.click_count += 1
        db.commit()

        print(f"Click event processed for short code: {short_code}. Updated click count: {url.click_count}")
    except Exception as e:
        db.rollback()
        print(f"Error processing click event: {e}")
    finally:
        db.close()

def run_consumer() -> None:
    print("Analytics consumer started. Listening for click events...")
    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            event = json.loads(msg.value().decode("utf-8"))
            try:
                process_click_event(event)
            except Exception as e:
                print(f"Error processing click event: {e}")
    except KeyboardInterrupt:
        print("Consumer interrupted by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()