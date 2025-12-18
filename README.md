# Real-Time Autonomous Taxi Network with Apache Kafka

## 1. Project Overview

This project demonstrates a **real-time Big Data streaming architecture** using **Apache Kafka** to simulate an **autonomous taxi fleet** operating in a smart city environment.

Each autonomous taxi continuously sends:
- **Vehicle telemetry data** (speed, battery level, temperature, GPS position)
- **User ride events** (ride requested, started, canceled, finished)

Apache Kafka acts as the **central event streaming platform**, enabling real-time ingestion and processing of these events.  
A **fleet monitoring service** consumes the data to display vehicle status and detect simple anomalies such as overspeeding or low battery.

The objective of this project is to illustrate:
- event-driven architectures
- producer–consumer communication
- real-time data streaming
- how Kafka fits into a Big Data ecosystem


## 2. Why Apache Kafka?

Apache Kafka was chosen because:

- It is widely used in industry for **real-time data streaming**
- It is designed for **high-throughput, low-latency event ingestion**
- It decouples data producers from consumers
- It scales naturally to large fleets and data volumes
- It is commonly used in mobility, IoT, and smart city systems

Kafka is particularly well-suited for autonomous vehicle platforms, where large amounts of telemetry and user interaction data must be processed in real time.



## 3. Use Case: Autonomous Taxi Fleet

In this simulated scenario:

- Each **autonomous taxi** behaves as a Kafka **producer**
- Each taxi periodically sends **vehicle status updates**
- User interactions with taxis generate **ride events**
- A centralized **fleet monitoring service** consumes and processes the data

### Kafka Topics

- `vehicle-status`  
  Stores telemetry data from autonomous taxis (speed, battery, GPS, temperature)

- `ride-events`  
  Stores user-related ride events (request, start, cancel, finish)

---

## 4. System Architecture

High-level architecture:

```
+---------------------------+
| Autonomous Taxis          |
| (Kafka Producers)         |
|                           |
| - Vehicle telemetry       |
|   (speed, battery, GPS)   |
| - Ride events             |
|   (start, stop, cancel)   |
+-------------+-------------+
              |
              v
+---------------------------+
| Apache Kafka (KRaft mode) |
|                           |
| Topics:                   |
| - vehicle-status          |
| - ride-events             |
+-------------+-------------+
              |
              v
+---------------------------+
| Fleet Monitoring Service  |
| (Kafka Consumer)          |
|                           |
| - Real-time logs          |
| - Alerts (battery/speed)  |
+---------------------------+
```

Kafka is deployed using the **official `apache/kafka` Docker image** in **KRaft mode**, without ZooKeeper.

## 5. Technologies Used

- Apache Kafka (KRaft mode)
- Docker & Docker Compose
- Python 3.11
- kafka-python library
- Kafka UI (Provectus)

## 6. Installation and Setup

### 6.1 Prerequisites

- Docker and Docker Compose
- Python 3.11

### 6.2 Clone Repository

```bash
git clone https://github.com/axelClement/Kafka-Autonomous-Taxi-Network.git
cd Kafka-Autonomous-Taxi-Network
```

## 7. Running the Project

You can run the project in two ways:
- **Option A (Recommended):** Run everything (Kafka, Producer, Consumer, Dashboard) in Docker containers.
- **Option B (Manual):** Run Kafka in Docker, but run the Python scripts locally on your machine.

### 7.1 Option A: Full Docker Deployment

This method starts all components automatically.

1. **Start the services:**

   ```bash
   docker-compose up --build
   ```

