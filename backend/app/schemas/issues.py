from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from ..models.entities import IssueStatus, Severity

class IssueUpdate(BaseModel):
    status: IssueStatus|None=None
    severity: Severity|None=None
    assigned_department: str|None=None
    assigned_to: str|None=None

class VerificationRequest(BaseModel):
    vehicle_id: str; latitude: float; longitude: float
    result: str = Field(pattern="^(ISSUE_PRESENT|ISSUE_NOT_PRESENT)$")
    confidence: float = Field(ge=0, le=1); timestamp: datetime

class Heartbeat(BaseModel):
    vehicle_id: str; name: str="Monitoring Vehicle"; registration_number: str|None=None
    latitude: float|None=None; longitude: float|None=None; status: str="ONLINE"

class ORMModel(BaseModel):
    model_config=ConfigDict(from_attributes=True)

