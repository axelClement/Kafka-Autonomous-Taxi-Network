import json
import random
import time
import os
import math
from datetime import datetime, timezone

from kafka import KafkaProducer

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

VEHICLE_TOPIC = "vehicle-status"
RIDE_TOPIC = "ride-events"

CAR_IDS = ["TX-101", "TX-102", "TX-103", "TX-104"]
USERS = ["U-201", "U-202", "U-203", "U-204", "U-205"]
RIDE_EVENTS = ["ride_requested", "ride_started", "ride_canceled", "ride_finished"]

# Base location (Paris)
BASE_LAT = 48.8566
BASE_LON = 2.3522

def current_timestamp():
    return datetime.now(timezone.utc).isoformat()

class Taxi:
    def __init__(self, car_id, battery=None):
        self.car_id = car_id
        # Initialize with random battery to simulate some cars having low battery
        if battery is not None:
            self.battery = battery
        else:
            self.battery = random.uniform(15.0, 100.0)
        # Start with some speed
        self.speed = random.uniform(10.0, 30.0)
        # Start near base location
        self.lat = BASE_LAT + random.uniform(-0.01, 0.01)
        self.lon = BASE_LON + random.uniform(-0.01, 0.01)
        # Random heading (0-360 degrees)
        self.heading = random.uniform(0, 360)
        self.temperature = 20.0

    def update(self):
        # 1. Update Speed (smooth acceleration/deceleration)
        # Change speed by -5 to +5 km/h
        delta_speed = random.uniform(-5, 5)
        self.speed += delta_speed
        # Clamp speed between 0 and 50 km/h (City driving)
        self.speed = max(0, min(50, self.speed))

        # 2. Update Battery
        # Drain depends on speed. Idle drain + movement drain.
        # Adjusted for lower max speed (50km/h)
        drain = 0.005 + (self.speed / 50) * 0.05
        self.battery -= drain
        
        # Simulate charging if low (magic instant charge for simulation continuity)
        if self.battery < 5:
            self.battery = 100.0
        
        # 3. Update Temperature (fluctuate slightly)
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(15, min(45, self.temperature))

        # 4. Update Position
        # Distance traveled in 1 second (km)
        dist_km = (self.speed) / 3600.0
        
        # Convert heading to radians
        rad_heading = math.radians(self.heading)
        
        # 1 deg lat ~= 111 km
        # 1 deg lon ~= 111 km * cos(lat) ~= 73 km at 48 deg lat
        delta_lat = (dist_km / 111.0) * math.cos(rad_heading)
        delta_lon = (dist_km / 73.0) * math.sin(rad_heading)
        
        self.lat += delta_lat
        self.lon += delta_lon

        # 5. Update Heading (steer slightly)
        # Change heading by -10 to +10 degrees
        self.heading += random.uniform(-10, 10)
        self.heading %= 360

    def to_dict(self):
        return {
            "car_id": self.car_id,
            "speed": round(self.speed, 1),
            "battery": round(self.battery, 1),
            "temperature": int(self.temperature),
            "latitude": round(self.lat, 6),
            "longitude": round(self.lon, 6),
            "timestamp": current_timestamp()
        }

def generate_ride_event():
    car_id = random.choice(CAR_IDS)
    user_id = random.choice(USERS)
    event = random.choice(RIDE_EVENTS)

    return {
        "car_id": car_id,
        "user_id": user_id,
        "event": event,
        "pickup": "Some pickup location",
        "destination": "Some destination",
        "timestamp": current_timestamp()
    }

def main():
    # Wait for Kafka to be ready (simple retry logic could be added here, 
    # but docker restart policy handles it usually)
    print("Connecting to Kafka...")
    producer = KafkaProducer(
        bootstrap_servers=[BROKER],
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    print("Starting autonomous taxi producer... (Ctrl+C to stop)")
    
    # Initialize fleet
    fleet = []
    for i, car_id in enumerate(CAR_IDS):
        if i == 0:
            # Force one car to start with low battery (< 20%)
            fleet.append(Taxi(car_id, battery=random.uniform(5.0, 19.0)))
        else:
            fleet.append(Taxi(car_id))

    try:
        while True:
            for taxi in fleet:
                # Update state
                taxi.update()
                
                # Send vehicle status
                msg = taxi.to_dict()
                producer.send(VEHICLE_TOPIC, msg)
                print(f"[VEHICLE] Sent: {msg['car_id']} | Bat: {msg['battery']}% | Spd: {msg['speed']} km/h")

            # Randomly send a ride event
            if random.random() < 0.3:
                ride_msg = generate_ride_event()
                producer.send(RIDE_TOPIC, ride_msg)
                print(f"[RIDE]    Sent: {ride_msg}")

            producer.flush()
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()