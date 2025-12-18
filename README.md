# Real-Time Autonomous Taxi Network: A Distributed Streaming Architecture with Apache Kafka

## 1. Project Overview

This project presents a comprehensive implementation of a **Real-Time Big Data Streaming Architecture**, designed to simulate and manage a network of **autonomous taxis** within a smart city environment.

In the rapidly evolving domain of Intelligent Transportation Systems (ITS), the ability to ingest, process, and visualize high-velocity sensor data is paramount. This project addresses that challenge by simulating a fleet of autonomous agents that continuously emit heterogeneous data streams:

* **Telemetry Data:** High-frequency operational metrics including instantaneous velocity, State of Charge (SoC), internal temperature, and geospatial coordinates (GPS).
* **Transactional Events:** Discrete, state-changing events representing the lifecycle of user interactions (Ride Requested \rightarrow Started \rightarrow Completed).

**Apache Kafka** serves as the central nervous system of this architecture, functioning as a distributed event streaming platform that ensures fault-tolerant, low-latency data ingestion. A dedicated **Fleet Monitoring Service** consumes these streams to construct a materialized view of the fleet's state, enabling real-time anomaly detection (e.g., safety violations or critical energy levels).

The primary pedagogical and technical objective is to demonstrate the efficacy of **Event-Driven Architectures (EDA)** in modern software engineering, specifically illustrating:

* The decoupling of high-throughput producers from downstream consumers.
* The mechanics of stream-to-state transformation.
* The integration of Kafka within a broader Big Data and IoT ecosystem.

---

## 2. Why Apache Kafka?

The selection of Apache Kafka as the backbone for this architecture is driven by its unique design characteristics that distinguish it from traditional message queues (e.g., RabbitMQ or ActiveMQ).

### 2.1 Throughput and Latency

Autonomous vehicle networks generate massive volumes of telemetry. Kafka is architected as a **distributed commit log**, capable of handling millions of writes per second with sub-millisecond latency. Its sequential I/O patterns on disk maximize throughput, making it ideal for the "firehose" nature of IoT sensor data.

### 2.2 Decoupling and Scalability

Kafka enforces a strict separation between data producers and consumers. The producers (taxis) are unaware of who consumes the data, allowing the system to scale horizontally. We can add new consumers (e.g., a billing service or a machine learning training pipeline) without modifying the producers or impacting the existing monitoring service.

### 2.3 Durability and Replayability

Unlike ephemeral messaging systems, Kafka persists data to disk for a configurable retention period. This durability allows for **stream replayability**—a critical feature for debugging, historical analysis, and training predictive models on past fleet behaviors.

---

## 3. Use Case: Autonomous Taxi Fleet Simulation

The simulation models a dynamic urban environment where entities act autonomously.

### 3.1 The Producer Role: Autonomous Taxis

Each taxi is modeled as an independent thread of execution that simulates realistic driving behavior.

* **Stochastic Behavior:** The simulation introduces randomness in speed and battery consumption to mirror real-world variability.
* **Geospatial Movement:** Taxis generate coordinate updates that simulate movement through the streets of Paris.

### 3.2 Data Schemas and Kafka Topics

The data flow is segregated into two distinct topics to separate high-volume telemetry from high-value business events.

#### Topic: `vehicle-status`

This topic handles the high-velocity stream of sensor readings.

* **Payload:** JSON object containing `vehicle_id`, `timestamp`, `latitude`, `longitude`, `speed`, `battery_level`, and `temperature`.
* **Characteristics:** High frequency (~1Hz per vehicle), ephemeral value (latest data is most important).

#### Topic: `ride-events`

This topic handles the business logic state transitions.

* **Payload:** JSON object containing `ride_id`, `vehicle_id`, `customer_id`, `timestamp`, and `event_type` (REQUEST, START, CANCEL, END).
* **Characteristics:** Lower frequency, high consistency requirement (every event matters for billing).

---

## 4. System Architecture

The system follows a **Lambda-style streaming architecture**, prioritizing a "Speed Layer" for immediate operational awareness.

### High-Level Data Flow

```ascii
+-----------------------+           +-----------------------+
|   Data Sources        |           |   Streaming Layer     |
| (Autonomous Agents)   |           |    (Apache Kafka)     |
|                       |           |                       |
|  [ Taxi 1 ] --(JSON)-->           |  [ Topic: status ]    |
|  [ Taxi 2 ] --(JSON)-->  ------>  |  [ Topic: rides  ]    |
|  [ Taxi N ] --(JSON)-->           |                       |
+-----------------------+           +-----------+-----------+
                                                |
                                                v
                                    +-----------------------+
                                    |   Processing Layer    |
                                    | (Fleet Monitor Svc)   |
                                    |                       |
                                    | 1. Ingest Stream      |
                                    | 2. Detect Anomalies   |
                                    | 3. Update State File  |
                                    +-----------+-----------+
                                                |
                                                v
                                    +-----------------------+
                                    |   Presentation Layer  |
                                    | (Streamlit Dashboard) |
                                    |                       |
                                    | - Read State File     |
                                    | - Render Live Map     |
                                    +-----------------------+

```

