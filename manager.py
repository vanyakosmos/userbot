import logging
import re
from contextlib import contextmanager

from telethon import TelegramClient, events

from argparse_extra import ArgumentParser, HelpAction
from config import USERBOT_NAME

logger = logging.getLogger(__name__)


class NewMessage(events.NewMessage):
    def __init__(self, *args, parser=None, cmd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser
        if cmd is not None:
            self.cmd = re.compile(f"^[>\\-]\\s*({cmd}(?:\\s+.*)?)$").match
        else:
            self.cmd = None

    def filter(self, event):
        if self.cmd is not None:
            match = self.cmd(event.message.message or '')
            if not match:
                return
            logger.debug(f"matched: {match.groups()}")
            text = match[1]
            args_tuple = self.parser.parse_known_args(text.split())
            if not args_tuple or not args_tuple[0]:
                return
            event.pattern_match = args_tuple[0]

        return super().filter(event)


class Manager:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.handlers = []

        self.parser = ArgumentParser(prog='USERBOT', conflict_handler='resolve')
        self.parser.add_argument('-h', '--help', action=HelpAction)
        self.subparsers = self.parser.add_subparsers()

        client.add_event_handler(
            self.handle_toggle,
            NewMessage(outgoing=True, pattern=r'[>\-]\s*(-t|toggle)', parser=self.parser),
        )

    def add_handler(self, callback, event: NewMessage):
        logger.debug(f"registered callback {callback} for event {event}")
        return self.handlers.append((callback, event))

    @contextmanager
    def add_command(self, name, help_text, callback, outgoing=True, incoming=False, **kwargs):
        sub_parser = self.subparsers.add_parser(name, help=help_text, conflict_handler='resolve')
        sub_parser.add_argument('-h', '--help', action=HelpAction)
        yield sub_parser
        logger.debug(f"registered command {name!r} with callback {callback}")
        self.handlers.append((
            callback,
            NewMessage(
                cmd=name,
                parser=self.parser,
                outgoing=outgoing,
                incoming=incoming,
                **kwargs,
            )
        ))

    def register_handlers(self):
        for c, e in self.handlers:
            self.client.add_event_handler(c, e)

    def remove_handlers(self):
        for c, e in self.handlers:
            self.client.remove_event_handler(c, e)

    async def handle_toggle(self, event):
        first = self.handlers[0]
        toggle = first in self.client.list_event_handlers()
        if toggle:
            self.remove_handlers()
        else:
            self.register_handlers()
        toggle_text = 'off' if toggle else 'on'
        await event.reply(f"{USERBOT_NAME} is {toggle_text}")
