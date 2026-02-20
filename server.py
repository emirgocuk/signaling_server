import os
import logging
from aiohttp import web
import json
import asyncio
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalingServer")

app = web.Application()

# In-memory storage for rooms and messages
# rooms: { room_id: set(sid1, sid2) }
rooms = defaultdict(set)
# messages: { target_sid: asyncio.Queue() }
message_queues = {}

async def handle_join(request):
    try:
        data = await request.json()
        room_id = data.get('room')
        sid = data.get('sid')
        
        if not room_id or not sid:
            return web.json_response({'error': 'Missing room or sid'}, status=400)
            
        rooms[room_id].add(sid)
        
        if sid not in message_queues:
            message_queues[sid] = asyncio.Queue()
            
        logger.info(f"Client {sid} joined room {room_id}")
        
        # Notify others
        peers = list(rooms[room_id])
        peers.remove(sid)
        for peer in peers:
            if peer in message_queues:
                await message_queues[peer].put({
                    'type': 'peer_joined',
                    'sid': sid
                })
                
        return web.json_response({'status': 'ok', 'peers': peers})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def handle_signal(request):
    try:
        data = await request.json()
        sender_sid = data.get('sender')
        target_sid = data.get('target')
        msg_type = data.get('type')
        payload = data.get('data')
        room_id = data.get('room')
        
        if target_sid:
            if target_sid in message_queues:
                await message_queues[target_sid].put({
                    'type': msg_type,
                    'data': payload,
                    'sender': sender_sid
                })
        else:
            if room_id in rooms:
                for peer in rooms[room_id]:
                    if peer != sender_sid and peer in message_queues:
                        await message_queues[peer].put({
                            'type': msg_type,
                            'data': payload,
                            'sender': sender_sid
                        })
                        
        return web.json_response({'status': 'ok'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def handle_poll(request):
    sid = request.query.get('sid')
    if not sid:
         return web.json_response({'error': 'Missing sid'}, status=400)
         
    if sid not in message_queues:
        message_queues[sid] = asyncio.Queue()
        
    try:
        # Long polling: wait for up to 30 seconds for a message
        msg = await asyncio.wait_for(message_queues[sid].get(), timeout=30.0)
        return web.json_response({'messages': [msg]})
    except asyncio.TimeoutError:
        return web.json_response({'messages': []})
    except Exception as e:
         return web.json_response({'error': str(e)}, status=500)

async def index(request):
    return web.Response(text="QuickShare HTTP Signaling Server Running!")

app.router.add_post('/join', handle_join)
app.router.add_post('/signal', handle_signal)
app.router.add_get('/poll', handle_poll)
app.router.add_get('/', index)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    # Note: Render handles CORS, but simple HTTP doesn't restrict strictly unless preflight is enforced.
    web.run_app(app, port=port)
