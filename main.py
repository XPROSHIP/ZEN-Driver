import math
import os
import re
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"status": "ZEN Driver Proxy Active"}


@app.get("/download")
def stream_download(url: str, request: Request):
    # Hedef dosyanın boyutunu ve header bilgilerini al
    head_resp = requests.head(url, allow_redirects=True)
    file_size = int(head_resp.headers.get("content-length", 0))

    # Range başlığı (Resume / Çoklu bağlantı için)
    range_header = request.headers.get("range")

    headers = {}
    status_code = 200

    if range_header:
        headers["Range"] = range_header
        status_code = 206

    req_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    if range_header:
        req_headers["Range"] = range_header

    r = requests.get(url, headers=req_headers, stream=True)

    def iterfile():
        for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB Chunks
            if chunk:
                yield chunk

    response_headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": r.headers.get(
            "content-type", "application/octet-stream"
        ),
        "Content-Disposition": r.headers.get(
            "content-disposition", 'attachment; filename="downloaded_file"'
        ),
    }

    if "content-length" in r.headers:
        response_headers["Content-Length"] = r.headers["content-length"]
    if "content-range" in r.headers:
        response_headers["Content-Range"] = r.headers["content-range"]

    return StreamingResponse(
        iterfile(),
        status_code=status_code,
        headers=response_headers,
        media_type=r.headers.get("content-type"),
    )
