import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Установка размера окна
        self.setFixedSize(300, 100)

        # Установка текста
        label = QLabel("Ваш текст здесь", self)
        label.setStyleSheet("color: white; font-size: 24px; background-color: rgba(169, 169, 169, 180);")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(300, 100)
    def show(self):
        super().show()
        self.raise_()
    def hide(self):
        super().hide()
    def set_text(self, text):
        self.label.setText(text)