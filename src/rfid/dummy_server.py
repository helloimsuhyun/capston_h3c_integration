from fastapi import FastAPI, Form, File, UploadFile
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

class StartAuthReq(BaseModel):
    tracking_person_id: str
    timestamp: Optional[str] = None

@app.post("/auth/start")
async def start_auth(req: StartAuthReq):
    return {
        "ok": True,
        "auth_event_id": "test-auth-001",
        "auth_event": {
            "auth_event_id": "test-auth-001",
            "tracking_person_id": req.tracking_person_id,
            "status": "waiting_rfid",
            "timestamp": req.timestamp or datetime.now().isoformat(),
        }
    }

@app.post("/auth/rfid")
async def auth_rfid(
    auth_event_id: str = Form(...),
    rfid_uid: str = Form(...),
    timestamp: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    return {
        "ok": True,
        "auth_event": {
            "auth_event_id": auth_event_id,
            "status": "success",
            "rfid_uid": rfid_uid,
            "timestamp": timestamp or datetime.now().isoformat(),
        },
        "image_received": image is not None,
    }

@app.post("/auth/timeout")
async def auth_timeout(
    auth_event_id: str = Form(...),
    timestamp: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    return {
        "ok": True,
        "auth_event": {
            "auth_event_id": auth_event_id,
            "status": "timeout",
            "timestamp": timestamp or datetime.now().isoformat(),
        },
        "image_received": image is not None,
    }