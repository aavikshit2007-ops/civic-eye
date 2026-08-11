import time
from collections import defaultdict,deque
from .models import IssueType
class EventGate:
 def __init__(self,minimums,window=20,cooldown=20):self.minimums=minimums;self.window=window;self.cooldown=cooldown;self.hits=defaultdict(lambda:deque(maxlen=window));self.last={}
 def observe(self,detection,frame):
  key=detection.issue_type;self.hits[key].append((detection.confidence,frame.copy()))
  if len(self.hits[key])<self.minimums[key] or time.time()-self.last.get(key,0)<self.cooldown:return None
  best=max(self.hits[key],key=lambda x:x[0]);self.hits[key].clear();self.last[key]=time.time();return best

