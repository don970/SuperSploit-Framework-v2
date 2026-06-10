import socket
import ssl
import threading
import time

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='/home/donald/.SuperSploit/.data/.config/c2_cert.pem', 
                            keyfile='/home/donald/.SuperSploit/.data/.config/c2_key.pem')
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5001))
    server.listen(1)
    print("[*] Server listening on 127.0.0.1:5001")
    
    try:
        raw_client, addr = server.accept()
        print(f"[*] Connection from {addr}")
        try:
            client = context.wrap_socket(raw_client, server_side=True)
            print("[+] SSL handshake successful")
            client.close()
        except Exception as e:
            print(f"[-] SSL Error: {e}")
    finally:
        server.close()

def start_client():
    time.sleep(1)
    print("[*] Client connecting...")
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Simulate stager behavior
        client_socket = ssl_context.wrap_socket(raw_socket, server_hostname='127.0.0.1')
        client_socket.connect(('127.0.0.1', 5001))
        print("[+] Client handshake successful")
        client_socket.close()
    except Exception as e:
        print(f"[-] Client SSL Error: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=start_server)
    t.start()
    start_client()
    t.join()
