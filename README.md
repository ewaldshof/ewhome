# ewhome 0.3.0

## Statusanzeige

Die Boards sind mit 8 Zeilen à 16 Zeichen Monochrom-Displays ausgestattet, die folgende Informationen zeigen:

```text
Name d. Boards
0.3.0




b4 e6 2d 8f c8 29
M WL OK: .123 <3
```

Die zweite Zeile zeigt die Softwareversion an, die vorletzte Zeile die MAC-Adresse des WLAN-Adapters.

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

## MQTT-Hierarchie

Hier ist beispielhaft aufgeführt, unter welchen MQTT-Pfaden welche Informationen zu finden sind.
Die einzelnen Ebenen werden durch Slash (`/`) getrennt.

* **`ewhome`:** Der Namensraum, unter dem sich alle von diesem Projekt verarbeiteten Daten finden.
  * **`config`:** Die Konfigurationsdaten aus [`ewhome.yaml`](config/ewhome.yaml) in JSON-Form, wie sie von [`push-config-to-mqtt.py`](config/push-config-to-mqtt.py) abgelegt werden.
  * **`ds18x20`:** Sensorwerte der DS18x20-Temperatursensoren.
    * **`28190f43980e0005`:** Temperaturwert des Sensors mit dieser Hardware-ID, im JSON-Format.
  * **`rooms`:** Die einzelnen Räume, benannt nach ihren „IDs“.
    * **`A2.3`:** Gebäudeteil A, 2. Stock, Raum 3
      * **`meta`:** JSON-kodierte Informationen über den Raum (menschenlesbarer Name, Koordinaten, etc.)
      * **`actuators`:**
      * **`controllers`:**
      * **`sensors`:**
        * **`luft`, `vorlauf`, `ruecklauf1`, `ruecklauf2`, …:** Daten von dem Raum zugeordneten Sensoren, z.B. Kopie der JSON-Struktur aus `ds18x20`.


## Port-Konfiguration

Ein mit dem Computer verbundenes Board ist über einen seriellen Port erreichbar, der sich aber von Rechner zu Rechner unterscheidet, z.B. `/dev/tty.SLAB_USBtoUART` unter Linux, `/dev/ttyS3` unter WSL und `COM3` unter Windows.
Die Portnummern können sich aber auch bei Rechnern, die dasselbe Betriebssystem verwenden, unterscheiden.
Daher muss bei der Verwendung der MicroPython-Tools wie `esptool` und `rshell` üblicherweise der Port mit angegeben werden.

Um sich die Tipparbeit, bei jedem Kommando den Port anzugeben, zu sparen, lässt er sich auch in einer Umgebungsvariable definieren.
Leider benutzen die unterschiedlichen Tools unterschiedliche Namen für die Umgebungsvariablen.

Wenn du nur unsere Scripts `sync-to-board.sh` und `flash-firmware.sh` verwendest:
Beide akzeptieren die Umgebungsvariable `EWHOME_PORT` und geben sie entsprechend weiter.
Du kannst ihnen auch als Parameter einen Port übergeben, dieser überschreibt dann die Umgebungsvariable (und wird ebenfalls an Subtools weitergegeben).

Alternativ empfiehlt es sich, die Portzuweisung für alle Tools auf einmal vorzunehmen.
In POSIX-kompatiblen Shells wie der bash lässt sich dafür schreiben:

```sh
export EWHOME_PORT='/dev/tty.SLAB_USBtoUART' # Den Variableninhalt natürlich anpassen.
export AMPY_PORT="$EWHOME_PORT" ESPTOOL_PORT="$EWHOME_PORT" RSHELL_PORT="$EWHOME_PORT"
```

## Board flashen

Ein Board, das noch kein aktuelles MicroPython aufgespielt bekommen hat, lässt sich folgendermaßen flashen:

1. `esptool.py` besorgen via `pip install esptool`. **Nicht** das `esptool` aus den Debian-/Ubuntu-Paketen benutzen.
2. Sicherstellen, dass du wie oben beschrieben [den Port konfiguriert](#port-konfiguration) hast.
3. Das Script `flash-firmware.sh` ausführen.

## Dateien auf ESP32 übertragen

Der Quellcode liegt im Verzeichnis `firmware`.
Er lässt sich mit den für MicroPython üblichen Wegen übertragen.

Alternativ steht das Script `sync-to-board.sh` zur Verfügung, das alle Firmware-Files mit dem Board abgleicht und die geänderten hochlädt.
Das Script benötigt [rshell](https://github.com/dhylands/rshell) (`pip install --user rshell`).

Es akzeptiert den zu verwendenden Port [wie oben beschrieben](#port-konfiguration) per Umgebungsvariable oder Parameter.

## Config schreiben

Unter `config` gibt es das Script `push-config-to-mqtt.py`, das die Konfiguration aus `ewhome.yaml` in JSON konvertiert und in MQTT ablegt.

Beispielaufruf:

```sh
cd config
pipenv run python push-config-to-mqtt.py
```

# Bump2version

Bump2version ist eine aktuellere Version von bumpversion.
Es verändert die Versionsnummern in den Quellcode und Dokumentation und erstellt in Git auf Wunsch Tag und Commit.
(Der Schalter `-n` führt einen dry-run durch.)

Siehe auch: [Versioning using bumpversion](https://medium.com/@williamhayes/versioning-using-bumpversion-4d13c914e9b8).

Beispielaufruf:

```sh
bump2version --tag --commit minor
git push origin master --tags
```
