from quart import Quart, request, render_template
from telethon import TelegramClient

from config import API_ID, API_HASH
from main import setup_handlers

app = Quart(__name__, template_folder='templates')
db = {}


async def try_connect(client):
    if not client.is_connected():
        await client.connect()


async def get_client(phone):
    client = TelegramClient(f'SERVER:{phone}', API_ID, API_HASH)
    client.parse_mode = 'html'
    await try_connect(client)
    return client


@app.route('/', methods=['GET', 'POST'])
async def index_view():
    form = await request.form

    if 'phone' in form:
        phone = form['phone']
        client = await get_client(phone)
        if phone not in db:
            setup_handlers(client)
            db[phone] = client
        if 'code' not in form and not await client.is_user_authorized():
            await client.send_code_request(phone)
    else:
        phone = None
        client = None

    if phone and 'code' in form:
        await client.sign_in(code=form['code'])

    if client and await client.is_user_authorized():
        me = await client.get_me()
        return await render_template('me.html', username=me.username, already='code' not in form)

    if not phone:
        return await render_template('index.html')

    return await render_template('code.html')


def main():
    # todo load sessions and setup mutual loop
    app.run()


if __name__ == '__main__':
    main()
