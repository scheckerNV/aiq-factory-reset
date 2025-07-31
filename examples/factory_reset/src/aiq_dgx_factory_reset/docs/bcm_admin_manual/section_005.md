## node010..node014 get forced to 1000 duplex

if [[ $CMD_HOSTNAME = node01[0-4] ]]

then

echo 'ETHTOOL_OPTS="speed 1000 duplex full"'>>/localdisk/etc/sysconfig/network-scripts/ifcfg-eth0

fi


The method of enforcing an interface space just outlined is actually just for educational illustration,
and is not a recommended method.


**206** **Configuring The Cluster**


In practice, the recommended way to enforce an interface speed is to simply set it in the CMDaemon
database. For example, for the boot interface of node001 it could be via the Base View navigation path:
Devices  - Nodes[node001]  - Edit  - Settings  - Interfaces[BOOTIF]  - Edit  - Speed


**3.19.5** **Examples Of Configuring Nodes With Or Without CMDaemon**
A node or node category can often have its software configured in CMDaemon via Base View or cmsh :


**Example**


**Configuring a software for nodes using Base View or** cmsh **:** If the software under consideration is
CUPS, then a node or node category can manage it from Base View or cmsh as outlined in section 3.14.2.


A counterexample to this is:


**Example**


**Configuring a software for nodes without using Base View or** cmsh [3] **, using an image:** Software images
can be created with and without CUPS configured. Setting up nodes to load one of these two images via
a node category is an alternative way of letting nodes run CUPS.


Whether node configuration for a particular functionality is done with CMDaemon, or directly with
the software, depends on what an administrator prefers. In the preceding two examples, the first example, that is the one with Base View or cmsh setting the CUPS service, is likely to be preferred over
the second example, where an entire separate image must be maintained. A new category must also be
created in the second case.

Generally, sometimes configuring the node via BCM, and not having to manage images is better,
sometimes configuring the software and making various images to be managed out of it is better, and
sometimes only one of these techniques is possible anyway.


**Configuring Nodes Using Base View Or** cmsh **: Category Settings**
When configuring nodes using Base View or cmsh, configuring particular nodes from a node category to
overrule the state of the rest of its category (as explained in section 2.1.3) is sensible for a small number
of nodes. For larger numbers it may not be organizationally practical to do this, and another category
can instead be created to handle nodes with the changes conveniently.
The CUPS service in the next two examples is carried out by implementing the changes via Base
View or cmsh acting on CMDaemon.


**Example**


**Setting a few nodes in a category:** If only a few nodes in a category are to run CUPS, then it can be done
by enabling CUPs just for those few nodes, thereby overriding (section 2.1.3) the category settings.


**Example**


**Setting many nodes to a category:** If there are many nodes that are to be set to run CUPS, then a separate, new category can be created (cloning it from the existing one is easiest) and those many nodes are
moved into that category, while the image is kept unchanged. The CUPS service setting is then set at
category level to the appropriate value for the new category.


In contrast to these two examples, the software image method used in section 3.19.2 to implement
a functionality such as CUPS would load up CUPS as configured in an image, and would not handle


3 except to link nodes to their appropriate image via the associated category


**3.20 Saving A Backup Of Configuration Files With** versionconfigfiles **207**


it via CMDaemon [3] . So, in section 3.19.2, software images prepared by the administrator are set for a
node category. Since, by design, images are only selected for a category, a node cannot override the
image used by the category other than by creating a new category, and using it with the new image. The
administrative overhead of this can be inconvenient.

Administrators would therefore normally prefer letting CMDaemon track software functionality
across nodes as in the last two examples, rather than having to deal with tracking software images manually. Indeed, the roles assignment option (section 2.1.5) is just a special pre-configured functionality
toggle that allows CMDaemon to set categories or regular nodes to provide certain functions, typically
by enabling services.


**3.20** **Saving A Backup Of Configuration Files With** versionconfigfiles


If versionconfigfiles is set to the value yes for a node or a category, then if configuration files changed
for that node or category due to CMDaemon, then the old configuration files are saved.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% set versionconfigfiles yes; commit


This is useful, for example, if an administrator would like to know what the configuration was just
before it was changed.
If a configuration change takes place, then the old configuration files are automatically sent from the
node where they changed, to the active head node. The configuration files:


  - are saved on the active head node under the directory /var/spool/cmd/config_file_versions, under their node name.


  - have a modification time that indicates the time of the change.


  - are given a suffix in the form of the local unix epoch time.


**Example**


[root@basecm11 ~]# cd /var/spool/cmd/

[root@basecm11 cmd]# tree -a --charset=C config_file_versions/
config_file_versions/

|-- node001

| |-- cm

| | `-- local

| | `-- modulefiles

| | `-- slurm

| | |-- .modulerc.lua.1970-01-01_01:00:00

| | `-- slurm

