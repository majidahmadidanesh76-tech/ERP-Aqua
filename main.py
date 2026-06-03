"""
ERP-Aqua - نرمافزار مدیریت مزارع پرورش ماهی
نسخه 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5 import QtWidgets, QtCore
from src.gui.main_window import MainWindow
from src.core.constants import APP_NAME, APP_VERSION

def start_api_server():
    """راه‌اندازی سرور API برای ارتباط با موبایل"""
    try:
        from src.api.server import start_api_server as _start_server
        import threading
        server_thread = threading.Thread(target=_start_server, daemon=True)
        server_thread.start()
        print("✅ سرور API برای ارتباط با موبایل راه‌اندازی شد")
        return True
    except ImportError as e:
        print(f"⚠️ خطا در import: {e}")
        print("   مسیر فایل باید: src/api/server.py")
        return False
    except Exception as e:
        print(f"⚠️ خطا در راه‌اندازی سرور API: {e}")
        return False

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setLayoutDirection(QtCore.Qt.RightToLeft)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # راه‌اندازی سرور API
    start_api_server()

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()