import asyncio
from enum import Enum, auto
from typing import Dict

from telethon import TelegramClient
from telethon.events import NewMessage

from settings import USERBOT_NAME


class HandlerType(Enum):
    outgoing = auto()
    incoming = auto()
    removed = auto()

    def __str__(self):
        return self._name_


class Handler:
    def __init__(self, callback, pattern: str, type=HandlerType.removed):
        self.name = callback.__name__
        self.callback = callback
        self.pattern = pattern
        self.type = type

    @property
    def pack(self):
        return self.callback, self.pattern

    @property
    def strict_pattern(self):
        return f'^{self.pattern}$'


class Manager:
    def __init__(self, client: TelegramClient):
        self.handlers = {}  # type: Dict[str, Handler]
        self.userbot_up = True
        self.client = client
        # commands
        commands = [
            (self.toggle, '-toggle'),
            (self.handlers_status, '-stat(p)?'),
            (self.to_outgoing, '-too ([\w_]+)'),
            (self.to_incoming, '-toi ([\w_]+)'),
            (self.to_removed, '-tor ([\w_]+)'),
        ]
        self.register_outgoing(*commands, add=False)

    def add_outgoing_handler(self, handler: Handler, add=True):
        handler.type = HandlerType.outgoing
        self.client.add_event_handler(handler.callback,
                                      NewMessage(outgoing=True, pattern=handler.strict_pattern))
        if add:
            self.handlers[handler.name] = handler

    def add_incoming_handler(self, handler: Handler, add=True):
        handler.type = HandlerType.incoming
        self.client.add_event_handler(handler.callback,
                                      NewMessage(pattern=handler.strict_pattern))
        if add:
            self.handlers[handler.name] = handler

    def register_trashy(self, *raw_handlers):
        for callback, pattern in raw_handlers:
            handler = Handler(callback, pattern)
            self.handlers[handler.name] = handler

    def register_outgoing(self, *raw_handlers, add=True):
        for callback, pattern in raw_handlers:
            handler = Handler(callback, pattern)
            self.add_outgoing_handler(handler, add)

    def register_incoming(self, *handlers):
        for callback, pattern in handlers:
            handler = Handler(callback, pattern)
            self.add_incoming_handler(handler)

    def unregister_handlers(self):
        for handler in self.handlers.values():
            self.client.remove_event_handler(handler.callback)

    def register_handlers(self):
        for handler in self.handlers.values():
            if handler.type == HandlerType.outgoing:
                self.add_outgoing_handler(handler, add=False)
            elif handler.type == HandlerType.incoming:
                self.add_incoming_handler(handler, add=False)

    async def migrate_callback(self, event, to_type: HandlerType):
        handler_name = event.pattern_match.group(1)
        if handler_name not in self.handlers:
            return
        handler = self.handlers[handler_name]
        self.client.remove_event_handler(handler.callback)
        if to_type == HandlerType.outgoing:
            self.add_outgoing_handler(handler, add=False)
        elif to_type == HandlerType.incoming:
            self.add_incoming_handler(handler, add=False)
        else:
            handler.type = HandlerType.removed

        await event.edit(f'✅ moved **{handler.name}** to **{handler.type}** handlers')
        await asyncio.sleep(5)
        await event.delete()

    async def to_outgoing(self, event):
        await self.migrate_callback(event, HandlerType.outgoing)

    async def to_incoming(self, event):
        await self.migrate_callback(event, HandlerType.incoming)

    async def to_removed(self, event):
        await self.migrate_callback(event, HandlerType.removed)

    def add_line(self, lines: list, handler: Handler, add_pattern=False):
        if add_pattern:
            text = f"` > {handler.name:20s} : {handler.pattern}`"
        else:
            text = f"` > {handler.name}`"
        lines.append(text)

    async def handlers_status(self, event):
        add_pattern = event.pattern_match.group(1) is not None
        outgoing = []
        incoming = []
        removed = []
        for handler in self.handlers.values():
            if handler.type is HandlerType.outgoing:
                outgoing.append(handler)
            elif handler.type is HandlerType.incoming:
                incoming.append(handler)
            elif handler.type is HandlerType.removed:
                removed.append(handler)

        lines = [
            '✅ Userbot is up' if self.userbot_up else '🚨 Userbot is down',
            '\n**outgoing handlers:**',
        ]
        for handler in outgoing:
            self.add_line(lines, handler, add_pattern)
        lines.append('\n**incoming handlers:**')
        for handler in incoming:
            self.add_line(lines, handler, add_pattern)
        lines.append('\n**removed handlers:**')
        for handler in removed:
            self.add_line(lines, handler, add_pattern)
        await event.edit('\n'.join(lines))
        await asyncio.sleep(15)
        await event.delete()

    async def toggle(self, event):
        if self.userbot_up:
            self.unregister_handlers()
            message = f"🚨 Userbot '{USERBOT_NAME}' is down"
        else:
            self.register_handlers()
            message = f"✅ Userbot '{USERBOT_NAME}' is up"

        self.userbot_up = not self.userbot_up
        alert, _ = await asyncio.gather(
            event.respond(message),
            event.delete(),
        )
        await asyncio.sleep(2)
        await alert.delete()
