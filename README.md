# Zigpy Hello World
This program is an interactive hello world example for the [zigpy](https://github.com/zigpy/zigpy) library.

## Supported radios
Have a look under https://github.com/zigpy for the latest supported radios. Here are some of the radios that are supported at the point of writing

https://github.com/zigpy/zigpy-deconz

https://github.com/zigpy/zigpy-xbee

https://github.com/zigpy/zigpy-znp

https://github.com/zigpy/zigpy-cc

https://github.com/zigpy/zigpy-zigate

To change the radio type, replace the zigpy_xbee with your radio type and install the library using pip. Also ensure you change the device settings such as UART baud rate if needed.
```python
from zigpy_xbee.zigbee.application import ControllerApplication
```
If we were using zigpy-deconz the following would be used:

```python
from zigpy_deconz.zigbee.application import ControllerApplication
```

## Usage

The program is started with `./zigpy_app.py`
```bash
mg@computer:~/zigpy-standalone$ ./zigpy_app.py 
Started ZigPy ControllerApplication
Zigbee started!
>?
Avalible commands are
pair p  : Enable pairing mode
bind bd         : Bind to a device
list ls         : Shows all avalible devices
device d        : Shows device information
q quit  : Quit program
>
```

**List all devices**
```
>list
Found 2 devices...
0: 00:13:a2:00:41:85:c1:9f: 'Digi': 'XBee'
1: 04:cd:15:ff:fe:0f:b2:29: 'IKEA of Sweden': 'TRADFRI on/off switch'
>
```
**Getting Device Info**
```
>d 1
====== 1: IKEA of Sweden TRADFRI on/off switch ====== 
IEEE Adress 04:cd:15:ff:fe:0f:b2:29
NWK 0xE877
Initialized True
Input clusters:
        0       basic
        1       power
        3       identify
        9       alarms
        32      poll_control
        4096    lightlink
        64636   manufacturer_specific
Output clusters:
        3       identify
        4       groups
        6       on_off
        8       level
        25      ota
        258     window_covering
        4096    lightlink
>
```

## Example: Pairing and Binding a device
This is an example of how the program can be used to interact with a wall switch.

### Pairing the device

First we need to tell the coordinator to go into pairing mode, the ZigBee standard says that the maximum time is 254 seconds, so we provide 120 seconds as the pairing window.

```
>pair 120
Allowing pairing for 120 seconds
```
*We now put the zigbee device to be paired into pairing mode*

When we get a message like this we know the device joined the coordinator.
```
>device_joined <Device model='TRADFRI on/off switch' manuf='IKEA of Sweden' nwk=0x7E7D ieee=04:cd:15:ff:fe:0f:b2:29 is_initialized=True>
```
### Binding the device
We are using ZigBee ZCL to get data from the switch. This means for the switch to send anything to us we first have to bind to a cluster (See the cluster device info section for how to get a list of the clusters of a device). These clusters are defined by the standard and provide a predefined way of interacting with a device.

```
>bind 1 1 6 out
IEEE 04:cd:15:ff:fe:0f:b2:29
Binding device <Device model='TRADFRI on/off switch' manuf='IKEA of Sweden' nwk=0x7E7D ieee=04:cd:15:ff:fe:0f:b2:29 is_initialized=True>
``` 

## Reading material and get started with Zigbee



### Clusters
For information about various clusters, have a look in [/zigpy/zcl/clusters](https://github.com/zigpy/zigpy/blob/dev/zigpy/zcl/clusters/).

For example in the cluster OnOff (6) the zigpy library defines the attributes and commands in the class
```python
class OnOff(Cluster):
    .....


    attributes: dict[int, ZCLAttributeDef] = {
        0x0000: ZCLAttributeDef("on_off", type=t.Bool, access="rps", mandatory=True),
        0x4000: ZCLAttributeDef("global_scene_control", type=t.Bool, access="r"),
        .....
     
        0xFFFE: foundation.ZCL_REPORTING_STATUS_ATTR,
    }
    server_commands: dict[int, ZCLCommandDef] = {
        0x00: ZCLCommandDef("off", {}, False),
        0x01: ZCLCommandDef("on", {}, False),
        0x02: ZCLCommandDef("toggle", {}, False),
        .....
    }
    client_commands: dict[int, ZCLCommandDef] = {}
```


## Limitations
**This program currently does not support sending commands from the coordinator!**
