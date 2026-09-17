import time, asyncio

async def load_db():
    print('I am loading data from database...')
    await asyncio.sleep(2)
    print('DB Data Loaded')

async def load_api():
    print('I am calling API and getting some json...')
    await asyncio.sleep(3)
    print('JSON Loaded')

async def running():
    await asyncio.gather(load_db(), load_api())

async def main():
    start_time = time.time()

    task_db = asyncio.create_task(load_db())
    task_api = asyncio.create_task(load_api())

    await task_db
    await task_api

    end_time = time.time()

    total_time_taken = end_time - start_time
    print(f'Total time takes: {total_time_taken}')
    

if __name__ == "__main__":
    asyncio.run(main())