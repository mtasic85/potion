# http://aiohttp.readthedocs.org/en/stable/client.html
# https://docs.python.org/3/library/asyncio-task.html#example-parallel-execution-of-tasks

# real  0m0.415s
# user  0m0.307s
# sys   0m0.020s

import asyncio
import aiohttp

loop = asyncio.get_event_loop()

async def fetch_page(session, url):
    with aiohttp.Timeout(10):
        async with session.get(url) as response:
            assert response.status == 200
            return await response.read()

with aiohttp.ClientSession(loop=loop) as session:
    tasks = [
        asyncio.ensure_future(fetch_page(session, 'http://ipinfo.io/ip'))
        for i in range(10)
    ]

    done_tasks, not_done_tasks = loop.run_until_complete(asyncio.wait(tasks))
    results = [task.result() for task in done_tasks]
    print(results)