2. **Access the services:**

   - **Kafka UI:** [http://localhost:8080](http://localhost:8080)
   - **Streamlit Dashboard:** [http://localhost:8501](http://localhost:8501)

3. **View Logs:**

   - Producer: `docker logs -f taxi-producer`
   - Consumer: `docker logs -f fleet-monitor`

### 7.2 Option B: Manual Execution (Hybrid)

Use this method if you want to develop or debug the Python scripts locally.

#### Step 1: Environment Setup

Create and activate a virtual environment, then install dependencies.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

#### Step 2: Start Infrastructure

Start only the Kafka broker and Kafka UI.

```bash
docker-compose up -d kafka kafka-ui
```

- **Kafka UI:** [http://localhost:8080](http://localhost:8080)

#### Step 3: Start the Consumer

In a new terminal:

```bash
.\.venv\Scripts\python.exe src\consumer_fleet_monitor.py
```

Expected output:
```
Fleet Monitoring Consumer started...
```

#### Step 4: Start the Producer

In a separate terminal:

```bash
.\.venv\Scripts\python.exe src\producer_taxi.py
```

Example producer output:
```
[VEHICLE] Sent {...}
[RIDE] Sent {...}
```

#### Step 5: Start the Dashboard

In a third terminal:

```bash
streamlit run src/dashboard_map.py
```

- **Streamlit Dashboard:** [http://localhost:8501](http://localhost:8501)

Example consumer output:

```
[VEHICLE] TX-102 | speed=115.2 | battery=18
⚠ Overspeed alert for TX-102
⚠ Low battery alert for TX-102
[RIDE] TX-101 - U-203 - ride_started @ 2025-11-25T20:18:02Z
```

## 8. Monitoring with Kafka UI

Kafka UI is used to visualize:

- existing topics
- incoming messages
- consumer activity

**Steps:**

1. Open http://localhost:8080
2. Select the cluster autonomous-taxi-cluster
3. Navigate to Topics
4. View messages in vehicle-status and ride-events

Kafka UI provides visual confirmation that the streaming pipeline is working correctly.

## 9. Real-Time Fleet Visualization (Live Map Dashboard)

In addition to console-based monitoring, the project includes a **real-time fleet visualization dashboard** that displays the live positions of autonomous taxis on a map.

The fleet monitoring consumer maintains an in-memory state of the latest telemetry received for each vehicle, including:
- GPS position (latitude, longitude)
- speed
- battery level
- operational status (OK, OVERSPEED, LOW_BATTERY)

This state is continuously persisted to a local file (`fleet_state.json`), which acts as a lightweight representation of a **real-time operational data store**.

A separate **Streamlit dashboard** reads this state and renders a **live map of the fleet**, refreshing automatically every two seconds.

### Live Map Features

- Real-time display of taxi positions on an OpenStreetMap background
- Automatic refresh every 2 seconds
- Large, clearly visible markers for each taxi
- Color-coded markers based on vehicle status:
  - OK
  - OVERSPEED
  - LOW_BATTERY
- Interactive tooltips showing speed, battery level, and last update timestamp

### Running the Live Map Dashboard

In a third terminal, run:

```bash
streamlit run src/dashboard_map.py
```

## 10. Challenges Encountered and Solutions

### Python Version Compatibility

We encountered issues running the Kafka consumer due to incompatibility between Python 3.12 and the kafka-python library.

**Solution:** We downgraded to Python 3.11, which is officially supported by kafka-python.

### Interpreter Mismatch Between VS Code and Terminal

The application worked in VS Code but not in a standard terminal due to different Python interpreters being used.

**Solution:** We explicitly activated the virtual environment and executed scripts using the virtual environment's Python executable.

## 11. My Setup Notes

This project highlighted the importance of:

- managing Python versions and virtual environments
- understanding Kafka networking in Docker
- using visualization tools like Kafka UI for debugging

Debugging these issues improved our understanding of real-world Big Data system setup and dependency management.

## 12. How Kafka Fits into a Big Data Ecosystem

In a real autonomous taxi platform, Kafka would act as the central streaming backbone, connecting:

- vehicles and mobile applications (data producers)
- real-time monitoring systems
- anomaly detection services
- billing and invoicing systems
- long-term storage systems (data lakes)
- machine learning pipelines

This project represents a simplified but realistic version of such an architecture.

## 13. Possible Extensions

- Persist events to a database or data lake
- Add real-time analytics with Kafka Streams or Spark Streaming
- Enhance the existing map dashboard with additional metrics and analytics
- Add anomaly detection or predictive maintenance models

## 14. Conclusion

This project demonstrates how Apache Kafka can be used to build a scalable, real-time data streaming system for autonomous vehicles.
By simulating vehicle telemetry and user ride events, we showcased Kafka’s role in modern Big Data architectures and event-driven systems.
