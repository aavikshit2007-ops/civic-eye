import os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from app.models.entities import Issue,IssueStatus,IssueType
from app.services.logic import find_match,validate_transition
def issue(lat=28.6139,lon=77.2090):return Issue(issue_type=IssueType.POTHOLE,latitude=lat,longitude=lon,highest_confidence=.8,status=IssueStatus.NEW)
def test_nearby_same_type_matches():assert find_match([issue()],IssueType.POTHOLE,28.61391,77.20901) is not None
def test_far_issue_does_not_match():assert find_match([issue()],IssueType.POTHOLE,28.7,77.3) is None
def test_work_complete_requires_verification():validate_transition(IssueStatus.IN_PROGRESS,IssueStatus.PENDING_VERIFICATION)
def test_direct_resolution_rejected():
 try:validate_transition(IssueStatus.IN_PROGRESS,IssueStatus.VERIFIED_RESOLVED)
 except ValueError:return
 assert False
