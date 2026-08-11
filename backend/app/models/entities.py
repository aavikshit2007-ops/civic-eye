import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid.uuid4())

class IssueType(str, enum.Enum):
    WASTE="WASTE"; POTHOLE="POTHOLE"; WATERLOGGING="WATERLOGGING"
class IssueStatus(str, enum.Enum):
    NEW="NEW"; VALIDATED="VALIDATED"; ASSIGNED="ASSIGNED"; IN_PROGRESS="IN_PROGRESS"; PENDING_VERIFICATION="PENDING_VERIFICATION"; VERIFIED_RESOLVED="VERIFIED_RESOLVED"; REOPENED="REOPENED"; ESCALATED="ESCALATED"; REJECTED="REJECTED"
class Severity(str, enum.Enum):
    LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"; CRITICAL="CRITICAL"

class Issue(Base):
    __tablename__="issues"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    issue_type: Mapped[IssueType] = mapped_column(Enum(IssueType))
    latitude: Mapped[float] = mapped_column(Float); longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[IssueStatus] = mapped_column(Enum(IssueStatus), default=IssueStatus.NEW)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.MEDIUM)
    priority: Mapped[int] = mapped_column(Integer, default=50)
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    detection_count: Mapped[int] = mapped_column(Integer, default=1)
    highest_confidence: Mapped[float] = mapped_column(Float)
    assigned_department: Mapped[str|None] = mapped_column(String(120), nullable=True)
    assigned_to: Mapped[str|None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    resolved_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    events: Mapped[list["DetectionEvent"]] = relationship(back_populates="issue")

class DetectionEvent(Base):
    __tablename__="detection_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(80), index=True)
    issue_id: Mapped[str|None] = mapped_column(ForeignKey("issues.id"), nullable=True)
    issue_type: Mapped[IssueType] = mapped_column(Enum(IssueType))
    confidence: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float); longitude: Mapped[float] = mapped_column(Float)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True)); received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    image_path: Mapped[str] = mapped_column(Text); clip_path: Mapped[str|None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str] = mapped_column(String(80)); verification_event: Mapped[bool] = mapped_column(Boolean, default=False)
    issue: Mapped[Issue|None] = relationship(back_populates="events")

class Vehicle(Base):
    __tablename__="vehicles"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Monitoring Vehicle")
    registration_number: Mapped[str|None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ONLINE")
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    latitude: Mapped[float|None] = mapped_column(Float, nullable=True); longitude: Mapped[float|None] = mapped_column(Float, nullable=True)

