
import json
import uuid
import os
import getpass
import socket
import sys
from datetime import datetime

from . device import get_device

# Configuration object, loads configuration from a JSON file, and then
# supports path navigate with config.get("part1.part2.part3")
class Config:
    def __init__(self, file="config.json"):
        self.config = json.loads(open(file).read())
    def get(self, key):
        cfg = self.config
        for v in key.split("."):
            cfg = cfg[v]
        return cfg


# Initialise configuration file with some (mainly) static values.  Also,
# collate personal information for the Fraud API.
def initialise_config(config_file):

    # This gets hold of the MAC address, which the uuid module knows.
    # FIXME: Hacky.
    try:
        mac = uuid.getnode()
        mac = [
            '{:02x}'.format((mac >> ele) & 0xff)
            for ele in range(0,8*6,8)
        ][::-1]
        mac = ':'.join(mac)
    except:
        # Fallback.
        mac = '00:00:00:00:00:00'

    # Operating system information, turn into a user-agent.  Can't get
    # device-manufacturer without accessing /dev/mem on Linux (using
    # e.g. using py-dmidecode).  Not appopriate to have this code running
    # with those level of privileges.
    uname = os.uname()
    di = {
        'os-family': uname.sysname,
        'os-version': uname.release,
        'device-manufacturer': '',
        'device-model': '',
        'id': str(uuid.uuid1()),
    }

    config = {
        "accounts": {
	    "file": "accounts/accounts.gnucash",
            "vatDueSales": "VAT:Output:Sales",
            "vatDueAcquisitions": "VAT:Output:EU",
            "totalVatDue": "VAT:Output",
            "vatReclaimedCurrPeriod": "VAT:Input",
            "netVatDue": "VAT",
            "totalValueSalesExVAT": "Income:Sales",
            "totalValuePurchasesExVAT": "Expenses:VAT Purchases",
            "totalValueGoodsSuppliedExVAT": "Income:Sales:EU:Goods",
            "totalAcquisitionsExVAT": "Expenses:VAT Purchases:EU Reverse VAT",
            "liabilities": "VAT:Liabilities",
            "bills": "Accounts Payable",
            "vendor": {
                "id": "hmrc-vat",
                "currency": "GBP",
                "name": "HM Revenue and Customs - VAT",
                "address": [
                    "123 St Vincent Street",
                    "Glasgow City",
                    "Glasgow G2 5EA",
                    "UK"
                ]
            }
        },
        "application": {
            "profile": "test",
            "client-id": "<CLIENTID>",
            "client-secret": "<CLIENTSECRET>"
        },
        "identity": {
            "vrn": "<VRN>",
            "device": di,
            "user": getpass.getuser(),
            "hostname": socket.gethostbyname(socket.gethostname()),
            "mac-address": mac,
            "time": datetime.utcnow().isoformat()[:-3] + "Z"
        }
    }

    with open(config_file, "w") as cfg_file:
        cfg_file.write(json.dumps(config, indent=4))

    sys.stderr.write("Wrote %s.\n" % config_file)

def initialise_device_config(config_file):

    dmi = get_device()
    if dmi == None:
        raise RuntimeError("Couldn't fetch device information, run sudo?")

    config = Config(config_file)

    uname = os.uname()
    config.config['identity']['device'] = {
        'os-family': uname.sysname,
	'os-version': uname.release,
        'device-manufacturer': dmi["manufacturer"],
        'device-model': dmi["model"],
        'id': str(uuid.uuid1()),
    }

    with open(config_file, "w") as cfg_file:
        cfg_file.write(json.dumps(config.config, indent=4))

    sys.stderr.write("Wrote %s.\n" % config_file)
