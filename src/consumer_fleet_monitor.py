import json
import os
from kafka import KafkaConsumer
from pathlib import Path
from datetime import datetime


BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
VEHICLE_TOPIC = "vehicle-status"
RIDE_TOPIC = "ride-events"


STATE_FILE = Path(__file__).resolve().parents[1] / "data" / "fleet_state.json"


fleet_state = {}


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

    lat = data.get("lat")
    lon = data.get("lon")

    status = "OK"

    print(
        f"[VEHICLE] Car {car_id} | "
        f"speed={speed} km/h | battery={battery}% | temp={temp}°C | "
        f"lat={lat}, lon={lon}"
    )

    if battery is not None and battery < 20:
        status = "LOW_BATTERY"
        print(f"  ⚠ ALERT: Low battery for {car_id} ({battery}%)")

    if speed is not None and speed > 110:
        status = "OVERSPEED"
        print(f"  ⚠ ALERT: Overspeed detected for {car_id} ({speed} km/h)")


    fleet_state[car_id] = {
        "lat": lat,
        "lon": lon,
        "speed": speed,
        "battery": battery,
        "temperature": temp,
        "status": status,
        "last_update": datetime.utcnow().isoformat()
    }

    write_fleet_state()

  if speed is not None and speed > 30:
    print(f"  ⚠ ALERT: Overspeed detected for {car_id} ({speed} km/h)")

def handle_ride_event(data):
    car_id = data.get("car_id")
    user_id = data.get("user_id")
    event = data.get("event")
    ts = data.get("timestamp")

    print(f"[RIDE] Car {car_id}, User {user_id}, Event={event}, Time={ts}")


def write_fleet_state():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(fleet_state, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
