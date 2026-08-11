import cv2
class Camera:
 def __init__(self,source):self.source=int(source) if str(source).isdigit() else source;self.cap=None
 def open(self):
  self.cap=cv2.VideoCapture(self.source)
  if not self.cap.isOpened():raise RuntimeError(f"Camera source unavailable: {self.source}")
 def read(self):return self.cap.read()
 def close(self):
  if self.cap:self.cap.release()

