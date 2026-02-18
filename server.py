import os
import logging
from aiohttp import web
import socketio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalingServer")

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Store room participants
rooms = {}

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    # Remove client from rooms
    for room_id, participants in list(rooms.items()):
        if sid in participants:
            participants.remove(sid)
            if not participants:
                del rooms[room_id]
            else:
                # Notify others
                await sio.emit('peer_left', {'sid': sid}, room=room_id)

@sio.event
async def join(sid, data):
    """Join a secure room for P2P connection"""
    room_id = data.get('room')
    if not room_id:
        return
    
    sio.enter_room(sid, room_id)
    logger.info(f"Client {sid} joined room {room_id}")
    
    if room_id not in rooms:
        rooms[room_id] = set()
    
    rooms[room_id].add(sid)
    
    # Notify other peers in the room that a new peer has joined
    await sio.emit('peer_joined', {'sid': sid}, room=room_id, skip_sid=sid)
    
    # Send list of existing peers to the new joiner
    peers = list(rooms[room_id])
    peers.remove(sid)
    if peers:
        await sio.emit('existing_peers', {'peers': peers}, to=sid)

@sio.event
async def signal(sid, data):
    """Relay WebRTC signaling messages (SDP, ICE candidates)"""
    target_sid = data.get('target')
    if target_sid:
        # Send direct message to target
        await sio.emit('signal', {
            'sender': sid,
            'type': data.get('type'),
            'data': data.get('data')
        }, to=target_sid)
    else:
        # Broadcast to room (excluding sender)
        room_id = data.get('room')
        if room_id:
            await sio.emit('signal', {
                'sender': sid,
                'type': data.get('type'),
                'data': data.get('data')
            }, room=room_id, skip_sid=sid)

async def index(request):
    return web.Response(text="QuickShare Signaling Server Running!")

app.router.add_get('/', index)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, port=port)
