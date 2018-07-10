import asyncio
from itertools import chain

from telethon import TelegramClient
from telethon.events import NewMessage

from settings import USERBOT_NAME


class Manager:
    def __init__(self, client: TelegramClient):
        self.outgoing_handlers = {}
        self.incoming_handlers = {}
        self.userbot_up = True
        self.client = client
        # commands
        commands = [
            (self.toggle, '^-toggle$'),
            (self.handlers_list, '^-list$'),
            (self.to_outgoing, '^-too ([\w_]+)$'),
            (self.to_incoming, '^-toi ([\w_]+)$'),
        ]
        self.register_outgoing(*commands, save=False)

    def register_outgoing(self, *handlers, save=True):
        for callback, pattern in handlers:
            self.client.add_event_handler(callback, NewMessage(outgoing=True, pattern=pattern))
            if save:
                name = callback.__name__
                self.outgoing_handlers[name] = (callback, pattern)

    def register_incoming(self, *handlers):
        for callback, pattern in handlers:
            self.client.add_event_handler(callback, NewMessage(pattern=pattern))
            name = callback.__name__
            self.incoming_handlers[name] = (callback, pattern)

    def unregister_handlers(self):
        for callback, pattern in chain(self.outgoing_handlers.values(), self.incoming_handlers.values()):
            self.client.remove_event_handler(callback)

    def reregister_handlers(self):
        self.register_incoming(*self.incoming_handlers)
        self.register_outgoing(*self.outgoing_handlers)

    async def migrate_command(self, event, handlers: dict, register, migration_type: str):
        handler_name = event.pattern_match.group(1)
        if handler_name in handlers:
            callback, handler = handlers[handler_name]
            del handlers[handler_name]
            self.client.remove_event_handler(callback)
            register((callback, handler))
        await event.edit(f'✅ moved **{handler_name}** to **{migration_type}** handlers')
        await asyncio.sleep(5)
        await event.delete()

    async def to_outgoing(self, event):
        await self.migrate_command(event, self.incoming_handlers,
                                   self.register_outgoing, '<<outgoing>>')

    async def to_incoming(self, event):
        await self.migrate_command(event, self.outgoing_handlers,
                                   self.register_incoming, '>>incoming<<')

    async def handlers_list(self, event):
        lines = ['**outgoing handlers:**']
        for callback, handler in self.outgoing_handlers.values():
            lines.append(f"` > {callback.__name__}`")
        lines.append('\n**incoming handlers:**')
        for callback, handler in self.incoming_handlers.values():
            lines.append(f"` > {callback.__name__}`")
        await event.edit('\n'.join(lines))
        await asyncio.sleep(15)
        await event.delete()

    async def toggle(self, event):
        if self.userbot_up:
            self.unregister_handlers()
            message = f"🚨 Userbot '{USERBOT_NAME}' is down"
        else:
            self.reregister_handlers()
            message = f"✅ Userbot '{USERBOT_NAME}' is up"

        self.userbot_up = not self.userbot_up
        alert, _ = await asyncio.gather(
            event.respond(message),
            event.delete(),
        )
        await asyncio.sleep(2)
        await alert.delete()
