from functools import partial
from collections import namedtuple
from aiohttp import web
import aiohttp
import aiofiles
import asyncio
import os.path
import argparse
import yaml


async def handle(request, config):
    port = config.port
    directory = config.directory
    nodes = config.nodes
    save_files = config.save_files

    file_name = request.match_info.get('file_name', '')
    asked_str = request.rel_url.query.get('asked', '')

    asked = {int(node) for node in asked_str.split(',') if node}
    asked.add(port)
    to_ask = nodes.difference(asked)

    file_path = os.path.join(directory, file_name)
    if not os.path.isfile(file_path):
        content_b = await async_fetch(file_name, to_ask=to_ask, asked=asked)
        if content_b is None:
            return web.Response(status=404, text=f'File "{file_name}" not found.')
        if save_files:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content_b)
        return web.Response(body=content_b)
    return web.FileResponse(path=file_path)


async def async_fetch(file_name, to_ask: set, asked: set):
    if not to_ask:
        return None
    futures = [fetch_file(file_name, ask=node, asked=asked | to_ask) for node in to_ask]
    done, _ = await asyncio.wait(futures)
    for response in done:
        status, content_b = response.result()
        if status == 200:
            return content_b

    return None


async def fetch_file(file_name, ask: int, asked: set):
    async with aiohttp.ClientSession() as session:
        url = f'http://localhost:{ask}/{file_name}'
        asked_str = ','.join(str(i) for i in asked)
        async with session.get(url + '?asked=' + asked_str) as response:
            return response.status, await response.content.read()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./config1.yaml',
        help='Configuration path')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    config_path = args.path
    with open(config_path, 'r') as f:
        config = yaml.load(f.read())

    port = config['port']
    directory = config['directory']
    nodes = set(config['nodes'])
    save_files = config['save_files']

    Config = namedtuple('Config', ['port', 'directory', 'nodes', 'save_files'])
    config = Config(port, directory, nodes, save_files)

    handle = partial(handle, config=config)

    app = web.Application()
    app.add_routes([
        web.get('/', handle),
        web.get('/{file_name}', handle),
    ])

    web.run_app(app, port=port)
