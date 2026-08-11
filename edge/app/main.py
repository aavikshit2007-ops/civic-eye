import argparse,logging,threading,time,cv2
from .camera import Camera
from .config import settings
from .detector import Detector
from .event_gate import EventGate
from .evidence import create_event
from .gps import GPS
from .models import IssueType
from .offline_queue import OfflineQueue
from .uploader import Uploader
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
def run(source=None):
 camera=Camera(source or settings.camera_source);detector=Detector(settings.model_path,settings.waterlog_model_path,settings.confidence_threshold,settings.mock_detection,settings.demo_issue_type,{IssueType.WASTE:settings.waste_confidence_threshold,IssueType.POTHOLE:settings.pothole_confidence_threshold,IssueType.WATERLOGGING:settings.waterlog_confidence_threshold},settings.road_region_top_ratio,settings.min_detection_area_ratio,settings.max_detection_area_ratio);gps=GPS();queue=OfflineQueue(settings.queue_db);uploader=Uploader(settings.backend_url,queue)
 gate=EventGate({IssueType.WASTE:settings.min_waste_frames,IssueType.POTHOLE:settings.min_pothole_frames,IssueType.WATERLOGGING:settings.min_waterlog_frames},cooldown=settings.event_cooldown_seconds);camera.open();last_flush=0
 try:
  while True:
   ok,frame=camera.read()
   if not ok:break
   detections=detector.detect(frame)
   for d in detections:
    x1,y1,x2,y2=d.box;cv2.rectangle(frame,(x1,y1),(x2,y2),(53,232,137),2);cv2.putText(frame,f"{d.issue_type.value} {d.confidence:.0%}",(x1,max(20,y1-8)),cv2.FONT_HERSHEY_SIMPLEX,.65,(53,232,137),2)
    confirmed=gate.observe(d,frame)
    if confirmed:
     confidence,best=confirmed;event=create_event(d.issue_type,confidence,best,gps);queue.add(event);logging.info("AI confirmed %s event %s",d.issue_type.value,event.id);threading.Thread(target=uploader.flush,daemon=True).start()
   if time.time()-last_flush>10:last_flush=time.time();threading.Thread(target=uploader.flush,daemon=True).start()
   cv2.putText(frame,f"AI ONLINE | GPS LOCKED | QUEUED {queue.count()}",(16,30),cv2.FONT_HERSHEY_SIMPLEX,.55,(34,199,232),2)
   if settings.show_preview:
    cv2.imshow("CIVIC EYE - Autonomous Monitoring",frame)
    if cv2.waitKey(1)&0xFF in (27,ord('q')):break
 finally:camera.close();cv2.destroyAllWindows();uploader.flush()
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source");run(p.parse_args().source)
