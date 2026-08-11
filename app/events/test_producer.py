from app.events.producer import publish_click_event

publish_click_event("abc123")
print("Event published successfully.")