import keyboard
import ctypes
from constants import *
from ctypes import wintypes
import time
import threading

import win32api

user32 = ctypes.WinDLL('user32', use_last_error=True)

GetKeyboardLayout = user32.GetKeyboardLayout
GetKeyboardLayout.restype = wintypes.HKL
GetKeyboardLayout.argtypes = [wintypes.DWORD]

GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = wintypes.HWND
GetForegroundWindow.argtypes = []

GetWindowThreadProcessId = user32.GetWindowThreadProcessId
GetWindowThreadProcessId.restype = wintypes.DWORD
GetWindowThreadProcessId.argtypes = [wintypes.HWND, wintypes.LPDWORD]

class Inputhandler:
    def __init__(self, translator, target_language):
        self.overlay = None
        self.translator = translator
        self.target_language = target_language
        self.last_key = None
        self.inputed_text = ''
        self.keys_pressed = []
        self.caret_position = 0;
        self.translation_timer = None
        self.stamp_for_program_replace = '►►►'
        self.start_recording_stamp = 'ъъъ'
        self.is_recording = False
        self.last_translated_text = ''
        self.last_text_to_translate_length = 0
        self.input_length_when_timer_started = 0
        self.caret_position_when_timer_started = 0
    def is_ctrl_pressed(self):
        return KEY_CTRL in self.keys_pressed or KEY_RIGHT_CTRL in self.keys_pressed
    def on_press(self, event):
        self.keys_pressed.append(event.scan_code)


        if event.scan_code == KEY_BACKSPACE:
            self.delete_last_char()
            if self.is_ctrl_pressed():
                self.delete_word_by_caret()
            self.reset_timer(self.is_recording)
        elif event.scan_code == KEY_LEFT:
            if self.caret_position > 0:
                if self.is_ctrl_pressed():
                    self.caret_position = self.find_prev_specialchar()
                else:
                    self.caret_position -= 1
            self.reset_timer(self.is_recording)
        elif event.scan_code == KEY_RIGHT:
            if self.caret_position < len(self.inputed_text):
                if self.is_ctrl_pressed():
                    self.caret_position = self.find_next_specialchar()
                else:
                    self.caret_position += 1
            self.reset_timer(self.is_recording)
        elif self.get_char(event.scan_code) is not None or (event.scan_code == KEY_ENTER and self.is_recording):
            if event.scan_code != KEY_ENTER:
                self.add_char(event)
            if self.inputed_text[-3:] == self.start_recording_stamp or event.scan_code == KEY_ENTER:
                if event.scan_code != KEY_ENTER:
                    self.inputed_text = self.inputed_text[:-3]
                    keyboard.write('\b' * len(self.start_recording_stamp))
                self.start_recording()
            self.reset_timer(self.is_recording)
        self.print_inputed_text_with_caret()

    def on_release(self, event):
        self.keys_pressed.remove(event.scan_code)
    def print_inputed_text_with_caret(self):
        print(self.inputed_text[:self.caret_position] + '|' + self.inputed_text[self.caret_position:], f'({self.caret_position})')
    def trim_text(self):
        self.inputed_text = self.inputed_text.strip()
    def get_current_keyboard_language(self):
        hwnd = GetForegroundWindow()
        thread_id = GetWindowThreadProcessId(hwnd, None)
        keyboard_layout_id = GetKeyboardLayout(thread_id)

        # Получаем язык ввода из идентификатора раскладки
        language_id = keyboard_layout_id & (2**16 - 1)
        
        # Переводим идентификатор языка в строку
        locale_name = ctypes.create_unicode_buffer(9)
        if ctypes.windll.kernel32.LCIDToLocaleName(language_id, locale_name, 9, 0) == 0:
            return None
        return locale_name.value
    def get_char(self, key_code):
        lang = self.get_current_keyboard_language()
        if key_code not in KEYCODES_TO_SYMBOLS or KEY_ALT in self.keys_pressed or KEY_CTRL in self.keys_pressed:
            return None
        return KEYCODES_TO_SYMBOLS[key_code][lang]
    def get_shifted_char(self, key_code):
        lang = self.get_current_keyboard_language()
        if key_code not in KEYCODES_TO_SYMBOLS_SHIFT:
            return None
        return KEYCODES_TO_SYMBOLS_SHIFT[key_code][lang]
    def add_char(self, event):
        if KEY_SHIFT in self.keys_pressed:
            char = self.get_shifted_char(event.scan_code)
        else:
            char = self.get_char(event.scan_code)
        if char is not None:
            self.inputed_text = self.inputed_text[:self.caret_position] + char + self.inputed_text[self.caret_position:]
            self.caret_position += 1
    def delete_last_char(self):
        if len(self.inputed_text) > 0:
            print(self.inputed_text[:self.caret_position - 1], self.inputed_text[self.caret_position:])
            self.inputed_text = self.inputed_text[:self.caret_position - 1] + self.inputed_text[self.caret_position:]
            self.caret_position -= 1
    def delete_word_by_caret(self):
        #find last space
        prev_specialchar = self.find_prev_specialchar()
        self.inputed_text = self.inputed_text[:prev_specialchar] + self.inputed_text[self.caret_position:]
        self.caret_position = prev_specialchar        
    def find_prev_specialchar(self):
        start_index = self.caret_position-1
        while start_index > 0:
            if start_index < 0:
                return 0
            current_char = self.inputed_text[start_index]
            if current_char in CARET_STOP_SYMBOLS and start_index != self.caret_position-1:
                return start_index+1
            start_index -= 1
        return 0
    def find_next_specialchar(self):
        start_index = self.caret_position-1
        while start_index < len(self.inputed_text):
            if start_index > len(self.inputed_text):
                return len(self.inputed_text)
            current_char = self.inputed_text[start_index]
            if current_char in CARET_STOP_SYMBOLS and start_index != self.caret_position-1:
                return start_index
            start_index += 1
        return len(self.inputed_text)
    def reset_timer(self, run_new_timer):
        if self.translation_timer is not None:
            self.translation_timer.cancel()
        if run_new_timer:
            self.input_length_when_timer_started = len(self.inputed_text)
            self.caret_position_when_timer_started = self.caret_position
            self.translation_timer = threading.Timer(0.2, self.translate_text)
            self.translation_timer.start()
    def translate_text(self):
        if self.input_length_when_timer_started != len(self.inputed_text) or self.caret_position_when_timer_started != self.caret_position:
            return
        input_to_translate = self.inputed_text[self.get_last_recording_stamp()+3:]
        # Перевод текста
        if len(input_to_translate) > 0:
            start_to_replace = self.get_last_recording_stamp()+3+len(self.last_translated_text)
            translated = self.translator.translate(self.target_language, [input_to_translate])['translations'][0]['text']
            

            keyboard.write('\b' * (len(self.last_translated_text) + len(input_to_translate)-self.last_text_to_translate_length))
            keyboard.write(translated)
            self.last_text_to_translate_length = len(input_to_translate)
            self.last_translated_text = translated
            print('translated:', translated, 'from', input_to_translate, 'caret:', self.caret_position)
    def get_last_recording_stamp(self):
        return self.inputed_text.rfind(self.stamp_for_program_replace)
    def start_recording(self):
        self.is_recording = not self.is_recording
        # if self.is_recording:
        #     self.overlay.show()Hi
        # else:
        #     self.overlay.hide()

        if self.is_recording:

            self.caret_position += len(self.start_recording_stamp)
        self.inputed_text += self.stamp_for_program_replace
        self.caret_position += len(self.stamp_for_program_replace)
        self.last_translated_text = ''
        self.last_text_to_translate_length = 0
        self.input_length_when_timer_started = 0
        self.caret_position_when_timer_started = 0
        if not self.is_recording:
            self.inputed_text = ''
    def set_overlay(self, overlay):
        self.overlay = overlay
