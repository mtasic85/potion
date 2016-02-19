# env DB_USER= DB_PASS= DB_DB= DB_HOST= DB_PORT= time python -B -m timeit 'import mysql0; mysql0.loop.run_until_complete(mysql0.go(mysql0.loop))'
import os
import asyncio
from aiomysql.sa import create_engine
import sqlalchemy as sa

DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_DB = os.environ['DB_DB']
DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ['DB_PORT'])

metadata = sa.MetaData()

tbl = sa.Table('tbl', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('val', sa.String(255)),
)

async def create_all(loop):
    engine = await create_engine(user=DB_USER,
                                 password=DB_PASS,
                                 db=DB_DB,
                                 host=DB_HOST,
                                 port=DB_PORT,
                                 loop=loop)

    async with engine.acquire() as conn:
        for t in metadata.sorted_tables:
            try:
                q = sa.schema.CreateTable(t)
                await conn.execute(q)
            except Exception as e:
                pass

async def drop_all(loop):
    engine = await create_engine(user=DB_USER,
                                 password=DB_PASS,
                                 db=DB_DB,
                                 host=DB_HOST,
                                 port=DB_PORT,
                                 loop=loop)

    async with engine.acquire() as conn:
        for t in metadata.sorted_tables:
            try:
                q = sa.schema.DropTable(t)
                await conn.execute(q)
            except Exception as e:
                pass

async def go(loop):
    engine = await create_engine(user=DB_USER,
                                 password=DB_PASS,
                                 db=DB_DB,
                                 host=DB_HOST,
                                 port=DB_PORT,
                                 loop=loop)

    async with engine.acquire() as conn:
        q = tbl.insert().values(val='abc')
        await conn.execute(q)

        q = tbl.select()
        res = await conn.execute(q)
        
        for row in res:
            print(row.id, row.val)

    engine.close()
    await engine.wait_closed()

loop = asyncio.get_event_loop()

if __name__ == '__main__':
    loop.run_until_complete(drop_all(loop))
    loop.run_until_complete(create_all(loop))
    loop.run_until_complete(go(loop))
