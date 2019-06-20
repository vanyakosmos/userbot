import logging
import re
from contextlib import contextmanager

from telethon import TelegramClient, events

import handlers
from argparse_extra import ArgumentParser, HelpAction, MergeAction
from config import NOU_LIST_REGEX, USERBOT_NAME

logger = logging.getLogger(__name__)


class NewMessage(events.NewMessage):
    def __init__(self, *args, parser=None, cmd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser
        self.cmd = None
        self.cmd_pattern = None
        if cmd is not None:
            if cmd:
                self.cmd_pattern = re.compile(r"^[>\-]\s*(%s(?:\s+.*)?)$" % cmd)
            else:
                self.cmd_pattern = re.compile(r"^[>\-]\s*((?:\s*.*)?)$")
            self.cmd = self.cmd_pattern.match

    def filter(self, event):
        if self.cmd is not None:
            match = self.cmd(event.message.message or '')
            if not match:
                return
            logger.debug(f"matched: {match.groups()}")
            text = match[1]
            try:
                args_tuple = self.parser.parse_known_args(text.split())
            except ValueError as e:
                logger.debug(f"parse error: {e}")
                return
            if not args_tuple or not args_tuple[0]:
                return
            logger.debug(f"command arguments: {args_tuple[0]}")
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
        logger.debug(f"registered callback {callback.__name__!r}")
        return self.handlers.append((callback, event))

    @contextmanager
    def add_command(self, name, help_text, callback, outgoing=True, incoming=False, **kwargs):
        sub_parser = self.subparsers.add_parser(name, help=help_text, conflict_handler='resolve')
        sub_parser.add_argument('-h', '--help', action=HelpAction)
        yield sub_parser
        logger.debug(f"registered command {name!r} with callback {callback.__name__!r}")
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


def setup_handlers(client: TelegramClient):
    m = Manager(client)

    m.add_handler(handlers.handle_help, NewMessage(cmd='', outgoing=True, parser=m.parser))
    m.add_handler(handlers.handle_nou, NewMessage(pattern=NOU_LIST_REGEX))

    with m.add_command('hello', "say hello from userbot", handlers.handle_hello):
        pass

    with m.add_command('e', "evaluate expression", handlers.handle_eval) as p:
        p.add_argument('expression', action=MergeAction)

    with m.add_command('s', "sed substitution (aka find and replace)", handlers.handle_sub) as p:
        p.add_argument('text', help='sed substitution string')
        p.add_argument('-h', dest='highlight', action='store_true', help="highlight replaced")

    with m.add_command('t', "timer", handlers.handle_timer) as p:
        p.add_argument('time', help='time is seconds')
        p.add_argument('-m', dest='message', help='message to show after time is up')

    with m.add_command('g', "google search", handlers.google) as p:
        p.add_argument('query', help='query to search', action=MergeAction)
        p.add_argument('-i', dest='image', action='store_true', help='image search')
        p.add_argument('-l', dest='let_me', action='store_true', help='"let me google for you"')

    with m.add_command('m', "magic moon loop", handlers.magic) as p:
        p.add_argument('text', nargs='*', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')
        p.add_argument('-w', dest='wide', action='store_true', help='use wide text')

    with m.add_command('mar', "marquee loop", handlers.marquee) as p:
        p.add_argument('text', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')

    with m.add_command('h', "highlight text/code block", handlers.highlight_code) as p:
        p.add_argument('text', nargs='*', action=MergeAction)
        p.add_argument('-l', dest='lang', help="programming language")
        p.add_argument('-c', dest='carbon', action='store_true', help="add carbon link")
        p.add_argument('--ln', dest='line_numbers', action='store_true', help="show line numbers")
        p.add_argument('-t', dest='theme', default='monokai', help="highlight theme")

    with m.add_command('r', "rotate image in reply", handlers.handle_rotate) as p:
        p.add_argument('angle', type=int, default=90, help="rotation angle")

    with m.add_command('loop_desc', "loop description", handlers.loop_description) as p:
        p.add_argument('-t', dest='type', help="type of description")
        p.add_argument('-s', dest='sleep', type=int, default=30, help='sleep/update interval')

    with m.add_command('loop_name', "loop name", handlers.loop_name) as p:
        p.add_argument('-s', dest='sleep', type=int, default=120, help='sleep/update interval')

    with m.add_command('logs', "show bot logs", handlers.handle_logs) as p:
        p.add_argument('-s', dest='size', type=int, default=20, help='number of lines to return')

    m.register_handlers()
    return m
