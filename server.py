if __name__ == '__main__':
    import uvicorn

    from tdb.poc_websockets.server import app

    uvicorn.run(app.app, host='localhost', port=8000, log_level='debug')
