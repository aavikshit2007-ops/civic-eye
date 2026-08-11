from math import asin, cos, radians, sin, sqrt
from ..config import settings
from ..models.entities import IssueStatus, IssueType, Severity

OPEN={IssueStatus.NEW,IssueStatus.VALIDATED,IssueStatus.ASSIGNED,IssueStatus.IN_PROGRESS,IssueStatus.PENDING_VERIFICATION,IssueStatus.REOPENED,IssueStatus.ESCALATED}
TRANSITIONS={IssueStatus.NEW:{IssueStatus.VALIDATED,IssueStatus.ASSIGNED,IssueStatus.REJECTED,IssueStatus.ESCALATED},IssueStatus.VALIDATED:{IssueStatus.ASSIGNED,IssueStatus.REJECTED,IssueStatus.ESCALATED},IssueStatus.ASSIGNED:{IssueStatus.IN_PROGRESS,IssueStatus.REJECTED,IssueStatus.ESCALATED},IssueStatus.IN_PROGRESS:{IssueStatus.PENDING_VERIFICATION,IssueStatus.ESCALATED},IssueStatus.PENDING_VERIFICATION:{IssueStatus.VERIFIED_RESOLVED,IssueStatus.REOPENED,IssueStatus.ESCALATED},IssueStatus.REOPENED:{IssueStatus.ASSIGNED,IssueStatus.IN_PROGRESS,IssueStatus.ESCALATED},IssueStatus.ESCALATED:{IssueStatus.ASSIGNED,IssueStatus.IN_PROGRESS,IssueStatus.PENDING_VERIFICATION},IssueStatus.VERIFIED_RESOLVED:{IssueStatus.REOPENED},IssueStatus.REJECTED:set()}
def distance_m(a,b,c,d):
 x=radians(c-a); y=radians(d-b); q=sin(x/2)**2+cos(radians(a))*cos(radians(c))*sin(y/2)**2
 return 12742000*asin(sqrt(q))
def radius(t): return {IssueType.WASTE:settings.waste_match_radius_meters,IssueType.POTHOLE:settings.pothole_match_radius_meters,IssueType.WATERLOGGING:settings.waterlog_match_radius_meters}[t]
def severity(t,confidence,count):
 score=confidence+(.12 if count>=3 else 0)+(.08 if t==IssueType.WATERLOGGING else 0)
 return Severity.CRITICAL if score>=1.08 else Severity.HIGH if score>=.86 else Severity.MEDIUM if score>=.65 else Severity.LOW
def find_match(issues,t,lat,lon):
 rows=[i for i in issues if i.issue_type==t and i.status in OPEN|{IssueStatus.VERIFIED_RESOLVED} and distance_m(lat,lon,i.latitude,i.longitude)<=radius(t)]
 return min(rows,key=lambda i:distance_m(lat,lon,i.latitude,i.longitude),default=None)
def validate_transition(old,new):
 if old!=new and new not in TRANSITIONS[old]: raise ValueError(f"Invalid transition: {old.value} -> {new.value}")
