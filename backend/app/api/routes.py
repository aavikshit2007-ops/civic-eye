import shutil, uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models.entities import DetectionEvent, Issue, IssueStatus, IssueType, Vehicle
from ..schemas.issues import Heartbeat, IssueUpdate, VerificationRequest
from ..services.logic import find_match, severity, validate_transition
router=APIRouter(prefix="/api/v1")
def issue_dict(i,detail=False):
 d={"id":i.id,"issue_type":i.issue_type.value,"latitude":i.latitude,"longitude":i.longitude,"status":i.status.value,"severity":i.severity.value,"priority":i.priority,"first_detected_at":i.first_detected_at,"last_detected_at":i.last_detected_at,"detection_count":i.detection_count,"highest_confidence":i.highest_confidence,"assigned_department":i.assigned_department,"assigned_to":i.assigned_to,"verified_at":i.verified_at}
 if detail:d["events"]=[{"id":e.id,"vehicle_id":e.vehicle_id,"confidence":e.confidence,"captured_at":e.captured_at,"image_url":"/media/"+Path(e.image_path).name,"clip_url":"/media/"+Path(e.clip_path).name if e.clip_path else None} for e in sorted(i.events,key=lambda x:x.captured_at,reverse=True)]
 return d
@router.post("/detections")
async def detection(event_id:str=Form(...),vehicle_id:str=Form(...),issue_type:IssueType=Form(...),confidence:float=Form(...),latitude:float=Form(...),longitude:float=Form(...),captured_at:datetime=Form(...),model_version:str=Form(...),image:UploadFile=File(...),clip:UploadFile|None=File(None),db:Session=Depends(get_db)):
 if not 0<=confidence<=1 or not -90<=latitude<=90 or not -180<=longitude<=180:raise HTTPException(422,"Invalid confidence or coordinates")
 existing=db.get(DetectionEvent,event_id)
 if existing:return {"event_id":event_id,"issue_id":existing.issue_id,"result":"duplicate"}
 if not (image.content_type or "").startswith("image/"):raise HTTPException(415,"Evidence image required")
 settings.media_root.mkdir(parents=True,exist_ok=True); suffix=Path(image.filename or ".jpg").suffix.lower(); suffix=suffix if suffix in {".jpg",".jpeg",".png",".webp"} else ".jpg"; image_path=settings.media_root/f"{uuid.uuid4()}{suffix}"
 with image_path.open("wb") as out:shutil.copyfileobj(image.file,out)
 if image_path.stat().st_size>settings.max_image_mb*1024*1024:image_path.unlink();raise HTTPException(413,"Image too large")
 clip_path=None
 if clip:
  clip_path=settings.media_root/f"{uuid.uuid4()}.mp4"
  with clip_path.open("wb") as out:shutil.copyfileobj(clip.file,out)
 issues=db.scalars(select(Issue)).all(); match=find_match(issues,issue_type,latitude,longitude)
 if match:
  result="merged";match.detection_count+=1;match.last_detected_at=captured_at;match.highest_confidence=max(match.highest_confidence,confidence)
  if match.status in {IssueStatus.PENDING_VERIFICATION,IssueStatus.VERIFIED_RESOLVED}:match.status=IssueStatus.REOPENED
  match.severity=severity(issue_type,match.highest_confidence,match.detection_count)
 else:
  result="created";match=Issue(issue_type=issue_type,latitude=latitude,longitude=longitude,highest_confidence=confidence,first_detected_at=captured_at,last_detected_at=captured_at,severity=severity(issue_type,confidence,1));db.add(match);db.flush()
 db.add(DetectionEvent(id=event_id,vehicle_id=vehicle_id,issue_id=match.id,issue_type=issue_type,confidence=confidence,latitude=latitude,longitude=longitude,captured_at=captured_at,image_path=str(image_path),clip_path=str(clip_path) if clip_path else None,model_version=model_version))
 vehicle=db.get(Vehicle,vehicle_id) or Vehicle(id=vehicle_id);vehicle.last_seen=datetime.now(timezone.utc);vehicle.latitude=latitude;vehicle.longitude=longitude;db.add(vehicle);db.commit();return {"event_id":event_id,"issue_id":match.id,"result":result}
