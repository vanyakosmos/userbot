import re
from contextlib import contextmanager

from telethon import TelegramClient, events

from argsparse_extra import ArgumentParser, HelpAction
from settings import USERBOT_NAME


class NewMessage(events.NewMessage):
    def __init__(self, *args, parser=None, cmd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser
        if cmd is not None:
            self.cmd = re.compile(f">\\s*({cmd}.*)").match
        else:
            self.cmd = None

    def filter(self, event):
        if self.cmd is not None:
            match = self.cmd(event.message.message or '')
            if not match:
                return
            text = match[1]
            args, _ = self.parser.parse_known_args(text.split())
            if not args:
                return
            event.pattern_match = args

        return super().filter(event)


class Manager:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.handlers = []

        self.parser = ArgumentParser(prog='USERBOT', conflict_handler='resolve')
        self.parser.add_argument('-h', '--help', action=HelpAction)
        self.subparsers = self.parser.add_subparsers()

        client.add_event_handler(
            self.handle_help,
            NewMessage(outgoing=True, pattern=r'>\s*(-h|help)', parser=self.parser),
        )
        client.add_event_handler(
            self.handle_toggle,
            NewMessage(outgoing=True, pattern=r'>\s*(-t|toggle)', parser=self.parser),
        )

    def add_handler(self, callback, event: NewMessage):
        return self.handlers.append((callback, event))

    @contextmanager
    def add_command(self, name, help_text, callback, outgoing=True, incoming=False, **kwargs):
        sub_parser = self.subparsers.add_parser(name, help=help_text, conflict_handler='resolve')
        sub_parser.add_argument('-h', '--help', action=HelpAction)
        yield sub_parser
        self.handlers.append((
            callback,
            NewMessage(
                cmd=name, parser=self.parser, outgoing=outgoing, incoming=incoming, **kwargs
            )
        ))

    def register_handlers(self):
        for c, e in self.handlers:
            self.client.add_event_handler(c, e)

    def remove_handlers(self):
        for c, e in self.handlers:
            self.client.remove_event_handler(c, e)

    async def handle_help(self, event):
        text = self.parser.format_help()
        text = f"```{text}```"
        await event.reply(text)

    async def handle_toggle(self, event):
        first = self.handlers[0]
        toggle = first in self.client.list_event_handlers()
        if toggle:
            self.remove_handlers()
        else:
            self.register_handlers()
        toggle_text = 'off' if toggle else 'on'
        await event.reply(f"{USERBOT_NAME} is {toggle_text}")
