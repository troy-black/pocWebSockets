if __name__ == '__main__':
    import asyncio

    from tdb.poc_websockets.client.client import Client

    client = Client()

    asyncio.run(client.run())
