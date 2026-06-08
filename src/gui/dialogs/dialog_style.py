"""
استایل مشترک برای همه دیالوگ‌های برنامه
"""

DIALOG_STYLE = """
    QDialog {
        background-color: #2D2D30;
    }
    QLabel {
        color: #C8C8C8;
        font-size: 12px;
        background-color: transparent;
        border: none;
    }
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit {
        background-color: #3C3C3F;
        border: 1px solid #4A4A4F;
        border-radius: 4px;
        padding: 7px 10px;
        color: #FFFFFF;
        font-size: 12px;
        min-height: 32px;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDateEdit:focus, QTimeEdit:focus {
        border-color: #569CD6;
        background-color: #45454A;
    }
    QTextEdit {
        min-height: 70px;
        max-height: 70px;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: #3C3C3F;
        color: #FFFFFF;
        selection-background-color: #0E639C;
    }
    QSpinBox::up-button, QSpinBox::down-button,
    QTimeEdit::up-button, QTimeEdit::down-button {
        width: 18px;
        background-color: #3C3C3F;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
        background-color: #569CD6;
    }
    QDateEdit::drop-down {
        border: none;
        width: 20px;
    }
    QDateEdit::down-arrow {
        image: none;
    }
    QGroupBox {
        color: #C8C8C8;
        border: 1px solid #4A4A4F;
        border-radius: 4px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #3C3C3F;
        color: #C8C8C8;
        border: 1px solid #4A4A4F;
        border-radius: 4px;
        font-weight: bold;
        padding: 7px 14px;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #4A4A4F;
        border-color: #569CD6;
        color: white;
    }
    QPushButton:pressed {
        background-color: #569CD6;
        color: white;
    }
"""

CANCEL_BUTTON_STYLE = """
    QPushButton {
        background-color: #3C3C3F;
        color: #C8C8C8;
        border: 1px solid #4A4A4F;
        border-radius: 4px;
        font-weight: bold;
        padding: 7px 14px;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #4A4A4F;
        border-color: #F48771;
        color: #F48771;
    }
    QPushButton:pressed {
        background-color: #F48771;
        color: white;
    }
"""

TOOLBUTTON_STYLE = """
    QToolButton {
        background-color: #3C3C3F;
        border: 1px solid #4A4A4F;
        border-radius: 3px;
    }
    QToolButton:hover {
        background-color: #4A4A4F;
        border-color: #569CD6;
    }
"""