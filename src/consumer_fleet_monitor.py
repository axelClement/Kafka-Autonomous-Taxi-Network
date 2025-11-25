import json
from kafka import KafkaConsumer

BROKER = "localhost:9092"
VEHICLE_TOPIC = "vehicle-status"
RIDE_TOPIC = "ride-events"

def main():
  consumer = KafkaConsumer(
      VEHICLE_TOPIC,
      RIDE_TOPIC,
      bootstrap_servers=[BROKER],
      auto_offset_reset="earliest",
      enable_auto_commit=True,
      group_id="fleet-monitor",
      value_deserializer=lambda v: json.loads(v.decode("utf-8"))
  )

  print("Fleet Monitoring Consumer started... (Ctrl+C to stop)")

  try:
    for message in consumer:
      topic = message.topic
      data = message.value

      if topic == VEHICLE_TOPIC:
        handle_vehicle_status(data)
      elif topic == RIDE_TOPIC:
        handle_ride_event(data)

  except KeyboardInterrupt:
    print("Stopping consumer...")
  finally:
    consumer.close()

def handle_vehicle_status(data):
  car_id = data.get("car_id")
  speed = data.get("speed")
  battery = data.get("battery")
  temp = data.get("temperature")

  print(f"[VEHICLE] Car {car_id} | speed={speed} km/h | battery={battery}% | temp={temp}°C")

  if battery is not None and battery < 20:
    print(f"  ⚠ ALERT: Low battery for {car_id} ({battery}%)")

  if speed is not None and speed > 110:
    print(f"  ⚠ ALERT: Overspeed detected for {car_id} ({speed} km/h)")

def handle_ride_event(data):
  car_id = data.get("car_id")
  user_id = data.get("user_id")
  event = data.get("event")
  ts = data.get("timestamp")

  print(f"[RIDE] Car {car_id}, User {user_id}, Event={event}, Time={ts}")

if __name__ == "__main__":
  main()
