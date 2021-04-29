import threading
import http.server
import socket
from contextlib import closing
from django.core.cache import cache


def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

# This initizes the cronjob server
def init():
    cache.delete("ImapFetcher")

    PORT = 5000
    DIRECTORY = "/tmp/"
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

    if not check_socket("127.0.0.1", PORT):
        server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
        return server, startThread(server)
    else:
        return None, None

def startThread(server):
    # This function serves email messages as small websites
    # create a dummy favicon.ico
    open("/tmp/favicon.ico", "a").close()
    thread = threading.Thread(target=server.serve_forever)
    thread.deamon = True
    thread.start()
    print("--- WEB Server started on port 5000 ---")

    return thread