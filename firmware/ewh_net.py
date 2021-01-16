import network as net
from task import Task
from ubinascii import hexlify
import ujson
import ntptime

class Network(Task):

    def __init__(self):
        super().__init__()
        with open("/wlan.json", "r") as wlan_config:
            self.config = ujson.load(wlan_config)
        print("WLAN config:", self.config)
        self.wlan = net.WLAN(net.STA_IF)
        self.wlan.active(True)
        self.status = None
        self.mac = hexlify(self.wlan.config("mac"), ":").decode()
        self.ip = "0.0.0.0"
        self.short_ip = "  .0"
        self.wlan_msg = "Init ..."

    def update(self, scheduler):
        status = self.wlan.status()
        if status == self.status: # no change, do nothing
            return
        if status == net.STAT_IDLE or status == net.STAT_NO_AP_FOUND:
            self.wlan.connect(self.config["ssid"], self.config["password"])
            msg = "Starting"
        elif status == net.STAT_CONNECTING:
            msg = "Trying.."
        elif status == net.STAT_WRONG_PASSWORD:
            msg = "Wrong PW"
        elif status == net.STAT_GOT_IP:
            ip = self.wlan.ifconfig()[0]
            if ip != self.ip:
                self.ip = ip
                self.short_ip = "{:>4s}".format(ip[ip.rindex("."):])
            msg = "NTP " + self.short_ip
            ntptime.settime() # this takes to long. Better schedule a task for that
            msg = "OK: " + self.short_ip
        else:
            msg = "Unknown"
        self.wlan_msg = msg
        self.status = status
