# Kafka Pipeline

## Overview

This project demonstrates a Kafka-based video streaming pipeline using Python, OpenCV, and Docker. It consists of a producer that reads a video file and streams its frames to a Kafka topic, and a consumer that reads the frames from the topic, processes them (e.g., converts to grayscale), and saves the processed video to a file.


The video is converted to greyscale as a demonstration of the processing pipeline, the infrastrutre can be scaled to caryy out other processes and also multiple processes based of a single data stream.

## Key Features

- Real-Time Video Streaming: Stream video frames from a producer to a consumer using Kafka.
- Frame Processing: Apply computer vision operations (e.g., grayscale conversion) on each frame.
- Dockerized Services: Use Docker and Docker Compose for containerization and orchestration.
- Scalable Architecture: Easily extendable to handle multiple producers and consumers.
- Kafka Integration: Utilize Apache Kafka for efficient and reliable message streaming.

## Prerequisites

Docker: Ensure you have Docker installed on your system.
Docker Compose: Required for orchestrating multiple Docker containers.
Git: For cloning the repository.

## Setup and Installation

1. Clone the Repository

```
bash
git clone https://github.com/yourusername/kafka-video-streaming.git
cd kafka-video-streaming
```

2. Prepare the Output Directory
Create an output directory where the consumer will save the processed video.

```
bash
mkdir output
```

## Running the Application

1. Build and Run the Docker Containers
Use Docker Compose to build the images and start all services.

```
bash
docker-compose up --build
```

This command will:

- Start Zookeeper and Kafka services.
- Build the producer and consumer Docker images.
- Run the producer and consumer containers.

2. Monitor the Output

- Producer: Logs will indicate frames being sent to the Kafka topic.
- Consumer: Logs will show processing status and save the output video to output/output_video.avi.

3. Stop the Application
To stop the application and remove the containers, press Ctrl+C and then run:

```
bash
docker-compose down
```

## Docker Setup

### Docker Compose Services

Zookeeper: Required by Kafka for cluster coordination.
Kafka: Message broker that facilitates communication between producer and consumer.
Producer: Streams video frames to the Kafka topic.
Consumer: Processes frames from the Kafka topic and saves the output video.

### Service Configurations

Networks: All services are connected via a Docker network for internal communication.
Volumes: The output directory is mapped to the consumer container for accessing the processed video.
Environment Variables: Kafka and the Python scripts use environment variables for configuration.

## Kafka Heartbeat Feature

In Apache Kafka, the heartbeat mechanism is a critical component that enables consumers within a consumer group to maintain their membership and coordinate with the Kafka broker. It ensures that the broker is aware of the active consumers and can detect when a consumer becomes unresponsive or fails. This mechanism is essential for maintaining the reliability and fault tolerance of the system.

### How Heartbeats Work

Heartbeat Messages: Consumers send regular heartbeat messages to the Group Coordinator (a specific Kafka broker) to indicate that they are alive and able to process messages.

Session Timeout: If a consumer fails to send a heartbeat within the session timeout period, the broker considers the consumer dead and triggers a rebalance to redistribute the partitions among the remaining consumers.

Rebalancing: Rebalancing is the process of redistributing partition ownership among consumers when there is a change in the consumer group (e.g., when a consumer joins or leaves).


### Importance in the Project

Ensuring Reliable Consumption
In your Kafka video streaming project:

The consumer continuously polls messages (video frames) from the Kafka topic and processes them.

The heartbeat mechanism ensures that the consumer remains a part of the consumer group (video-group) by regularly communicating with the broker.

Handling Long Processing Times
Potential Issue: Processing video frames might take longer than the default max.poll.interval.ms.

Solution: Increase max.poll.interval.ms to accommodate longer processing times, ensuring the consumer is not considered unresponsive.

