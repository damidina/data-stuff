from datetime import datetime
from typing import List, Dict, Any

class MessageBus:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    def send_message(self, sender: str, receiver: str, content: str) -> None:
        message = {
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)

    def get_messages(self, sender: str = None, receiver: str = None) -> List[Dict[str, Any]]:
        filtered_messages = self.messages
        if sender:
            filtered_messages = [m for m in filtered_messages if m["sender"] == sender]
        if receiver:
            filtered_messages = [m for m in filtered_messages if m["receiver"] == receiver]
        return filtered_messages

    def clear_messages(self) -> None:
        self.messages = []