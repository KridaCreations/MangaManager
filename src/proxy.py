# import socket
# import select
# import http.server
# import socketserver

# PORT = 8080  # Proxy server runs on this port

# class ProxyHandler(http.server.BaseHTTPRequestHandler):
#     def do_CONNECT(self):
#         """Handles HTTPS (CONNECT) requests by tunneling them."""
#         target_host, target_port = self.path.split(":")
#         target_port = int(target_port)

#         try:
#             with socket.create_connection((target_host, target_port)) as remote_socket:
#                 self.send_response(200, "Connection Established")
#                 self.end_headers()

#                 # Transfer data between client and target server
#                 self._tunnel_data(self.connection, remote_socket)

#         except Exception as e:
#             self.send_error(502, f"Error connecting to {self.path}: {e}")

#     def _tunnel_data(self, client_socket, remote_socket):
#         """Transfers data between client and server using select for efficiency."""
#         sockets = [client_socket, remote_socket]
#         try:
#             while True:
#                 readable, _, _ = select.select(sockets, [], [])
                
#                 for sock in readable:
#                     data = sock.recv(4096)
#                     if not data:
#                         return  # Connection closed

#                     # Send received data to the opposite socket
#                     target_sock = remote_socket if sock is client_socket else client_socket
#                     target_sock.sendall(data)

#         except Exception as e:
#             print(f"Tunnel error: {e}")

# # Start Proxy Server
# with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), ProxyHandler) as httpd:
#     print(f"Proxy server running at port {PORT}")
#     httpd.serve_forever()



import socket
import select
import http.server
import socketserver

PORT = 8080  # Proxy server runs on this port

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        """Handles HTTPS (CONNECT) requests by tunneling them."""
        target_host, target_port = self.path.split(":")
        target_port = int(target_port)

        try:
            with socket.create_connection((target_host, target_port)) as remote_socket:
                self.send_response(200, "Connection Established")
                self.end_headers()

                # Transfer data between client and target server
                self._tunnel_data(self.connection, remote_socket)

        except Exception as e:
            self.send_error(502, f"Error connecting to {self.path}: {e}")

    def do_GET(self):
        """Handles HTTP GET requests by forwarding them."""
        url = self.path
        self.send_error(403, f"HTTP Proxy Not Implemented for {url}")  # Block for now

    def _tunnel_data(self, client_socket, remote_socket):
        """Transfers data between client and server using select for efficiency."""
        sockets = [client_socket, remote_socket]
        try:
            while True:
                readable, _, _ = select.select(sockets, [], [])
                
                for sock in readable:
                    data = sock.recv(4096)
                    if not data:
                        return  # Connection closed

                    # Send received data to the opposite socket
                    target_sock = remote_socket if sock is client_socket else client_socket
                    target_sock.sendall(data)

        except Exception as e:
            print(f"Tunnel error: {e}")

# Start Proxy Server
with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), ProxyHandler) as httpd:
    print(f"Proxy server running at port {PORT}")
    httpd.serve_forever()
