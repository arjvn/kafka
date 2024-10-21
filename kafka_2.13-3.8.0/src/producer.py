import os
import cv2
import time
from confluent_kafka import Producer

# Kafka producer configuration
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
producer_conf = {'bootstrap.servers': bootstrap_servers}
producer = Producer(producer_conf)

# Function to handle message delivery report
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Open video file
video_path = 'test1.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Stream video frames
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("End of video stream.")
        break

    # Serialize the frame (convert it to bytes)
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()

    # Produce the frame bytes to the Kafka topic
    producer.produce('video-stream', key=str(time.time()), value=frame_bytes, callback=delivery_report)

    # Flush to ensure all messages are sent
    producer.flush()

    # Optional: Control frame rate
    time.sleep(0.3)  # ~30 FPS

cap.release()
