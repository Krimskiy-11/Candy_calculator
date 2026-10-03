import sys
import os
import threading
import time
import socket
from pathlib import Path
from wsgiref.simple_server import make_server

# Определяем корень приложения
if getattr(sys, 'frozen', False):
    EXE_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(getattr(sys, '_MEIPASS', EXE_DIR))
else:
    EXE_DIR = Path(__file__).resolve().parent.parent
    BUNDLE_DIR = EXE_DIR

# Добавляем пути в sys.path
for p in [str(BUNDLE_DIR), str(EXE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Принудительно задаем SQLite, если нет других переменных
if "DATABASE_ENGINE" not in os.environ:
    os.environ["DATABASE_ENGINE"] = "sqlite"

import django
django.setup()

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont
from desktop.api_client import ApiClient
from desktop.ui.main_window import MainWindow

def run_wsgi_server():
    """Надежный фоновый запуск Django через стандартный wsgiref сервер"""
    try:
        # Автоматически проверяем/накатываем миграции SQLite
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Ошибка миграции: {e}")

    application = get_wsgi_application()
    server = make_server('127.0.0.1', 8000, application)
    server.serve_forever()

def wait_for_server(host='127.0.0.1', port=8000, timeout=10.0):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            if s.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.2)
    return False

def main():
    # 1. Запускаем сервер Django в фоновом потоке
    server_thread = threading.Thread(target=run_wsgi_server, daemon=True)
    server_thread.start()

    # 2. Ждём фактического открытия сокета
    if not wait_for_server('127.0.0.1', 8000, timeout=8.0):
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Ошибка", "Локальный сервер базы данных не смог запуститься.")
        sys.exit(1)

    # 3. Запускаем главное окно
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    api = ApiClient("http://127.0.0.1:8000/api")
    window = MainWindow(api)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
