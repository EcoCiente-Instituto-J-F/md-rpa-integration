"""
Interface local da migração.

    python src/ui.py

Sobe um servidor em 127.0.0.1 e abre o navegador. Só a biblioteca padrão.
"""

import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST, PORT = "127.0.0.1", 8765
HOSTS_ACEITOS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}

# Empacotado com PyInstaller, os arquivos estáticos ficam em sys._MEIPASS.
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ARQUIVOS = {
    "/": (ROOT / "src" / "ui_static" / "index.html", "text/html; charset=utf-8"),
    "/logo.png": (ROOT / "assets" / "logo-ecociente.png", "image/png"),
    "/favicon.ico": (ROOT / "assets" / "ecociente.ico", "image/x-icon"),
}

_lock = threading.Lock()
_execucao = {"orquestrador": None, "thread": None}


def _backend():
    """
    Importa o backend sob demanda: sem um .env válido o import falha, e a
    interface precisa abrir mesmo assim para dizer o que falta.
    Devolve (módulos, None) ou (None, mensagem de erro).
    """
    try:
        from config.database import database_health_check
        from config.logging_config import memory_log
        from rpa.orchestrator import MigrationOrchestrator
    except ModuleNotFoundError as error:
        return None, (
            f"Dependência ausente: {error.name}. Rode "
            ".venv\\Scripts\\python -m pip install -r requirements.txt "
            "(ou abra pelo EcoCiente.bat, que faz isso sozinho)."
        )
    except Exception as error:
        faltando = [str(e["loc"][0]) for e in getattr(error, "errors", lambda: [])()]
        detalhe = f"defina {', '.join(faltando)}" if faltando else str(error)
        return None, (
            f"Configuração incompleta: {detalhe}. Copie .env.example para .env, "
            "na mesma pasta do programa, e ajuste as conexões."
        )
    return (database_health_check, memory_log, MigrationOrchestrator), None


def _rodando():
    thread = _execucao["thread"]
    return thread is not None and thread.is_alive()


def status():
    backend, erro = _backend()
    if erro:
        return {"config_erro": erro, "execucao": None, "log": []}
    orquestrador = _execucao["orquestrador"]
    return {
        "config_erro": None,
        "execucao": orquestrador.log.snapshot() if orquestrador else None,
        "log": list(backend[1])[-200:],
    }


def bancos():
    backend, erro = _backend()
    return {"config_erro": erro} if erro else backend[0]()


def executar(simular):
    backend, erro = _backend()
    if erro:
        return 400, {"erro": erro}
    with _lock:
        if _rodando():
            return 409, {"erro": "Já existe uma execução em andamento."}
        orquestrador = backend[2](dry_run=simular)
        thread = threading.Thread(target=orquestrador.execute, daemon=True)
        _execucao.update(orquestrador=orquestrador, thread=thread)
        thread.start()
    return 202, {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # o executável sem console não tem stderr
        pass

    def _json(self, code, body):
        data = json.dumps(body, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        # Barra DNS rebinding: só atende quem pediu por 127.0.0.1/localhost.
        if self.headers.get("Host") in HOSTS_ACEITOS:
            return True
        self._json(403, {"erro": "Host não permitido."})
        return False

    def do_GET(self):
        if not self._host_ok():
            return
        if self.path == "/api/status":
            return self._json(200, status())
        if self.path == "/api/bancos":
            return self._json(200, bancos())
        if self.path in ARQUIVOS:
            path, content_type = ARQUIVOS[self.path]
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return self.wfile.write(data)
        self._json(404, {"erro": "Não encontrado."})

    def do_POST(self):
        if not self._host_ok():
            return
        # Exigir JSON impede que outro site dispare a migração com um <form>.
        if self.headers.get("Content-Type") != "application/json":
            return self._json(415, {"erro": "Envie application/json."})
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._json(400, {"erro": "JSON inválido."})

        if self.path == "/api/executar":
            return self._json(*executar(simular=body.get("simular") is not False))
        if self.path == "/api/encerrar":
            if _rodando():
                return self._json(409, {"erro": "Aguarde a execução terminar."})
            self._json(200, {})
            return threading.Thread(target=self.server.shutdown).start()
        self._json(404, {"erro": "Não encontrado."})


class Server(ThreadingHTTPServer):
    allow_reuse_address = False  # no Windows, True deixaria abrir duas instâncias
    daemon_threads = True


def main():
    url = f"http://{HOST}:{PORT}"
    try:
        server = Server((HOST, PORT), Handler)
    except OSError:  # já está aberta: só mostra a janela
        webbrowser.open(url)
        return
    if "--sem-navegador" not in sys.argv:
        threading.Timer(0.5, webbrowser.open, [url]).start()
    print(f"EcoCiente aberto em {url}  (Ctrl+C encerra)") if sys.stdout else None
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
