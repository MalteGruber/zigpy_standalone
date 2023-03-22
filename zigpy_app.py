#!/usr/bin/python3
from zigpy.config import CONF_DEVICE
import zigpy.config as conf
from zigpy.types.named import EUI64
import zigpy.device
import asyncio

from asyncio import create_task

import shella
import json
"""
Replace 'zigpy_xbee' with the radio that you are using, you can download it using pip.
https://github.com/zigpy/zigpy-xbee
https://github.com/zigpy/zigpy-deconz
https://github.com/zigpy/zigpy-zigate
"""
from zigpy_xbee.zigbee.application import ControllerApplication
from zigpy.zcl.clusters.general import OnOff


s=OnOff.server_commands.get(0x0)



def print_cluster_info(cluster):
    print(cluster.name)
    for x in cluster.server_commands:
        s=OnOff.server_commands.get(x)
        if s:
            print(f"Command '{s.name}', arguments= {s.schema.__dict__.get('__annotations__')}")
    for x in cluster.client_commands:
        s=OnOff.server_commands.get(x)
        if s:
            print(f"Command '{s.name}', arguments= {s.schema.__dict__.get('__annotations__')}")

    for k,v in enumerate(cluster.attributes_by_name):
        print(f"Attribute {k}: {v} ")


    

if 0:
    for c in OnOff._registry:
        cluster=OnOff._registry.get(c)
        print(cluster)
        print(cluster.attributes_by_name.keys())
        print_cluster_commands(cluster)

if 0:
    import sys
    sys.exit(1)


device_config = {
    #Change to your device
    conf.CONF_DEVICE_PATH: "/dev/ttyDigi",
}

zigpy_config = {
    conf.CONF_DATABASE: "zigpy.db",
    conf.CONF_DEVICE: device_config,
    conf.CONF_NWK_CHANNEL: 20
}

cluster_help="[device_id:int|ieee] [endpoint:int] [cluster:int] [in_out:str]"
cluster_template="%s %d %d %s"


"""
argv=[device_id:int|ieee, endpoint:int, cluster:int, in_out:str]
"""
def get_cluster_from_args(argv:list):
    try:
        #The IEEE address is being used as keys in a dict
        device_ids=list(za.devices.keys())
        device=None
        

        if ":" in argv[1]:
            device=za.get_device(EUI64.convert(argv[1]))
        
        else:
            try:
                dev_id=int(argv[1])
                ieee=str(device_ids[dev_id])
                device=za.get_device(EUI64.convert(ieee))
            except:

                dev_help_list=[str(i)+':\t'+str(v) for i,v in enumerate(device_ids)]
                print(f"Could not find device <{dev_id}>, available devices are:")
                print("<id>\t<IEEE>")
                print('\n'.join(dev_help_list))
                print("Please provide either as a IEEE address or id")
                return None

        endpoint_id=int(argv[2])
        endpoint=None
        help_list=[str(ep) for ep in device.endpoints.values()]
        try:
            endpoint=device.endpoints.get(endpoint_id)
            if not endpoint:
                raise Exception("No endpoint found")
        except:
            print(device.endpoints.values())
            
            print(f"Could not find endpoint {endpoint_id}, avalible endpoints for device {argv[1]} are:\n",'\n'.join(help_list))
            return None
        cluster_id=int(argv[3])    
        out_in=argv[4].lower()
        try:
            cluster=None
            if out_in in ["o","output","out"]:       
                cluster=endpoint.out_clusters.get(cluster_id)
            elif out_in in ["i","input","in"]:
                cluster=endpoint.in_clusters.get(cluster_id)
            else:
                print("Please specifiy cluster direction as i|in|input or o|out|output")
                return None
            if not cluster:
                raise Exception("Could not find cluster")
            return cluster
        except:
            print(f"Could not find cluster {cluster_id}, available clusters are:\n",'\n'.join(help_list))
        return None
    except:
        print("ERROR, Please use [device_id:int|ieee, endpoint:int, cluster:int, in_out:str]")

@shella.shell_cmd(["cluster","ci"],desc="Get cluster info",usage=f"[cluster_id:int]",template=f"%d")
async def cluster_info_cmf(argv):
    cluster=OnOff._registry.get(int(argv[1]))
    print_cluster_info(cluster)


