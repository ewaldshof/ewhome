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
2. Das Script `flash-firmware.sh` mit dem Port, über den das Board erreichbar ist, ausführen, also z.B. `./flash-firmware.sh /dev/tty.SLAB_USBtoUART`.

## Dateien auf ESP32 übertragen

Der Quellcode liegt im Verzeichnis `firmware`.
Er lässt sich mit den für MicroPython üblichen Wegen übertragen.

Alternativ steht das Script `sync-to-board.sh` zur Verfügung, das alle Firmware-Files mit dem Board abgleicht und die geänderten hochlädt.
Das Script benötigt [rshell](https://github.com/dhylands/rshell) (`pip install --user rshell`).

sync-to-board.sh [<Serial Port>]
Default für Serial Port: "/dev/tty.SLAB_USBtoUART"

Beispielaufruf:

```sh
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
