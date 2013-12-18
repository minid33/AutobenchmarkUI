from autobenchmarkui import app, configure_app

cfg = configure_app()

if __name__ == '__main__':  # pragma: no cover
    app.run(host=cfg.HOST, port=cfg.PORT)
