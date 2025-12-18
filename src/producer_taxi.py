import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

BROKER = "localhost:9092"  # if run inside docker network, use "kafka:9092"

VEHICLE_TOPIC = "vehicle-status"
RIDE_TOPIC = "ride-events"

cars = ["TX-101", "TX-102", "TX-103", "TX-104"]
users = ["U-201", "U-202", "U-203", "U-204", "U-205"]

ride_events = ["ride_requested", "ride_started", "ride_canceled", "ride_finished"]

# Simple coordinates around some city (e.g. Paris, Montreal, whatever you like)
base_lat = 48.8566
base_lon = 2.3522

def current_timestamp():
  return datetime.now(timezone.utc).isoformat()

def random_coordinates():
  # small random offset around the base location
  lat = base_lat + random.uniform(-0.01, 0.01)
  lon = base_lon + random.uniform(-0.01, 0.01)
  return round(lat, 6), round(lon, 6)

def generate_vehicle_status():
  car_id = random.choice(cars)
  speed = round(random.uniform(0, 120), 1)      # km/h
  battery = random.randint(10, 100)             # %
  temperature = random.randint(15, 40)          # °C
  lat, lon = random_coordinates()

  return {
    "car_id": car_id,
    "speed": speed,
    "battery": battery,
    "temperature": temperature,
    "lat": lat,
    "lon": lon,
    "timestamp": current_timestamp()
}


def generate_ride_event():
  car_id = random.choice(cars)
  user_id = random.choice(users)
  event = random.choice(ride_events)

  return {
      "car_id": car_id,
      "user_id": user_id,
      "event": event,
      "pickup": "Some pickup location",
      "destination": "Some destination",
      "timestamp": current_timestamp()
  }

def main():
  producer = KafkaProducer(
      bootstrap_servers=[BROKER],
      value_serializer=lambda v: json.dumps(v).encode("utf-8")
  )

  print("Starting autonomous taxi producer... (Ctrl+C to stop)")

  try:
    while True:
      # Send vehicle status every loop
      vehicle_msg = generate_vehicle_status()
      producer.send(VEHICLE_TOPIC, vehicle_msg)
      print(f"[VEHICLE] Sent: {vehicle_msg}")

      # Sometimes also send a ride event
      if random.random() < 0.3:  # 30% chance
        ride_msg = generate_ride_event()
        producer.send(RIDE_TOPIC, ride_msg)
        print(f"[RIDE] Sent: {ride_msg}")

      # flush to ensure messages are delivered regularly
      producer.flush()

      # wait 1 second before next iteration
      time.sleep(1.0)

  except KeyboardInterrupt:
    print("Stopping producer...")
  finally:
    producer.close()

if __name__ == "__main__":
  main()
