import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.logic.config import Config

def main():
    # Fix for Windows taskbar icon grouping
    myappid = 'glassnotes.app.1.0' # arbitrary string
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # Modern apps usually handle high DPI automatically, but let's be safe
    # This MUST be called before creating the QApplication instance
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Set application icon globally
    icon_path = Config.get_resource_path("assets/icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
