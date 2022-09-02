from ui_func import GuiClass
from audio_func import AudioClass
from settings_func import SettingsClass
from key_func import KeyClass


def save(settings, audio, ui):
    ui.apply_settings()
    settings.save_file(settings.param)

def main():
    #setup
    settings = SettingsClass("./resources/settings.json");
    audio = AudioClass(settings)
    key_func = KeyClass(settings)
    ui = GuiClass(settings, audio, key_func)


    #loop
    ui.ui_loop(key_func.loop, settings, audio, ui)

    #end
    save(settings, audio, ui)
    del settings, audio, ui

if __name__ == '__main__':
    main()