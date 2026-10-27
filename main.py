#!/usr/bin/env python3
"""Compartilha uma pasta com quem está na mesma rede, em um comando.

    python main.py
    python main.py --pasta ~/Downloads --porta 8080

O `python -m http.server` já faz o básico. O que falta nele é justamente o que
trava todo mundo: ele imprime 0.0.0.0, e ninguém sabe qual endereço digitar no
celular. Aqui o endereço certo aparece na tela.
"""
import argparse
import http.server
import socket
import socketserver
from functools import partial
from pathlib import Path


def ip_da_rede():
    """O IP que as outras máquinas enxergam.

    O truque do socket UDP: não envia pacote nenhum, mas obriga o sistema a
    escolher a interface que sairia para a internet -- que é a mesma do
    roteador de casa. Mais confiável que gethostbyname, que em muita máquina
    devolve 127.0.0.1.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Reutilizavel(socketserver.TCPServer):
    # Sem isto, parar e subir de novo na mesma porta dá "address already in
    # use" por alguns minutos.
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description="servidor de arquivos da rede local")
    ap.add_argument("--pasta", type=Path, default=Path("."))
    ap.add_argument("--porta", type=int, default=8000)
    ap.add_argument("--so-mostrar", action="store_true")
    a = ap.parse_args()

    handler = partial(http.server.SimpleHTTPRequestHandler,
                      directory=str(a.pasta.resolve()))
    endereco = f"http://{ip_da_rede()}:{a.porta}"
    print(f"servindo {a.pasta.resolve()}")
    print(f"\n    no seu computador:  http://localhost:{a.porta}")
    print(f"    no celular/na rede: {endereco}\n")
    print("ctrl+c para parar")

    if a.so_mostrar:
        return
    with Reutilizavel(("", a.porta), handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nparado")
