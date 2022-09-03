from ui_func import GuiClass
from audio_func import AudioClass
from settings_func import SettingsClass
from key_func import KeyClass
from ui_func import virtual_console_print as print

def main():
    print("[Info] start Minecraft Automation Tools")

    #setup
    settings = SettingsClass("./resources/settings.json");
    audio = AudioClass(settings)
    key_func = KeyClass(settings)
    ui = GuiClass(settings, audio, key_func)

    #loop
    ui.ui_loop(key_func.loop, settings, audio, ui)

    #end
    ui.apply_settings(save_flag=True)
    del settings, audio, ui, key_func

if __name__ == '__main__':
    main()