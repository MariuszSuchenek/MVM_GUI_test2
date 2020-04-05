from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys, yaml

from communication.fake_esp32serial import FakeESP32Serial


base_dir = os.path.dirname(__file__)
settings_file = os.path.join(base_dir, 'default_settings.yaml')
with open(settings_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
esp32 = FakeESP32Serial()