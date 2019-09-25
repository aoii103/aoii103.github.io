import aiohttp
import asyncio

tasks = ['http://www.baidu.com']*10

import aiohttp
import asyncio


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        await session.get(url)

async def run_all():
    await asyncio.gather(*[fetch(url) for url in tasks ])

asyncio.run(run_all())
