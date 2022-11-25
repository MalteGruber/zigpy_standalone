#!/usr/bin/python3
from zigpy.config import CONF_DEVICE
import zigpy.config as conf
from zigpy.types.named import EUI64
import zigpy.device
import asyncio

from asyncio import create_task
from mincli import demo_command,start_mincli,stop_minicli

"""
Replace 'zigpy_xbee' with the radio that you are using, you can download it using pip.
https://github.com/zigpy/zigpy-xbee
https://github.com/zigpy/zigpy-deconz
https://github.com/zigpy/zigpy-zigate
"""
from zigpy_xbee.zigbee.application import ControllerApplication

device_config = {
    #Change to your device
    conf.CONF_DEVICE_PATH: "/dev/ttyUSB0",
}

zigpy_config = {
    conf.CONF_DATABASE: "zigpy.db",
    conf.CONF_DEVICE: device_config
}

@demo_command(commands=["pair","p"],desc="Enable pairing mode")
async def pair_cmd(argv):
    if len(argv)>1:
        duration=argv[1]
        await za.permit(254)
        print(f"Allowing pairing for {duration} seconds")            
    else:
        print("Please provide pairing time from 1-254 seconds")

async def binding_handler(dev,endpoint_id:int,cluster_id:int,is_unbind=False,is_input_bind =False):
    device=za.get_device(EUI64.convert(dev))
    print(f"Binding device {device}")
    if is_unbind:
        pass
    else:

        await device.endpoints.get(endpoint_id).out_clusters.get(cluster_id).bind()

@demo_command(commands=["bind","bd"],desc="Bind to a device")
async def bind_cmd(argv):     
    if(len(argv)<5):
        print("please provide device:ieee|int endpoint:int, cluster:int, direction:'in'|'out'")
        return
    dev_id=int(argv[1])
    ieee=str(list(za.devices.keys())[dev_id])
    print("IEEE",ieee)
    cluster_id=int(argv[3])
    is_input_bind=True
    if argv[4].lower() in ["o","output","out"]:
        is_input_bind=False
    await binding_handler(dev=ieee,endpoint_id=int(argv[2]),cluster_id=cluster_id,is_unbind=False,is_input_bind=is_input_bind)

@demo_command(commands=["list","ls"],desc="Shows all avalible devices")
async def devices_list_cmd(argv):
    print(f"Found {len(za.devices.values())} devices...")        
    for i,device in enumerate(za.devices.values()):
        print(f"{i}: {device.ieee}: '{device.manufacturer}': '{device.model}'")   

@demo_command(commands=["device","d"],desc="Shows device information")
async def devices_cmd(argv):
    if len(argv)<1:
        print("Please provide device int|ieee")
    for i,device in enumerate(za.devices.values()):
        if i==int(argv[1]):
            print(f"====== {i}: {device.manufacturer} {device.model} ====== ")
            print(f"IEEE Adress {device.ieee}")
            print(f"NWK {device.nwk}")
            print(f"Initialized {device.is_initialized}")
            for endpoint in device.endpoints.values():
                if not isinstance(endpoint, zigpy.zdo.ZDO):
                    def print_clusters_info(clusters):
                        any_clusters=False
                        for k,v in clusters.items():
                            any_clusters=True
                            #print(f"{v.cluster_id} Cluster Command: {list(command.name for command in v.client_commands.values())}")
                            print(f"\t{v.cluster_id}\t{v.ep_attribute}")
                        if not any_clusters:
                            print("\tNo clusters")
                    print("Input clusters:")
                    print_clusters_info(endpoint.in_clusters)
                    print("Output clusters:")
                    print_clusters_info(endpoint.out_clusters)

@demo_command(commands=["q","quit"],desc="Quit program")
async def stop_program(argv):      
    global running
    import sys
    print("Shutting down zigbee, saving state...")
    await za.shutdown()
    print("Stopping other tasks...")
    running=False
    stop_minicli()
    print("Good bye")
    
class YourListenerClass:
    def __init__(self,za):
        self.za=za
    """
    These are called by the ControllerApplication using call like this: 
    self.listener_event("raw_device_initialized", device)
    """
    def raw_device_initialized(self,device: zigpy.device.Device):
        print("Raw device init",device)
    def device_initialized(self,device: zigpy.device.Device):
        print("device_initialized",device)
    def device_removed(self,device: zigpy.device.Device):
        print("device_removed",device)
    def handle_message(
        self,
        device: zigpy.device.Device,
        profile: int,
        cluster: int,
        src_ep: int,
        dst_ep: int,
        message: bytes,
    ) -> None:
        print(f"Handle_message {device.ieee} profile {profile}, cluster {cluster}, src_ep {src_ep}, dst_ep {dst_ep},\tmessage {message} ")


    def device_joined(self,device: zigpy.device.Device):
        print("device_joined",device)
    def group_added(self,group,ep):
        print("Group added",group,ep)
    def device_left(self,device: zigpy.device.Device):
        print("device_left",device)

async def start_zigbee():
    try:
        global za
        za = await ControllerApplication.new(
            config=ControllerApplication.SCHEMA(zigpy_config),
            auto_form=True,
            start_radio=True,
        )
        print("Started ZigPy ControllerApplication")
        listener = YourListenerClass( za )

        za.add_listener(listener)
        za.groups.add_listener(listener)
        print("Zigbee started!")

    except Exception:
        import traceback
        traceback.print_exc()

running=True
async def start_application():
    await start_zigbee()
    start_mincli()
    while running:            
        await asyncio.sleep(0.1)

asyncio.run(start_application())
