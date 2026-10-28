import socket
import random
import threading

HOST = "0.0.0.0"
PORT = 2605

jokes = []
jokes_lock = threading.Lock()

def load_jokes():
    with open("jokes.txt", "r") as file:
        for line in file:
            parts = line.strip().split("|")
            if len(parts) == 3:
                jokes.append((parts[0], parts[1], parts[2]))

load_jokes()
print("Jokes loaded:", len(jokes))


def handle_client(conn, addr):
    print("Connected by", addr)

    try:
        request = conn.recv(1024).decode().strip()
        print("Received:", request)

        if request not in ("HEAR", "TELL"):
            conn.sendall(b"Protocol Violation")
            return

        if request == "HEAR":
            with jokes_lock:
                if not jokes:
                    conn.sendall(b"Protocol Violation")
                    return

                name, punchline, source_ip = random.choice(jokes)

            conn.sendall(b"Knock-Knock")

            reply = conn.recv(1024).decode().strip()
            if reply != "Who's there?":
                conn.sendall(b"Protocol Violation")
                return

            conn.sendall(name.encode())

            reply = conn.recv(1024).decode().strip()
            if reply != name + " who?":
                conn.sendall(b"Protocol Violation")
                return

            conn.sendall(punchline.encode())

        elif request == "TELL":
            conn.sendall(b"Ok, tell me a joke.")

            reply = conn.recv(1024).decode().strip()
            if reply != "Knock-Knock":
                conn.sendall(b"Protocol Violation")
                return

            conn.sendall(b"\tWho's there?")

            name = conn.recv(1024).decode().strip()
            if not name:
                conn.sendall(b"Protocol Violation")
                return

            with jokes_lock:
                duplicate = any(joke[0] == name for joke in jokes)

            if duplicate:
                conn.sendall(b"I've heard that one already")

                reply = conn.recv(1024).decode().strip()
                if reply != "Ok, Sorry":
                    conn.sendall(b"Protocol Violation")

                return

            conn.sendall((name + " who?").encode())

            punchline = conn.recv(1024).decode().strip()
            if not punchline:
                conn.sendall(b"Protocol Violation")
                return

            source_ip = addr[0]

            with jokes_lock:
                # Check again in case another client added this joke.
                duplicate = any(joke[0] == name for joke in jokes)

                if not duplicate:
                    jokes.append((name, punchline, source_ip))

                    with open("jokes.txt", "a") as file:
                        file.write(
                            f"{name}|{punchline}|{source_ip}\n"
                        )

            if duplicate:
                conn.sendall(b"I've heard that one already")
                return

    except (ConnectionError, OSError) as error:
        print("Client connection error:", error)

    finally:
        conn.close()



def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print(f"Generalized server listening on port {PORT}")

    while True:
        conn, addr = s.accept()
        print("Waiting for clients...")

        client_thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )
        client_thread.start()


if __name__ == "__main__":
    start_server()