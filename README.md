# ewhome

README.md for Version 0.3.0

## Statusanzeige

Die Boards sind mit 8 Zeilen à 16 Zeichen Monochrom-Displays ausgestattet, die folgende Informationen zeigen:

```text
Name d. Boards
Version der Software




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
2. Das Script `fw_flash.sh` mit dem Port, über den das Board erreichbar ist, ausführen, also z.B. `./fw_flash.sh /dev/tty.SLAB_USBtoUART`.

## Dateien auf ESP32 übertragen
Der Source Code liegt im Verzeichnis "firmware". Übertragung z.B. mit Hilfe des Scripts firmware/sync-to-board.sh
rshell muss für das Script installiert sein.

sync-to-board.sh [<Serial Port>]
Default für Serial Port: "/dev/tty.SLAB_USBtoUART"

Beispielaufruf:
```sh
cd firmware
./sync-to-board.sh COM4
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

Siehe auch: [Versioning using bumpversion](https://medium.com/@williamhayes/versioning-using-bumpversion-4d13c914e9b8)

Beispielaufruf:
```sh
bump2version --tag --commit minor
git push origin master --tags
```
