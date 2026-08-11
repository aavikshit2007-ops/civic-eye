from dataclasses import dataclass
from datetime import datetime
from enum import Enum
class IssueType(str,Enum): WASTE="WASTE";POTHOLE="POTHOLE";WATERLOGGING="WATERLOGGING"
@dataclass
class Detection:
 issue_type:IssueType;confidence:float;box:tuple[int,int,int,int]
@dataclass
class Event:
 id:str;vehicle_id:str;issue_type:IssueType;confidence:float;latitude:float;longitude:float;captured_at:datetime;model_version:str;image_path:str

