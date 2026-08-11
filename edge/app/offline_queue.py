import json,sqlite3,threading
from dataclasses import asdict
from pathlib import Path
from .models import Event,IssueType
class OfflineQueue:
 def __init__(self,path:Path):
  path.parent.mkdir(parents=True,exist_ok=True);self.lock=threading.Lock();self.db=sqlite3.connect(path,check_same_thread=False);self.db.execute("CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,payload TEXT NOT NULL,state TEXT NOT NULL DEFAULT 'PENDING',attempts INTEGER NOT NULL DEFAULT 0)");self.db.commit()
 def add(self,event):
  data=asdict(event);data["issue_type"]=event.issue_type.value;data["captured_at"]=event.captured_at.isoformat()
  with self.lock:self.db.execute("INSERT OR IGNORE INTO events(id,payload) VALUES(?,?)",(event.id,json.dumps(data)));self.db.commit()
 def pending(self):
  with self.lock:return self.db.execute("SELECT id,payload,attempts FROM events WHERE state IN ('PENDING','FAILED') ORDER BY attempts,id").fetchall()
 def uploaded(self,id):
  with self.lock:self.db.execute("UPDATE events SET state='UPLOADED' WHERE id=?",(id,));self.db.commit()
 def failed(self,id):
  with self.lock:self.db.execute("UPDATE events SET state='FAILED',attempts=attempts+1 WHERE id=?",(id,));self.db.commit()
 def count(self):
  with self.lock:return self.db.execute("SELECT count(*) FROM events WHERE state!='UPLOADED'").fetchone()[0]
