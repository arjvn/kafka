import os
import cv2
import numpy as np
import time

from confluent_kafka import Consumer, KafkaException, KafkaError

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

try:
    print(">>>>> TRYING TO CONSUME VIDEO STREAM <<<<<")
    while True:
        print(">>>>> TRYING TO POLL <<<<<")
        msg = consumer.poll(1.0)  # Poll for new messages

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

        print("FRAME RECEIVED")
        # Apply a simple CV operation (convert to grayscale)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        print("FRAME PROCESSED")
        # Initialize VideoWriter once frame dimensions are known
        if video_writer is None:
            frame_height, frame_width = gray_frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can choose other codecs like 'MP4V'
            video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), isColor=False)

        print("FRAME WRITTEN")
        # Write the processed frame to the video file
        video_writer.write(gray_frame)

except KeyboardInterrupt:
    print("Interrupted by user")
    # Close the consumer
    consumer.close()
    cv2.destroyAllWindows()

print(">>>>> END OF VIDEO STREAM <<<<<")