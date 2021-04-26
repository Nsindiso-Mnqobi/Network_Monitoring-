from ncclient import manager
from CSR1000v import router

with manager.connect(host = router['host'], port = router['port'], username=router['username'], password= router['password'], hostkey_verify=False) as device:
    for capability in device.server_capabilities:
        print(capability)
