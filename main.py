"""
ERP-Aqua - نرمافزار مدیریت مزارع پرورش ماهی
نسخه 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5 import QtWidgets, QtCore
from src.gui.main_window import MainWindow
from src.gui.dialogs.login_dialog import LoginDialog
from src.core.constants import APP_NAME, APP_VERSION

def start_api_server():
    """راهاندازی سرور API برای ارتباط با موبایل"""
    try:
        from src.api.server import start_api_server as _start_server
        import threading
        server_thread = threading.Thread(target=_start_server, daemon=True)
        server_thread.start()
        print("✅ سرور API برای ارتباط با موبایل راهاندازی شد")
        return True
    except ImportError as e:
        print(f"⚠️ خطا در import: {e}")
        return False
    except Exception as e:
        print(f"⚠️ خطا در راهاندازی سرور API: {e}")
        return False

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setLayoutDirection(QtCore.Qt.RightToLeft)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # راهاندازی سرور API
    start_api_server()

    # نمایش دیالوگ لاگین
    login_dialog = LoginDialog()
    
    # اگر کاربر لاگین نکرد، برنامه بسته شود
    if login_dialog.exec_() != QtWidgets.QDialog.Accepted:
        print("کاربر لاگین نکرد، برنامه بسته میشود")
        sys.exit(0)
    
    current_user = login_dialog.get_current_user()
    print(f"کاربر جاری: {current_user}")

    window = MainWindow(current_user)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()