@router.get("/issues")
def issues(issue_type:IssueType|None=None,status:IssueStatus|None=None,search:str|None=None,db:Session=Depends(get_db)):
 rows=db.scalars(select(Issue).order_by(Issue.last_detected_at.desc())).all()
 if issue_type:rows=[i for i in rows if i.issue_type==issue_type]
 if status:rows=[i for i in rows if i.status==status]
 if search:rows=[i for i in rows if search.lower() in i.id.lower()]
 return [issue_dict(i) for i in rows]
@router.get("/issues/map")
def issue_map(db:Session=Depends(get_db)):return [issue_dict(i) for i in db.scalars(select(Issue)).all()]
@router.get("/issues/verification-targets")
def targets(db:Session=Depends(get_db)):return [issue_dict(i) for i in db.scalars(select(Issue).where(Issue.status==IssueStatus.PENDING_VERIFICATION)).all()]
@router.get("/issues/{issue_id}")
def issue(issue_id:str,db:Session=Depends(get_db)):
 row=db.get(Issue,issue_id)
 if not row:raise HTTPException(404,"Issue not found")
 return issue_dict(row,True)
@router.patch("/issues/{issue_id}")
def update_issue(issue_id:str,payload:IssueUpdate,db:Session=Depends(get_db)):
 row=db.get(Issue,issue_id)
 if not row:raise HTTPException(404,"Issue not found")
 if payload.status:
  try:validate_transition(row.status,payload.status)
  except ValueError as e:raise HTTPException(409,str(e))
  row.status=payload.status
  if payload.status==IssueStatus.PENDING_VERIFICATION:row.resolved_at=datetime.now(timezone.utc)
 for f in ("severity","assigned_department","assigned_to"):
  if getattr(payload,f) is not None:setattr(row,f,getattr(payload,f))
 db.commit();return issue_dict(row,True)
@router.post("/issues/{issue_id}/verify")
def verify(issue_id:str,payload:VerificationRequest,db:Session=Depends(get_db)):
 row=db.get(Issue,issue_id)
 if not row:raise HTTPException(404,"Issue not found")
 if row.status!=IssueStatus.PENDING_VERIFICATION:raise HTTPException(409,"Issue is not pending verification")
 row.status=IssueStatus.REOPENED if payload.result=="ISSUE_PRESENT" else IssueStatus.VERIFIED_RESOLVED
 if row.status==IssueStatus.VERIFIED_RESOLVED:row.verified_at=payload.timestamp
 db.commit();return issue_dict(row)
@router.get("/dashboard/stats")
def dashboard(db:Session=Depends(get_db)):
 rows=db.scalars(select(Issue)).all();active=[i for i in rows if i.status not in {IssueStatus.VERIFIED_RESOLVED,IssueStatus.REJECTED}]
 return {"total_detections":sum(i.detection_count for i in rows),"active_issues":len(active),"new":sum(i.status==IssueStatus.NEW for i in rows),"in_progress":sum(i.status==IssueStatus.IN_PROGRESS for i in rows),"pending_verification":sum(i.status==IssueStatus.PENDING_VERIFICATION for i in rows),"verified_resolved":sum(i.status==IssueStatus.VERIFIED_RESOLVED for i in rows),"by_type":{t.value:sum(i.issue_type==t for i in rows) for t in IssueType},"latest":[issue_dict(i) for i in sorted(rows,key=lambda x:x.last_detected_at,reverse=True)[:6]]}
@router.get("/vehicles")
def vehicles(db:Session=Depends(get_db)):return [{"id":v.id,"name":v.name,"status":v.status,"last_seen":v.last_seen,"latitude":v.latitude,"longitude":v.longitude} for v in db.scalars(select(Vehicle)).all()]
@router.post("/vehicles/heartbeat")
def heartbeat(p:Heartbeat,db:Session=Depends(get_db)):
 v=db.get(Vehicle,p.vehicle_id) or Vehicle(id=p.vehicle_id);v.name=p.name;v.latitude=p.latitude;v.longitude=p.longitude;v.status=p.status;v.last_seen=datetime.now(timezone.utc);db.add(v);db.commit();return {"status":"ok"}
