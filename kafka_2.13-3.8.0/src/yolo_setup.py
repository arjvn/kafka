import time
from ultralytics import YOLOWorld

model = YOLOWorld("yolov8s-worldv2.pt")
# model = YOLOWorld("yolov8l-worldv2.pt")

model.set_classes(["dog", "cat"])
model.predict("cat_dog.jpeg")
print("🚀 Lets gooooooo!")
time.sleep(1)
