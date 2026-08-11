import os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from app.event_gate import EventGate
from app.models import Detection,IssueType
class Frame:
 def copy(self):return self
def test_temporal_confirmation():
 gate=EventGate({IssueType.POTHOLE:3},cooldown=0);d=Detection(IssueType.POTHOLE,.8,(0,0,1,1));frame=Frame()
 assert gate.observe(d,frame) is None;assert gate.observe(d,frame) is None;assert gate.observe(d,frame) is not None
def test_cooldown_blocks_repeat():
 gate=EventGate({IssueType.WASTE:1},cooldown=60);d=Detection(IssueType.WASTE,.8,(0,0,1,1));frame=Frame()
 assert gate.observe(d,frame) is not None;assert gate.observe(d,frame) is None
