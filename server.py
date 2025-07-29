from http.server import HTTPServer, BaseHTTPRequestHandler
from html import escape
import time
import os

HOST = "192.168.56.1"  # IP local
PORT = 9999

class luanHTTP(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.wfile.write(bytes(f'{{"time": "{data}"}}', "utf-8"))

    def do_GET(self):
        requested_path = self.path.lstrip('/')
        local_path = os.path.join(os.getcwd(), requested_path)

        if os.path.isfile(local_path):
            try:
                with open(local_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(local_path)}"')
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Erro ao abrir o arquivo: {e}")
            return
        
        if os.path.isdir(local_path):
            try:
                list_dir = os.listdir(local_path)
            except OSError:
                self.send_error(404, "Diretório não encontrado")
                return

            list_dir.sort()
            r = []
            displaypath = escape(self.path)

            # HTML
            r.append('<!DOCTYPE html>')
            r.append('<html><head>')
            r.append('<meta charset="utf-8">')
            r.append('<title>Trabalho 2 - Listagem de arquivos</title>')
            r.append('</head><body>')
            r.append('<h1>Trabalho 2 - Listagem de arquivos</h1>')
            r.append('<hr><ul>')

            for name in list_dir:
                fullname = os.path.join(local_path, name)
                displayname = linkname = name
                if os.path.isdir(fullname):
                    displayname += "/"
                    linkname += "/"
                r.append(f'<li><a href="{escape(linkname)}">{escape(displayname)}</a></li>')

            r.append('</ul><hr></body></html>')

            encoded = "\n".join(r).encode('utf-8', 'surrogateescape')
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        
        self.send_error(404, "Arquivo ou diretório não encontrado")

server = HTTPServer((HOST, PORT), luanHTTP)
print(f"Servidor local ativo em http://{HOST}:{PORT}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
server.server_close()
print("Servidor local inativo")
