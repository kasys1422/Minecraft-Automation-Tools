import pyaudio
import numpy as np
import sys
import time
from ui_func import virtual_console_print as print

class AudioClass:
    def __init__(self, settings):
        self.settings = settings
        self.setup()
        self.is_streamed = False

    def setup(self):
        print("[Info] setup audio")
        self.audio = pyaudio.PyAudio()
        self.device_list = {"name":[], "all_info":[]}
        for x in range(0, self.audio.get_device_count()):
            if self.audio.get_device_info_by_index(x)["maxInputChannels"] > 0 and self.audio.get_device_info_by_index(x)["hostApi"] == 0:
                self.device_list["all_info"].append(self.audio.get_device_info_by_index(x))
                self.device_list["name"].append(self.audio.get_device_info_by_index(x)["name"])

        if self.settings.get_value("device", {"name":"Null"})["name"] in self.device_list["name"]:
            self.device = self.settings.get_value("device")
            print("[Info] a saved device(" + str(self.settings.get_value("device")["name"]) + ") has been found, use this device")
        else:
            self.settings.set_value("device", {"name":self.device_list["all_info"][0]["name"], "all_info":self.device_list["all_info"][0]})
            self.device = self.settings.get_value("device")
            print("[Info] no saved device found, use default device")

    def start_stream(self, device):
        print("[Info] start stream")
        self.device = device
        self.open_stream(self.device)

    def restart_stream(self, device):
        print("[Info] restart stream")
        self.close_audio()
        self.setup()
        self.start_stream(device)

    def open_stream(self, device):
        try:
            print("[Info] open stream")
            self.stream = self.audio.open(format = pyaudio.paInt16,
                                   channels = int(device["all_info"]["maxInputChannels"]),
                                   rate = int(device["all_info"]["defaultSampleRate"]),
                                   input = True,
                                   frames_per_buffer = 1024,
                                   input_device_index = int(device["all_info"]["index"]))
            
            self.is_streamed = True
        except OSError as e:
            print("[Error] cannot open stream, use default device" + str(e.args))
            self.settings.set_value("device", {"name":self.device_list["all_info"][0]["name"], "all_info":self.device_list["all_info"][0]})
            self.start_stream(self.settings.get_value("device"))

    def close_stream(self):
        self.is_streamed = False
        self.stream.stop_stream()
        self.stream.close()
        print("[Info] close stream")

    def close_audio(self):
        self.close_stream()
        self.audio.terminate()
        print("[Info] close audio")

    def get_input_volume(self, device_all_info):
        if self.is_streamed == True:
            try:
                return (np.frombuffer(self.stream.read(1024), dtype="int16") / 32768.0).max()
            except OSError as e:
                print("[Error] stream closed " + str(e.args))
                return 0.0
        else:
            return 0.0


    def __del__(self):
        self.close_audio()