from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message

Event = Union[Message, NewMessage.Event]
