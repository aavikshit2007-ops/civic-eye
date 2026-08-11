import uuid,cv2
from datetime import datetime,timezone
from .config import settings
from .models import Event
def create_event(kind,confidence,frame,gps):
 event_id=str(uuid.uuid4());folder=settings.evidence_root/event_id;folder.mkdir(parents=True,exist_ok=True);path=folder/"best_frame.jpg"
 if not cv2.imwrite(str(path),frame):raise RuntimeError("Could not save evidence frame")
 lat,lon=gps.position();return Event(event_id,settings.vehicle_id,kind,confidence,lat,lon,datetime.now(timezone.utc),settings.model_version,str(path))

