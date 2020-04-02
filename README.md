# MVM - gui

## Code organization

- the `gui` folder is deputed to contain the Python files for the GUI
- the `mock` folder contains the mock-ups for testing purposes, basically
  to mimic hardware interaction

## Requirements

- Python >= 3.5
- PyQt5
- PyQtGraph
- PySerial
- PyYaml

## Run

You can run with 
```
./gui/mvm_gui.py
```

Default settings are stored in 
```
./gui/default_settings.yaml
```

Basics settings are:
- port: (string) the serial port to use
- read_from_esp: (bool) if true reads data from the ESP32

More settings and description can be found in the yaml file itself.

If you want to read from an Arduino (ESP), you need to download `mock.ino`
into your Arduino device, and specify the serial port in the settings file.
