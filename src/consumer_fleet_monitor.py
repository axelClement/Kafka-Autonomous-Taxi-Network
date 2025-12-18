import json
import os
from kafka import KafkaConsumer
from pathlib import Path
from datetime import datetime

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
VEHICLE_TOPIC = "vehicle-status"
RIDE_TOPIC = "ride-events"

STATE_FILE = Path(__file__).resolve().parents[1] / "data" / "fleet_state.json"

# Thresholds (should match producer)
SPEED_LIMIT = 110
LOW_BATTERY_LIMIT = 20

fleet_state = {}


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


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
            data = message.value

            if message.topic == VEHICLE_TOPIC:
                handle_vehicle_status(data)
            elif message.topic == RIDE_TOPIC:
                handle_ride_event(data)

    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()


def handle_vehicle_status(data):
    car_id = data.get("car_id")
    if not car_id:
        print("  ⚠ Invalid vehicle message (missing car_id):", data)
        return

    # Raw values
    speed_raw = data.get("speed")
    battery_raw = data.get("battery")
    temp = data.get("temperature")
    lat = data.get("lat")
    lon = data.get("lon")

    # Safe numeric versions (never crash)
    speed = safe_float(speed_raw)
    battery = safe_float(battery_raw)

    # Prefer statuses coming from producer, otherwise compute here
    speed_status = data.get("speed_status")
    battery_status = data.get("battery_status")

    # Fallback computation if producer didn't send them (safe)
    if speed_status is None:
        speed_status = "OVERSPEED" if (speed is not None and speed > SPEED_LIMIT) else "OK"
    if battery_status is None:
        battery_status = "LOW_BATTERY" if (battery is not None and battery < LOW_BATTERY_LIMIT) else "OK"

    print(
        f"[VEHICLE] Car {car_id} | "
        f"speed={speed} km/h ({speed_status}) | "
        f"battery={battery}% ({battery_status}) | "
        f"temp={temp}°C | lat={lat}, lon={lon}"
    )

    # Alerts (independent)
    if battery_status == "LOW_BATTERY":
        print(f"  ⚠ ALERT: Low battery for {car_id} ({battery}%)")
    if speed_status == "OVERSPEED":
        print(f"  ⚠ ALERT: Overspeed detected for {car_id} ({speed} km/h)")

    # Persist state for dashboard
    fleet_state[car_id] = {
        "lat": lat,
        "lon": lon,
        "speed": speed,
        "battery": battery,
        "temperature": temp,
        "speed_status": speed_status,
        "battery_status": battery_status,
        "last_update": datetime.utcnow().isoformat()
    }

    write_fleet_state()


def handle_ride_event(data):
    car_id = data.get("car_id")
    user_id = data.get("user_id")
    event = data.get("event")
    ts = data.get("timestamp")

    print(f"[RIDE] Car {car_id}, User {user_id}, Event={event}, Time={ts}")


def write_fleet_state():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(fleet_state, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
