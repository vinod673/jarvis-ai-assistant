import asyncio
import json
import threading

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    websockets = None
    WEBSOCKETS_AVAILABLE = False

connected_device = None
server_loop = None

async def _handler(websocket):
    global connected_device
    connected_device = websocket
    print("\n[Android Bridge] Phone connected over WiFi!")
    try:
        async for msg in websocket:
            print(f"[Android Bridge] Phone sent: {msg}")
    except Exception:
        print("\n[Android Bridge] Phone disconnected.")
        if connected_device == websocket:
            connected_device = None

async def _start_server():
    if not WEBSOCKETS_AVAILABLE:
        return
    async with websockets.serve(_handler, "0.0.0.0", 8765):
        await asyncio.Future()

def run_server_in_background():
    global server_loop
    if not WEBSOCKETS_AVAILABLE:
        return
    def _run():
        global server_loop
        server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(server_loop)
        server_loop.run_until_complete(_start_server())
    t = threading.Thread(target=_run, daemon=True)
    t.start()

async def _send_async(action, params):
    if not connected_device:
        return {"status": "error", "message": "No phone connected to Jarvis Bridge on port 8765."}
    payload = {"command": action, "params": params}
    await connected_device.send(json.dumps(payload))
    return {"status": "success", "result": f"Sent {action} to phone."}

def send_android_command(action, params):
    if not WEBSOCKETS_AVAILABLE:
        return {"status": "error", "message": "websockets library not available."}
    if not connected_device or not server_loop:
        return {"status": "error", "message": "Phone bridge is not currently connected."}
    future = asyncio.run_coroutine_threadsafe(_send_async(action, params), server_loop)
    try:
        return future.result(timeout=8)
    except Exception as e:
        return {"status": "error", "message": str(e)}
