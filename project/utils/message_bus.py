class MessageBus:
    def __init__(self):
        self.messages = []

    def send_message(self, sender: str, receiver: str, content: any):
        message = {
            'sender': sender,
            'receiver': receiver,
            'content': content
        }
        self.messages.append(message)
        return message

    def get_messages(self, receiver: str = None):
        if receiver:
            return [m for m in self.messages if m['receiver'] == receiver]
        return self.messages