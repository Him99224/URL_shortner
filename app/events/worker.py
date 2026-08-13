import threading

from app.events.producer import producer

stop_event=threading.Event()

def poll_kafka():
    while not stop_event.is_set():
        producer.poll(1)  # Trigger delivery report callbacks

def start_polling_worker():
    thread=threading.Thread(target=poll_kafka,daemon=True)
    thread.start()
