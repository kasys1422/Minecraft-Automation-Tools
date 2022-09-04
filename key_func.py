import mouse
import time
import ctypes
import platform
from ui_func import _
from ui_func import virtual_console_print as print
from ui_func import virtual_console_update as update_console

def mouse_ispressed_middle():
    if platform.system() == "Windows":
        return (bool(ctypes.windll.user32.GetAsyncKeyState(0x04)&0x8000))
    else:
        return mouse.is_pressed(button='middle')

class KeyClass:
    def __init__(self, settings):
        self.settings = settings
        self.state = "stop"
        self.last_time = time.time()
        pass

    def change_state(self, state_param):
        self.state = state_param
        self.last_time = time.time()

    def start_stop_fishing(self, view_port_func):
        if self.state == "stop":
            self.change_state("fishing_enable")
            if self.settings.get_value("auto_hide_fishing", False) == True:
                view_port_func()
            print("[Info] start fishing")
            return _("Stop Fishing")
            pass
        else:
            self.change_state("stop")
            print("[Info] stop fishing")
            return _("Start Fishing")

    def start_stop_trap(self, view_port_func):
        if self.state == "stop":
            self.change_state("trap_enable")
            if self.settings.get_value("auto_hide_trap", False) == True:
                view_port_func()
            print("[Info] start trap tool")
            return _("Stop")
            pass
        else:
            self.change_state("stop")
            print("[Info] stop trap tool")
            return _("Start")

    def stop_all_tools(self, ui):
        if self.state != "stop":
            if self.state == "fishing_enable" or self.state == "wait_after_pull_up_the_fishing_rod" or self.state == "use_the_fishing_rod_again" or self.state == "wait_next_fishing":
                mouse.click('right')
                if self.settings.get_value("auto_hide_fishing", False) == True:
                    ui.maximize_viewport()
                ui.configure_item_label('fishing_button', label=_("Start Fishing"))
                print("[Info] stop fishing")
            elif self.state == "trap_enable" or self.state == "attack":
                if self.settings.get_value("auto_hide_trap", False) == True:
                    ui.maximize_viewport()
                ui.configure_item_label('trap_button', label=_("Start"))
                print("[Info] stop trap tool")
            self.change_state("stop")

    def loop(self, settings, audio, ui):
        # get volume of audio input device
        vol = audio.get_input_volume(audio.device)
        ui.update_volume_bar(vol)

        if self.state == "stop":
            pass

        # stop tools
        elif mouse_ispressed_middle() == True:
            self.stop_all_tools(ui)

        # fishing
        elif self.state == "fishing_enable":
            if vol > ui.get_value("threshold") / 100:
                print("[Info] hit a fish")
                self.change_state("wait_after_pull_up_the_fishing_rod")
                mouse.click('right')
            pass
        elif self.state == "wait_after_pull_up_the_fishing_rod":
            if time.time() - self.last_time > 0.5:
                self.change_state("use_the_fishing_rod_again")
            pass
        elif self.state == "use_the_fishing_rod_again":
            if time.time() - self.last_time > 0.5:
                print("[Info] fishing again")
                mouse.click('right')
                self.change_state("wait_next_fishing")
            pass
        elif self.state == "wait_next_fishing":
            if time.time() - self.last_time > 1.0:
                self.change_state("fishing_enable")
            pass

        # trap
        elif self.state == "trap_enable":
            if mouse.is_pressed(button='left') == True:
                self.change_state("attack")
                print("[Info] first attack")
        elif self.state == "attack":
            if time.time() - self.last_time > 1.0 / 1.7:
                mouse.click('left')
                print("[Info] attack")
                self.last_time = time.time()
            pass
        pass

        # update console
        update_console()