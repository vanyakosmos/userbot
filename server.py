"""
Run multiple telegram clients and auth server.
"""
import glob
import logging
import re

from quart import Quart, request, render_template
from telethon import TelegramClient
import asyncio

from config import API_ID, API_HASH, DEBUG, configure_logging
from manager import setup_handlers

configure_logging(level=DEBUG and logging.DEBUG)
logger = logging.getLogger(__name__)
app = Quart(__name__, template_folder='templates')
db = {}


def session_name(phone):
    return f'SERVER:{phone}'


async def try_connect(client):
    if not client.is_connected():
        await client.connect()


async def get_client(phone, **kwargs):
    client = TelegramClient(session_name(phone), API_ID, API_HASH, **kwargs)
    client.parse_mode = 'md'
    setup_handlers(client)
    await try_connect(client)
    return client


@app.route('/', methods=['GET', 'POST'])
async def index_view():
    form = await request.form
    logger.debug(f"received form {form}")

    if 'phone' in form:
        phone = form['phone']

        if phone in db:
            logger.debug(f"phone {phone} is in registry")
            client = db[phone]
        else:
            logger.debug(f"phone {phone} was not in registry")
            client = await get_client(phone)
            db[phone] = client
        if 'code' not in form and not await client.is_user_authorized():
            logger.debug(f"sending code for {phone}")
            await client.send_code_request(phone)
    else:
        logger.debug(f"no phone provided")
        phone = None
        client = None

    if phone and 'code' in form:
        logger.debug(f"trying to sign in for {phone}")
        await client.sign_in(code=form['code'])

    if client and await client.is_user_authorized():
        logger.debug(f"user authenticated")
        me = await client.get_me()
        return await render_template('me.html', username=me.username, already='code' not in form)

    if not phone:
        logger.debug(f"show phone form")
        return await render_template('index.html')

    logger.debug(f"show phone-code form")
    return await render_template('code.html')


def load_sessions(loop):
    for s in glob.glob('SERVER:*.session'):
        phone = re.match(r'^SERVER:(.+)\.session$', s)[1]
        client = loop.run_until_complete(get_client(phone, loop=loop))
        setup_handlers(client)
        db[phone] = client
    print(db)


def main():
    # todo: persist sessions on exit
    # todo: load from redis on start
    # todo: add master key
    # todo: add password processing

    loop = asyncio.get_event_loop()
    load_sessions(loop)
    app.run(loop=loop)


if __name__ == '__main__':
    main()
