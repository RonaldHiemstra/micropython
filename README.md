# MicroPython

Support tools and libraries for my MicroPython projects.

## Prepare Python development environment

Install [Anaconda](https://www.anaconda.com/).

Create a MicroPython development environment:

``` bat
conda create --name mpydev python=3.8 pyserial
conda activate mpydev
pip install esptool mpfshell
```

## Setup VSCode as development environment

Add the following to the user `settings.json` of VSCode (Ctrl-Shift-P - Preferences: Open Settings (JSON)):

``` json
    "terminal.integrated.profiles.windows": {
        "micropython": {
            "path": "cmd.exe",
            "args": [
                "/K",
                "${env:HOME}\\anaconda3\\Scripts\\activate.bat ${env:HOME}\\anaconda3\\envs\\mpydev"
            ]
        }
    },
```

## Install MicroPython on an ESP32

Download the latest firmware from [micropython.org/download/esp32](https://micropython.org/download/esp32/) and install it using the following commands:

``` bat
set ESPTOOL_PORT=COM5
esptool --chip esp32 erase_flash
esptool --chip esp32 --baud 460800 write_flash -z 0x1000 "path to firmware.bin"
```

## Copy files to target device

Use [upload_all.py](upload_all.py) to upload files to the MicroPython device.

## Open a shell on the device

```bat
mpfshell -n -c "open COM5; repl"
```

:information_source: Use Ctrl-Q to exit.

### Accessing and configuring the ESP via the browser

* Configure WiFi (see below)
* Configure webREPL

    ```python
    import webrepl_setup
    ```

* Start webREPL

    ```python
    import webrepl
    webrepl.start()
    ```

* Open REPL

    <http://micropython.org/webrepl/#the.esp.ip.address:8266>

* Copy all files in /boot to the ESP
* Create the file `network_config.json` with the initial configuration:

    ```python
    open('network_config.json').write('{"ssid": "%s", "__password": "%s"}' % (input('ssid: '), input('password: ')))
    ```

* Reset the ESP :) `Ctrl-d`

## Quick reference

* [docs.micropython.org/esp32/quickref](http://docs.micropython.org/en/latest/esp32/quickref.html)

## Projects

* [magic_clock](magic_clock/readme.md)
* [ambient](ambient/readme.md)
