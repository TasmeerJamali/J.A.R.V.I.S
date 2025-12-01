import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Create a FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wrap FastAPI app with Socket.IO
app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print(f"[API] Client connected: {sid}")
    await sio.emit('status', {'msg': 'Connected to J.A.R.V.I.S. Backend'})

@sio.event
async def disconnect(sid):
    print(f"[API] Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"[API] Message from {sid}: {data}")
    # Echo back for now
    await sio.emit('response', {'data': f"Received: {data}"})

def start_server(host='127.0.0.1', port=8000):
    print(f"[API] Starting WebSocket Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_server()
