import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Create a FastAPI app
fastapi_app = FastAPI(title="J.A.R.V.I.S. Backend API")
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System state shared with main.py
system_state = {
    "wake_word": "LISTENING",
    "voice": "IDLE",
    "brain": "STANDBY",
    "security": "MONITORING",
    "perception": "ACTIVE",
    "connection": "ONLINE",
}

command_history = []

# --- REST endpoints ---

@fastapi_app.get("/api/health")
async def health_check():
    return {"status": "online", "system": "J.A.R.V.I.S.", "version": "3.0"}

@fastapi_app.get("/api/status")
async def get_status():
    return {"state": system_state, "uptime": time.time()}

@fastapi_app.get("/api/history")
async def get_history():
    return {"commands": command_history[-50:]}

# --- Socket.IO events ---

@sio.event
async def connect(sid, environ):
    print(f"[API] Client connected: {sid}")
    await sio.emit('status', {
        'type': 'connection',
        'message': 'Connected to J.A.R.V.I.S. Backend',
        'state': system_state,
    }, room=sid)

@sio.event
async def disconnect(sid):
    print(f"[API] Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"[API] Message from {sid}: {data}")
    await sio.emit('response', {'data': f"Received: {data}"}, room=sid)

@sio.event
async def send_command(sid, data):
    """Handle text commands from the frontend"""
    command = data.get('text', '')
    print(f"[API] Command from frontend: {command}")
    command_entry = {
        'text': command,
        'source': 'frontend',
        'timestamp': time.time(),
    }
    command_history.append(command_entry)
    await sio.emit('command_received', command_entry)

# --- Helper functions called from main.py ---

async def emit_status_update(key, value, color="cyan"):
    """Emit a status change to all connected frontend clients"""
    system_state[key] = value
    await sio.emit('status_update', {
        'key': key,
        'value': value,
        'color': color,
        'timestamp': time.time(),
    })

async def emit_voice_activity(state, text=""):
    """Emit voice activity events (listening, processing, speaking)"""
    await sio.emit('voice_activity', {
        'state': state,
        'text': text,
        'timestamp': time.time(),
    })

async def emit_command_log(entry):
    """Emit a new command to the frontend log"""
    entry['id'] = str(uuid.uuid4())[:8]
    command_history.append(entry)
    await sio.emit('command_log', entry)

async def emit_brain_activity(thought="", action="", status="thinking"):
    """Emit brain/AI activity to frontend"""
    await sio.emit('brain_activity', {
        'thought': thought,
        'action': action,
        'status': status,
        'timestamp': time.time(),
    })

async def emit_notification(message, level="info"):
    """Emit a notification to the frontend"""
    await sio.emit('notification', {
        'message': message,
        'level': level,
        'timestamp': time.time(),
    })

async def emit_target_lock(x, y, width, height, label="Target"):
    """Emit a target lock overlay to the frontend"""
    await sio.emit('target_lock', {
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'label': label,
        'timestamp': time.time(),
    })

# Wrap FastAPI app with Socket.IO
app = socketio.ASGIApp(sio, fastapi_app)

def start_server(host='127.0.0.1', port=8000):
    print(f"[API] Starting J.A.R.V.I.S. Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_server()
