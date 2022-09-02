import pyaudio
import numpy as np
import sys
import time

class AudioClass:
    def __init__(self, settings):
        self.settings = settings
        self.setup()
        self.is_streamed = False

    def setup(self):
        self.audio = pyaudio.PyAudio()
        self.device_list = {"name":[], "all_info":[]}
        for x in range(0, self.audio.get_device_count()):
            if self.audio.get_device_info_by_index(x)["maxInputChannels"] > 0 and self.audio.get_device_info_by_index(x)["hostApi"] == 0:
                self.device_list["all_info"].append(self.audio.get_device_info_by_index(x))
                self.device_list["name"].append(self.audio.get_device_info_by_index(x)["name"])

        if self.settings.get_value("device", {"name":"Null"})["name"] in self.device_list["name"]:
            self.start_stream(self.settings.get_value("device"))
        else:
            self.settings.set_value("device", {"name":self.device_list["all_info"][0]["name"], "all_info":self.device_list["all_info"][0]})
            self.start_stream(self.settings.get_value("device"))

    def start_stream(self, device):
        self.device = device
        self.open_stream(self.device)

    def restart_stream(self, device):
        print("[Info] restart stream")
        self.close_stream()
        self.start_stream(device)

    def open_stream(self, device):
        try:
            self.stream = self.audio.open(format = pyaudio.paInt16,
                                   channels = int(device["all_info"]["maxInputChannels"]),
                                   rate = int(device["all_info"]["defaultSampleRate"]),
                                   input = True,
                                   frames_per_buffer = 1024,
                                   input_device_index = int(device["all_info"]["index"]))
            print("[Info] open stream")
            self.is_streamed = True
        except OSError as e:
            print("[Error] can not open stream " + str(e.args))
            self.settings.set_value("device", {"name":self.device_list["all_info"][0]["name"], "all_info":self.device_list["all_info"][0]})
            self.start_stream(self.settings.get_value("device"))
        except e:
            print("[Error] " + str(e.args))
    def close_stream(self):
        self.stream.close()
        print("[Info] close stream")
        self.is_streamed = False

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
        self.close_stream()