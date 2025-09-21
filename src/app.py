import mimetypes
import urllib.parse
import json
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader

# Налаштування Jinja2 для обробки шаблонів
env = Environment(loader=FileSystemLoader('templates'))

# Порт для роботи сервера
PORT = 3000

# Шлях до директорій
STORAGE_DIR = Path('storage')
DATA_FILE = STORAGE_DIR / 'data.json'
STATIC_DIR = Path('static')

# Створення директорій та файлів, якщо вони не існують
STORAGE_DIR.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

class SimpleServer(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        
        # Обробка маршрутів
        if pr_url.path == '/':
            self.send_html('index.html')
        elif pr_url.path == '/message.html':
            self.send_html('message.html')
        elif pr_url.path == '/read':
            self.read_data()
        elif pr_url.path.startswith('/static/'):
            self.send_static(pr_url.path)
        else:
            self.send_html('error.html', 404)

    def do_POST(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/message':
            data = self.rfile.read(int(self.headers['Content-Length']))
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            
            # Збереження даних у JSON-файл
            with open(DATA_FILE, 'r+') as f:
                try:
                    file_data = json.load(f)
                except json.JSONDecodeError:
                    file_data = {}
                file_data[str(datetime.now())] = data_dict
                f.seek(0)
                json.dump(file_data, f, indent=2)

            self.send_html('index.html', 302)
        else:
            self.send_html('error.html', 404)

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        template = env.get_template(filename)
        self.wfile.write(template.render().encode())

    def send_static(self, file_path):
        file_path_relative = Path(file_path[1:])
        if file_path_relative.exists():
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(file_path_relative)
            self.send_header('Content-type', mime_type or 'application/octet-stream')
            self.end_headers()
            with open(file_path_relative, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_html('error.html', 404)

    def read_data(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(DATA_FILE, 'r') as f:
            messages = json.load(f)

        template = env.get_template('read.html')
        self.wfile.write(template.render(messages=messages).encode())

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), SimpleServer)
    print(f"Server started on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run_server()