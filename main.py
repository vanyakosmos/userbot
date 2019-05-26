import logging
import re
from contextlib import contextmanager

from telethon import TelegramClient
from telethon import events

import handlers
from persistence import load_session_file, save_before_term
from settings import API_HASH, API_ID, NOU_LIST, USERBOT_NAME, USER_PASSWORD, USER_PHONE
import argparse

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

save_before_term()
load_session_file()

client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)
client.parse_mode = 'md'


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        pass


class HelpAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, nargs=0)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, parser.format_help())


class MergeAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, nargs='+', type=str)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))


class NewMessage(events.NewMessage):
    def __init__(self, *args, parser=None, cmd=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser
        if cmd:
            self.cmd = re.compile(f">\\s*({cmd}.*)").match
        else:
            self.cmd = None

    def _message_filter_event(self, event):
        if self._no_check:
            return event

        if self.incoming and event.message.out:
            return
        if self.outgoing and not event.message.out:
            return
        if self.forwards is not None:
            if bool(self.forwards) != bool(event.message.fwd_from):
                return

        if self.from_users is not None:
            if event.message.from_id not in self.from_users:
                return

        if self.pattern:
            match = self.pattern(event.message.message or '')
            if not match:
                return
            event.pattern_match = match

        if self.cmd:
            match = self.cmd(event.message.message or '')
            if not match:
                return
            text = match[1]
            args, _ = self.parser.parse_known_args(text.split())
            if not args:
                return
            event.pattern_match = args

        return self._filter_event(event)


def setup():
    async def handle_toggle(event):
        first = handler_callbacks[0]
        toggle = first in client.list_event_handlers()
        await event.reply(f"toggle {toggle}")
        if toggle:
            for c, e in handler_callbacks:
                client.remove_event_handler(c, e)
        else:
            for c, e in handler_callbacks:
                client.add_event_handler(c, e)

    parser = ArgumentParser(prog='USERBOT', conflict_handler='resolve')
    parser.add_argument('-h', '--help', action=HelpAction)
    parser.add_argument('-t', '--toggle', action=HelpAction)
    subparsers = parser.add_subparsers()

    client.add_event_handler(
        handlers.handle_help,
        NewMessage(outgoing=True, cmd='-h', parser=parser),
    )
    client.add_event_handler(
        handle_toggle,
        NewMessage(outgoing=True, cmd='-t', parser=parser),
    )
    handler_callbacks = []

    @contextmanager
    def add_handler(name, help_text, callback, outgoing=True, incoming=False, **kwargs):
        sub_parser = subparsers.add_parser(name, help=help_text, conflict_handler='resolve')
        sub_parser.add_argument('-h', '--help', action=HelpAction)
        yield sub_parser
        handler_callbacks.append((
            callback,
            NewMessage(cmd=name, parser=parser, outgoing=outgoing, incoming=incoming, **kwargs)
        ))

    with add_handler('e', "evaluate expression", handlers.calculator) as p:
        p.add_argument('expression', action=MergeAction)

    with add_handler('s', "find and replace", handlers.sub) as p:
        p.add_argument('a', help='what to replace')
        p.add_argument('b', help='with what replace')

    with add_handler('t', "timer", handlers.timer) as p:
        p.add_argument('time', help='time is seconds')
        p.add_argument('-m', dest='message', help='message to show after time is up')

    with add_handler('g', "google search", handlers.google) as p:
        p.add_argument('query', help='query to search', action=MergeAction)
        p.add_argument('-i', dest='image', action='store_true', help='image search')
        p.add_argument('-l', dest='let_me', action='store_true', help='"let me google for you"')

    with add_handler('m', "magic moon loop", handlers.magic) as p:
        p.add_argument('text', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')
        p.add_argument('-w', dest='wide', action='store_true', help='use wide text')

    with add_handler('mar', "marquee loop", handlers.marquee) as p:
        p.add_argument('text', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')

    with add_handler('h', "highlight text/code block", handlers.highlight_code) as p:
        p.add_argument('text', action=MergeAction)
        p.add_argument('-l', dest='lang', help="programming language")
        p.add_argument('-c', dest='carbon', action='store_true', help="add carbon link")
        p.add_argument('--ln', dest='line_numbers', action='store_true', help="show line numbers")

    with add_handler('loop_desc', "loop random description", handlers.loop_description):
        pass

    # no u
    nou_pattern = "|".join(NOU_LIST)
    nou_pattern = f'^.*({nou_pattern}).*$'
    handler_callbacks.append((handlers.nou, NewMessage(pattern=nou_pattern)))

    for cb, event in handler_callbacks:
        client.add_event_handler(cb, event)


if __name__ == '__main__':
    logger.info("setting up...")
    setup()
    logger.info("starting...")
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()
