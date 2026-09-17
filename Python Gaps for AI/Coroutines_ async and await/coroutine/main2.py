import asyncio

async def greet():
    print('Hello')

def main():
    asyncio.run(greet())

if __name__ == "__main__":
    main()