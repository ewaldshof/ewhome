# ewhome 0.8.0

EWHome is a system to conveniently configure a set of microcontroller boards to perform control operations for example in a smart home. The boards can be integrated into a smart home system like Home Assistant or FHEM for monitoring and setting parameters. But unlike a centralized system the EWHome will keep performing there control tasks when the server or even the complete network are down.

See [https://github.com/ewaldshof/ewhome/wiki] for documentation.



## Statusanzeige

Die Boards sind mit 8 Zeilen à 16 Zeichen Monochrom-Displays ausgestattet, die folgende Informationen zeigen:

```text
Name d. Boards
0.8.0




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

