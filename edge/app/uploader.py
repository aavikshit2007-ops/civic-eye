import json,logging,requests
class Uploader:
 def __init__(self,url,queue):self.url=url.rstrip("/");self.queue=queue
 def flush(self):
  for id,payload,_ in self.queue.pending():
   data=json.loads(payload);path=data.pop("image_path");data["event_id"]=data.pop("id")
   try:
    with open(path,"rb") as image:r=requests.post(self.url+"/api/v1/detections",data=data,files={"image":("best_frame.jpg",image,"image/jpeg")},timeout=8)
    r.raise_for_status();self.queue.uploaded(id);logging.info("Uploaded event %s",id)
   except (OSError,requests.RequestException) as exc:logging.warning("Upload failed for %s: %s",id,exc);self.queue.failed(id)
