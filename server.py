"""
Run multiple telegram clients and auth server.
"""
import asyncio
import atexit
import logging

from quart import Quart, render_template, request

from config import DEBUG, configure_logging
from registry import Registry, registry

configure_logging(level=DEBUG and logging.DEBUG)
logger = logging.getLogger(__name__)
app = Quart(__name__, template_folder='templates')


@app.route('/', methods=['GET', 'POST'])
async def index_view():
    form = await request.form
    logger.debug(f"received form {form}")

    if 'phone' not in form:
        logger.debug(f"show phone form")
        return await render_template('index.html')

    phone = form['phone']

    if phone in registry:
        logger.debug(f"phone {phone} is in registry")
        client = registry.get_client(phone)
    else:
        logger.debug(f"phone {phone} was not in registry")
        client = await Registry.make_client(phone)
        registry.save_client(phone, client)
    if 'code' not in form and not await client.is_user_authorized():
        logger.debug(f"sending code for {phone}")
        await client.send_code_request(phone)

    if 'code' in form:
        logger.debug(f"trying to sign in for {phone}")
        await client.sign_in(code=form['code'])

    if await client.is_user_authorized():
        logger.debug(f"user authenticated")
        me = await client.get_me()
        return await render_template('me.html', username=me.username, already='code' not in form)

    logger.debug(f"show phone-code form")
    return await render_template('code.html')


def main():
    # todo: add master key
    # todo: add password processing
    # todo: restyle views
    # todo: save phone in cookies or localStorage

    loop = asyncio.get_event_loop()
    atexit.register(registry.disconnect_clients)
    registry.load_sessions(loop)
    app.run(loop=loop)


if __name__ == '__main__':
    main()
