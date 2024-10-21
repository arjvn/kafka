import os
import cv2
import numpy as np
import time
from PIL import Image

from ultralytics import YOLOWorld
from confluent_kafka import Consumer, KafkaError, TopicPartition, OFFSET_END


# Kafka consumer configuration
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
consumer_conf = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'video-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_conf)

# Subscribe to the Kafka topic
consumer.subscribe(['video-stream'])

output_video_path = 'output/output_video.avi'
frame_width = None
frame_height = None
video_writer = None
fps = 30  # Adjust FPS as needed

print(">>>>> STARTING VIDEO CONSUMER <<<<<")

model = YOLOWorld("yolov8s-worldv2.pt")
model.set_classes(["car"])

try:
    print(">>>>> TRYING TO CONSUME VIDEO STREAM <<<<<")
    while True:
        print(">>>>> TRYING TO POLL <<<<<")
        msg = consumer.poll(1)  # Poll for new messages

        if msg is None:
            print("NO MESSAGE RECEIVED")
            continue

        if msg.error():
            error_code = msg.error().code()
            if error_code == KafkaError.UNKNOWN_TOPIC_OR_PARTITION:
                print("Topic not available yet, retrying in 1 second...")
                time.sleep(1)
                continue
            elif error_code == KafkaError._PARTITION_EOF:
                # End of partition event, can be ignored
                print("End of partition error")
                continue
            else:
                # For other errors, you might want to handle them differently
                print(f"Consumer error: {msg.error()}")
                time.sleep(1)
                continue

        print(">>>>> MESSAGE RECEIVED <<<<<")
        # Deserialize the frame (convert bytes back to image)
        frame_bytes = msg.value()
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Process the frame using GroundingDINO
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        print(">>>>> DETECTING OBJECTS: YOLO WORLD <<<<<")
        results = model.predict(image)
        bboxes = results[0].boxes.xywh.cpu().numpy()

        # Create a copy of the frame to annotate
        annotated_frame = frame.copy()

        # Loop over each bounding box and draw it on the image
        for bbox in bboxes:
            cx, cy, w, h = bbox

            # Convert from (cx, cy, w, h) to (x1, y1, x2, y2)
            x1 = int(cx - w / 2)
            y1 = int(cy - h / 2)
            x2 = int(cx + w / 2)
            y2 = int(cy + h / 2)

            # Draw the rectangle (bounding box) on the image
            color = (0, 255, 0)  # Green color for the box
            thickness = 2  # Thickness of the box lines
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)

        # Convert annotated_frame back to BGR for OpenCV
        print(">>>>> FRAME PROCESSED <<<<<")
        # Initialize VideoWriter once frame dimensions are known
        if video_writer is None:
            frame_height, frame_width, _ = annotated_frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can choose other codecs like 'MP4V'
            video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), isColor=True)

        # Write the processed frame to the video file
        video_writer.write(annotated_frame)

        partitions = consumer.assignment()  # Get assigned partitions
        for partition in partitions:
            consumer.seek(TopicPartition(partition.topic, partition.partition, OFFSET_END))

except KeyboardInterrupt:
    print("Interrupted by user")
    # Close the consumer and release resources
    consumer.close()
    if video_writer is not None:
        video_writer.release()
    cv2.destroyAllWindows()

print(">>>>> END OF VIDEO STREAM <<<<<")
