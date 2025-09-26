import asyncio
import websockets
import json
from collections import defaultdict

class RealTimeStreamer:
    def __init__(self, database, host='localhost', port=8765):
        self.db = database
        self.host = host
        self.port = port
        self.subscriptions = defaultdict(set)  # table -> set of websockets
        self.websocket_server = None
    
    async def start_server(self):
        """Start WebSocket server for real-time updates"""
        self.websocket_server = await websockets.serve(
            self.handle_connection, self.host, self.port
        )
        print(f"Real-time stream server started on ws://{self.host}:{self.port}")
    
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        try:
            async for message in websocket:
                await self.handle_message(websocket, json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            self.remove_subscriber(websocket)
    
    async def handle_message(self, websocket, message):
        """Handle subscription messages"""
        if message['type'] == 'subscribe':
            table = message['table']
            self.subscriptions[table].add(websocket)
            await websocket.send(json.dumps({
                'type': 'subscribed',
                'table': table
            }))
    
    def notify_subscribers(self, table: str, operation: str, data: dict):
        """Notify all subscribers of table changes"""
        if table in self.subscriptions:
            message = json.dumps({
                'type': 'data_change',
                'table': table,
                'operation': operation,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
            
            # Send to all subscribers (in real implementation, use proper async)
            for websocket in list(self.subscriptions[table]):
                try:
                    asyncio.create_task(websocket.send(message))
                except:
                    self.remove_subscriber(websocket)
    
    def remove_subscriber(self, websocket):
        """Remove disconnected subscriber"""
        for table, subscribers in self.subscriptions.items():
            if websocket in subscribers:
                subscribers.remove(websocket)