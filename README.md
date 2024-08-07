# ewhome 0.8.0

EWHome is a system to conveniently configure a set of microcontroller boards to perform control operations for example in a smart home. The boards can be integrated into a smart home system like Home Assistant or FHEM for monitoring and setting parameters. But unlike a centralized system the EWHome will keep performing the configured control tasks when the server or even the complete network is down.

It is currently running on ESP32 but should be easy to port to any device that is running micropython. Running on CPython should be possible with a very small abstraction layer.

See [https://github.com/ewaldshof/ewhome/wiki] for documentation.

> [!NOTE]
> For production use we recommend [ESPHome](https://esphome.io/). It is much more active, mature, stable and complete than this project.
> However, EWHome has some unique concepts. For example there is no compile time, much less dependencies, it needs no dedicated server except for MQTT. If you are interested in any of this you are very welcome to contribute.

Added private git repo with configs as git submodule. 

After checkout run:
```bash
git submodule init
git submodule update
```

To update submodule run:
```bash
git submodule update --remote
```
