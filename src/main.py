from dotenv import load_dotenv
import os
import translator
from PyQt5.QtWidgets import QApplication
import sys
import keyboard
import inputhandler
import overlay

load_dotenv()

YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
FOLDER_ID = os.getenv('FOLDER_ID')

translator = translator.Translator(YANDEX_API_KEY, FOLDER_ID)
target_language = 'en'

input_handler = inputhandler.Inputhandler(translator, target_language)

app = QApplication(sys.argv)

input_handler.overlay = overlay.OverlayWindow()
# input_handler.overlay.show()

def on_key_event(event):
    #write to file info
    if event.event_type == keyboard.KEY_DOWN:
        input_handler.on_press(event)
    else:
        input_handler.on_release(event)

keyboard.hook(on_key_event)
keyboard.add_hotkey('alt+x', input_handler.start_recording)

# exit from program by hotkey
def quit_app():
    print('exit')
    keyboard.unhook_all()
    app.quit()
    sys.exit()

keyboard.add_hotkey('alt+q', quit_app)
app.exec_()

keyboard.wait('alt+q')

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#
#     # Создание и отображение окна
#     overlay = OverlayWindow()
#     overlay.show()
#
#     sys.exit()


