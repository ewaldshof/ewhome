# ewhome

README.md for Version 0.2.0

## Statusanzeige

Die Boards sind mit 8 Zeilen à 16 Zeichen Monochrom-Displays ausgestattet, die folgende Informationen zeigen:

```text
Name d. Boards





b4 e6 2d 8f c8 29
M WL OK: .123 <3
```

Die vorletzte Zeile zeigt die MAC-Adresse des WLAN-Adapters an.

In der letzten Zeile finden sich Statusinformationen:

* `M`, wenn eine Verbindung zum MQTT-Server besteht.
* WLAN-Statusinformationen (`WL`):
  * `Init ...` wenn der Netzwerk-Stack noch nicht initialisiert wurde.
  * `Starting` beim Starten eines Verbindungsaufbaus.
  * `Trying..` während die Verbindung aufgebaut wird.
  * `Wrong PW` falls das WLAN-Passwort (gesetzt in `ewh_net.py` nicht korrekt ist).
  * `OK: .123` wenn eine Verbindung besteht. Das letzte Byte der Adresse wird angezeigt.
  * `Unknown` wenn es für das Statusflag kein passendes `if` im Code gibt.
* `<3` ist ein jede Sekunde rhythmisch blinkender Herzschlag, der zeigt, ob das Board gecrasht ist.

## Board flashen

Ein Board, das noch kein aktuelles MicroPython aufgespielt bekommen hat, lässt sich folgendermaßen flashen:

1. `esptool.py` besorgen via `pip install esptool`. **Nicht** das `esptool` aus den Debian-/Ubuntu-Paketen benutzen.
2. Firmware-Image von http://micropython.org/download herunterladen. Der Ewaldshof benutzt ESP32-Boards.
3. Firmware flashen mittels `esptool.py -p /dev/ttyS0 write_flash 0x1000 esp32-20190529-v1.11.bin`. Dabei natürlich `ttyS0` mit dem korrekten Port ersetzen und auch den Namen der Firmware-Datei wenn nötig anpassen.

Alternativ:

```sh
./firmware/fw_flash.sh
```

## Dateien auf ESP32 übertragen
Der Source Code liegt im Verzeichnis "firmware". Übertragung z.B. mit Hilfe des Scripts firmware/sync-to-board.sh
rshell muss für das Script installiert sein.

Beispielaufruf:
```sh
cd firmware
./sync-to-board.sh
```


## Config schreiben

Unter `config` gibt es das Script `push-config-to-mqtt.py`, das die Konfiguration aus `ewhome.yaml` in JSON konvertiert und in MQTT ablegt.

Beispielaufruf:

```sh
cd config
pipenv run python push-config-to-mqtt.py
```


## Bump2version

Bump2version ist eine aktuellere Version von bumpversion. Es verändert die Versionen in den Dateien und erstellt in git auf Wunsch Tag und commit. (Der Schalter -n führt einen dry-run durch.)

Beispielaufruf:
```sh
pipenv run python push-config-to-mqtt.py
```
