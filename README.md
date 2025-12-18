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

### 6.2 Clone Repository and Setup

### 6.3 Create and Activate Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 6.4 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 6.5 Start Kafka and Kafka UI

```bash
docker-compose up -d
```

**Verify containers:**

```bash
docker ps
```

Kafka UI will be available at:

## 7. Running the Minimal Working Example

### 7.1 Start the Consumer

In the first terminal:

```bash
.\.venv\Scripts\python.exe src\consumer_fleet_monitor.py
```

Expected output:

```
Fleet Monitoring Consumer started...
```

### 7.2 Start the Producer

In a second terminal:

```bash
.\.venv\Scripts\python.exe src\producer_taxi.py
```


Example producer output:

```
[VEHICLE] Sent {...}
[RIDE] Sent {...}
```

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

## 9. Challenges Encountered and Solutions

### Python Version Compatibility

We encountered issues running the Kafka consumer due to incompatibility between Python 3.12 and the kafka-python library.

**Solution:** We downgraded to Python 3.11, which is officially supported by kafka-python.

### Interpreter Mismatch Between VS Code and Terminal

The application worked in VS Code but not in a standard terminal due to different Python interpreters being used.

**Solution:** We explicitly activated the virtual environment and executed scripts using the virtual environment's Python executable.

## 10. My Setup Notes

This project highlighted the importance of:

- managing Python versions and virtual environments
- understanding Kafka networking in Docker
- using visualization tools like Kafka UI for debugging

Debugging these issues improved our understanding of real-world Big Data system setup and dependency management.

## 11. How Kafka Fits into a Big Data Ecosystem

In a real autonomous taxi platform, Kafka would act as the central streaming backbone, connecting:

- vehicles and mobile applications (data producers)
- real-time monitoring systems
- anomaly detection services
- billing and invoicing systems
- long-term storage systems (data lakes)
- machine learning pipelines

This project represents a simplified but realistic version of such an architecture.

## 12. Possible Extensions

- Persist events to a database or data lake
- Add real-time analytics with Kafka Streams or Spark Streaming
- Implement dashboards for fleet visualization
- Add anomaly detection or predictive maintenance models

## 13. Conclusion

This project demonstrates how Apache Kafka can be used to build a scalable, real-time data streaming system for autonomous vehicles.
By simulating vehicle telemetry and user ride events, we showcased Kafka’s role in modern Big Data architectures and event-driven systems.