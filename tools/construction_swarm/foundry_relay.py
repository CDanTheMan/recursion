"""Trusted stdio-to-private-Unix-socket MCP relay inside the client namespace."""
import socket
import sys
import threading


def main():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
        channel.connect('/run/foundry.sock')

        def send():
            while line := sys.stdin.buffer.readline(1048577):
                if len(line) > 1048576 or not line.endswith(b'\n'):
                    break
                channel.sendall(line)
            channel.shutdown(socket.SHUT_WR)

        threading.Thread(target=send, daemon=True).start()
        while data := channel.recv(65536):
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
