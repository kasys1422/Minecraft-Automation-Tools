import gettext
import locale
import dearpygui.dearpygui as dpg


def GetTranslationData(disable_translation=False):
    now_locale, _ = locale.getdefaultlocale()
    if disable_translation == True:
        now_locale = 'en-US'
    return gettext.translation(domain='messages',
                            localedir = './resources/locale',
                            languages=[now_locale], 
                            fallback=True).gettext, now_locale
_ , now_locale = GetTranslationData()

class VirtualConsole:
    def __init__(self, tag):
        self.tag = tag
        self.text = "[Info] launch virtual console system"
        self.is_updated = False
        self.pos = [25, 420]
        self.width = 720
        self.height = 130

    def update_text(self):
        try:
            dpg.set_value(self.tag + "_text", self.text)
            self.is_updated = True
        except SystemError:
            pass

    def create_window(self):
        if dpg.does_item_exist(self.tag + "_window"):
            self.print("[Info] console window already exists")
        else:
            with dpg.window(
                tag=self.tag + "_window",
                width=self.width,
                height=self.height,
                pos=self.pos,
                autosize=False,
                no_resize=False,
                no_scrollbar=False,
                horizontal_scrollbar=True,
                no_close=False,
                label="Console",on_close=self.on_window_close):
                dpg.add_text(label=self.text, tag=self.tag + "_text")
                self.print("[Info] open console window")
            dpg.set_y_scroll(self.tag + '_window', dpg.get_y_scroll_max(self.tag + '_window') + 39 + (18 * (self.text.count('\n') - (dpg.get_item_height(self.tag + "_window") / (130/6)))))

    def on_window_close(self, sender, app_data, user_data):
        self.pos = dpg.get_item_pos(self.tag + "_window")
        self.width = dpg.get_item_width(self.tag + "_window")
        self.height = dpg.get_item_height(self.tag + "_window")
        children_dict = dpg.get_item_children(sender)
        for key in children_dict.keys():
            for child in children_dict[key]:
                dpg.delete_item(child)
        dpg.delete_item(sender)
        self.print("[Info] close console window")

    def print(self, text):
        print(text)
        count = self.text.count('\n')
        if count > 200:
           self.text = self.text[self.text.find('\n', 0) + 1:]
        self.text = self.text + "\n" + text
        if self.is_updated == True:
            if dpg.does_item_exist(self.tag + "_window"):
                if dpg.get_y_scroll_max(self.tag + '_window') - (18 * 3) <= dpg.get_y_scroll(self.tag + '_window'):
                    dpg.set_y_scroll(self.tag + '_window', dpg.get_y_scroll_max(self.tag + '_window') + (18 * (self.text.count('\n') - (dpg.get_item_height(self.tag + "_window") / 18))))
                    

virtual_console = VirtualConsole("console")

def virtual_console_print(text, console_class=virtual_console):
    console_class.print(text)

def virtual_console_update(console_class=virtual_console):
    console_class.update_text()