@shella.shell_cmd(["command","c"],desc="Enable pairing mode",usage=f"{cluster_help} [json_cmd]",template=f"{cluster_template} %s")
async def command_cmd(argv):

    if len(argv)<2:
        print("device_id:int|ieee, endpoint:int, cluster:int, in_out:str, command_id, (json_cmd)")
        print("Example, turn off onOff cluster: c 9 1 6 in 0")
        print("Example, command 1 1 3 in 0 {'identify_time':10}")
        return 

    #https://github.com/zigpy/zigpy/blob/dev/zigpy/zcl/clusters/general.py

    cluster=get_cluster_from_args(argv)
    command_id=None
    if not cluster:
        return
    try:
        command_id=int(argv[5])
    except:
        print("Provide command id:int")
        return
    cmd_args={}
    try:
        cmd_args=json.loads(argv[6])
    except:
        pass
    print("Cmd args",cmd_args)

    #command 1 1 3 in 0 {"identify_time":10}
    await cluster.command(command_id,**cmd_args)

@shella.shell_cmd(["pair","p"],desc="Enable pairing mode",usage=f"[pair_duration]",template="%d")
async def pair_cmd(argv):

    if len(argv)>1:
        duration=argv[1]
        await za.permit(int(duration))
        if(int(duration)>254):
            print("Warning: please provide a duration from 1-254 seconds")
        print(f"Allowing pairing for {duration} seconds")            
    else:
        print("Please provide pairing time from 1-254 seconds")
        return False

@shella.shell_cmd(["bind","bd"],desc="Bind to a device",usage=f"{cluster_help}",template=f"{cluster_template}")
async def bind_cmd(argv):
    await get_cluster_from_args(argv).bind()

@shella.shell_cmd(["unbind"],desc="Undbind from a device")
async def unbind_cmd(argv):     
    await get_cluster_from_args(argv).unbind()

@shella.shell_cmd(["list","ls"],desc="Shows all avalible devices")
async def devices_list_cmd(argv):
    print(f"Found {len(za.devices.values())} devices...")        
    for i,device in enumerate(za.devices.values()):
        print(f"{i}: {device.ieee}: '{device.manufacturer}': '{device.model}'")   

@shella.shell_cmd(["device","d"],desc="Shows device information",usage="[int|ieee]",template="%s")
async def devices_cmd(argv):
    if len(argv)<1:
        print("Please provide device int|ieee")
    for i,device in enumerate(za.devices.values()):
        if i==int(argv[1]):
            print(f"====== {i}: {device.manufacturer} {device.model} ====== ")
            print(f"IEEE Adress {device.ieee}")
            print(f"NWK {device.nwk}")
            print(f"Initialized {device.is_initialized}")
            print(f"rssi {device.rssi}")
            for endpoint in device.endpoints.values():

                if not isinstance(endpoint, zigpy.zdo.ZDO):
                    print(f"~~~ Endpoint #{endpoint.endpoint_id} ~~~")
                    def print_clusters_info(clusters):
                        any_clusters=False
                        for k,v in clusters.items():
                            any_clusters=True
                            #print(f"{v.cluster_id} Cluster Command: {list(command.name for command in v.client_commands.values())}")
                            print(f"\t{v.cluster_id}\t{v.ep_attribute}")
                        if not any_clusters:
                            print("\tNo clusters")
                    print("  Input clusters:")
                    print_clusters_info(endpoint.in_clusters)
                    print("  Output clusters:")
                    print_clusters_info(endpoint.out_clusters)
        

@shella.shell_cmd(["q","quit"],desc="Quit program")
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
    def __init__(self,za,ext_callback):
        self.za=za
        self.ext_callback=ext_callback
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
        if(self.ext_callback):
            self.ext_callback(ieee=device.ieee,message=message,cluster=cluster)
        else:
            print(f"Handle_message {device.ieee} profile {profile}, cluster {cluster}, src_ep {src_ep}, dst_ep {dst_ep},\tmessage {message} ")
        
    def device_joined(self,device: zigpy.device.Device):
        print("device_joined",device)
    def group_added(self,group,ep):
        print("Group added",group,ep)
    def device_left(self,device: zigpy.device.Device):
        print("device_left",device)

def get_za():
    global za
    return za

async def start_zigbee(ext_callback):
    try:
        global za
        za = await ControllerApplication.new(
            config=ControllerApplication.SCHEMA(zigpy_config),
            auto_form=True,
            start_radio=True,
        )

        listener = YourListenerClass( za,ext_callback )

        za.add_listener(listener)
        za.groups.add_listener(listener)
        print("ZigPy started!")

    except Exception:
        import traceback
        traceback.print_exc()

running=True
async def run_application(ext_callback=None):
    await start_zigbee(ext_callback)
    shella_task_ = asyncio.create_task(shella.shell_task())
    shella.set_prompt("zigbee$")
    await shella_task_
    if za:
        await za.shutdown()
    running=False

async def stop_application():
    print("Stopping application...")
    global running
    running=False
    await za.shutdown()


if __name__ =="__main__":
    asyncio.run(run_application())