### Architectural Decisions

* **KRaft Mode:** The Kafka cluster is deployed in KRaft (Kafka Raft) mode. This removes the dependency on ZooKeeper for cluster metadata management, simplifying the deployment architecture and improving stability.
* **State Materialization:** The consumer does not push data directly to the dashboard. Instead, it writes to a lightweight "Operational Data Store" (a JSON file in this implementation). This decouples the visualization refresh rate from the message ingestion rate.

---

## 5. Technologies Used

The technology stack was chosen to balance performance, ease of development, and industry relevance.

* **Apache Kafka (Image: `apache/kafka:latest`):** The core streaming platform. KRaft mode is utilized to align with the future of Kafka architecture (post-ZooKeeper removal).
* **Docker & Docker Compose:** Provides containerization, ensuring that the Kafka broker, networking configurations, and application logic run consistently across different development environments.
* **Python 3.11:** Selected as the runtime language. **Note:** Python 3.11 was specifically chosen over 3.12 due to compatibility requirements with the `kafka-python` client library.
* **`kafka-python`:** A robust Python client for the Kafka protocol, handling low-level details like heartbeat maintenance and offset commits.
* **Streamlit:** An open-source app framework used here to rapidly prototype the real-time geospatial dashboard without complex frontend scaffolding.
* **Provectus Kafka UI:** A web-based UI for observing the Kafka cluster, inspecting topic partitions, and debugging message serialization.

---

## 6. Installation and Setup

### 6.1 Prerequisites

Ensure the following tools are installed and configured on your host machine:

* **Docker Desktop / Docker Engine:** Required for container orchestration.
* **Python 3.11:** Required for local development (if bypassing Docker for Python components).
* **Git:** For version control.

### 6.2 Repository Initialization

Clone the repository to your local environment:

```bash
git clone https://github.com/axelClement/Kafka-Autonomous-Taxi-Network.git
cd Kafka-Autonomous-Taxi-Network

```

---

## 7. Running the Project

To accommodate different development workflows, the project supports two execution modes.

### 7.1 Option A: Full Docker Deployment (Production Simulation)

This approach runs the entire ecosystem (Broker, UI, Producer, Consumer, Dashboard) within a unified Docker network. It simulates a production-like environment where services communicate over an internal container network.

1. **Launch Services:**
```bash
docker-compose up --build

```


