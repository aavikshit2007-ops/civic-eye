from .config import settings
class GPS:
 def position(self):
  if settings.gps_mode!="mock":raise RuntimeError("Real GPS adapter is not configured")
  return settings.mock_latitude,settings.mock_longitude

