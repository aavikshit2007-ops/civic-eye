import os
from pathlib import Path
from .models import Detection,IssueType
class Detector:
 def __init__(self,path:Path,waterlog_path:Path,threshold:float,mock=False,demo_type="POTHOLE",class_thresholds=None,road_region_top=.38,min_area_ratio=.002,max_area_ratio=.62):
  self.threshold=threshold;self.mock=mock;self.demo_type=IssueType(demo_type.upper());self.frame=0;self.models=[]
  self.class_thresholds=class_thresholds or {};self.road_region_top=road_region_top;self.min_area_ratio=min_area_ratio;self.max_area_ratio=max_area_ratio
  if not mock:
   if not path.exists():raise FileNotFoundError(f"Local model not found: {path}. Set MODEL_PATH or enable MOCK_DETECTION=true.")
   if not waterlog_path.exists():raise FileNotFoundError(f"Local waterlogging model not found: {waterlog_path}. Set WATERLOG_MODEL_PATH or enable MOCK_DETECTION=true.")
   os.environ.setdefault("YOLO_CONFIG_DIR",str(Path("data/ultralytics").resolve()))
   from ultralytics import YOLO
   self.models=[YOLO(str(path)),YOLO(str(waterlog_path))]
 def detect(self,frame):
  self.frame+=1;h,w=frame.shape[:2]
  if self.mock:
   if self.frame%90<22:return [Detection(self.demo_type,.91,(w//4,h//2,w*3//4,h*4//5))]
   return []
  out=[];height,width=frame.shape[:2];frame_area=max(1,height*width)
  aliases={"garbage":IssueType.WASTE,"waste":IssueType.WASTE,"trash":IssueType.WASTE,"pothole":IssueType.POTHOLE,"waterlogging":IssueType.WATERLOGGING,"flooded":IssueType.WATERLOGGING,"flood-area":IssueType.WATERLOGGING,"flood":IssueType.WATERLOGGING}
  for model in self.models:
   result=model.predict(frame,conf=self.threshold,verbose=False)[0]
   for box in result.boxes:
    name=str(result.names[int(box.cls[0])]).lower();kind=aliases.get(name)
    if kind:
     confidence=float(box.conf[0]);coords=tuple(map(int,box.xyxy[0]));x1,y1,x2,y2=coords
     area_ratio=max(0,x2-x1)*max(0,y2-y1)/frame_area;center_y=(y1+y2)/(2*height)
     if confidence<self.class_thresholds.get(kind,self.threshold):continue
     if not self.min_area_ratio<=area_ratio<=self.max_area_ratio:continue
     if center_y<self.road_region_top:continue
     out.append(Detection(kind,confidence,coords))
  return out
