import socket
import base64
import threading

# Configuration
HOST = '127.0.0.1'
PORT = 2525
VALID_USER = 'admin'
VALID_PASS = 'password'

def handle_client(conn, addr):
    print(f"\n[+] Connection established from {addr}")
    
    # Send SMTP greeting
    conn.sendall(b"220 FakeSMTP Server Ready\r\n")
    
    authenticated = False
    state = "INIT"
    
    try:
        while True:
            data = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            if not data:
                break
            
            print(f"C: {data}")
            
            if data.upper().startswith("EHLO") or data.upper().startswith("HELO"):
                # Advertise AUTH capability
                conn.sendall(b"250-fake.smtp.local Hello\r\n")
                conn.sendall(b"250-AUTH LOGIN\r\n")
                conn.sendall(b"250 OK\r\n")
            
            elif data.upper().startswith("AUTH LOGIN"):
                parts = data.split()
                if len(parts) > 2:
                    # Client sent AUTH LOGIN <username>
                    try:
                        username = base64.b64decode(parts[2]).decode('utf-8')
                        if username == VALID_USER:
                            conn.sendall(b"334 UGFzc3dvcmQ6\r\n") # "Password:"
                            state = "AUTH_PASS"
                        else:
                            conn.sendall(b"535 Authentication failed\r\n")
                            state = "INIT"
                    except:
                        conn.sendall(b"501 Invalid base64\r\n")
                        state = "INIT"
                else:
                    conn.sendall(b"334 VXNlcm5hbWU6\r\n") # "Username:"
                    state = "AUTH_USER"
            
            elif state == "AUTH_USER":
                try:
                    username = base64.b64decode(data).decode('utf-8')
                    if username == VALID_USER:
                        conn.sendall(b"334 UGFzc3dvcmQ6\r\n") # "Password:" in base64
                        state = "AUTH_PASS"
                    else:
                        conn.sendall(b"535 Authentication failed\r\n")
                        state = "INIT"
                except:
                    conn.sendall(b"501 Invalid base64\r\n")
                    state = "INIT"
                    
            elif state == "AUTH_PASS":
                try:
                    password = base64.b64decode(data).decode('utf-8')
                    if password == VALID_PASS:
                        conn.sendall(b"235 Authentication successful\r\n")
                        authenticated = True
                    else:
                        conn.sendall(b"535 Authentication failed\r\n")
                except:
                    conn.sendall(b"501 Invalid base64\r\n")
                state = "INIT"
                
            elif data.upper().startswith("MAIL FROM:"):
                if not authenticated:
                    conn.sendall(b"530 5.7.1 Authentication required\r\n")
                else:
                    conn.sendall(b"250 OK\r\n")
                    
            elif data.upper().startswith("RCPT TO:"):
                if not authenticated:
                    conn.sendall(b"530 5.7.1 Authentication required\r\n")
                else:
                    conn.sendall(b"250 OK\r\n")
                    
            elif data.upper() == "DATA":
                if not authenticated:
                    conn.sendall(b"530 5.7.1 Authentication required\r\n")
                else:
                    conn.sendall(b"354 End data with <CR><LF>.<CR><LF>\r\n")
                    state = "DATA"
                    email_data = []
                    
            elif state == "DATA":
                if data == ".":
                    print("\n--- Received Email Content ---")
                    print("\n".join(email_data))
                    print("------------------------------\n")
                    conn.sendall(b"250 Message queued for delivery\r\n")
                    state = "INIT"
                else:
                    email_data.append(data)
                    
            elif data.upper() == "QUIT":
                conn.sendall(b"221 Bye\r\n")
                break
                
            elif state == "INIT":
                conn.sendall(b"500 Command unrecognized\r\n")

    except Exception as e:
        print(f"[-] Error handling client: {e}")
    finally:
        conn.close()
        print(f"[-] Connection closed with {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Fake SMTP Server listening on {HOST}:{PORT}")
    print(f"[*] Configured Credentials -> User: '{VALID_USER}', Pass: '{VALID_PASS}'")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()
