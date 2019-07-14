import asyncio
import logging
import re
from argparse import Action
from collections import OrderedDict
from contextlib import contextmanager
from typing import Union, Type, Tuple

from telethon import TelegramClient, events
from telethon.events import StopPropagation

import handlers
from argparse_extra import ArgumentParser, HelpAction, MergeAction
from config import NOU_LIST_REGEX, USERBOT_NAME, NOU_PATTERN
from handlers.utils import Event

ActionType = Union[str, Type[Action]]
logger = logging.getLogger(__name__)


class NewMessage(events.NewMessage):
    def __init__(self, *args, name=None, parser=None, cmd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser
        self.cmd = None
        self.cmd_pattern = None
        if cmd is not None:
            commands = cmd
            if not isinstance(cmd, (tuple, list)):
                commands = [cmd]
            assert len(commands) > 0
            if cmd != '':
                cmd_pattern = '(?:' + '|'.join(commands) + ')'
                self.cmd_pattern = re.compile(r"^[>\-]\s*(%s(?:\s+.*)?)$" % cmd_pattern)
            else:
                self.cmd_pattern = re.compile(r"^[>\-]\s*((?:\s*.*)?)$")
            self.cmd = self.cmd_pattern.match
        # explicit or first command or None
        self.name = name or (cmd and isinstance(cmd, (tuple, list)) and cmd[0]) or cmd or None

    def filter(self, event):
        if self.cmd is not None:
            match = self.cmd(event.message.message or '')
            if not match:
                return
            tokens = match[1].split()
            logger.debug(f"matched: {match.groups()}, tokens: {tokens}")
            try:
                args_tuple = self.parser.parse_known_args(tokens)
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
        self.handlers_statuses = OrderedDict()

        self.parser = ArgumentParser(prog='USERBOT', conflict_handler='resolve')
        self.parser.add_argument('-h', '--help', action=HelpAction)
        self.subparsers = self.parser.add_subparsers()

    def set_status(self, name: str, status: bool):
        if name:
            self.handlers_statuses[name] = status

    def add_handler(self, callback, event: NewMessage):
        logger.debug(f"registered callback {callback.__name__!r}")
        self.handlers.append((callback, event))

    @contextmanager
    def add_command(
        self,
        name,
        help_text,
        callback,
        description=None,
        outgoing=True,
        incoming=False,
        aliases=(),
        action=None,  # type: Union[None, ActionType, Tuple[str, ActionType]]
        registry=True,
        **kwargs
    ):
        sub_parser = self.subparsers.add_parser(
            name,
            help=help_text,
            description=description or help_text,
            conflict_handler='resolve',
            aliases=aliases,
        )
        if action:
            if isinstance(action, tuple):
                dest, action = action
            else:
                dest = 'root'
            sub_parser.add_argument(dest=dest, action=action)
        sub_parser.add_argument('-h', '--help', action=HelpAction)
        yield sub_parser
        logger.debug(f"registered command {name!r} with callback {callback.__name__!r}")
        message_matcher = NewMessage(
            cmd=(name,) + tuple(aliases),
            parser=self.parser,
            outgoing=outgoing,
            incoming=incoming,
            **kwargs,
        )
        if registry:
            self.handlers.append((callback, message_matcher))
        else:
            self.client.add_event_handler(callback, message_matcher)

    def register_handlers(self):
        for c, e in self.handlers:
            self.client.add_event_handler(c, e)
            self.set_status(e.name, True)

    def remove_handlers(self):
        for c, e in self.handlers:
            self.client.remove_event_handler(c, e)
            self.set_status(e.name, False)

    async def delayed_respond(self, event, respond, delay=3):
        _, msg = await asyncio.gather(event.delete(), event.respond(respond))
        await asyncio.sleep(delay)
        await msg.delete()

    async def handle_toggle(self, event: Event):
        first = self.handlers[0]
        toggle = first in self.client.list_event_handlers()
        if toggle:
            self.remove_handlers()
        else:
            self.register_handlers()
        toggle_text = '❌ off' if toggle else '✅ on'
        await self.delayed_respond(event, f"{USERBOT_NAME} is {toggle_text}")
        raise StopPropagation()

    async def handle_toggle_command(self, event: Event, adding: bool):
        handler_name = event.pattern_match.handler
        for c, e in self.handlers:
            if e.name == handler_name:
                if adding:
                    self.client.add_event_handler(c, e)
                    respond = f"✅ handler {handler_name!r} was started"
                else:
                    self.client.remove_event_handler(c, e)
                    respond = f"❌ handler {handler_name!r} was stopped"
                self.set_status(e.name, adding)
                await self.delayed_respond(event, respond)
                break
        else:
            respond = f"😡 no handler with name {handler_name!r} was found"
            await self.delayed_respond(event, respond)
        raise StopPropagation()

    async def handle_stop_command(self, event: Event):
        await self.handle_toggle_command(event, adding=False)

    async def handle_start_command(self, event: Event):
        await self.handle_toggle_command(event, adding=True)

    async def handle_status(self, event: Event):
        text = '\n'.join([
            f"{'✅' if status else '❌'} {handler}"
            for handler, status in self.handlers_statuses.items()
        ])
        await self.delayed_respond(event, f"```{text}```", delay=10)


def setup_handlers(client: TelegramClient):
    m = Manager(client)

    m.add_handler(handlers.handle_help, NewMessage(cmd='', outgoing=True, parser=m.parser))

    with m.add_command(
        'toggle',
        "turn on/off bot",
        m.handle_toggle,
        aliases=('to',),
        registry=False,
    ):
        pass

    with m.add_command(
        'status',
        "show handlers statuses",
        m.handle_status,
        registry=False,
    ):
        pass

    with m.add_command(
        'stop_command',
        "stop command/handler",
        m.handle_stop_command,
        aliases=('stop',),
        registry=False,
    ) as p:
        p.add_argument('handler', help='name of handler to stop')

    with m.add_command(
        'start_command',
        "start command/handler",
        m.handle_start_command,
        aliases=('start',),
        registry=False,
    ) as p:
        p.add_argument('handler', help='name of handler to start')

    with m.add_command(
        'nou',
        f"Respond to specific messages with 'no u'.",
        handlers.handle_noop,
        description=(
            f"Respond to specific incoming/outgoing messages with 'no u'. "
            f"Match regex: {NOU_PATTERN}"
        ),
        action=('help', HelpAction),
    ):
        m.add_handler(handlers.handle_nou, NewMessage(name='nou', pattern=NOU_LIST_REGEX))

    with m.add_command('hello', "say hello from userbot", handlers.handle_hello):
        pass

    with m.add_command('eval', "evaluate expression", handlers.handle_eval, aliases=('e',)) as p:
        p.add_argument('expression', action=MergeAction)

    with m.add_command(
        'sed',
        "sed substitution (aka find and replace)",
        handlers.handle_sub,
        aliases=('s',),
    ) as p:
        p.add_argument('text', help='sed substitution string')
        p.add_argument('-h', dest='highlight', action='store_true', help="highlight replaced")

    with m.add_command('timer', "timer", handlers.handle_timer, aliases=('t',)) as p:
        p.add_argument('time', help='time is seconds')
        p.add_argument('-m', dest='message', help='message to show after time is up')

    with m.add_command('google', "google search", handlers.google, aliases=('g',)) as p:
        p.add_argument('query', help='query to search', action=MergeAction)
        p.add_argument('-i', dest='image', action='store_true', help='image search')
        p.add_argument('-l', dest='let_me', action='store_true', help='"let me google for you"')

    with m.add_command('moon', "magic moon loop", handlers.magic, aliases=('m',)) as p:
        p.add_argument('text', nargs='*', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')
        p.add_argument('-w', dest='wide', action='store_true', help='use wide text')

    with m.add_command('marquee', "marquee loop", handlers.marquee, aliases=('mar',)) as p:
        p.add_argument('text', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')

    with m.add_command(
        'highlight',
        "highlight text/code block",
        handlers.highlight_code,
        aliases=('h',),
    ) as p:
        p.add_argument('text', nargs='*', action=MergeAction)
        p.add_argument('-l', dest='lang', help="programming language")
        p.add_argument('-c', dest='carbon', action='store_true', help="add carbon link")
        p.add_argument('--ln', dest='line_numbers', action='store_true', help="show line numbers")
        p.add_argument('-t', dest='theme', default='monokai', help="highlight theme")

    with m.add_command(
        'rotate',
        "rotate image in reply",
        handlers.handle_rotate,
        aliases=('r',),
    ) as p:
        p.add_argument('-a', '--angle', type=int, default=90, help="rotation angle")

    with m.add_command('loop_desc', "loop description", handlers.loop_description) as p:
        p.add_argument('-t', dest='type', help="type of description")
        p.add_argument('-s', dest='sleep', type=int, default=30, help='sleep/update interval')

    with m.add_command('loop_name', "loop name", handlers.loop_name) as p:
        p.add_argument('-s', dest='sleep', type=int, default=120, help='sleep/update interval')

    with m.add_command('logs', "show bot logs", handlers.handle_logs) as p:
        p.add_argument('-s', dest='size', type=int, default=20, help='number of lines to return')

    m.register_handlers()
    return m
