from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uuid
from typing import List, Dict

app = FastAPI(title="Echo - The Secret Mirror Backend")

# قاعدة بيانات مؤقتة في الذاكرة (In-Memory Storage) للتجربة السريعة
keys_db = {"SECRET2026": False}  # مفتاح تجريبي
messages_db = []
active_connections: List[WebSocket] = []

# نماذج البيانات (Pydantic Models)
class SecretMessage(BaseModel):
    key_used: str
    content: str

@app.get("/")
def home():
    return {"status": "Echo Engine is Running", "version": "1.0.0"}

# 1. التحقق من مفتاح الدعوة السري (الولوج الحصري)
@app.post("/api/verify-key")
def verify_key(key: str):
    if key in keys_db:
        if not keys_db[key]:
            keys_db[key] = True  # تفعيل المفتاح بحيث لا يُستخدم مرة أخرى
            return {"success": True, "message": "تم قبول المفتاح السري، مرحباً بك في صدى."}
        else:
            raise HTTPException(status_code=400, detail="هذا المفتاح تم استخدامه من قبل!")
    raise HTTPException(status_code=404, detail="مفتاح غير صحيح!")

# 2. إرسال بوح/سر مجهول
@app.post("/api/send-echo")
def send_echo(msg: SecretMessage):
    message_data = {
        "id": str(uuid.uuid4())[:8],
        "content": msg.content,
        "glows": 0
    }
    messages_db.append(message_data)
    return {"success": True, "data": message_data}

# 3. إحداث اتصال لحظي (WebSocket) لاستقبال الرسائل كـ "زجاجة في البحر"
@app.websocket("/ws/echoes")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # إرسال البوح الجديد فوراً للطرف الآخر لإشعال الفضول
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(f"بوح جديد في المحيط: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
