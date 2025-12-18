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

CAR_IDS = [f"TX-{100 + i}" for i in range(1, 11)]
USERS = ["U-201", "U-202", "U-203", "U-204", "U-205"]
RIDE_EVENTS = ["ride_requested", "ride_started", "ride_canceled", "ride_finished"]

# Thresholds
SPEED_LIMIT = 30 # 30 km/h for Paris downtown
LOW_BATTERY_LIMIT = 20

# Base location (Paris)
BASE_LAT = 48.8566
BASE_LON = 2.3522


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()


class Taxi:
    def __init__(self, car_id, position_index, battery=None):
        self.car_id = car_id

        # Battery initialization (optionally force low battery for demo)
        self.battery = float(battery) if battery is not None else random.uniform(15.0, 100.0)

        # Start with some speed (km/h)
        self.speed = random.uniform(10.0, 30.0)

        # Spread initial positions around the base location
        angle = (position_index / len(CAR_IDS)) * 2 * math.pi
        radius = 0.01
        jitter = 0.001
        self.lat = BASE_LAT + radius * math.cos(angle) + random.uniform(-jitter, jitter)
        self.lon = BASE_LON + radius * math.sin(angle) + random.uniform(-jitter, jitter)

        # Random heading (0-360 degrees)
        self.heading = random.uniform(0, 360)

        # Temperature
        self.temperature = 20.0

    def update(self):
        # 1) Speed (smooth accel/decel)
        self.speed += random.uniform(-8, 8)
        self.speed = max(0, min(130, self.speed))  # allow OVERSPEED to happen

        # 2) Battery drain (depends on speed)
        drain = 0.01 + (self.speed / 130) * 0.10
        self.battery -= drain

        # Simple recharge to keep simulation running
        if self.battery < 5:
            self.battery = 100.0

        # 3) Temperature slight fluctuation
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(15, min(45, self.temperature))

        # 4) Position update (move according to speed & heading)
        dist_km = self.speed / 3600.0  # distance in 1 second

        rad = math.radians(self.heading)

        # Rough conversions around Paris
        # 1 deg lat ≈ 111 km; 1 deg lon ≈ 73 km near 48.8°N
        delta_lat = (dist_km / 111.0) * math.cos(rad)
        delta_lon = (dist_km / 73.0) * math.sin(rad)

        self.lat += delta_lat
        self.lon += delta_lon

        # 5) Heading changes slightly
        self.heading = (self.heading + random.uniform(-10, 10)) % 360

    def get_speed_status(self):
        return "OVERSPEED" if self.speed > SPEED_LIMIT else "OK"

    def get_battery_status(self):
        return "LOW_BATTERY" if self.battery < LOW_BATTERY_LIMIT else "OK"

    def to_dict(self):
        # IMPORTANT: use 'lat'/'lon' to match your consumer + dashboard
        return {
            "car_id": self.car_id,
            "speed": round(self.speed, 1),
            "battery": round(self.battery, 1),
            "temperature": int(round(self.temperature)),
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6),
            "speed_status": self.get_speed_status(),
            "battery_status": self.get_battery_status(),
            "timestamp": current_timestamp(),
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
            fleet.append(Taxi(car_id, position_index=i, battery=random.uniform(5.0, 19.0)))
        else:
            fleet.append(Taxi(car_id, position_index=i))

    try:
        while True:
            for taxi in fleet:
                taxi.update()
                msg = taxi.to_dict()

                producer.send(VEHICLE_TOPIC, msg)
                print(
                    f"[VEHICLE] {msg['car_id']} | "
                    f"Spd: {msg['speed']} ({msg['speed_status']}) | "
                    f"Bat: {msg['battery']}% ({msg['battery_status']})"
                )

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
