import network as net
from task import Task
from ubinascii import hexlify

class Network(Task):

    ssid     = "Wohnis"
    password = "y0ur_W1F1_p@sswORD"

    def __init__(self):
        super().__init__()
        self.wlan = net.WLAN(net.STA_IF)
        self.wlan.active(True)
        self.mac = hexlify(self.wlan.config("mac"), ":").decode()
        self.ip = "0.0.0.0"
        self.short_ip = "  .0"
        self.wlan_msg = "Init ..."

    def update(self, scheduler):
        status = self.wlan.status()
        if status == net.STAT_IDLE or status == net.STAT_NO_AP_FOUND:
            self.wlan.connect(Network.ssid, Network.password)
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
            msg = "OK: " + self.short_ip
        else:
            msg = "Unknown"
        self.wlan_msg = msg
