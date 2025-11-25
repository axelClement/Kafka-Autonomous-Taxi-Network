# Real-Time Autonomous Taxi Network with Apache Kafka

## 1. Project Description

This project simulates a **real-time data streaming architecture** for an autonomous taxi fleet using **Apache Kafka**.

Each taxi behaves like a Kafka producer, sending:
- **Vehicle telemetry** (speed, battery level, temperature, GPS location)
- **User ride events** (ride requested, started, canceled, finished)

A **Fleet Monitoring Service** acts as a Kafka consumer, reading events in real time and printing alerts when:
- a vehicle is overspeeding
- a vehicle battery is low

The goal is to demonstrate how Kafka can be used as a **central streaming backbone** in a Big Data ecosystem for mobility and smart city applications.

---

## 2. Why We Selected Kafka

We chose **Apache Kafka** because:

- It is widely used in production for **real-time streaming** (Uber, Lyft, Netflix, etc.)
- It is designed for **high-throughput, scalable event ingestion**
- It fits very well with our **autonomous taxi fleet use case**
- It allows us to demonstrate:
  - producers and consumers
  - topics and event streams
  - decoupling between data producers and processing services

---

## 3. Architecture

**High-level architecture:**

- **Producers**: simulated autonomous taxis sending JSON events
- **Kafka Cluster**: one broker + one Zookeeper (Docker)
- **Topics**:
  - `vehicle-status` — telemetry from vehicles
  - `ride-events` — user ride interactions
- **Consumer**: Fleet Monitoring Service that:
  - logs events
  - raises alerts for dangerous or abnormal situations

(Include your architecture diagram or ASCII diagram here.)

---

## 4. Installation and Setup

### 4.1 Prerequisites

- Docker and Docker Compose
- Python 3.x
- `pip` for installing Python packages

### 4.2 Clone the Repository

```bash
git clone https://github.com/axelClement/Kafka-Autonomous-Taxi-Network.git
cd kafka-autonomous-taxis
