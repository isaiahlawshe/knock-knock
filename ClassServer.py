from socket import *
import random

def loadJokes():
    jokes = []

    with open("jokes.txt", "r") as jokeFile:
        for line in jokeFile:
            line = line.strip()

            if "|" in line:
                name, punchline = line.split("|", 1)
                jokes.append((name.strip(), punchline.strip()))

    return jokes


def SimpleServer():
    jokes = loadJokes()

    if len(jokes) == 0:
        print("No jokes found in jokes.txt")
        return

    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    ip = "0.0.0.0"
    port = 2603

    s.bind((ip, port))
    s.listen()

    displayIP = gethostbyname(gethostname())
    print("Listening on", displayIP, "port", port)
    print("Server ready")


    while True:
        print("Waiting")
        conn, addr = s.accept()
        print("Connected by", addr)

        try:
            name, punchline = random.choice(jokes)

            message = "Knock-Knock"
            conn.sendall(message.encode("utf-8"))
            print("Sent:", message)

            message = conn.recv(1024).decode("utf-8")
            print("Received:", message)

            if message != "\t" + name + " who?":
                conn.sendall(b"Protocol Violation")
                continue

            conn.sendall(name.encode("utf-8"))
            print("Sent:", name)

            message = conn.recv(1024).decode("utf-8")
            print("Received:", message)

            if message != "\t" + name + " who?":
                conn.sendall(b"Protocol Violation")
                continue

            conn.sendall(punchline.encode("utf-8"))
            print("Sent:", punchline)

        except (ConnectionResetError, ConnectionAbortedError):
            print("Client disconnected unexpectedly")

        finally:
            conn.close()


SimpleServer()