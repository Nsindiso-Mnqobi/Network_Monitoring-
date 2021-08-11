from ncclient import manager
from ncclient import xml_
from ncclient.operations import subscribe
from ncclient.transport.errors import SSHUnknownHostError
from CSR1000v import router
import csv
import xmltodict 
import requests
import json
from time import ctime 

class  configure_mdt:
    host = ""
    subscription_id = 0
    xpath =  ""
    r_ip_address = ""
    s_ip_address =  ""
    period = ""

    def __init__(self,host, subscription_id ,xpath,r_ip_address,s_ip_address,
                        period):
        self.host= host
        self.subscription_id =subscription_id
        self.xpath=xpath
        self.r_ip_address=r_ip_address
        self.s_ip_address=s_ip_address
        self.period=period
    
    def configure_device(self):

        with manager.connect(host = self.host, port = router['port'], 
                                            username=router['username'], password= router['password'], 
                                            hostkey_verify=False) as device:
            
            with device.locked("running"):
                config_template = open('Config-template.xml').read()
                netconf_config = config_template.format(subscription_id=self.subscription_id,
                                                                                    xpath = self.xpath,
                                                                                    receiver_ip_address = self.r_ip_address ,
                                                                                    source_ip_address = self.s_ip_address,
                                                                                    period = self.period)

                device_reply = device.edit_config(config = netconf_config, target = "running")

                
    def get_config(self):

        with manager.connect(host = self.host, port = router['port'], 
                                            username=router['username'], password= router['password'], 
                                            hostkey_verify=False) as device:
            
            get_config = open("get_config.xml").read()
            netconf_filter = get_config.format(sub_id = self.subscription_id,
                                                                    source_address = self.s_ip_address)
            
            subscription_config = device.get(netconf_filter)
            subscription = xmltodict.parse(subscription_config.xml)["rpc-reply"]["data"]["mdt-oper-data"]
            T = ctime()
            print("*" * 25 + self.host + "*" * 50)
            Power = "Subscription ID:  " + subscription["mdt-subscriptions"]["subscription-id"] + "\n" + "Source Address:   " + subscription["mdt-subscriptions"]["base"]["source-address"] + "\n" +"Stream:   " +  subscription["mdt-subscriptions"]["base"]["stream"] + "\n" + "Xpath:   " + subscription["mdt-subscriptions"]["base"]["xpath"]  + "\n" + "State:   "  +  subscription["mdt-subscriptions"]["state"]  + "\n" +  "Comments:  "+ subscription["mdt-subscriptions"]["state"] + "\n" + "Receiver Address:   " + subscription["mdt-subscriptions"]["mdt-receivers"]["address"]  + "\n" + "Port:   " + subscription["mdt-subscriptions"]["mdt-receivers"]["port"]  + "\n" + "Connection State   :" + subscription["mdt-connections"]["state"]  + "\n" + "Time of Configuration   :"  +  T        
            return Power   

    def save_config(self):

        with manager.connect(host = self.host, port = router['port'], 
                                            username=router['username'], password= router['password'], 
                                            hostkey_verify=False ,device_params={'name':'csr'}) as device:

            save_body =  """ 
            <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
            """
            save_rpc = device.dispatch(xml_.to_ele(save_body)) 
            save_reply = xmltodict.parse(save_rpc.xml) 
            reply = self.host +" : "+ save_reply["rpc-reply"]["result"]["#text"]
            return reply

    def send_message(self, message):
        token = 'Yzg4Nzg0YTUtYzkzZi00YmEzLWFjNmUtNTcxOTdkOGFhMWRlZTI5NGMxOTgtMzdj_PF84_consumer'

        headers = {
         'Authorization' : 'Bearer {token}'.format(token=token),
         'Content-Type' : 'application/json'
        }
        
        msg_url = 'https://webexapis.com/v1/messages'
        id_room = "Y2lzY29zcGFyazovL3VzL1JPT00vNDhjMjY4NjAtYTgzNy0xMWViLWE3ZTQtY2Q5MTkwNzU5ZTRk"
        
        msg_body ={
        "roomId": id_room,
        "text": message
        }

        Body = json.dumps(msg_body)

        msg_power = requests.request("POST",msg_url, data= Body, headers=headers).json()
      

if  __name__ == "__main__":

    with open("subscription_details.csv") as sub_details, open("host_details.csv") as host_details:
        sub_list = list(csv.reader(sub_details))
        host_list = list(csv.reader(host_details))
        for x in host_list:
            host =x[0]
            for row in sub_list:
                sub=row[0]
                xpath=row[1]
                r_ip = row[2] 
                s_ip = row[3] = host
                period = row[4]
                Config = configure_mdt(host,sub, xpath,r_ip, s_ip, period)
                Config.configure_device()            
                Config.send_message(Config.get_config())
            Config.send_message(Config.save_config())




s