| | `-- 21.08.8.1970-01-01_01:00:00

...


[root@basecm11 cmd]# cd config_file_versions/node001/cm/local/modulefiles/slurm/

[root@basecm11 slurm]# ls -al .modulerc.lua.1970-01-01_01:00:00

-rw-r--r-- 1 root root 43 Mar 14 17:22 .modulerc.lua.1970-01-01_01:00:00

[root@basecm11 slurm]#


# **4**

### **Power Management**

Aspects of power management in NVIDIA Base Command Manager include:


  - managing the main power supply to nodes through the use of power distribution units, baseboard
management controllers, or CMDaemon


  - monitoring power consumption over time


  - setting power-saving options in workload managers


  - ensuring the passive head node can safely take over from the active head during failover (Chapter 15)


  - allowing cluster burn tests to be carried out (Chapter 11 of the _Installation Manual_ )


The ability to control power inside a cluster is therefore important for cluster administration, and
also creates opportunities for power savings. This chapter describes BCM power management features.
In section 4.1 the configuration of the methods used for power operations is described.
Section 4.2 then describes the way the power operations commands themselves are used to allow the
administrator turn power on or off, reset the power, and retrieve the power status. It explains how these
operations can be applied to devices in various ways.
Section 4.3 briefly covers monitoring power.
The integration of power saving with workload management systems is covered in the chapter on
Workload Management (section 7.9).
Power management at rack level and at data center level, and using power shelves, is covered in
chapters 3 and 4 of the _NVIDIA Mission Control Manual_ .


**4.1** **Configuring Power Parameters**


Several methods exist to control power to devices:


  - Power Distribution Unit (PDU) based power control


  - IPMI-based power control (for node devices only)


  - Custom power control


  - HP iLO-based power control (for node devices only)


  - Dell DRAC-based power control (for node devices only)


  - Cisco UCS CIMC-based power control (for node devices only)


  - Redfish-based power control (for node devices only)


**210** **Power Management**


**4.1.1** **PDU-based Power Control**

**Introduction To PDU-based Power Control**

For PDU-based power control, the power supply of a device is plugged into a port on a PDU. The device
can be a node, but also anything else with a power supply, such as a switch or a blade chassis. The device
can then be turned on or off by changing the state of the PDU port.


**Configuring The PDU Itself**
To use PDU-based power control, the PDU itself must be added and configured as a device in the cluster,
and must be reachable over the network. PDU configuration was introduced in section 3.9. A summary
of the configuration of PDUs is as follows:
The PDU can be added via cmsh using device mode, and is set as an object with a type of
PowerDeviceUnit and is given a name. The value for Ports is automatically read, and is the number of
power ports available to the other devices in the cluster.
In Base View the corresponding navigation path for a PDU named mypdu is:


Devices  - PowerDistribution Unit list  - mypdu  - Add


**Configuring The Devices To Use The PDU**
After the PDU itself is configured, then the devices that use it can be configured to use the PDU and its
ports.
For example, for a node node001 that is be powered by the PDU mypdu, in Base View the configuration can be done using the navigation path:


Devices  - Nodes  - Physical Node list[node001]  - Edit  - Settings  - JUMP TO  - Power

Distribution Units - ADD - PDUPort


which opens up the PDU Port window (figure 4.1):


**4.1 Configuring Power Parameters** **211**


Figure 4.1: PDU configuration settings for a node


and allows the PDU and port used by node001 to be set.


**For the APC brand of PDUs:** the Power control property (page 138) should be set to apc, or the list
of PDU ports is ignored by default. Overriding the default is described in section 4.1.3.


**Power Ports: One-to-many And Many-to-one**
Nodes may have multiple power feeds for redundancy reasons. Thus, there may be multiple PDU ports
and multiple PDUs defined for a single device. The cluster management takes care of operating all ports
of a device in the correct order when a power operation is done on the device.
For example, if a PDU mypdu has its ports 2 and 4 connected to a blade chassis mychassis, then the
configuration can be specified using cmsh with:


**Example**


[basecm11->device*[mychassis]]% set powerdistributionunits mypdu:2 mypdu:4; commit


It is also possible for multiple devices to share the same PDU port. This is the case for example when
_twin nodes_ are used (i.e. two nodes sharing a single power supply). In this case, all power operations on
one device apply to all nodes sharing the same PDU port.


**Non-manageable PDUs**
If the PDUs defined for a node are not manageable, then the node’s baseboard management controllers
(that is, IPMI/iLO and similar) are assumed to be inoperative and are therefore assigned an unknown
state. This means that dumb PDUs, which cannot be managed remotely, are best not assigned to nodes
in BCM. It is suggested that administrators record that a dumb PDU is assigned to a node as follows:


  - in Base View the Notes field or the Userdefined1 / Userdefined2 fields can be used with the navigation paths:


**212** **Power Management**


Devices _[device]_   - Settings   - Partition   - Notes

or

Devices _[device]_   - Settings   - User Defined   - Userdefined1 / Userdefined1


  - in cmsh the equivalent is accessible on using the device from device mode, and running:


**–** set notes


**–** set userdefined1 or


**–** set userdefined2


**Manageable PDUs And Node Power Status**
For PDUs that are manageable:


  - In cmsh, power-related options can be accessed from device mode, after selecting a device:


**Example**


[basecm11]% device use node001

[basecm11->device[node001]]% show | grep -i power

Custom power script argument
Ipmi/iLO power reset delay 0

Power control apc

PowerDistributionUnits apc01:6 apc01:7


The power status of a node can be accessed with:


**Example**


[basecm11->device[node001]]% power status


If the node is up and has one or more PDUs assigned to it, then the power status is one of ON, OFF,

RESET, FAILED, or UNKNOWN :


**Power Status** **Description**


ON Power is on


OFF Power is off


RESET Shows during the short time the power is off


during a power reset. The reset is a hard power


off for PDUs, but can be a soft or hard reset for


other power control devices.


FAILED Power status script communication failure.


UNKNOWN Power status script timeout


**4.1.2** **IPMI-Based Power Control**

IPMI-based power control relies on the baseboard management controller (BMC) inside a node.
It is therefore only available for node devices. Blades inside a blade chassis typically use IPMI
for power management. Section 3.7 describes setting up networking and authentication for
IPMI/iLO/DRAC/CIMC/Redfish interfaces.


**4.1 Configuring Power Parameters** **213**


To carry out IPMI-based power control operations, the Power control property (page 138) must
be set to the IPMI interface through which power operations should be relayed. Normally this IPMI
interface is configured to be ipmi0 . Any list of configured APC PDU ports displayed in the GUI is
ignored by default when the Power control property is not apc .


**Example**


Configuring power parameters settings for all the nodes using cmsh, with IPMI interfaces that are called
ipmi0 :


[mycluster]% device

[...device]% foreach -t physicalnode (set powercontrol ipmi0; commit)


**Example**


Configuring power parameters settings for a node using cmsh with APC:


[mycluster]% device use node001

[...device[node001]]% set powerdistributionunits apc01:6 apc01:7 apc01:8

[...device*[node001*]]% get powerdistributionunits

apc01:6 apc01:7 apc01:8

[...device*[node001*]]% removefrom powerdistributionunits apc01:7

[...device*[node001*]]% get powerdistributionunits

apc01:6 apc01:8

[...device*[node001*]]% set powercontrol apc

[...device*[node001*]]% get powercontrol

apc

[...device*[node001*]]% commit


**4.1.3** **Combining PDU- and IPMI-Based Power Control**
By default when nodes are configured for IPMI Based Power Control, any configured PDU ports are
ignored. However, it is sometimes useful to change this behavior.
For example, in the CMDaemon configuration file directives in /cm/local/apps/cmd/etc/cmd.conf
(introduced in section 2.6.2 and listed in Appendix C), the default value of PowerOffPDUOutlet is false .
It can be set to true on the head node, and CMDaemon restarted to activate it.
With PowerOffPDUOutlet set to true it means that CMDaemon, after receiving an IPMI-based power
off instruction for a node, and after powering off that node, also subsequently powers off the PDU port.
Powering off the PDU port shuts down the BMC, which saves some additional power—typically a few
watts per node. When multiple nodes share the same PDU port, the PDU port only powers off when all
nodes served by that particular PDU port are powered off.
When a node has to be started up again the power is restored to the node. It is important that the
node BIOS is configured to automatically power on the node when power is restored.


**4.1.4** **Custom Power Control**

For a device which cannot be controlled through any of the standard existing power control options, it
is possible to set a custom power management script. This is then invoked by the cluster management
daemon on the head node whenever a power operation for the device is done.
Power operations are described further in section 4.2.


**Using** custompowerscript
To set a custom power management script for a device, the powercontrol attribute is set by the administrator to custom using either Base View or cmsh, and the value of custompowerscript is specified by
the administrator. The value for custompowerscript is the full path to an executable custom power
management script on the head node(s) of a cluster.


A custom power script is invoked with the following mandatory arguments:


**214** **Power Management**


myscript <operation> <device>


where <device> is the name of the device on which the power operation is done, and <operation>
is one of the following:


ON

OFF

RESET

STATUS


On success a custom power script exits with exit code 0. On failure, the script exits with a non-zero
exit-code.


**Using** custompowerscriptargument
The mandatory argument values for <operation> and <device> are passed to a custom script for processing. For example, in bash the positional variables $1 and $2 are typically used for a custom power
script. A custom power script can also be passed a further argument value by setting the value of
custompowerscriptargument for the node via cmsh or Base View. This further argument value would
then be passed to the positional variable $3 in bash .
An example custom power script is located at /cm/local/examples/cmd/custompower . In it, setting
$3 to a positive integer delays the script via a sleep command by $3 seconds.
An example that is conceivably more useful than a “ sleep $3 ” command is to have a “ wakeonlan
$3 ” command instead. If the custompowerscriptargument value is set to the MAC address of the node,
that means the MAC value is passed on to $3 . Using this technique, the power operation ON can then
carry out a Wake On LAN operation on the node from the head node.
Setting the custompowerscriptargument can be done like this for all nodes:


#!/bin/bash

for nodename in $(cmsh -c "device; foreach * (get hostname)")

do

macad=`cmsh -c "device use $nodename; get mac"`
cmsh -c "device use $nodename; set customscriptargument $macad; commit"

done


The preceding material usefully illustrates how custompowerscriptargument can be used to pass on
arbitrary parameters for execution to a custom script.
However, the goal of the task can be achieved in a simpler and quicker way using the environment
variables available in the cluster management daemon environment (section 3.3.1 of the _Developer Man-_
_ual_ ). This is explained next.


**Using Environment Variables With** custompowerscript
Simplification of the steps needed for custom scripts in CMDaemon is often possible because there are
values in the CMDaemon environment already available to the script. A line such as:


env > /tmp/env


added to the start of a custom script dumps the names and values of the environment variables to
/tmp/env for viewing.
One of the names is $CMD_MAC, and it holds the MAC address string of the node being considered.
So, it is not necessary to retrieve a MAC value for custompowerscriptargument with a bash script
as shown in the previous section, and then pass the argument via $3 such as done in the command
“ wakeonlan $3 ”. Instead, custompowerscript can simply call “ wakeonlan $CMD_MAC ” directly in the
script when run as a power operation command from within CMDaemon.


**4.2 Power Operations** **215**


**4.1.5** **Hewlett Packard iLO-Based Power Control**

**iLO Configuration During Installation**
If “ Hewlett Packard ” is chosen as the node manufacturer during installation (section 3.3.11 of the _In-_
_stallation Manual_ ), and the nodes have an iLO management interface, then Hewlett-Packard’s iLO management package, hponcfg, is installed by default on the nodes and head nodes.


**iLO Configuration After Installation**
If “ Hewlett Packard ” has not been specified as the node manufacturer during installation then it can
be configured after installation as follows:
The hponcfg rpm package is normally obtained and upgraded for specific HP hardware from the
HP website. Using an example of hponcfg-3.1.1-0.noarch.rpm as the package downloaded from the
HP website, and to be installed, the installation can then be done on the head node, the software image,
and in the node-installer as follows:


rpm -iv hponcfg-3.1.1-0.noarch.rpm
rpm --root /cm/images/default-image -iv hponcfg-3.1.1-0.noarch.rpm
rpm --root /cm/node-installer -iv hponcfg-3.1.1-0.noarch.rpm


To use iLO on a node, the iLO interface of the node is set up just like the IPMI interfaces as outlined
in section 4.1.2. That is, using “ set powercontrol ilo0 ” instead of “ set powercontrol ipmi0 ”. BCM
treats HP iLO interfaces just like regular IPMI interfaces, except that the interface names are ilo0, ilo1 ...
instead of ipmi0, ipmi1 ...
For example, nodes in the default category can be brought under iLO power control as follows:


**Example**


[mycluster]% device foreach -c default (set powercontrol ilo0)

[mycluster]% device commit


**4.1.6** **Dell** drac **-based Power Control**

Dell drac configuration is covered on page 127.


**4.1.7** **Redfish-Based and CIMC-Based Power Control**
Section 3.7 describes setting up networking and authentication for Redfish/CIMC, as well as for
IPMI/iLO/DRAC interfaces.


**4.2** **Power Operations**


**4.2.1** **Power Operations Overview**

**Main Power Operations**
Power operations may be carried out on devices from either Base View or cmsh . There are four main
power operations:


  - Power On: power on a device


  - Power Off: power off a device


  - Power Reset: power off a device and power it on again after a brief delay


  - Power Status: check power status of a device


**216** **Power Management**


**Scheduling-related Power Operations**
There are also _scheduling-related_ power operations, which are currently (December 2018) only accessible
via cmsh . Scheduling-related power operations are power operations associated with managing and
viewing explicitly-scheduled execution.
Scheduled execution of power operations can be carried out explicitly via the --at, --after, -d,
and --parallel-delay options. The scheduling-related power operations to manage and view such
scheduled power operations are:


 - power wait : Identifies the devices that have power operations that are in the waiting state, i.e.
waiting to be carried out, and also outputs the number of operations that are waiting to be carried

out.


 - power cancel : Cancels an operation in the waiting state. The devices on which they should be
cancelled can be specified.


 - power list : Lists the power operations on the device and the states of the operations. Possible
states for operations are:


**–**
waiting : waiting to be executed


**–**
busy : are being executed


**–** canceled : have been canceled


**–** done : have been executed


It is possible that power operations without an explicitly-scheduled execution time setting show up very
briefly in the output of power list and power wait . However, the output displayed is almost always
about the explicitly-scheduled power operations.


**4.2.2** **Power Operations With Base View**
In Base View, executing the main power operations can be carried out as follows:


  - via the menu dropdown for a node. For example:


**–** for the head node, via the navigation path Devices    - Head Nodes    - Power


**–** for a regular node via the navigation path Devices    - Nodes    - Power


  - via the menu dropdown for a category or group. For example, for the default category, via the
navigation path Grouping   - Categories   - Power


  - via the Actions button. The Actions button is available when specific device has been selected.
For example, for the head node basecm11 the Actions button can be seen via the navigation path
Devices   - Head Nodes[basecm11]   - _checkbox_ .


Clicking on the Actions button then makes power operation buttons available (figure 4.2).


**4.2 Power Operations** **217**


Figure 4.2: Actions button, accessing the power operations


**4.2.3** **Power Operations Through** cmsh
Power operations on nodes can be carried out from within the device mode of cmsh, via the power
command options.


**Powering On**
Powering on can be carried out on a list of nodes (page 67). Powering on node001, and nodes from
node018 to node033 (output truncated):


**Example**


[mycluster]% device power -n node001,node018..node033 on
apc01:1 ............. [ ON ] node001
apc02:8 ............. [ ON ] node018
apc02:9 ............. [ ON ] node019

...


When a power operation is carried out on multiple devices, CMDaemon ensures that a 1 second delay
occurs by default between successive devices. This helps avoid power surges on the infrastructure.


**Delay Period Between Nodes**
The delay period can be modified from within the device mode of cmsh, by using the -d|--delay option
of the power command. For example, the preceding power command can be run with a shorter, 10ms
delay with:


[mycluster]% device power -n node001,node018..node033 -d 0.01 on


A 0-second delay ( -d 0 ) should not be set for larger number of nodes, unless the power surge that
this would cause has been taken into consideration.


**218** **Power Management**


**Powering Up In Batches**
Groups of nodes can be powered up “in batches”, according to power surge considerations. For example, to power up 3 racks at a time (“in batches of 3”), the -p|--parallel option is used:


**Example**


[mycluster]% device power on -p 3 rack[01-12]


By default, there is a delay of 20s between batch commands. So, in the preceding example, there is
a 20s pause before the each batch of the next three racks is powered up. For batch operation a delay of
-d 0 is assumed, i.e. the nodes within in the rack are powered up without a built-in delay between the
nodes of the rack.


**Thread Use During Powering Up**
The default number of threads that are started up to handle powering up of all the nodes is 32. If the
hardware can cope with it, then it is possible to decrease startup time by increasing the default number of
threads used to handle powerup, by editing the PowerThreadPoolSize advanced configuration directive
in CMDaemon (page 856).


**Powering Off Nodes**
An example of powering off nodes is the following, where all nodes in the default category are powered
off, with a 100ms delay between nodes (some output elided):


**Example**


[mycluster]% device power off -c default -d 0.1
apc01:1 ............. [ OFF ] node001
apc01:2 ............. [ OFF ] node002

...

apc23:8 ............. [ OFF ] node953


**Getting The Power Status**
The power status command lists the status for devices:


**Example**


[mycluster]% device power status -g mygroup
apc01:3 ............. [ ON ] node003
apc01:4 ............. [ OFF ] node004


**Getting The Power History**
The power history command lists the last few power operations on nodes. By default it lists up to the
last 8.


**Example**


[mycluster]% device power history

Device Time Operation Success

-------- ------------------------ ------------ -----------
node001 Sat Sep 14 03:35:03 2019 shutdown yes

node001 Fri Sep 20 14:28:38 2019 on yes

node002 Sat Sep 14 03:35:03 2019 shutdown yes

node002 Fri Sep 20 14:28:38 2019 on yes

node003 Sat Sep 14 03:35:03 2019 shutdown yes

node003 Fri Sep 20 14:28:38 2019 on yes

node004 Sat Sep 14 03:35:03 2019 shutdown yes


**4.2 Power Operations** **219**


**The** power **Command Help Text**
The help text for the power command is:


[basecm11->device]% help power

Name:

power - Manipulate or retrieve power state of devices


Usage:


power [OPTIONS] status
power [OPTIONS] on
power [OPTIONS] off
power [OPTIONS] reset
power [OPTIONS] list
power [OPTIONS] history
power [OPTIONS] cancel
power [OPTIONS] wait <index>


Options:

-n, --nodes <node>

List of nodes, e.g. node001..node015,node020..node028,node030 or
^/some/file/containing/hostnames


-g, --group <group>

Include all nodes that belong to the node group, e.g. testnodes or test01,test03


-c, --category <category>

Include all nodes that belong to the category, e.g. default or default,gpu


-r, --rack <rack>

Include all nodes that are located in the given rack, e.g rack01 or

rack01..rack04


-h, --chassis <chassis>

Include all nodes that are located in the given chassis, e.g chassis01 or

chassis03..chassis05


-e, --overlay <overlay>

Include all nodes that are part of the given overlay, e.g overlay1 or

overlayA,overlayC


-m, --image <image>

Include all nodes that have the given image, e.g default-image or

default-image,gpu-image


-t, --type <type>

Type of devices, e.g node or virtualnode,cloudnode


-i, --intersection

Calculate the intersection of the above selections


-u, --union

Calculate the union of the above selections


-l, --role role

Filter all nodes that have the given role


**220** **Power Management**


-s, --status <status>

Only run command on nodes with specified status, e.g. UP, "CLOSED|DOWN",

"INST.*"


-b, --background

Run in background, output will come as events


-d, --delay <seconds>

Wait <seconds> between executing two sequential power commands. This option is

ignored for the status command


-f, --force

Force power command on devices which have been closed


-w, --overview

Group all power operation results into an overview


-p, --parallel <number>
Number of parallel option-items to be used per batch, default 0 (disabled)


--at <time>

Execute the operation at the provided time


--after <seconds>

Wait <seconds> before executing the operation


--parallel-delay <seconds>

Wait <seconds> between executing the next batch of parallel commands, default

20s


--parallel-dry-run

Only display the times at which operations will be executed, do not perform

any power operations


--retry-count <number>
Number of times to retry operation if it failed the first time (default 0)


--retry-delay <seconds>
Delay between consecutive tries of a failed power operation (default 3s)


--port <pdu>:<port>

Do the power operation directly on a pdu port.


Examples:

power status Display power status for all devices or current device

power on node001 Power on node001
power on -n node00[1-2] Power on node001 and node002

power list List all pending power operations

power history List the last couple of power operations

power wait List all power operation that can be waited for

power wait 1 Wait for a power operation to be completed

power wait all Wait for all power operations to be completed

power wait last Wait for the last given power operation to be completed

power off --after 10m Power off the current node after 10 minutes


**4.3 Monitoring Power** **221**


power off --at 23:55 Power off the current node today just before midnight

power cancel node001 Cancel all pending power operations for node001
power on -p 4 rack[01-80] Power on racks 1 to 80 in batches of 4. With a delay of 20s

between each batch. And a delay of 0s between nodes.

power on --port pdu1:1 Power on port 1 on pdu1
power on --port pdu1:[1-4] Power on port 1 through 4 on pdu1


**4.3** **Monitoring Power**


Monitoring power consumption is important since electrical power is an important component of the
total cost of ownership for a cluster. The monitoring system of BCM collects power-related data from
PDUs in the following metrics:


 - PDUBankLoad : Phase load (in amperes) for one (specified) bank in a PDU


 - PDULoad : Total phase load (in amperes) for one PDU


Chapter 10 on cluster monitoring has more on metrics and how they can be visualized.


**4.4** **Switch Configuration To Survive Power Downs**


Besides the nodes and the BMC interfaces being configured for power control, it may be necessary to
check that switches can handle power on and off network operations properly. Interfaces typically negotiate the link speed down to reduce power while still supporting Wake On Lan and other features.
During such renegotiations the switch may lose connectivity to the node or BMC interface. This can happen if dynamic speed negotiation is disabled on the switch. Dynamic speed negotiation should therefore
be configured to be on on the switch in order to reduce the chance that a node does not provision from
a powered down state.


# **5**

### **Node Provisioning**

This chapter covers _node provisioning_ . Node provisioning is the process of how nodes obtain an image.
Typically, this happens during their stages of progress from power-up to becoming active in a cluster,
but node provisioning can also take place when updating a running node.
Section 5.1 describes the stages leading up to the loading of the kernel onto the node.
Section 5.2 covers configuration and behavior of the provisioning nodes that supply the software
images.
Section 5.3 describes the configuration and loading of the kernel, the ramdisk, and kernel modules.
Section 5.4 elaborates on how the node-installer identifies and places the software image on the node
in a 13-step process.
Section 5.5 explains node states during normal boot, as well node states that indicate boot problems.
Section 5.6 describes how running nodes can be updated, and modifications that can be done to the
update process.
Section 5.7 explains how to add new nodes to a cluster so that node provisioning will work for these
new nodes too. The Base View and cmsh front ends for creating new node objects and properties in
CMDaemon are described.

Section 5.8 describes troubleshooting the node provisioning process.


**5.1** **Before The Kernel Loads**


Immediately after powering up a node, and before it is able to load up the Linux kernel, a node starts
its boot process in several possible ways:


**5.1.1** **PXE Booting**
By default, nodes boot from the network when using BCM. This is called a _network boot_ . On the x86_64
( amd64 ) architecture it is known as a _PXE boot_ (often pronounced as “pixie boot”). It is recommended
as a BIOS setting for nodes. The head node runs a tftpd server that is managed by systemd . The tftpd
server supplies the boot loader from within the default software image (section 2.1.2) offered to nodes.
The boot loader runs on the node and displays a menu (figure 5.1) based on loading a menu module within a configuration file. The default configuration files offered to nodes are located under
/tftpboot/pxelinux.cfg/ on the head node. To implement changes in the files, CMDaemon may need
to be restarted, or the updateprovisioners command (page 233) can be run.
The default configuration files give instructions to the menu module of PXElinux . The instruction set
used is documented at [http://www.syslinux.org/wiki/index.php/Comboot/menu.c32](http://www.syslinux.org/wiki/index.php/Comboot/menu.c32), and includes
the TIMEOUT, LABEL, MENU LABEL, DEFAULT, and MENU DEFAULT instructions.


**The PXE** TIMEOUT **Instruction**

During the display of the PXE boot menu, a selection can be made within a timeout period to boot the
node in a several ways. Among the options are some of the install mode options (section 5.4.4). If no


**224** **Node Provisioning**


Figure 5.1: PXE boot menu options


selection is made by the user within the timeout period, then the AUTO install mode option is chosen by
default.

In the PXE menu configuration files under pxelinux.cfg/, the default timeout of 5 seconds can be
adjusted by changing the value of the “ TIMEOUT 50 ” line. This value is specified in deciseconds.


**Example**


TIMEOUT 300 # changed timeout from 50 (=5 seconds)


**The PXE** LABEL **And** MENU LABEL **Instructions**

**LABEL** **:** The menu configuration files under pxelinux.cfg/ contain several multiline LABEL state
ments.

Each LABEL statement is associated with a kernel image that can be loaded from the PXE boot menu
along with appropriate kernel options.
Each LABEL statement also has a text immediately following the LABEL tag. Typically the text is a
description, such as linux, main, RESCUE, and so on. If the PXE menu module is not used, then tab completion prompting displays the list of possible text values at the PXE boot prompt so that the associated
kernel image and options can be chosen by user intervention.


**MENU LABEL** **:** By default, the PXE menu module is used, and by default, each LABEL statement also
contains a MENU LABEL instruction. Each MENU LABEL instruction also has a text immediately following
the MENU LABEL tag. Typically the text is a description, such as AUTO, RESCUE and so on (figure 5.1). Using
the PXE menu module means that the list of the MENU LABEL text values is displayed when the PXE boot
menu is displayed, so that the associated kernel image and options can conveniently be selected by user
intervention.


**The PXE** DEFAULT **And** MENU DEFAULT **Instructions**

**DEFAULT** **:** If the PXE menu module is not used and if no MENU instructions are used, and if there is
no user intervention, then setting the same text that follows a LABEL tag immediately after the DEFAULT
instruction, results in the associated kernel image and its options being run by default after the timeout.
By default, as already explained, the PXE menu module is used. In particular it uses the setting:
DEFAULT menu.c32 to enable the menu.


**MENU DEFAULT** **:** If the PXE menu module is used and if MENU instructions are used, and if there is no
user intervention, then setting a MENU DEFAULT tag as a line within the multiline LABEL statement results
in the kernel image and options associated with that LABEL statement being loaded by default after the
timeout.


**5.1 Before The Kernel Loads** **225**


**The CMDaemon** PXE Label **Setting For Specific Nodes**
The MENU DEFAULT value by default applies to every node using the software image that the PXE menu
configuration file under pxelinux.cfg/ is loaded from. To override its application on a per-node basis,
the value of PXE Label can be set for each node.


  - Some simple examples of overriding the default MENU DEFAULT value are as follows:


**–** For example, using cmsh :


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% set pxelabel MEMTEST ; commit


Carrying it out for all nodes in the default category can be done, for example, with:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% foreach -c default (set pxelabel MEMTEST)

[basecm11->device*]% commit


The value of pxelabel can be cleared with:


**Example**


[root@basecm11 ~]# cmsh -c "device; foreach -c default (clear pxelabel); commit"


**–** In Base View, the PXE label can be set for a node node001 using the navigation path


Devices     - Nodes     - Physical Node list[node001]     - Settings[Physical Node node001]     Provisioning[PXE Label]


which leads to a screen as in (figure 5.2):


Figure 5.2: Base View PXE Label option


**226** **Node Provisioning**


  - A more complicated example of overriding the default MENU DEFAULT value now follows. Although it helps in understanding how PXE labels can be used, it can normally be skipped because
the use case for it is unlikely, and the details are involved.


In this example, pxelabel is set by the administrator via Base View or cmsh to localdrive . This
will then set the node to boot from the first local drive and not the node-installer. This is a setting
that is discouraged since it usually makes node management harder, but it can be used by administrators who do not wish to answer any prompt during node boot, and also want the node drives
to have no risk of being overwritten by the actions of the node-installer, and also want the system
to be up and running quite fully, even if not necessarily provisioned with the latest image from the
head node.


Here, the overwriting-avoidance method relies on the nodes being associated with a configuration
file under pxelinux.cfg at the time that the localdrive setting is done. However, nodes that are
unidentified, or are identified later on, will have their MENU DEFAULT value still set to a default
pxelabel value set in the files under /tftpboot/pxelinux.cfg/, which is the value linux by
default, and which is associated with a code block in that file with the label LABEL linux . To make
such (as yet) unidentified nodes boot to a localdrive setting instead, requires modifying the files
under /tftpboot/pxelinux.cfg/, so that the MENU DEFAULT line is associated with the code block
of LABEL localdrive rather than the code block of LABEL linux .


There are two methods other than using the preceding pxelabel method to deal with the risk of
overwriting. Unlike the pxelabel method however, these methods can interrupt node booting, so
that the node does not progress to being fully up until the administrator takes further action:


1. If it is acceptable that the administrator manually enters a confirmation as part of the boot
process when a possible overwrite risk is found, then the datanode method (section 5.4.4)
can be used.


2. If it is acceptable that the boot process halts on detecting a possible overwrite risk, then the
XML assertions method (Appendix D.11) is recommended.


**Changing The Install Mode Or Default Image Offered To Nodes**
The selections offered by the PXE menu are pre-configured by default so that the AUTO menu option by
default loads a kernel, runs the AUTO install mode, and eventually the default-image software image is
provisioned.
Normally administrators should not be changing the install mode, kernel, or kernel options in the
PXE menu configuration files under pxelinux.cfg/ .
More on changing the install mode is given in section 5.4.4. More on changing software images,
image package management, kernels, and kernel options, is to be found in Chapter 9.


**5.1.2** **iPXE Booting From A Disk Drive**
Also by default, on disked nodes, iPXE software is placed on the drive during node installation. If the
boot instructions from the BIOS for PXE booting fail, and if the BIOS instructions are that a boot attempt
should then be made from the hard drive, it means that a PXE network boot attempt is done again, as
instructed by the bootable hard drive. This can be a useful fallback option that works around certain
BIOS features or problems.


**5.1.3** **iPXE Booting Using InfiniBand**
On clusters that have InfiniBand hardware, it is normally used for data transfer as a service after the
nodes have fully booted up (section 3.6). InfiniBand can also be used for PXE booting (described here)
and used for node provisioning (section 5.3.3). However these uses are not necessary, even if InfiniBand
is used for data transfer as a service later on, because booting and provisioning is available over Ethernet by default. This section (about boot over InfiniBand) may therefore safely be skipped when first
configuring a cluster.


**5.1 Before The Kernel Loads** **227**


Booting over InfiniBand via PXE is enabled by carrying out these 3 steps:


1. Making BCM aware that nodes are to be booted over InfiniBand. Node booting (section 3.2.3,
page 104) can be set from cmsh or Base View as follows:


(a) From cmsh ’s network mode: If the InfiniBand network name is ibnet, then a cmsh command
that will set it is:

cmsh -c "network; set ibnet nodebooting yes; commit"


(b) From Base View: The Settings window for the InfiniBand network, for example ibnet,
can be accessed from the Networking resource via the navigation path Networking     Networks[ibnet]     - Edit     - Settings (this is similar to figure 3.5, but for ibnet ). The Node
booting option for ibnet is then enabled and saved.


If the InfiniBand network does not yet exist, then it must be created (section 3.2.2). The recommended default values used are described in section 3.6.3. The MAC address of the interface in

CMDaemon defaults to using the GUID of the interface.


The administrator should also be aware that the interface from which a node boots, (conveniently
labeled BOOTIF ), must not be an interface that is already configured for that node in CMDaemon.
For example, if BOOTIF is the device ib0, then ib0 must not already be configured in CMDaemon.
Either BOOTIF or the ib0 configuration should be changed so that node installation can succeed. It
is recommended to set BOOTIF to eth0 if the ib0 device should exist.


2. Flashing iPXE onto the InfiniBand HCAs. (The ROM image is obtained from the HCA vendor).


3. Configuring the BIOS of the nodes to boot from the InfiniBand HCA.


All MAC addresses become invalid for identification purposes when changing from booting over
Ethernet to booting over InfiniBand.
Administrators who enable iPXE booting almost always wish to provision over InfiniBand too. Configuring provisioning over InfiniBand is described in section 5.3.3.


**5.1.4** **Using PXE To Boot From The Drive**
Besides PXE booting from only the network, a node can also be configured via PXE to step over to using
its own drive to start booting and get to the stage of loading up its kernel entirely from its drive, just like
a normal standalone machine. This can be done by setting PXE LABEL to localdrive (page 223).


**5.1.5** **Network Booting Without PXE On The ARMv8 Architecture**
ARMv8 nodes use a network boot implementation that differs slightly from the x86 PXE boot implementation. The actual firmware that starts up on ARMv8 nodes depends on the environment the hardware
is in. Networking is then started by the firmware and the network requests what to boot. The head node
however then sends out a GRUB binary instead of an iPXE binary. The GRUB binary then runs on the
regular node, and fetches the kernel and initrd via TFTP. The node-installer then runs on the nodes and
follows the same steps as in the x86 process.


**5.1.6** **Network Booting Protocol**
The protocol used by network booting is set with the parameter bootloaderprotocol . It is set to HTTP
by default at category level:


**Example**


[basecm11->category[mydefaultimage]]% get bootloaderprotocol

HTTP


The protocol can be modified at category or node level, to one of the values HTTP, HTTPS, or TFTP :


**228** **Node Provisioning**


**Example**


[basecm11->device[node001]]% get bootloaderprotocol
HTTP (mydefaultimage)

[basecm11->device[node001]]% set bootloaderprotocol _<TAB><TAB>_

http https tftp

[basecm11->device[node001]]% set bootloaderprotocol tftp

[basecm11->device*[node001*]]% commit

[basecm11->device[node001]]% get bootloaderprotocol

TFTP


If the protocol has the setting of HTTP, then initial PXE booting actually still uses the TFTP protocol
on x86_64 hardware. However, a switchover to the HTTP protocol is done when loading up the kernel
and RAM disk.

The HTTPS protocol for node booting should almost never be used, because it is rarely implemented
in hardware.


**5.1.7** **The Boot Role**

The action of providing a boot image to a node via DHCP and TFTP is known as providing _node booting_ .
Node provisioning (section 5.2), on the other hand, is about provisioning the node with the rest of the
node image.
Roles in general are introduced in section 2.1.5. The _boot role_ is one such role that can be assigned to
a regular node. The boot role configures a regular node so that it can then provide node booting. The
role cannot be assigned or removed from the head node—the head node always has a boot role.
The boot role is assigned by administrators to regular nodes if there is a need to cope with the
scaling limitations of TFTP and DHCP. TFTP and DHCP services can be overwhelmed when there are
large numbers of nodes making use of them during boot. An example of the scaling limitations may be
observed, for example, when, during the powering up and network booting attempts of a large number
of regular nodes from the head node, it turns out that random different regular nodes are unable to boot,
typically due to network effects.
One implementation of boot role assignment might therefore be, for example, to have a several
groups of racks, with each rack in a subnet, and with one regular node in each subnet that is assigned
the boot role. The boot role regular nodes would thus take the DHCP and TFTP load off the head node
and onto themselves for all the nodes in their associated subnet, so that all nodes of the cluster are then
able to boot without networking issues.


**5.2** **Provisioning Nodes**


The action of transferring the software image to the nodes is called _node provisioning_, and is done by
special nodes called the _provisioning nodes_ . More complex clusters can have several provisioning nodes
configured by the administrator, thereby distributing network traffic loads when many nodes are booting.
Creating provisioning nodes is done by assigning a _provisioning role_ to a node or category of nodes.
Similar to how the head node always has a boot role (section 5.1.7), the head node also always has a
provisioning role.


**5.2.1** **Provisioning Nodes: Configuration Settings**
The provisioning role has several parameters that can be set:


**5.2 Provisioning Nodes** **229**


**Property** **Description**


allImages The following values decide what images the provisioning node
provides:


            - onlocaldisk (the default): all images on the local disk, regardless of any other parameters set


            - onlocaldiskexceptsharedimages : all images on the local
disk, except for shared images


            - onsharedstorage : all images on the shared storage, regardless
of any other parameters set


            - no : only images listed in the localimages or sharedimages
parameters, described next


localimages A list of software images on the local disk that the provisioning node
accesses and provides. The list is used only if allImages is “ no ”.


sharedimages A list of software images on the shared storage that the provisioning
node accesses and provides. The list is used only if allImages is
“ no ”


Provisioning slots The maximum number of nodes that can be provisioned in parallel
by the provisioning node. The optimum number depends on the infrastructure. The default value is 10, which is safe for typical cluster
setups. Setting it lower may sometimes be needed to prevent network and disk overload.


nodegroups A list of node groups (section 2.1.4). If set, the provisioning node
only provisions nodes in the listed groups. Conversely, nodes in one
of these groups can only be provisioned by provisioning nodes that
have that group set. Nodes without a group, or nodes in a group not
listed in nodegroups, can only be provisioned by provisioning nodes
that have no nodegroups values set. By default, the nodegroups list
is unset in the provisioning nodes.
The nodegroups setting is typically used to set up a convenient hierarchy of provisioning, for example based on grouping by rack and
by groups of racks.


A provisioning node keeps a copy of all the images it provisions on its local drive, in the same
directory as where the head node keeps such images. The local drive of a provisioning node must
therefore have enough space available for these images, which may require changes in its disk layout.


**5.2.2** **Provisioning Nodes: Role Setup With** cmsh
In the following cmsh example the administrator creates a new category called misc . The default category default already exists in a newly installed cluster.
The administrator then assigns the role called provisioning, from the list of available assignable
roles, to nodes in the misc category. After the assign command has been typed in, but before entering
the command, tab-completion prompting can be used to list all the possible roles. Assignment creates
an association between the role and the category. When the assign command runs, the shell drops into
the level representing the provisioning role.
If the role called provisioning were already assigned, then the use provisioning command would
drop the shell into the provisioning role, without creating the association between the role and the
category.


**230** **Node Provisioning**


As an aside from the topic of provisioning, from an organizational perspective, other assignable roles
include monitoring, storage, and failover .
Once the shell is within the role level, the role properties can be edited conveniently.
For example, the nodes in the misc category assigned the provisioning role can have
default-image set as the image that they provision to other nodes, and have 20 set as the maximum
number of other nodes to be provisioned simultaneously (some text is elided in the following example):


**Example**


[basecm11]% category add misc

[basecm11->category*[misc*]]% roles

[basecm11->category*[misc*]->roles]% assign provisioning

[basecm11...*]->roles*[provisioning*]]% set allimages no

[basecm11...*]->roles*[provisioning*]]% set localimages default-image

[basecm11...*]->roles*[provisioning*]]% set provisioningslots 20

[basecm11...*]->roles*[provisioning*]]% show

Parameter Value

--------------------------------- --------------------------------
All Images no

Include revisions of local images yes

Local images default-image

Name provisioning

Nodegroups

Provisioning associations <0 internally used>

Revision

Shared images

Type ProvisioningRole

Provisioning slots 20

[basecm11->category*[misc*]->roles*[provisioning*]]% commit

[basecm11->category[misc]->roles[provisioning]]%


Assigning a provisioning role can also be done for an individual node instead, if using a category
is deemed overkill:


**Example**


[basecm11]% device use node001

[basecm11->device[node001]]% roles

[basecm11->device[node001]->roles]% assign provisioning

[basecm11->device*[node001*]->roles*[provisioning*]]%

...


A role change configures a provisioning node, but does not directly update the provisioning node
with images. After carrying out a role change, BCM runs the updateprovisioners command described
in section 5.2.4 automatically, so that regular images are propagated to the provisioners. The propagation can be done by provisioners themselves if they have up-to-date images. CMDaemon tracks the
provisioning nodes role changes, as well as which provisioning nodes have up-to-date images available,
so that provisioning node configurations and regular node images propagate efficiently. Thus, for example, image update requests by provisioning nodes take priority over provisioning update requests
from regular nodes.


**5.2.3** **Provisioning Nodes: Role Setup With Base View**
The provisioning configuration outlined in cmsh mode in section 5.2.2 can be done via Base View too, as
follows:


**5.2 Provisioning Nodes** **231**


A misc category can be added via the navigation path
Grouping - Categories - Add - Settings - < _name_ Within the Settings tab, the node category should be given a name misc (figure 5.3), and saved:


Figure 5.3: Base View: Adding A misc Category


The Roles window can then be opened from within the JUMP TO section of the settings pane. To
add a role, the Add button in the Roles window is clicked. A scrollable list of available roles is then
displayed, (figure 5.4):


Figure 5.4: Base View: Setting A provisioning Role


After selecting a role, then navigating via the Back buttons to the Settings menu of figure 5.3, the
role can be saved using the Save button there.


**232** **Node Provisioning**


The role has properties which can be edited (figure 5.5):


Figure 5.5: Base View: Configuring A provisioning Role


For example:


  - the Provisioning slots setting decides how many images can be supplied simultaneously from
the provisioning node


  - the All images setting decides if the role provides all images


  - the Local images setting decides what images the provisioning node supplies from local storage


  - the Shared images setting decides what images the provisioning node supplies shared storage.


The settings can be saved with the Save button of figure 5.5.
The images offered by the provisioning role should not be confused with the software image setting
of the misc category itself, which is the image the provisioning node requests for itself from the category.


**5.2.4** **Provisioning Nodes: Housekeeping**
The head node does housekeeping tasks for the entire provisioning system. Provisioning is done on
request for all non-head nodes on a first-come, first-serve basis. Since provisioning nodes themselves,
too, need to be provisioned, it means that to cold boot an entire cluster up quickest, the head node
should be booted and be up first, followed by provisioning nodes, and finally by all other non-head
nodes. Following this start-up sequence ensures that all provisioning services are available when the
other non-head nodes are started up.
Some aspects of provisioning housekeeping are discussed next:


**Provisioning Node Selection**
When a node requests provisioning, the head node allocates the task to a provisioning node. If there
are several provisioning nodes that can provide the image required, then the task is allocated to the
provisioning node with the lowest number of already-started provisioning tasks.


**Limiting Provisioning Tasks With** MaxNumberOfProvisioningThreads
Besides limiting how much simultaneous provisioning per provisioning node is allowed with
Provisioning Slots (section 5.2.1), the head node also limits how many simultaneous provisioning


**5.2 Provisioning Nodes** **233**


tasks are allowed to run on the entire cluster. This is set using the MaxNumberOfProvisioningThreads
directive in the head node’s CMDaemon configuration file, /etc/cmd.conf, as described in Appendix C.


**Provisioning Tasks Deferral and Failure**
A provisioning request is _deferred_ if the head node is not able to immediately allocate a provisioning
node for the task. Whenever an ongoing provisioning task has finished, the head node tries to re-allocate
deferred requests.
A provisioning request _fails_ if an image is not transferred. 5 retry attempts at provisioning the image
are made in case a provisioning request fails.
A provisioning node that is carrying out requests, and which loses connectivity, has its provisioning
requests remain allocated to it for 180 seconds from the time that connectivity was lost. After this time
the provisioning requests fail.


**Provisioning Role Change Notification With** updateprovisioners
The updateprovisioners command can be accessed from the softwareimage mode in cmsh . It can also
be accessed from Base View, via the navigation path Provisioning - Provisioning requests - Update
provisioning nodes .
In the examples in section 5.2.2, changes were made to provisioning role attributes for an individual
node as well as for a category of nodes. This automatically ran the updateprovisioners command.
The updateprovisioners command runs automatically if CMDaemon is involved during software
image changes or during a provisioning request. If on the other hand, the software image is changed
outside of the CMDaemon front ends (Base View and cmsh ), for example by an administrator adding a
file by copying it into place from the bash prompt, then updateprovisioners should be run manually
to update the provisioners.
In any case, if it is not run manually, then by default it runs every midnight (UTC). The scheduling
period can be adjusted with the autoupdateperiod setting:


**Example**


[root@basecm11 ]# cmsh

[basecm11]% partition use base

[basecm11->partition[base]]% provisioningsettings

[basecm11->partition[base]->provisioningsettings]% get autoupdateperiod

[basecm11->partition[base]->provisioningsettings]% 86400

[basecm11->partition[base]->provisioningsettings]% # is UTC epoch start time modulo 24 hours

[basecm11->partition[base]->provisioningsettings]% # set UTC epoch start time modulo 18 hours:

[basecm11->partition[base]->provisioningsettings]% set autoupdateperiod 64800

[basecm11->partition*[base*]->provisioningsettings*]% commit


When the default updateprovisioners is invoked manually, the provisioning system waits for all
running provisioning tasks to end, and then updates all images located on any provisioning nodes by
using the images on the head node. It also re-initializes its internal state with the updated provisioning
role properties, i.e. keeps track of what nodes are provisioning nodes.
The default updateprovisioners command, run with no options, updates all images. If run from
cmsh with a specified image as an option, then the command only does the updates for that particular
image. A provisioning node undergoing an image update does not provision other nodes until the
update is completed.


**Example**


[basecm11]% softwareimage updateprovisioners

Provisioning nodes will be updated in the background.


Sun Dec 12 13:45:09 2010 basecm11: Starting update of software image(s) _\_


**234** **Node Provisioning**


provisioning node(s). (user initiated).

[basecm11]% softwareimage updateprovisioners [basecm11]%
Sun Dec 12 13:45:41 2010 basecm11: Updating image default-image on prov _\_

isioning node node001.

[basecm11]%
Sun Dec 12 13:46:00 2010 basecm11: Updating image default-image on prov _\_

isioning node node001 completed.

Sun Dec 12 13:46:00 2010 basecm11: Provisioning node node001 was updated
Sun Dec 12 13:46:00 2010 basecm11: Finished updating software image(s) _\_
on provisioning node(s).


**Provisioning Role Draining And Undraining Nodes With** drain **,** undrain
The drain and undrain commands to control provisioning nodes are accessible from within the
softwareimage mode of cmsh .
If a node is put into a drain state, then all currently active provisioning requests continue until they
are completed. However, the node is not assigned any further pending requests, until the node is put
back into an undrain state.


**Example**


[basecm11->softwareimage]% drain -n master

Nodes drained

[basecm11->softwareimage]% provisioningstatus

Provisioning subsystem status

Pending request: node001, node002

Provisioning node status:

+ basecm11

Slots: 1 / 10

State: draining

Active nodes: node003

Up to date images: default-image

[basecm11->softwareimage]% provisioningstatus

Provisioning subsystem status

Pending request: node001, node002

Provisioning node status:

+ basecm11

Slots: 0 / 10

State: drained

Active nodes: none

Up to date images: default-image


To drain all nodes at once, the --role option can be used, with provisioning role as its value. All
pending requests then remain in the queue, until the nodes are undrained again.


**Example**


[basecm11->softwareimage]% drain --role provisioning
... _Time passes. Pending_
_requests stay in the queue. Then_
_admin undrains it..._

[basecm11->softwareimage]% undrain --role provisioning


**Provisioning Node Update Safeguards And** dirtyautoupdatetimeout
The updateprovisioners command is subject to safeguards that prevent it running too frequently.
The minimum period between provisioning updates can be adjusted with a timeout parameter
dirtyautoupdatetimeout, which has a default value of 300s.


**5.2 Provisioning Nodes** **235**


Exceeding the timeout does not by itself trigger an update to the provisioning node.
When the head node receives a provisioning request, it checks if the last update of the provisioning
nodes is more than the timeout period. If true, then an update is triggered to the provisioning node. The
update is disabled if the dirtyautoupdatetimeout is set to zero ( false ).
The parameter can be accessed and set within cmsh from partition mode:


**Example**


[root@basecm11 ]# cmsh

[basecm11]% partition use base

[basecm11->partition[base]]% provisioningsettings

[basecm11->partition[base]->provisioningsettings]% get dirtyautoupdatetimeout

[basecm11->partition[base]->provisioningsettings]% 300

[basecm11->partition[base]->provisioningsettings]% set dirtyautoupdatetimeout 0

[basecm11->partition*[base*]->provisioningsettings*]% commit


Within Base View the parameter is accessible via the navigation path:
Cluster - Settings - Provisioning Settings - Dirty auto update timeout .
To prevent provisioning an image to the nodes, it can be locked (section 5.4.7). The provisioning
request is then deferred until the image is once more unlocked.


**Synchronization Of Fspart Subdirectories To Provisioning Nodes**
In BCM, an _fspart_ is a subdirectory, and it is a filesystem part that can be synced during provisioning.
The fsparts can be listed with:


**Example**


[root@basecm11 ]# cmsh

[basecm11]% fspart

[basecm11->fspart]% list
Path (key) Type Image

------------------------------ --------------- -----------------------
/cm/images/default-image image default-image
/cm/images/default-image/boot boot default-image:boot

/cm/node-installer node-installer

/cm/shared cm-shared

/tftpboot tftpboot
/var/spool/cmd/monitoring monitoring


The updateprovisioners command (page 233) is used to update image fsparts to all nodes with a
provisioning role.


**The** trigger **command:** is used to update non-image fsparts to off-premises nodes, such as cloud
directors and edge directors. The directors have a provisioning role for the nodes that they direct.
All of the non-image types can be updated with the --all option:


**Example**


[basecm11->fspart]% trigger --all


The command help trigger in fspart mode gives further details.


**236** **Node Provisioning**


**The** info **command:** shows the architecture, OS, and the number of inotify watchers that track rsyncs
in the fspart subdirectory.


[basecm11->fspart]% info

Path Architecture OS Inotify watchers

------------------------------ ---------------- ---------------- ---------------
/cm/images/default-image x86_64 rhel9 0
/cm/images/default-image/boot - - 0

/cm/node-installer x86_64 rhel9 0

/cm/shared x86_64 rhel9 0

/tftpboot - - 0
/var/spool/cmd/monitoring - - 0


[basecm11->fspart]% info -s _(!#with size, takes longer)_

Path Architecture OS Inotify watchers Size

------------------------------ ---------------- ---------------- ---------------- ---------------
/cm/images/default-image x86_64 rhel9 0 4.8 GiB
/cm/images/default-image/boot - - 0 313 MiB

/cm/node-installer x86_64 rhel9 0 2.84 GiB

/cm/shared x86_64 rhel9 0 1.16 GiB

/tftpboot - - 0 3.5 MiB
/var/spool/cmd/monitoring - - 0 1.02 GiB


**The** locked **,** lock **, and** unlock **commands:**


  - The locked command lists fsparts that are prevented from syncing.


**Example**


[basecm11->fspart]% locked

No locked fsparts


  - The lock command prevents a specific fspart from syncing.


**Example**


[basecm11->fspart]% lock /var/spool/cmd/monitoring

[basecm11->fspart]% locked
/var/spool/cmd/monitoring


  - The unlock command unlocks a specific locked fspart again.


**Example**


[basecm11->fspart]% unlock /var/spool/cmd/monitoring

[basecm11->fspart]% locked

No locked fsparts


**Access to** excludelistsnippets **:** The properties of excludelistsnippets for a specific fspart can be
accessed from the excludelistsnippets submode:


**Example**


**5.3 The Kernel Image, Ramdisk And Kernel Modules** **237**


[basecm11->fspart]% excludelistsnippets /tftpboot


[basecm11->fspart[/tftpboot]->excludelistsnippets]% list
Name (key) Lines Disabled Mode sync Mode full Mode update Mode grab Mode grab new

------------ ------- ------------ ----------- ----------- -------------- ----------- -------------
Default 2 no yes yes yes no no


[basecm11->fspart[/tftpboot]->excludelistsnippets]% show default

Parameter Value

-------------------------------- ----------------------------------------------------------------
Lines 2

Name Default

Revision

Exclude list # no need for rescue on nodes with a boot role,/rescue,/rescue/*

Disabled no

No new files no

Mode sync yes

Mode full yes

Mode update yes

Mode grab no

Mode grab new no


[basecm11->fspart[/tftpboot]->excludelistsnippets]% get default excludelist