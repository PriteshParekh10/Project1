import socket
import threading
import os

HOST = 'localhost'
PORT = 8080
ROOT_DIR = './public'
REDIRECTS = {
    '/page1.html': '/page2.html'
}

STATUS_CODES = {
    200: 'OK',
    301: 'Moved Permanently',
    404: 'Not Found'
}

CONTENT_TYPES = {
    '.html': 'text/html',
    '.jpg': 'image/jpeg',
    '.png': 'image/png'
}

def handle_client(connection, address):
    print(f"Connection from {address}")
    request = connection.recv(1024).decode()
    print("Request:\n" + request)
    lines = request.splitlines()
    if len(lines) > 0:
        method, path, _ = lines[0].split()
        if method == 'GET':
            if path in REDIRECTS:
                redirect_path = REDIRECTS[path]
                response = f"HTTP/1.1 301 Moved Permanently\r\n"
                response += f"Location: http://{HOST}:{PORT}{redirect_path}\r\n\r\n"
                connection.sendall(response.encode())
            else:
                if path == '/':
                    path = '/index.html'
                file_path = ROOT_DIR + path
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as file:
                        content = file.read()
                    ext = os.path.splitext(file_path)[1]
                    content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')
                    response = f"HTTP/1.1 200 OK\r\n"
                    response += f"Content-Type: {content_type}\r\n"
                    response += f"Content-Length: {len(content)}\r\n\r\n"
                    connection.sendall(response.encode() + content)
                else:
                    with open(ROOT_DIR + '/404.html', 'rb') as file:
                        content = file.read()
                    response = f"HTTP/1.1 404 Not Found\r\n"
                    response += "Content-Type: text/html\r\n"
                    response += f"Content-Length: {len(content)}\r\n\r\n"
                    connection.sendall(response.encode() + content)
    connection.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server running on http://{HOST}:{PORT}")
        while True:
            client_connection, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_connection, client_address))
            client_thread.start()

start_server()