class GuiClass:
    def __init__(self, settings, audio, key_func):
        self.settings = settings
        self.audio = audio
        self.key_func = key_func
        dpg.create_context()
        dpg.create_viewport(title="Minecraft Automation Tools", width=800, height=600, min_width=800, min_height=600, max_width=800, max_height=600, resizable=False)
        dpg.setup_dearpygui()
        self.create_gui()
        dpg.show_viewport()
        self.audio.start_stream(self.settings.get_value("device"))

        virtual_console_print("[Info] software version " + str(self.settings.get_value("SOFTWARE_VERSION")))
        virtual_console_print("[Info] language = " + str(now_locale))

    def create_gui(self):
        with dpg.font_registry():
            with dpg.font(file=self.settings.get_value("font_path", "./resources/Mplus1-Medium.ttf"), size = 18) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
        dpg.bind_font(default_font)

        with dpg.window(tag="main_window", label="Main Window", horizontal_scrollbar=True):
            with dpg.tab_bar(label="Tool Select Tab Bar", tag="tool_select_tab_bar", callback=lambda:self.key_func.stop_all_tools(self)):
                # Fishing tool
                with dpg.tab(label="Fishing Tool", tag="fishingtool"):

                    dpg.add_text("[Minecraft Auto Fishing Tool]")
                    dpg.add_button(label=_("Start Fishing"), tag="fishing_button", callback=lambda:dpg.configure_item('fishing_button', label=self.key_func.start_stop_fishing(self.minimize_viewport)))
                    with dpg.drawlist(width=500, height=42, tag="volume_bar_outer"):
                       dpg.draw_line((0, 20), (500, 20), color=(255, 255, 255, 255), thickness=20, tag="volume_bar")
                       dpg.draw_line((0, 0), (0, 40), color=(255, 128, 0, 255), thickness=2, tag="volume_bar_threshold")
                       dpg.draw_line((0, 0), (500, 0), color=(128, 200, 255, 255), thickness=1, tag="volume_bar_top")
                       dpg.draw_line((500, 0), (500, 40), color=(128, 200, 255, 255), thickness=1, tag="volume_bar_right")
                       dpg.draw_line((0, 40), (500, 40), color=(128, 200, 255, 255), thickness=1, tag="volume_bar_bottom")
                       dpg.draw_line((0, 0), (0, 40), color=(128, 200, 255, 255), thickness=1, tag="volume_bar_left")
                    dpg.add_slider_int(label=_("Threshold for pulling up the fishing rod"), tag="threshold", default_value=self.settings.get_value("threshold", 5), callback=self.apply_threshold)
                    dpg.add_separator()
                    dpg.add_text("[" +_("Option") + "]")
                    dpg.add_combo(tag="audio_input_device_combo", label=_("Audio input device"), items=self.audio.device_list["name"], default_value=self.audio.device["name"])
                    dpg.add_checkbox(label=_("Automatically minimize windows when launching tools"), tag="auto_hide_fishing",default_value=self.settings.get_value("auto_hide_fishing", True))
                    dpg.add_button(label=_("Apply"), tag="apply_button", callback=lambda:self.apply_settings())
                    dpg.add_separator()
                    dpg.add_text("[" +_("How to use") + "]")
                    dpg.add_text(_('1. Set the audio input device (a device that can record in-game music, such as Stereo Mix) and threshold.') + "\n" + 
                                 _('2. Press "Start Fishing".') + "\n" + 
                                 _('3. Start fishing in the game.') + "\n" + 
                                 _('4. Fishing is done automatically.') + "\n" + 
                                 _('5. Press the middle mouse button or "Stop Fishing" to exit.'))
                    dpg.add_separator()
                with dpg.tab(label="Trap Tool", tag="trap_tool"):
                    dpg.add_text("[Minecraft Trap Automation Tool]")
                    dpg.add_button(label=_("Start"), tag="trap_button", callback=lambda:dpg.configure_item('trap_button', label=self.key_func.start_stop_trap(self.minimize_viewport)))
                    dpg.add_separator()
                    dpg.add_text("[" +_("Option") + "]")
                    dpg.add_checkbox(label=_("Automatically minimize windows when launching tools"), tag="auto_hide_trap",default_value=self.settings.get_value("auto_hide_trap", True))
                    dpg.add_button(label=_("Apply"), tag="apply_button_trap", callback=lambda:self.apply_settings("Trap"))
                    dpg.add_separator()
                    dpg.add_text("[" +_("How to use") + "]")
                    dpg.add_text(_('1. Press "Start" button.') + "\n" +
                                 _('2. Press left click once.') + "\n" + 
                                 _('3. The left click is automatically pressed at regular intervals.') + "\n" + 
                                 _('4. Press the middle mouse button or "Stop" button to exit.'))
                    dpg.add_separator()
                    pass
                with dpg.tab(label=_("Software Information"), tag="information_tab"):
                    dpg.add_text("[" + _("Software Information") + "]")
                    dpg.add_text("Minecraft Automation Tools (version " + str(self.settings.get_value("SOFTWARE_VERSION")) + ")")
                    dpg.add_text("[" + _("Console") + "]")
                    dpg.add_button(label="Open", tag="open_console", callback=lambda:virtual_console.create_window())
                    dpg.add_text("[" + _("Third Party License") + "]")
                    try:
                        f = open('./resources/third_party_licenses.txt', 'r', encoding='UTF-8')
                        licenses_text = f.read()
                        f.close()
                        dpg.add_text(licenses_text)
                    except NameError:
                        print("[Error] Could not open licenses file")
                    except FileNotFoundError:
                        print("[Error] Could not open licenses file")
                    pass
        # Setup main window
        dpg.set_primary_window("main_window", True)
        dpg.set_viewport_large_icon("./resources/icon.ico")
        dpg.set_viewport_small_icon("./resources/icon.ico")

    def update_volume_bar(self, vol):
        width = dpg.get_viewport_client_width() - 22
        dpg.configure_item('volume_bar_outer', width=width + 2)
        dpg.configure_item('volume_bar', p2=(width*vol, 20))
        dpg.configure_item('volume_bar_top', p2=(width, 0))
        dpg.configure_item('volume_bar_right', p1=(width, 0), p2=(width, 40))
        dpg.configure_item('volume_bar_bottom', p2=(width, 40))
        threshold = dpg.get_value("threshold")
        dpg.configure_item('volume_bar_threshold', p1=(width * (threshold / 100), 0), p2=(width * (threshold / 100), 40))

    def get_value(self, tag):
        return dpg.get_value(tag)
    
    def configure_item_label(self, tag, label):
        dpg.configure_item(tag, label=label)

    def minimize_viewport(self):
        virtual_console_print("[Info] minimize window")
        self.viewport_pos = dpg.get_viewport_pos()
        dpg.minimize_viewport()

    def maximize_viewport(self):
        virtual_console_print("[Info] restore window")
        dpg.maximize_viewport()
        dpg.toggle_viewport_fullscreen()
        dpg.toggle_viewport_fullscreen()
        dpg.set_viewport_pos(self.viewport_pos)
        dpg.set_viewport_resizable(False)

    def apply_settings(self, mode="Fishing", save_flag=False):
        if mode=="Fishing":
            virtual_console_print("[Info] apply fishing options")
            device = {
                     "name":self.audio.device_list["name"][self.audio.device_list["name"].index(self.get_value("audio_input_device_combo"))],
                     "all_info":self.audio.device_list["all_info"][self.audio.device_list["name"].index(self.get_value("audio_input_device_combo"))],
                     }
            self.settings.set_value("device", device)
            self.settings.set_value("auto_hide_fishing", dpg.get_value("auto_hide_fishing"))
            self.audio.restart_stream(self.settings.get_value("device"))
            virtual_console_print("[Info] successfully applied(device="+str(device["name"])+", auto_hide_fishing=" + str(dpg.get_value("auto_hide_fishing"))+")")
            dpg.set_value("audio_input_device_combo", self.settings.get_value("device")["name"])
        elif mode=="Trap":
            virtual_console_print("[Info] apply trap options")
            self.settings.set_value("auto_hide_trap", dpg.get_value("auto_hide_trap"))
            virtual_console_print("[Info] successfully applied(auto_hide_trap=" + str(dpg.get_value("auto_hide_trap"))+")")
        if save_flag == True:
            self.settings.save_file(self.settings.param)

    def apply_threshold(self):
        virtual_console_print("[Info] threshold changed")
        self.settings.set_value("threshold", dpg.get_value("threshold"))

    def ui_loop(self, func, *args):
        while dpg.is_dearpygui_running():
            func(*args)
            dpg.render_dearpygui_frame()

    def __del__(self):
        dpg.destroy_context()


