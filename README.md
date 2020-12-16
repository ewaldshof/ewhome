# ewhome 0.6.0
# 

## Statusanzeige

Die Boards sind mit 8 Zeilen à 16 Zeichen Monochrom-Displays ausgestattet, die folgende Informationen zeigen:

```text
Name d. Boards
0.6.0




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

## WLAN-Konfiguration für Boards

Um die WLAN-Konfigurationsdaten nicht im Repository zu haben, erwarten die Boards eine Datei `wlan.json` im Hauptverzeichnis, in der `ssid` und `password` gesetzt werden.
Ein Beispiel findet sich unter [`wlan.json.example`](firmware/wlan.json.example).

## Config schreiben

Unter `config` gibt es das Script `push-config-to-mqtt.py`, das die Konfiguration aus `ewhome.yaml` in JSON konvertiert und in MQTT ablegt.

Beispielaufruf:

```sh
cd config
pipenv run python push-config-to-mqtt.py
```

## bump2version

bump2version ist eine aktuellere Version von bumpversion.
Es verändert die Versionsnummern in den Quellcode und Dokumentation und erstellt in Git auf Wunsch Tag und Commit.
(Der Schalter `-n` führt einen dry-run durch.)

Siehe auch: [Versioning using bumpversion](https://medium.com/@williamhayes/versioning-using-bumpversion-4d13c914e9b8).

Beispielaufruf:

```sh
bump2version --tag --commit minor
git push origin master --tags
```

# EWH ESP Board

This project contains the MicroPython firmware setup for the ewh esp board, as well as some helpful scripts to flash MicroPython to a board and copy firmware files over.

## Software setup ???

This repository is using submodules.
The build script will automatically try to clone them if they're missing, but you can also do it manually, either by specifying `--recurse-submodules` directly when running `git clone`, or by running `git submodule update --init` afterwards.

### Python

You need to have Python 3 available via a command called `python3`.
The minimum minor version has not been decided yet; 3.7 should be enough.

### Pipenv

We're using [Pipenv](https://pipenv.pypa.io/) to set up Python dependencies.
If you don't have it yet, install it using a command like `sudo apt install pipenv`, `pip3 install --user pipenv`, or whatever your local machine requires.
Please refer to [the Pipenv installation docs](https://pipenv.pypa.io/en/latest/install/) if you're having trouble.

### Environment variables

Even if everyone is using the same _code_ when working with a project, some things are still different depending on the machine the code runs _on_.
The usual way of changing these things without writing them directly into the code is to configure them using _environment variables_.

The way you set an environment variable depends on your operating system and shell and is out of scope for this document, but there is another way supported by Pipenv:
Creating a `.env` file.
This is simply a file, named `.env`, that contains environment variable assignments, one per line.

Here is an example `.env` file for this project, that also serves as the template for your personal `.env` file.
Copy it and edit it for your system.

```
# The serial port your board is connected to.
ESP_PORT=/dev/ttyUSB0

# This variable defines the MicroPython version to use.
# You should only change it if you have a good reason.
ESP_MICROPYTHON=esp32-idf3-20200902-v1.13

# The following settings just set other variables based on the values above.
# You should not need to edit anything here.
ESPTOOL_PORT=${ESP_PORT}
RSHELL_PORT=${ESP_PORT}
```

The `.env` file is local to your system and should not be committed.

### Dependencies

You're done with the hardest part once you have a working Pipenv and your environment variables set.
Installing all the dependencies is now simply running

```sh
pipenv install
```

## Provisioning a board

To run this project on a microcontroller board, the board needs to have two things:
MicroPython, and the Tally code.

* When you're developing on this project, you typically install MicroPython only once to the board, and copy over Tally code every time you changed something in it.
* When you're not developing, but just want to provision a board, you do both things only once.

### Getting MicroPython

There is a Pipenv script that will download the correct version of MicroPython for you.
It will place a file ending in `.bin` into the `micropython` directory.
Call it like this:

```sh
pipenv run get-micropython
```

The script currently depends on `curl` being available on your system.
If you don't have it, either install it, or get the MicroPython binary manually by downloading the file referred to by `TALLY_MICROPYTHON` in your `.env` file from [the MicroPython ESP32 download page](https://micropython.org/download/esp32/).

### Flashing MicroPython

You need to first wipe the board's flash memory and then flash MicroPython.
There are helper scripts for this, too.
Call them like this:

```sh
pipenv run erase-flash
pipenv run flash-micropython
```

### Flashing the Tally code

There is another helper script which will copy everything in the `src` directory over to the board (and also delete any files on the board that are not in `src`, to have a clean environment).
Simply call:

```sh
pipenv run sync-code
```

## Debugging

For an interactive Python shell, you can either connect with a serial terminal emulator directly to the board or use `pipenv run repl`.
Once connected, press <kbd>Ctrl</kbd>+<kbd>C</kbd> to enter interactive mode instead of just watching log messages.
