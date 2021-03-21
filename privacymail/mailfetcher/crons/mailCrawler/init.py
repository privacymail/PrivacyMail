import threading
from django.core.cache import cache
import http.server

# This initizes the cronjob server
def init():
    cache.delete("ImapFetcher")

    PORT = 5000
    DIRECTORY = "/tmp/"
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)

    return server, startThread(server)


def startThread(server):
    # This function serves email messages as small websites
    # create a dummy favicon.ico
    open("/tmp/favicon.ico", "a").close()
    thread = threading.Thread(target=server.serve_forever)
    thread.deamon = True
    thread.start()
    print("--- WEB Server started on port 5000 ---")

    return thread