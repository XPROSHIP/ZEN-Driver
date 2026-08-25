import os
import time
import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="ZEN Driver Backend")

# CORS Ayarları (Her yerden erişim için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global durum takibi (Canlı ilerleme ve hız göstergesi için)
tasks_status = {}

class DownloadRequest(BaseModel):
    download_url: str
    access_token: str
    file_name: str = "ZEN_Driver_Video.mp4"

def process_stream_upload(task_id: str, url: str, access_token: str, file_name: str):
    try:
        # 1. Kaynak URL'den veri akışını başlat
        res = requests.get(url, stream=True, timeout=30)
        total_size = int(res.headers.get('content-length', 0))
        
        # 2. Google Drive Resumable Upload Başlat
        drive_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        meta_data = {"name": file_name, "mimeType": res.headers.get('content-type', 'video/mp4')}
        
        init_res = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
            headers=drive_headers,
            json=meta_data
        )
        
        upload_url = init_res.headers.get("Location")
        
        # 3. Akış halinde Drive'a aktar ve hız/yüzde hesapla
        uploaded_bytes = 0
        start_time = time.time()
        
        # 5 MB parçalar halinde aktarım
        chunk_size = 5 * 1024 * 1024 
        
        for chunk in res.iter_content(chunk_size=chunk_size):
            if chunk:
                chunk_len = len(chunk)
                end_byte = uploaded_bytes + chunk_len - 1
                
                up_headers = {
                    "Content-Length": str(chunk_len),
                    "Content-Range": f"bytes {uploaded_bytes}-{end_byte}/{total_size if total_size else '*'}"
                }
                requests.put(upload_url, headers=up_headers, data=chunk)
                
                uploaded_bytes += chunk_len
                elapsed_time = time.time() - start_time
                speed_mbps = (uploaded_bytes / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0
                progress_percent = (uploaded_bytes / total_size * 100) if total_size > 0 else 0
                
                tasks_status[task_id] = {
                    "status": "downloading",
                    "progress": round(progress_percent, 2),
                    "speed": round(speed_mbps, 2),
                    "uploaded_mb": round(uploaded_bytes / (1024 * 1024), 2),
                    "total_mb": round(total_size / (1024 * 1024), 2)
                }

        tasks_status[task_id]["status"] = "completed"
    except Exception as e:
        tasks_status[task_id] = {"status": "error", "message": str(e)}

@app.post("/api/start-transfer")
def start_transfer(req: DownloadRequest, background_tasks: BackgroundTasks):
    task_id = str(int(time.time()))
    tasks_status[task_id] = {"status": "starting", "progress": 0, "speed": 0, "uploaded_mb": 0, "total_mb": 0}
    background_tasks.add_task(process_stream_upload, task_id, req.download_url, req.access_token, req.file_name)
    return {"task_id": task_id}

@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    return tasks_status.get(task_id, {"status": "not_found"})