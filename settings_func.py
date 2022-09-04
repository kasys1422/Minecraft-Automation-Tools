import json
import dearpygui.dearpygui as dpg
from ui_func import virtual_console_print as print

SOFTWARE_VERSION = "2.0.4"
DEFAULT_SETTINGS_VALUE = {
                           "version":1,
                           "font_path":"./resources/Mplus1-Medium.ttf",
                           "threshold":5,
                           "auto_hide_fishing":True,
                           "auto_hide_trap":True
                          }

class SettingsClass:
    def __init__(self, file_path):
        self.file_path = file_path
        self.load_file()

    def load_file(self):
        try:
            with open(self.file_path) as f:
              self.param = json.load(f)
        except FileNotFoundError:
            self.save_file(DEFAULT_SETTINGS_VALUE)
            self.load_file()
        except json.decoder.JSONDecodeError:
            self.save_file(DEFAULT_SETTINGS_VALUE)
            self.load_file()
    def save_file(self, param):
        with open(self.file_path, 'w') as f:
            json.dump(param, f, indent=4)

    def get_value(self, key, none_value=None):
        if key == "SOFTWARE_VERSION":
            return SOFTWARE_VERSION
        try:
            return self.param[key]
        except:
            if none_value != None:
                self.set_value(key, none_value)
            return none_value

    def set_value(self, key, value):
        try:    
            self.param[key] = value
        except:
            pass
