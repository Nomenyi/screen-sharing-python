#! /usr/bin/python3
# -*- coding: utf-8 -*-

# python 3
# (C) Angelico Denis

#from client import WIDTH
import socket
import threading
import zlib

import mss

# Dimensions des captures d'écran, plus petit = plus rapide
WIDTH = 900
HEIGHT = 700


def retreive_screenshot(conn):
    """ Envoi des captures d'écran via un socket. """

    # Si utilisation via SSH, il est possible de spécifier le $DISPLAY à utilser :
    # with mss(display=':0.0') as sct:
    with mss.mss() as sct:
        # La région de l'écran à capturer
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            # Prendre la capture d'écran
            img = sct.grab(rect)
            # Ajuster le niveau de compression ici (0-9)
            pixels = zlib.compress(img.rgb, 6)

            # Envoie de la taille de la taille des pixels
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Envoie de la taille des pixels
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Envoi des pixels compressés
            conn.sendall(pixels)


def main(host='192.168.1.102', port=5000):
    with socket.socket() as sock:
        sock.bind((host, port))
        sock.listen()
        print('Server started.')

        while 'connected':
            conn, addr = sock.accept()
            print('Client connected IP:', addr)
            thread = threading.Thread(target=retreive_screenshot, args=(conn,))
            thread.start()


if __name__ == '__main__':
    import argparse
    import sys

    cli_args = argparse.ArgumentParser()
    cli_args.add_argument('--port', default=5000, type=int)
    options = cli_args.parse_args(sys.argv[1:])

    main(port=options.port)
