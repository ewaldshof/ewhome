# ewhome

## Board flashen

Ein Board, das noch kein aktuelles MicroPython aufgespielt bekommen hat, lässt sich folgendermaßen flashen:

1. `esptool.py` besorgen via `pip install esptool`. **Nicht** das `esptool` aus den Debian-/Ubuntu-Paketen benutzen.
2. Firmware-Image von http://micropython.org/download herunterladen. Der Ewaldshof benutzt ESP32-Boards.
3. Firmware flashen mittels `esptool.py -p /dev/ttyS0 write_flash 0x1000 esp32-20190529-v1.11.bin`. Dabei natürlich `ttyS0` mit dem korrekten Port ersetzen und auch den Namen der Firmware-Datei wenn nötig anpassen.

## Config schreiben

Unter `config` gibt es das Script `push-config-to-mqtt.py`, das die Konfiguration aus `ewhome.yaml` in JSON konvertiert und in MQTT ablegt.

Beispielaufruf:

```sh
cd config
pipenv run python push-config-to-mqtt.py
```