*The `--build` flag ensures that any changes to the Python source code are rebuilt into the container images.*
2. **Access Endpoints:**
* **Kafka UI (Cluster Management):** [http://localhost:8080](https://www.google.com/search?q=http://localhost:8080)
* **Operational Dashboard:** [http://localhost:8501](https://www.google.com/search?q=http://localhost:8501)


3. **Monitor Logs:**
Use Docker to tail the logs of specific services to verify data flow:
```bash
docker logs -f taxi-producer
docker logs -f fleet-monitor

```



### 7.2 Option B: Manual Execution (Hybrid Development Mode)

This mode is recommended for active development. The Kafka infrastructure runs in Docker, but the Python logic runs on the host machine, allowing for rapid debugging and iteration without rebuilding containers.

#### Step 1: Environment Setup

Isolate dependencies using a virtual environment to avoid conflicts.

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

#### Step 2: Infrastructure Initialization

Start only the Kafka broker and the management UI.

```bash
docker-compose up -d kafka kafka-ui

```

*Wait approximately 15 seconds for the Kafka broker to elect a controller and become ready.*

#### Step 3: Start the Consumer Service

The consumer listens for messages and updates the state file.

```bash
python src/consumer_fleet_monitor.py

```

#### Step 4: Start the Producer Service

The producer begins generating synthetic telemetry and ride events.

```bash
python src/producer_taxi.py

```

#### Step 5: Start the Visualization Layer

Launch the Streamlit dashboard.

```bash
streamlit run src/dashboard_map.py

```

---

## 8. Monitoring with Kafka UI

Observability is critical in distributed systems. **Kafka UI** provides a graphical interface to inspect the state of the cluster.

### Key Monitoring Activities

1. **Topic Inspection:** Navigate to the "Topics" tab to verify that `vehicle-status` and `ride-events` have been created.
2. **Message Browsing:** Click into a topic to view raw messages. This confirms that JSON serialization is functioning correctly.
3. **Consumer Lag:** Check the "Consumers" tab. "Lag" represents the difference between the latest message produced and the latest message consumed. High lag indicates the consumer service cannot keep up with the data volume.

---

## 9. Real-Time Fleet Visualization (Live Map Dashboard)

The visualization layer provides a human-readable interface for the system's state.

### The "Operational Data Store" Pattern

Directly consuming Kafka messages in a frontend application can be challenging due to WebSocket complexities and connection limits. Instead, this project uses an intermediate persistence pattern:

1. The **Consumer** processes the stream and updates an in-memory dictionary of the latest vehicle states.
2. This dictionary is periodically dumped to `fleet_state.json`.
3. The **Streamlit Dashboard** polls this file every 2 seconds.

This decouples the "Write Path" (high velocity) from the "Read Path" (periodic refresh), a common pattern in real-time analytics.

### Visual Features

* **Geospatial Rendering:** Uses OpenStreetMap tiles to render vehicle positions.
* **Status Encoding:**
* **Green:** Normal operation.
* **Red:** Overspeed Warning (> 30 km/h).
* **Battery Icon:** Low Battery Warning (< 20\%).


* **Metric Tooltips:** Hovering over a vehicle displays precise telemetry values.

---

## 10. Challenges Encountered and Solutions

Real-world systems integration often uncovers subtle compatibility and networking issues.

### 10.1 Python Version Compatibility

**Challenge:** Initial attempts to use Python 3.12 resulted in runtime errors with `kafka-python`. This library relies on asynchronous features that were modified in newer Python releases.
**Solution:** The project was strictly version-locked to **Python 3.11**. This highlights the importance of dependency management and pinning runtime versions in `requirements.txt` and `Dockerfile`.

### 10.2 Docker Networking & "Advertised Listeners"

**Challenge:** When running in Hybrid Mode (Option B), the local Python scripts could not connect to the Kafka broker running inside Docker.
**Solution:** The Kafka broker configuration was updated to expose two listeners:

* `PLAINTEXT://:9092`: For internal communication between Docker containers.
* `PLAINTEXT_HOST://localhost:29092`: For external communication from the host machine.
This dual-listener setup is crucial for enabling hybrid development workflows.

---

## 11. My Setup Notes

Throughout the development of this project, several key learnings emerged regarding environment management:

* **Virtual Environments are Mandatory:** Mixing system-level Python packages with project dependencies leads to unpredictable behavior. Always use `.venv`.
* **Interpreter Selection:** In IDEs like VS Code, ensuring the correct interpreter (from the virtual environment) is selected is critical. A mismatch often leads to `ModuleNotFoundError`.
* **Startup Order Matters:** Kafka takes time to initialize. Attempting to start the producer immediately after `docker-compose up` results in connection failures. Implementing retry logic or manually waiting is necessary.

---

## 12. How Kafka Fits into a Big Data Ecosystem

While this project is a self-contained simulation, it represents a microcosm of a larger enterprise architecture. In a full-scale production environment, this Kafka cluster would serve as the ingestion layer for a much broader ecosystem:

1. **Data Lake (Storage):** A generic consumer could offload all raw events to Amazon S3 or HDFS for long-term archival and compliance.
2. **Stream Processing (Analytics):** Frameworks like **Apache Flink** or **Kafka Streams** could be used to perform windowed aggregations (e.g., "Calculate average speed per district every 5 minutes").
3. **Machine Learning:** Data scientists would subscribe to historical topics to train models that predict battery degradation or ride demand, which are then deployed back into the system.

---

## 13. Possible Extensions

To further deepen the academic and practical value of this project, several extensions are proposed:

* **Database Integration:** Replace the `fleet_state.json` file with a proper time-series database like **InfluxDB** or a NoSQL store like **MongoDB** for more robust state management.
* **Advanced Analytics:** Implement a sliding window algorithm to detect "aggressive driving" patterns (rapid acceleration/deceleration) rather than just instantaneous overspeeding.
* **Back-Pressure Handling:** Implement logic in the producer to handle scenarios where the Kafka broker is temporarily unavailable, buffering messages locally to prevent data loss.
* **Schema Registry:** Integrate Confluent Schema Registry to enforce strict Avro or Protobuf schemas, preventing "poison pill" messages from corrupting the pipeline.

---

## 14. Conclusion

This project successfully demonstrates the design and implementation of a scalable, event-driven architecture for autonomous vehicle networks. By leveraging **Apache Kafka**, the system achieves the critical goals of high throughput, producer-consumer decoupling, and real-time observability.

The transition from a theoretical understanding of streaming data to a concrete implementation highlights the complexities of distributed systems—from networking configurations to stream processing logic. This architecture serves as a foundational model for understanding how modern smart cities will manage the deluge of data generated by the Internet of Things.
