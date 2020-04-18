from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys, yaml

from communication.fake_esp32serial import FakeESP32Serial


base_dir = os.environ['MVMGUI_BASEDIR']
settings_file = os.path.join(base_dir, 'gui/default_settings.yaml')
with open(settings_file) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


if __name__ == "__main__":
    print('Config:', yaml.dump(config), sep='\n')