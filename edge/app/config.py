from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 backend_url:str="http://localhost:8002";vehicle_id:str="GV-001";camera_source:str="0";model_path:Path=Path("models/civic_detector.pt");waterlog_model_path:Path=Path("models/waterlogging_detector.pt");model_version:str="civic-yolo-dual-v2";confidence_threshold:float=.55
 waste_confidence_threshold:float=.72;pothole_confidence_threshold:float=.68;waterlog_confidence_threshold:float=.88
 road_region_top_ratio:float=.38;max_detection_area_ratio:float=.62;min_detection_area_ratio:float=.002
 min_waste_frames:int=4;min_pothole_frames:int=4;min_waterlog_frames:int=8;event_cooldown_seconds:int=20
 gps_mode:str="mock";mock_latitude:float=28.6139;mock_longitude:float=77.2090;mock_detection:bool=False;demo_issue_type:str="POTHOLE";show_preview:bool=True
 evidence_root:Path=Path("evidence");queue_db:Path=Path("data/offline_queue.db")
 model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
