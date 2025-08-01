# nmcli connection add type bond con-name bond0 ifname bond0 bond.options \

"mode=active-backup,miimon=100"


**–** For SLES, YaST can be used as a front-end tool ( YaST    - System    - Network Settings ).


  - For Ubuntu, the interface definitions are in a file, either /etc/network/interfaces, or a file under
/etc/network/interfaces.d/ .


The line to set the value of miimon follows a form such as:


bond-miimon 100


instead of


miimon=100


and can be set manually.


Alternatively, Canonical’s netplan ( [https://netplan.io](https://netplan.io) ) utility can be used to set the network configuration files. The netplan YAML configuration key to set bond-miimon is

[mii-monitor-interval.](https://netplan.io/reference#properties-for-device-type-bonds)


**120** **Configuring The Cluster**


When listing interfaces in cmsh, if an interface is a member of a bond or bridge interface, then the
corresponding bonded or bridge interface name is shown in parentheses after the member interface
name. Section 3.3, on configuring bridge interfaces, shows an example of such a listing from within
cmsh on page 114.
More on bonded interfaces (including a detailed description of bonding options and modes) can be
found at [http://www.kernel.org/doc/Documentation/networking/bonding.txt](http://www.kernel.org/doc/Documentation/networking/bonding.txt) .


**3.6** **Configuring InfiniBand Interfaces**


On clusters with an InfiniBand interconnect, the InfiniBand Host Channel Adapter (HCA) in each node
must be configured before it can be used.
This section describes how to set up the InfiniBand service on the nodes for regular use. Setting up
InfiniBand for booting and provisioning purposes is described in Chapter 5, while setting up InfiniBand
for NFS is described in section 3.13.4.


**3.6.1** **Installing Software Packages**
On a standard NVIDIA Base Command Manager cluster, the OFED (OpenFabrics Enterprise Distribution) packages that are part of the Linux base distribution are used. These packages provide RDMA
implementations allowing high bandwidth/low latency interconnects on OFED hardware. The implementations can be used by InfiniBand hardware.
By default, all relevant OFED packages are installed on the head node and software images. It is
possible to replace the distribution OFED with a non-distribution OFED. The replacement can be for the
entire cluster, or only for certain software images. Administrators may choose to switch to a different
OFED version if the HCAs used are not supported by the distribution OFED version, or to increase
performance by using an OFED version that has been optimized for a particular HCA. Installing a
DOCA Mellanox OFED stack onto BCM is covered in Chapter 10 of the _Installation Manual_ .
If the InfiniBand network is enabled during cluster installation, then the infiniband.conf and
rdma.conf modules in the subdirectory etc/rdma/modules/ are automatically configured for the detected hardware.

The relevant InfiniBand HCA kernel modules are then automatically loaded during the init stage by
systemd. Verifying that InfiniBand is active can be done after the cluster is up and running by running

ibstat :


auser@head:~$ ibstat

CA 'mlx5_0'

CA type: MT4123

Number of ports: 1

Firmware version: 20.31.2006

Hardware version: 0

Node GUID: 0xb8599f0300e4222a

System image GUID: 0xb

Port 1:

State: Active

Physical state: LinkUp

...


**3.6.2** **Subnet Managers**
Every InfiniBand subnet requires at least one subnet manager to be running. The subnet manager takes
care of routing, addressing and initialization on the InfiniBand fabric. Some InfiniBand switches include
subnet managers. However, on large InfiniBand networks or in the absence of a switch-hosted subnet
manager, a subnet manager needs to be started on at least one node inside of the cluster. When multiple
subnet managers are started on the same InfiniBand subnet, one instance will become the active subnet


**3.6 Configuring InfiniBand Interfaces** **121**


manager whereas the other instances will remain in passive mode. It is recommended to run 2 subnet
managers on all InfiniBand subnets to provide redundancy in case of failure.
On a Linux machine that is not running BCM, an administrator sets a subnet manager service [1] to
start at boot-time with a command such as:

systemctl enable opensm.service
However, for clusters managed by BCM, a subnet manager is best set up using CMDaemon. There
are two ways of setting CMDaemon to start up the subnet manager on a node at boot time:


1. by assigning a role.


In cmsh this can be done with:


[root@basecm11 ~]# cmsh -c "device roles <node>; assign subnetmanager; commit"


where <node> is the name of a node on which it will run, for example: basecm11, node001,

node002 ...


In Base View, the subnet manager role is assigned by selecting a head node or regular node from
the Devices resource, and assigning it the “ Subnet manager role ”. The navigation path for this,
for a node node002 for example, is Devices   - Nodesnode002   - Settings   - Roles   - Add[Subnet
manager role] .


2. by setting the service up. Services are covered more generally in section 3.14.


In cmsh this is done with:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device services node001

[basecm11->device[node001]->services]% add opensm

[basecm11->device[node001]->services*[opensm*]]% set autostart yes

[basecm11->device[node001]->services*[opensm*]]% set monitored yes

[basecm11->device[node001]->services*[opensm*]]% commit

[basecm11->device[node001]->services[opensm]]%


In Base View the subnet manager service is configured by selecting a head node or regular node
from the resources tree, and adding the service to it. The navigation path for this, for a node
node002 for example, is: Devices   - Nodesnode002   - Settings   - Services [ _Service_ ].


When the head node in a cluster is equipped with an InfiniBand HCA, it is a good candidate to run
as a subnet manager for smaller clusters.
On large clusters a dedicated node is recommended to run the subnet manager.


**3.6.3** **InfiniBand Network Settings**
Although not strictly necessary, it is recommended that InfiniBand interfaces are assigned an IP address
(i.e. IP over IB). First, a network object in the cluster management infrastructure should be created. The
procedure for adding a network is described in section 3.2.2. The following settings are recommended
as defaults:


1 usually opensm, but opensmd in SLES


**122** **Configuring The Cluster**


**Property** **Value**


Name ibnet


Domain name ib.cluster


Type internal


Base address 10.149.0.0


Netmask bits 16


MTU up to 4k in datagram mode


up to 64k in connected mode


By default, an InfiniBand interface is set to datagram mode, because it scales better than connected
mode. It can be configured to run in connected mode by setting the connectedmode property:


**Example**


[basecm11->device[node001]->interfaces[ib0]]% set connectedmode yes


For nodes that are PXE booting or are getting provisioned over InfiniBand, the mode setting in the
node-installer script has to be changed accordingly.


**Example**


[root@basecm11 ~]# echo datagram > /cm/node-installer/scripts/ipoib_mode


Once the network has been created all nodes must be assigned an InfiniBand interface on this network. The easiest method of doing this is to create the interface for one node device and then to clone
that device several times.

For large clusters, a labor-saving way to do this is using the addinterface command (section 3.7.1)
as follows:


[root@basecm11 ~]# echo "device

addinterface -n node001..node150 physical ib0 ibnet 10.149.0.1

commit" | cmsh -x


When the head node is also equipped with an InfiniBand HCA, it is important that a corresponding
interface is added and configured in the cluster management infrastructure.


**Example**


Assigning an IP address on the InfiniBand network to the head node:


[basecm11->device[basecm11]->interfaces]% add physical ib0

[basecm11->device[basecm11]->interfaces*[ib0*]]% set network ibnet

[basecm11->device[basecm11]->interfaces*[ib0*]]% set ip 10.149.255.254

[basecm11->device[basecm11]->interfaces*[ib0*]]% commit


As with any change to the network setup, the head node needs to be restarted to make the above
change active.


**3.6.4** **Verifying Connectivity**
After all nodes have been restarted, the easiest way to verify connectivity is to use the ping utility


**Example**


Pinging node015 while logged in to node014 through the InfiniBand interconnect:


**3.6 Configuring InfiniBand Interfaces** **123**


[root@node014 ~]# ping node015.ib.cluster
PING node015.ib.cluster (10.149.0.15) 56(84) bytes of data.
64 bytes from node015.ib.cluster (10.149.0.15): icmp_seq=1 ttl=64

time=0.086 ms

...


If the ping utility reports that ping replies are being received, the InfiniBand is operational. The ping
utility is not intended to benchmark high speed interconnects. For this reason it is usually a good idea
to perform more elaborate testing to verify that bandwidth and latency are within the expected range.
The quickest way to stress-test the InfiniBand interconnect is to use the Intel MPI Benchmark (IMB),
which is installed by default in /cm/shared/apps/imb/current . The setup.sh script in this directory
can be used to create a template in a user’s home directory to start a run.


**Example**


Running the Intel MPI Benchmark using openmpi to evaluate performance of the InfiniBand interconnect between node001 and node002 :


[root@basecm11 ~]# su - cmsupport

[cmsupport@basecm11 ~]$ cd /cm/shared/apps/imb/current/

[cmsupport@basecm11 current]$ ./setup.sh

[cmsupport@basecm11 current]$ cd ~/BenchMarks/imb/2017

[cmsupport@basecm11 2017]$ module load openmpi/gcc

[cmsupport@basecm11 2017]$ module initadd openmpi/gcc

[cmsupport@basecm11 2017]$ make -f make_mpi2

[cmsupport@basecm11 2017]$ mpirun -np 2 -machinefile ../nodes IMB-MPI1 PingPong

#--------------------------------------------------
# Benchmarking PingPong

# #processes = 2

#--------------------------------------------------
#bytes #repetitions t[usec] Mbytes/sec

0 1000 0.78 0.00

1 1000 1.08 0.88

2 1000 1.07 1.78

4 1000 1.08 3.53

8 1000 1.08 7.06

16 1000 1.16 13.16

32 1000 1.17 26.15

64 1000 1.17 52.12

128 1000 1.20 101.39

256 1000 1.37 177.62

512 1000 1.69 288.67

1024 1000 2.30 425.34

2048 1000 3.46 564.73

4096 1000 7.37 530.30

8192 1000 11.21 697.20

16384 1000 21.63 722.24

32768 1000 42.19 740.72

65536 640 70.09 891.69

131072 320 125.46 996.35

262144 160 238.04 1050.25

524288 80 500.76 998.48

1048576 40 1065.28 938.72

2097152 20 2033.13 983.71

4194304 10 3887.00 1029.07


**124** **Configuring The Cluster**


# All processes entering MPI_Finalize


To run on nodes other than node001 and node002, the ../nodes file must be modified to contain
different hostnames. To perform other benchmarks, the PingPong argument should be omitted.


**3.7** **Configuring BMC (IPMI/iLO/DRAC/CIMC/Redfish) Interfaces**


BCM can initialize and configure the baseboard management controller (BMC) that may be present on
devices. This ability can be set during the installation on the head node (figure 3.15 of the _Installation_
_Manual_ ), or it can be set after installation as described in this section. The IPMI, iLO, DRAC, CIMC,
or Redfish interface that is exposed by a BMC is treated in the cluster management infrastructure as a
special type of network interface belonging to a device. In the most common setup a dedicated network
(i.e. IP subnet) is created for BMC communication. The 10.148.0.0/16 network is used by default for
BMC interfaces by BCM.


**3.7.1** **BMC Network Settings**
The first step in setting up a BMC is to add the BMC network as a network object in the cluster management infrastructure. The procedure for adding a network is described in section 3.2.2. The following
settings are recommended as defaults:


**Property** **Value**


Name bmcnet, ilonet, ipminet, dracnet, cimcnet, or rfnet


Domain name bmc.cluster, ilo.cluster, ipmi.cluster, drac.cluster,

cimc.cluster, or rf.cluster


Type Internal


Base address 10.148.0.0


Netmask bits 16


Broadcast address 10.148.255.255


Once the network has been created, all nodes must be assigned a BMC interface, of type bmc, on this
network. The easiest method of doing this is to create the interface for one node device and then to clone
that device several times.

For larger clusters this can be laborious, and a simple bash loop can be used to do the job instead:


[basecm11 ~]# for ((i=1; i<=150; i++)) do

echo "

device interfaces node$(printf '%03d' $i)

add bmc ipmi0

set network bmcnet

set ip 10.148.0.$i
commit"; done | cmsh -x # -x usefully echoes what is piped into cmsh


The preceding loop can conveniently be replaced with the addinterface command, run from within
the device mode of cmsh :


[basecm11 ~]# echo "

device

addinterface -n node001..node150 bmc ipmi0 bmcnet 10.148.0.1

commit" | cmsh -x


The help text in cmsh gives more details on how to use addinterface .
Most administrators are likely to simply run it as an interactive session in cmsh, running the help
addinterface command for reference, and then supplying the options for the nodes and interface settings in device mode. For example, as in the following session:


**3.7 Configuring BMC (IPMI/iLO/DRAC/CIMC/Redfish) Interfaces** **125**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% help addinterface

Name:

addinterface - Add a network interface to one or more nodes


Usage:
addinterface [OPTIONS] <type> <devicename> <network> <firstip>


Options:
... _help text omitted_ ...

Examples:

addinterface -n node001..node010 physical ib0 ibnet 10.149.0.1


[basecm11->device]% addinterface -n node001..node150 bmc ipmi0 bmcnet 10.148.0.1

[basecm11->device*]% commit


In order to be able to communicate with the BMC interfaces, the head node also needs an interface
on the BMC network. Depending on how the BMC interfaces are physically connected to the head node,
the head node has to be assigned an IP address on the BMC network one way or another. There are two
possibilities for how the BMC interface is physically connected:


  - When the BMC interface is connected to the primary internal network, the head node should be
assigned an alias interface configured with an IP address on the BMC network.


  - When the BMC interface is connected to a dedicated physical network, the head node must also
be physically connected to this network. A physical interface must be added and configured with
an IP address on the BMC network.


**Example**


Assigning an IP address on the BMC network to the head node using an alias interface:


[basecm11->device[basecm11]->interfaces]% add alias eth0:0

[basecm11->device[basecm11]->interfaces*[eth0:0*]]% set network bmcnet

[basecm11->device[basecm11]->interfaces*[eth0:0*]]% set ip 10.148.255.254

[basecm11->device[basecm11]->interfaces*[eth0:0*]]% commit

[basecm11->device[basecm11]->interfaces[eth0:0]]%

Mon Dec 6 05:45:05 basecm11: Reboot required: Interfaces have been modified

[basecm11->device[basecm11]->interfaces[eth0:0]]% ..;..

[basecm11->device[basecm11]]% reboot


As with any change to the network setup, the head node needs to be restarted to make the above
change active.
BMC connectivity from the head node to the IP addresses of the configured interfaces on the regular
nodes can be tested with Bash one-liner such as:


**Example**


[root@basecm11 ~]# for i in $(cmsh -c "device; foreach -t physicalnode (interfaces; _\_
use ilo0; get ip)"); do ping -c1 $i; done | grep -B1 packet

--- 10.148.0.1 ping statistics --1 packets transmitted, 0 received, 100% packet loss, time 0ms

--- 10.148.0.2 ping statistics --1 packets transmitted, 0 received, 100% packet loss, time 0ms

--- 10.148.0.3 ping statistics --1 packets transmitted, 0 received, 100% packet loss, time 0ms

...


**126** **Configuring The Cluster**


In the preceding example the packet loss demonstrates there is a connection problem between the head
node and the BMC subnet.


**3.7.2** **BMC Authentication**

The node-installer described in Chapter 5 is responsible for the initialization and configuration of the
BMC interface of a device. In addition to a number of network-related settings, the node-installer also
configures BMC authentication credentials. By default BMC interfaces are configured with username
bright and a random password that is generated during the installation of the head node. The password
is stored by CMDaemon. It can be managed from cmsh from within the base object of partition mode,
in the bmcsettings submode. This means that by default, each BMC in the cluster has that username
and password set during node boot.
For example, the current values of the BMC username and password for the entire cluster can be
obtained and changed as follows:


**Example**


[basecm11]% partition use base

[basecm11->partition[base]]% bmcsettings

[basecm11->partition[base]->bmcsettings]% get username

bright

[basecm11->partition[base]->bmcsettings]% get password

Za4ohni1ohMa2zew

[basecm11->partition[base]->bmcsettings]% set username bmcadmin

[basecm11->partition*[base*]->bmcsettings*]% set password

enter new password: ******

retype new password: ******

[basecm11->partition*[base*]->bmcsettings*]% commit


In Base View, selecting the cluster item in the resources pane, and then using the Settings option,
allows the BMC settings to be edited.
The BMC authentication credentials, and also some other BMC properties can be set cluster-wide,
category, or per node. As usual, category settings override cluster-wide settings, and node settings override category settings. The relevant properties are:


**Property** **Description**


BMC User ID User type. Normally set to 4 for administrator access.


BMC User Name User name used when sending a BMC command


BMC Password Password for specified user name when sending a BMC command


BMC Power reset delay Delay, in seconds, before powering up (default value: 0 )


BMC extra arguments Extra arguments passed to BMC commands


BMC privilege Possible options are


            - administrator


            - callback


            - OEMproprietary


            - operator


            - user


BMC configuration on a head node is done directly.


**3.7 Configuring BMC (IPMI/iLO/DRAC/CIMC/Redfish) Interfaces** **127**


For regular nodes BCM stores the BMC configuration, and uses it:


  - to configure the BMC interface from the node-installer


  - to authenticate to the BMC interface after it has come up


BMC management operations, such as power cycling nodes and collecting hardware metrics, can then
be performed after the node has been provisioned again.
If BMC authentication fails, then an explanation for why can often be found in the node-installer log
at /var/log/node-installer .


**3.7.3** **Interfaces Settings**

**Interface Name**

It is recommended that the network device name of a BMC interface start with ipmi, ilo, drac, cimc, or
rf, according to whether the BMC is running with IPMI, iLO, DRAC, CIMC, or Redfish. Numbers are
appended to the base name, resulting in, for example: ipmi0 .


**Obtaining The IP address**
BMC interfaces can have their IP addresses configured statically, or obtained from a DHCP server.
Only a node with a static BMC IP address has BMC power management done by BCM. If the node
has a DHCP-assigned BMC IP address, then it requires custom BMC power management (section 4.1.4)
due to its dynamic nature.


**Dell OpenManage And** racadm **Installation**
The Dell OpenManage utilities are provided with BCM only for RHEL8-based distributions at the time
of writing of this section (September 2023).
If Dell was chosen as the hardware vendor when the BCM ISO was created for installation, and
chosen as the hardware manufacturer when the head node was configured in the BCM installer (section 3.3.10 of the _Installation Manual_ ), then the Dell OpenManage utilities are located under /opt/dell
on the head node.

If Dell was chosen as the hardware manufacturer when nodes are configured in the BCM installer
(section 3.3.11 of the _Installation Manual_ ), then the default software image that is used by the node has
the Dell OpenManage utilities, located on the head node at /cm/images/default-image/opt/dell .
The Dell OpenManage utilities contain the racadm binary to carry out remote access control administration. The racadm tool can be used to issue power commands (Chapter 4). BCM runs commands
similar to the following to issue the power commands:


/opt/dell/srvadmin/sbin/racadm -r < _DRAC interface IP address_ - -u < _bmcusername_ - -p < _bmcpassword_ - _\_

serveraction powerstatus
/opt/dell/srvadmin/sbin/racadm -r < _DRAC interface IP address_ - -u < _bmcusername_ - -p < _bmcpassword_ - _\_

serveraction hardreset


The BMC username/password values can be obtained from cmsh as follows:


[root@basecm11 ~]# cmsh

[basecm11]% partition use base

[basecm11->partition[base]]% bmcsettings

[basecm11->partition[base]->bmcsettings]% get password

12345

[basecm11->partition[base]->bmcsettings]% get username

tom

[basecm11->partition[base]->bmcsettings]%


Sometimes the bright user does not have the right privilege to get the correct values. The racadm
commands then fail.

The bright user privilege can be raised using the following command:


**128** **Configuring The Cluster**


/opt/dell/srvadmin/sbin/racadm -r < _DRAC interface IP address_ - -u root -p < _root password_ - set _\_
iDRAC.Users.4.Privilege 511


Here it is assumed that the BMC user has the username bright, a userID 4, and the privilege can be

set to 511 .


**3.7.4** **Identification With A BMC**
Sometimes it is useful to identify a node using BMC commands. This can be done by, for example,
blinking a light via a BMC command on the node:


**Example**


ipmitool -U < _bmcusername_ - -P < _bmcpassword_ - -H < _host IP_ - chassis identify 1


The exact implementation may be vendor-dependent, and need not be an ipmitool command. Such
commands can be scripted and run from CMDaemon.
For testing without a BMC, the example script at /cm/local/examples/cmd/bmc_identify can be
used if the environment variable $CMD_HOSTNAME is set. The logical structure of the script can be used as
a basis for carrying out an identification task when a physical BMC is in place, by customizing the script
and then placing the script in a directory for use.
To have such a custom BMC script run from CMDaemon, the BMCIdentifyScript advanced configuration directive (page 855) can be used.


**3.8** **Configuring BlueField DPUs**


NVIDIA BlueField Data Processing Units (DPUs) are an aarch64 -based compute platform for cluster
infrastructure.

A DPU is a programmable network card with in-network compute, acceleration, isolation, storage,
and security capabilities.
Organizations can use DPUs to build software-defined, hardware-accelerated IT infrastructure.
The configuration of DPUs with BCM is done using the cm-dpu-setup utility. This creates DPU entities in BCM, installs the DOCA ( [https://docs.nvidia.com/doca/sdk/overview/index.html](https://docs.nvidia.com/doca/sdk/overview/index.html) ) software stack on host nodes, creates a specialized software image for the DPUs, and provisions them to
boot over the network.


**3.8.1** **Assumptions And Limitations**
DPU provisioning with BCM assumes that DPUs and their host nodes have a strict 1-to-1 relation. This
means that for all host nodes with DPUs, a single host only ever has a single DPU.
At the time of writing of this section, (April 2023) the cm-dpu-setup utility supports provisioning
using the 1.5.1 LTS version of the DPU software stack. Version 2.0 is due soon, but has not yet been
tested with cm-dpu-setup .


**3.8.2** **Preparation**

  - Secure boot must be disabled in the DPU BIOS settings. This is required to allow the DPU to boot
over PXE.


  - The DPU provisioning process requires the following two additional files:


1. a DOCA host software repository archive. For example:

doca-host-repo-ubuntu2004_1.5.1-0.1.8.1.5.1007.1.5.8.1.1.2.1_amd64.deb


2. a BlueField Bootstream (BFB) file. For example:

DOCA_1.5.1_BSP_3.9.3_Ubuntu_20.04-4.2211-LTS.signed.bfb


Both can be acquired from the NVIDIA developer website at [https://developer.nvidia.com/](https://developer.nvidia.com/networking/doca#downloads)
[networking/doca#downloads](https://developer.nvidia.com/networking/doca#downloads) . The files should be placed on the head node.


**3.8 Configuring BlueField DPUs** **129**


  - The DPUs all need to be physically installed in their hosts before running cm-dpu-setup .


1. Provisioning requires at least one performance port to be connected.


2. There must also be an Ethernet connection with the OOB/BMC port, which is the interface
over which BCM manages and PXE boots the DPU.


**3.8.3** **Installation**

New DPU deployments can only be provisioned using the cm-dpu-setup CLI tool, and not using Base
View. Configuration of the deployment should usually be done interactively, which results in a YAML
configuration file. This configuration file is then used by cm-dpu-setup to perform all provisioning
steps.
When a cluster already has a provisioned DPU deployment, cm-dpu-setup gives an option to extend
it with new DPUs.


**Provisioning DPUs With** cm-dpu-setup
Starting cm-dpu-setup without any arguments launches the interactive TUI for configuring a new DPU
deployment (figure 3.11):


Figure 3.11: Initial screen for cm-dpu-setup


When Provision is selected, the wizard guides the user on selecting the host nodes of the DPUs. It
is the DPUs that are to be provisioned within these hosts. Host nodes can be selected by choosing whole
categories or individual nodes. The selected nodes are rebooted during the provisioning process.
The cm-dpu-setup wizard then prompts for a name for the category of all DPU nodes. The DPU
image and DPU settings are assigned to this category, and the settings are thus automatically applied to
all DPU nodes.

Next is a screen to configure the performance network (figure 3.12):


Figure 3.12: Configuration screen for the DPU network


This configuration creates a network and connects it to the provided interface port. The options for
the port interfaces on most DPUs are P0 and P1. The exact value depends on the PCI bus numbering
allocated to the DPU.

The next screen asks for the IP address offset for the management interface, relative to the host node’s
assigned IP address on the internal network.
The cm-dpu-setup utility then prompts for names to be given for the software images that are to be
created on the DPU and the host nodes. The BFB file for building the DPU image, and a DOCA archive
for building an image for the host nodes, are also selected.


**130** **Configuring The Cluster**


Finally, cm-dpu-setup prompts for configuration of the DPU settings object that is defined in BCM
(figure 3.13):


Figure 3.13: Configuration screen for the DPU settings


Every physical interface port of a DPU can be configured to be either Ethernet or InfiniBand, depending on its SKU. The operation mode (section 3.8.4) of a DPU can be set to:


 - separated_host : treats the DPU as a separate host to the node hosting it


 - embedded_cpu : treats the DPU as part of the node hosting it


The boot mode determines from which device the DPU boots. This does not include PXE boot, which is
configured separately by cm-dpu-setup itself. This boot mode is relevant in cases where PXE boot fails.
The summary screen appears after the configuration steps are completed. It allows the configuration
to be viewed, saved, or saved and deployed.


Figure 3.14: Summary of the configuration


Deployment takes some time, especially during software image creation from the BFB file. The
DPU device is automatically given a name composed of the node which hosts it together with the suffix -dpu . Steps are displayed during the deployment process. The log file gets written at /var/log/
cm-dpu-setup.log


**Extending DPU Deployment With** cm-dpu-setup
When the cluster already contains DPU nodes, the cm-dpu-setup wizard provides additional menu
options to extend or remove the deployment (figure 3.15):


Figure 3.15: Initial screen for cm-dpu-setup with already existing DPU nodes


Extending the cluster with more DPU nodes can be done with


  - a new network, for example InfiniBand instead of Ethernet, or just a separate subnet


**3.8 Configuring BlueField DPUs** **131**


  - with a new BFB base image, which creates a new DPU software image


  - simply adding additional DPUs to an existing DPU category, which implies that they boot with
the same image and have the same network configuration


For the first two options, cm-dpu-setup prompts for the configuration of a new category, so that the
different subsets of DPUs in the cluster can be distinguished. All kinds of variations in configuration
can thus be carried out.


**CLI Options For** cm-dpu-setup
The cm-dpu-setup utility has the following usage instructions:


root@basecm11:~# cm-dpu-setup -h


usage: DPU cm-dpu-setup [-c <config_file>] [--remove] [--yes-i-really-mean-it] [--erase-images]

[--skip-network] [--skip-host-image] [--skip-archos] [--extend]

[--hold-bfb-packages HOLD_BFB_PACKAGES] [-v] [--store-name-aliases]

[--no-distro-checks] [--json] [--output-remote-execution-runner]

[--on-error-action debug,remotedebug,undo,abort] [--skip-packages]

[--min-reboot-timeout <reboot_timeout_seconds>] [--allow-running-from-secondary]

[--dev] [-h]


optional arguments:

-h, --help Print this screen


common:

Common arguments


-c <config_file> Load runtime configuration for plugins from a YAML config file


Managing DPUs:

Flags that can be used to manage DPUs in a cluster


--remove Remove and reset DPUs

--yes-i-really-mean-it

Required for additional safety

--erase-images Erase all images from disk during removal

--skip-network Skip check and creation of DPU performance network

--skip-host-image Skip creation of the Host Image

--skip-archos Skip creation of ArchOS and continue with DPU deployment

--extend Extend current deployment with new DPU nodes

--hold-bfb-packages HOLD_BFB_PACKAGES
Mark a custom set (comma-separated) of packages to be held for install

during DPU image build


The help output continues beyond this, but only contains advanced, generic cm-setup options, and
not DPU-specific options.
The options can be grouped as follows:


  - Common arguments:


**–** -c < _YAML configuration file_    - : Loads a runtime configuration for plugins, from a YAML configuration file.


  - Removal arguments:


**–** --remove : Starts the removal process. Does not do anything unless --yes-i-really-mean-it
is also provided.


**132** **Configuring The Cluster**


**–**
--yes-i-really-mean-it : Required as a safety precaution when removing the DPU deployment from the CLI.


**–**
--erase-images : Also removes the software images from disk instead of only removing the
entities from BCM.


  - Provisioning management arguments: This group of arguments is useful when the provisioning
process has been interrupted and an administrator wants to continue it without starting again
from scratch.


**–**
--skip-network : Skips check for overlap with existing networks and creation of the network.


**–**
--skip-host-image : Skips the creation of the host image.


**–**
--skip-archos : Skips the creation of the DPU image, node-installer image, shared image,
and the ArchOS object.


  - DPU image arguments:


**–** --hold-bfb-packages < _packages_    - : Comma-separated list of packages to hold off on with
post-install configuration and set up a service to finish it on DPU boot. This is necessary for
certain packages that fail to install inside of a chroot/systemd-spawn environment because
their configuration depends on certain hardware being present or being booted with systemd
as PID 1.


**Troubleshooting**
Some problems that may occur during installation are described in this section, along with possible
solutions.


**Host or DPU image creation stage fails:**


 - **A package fails to install or the software configuration fails:** If this happens, then the cluster
administrator should try to establish how it failed. Did it fail because of:


**–** dependencies on systemd ? A workaround could be to pass a dependency as an argument to
--hold-bfb-packages .


**–**
unsupported external hardware? The cluster administrator can check that that the base BFB
file used supports the hardware used (1.5.1 LTS or newer).


 - **A repository is inaccessible:** If this happens, then the cluster administrator should check that the
BCM repositories are reachable from the head node, and that the authentication is correct. If there
are missing or invalid GPG keys, then the keys that the BFB file is shipped with should be checked.
The 1.5.1 LTS version of the BFB file ships with a Kubernetes GPG key that expired in December
2022. The cm-dpu-setup utility automatically fetches the correct key.


**Pre-install checks are failing:**


  - DPU-related entities already exist in the cluster: if a previous deployment or setup process was
not cleaned up properly, then there might be leftover entities in BCM that inhibit a fresh setup.
The generic entities related to a DPU deployment are as follows:


**–** DPU network


**–** RShim network


**–**
DPU category


**–**
DPU settings (applied to the category)


**–**
Host image


**3.8 Configuring BlueField DPUs** **133**


**–**
DPU image


**–** Ubuntu 20.04 aarch64 (in the base partition, under archos mode)


**–** Ubuntu 20.04 aarch64 node-installer image


**–** Ubuntu 20.04 aarch64 shared image


**–** DPU nodes


**Rebooting nodes fails** Possible failures when trying to reboot nodes are:


**Mellanox configuration fails:** the DPU provisioning stage configures the DPU via the command:
mlxconfig -d /dev/mst/mt41686_pciconf0
on the host. If this stage fails, then possible reasons are:


  - the DPU is not available


  - it is a model that does not support Ethernet (the default config resets both ports to Ethernet during
provisioning)


  - the DPU appears under a different device identifier in the filesystem


In the last case, BCM support can be contacted to check on the state of updates for support on the device.


**Timeout while waiting for DPUs to become reachable:** It may be that cm-dpu-setup could not
establish an SSH connection from the RSHim (outside the DPU) to the tmfifo interface (inside the DPU).
Underlying reasons for this could be:


  - The PXE boot may have failed


  - the interfaces on the DPU are not configured correctly.


Provisioning a base BFB file to the DPU directly with cmsh using


**Example**


[basecm11->device[node001-dpu]]% dpu push-bfb


can be tried out to confirm that the interface is healthy. If the problem persists, then BCM support can
be contacted.


**3.8.4** **Managing DPU Settings**
A DPU is generally managed as a node, with a custom kernel, by CMDaemon. So most of the regular
node operations work with the DPU just as they do with a regular node.
This section covers DPU operations that are not managed by regular node operations in CMDaemon.
A backend script, cm-dpu-manage, is used to carry out these operations, but it is recommended to use
the cmsh front end for all the operations instead.


**DPU Discovery**
At device level, DPUs can be discovered:


**Example**


[basecm11->device]% dpu discover

Node bfb boot_order mac success version

----------- ---- -------------- ------------------ -------- -----------------------------------...

node001-dpu no NET-OOB-IPV4 94:6d:ae:6c:89:1e yes bright ubuntu 22.04 Cluster Manager...

node002-dpu no NET-OOB-IPV4 94:6d:ae:6c:88:be yes bright ubuntu 22.04 Cluster Manager...


**134** **Configuring The Cluster**


**Listing And Pushing BFB Files For DPUs**
All available BFB files can be listed with:


**Example**


[basecm11->device]% dpu list-bfb

DOCA_2.0.2_BSP_4.0.3_Ubuntu_22.04-10.23-04.prod.bfb


A specific BFP file can be provisioned to a DPU node001-dpu with


**Example**


[basecm11->device]% dpu push-bfb -n node001-dpu -f DOCA2.0.2_BSP_4.0.3_Ubuntu_test.bfb


**DPU Settings That Have Been Applied**
The DPU settings that are active (that have been _applied_ ) for a particular DPU can be viewed with:


**Example**


[basecm11->device]% dpu show -n node001-dpu

Node boot_mode boot_timeout display_level drop_mode operation_mode Result Error

------------ ----------- ------------- -------------- --------- ---------------- ------ ----
node001-dpu EMMC 100 BASIC NORMAL EMBEDDED_CPU(1) good


**DPU Settings Submode**
DPU settings can be managed with cmsh from within the dpusettings submode. This submode is
accessible from within the partition and category modes. The submode can also be accessed from
within device mode, if the device is a DPU.
For example, for a DPU category given the name dpu during a cm-dpu-setup run, the submode
settings might look like:


**Example**


basecm11->category[dpus]->dpusettings]% show

Parameter Value

-------------------------------- -----------------------------------------------
Revision

Operation mode embedded

Display level basic

Boot mode emmc

Drop mode normal

Boot timeout 1m 40s

Boot order NET-OOB-IPV4

Interface mode port 1 eth

Interface mode port 2 ib

Offload OVS to hardware yes

Key value settings <submode>


If a setting is changed within the dpusettings submode, then the value becomes active on the DPU
only after committing it, and then running the dpu apply command.


**The** dpu apply **command:** makes committed DPU settings active on the DPU.


**Example**


**3.8 Configuring BlueField DPUs** **135**


root@basecm11:~# cmsh

[basecm11]% device use node001-dpu

[basecm11->device[node001-dpu]]% dpusettings

[basecm11->device[node001-dpu]->dpusettings]% get displaylevel

advanced

[basecm11->device[node001-dpu]]% !ssh node001 grep DISPLAY /dev/rshim0/misc
DISPLAY_LEVEL 1 (0:basic, 1:advanced, 2:log)

[basecm11->device[node001-dpu]->dpusettings]% set displaylevel < _tab_ >< _tab_ 
advanced basic log

[basecm11->device[node001-dpu]->dpusettings]% set displaylevel basic

[basecm11->device*[node001-dpu*]->dpusettings*]% commit

[basecm11->device[node001-dpu]->dpusettings]% exit

[basecm11->device[node001-dpu]]% dpu apply

[basecm11->device[node001-dpu]]% !ssh node001 grep DISPLAY /dev/rshim0/misc
DISPLAY_LEVEL 0 (0:basic, 1:advanced, 2:log)


Within the dpusettings submode:


  - The displaylevel setting can take a value of


**–** basic


**–** advanced, or


**–** log .


The value configures the verbosity of the /dev/rshim0/misc file of the rshim0 device. An rshim
device is a network interface between the host and a DPU.


 - An Offload OVS to hardware value of yes allows Open vSwitch to offload tasks to the hardware
running on the interface, reducing CPU load.


  - The value of operationmode can be:


**–** embedded : ECPF (Embedded CPU Physical Function) mode lets the embedded ARM system
of the DPU control the NIC resources and data path of the host as well as of the DPU.


**–**
separated : separated host mode lets the host and the DPU control their own resources, but
has them sharing the same NIC.


Further details on the operation mode can be found in the DOCA SDK documentation at [https://docs.nvidia.com/doca/sdk/installation-guide-for-linux/index.html#](https://docs.nvidia.com/doca/sdk/installation-guide-for-linux/index.html#configuring-operation-mode)

[configuring-operation-mode](https://docs.nvidia.com/doca/sdk/installation-guide-for-linux/index.html#configuring-operation-mode) .


  - The boot order configures the UEFI order from which device the DPU boots. Options are:


**–** DISK : boots from an EMMC device


**–** UEFI_SHELL : boots into a UEFI shell


**–** NET-OOB-IPV4 : boots via PXE over an OOB interface running IPv4


Options can also be combined using comma-separation, and the boot order then follows that
comma-separated order. The boot order gets written with a dpu apply to a BlueField configuration file /etc/bf.cfg on the DPU. The value DISK,NET-OOB-IPV4 thus results in a bf.cfg file:


BOOT0=DISK

BOOT1=NET-OOB-IPV4


which results in disk booting being tried first, then PXE booting.


**136** **Configuring The Cluster**


  - The keyvaluesettings are existing key/value settings that can be committed from
the mlxconfig script ( [https://docs.nvidia.com/networking/display/MFT4170/Examples+of+](https://docs.nvidia.com/networking/display/MFT4170/Examples+of+mlxconfig+Usage)
[mlxconfig+Usage](https://docs.nvidia.com/networking/display/MFT4170/Examples+of+mlxconfig+Usage) ).


The settings can alternatively be user-defined for the DPU in cmsh and committed from there.


For example, the mlnxconfig script can be run directly on the DPU host, node001 as follows:


**Example**


node001# mlxconfig -d < _device-id_   - set PCI_DOWNSTREAM_PORT_OWNER[4]=0xF


The cmsh equivalent for the DPU is:


**Example**


[basecm11->device[node001-dpu]->dpusettings]% keyvaluesettings

[basecm11->device*[node001-dpu*]->dpusettings*->keyvaluesettings*]% set PCI_DOWNSTREAM_PORT_OWNER[4] 0xF

[basecm11->device*[node001-dpu*]->dpusettings*->keyvaluesettings*]% commit

[basecm11->device[node001-dpu]->dpusettings->keyvaluesettings]% show

Parameter Value

-------------------------------- -------------------------------
PCI_DOWNSTREAM_PORT_OWNER[4] 0xF


**DPU Interfaces And IP Addresss Persistence When Operation Mode Changes**
The IP address, network, and network device settings of the DPU and host can be seen as usual within
the interfaces mode. For a node node001, that hosts a DPU node001-dpu, the interfaces list would
show an output similar to:


**Example**


[basecm11->device[node001]->interfaces]% list

Type Network device name IP Network Start if

------------ -------------------- ---------------- ---------------- -------
physical BOOTIF [prov] 10.141.0.1 internalnet always

physical DPU1 10.147.0.1 netdpu1 always

physical tmfifo_net0 192.168.100.1 tmfifonet always

[basecm11->device[node001]->interfaces]% device use node001-dpu

[basecm11->device[node001-dpu]->interfaces]% list

Type Network device name IP Network Start if

------------ -------------------- ---------------- ---------------- -------
physical BOOTIF [prov] 10.141.0.101 internalnet always

physical p1 10.147.0.1 netdpu1 always

physical tmfifo_net0 192.168.100.2 tmfifonet always


In the example, looking at the performance embedded network netdpu1, the device DPU1 on the
host node node001 and the device p1 on the DPU node001-dpu, have the same IP address. This is to
avoid interfaces reconfiguration when the DPU is switched between embedded and separated mode.


**3.9** **Configuring Switches And PDUs**


**3.9.1** **Configuring With The Manufacturer’s Configuration Interface**
Network switches and PDUs that are to be used as part of the cluster should be configured with the
PDU/switch configuration interface described in the PDU/switch documentation supplied by the manufacturer. Typically the interface is accessed by connecting via a web browser or telnet to an IP address
preset by the manufacturer.
The IP address settings of the PDU/switch must match the settings of the device as stored by the
cluster manager.


**3.9 Configuring Switches And PDUs** **137**


  - In Base View, this is done via the navigation path Devices  - Edit  - < _switchname_  - to select the
switch. If the switch does not already exist, then it can be added via the ADD button. The values
in the associated Settings window that comes up (figure 3.16) can then be filled in, and the IP
address can be set and saved.


  - In cmsh this can be done in device mode, with a set command:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% set switch01 ip 10.141.253.2

[basecm11->device*]% commit


**Port Assignments For Switches**

  - Using the uplinks option to configure uplink ports is described in section 3.10.3.


  - The showport tool for seeing what MAC address matches what port number on a switch is described in section 3.10.4.


  - The switchoverview tool gives an overview of the MAC addresses detected on the ports based on
SNMP queries, and is described in section 3.10.6.


  - The switchports command lists the switches and switch ports that have been assigned a node.


  - The switchports option assigns ports on a switch to a node:


**Example**


[basecm11->device]% #the option:

[basecm11->device]% set node003 switchports switch01:1

[basecm11->device*]% commit

[basecm11->device]% #the command:

[basecm11->device*]% switchports

Switch #Port Node

---------------- ------ ---------------
switch01 1 node003


The switchports option used at node level is a legacy option, which can still be used in BCM
version 10. However it may not work as expected when a node has multiple interfaces that may
be connected to a switch.


Since BCM version 10 it is therefore recommended to assign ports from within the interfaces
submode for a node. This assigns ports clearly per interface, and supports bonding of the interfaces (section 3.5). Management of ports at interface level also makes it possible for CMDaemon
Lite (section 2.6.7) to manage the network configuration of Cumulus switches (section 3.10).


**Example**


[basecm11->device]% use node003; interfaces

[basecm11->device[node003]->interfaces]% set eth1 switchports switch01:2

[basecm11->device*[node003*]->interfaces*]% set eth2 switchports switch01:3

[basecm11->device*[node003*]->interfaces*]% commit; ..

[basecm11->device[node003]]% switchports

Switch #Port Node

---------------- ------ ---------------
switch01 1 node003

switch01 2 node003

switch01 3 node003


**138** **Configuring The Cluster**


Managing PDUs in Base View or cmsh is done in a similar way to the preceding method for switches.
However, assigning PDUs and PDU ports to devices such as nodes is not part of this method, and is
instead described in section 4.1.1.


**APC PDUs**

For the APC brand of PDUs, the powercontrol value for the PDU device should be set to apc .
For example, for a PDU with the name mypdu, its value can be set in cmsh with:


**Example**


[basecm11->device[mypdu]]% set powercontrol apc; commit


and in Base View with the navigation path:


Devices  - Power Distribution Units  - Power Distribution Unit list  - Power Distribution

Unit - Power control


If it is not set to apc, then the list of PDU ports is ignored by default.


**3.9.2** **Configuring SNMP**
BCM can be used to manage switches, including many InfiniBand switches, using SNMP. This requires
that SNMP be enabled. If disablesnmp is set to no, the default, then SNMP is enabled for the switch:


**Example**


[basecm11]% device add switch myibswitch

[basecm11->device[myibswitch]]% get disablesnmp

no


**Configuring SNMP Community Strings**
In order to allow the cluster management software to communicate with the switch or PDU, SNMP must
be enabled on it, and the SNMP community strings should be configured correctly.
By default, the SNMP community strings for switches and PDUs are set to public and private for
respectively read and write access. If different SNMP community strings have been configured in the
switch or PDU, the readstring and writestring properties of the corresponding switch device should
be changed.


**Example**


[basecm11]% device use switch01

[basecm11->device[switch01]]% snmpsettings

[basecm11->device[switch01]->snmpsettings]% get readstring

public

[basecm11->device[switch01]->snmpsettings]% get writestring

private

[basecm11->device[switch01]->snmpsettings]% set readstring public2

[basecm11->device*[switch01*]->snmpsettings*]% set writestring private2

[basecm11->device*[switch01*]->snmpsettings*]% commit


Alternatively, these properties can also be set in Base View via the navigation path:


Devices  - Switches  - Edit  - SNMP Settings


**3.9 Configuring Switches And PDUs** **139**


**Configuring SNMP Settings**
SNMP settings can be configured in cmsh via the snmpsettings submode, which is available under
partition mode as well as under device mode.
The submode allows the version to be set to v1, v2c, or v3 .
Setting the version to the value file is also an option, but is not meant as an option for end users. It
is used in SNMP walk emulation for debugging non-standard switches.
The SNMPv3 settings that can be managed in BCM are:


**Example**


[basecm11]% device use switch01

[basecm11->device[switch01]]% snmpsettings

[basecm11->device[switch01]->snmpsettings]% show

Parameter Value

-------------------------------- -----------------------------------------------
Authentication key < not set >

Authentication protocol MD5

Context

Privacy key < not set >

Privacy protocol DES

Retries -1

Revision

Security level Authentication encrypted

Security name

Timeout 0s

VLAN Timeout 0s

version V3


The set command can be used, sometimes with tab-completion, to set the SNMP switch parameters.
For example, for the SNMPv3 parameters that are set to use cryptographic keys:


**Example**


[basecm11->device*[switch01*]->snmpsettings*]% set authenticationprotocol _<TAB><TAB>_

md5 sha

[basecm11->device[switch01]->snmpsettings]% set authenticationprotocol aes

[basecm11->device*[switch01*]->snmpsettings*]% set privacyprotocol _<TAB><TAB>_

aes des

[basecm11->device*[switch01*]->snmpsettings*]% set privacyprotocol aes

[basecm11->device*[switch01*]->snmpsettings*]% commit

[basecm11->device[switch01]->snmpsettings]%


**SNMP Traps**
BCM can assign an SNMP trap manager role to a node. The snmptrapd daemon is then configured and
managed on the assigned node by CMDaemon.
Configuration options include enabling or disabling mailing of the messages, and setting the sender
and recipients for the mail. By default an undefined value for Server means that the SNMP server is

localhost .


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% roles

[basecm11->device[node001]->roles]% assign snmptrap

[basecm11->device[node001]->roles*[snmptrap*]]% show


**140** **Configuring The Cluster**


Parameter Value

-------------------------------- -----------------------------------------------
Access public

Add services yes

All administrators no

Alternative script

Arguments

Event yes

Mail yes

Name snmptrap

Provisioning associations <0 internally used>

Recipients

Revision

Sender

Server

Type SnmpTrapRole


**3.10** **Configuring Cumulus Switches**


A Cumulus switch is a switch that runs Cumulus Linux, which is a Debian-based distribution with a
networking focus.
The following capabilities and features are available, or can be run, on a switch that can run Cumulus
Linux:


  - ONIE (Open Network Install Environment, [https://opencomputeproject.github.io/onie/](https://opencomputeproject.github.io/onie/) ): a
bootloader, similar in concept to PXE booting. It allows the switch to boot up and install the
Cumulus OS from an image on the network. Installing Cumulus with ONIE wipes out any existing
image already installed on the switch.


  - ZTP (Zero Touch Provisioning): a protocol that is used with the ztp client. The protocol uses
specially defined DHCP options. ZTP allows the switch to automatically carry out provisioning
for other hardware devices on a network on top of an OS on the switch. The capability to carry
this out becomes available automatically when the switch is powered on, and the interface on
[which provisioning is to be carried out automatically becomes active with an IP address (“day-0](https://community.cisco.com/t5/nso-developer-hub-blogs/day-1-day-0-day-1-day-2-n-configurations/ba-p/3658255)
[provisioning”).](https://community.cisco.com/t5/nso-developer-hub-blogs/day-1-day-0-day-1-day-2-n-configurations/ba-p/3658255)


[• NVUE (NVIDIA User Experience):](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-54/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-CLI/) a CLI that uses the nv command set to manage the
network configuration of the switch. The NVUE CLI is documented at [https://docs.](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-CLI/)
[nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-CLI/)
[NVIDIA-User-Experience-NVUE/NVUE-CLI/](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-CLI/) .


  - The NVUE REST API: if it is explicitly enabled, can run the same commands via
HTTP as the NVUE CLI. The NVUE REST API is documented at [https://docs.](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-API/)
[nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-API/)
[NVIDIA-User-Experience-NVUE/NVUE-API/](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-API/)


  - Public key SSH: if configured, the administrator can access the switch from the head node safely
and securely with public key SSH, including passwordless SSH.


A Cumulus switch is added to the cluster manager as a regular switch object:


**Example**


[basecm11]% device add switch myswitch

[basecm11->device*[myswitch*]]% # hasclientdaemon: set if CMDaemon Lite should run on switch

[basecm11->device*[myswitch*]]% set hasclientdaemon yes


**3.10 Configuring Cumulus Switches** **141**


[basecm11->device*[myswitch*]]% interfaces

[basecm11->device*[myswitch*]->interfaces]% add physical eth0

[basecm11->device[myswitch*]->interfaces*[eth0*]]% set mac 12:34:56:78:90:AB

[basecm11->device[myswitch*]->interfaces*[eth0*]]% set ip 1.2.3.4

[basecm11->device[myswitch*]->interfaces*[eth0*]]% commit

[basecm11->device[myswitch]->interfaces[eth0]]% ..;..

[basecm11->device[myswitch]]% status
myswitch ................ [ DOWN ]


Cumulus access settings (described later on, starting from page 141) and ZTP settings (described
later on, starting from page 146) must also be configured for the switch to work correctly.
Committing the Cumulus switch object configuration automatically configures the DHCP and the
DNS services. The DHCP server is configured by CMDaemon to use the ZTP custom provisioning
script. The ZTP provisioning script is created on-demand, along with a directory, from a default template (page 147) when the switch boots. The creation can alternatively be forced right away by running
the initialize command.


**3.10.1** **Cumulus Switches Access Configuration, Initialization And Network Device**
**Discovery**

**Cumulus Switches Access Configuration**
By default, Cumulus switches use certificate-based authentication for CMDaemon access, just like regular nodes. DGX SuperPODS are configured in that manner.
However, CMDaemon Lite (section 2.6.7) is recommended instead of CMDaemon for Cumulus
switches on most other clusters. If CMDaemon Lite is to run on the switch, then the hasclientdaemon
parameter must be enabled for it:


**Example**


[basecm11]% device use mycumulus

[basecm11->device*[mycumulus*]]% set hasclientdaemon yes

[basecm11->device*[mycumulus*]]% commit


The cluster administrator must configure a username/password pair for SSH public key authentication with CMDaemon Lite.


  - Since BCM version 11, Cumulus switch access via a username/password pair is configured in the
accesssettings submode. Updates can be done using ZTP or NV.


  - In earlier versions of BCM SNMP settings were used to set the username/password pair.


**Example**


[basecm11->device]% add switch mycumulus

[basecm11->device*[mycumulus*]]% accesssettings

[basecm11->device*[mycumulus*]->accesssettings*]% set username cumulus; set password 1234

[basecm11->device*[mycumulus*]->accesssettings*]% show

Parameter Value

-------------------------------- -----------------------------------------------
Revision

Username cumulus

Password *********

Rest port 8765

Update in ztp no

Update in NV no

[basecm11->device*[mycumulus*]->accesssettings*]% commit


**142** **Configuring The Cluster**


If all switches are Cumulus switches, then setting the username/password can be carried out at
partition level with:


**Example**


[basecm11->partition[base]]% accesssettings

[basecm11->partition[base]]->accesssettings]% set username cumulus; set password 1234

[basecm11->partition*[base*]]->accesssettings*]% commit


Compared with a regular node (section 6.2), a Cumulus switch has these differences when setting a
username and password:


  - The password change only takes effect on the switch after the switch reboots.


  - If the startup.yaml file used by NV does not set the password, and cm-lite-daemon is not installed, then during reboot either


**–** Update in ztp must be set to yes to allow the password change using ZTP

or


**–** Update in NV must be set to yes, to allow the password change using NV


The REST API port, with a default value of 8765, can also be modified from the accesssettings
submode, to match the deployment specifications.
Other parameters for CMDaemon Lite integration are described in the section starting on page 143,
**Custom Services Option 1: Cumulus With CMDaemon Lite** . Also covered in that section, on page 146,
are the ZTP settings. ZTP settings are managed via the ZTP mode of cmsh, and are needed for the switch
to pick up its ZTP provisioning script.


**The Cumulus Custom Discovery Script (Deprecated)**
This is a legacy script that comes with BCM, and is at /cm/local/apps/cmd/scripts/
cm-cumulus-switch.py .
Setting the script and running the initialize command for the Cumulus switch in device mode
initializes access settings and carries out network discovery for the Cumulus switch, in versions of BCM
prior to version 10.
Since BCM version 10, the script is only needed for the Cumulus Linux version 4 series. Since Cumulus Linux version 5, and since BCM version 10, the script is no longer required, due to the integration
of Cumulus with BCM.

A Cumulus switch running version 4 of Cumulus Linux can be set up and initialized on BCM version
10 with:


**Example**


[basecm11->device*[mycumulus*]]% set controlscript /cm/local/apps/cmd/scripts/cm-cumulus-switch.py

[basecm11->device*[mycumulus*]]% commit

[basecm11->device[mycumulus]]% initialize


**3.10.2** **Custom Service Setups For Cumulus Linux**
There are two custom service setups that are supported for cluster management on top of Cumulus
Linux:


1. a setup that uses CMDaemon Lite (page 143, **Custom Services Option 1: Cumulus With CMDae-**
**mon Lite** )


2. a setup that uses YAML to configure the services (page 147, **Custom Services Option 2: Cumulus**
**With A YAML Preconfiguration** ).


**3.10 Configuring Cumulus Switches** **143**


These can actually be run together, if the services do not conflict with each other. For example, the
nvued service can be installed via YAML, to provide the NVUE, independently of CMDaemon Lite. It is
however useful to describe these custom service setups individually.


**Custom Services Option 1: Cumulus With CMDaemon Lite**
If the Cumulus switch is defined and configured with CMDaemon Lite, then this allows some Cumulus
features to be managed via BCM, as well as some of the standard features of BCM to work on the switch.
The following features can be managed:


  - monitoring (Chapter 10). For example, the latest data values (section 10.6.3) of the switch, including the bytes going through the many ports, can be seen with:


**Example**


[basecm11->device[myswitch]]% latestmonitoringdata

Measurable Parameter Type Value Age State Info

---------------- --------------- ------------ ------------- --------- --------- --------
AlertLevel count Internal 0 1m 5s

AlertLevel maximum Internal 0 1m 5s

AlertLevel sum Internal 0 1m 5s

BufferMemory Memory 113 MiB 2m 5s
BytesRecv eth0 Network 22.3917 B/s 2m 5s
BytesRecv mgmt Network 6.79167 B/s 2m 5s
BytesRecv mirror Network 0 B/s 2m 5s
BytesRecv swid0_eth Network 0 B/s 2m 5s
BytesRecv swp1 Network 0 B/s 2m 5s
BytesRecv swp2 Network 0 B/s 2m 5s
BytesRecv swp3 Network 0 B/s 2m 5s
BytesRecv swp4 Network 0 B/s 2m 5s

...


  - system information can be viewed with the sysinfo command:


**Example**


[basecm11->device[myswitch]]% sysinfo

Name Value

------------------------- ----------------------------------------------------------
BIOS Version 1.3

BIOS Vendor American Megatrends Inc.

BIOS Date

Motherboard Manufacturer

Motherboard Name

System Manufacturer NVIDIA

System Name SN2201

Vendor Tag
Total Memory 8048771072 bytes (7.496GB)
Swap Memory 0 bytes (0B)

OS Name Linux

OS Version 5.10.0-cl-1-amd64

OS Flavor #1 SMP Debian 5.10.162-1+cl5.4.0u1 (2023-01-20)

Number of Physical CPUs 1

Number of Cores 2

Core 0-1 Intel(R) Atom(TM) CPU C3338R @ 1.80GHz

Number of Disks 1


**144** **Configuring The Cluster**


Total Disk Space 115,923,419,136 bytes (115GB)
Disk /dev/nvme0n1p4 (19,320,569,856 bytes, 19.3GB) ()

SELinux no

FIPS no

Fabric no

Age 21h 58m
ZTP/date Tue Apr 11 09:50:21 2023 UTC

ZTP/method ZTP DHCP

ZTP/result success

ZTP/state enabled

ZTP/url http://10.141.255.254:8080/switch/myswitch/cumulus-ztp.sh

ZTP/version 1.0

[basecm11->device[myswitch]]%


  - systemd services can be added for the device via roles, and listed in the services submode (section 3.14). Management of services is a standard part of CMDaemon Lite since NVIDIA Base
Command Manager version 10.23.06.


  - configuration via cmsh : can be set up via either a YAML file, or manually, or automatically with
some optional manual parts. The appropriate mode is set with nvconfigurationmode for the
Cumulus device:


[basecm11->device[cumulus02]]% set nvconfigurationmode < _tab_ >< _tab_   
auto file manual


**–** auto : BCM settings such as for hostname or timezone for a Cumulus switch network configuration are converted automatically to run as nv commands. All the nv commands carried out
on the switch via BCM, whether from an automatic conversion or not, can be viewed within
nvconfiguration mode. The nv commands that have been automatically converted from
BCM settings are assigned a type value of auto, and can be viewed within nvconfiguration
mode:


**Example**


[basecm11->device[myswitch]->nvconfiguration]% show

Type #Index Command

-------- -------- ---------------------------------------------------------------
auto 1 nv set system hostname myswitch
auto 2 nv set system timezone Europe/Amsterdam

auto 3 nv set service snmp-server enable on

auto 4 nv set service snmp-server listening-address all

auto 5 nv set service snmp-server listening-address all-v6

auto 6 nv set service snmp-server readonly-community public access any

auto 7 nv set service ntp mgmt pool 10.141.255.254

auto 8 nv set service dns mgmt server 10.141.255.254

auto 9 nv set service syslog mgmt server 10.141.255.254 port 514

auto 10 nv set service syslog mgmt server 10.141.255.254 protocol udp

auto 11 nv set bridge domain br_default type vlan-aware

[basecm11->device[myswitch]->nvconfiguration]%


The settings are applied to the switch when the apply command is run within nvconfiguration
mode.


**–** manual : If nvconfigurationmode is set to manual then the commands of type auto (as shown
within the preceding example) are ignored. Direct nv commands can be entered by the administrator manually from within the manual NV Configuration mode.


**3.10 Configuring Cumulus Switches** **145**


Direct nv commands can actually also be added within auto mode for nvconfiguration, and
are in that case also of type manual :


**Example**


[basecm11->device[myswitch]->nvconfiguration]% nv set interface swp27 ip address 10.141.255.123

[basecm11->device*[myswitch*]->nvconfiguration*]% show

Type #Index Command

-------- -------- ---------------------------------------------------------------
auto 1 nv set system hostname myswitch

...

auto 11 nv set bridge domain br_default type vlan-aware

manual 1 nv set interface swp27 ip address 10.141.255.123


The changes are applied when the apply command is run within nvconfiguration mode.

Only commands of type manual can be removed from nvconfiguration mode. The removal
can be carried out from within nvconfiguration mode with the help of the manual command
and the nv del command:


**Example**


[basecm11->device*[myswitch]->nvconfiguration]% ..; get nvconfigurationmode; nvconfiguration

AUTO

[basecm11->device*[myswitch]->nvconfiguration]% show

...

auto 11 nv set bridge domain br_default type vlan-aware

manual 1 nv set interface swp27 ip address 10.141.255.123
manual 2 nv set system timezone Europe/Berlin

manual 3 nv set service snmp-server listening-address all-v6


[basecm11->device*[myswitch]->nvconfiguration]% manual #nvconfiguration mode changes to manual

#copies all types to be manual

[basecm11->device*[myswitch]->nvconfiguration]% ..; get nvconfigurationmode; nvconfiguration

MANUAL

[basecm11->device*[myswitch]->nvconfiguration]% show

manual 1 nv set interface swp27 ip address 10.141.255.123
manual 2 nv set system timezone Europe/Berlin

manual 3 nv set service snmp-server listening-address all-v6

[basecm11->device*[myswitch]->nvconfiguration]% nv del 1-2

[basecm11->device*[myswitch]->nvconfiguration]% commit

[basecm11->device*[myswitch]->nvconfiguration]% apply #only now is switch updated


The manual command switches nvconfigurationmode to manual, and copies the stack of auto
type commands over to the stack in manual mode. The commit command saves the configuration in the CMDaemon database. As usual, the configuration defined by the manual NV
configuration mode is only applied to the switch after using the apply command.


The stack in the manual mode stack is then what is used on the switch instead of the auto

mode stack, as per the CMDaemon state.


**–** file : If nvconfigurationmode is set to file, then a YAML file is used by BCM to carry out
the commands. A sample YAML file that uses the currently running configuration of the
switch can be displayed by running
nv config show
on the switch.


**Example**


**146** **Configuring The Cluster**


[basecm11->device[myswitch]]% set nvconfigurationmode file

[basecm11->device*[myswitch*]]% set nvconfigurationfile startup.yaml

[basecm11->device*[myswitch*]]% commit


The apply command is not used for file mode, since the commands are carried out over

ZTP.


  - the ZTP configuration can be managed from ztpsettings mode:


**Example**


[basecm11->device[cumulus02]]% ztpsettings

[basecm11->device[cumulus02]->ztpsettings]% show

Parameter Value

------------------------------------ -----------------------------------------------
Revision

Script template cumulus-ztp.sh

JSON template

Image cumulus-linux-5.13.1-mlx-amd64.bin

Check image on boot yes

Run ZTP on each boot yes

Install lite daemon yes
Authorized key file root /root/.ssh/authorized_keys

Authorized key file cumulus

Authorized key file admin

Enable API no

Enable external access API no

Merge key value settings partition no

Key value settings <submode>

Firmwares

Preinstall scripts

Post-install scripts

PTM topology file


Notes about some of the ztpsettings :


**–** By default, authorizedkeyfileroot is not set, which means that user root cannot access the
switch with public key authentication.


**–** By default, authorizedkeyfilecumulus is not set. The user cumulus is the API user with
administrator privileges for the Cumulus switch.


**–** By default, authorizedkeyfileadmin is not set. The user admin is the API user with administrator privileges for the NVLink switch.


**–**
Cumulus images for the switch, set by image, are provisioned from the head node. Cumulus
images can be picked up from [https://enterprise-support.nvidia.com/s/downloads](https://enterprise-support.nvidia.com/s/downloads) and
can then be placed on the head node at /cm/local/apps/cmd/etc/htdocs/switch/images/ .


**–** The checkimageonboot setting checks that the existing image on the switch matches the image that can be offered via ZTP. If it does not, then the switch updates its image, picking it up
via ZTP.


**–**
The file specified by scripttemplate is used to generate a ZTP provisioning file on-demand
when the switch boots. Running initialize from the switch object level (at cumulus02 level
in the preceding example) generates the file without a reboot.


**–**
The file specified by PTM topology file describes the cabling topology.


**3.10 Configuring Cumulus Switches** **147**


  - The switchoverview command returns output such as:


[basecm11->device[cumulus01]]% switchoverview

Device: cumulus01

State : [ UP ]

Model : Cumulus Linux 5.2.1

Port Name Status Assigned Uplink Speed Detected

---- ------ ------- ------------ ------ ----------- ---------------------------
1 swp1 DOWN no 0 b/s bridge domains: cm-default
2 swp2 DOWN no 0 b/s bridge domains: cm-default
3 swp3 DOWN no 0 b/s bridge domains: cm-default
4 swp4 DOWN no 0 b/s bridge domains: cm-default
5 swp5 UP node001-dpu no 100 Gb/s bridge domains: cm-default
6 swp6 DOWN no 0 b/s bridge domains: cm-default
7 swp7 UP node002-dpu no 100 Gb/s bridge domains: cm-default


  - The switchports command (page 137) is used to configure the port assignment between the nodes
and the switch ports. Configuring the port assignment at interfaces level is needed to allow
CMDaemon Lite to manage Cumulus network configuration.


**Example**


[basecm11->device[node002]]% interfaces node004

[basecm11->device[node004]->interfaces]% set DPU1 switchports cumulus01:4


**Custom Services Option 2: Cumulus With A YAML Preconfiguration**
A YAML configuration can be used outside of cmsh . DGX SuperPODS use this option during the standard BCM installation. It means that CMDaemon Lite running on the switch (section 3.10.2) does not
need to be used. Instead, two custom-generated YAML files are used.
The YAML files that are generated are:


 - startup.yaml : this contains a sequence of Cumulus nv commands


 - cm-startup.yaml : this contains the BCM DGX/switch definitions to be added by pythoncm


The cm-startup.yaml file is parsed, and the devices that are defined within it are configured with
the PythonCM (Chapter 1 of the _Developer Manual_ ) script, cm-import-startup .
The devices are then powered on in the correct order.
The YAML file startup.yaml can be handled manually (using scp and the nv apply command), or
by using ZTP, or by using Ansible.


**Settings Applied Via ZTP**
The configuration script cumulus-ztp.sh template, found under /cm/local/apps/cmd/etc/htdocs/
switch/template, can be customized to suit the requirements.
The YAML file startup.yaml is placed under:


/cm/local/apps/cmd/etc/htdocs/switch/< _switch or host name_ >/


This allows it to be picked up automatically via ZTP, and the nv commands are applied it to the
switch on boot.

CMDaemon Lite is not required, but can be installed separately.


**Settings Applied Via Ansible**
Alternatively, Ansible can be used to push the YAML configuration to each switch.
With an Ansible installation, ZTP is not required, but it can be used. CMDaemon Lite is not required
for applying the settings via Ansible either, but can be installed separately.


**148** **Configuring The Cluster**


**3.10.3** **Uplink Ports**
Uplink ports are switch ports that are connected to other switches. CMDaemon must be told about any
switch ports that are uplink ports, or the traffic passing through an uplink port will lead to mistakes
in what CMDaemon knows about port and MAC correspondence. Uplink ports are thus ports that
CMDaemon is told to ignore.
To inform CMDaemon about what ports are uplink ports, Base View or cmsh are used:


  - In Base View, the switch is selected, and uplinks can be added via the navigation path
Devices   - Switches   - Edit   - Uplinks
(figure 3.16):


Figure 3.16: Notifying CMDaemon about uplinks with Base View


A dialog box then appears, and allows uplink port numbers to be added with a _⊕_ button. The
state is saved with the SAVE button of figure 3.16.


  - In cmsh, the switch is accessed from the device mode. The uplink port numbers can be appended
one-by-one with the append command, or set in one go by using space-separated numbers.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% set switch01 uplinks 15 16


**3.10 Configuring Cumulus Switches** **149**


[basecm11->device*]% set switch02 uplinks 01

[basecm11->device*]% commit

successfully committed 3 Devices


**3.10.4** **The** showport **MAC Address to Port Matching Tool**
The showport command can be used in troubleshooting network topology issues, as well as checking
and setting up new nodes (section 5.4.2).


**Basic Use Of** showport
In the device mode of cmsh is the showport command, which works out which ports on which switch
are associated with a specified MAC address.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% showport 00:30:48:30:73:92

switch01:12


When running showport, CMDaemon on the head node queries all switches until a match is found.
If a switch is also specified using the “ -s ” option, then the query is carried out for that switch first.
Thus the preceding example can also be specified as:


[basecm11->device]% showport -s switch01 00:30:49.00:73:92

switch01:12


If there is no port number returned for the specified switch, then the scan continues on other switches.


**Mapping All Port Connections In The Cluster With** showport
A list indicating the port connections and switches for all connected devices that are up can be generated
using this script:


**Example**


#!/bin/bash

for nodename in $(cmsh -c "device; foreach * (get hostname)")

do

macad=$(cmsh -c "device use $nodename; get mac")

echo -n "$macad $nodename "

cmsh -c "device showport $macad"

done


The script may take a while to finish its run. It gives an output like:


**Example**


00:00:00:00:00:00 switch01: No ethernet switch found connected to this mac address

00:30:49.00:73:92 basecm11: switch01:12

00:26:6C:F2:AD:54 node001: switch01:1

00:00:00:00:00:00 node002: No ethernet switch found connected to this mac address


**3.10.5** **Disabling Port Detection**
An administrator may wish to disable node identification based on port detection. For example, in the
case of switches with buggy firmware, the administrator may feel more comfortable relying on MACbased identification. Disabling port detection can be carried out by clearing the switchports setting of
a node, a category, or a group. For example, in cmsh, for a node:


**150** **Configuring The Cluster**


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% clear switchports

[basecm11->device*[node001*]]% commit

[basecm11->device[node001]]%


Or, for example for the default category, with the help of the foreach command:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]]% foreach -c default (clear switchports); commit


**3.10.6** **The** switchoverview **Command**

Also within device mode, the switchoverview command gives an overview of MAC addresses detected
on the ports, and some related properties. The command works using SNMP queries. Output is similar
to the following (some lines ellipsized):


[basecm11->device]% switchoverview dell-switch1

Device: dell-switch1

State : [ UP ]

Model : 24G Ethernet Switch


Port Assignment:


Port Status Assigned Uplink Speed Detected
------ ------ ---------------- ------ -------- -------------------------- _\_

-------------------------------------------------------------------
1 UP false 1 Gb/s 
2 UP false 1 Gb/s 
3 UP false 1 Gb/s 74:86:7A:AD:3F:2F, node3

4 UP false 1 Gb/s 74:86:7A:AD:43:E9, node4

...

11 UP false 1 Gb/s 74:86:7A:AD:44:D8, node11

12 UP false 1 Gb/s 74:86:7A:AD:6F:55, node12

...

23 UP false 1 Gb/s 74:86:7A:E9:3E:85, node23

24 UP false 1 Gb/s 74:86:7A:AD:56:DF, node24

49 UP false 10 Gb/s 74:86:7A:AD:68:FD, node1

50 UP false 10 Gb/s 74:86:7A:AD:41:A0, node2

53 UP node34 false 1 Gb/s 5C:F9:DD:F5:79.0D, node34

54 UP node35 false 1 Gb/s 5C:F9:DD:F5:45:AC, node35

...

179 UP false 1 Gb/s 24:B6:FD:F6:20:6F, _\_
24:B6:FD:FA:64:2F, 74:86:7A:DF:7E:4C, 90:B1:1C:3F:3D:A9, _\_

90:B1:1C:3F:51:D1, D0:67:E5:B7:64:0F, D0:67:E5:B7:61:20

180 UP false 100 Mb/s QDR-switch

205 UP true 10 Gb/s 
206 DOWN false 10 Gb/s 
...

[basecm11 ->device]%


**3.11 Configuring NetQ Network Management System** **151**


**3.11** **Configuring NetQ Network Management System**


NetQ telemetry data values are produced by NetQ. A running NetQ server can be integrated with BCM
by configuring its credentials and connectivity settings in the netqsettings submode from within the
partition mode of BCM:


**Example**


[basecm11->partition[base]]% netqsettings

[basecm11->partition*[base*]->netqsettings*]% show

Parameter Value

-------------------------------- -----------------------------------------------
Revision

Server

User name

Password < not set >

Port 443

Verify SSL no

[basecm11->partition*[base*]->netqsettings*]% set username <NetQ username>

[basecm11->partition*[base*]->netqsettings*]% set password <NetQ password>

[basecm11->partition*[base*]->netqsettings*]% set server <NetQ hostname or IP address>

[basecm11->partition*[base*]->netqsettings*]% commit


Connecting to the NetQ server allows NetQ telemetry data values to be picked up by BCM. These
values are then treated as measurables (section 10.2.1). NetQ measurables (sections G.1.13 and G.2.4)
can be managed and displayed with BCM just like other measurables.


**3.12** **Disk Layouts: Disked, Semi-Diskless, And Diskless Node Configuration**


Configuring the disk layout for head and regular nodes is done as part of the initial setup (section 3.3.16
of the _Installation Manual_ ). For regular nodes, the disk layout can also be re-configured by BCM once the
cluster is running. For a head node, however, the disk layout cannot be re-configured after installation
by BCM, and head node disk layout reconfiguration must then therefore be treated as a regular Linux
system administration task, typically involving backups and resizing partitions.
The remaining parts of this section on disk layouts therefore concern regular nodes, not head nodes.


**3.12.1** **Disk Layouts**
A disk layout is specified using an XML schema (Appendix D.1). The disk layout typically specifies
the devices to be used, its partitioning scheme, and mount points. Possible disk layouts include the
following:


  - Default layout (Appendix D.3)


  - Hardware RAID setup (Appendix D.4)


  - Software RAID setup (Appendix D.5)


  - LVM setup (Appendix D.7)


  - Diskless setup (Appendix D.9)


  - Semi-diskless setup (Appendix D.10)


**3.12.2** **Disk Layout Assertions**
Disk layouts can be set to _assert_


  - that particular hardware be used, using XML element tags such as vendor or requiredSize (Appendix D.11)


**152** **Configuring The Cluster**


  - custom assertions using an XML assert element tag to run scripts placed in CDATA sections
(Appendix D.12)


**3.12.3** **Changing Disk Layouts**
A disk layout applied to a category of nodes is inherited by default by the nodes in that category. A disk
layout that is then applied to an individual node within that category overrides the category setting.
This is an example of the standard behavior for categories, as mentioned in section 2.1.3.
By default, the cluster is configured with a standard layout specified in section D.3. The layouts
can be accessed from Base View or cmsh, as is illustrated by the example in section 3.12.4, which covers
changing a node from disked to diskless mode:


**3.12.4** **Changing A Disk Layout From Disked To Diskless**
The XML schema for a node configured for diskless operation is shown in Appendix D.9. This can often
be deployed as is, or it can be modified during deployment using Base View or cmsh as follows:


**Changing A Disk Layout Using Base View**
To change a disk layout with Base View, the current disk layout is accessed by selecting a node category
or a specific node from the resource tree in the navigation panel. For a node, the navigation path is
Devices - Nodes - Edit - Settings - Installing - Disk setup
(figure 3.17):


**3.12 Disk Layouts: Disked, Semi-Diskless, And Diskless Node Configuration** **153**


Figure 3.17: Changing a disked node to a diskless node with Base View


The Disk setup field can then be edited.
Clicking on the Select from template button shows several possible ready-made configurations
that can be loaded up from the CMDaemon database, and if desired, the copy stored for the node can


**154** **Configuring The Cluster**


be edited to suit the situation.

To switch from the existing disk layout to a diskless one, the diskless XML configuration template is
loaded via the Select from template button, and saved to the node or node category.
The Browse button can be used to upload a custom configuration via the browser, and there is also a
Copy from Category:default button that can be used to copy the category configuration to the node.


**Changing A Disk Layout Using** cmsh
To edit an existing disk layout from within cmsh, the existing XML configuration is accessed by editing
the disksetup property in device mode for a particular node, or by editing the disksetup property in
category mode for a particular category. Editing is done using the set command, which opens up a
text editor:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% set disksetup


After editing and saving the XML configuration, the change is then committed to CMDaemon with
the commit command. It should be understood that a disk layout XML configuration is not stored in a
file on the filesystem, but in the CMDaemon database. The XML configurations that exist on a default
cluster at

/cm/images/default-image/cm/local/apps/cmd/etc/htdocs/disk-setup/
and

/cm/local/apps/cmd/etc/htdocs/disk-setup/
are merely default configurations.
If the disksetup setting for a device is deleted, using the clear command, then the category level
disksetup property is used by the device. This is in accordance with the usual behavior for node values
that override category values (section 2.1.5).


Instead of editing an existing disk layout, another XML configuration can also be assigned. A diskless configuration may be chosen and set as follows:


**Example**


[basecm11->device[node001]]% set disksetup /cm/local/apps/cmd/ _\_
etc/htdocs/disk-setup/slave-diskless.xml


In these preceding Base View and cmsh examples, after committing the change and rebooting the
node, the node then functions entirely from its RAM, without using its own disk.
However, RAM is usually a scarce resource, so administrators often wish to optimize diskless nodes
by freeing up the RAM on them from the OS that is using the RAM. Freeing up RAM can be accomplished by providing parts of the filesystem on the diskless node via NFS from the head node. That is,
mounting the regular node with filesystems exported via NFS from the head node. The details of how to
do this are a part of section 3.13, which covers the configuration of NFS exports and mounts in general.


**3.13** **Configuring NFS Volume Exports And Mounts**


NFS allows unix NFS clients shared access to a filesystem on an NFS server. The accessed filesystem is
called an NFS volume by remote machines. The NFS server exports the filesystem to selected hosts or
networks, and the clients can then mount the exported volume locally.
An unformatted filesystem cannot be used. The drive must be partitioned beforehand with fdisk or
similar partitioning tools, and its filesystem formatted with mkfs or similar before it can be exported.


**3.13 Configuring NFS Volume Exports And Mounts** **155**


In BCM, the head node is typically used to export an NFS volume to the regular nodes, and the
regular nodes then mount the volume locally.


  - NFS can be made to work at higher speeds with remote direct memory access (RDMA), by bypassing the CPU. If there is RDMA hardware present, and if the rdma-core package is installed, then
the RDMA service works automatically in RHEL 8 and 9.


The settings that determine client module loading are set in the file /etc/rdma/modules/rdma.conf
so that the service auto-loads by default.


[• An alternative to NFS over RDMA for very fast file systems is the massively parallel and free](https://whamcloud.com)
[(GPLv2) Lustre filesystem, running over InfiniBand.](https://whamcloud.com)


If auto-mounting is used, then the configuration files for exporting should be set up on the NFS
server, and the mount configurations set up on the software images. The service “ autofs ” or the equivalent can be set up using Base View via the “ Services ” option (section 3.14) on the head and regular
nodes or node categories. With cmsh the procedure to configure auto-mounting on the head and regular
nodes could be:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use basecm11

[basecm11->device[basecm11]]% services

[basecm11->device[basecm11]->services]% add autofs

[basecm11->device*[basecm11*]->services*[autofs*]]% show

Parameter Value

------------------------------ ------------------------------------
Autostart no

Belongs to role no

Monitored no

Revision

Run if ALWAYS

Service autofs

Sickness check interval 60

Sickness check script

Sickness check script timeout 10

Timeout -1

[basecm11->device*[basecm11*]->services*[autofs*]]% set autostart yes

[basecm11->device*[basecm11*]->services*[autofs*]]% commit

[basecm11->device[basecm11]->services[autofs]]% category use default

[basecm11->category[default]]% services

[basecm11->category[default]->services]% add autofs

[basecm11->category*[default*]->services*[autofs*]]% set autostart yes

[basecm11->category*[default*]->services*[autofs*]]% commit

[basecm11->category[default]->services[autofs]]%


Filesystems imported to a regular node via an auto-mount operation must explicitly be excluded in
excludelistupdate by the administrator, as explained in section 5.6.1, page 280.
The rest of this section describes the configuration of NFS for static mounts, using Base View or cmsh .
Sections 3.13.1 and 3.13.2 explain how exporting and mounting of filesystems is done in general by an
administrator using Base View and cmsh, and considers some mounting behavior that the administrator
should be aware of.

Section 3.13.3 discusses how filesystems in general on a diskless node can be replaced via mounts of
NFS exports.
Section 3.13.4 discusses how OFED InfiniBand or iWarp drivers can be used to provide NFS over
RDMA.


**156** **Configuring The Cluster**


**3.13.1** **Exporting A Filesystem Using Base View And** cmsh

**Exporting A Filesystem Using Base View**
As an example, if an NFS volume exists at “ basecm11:/modeldata ” it can be exported using Base View
using the head node navigation path:
Devices - Head nodes [ basecm11 ] > Settings[JUMP TO] - Filesystem exports
This shows the list of exports (figure 3.18):


Figure 3.18: NFS exports from a head node viewed using Base View


Using the Add button, and selecting FSExport from the popup, a new entry (figure 3.19) can be
configured with values as shown:


**3.13 Configuring NFS Volume Exports And Mounts** **157**


Figure 3.19: Setting up an NFS export using Base View


For this example, the value for “ Name ” is set arbitrarily to “ Fluid Model Data ”, the value for Path
is set to /modeldata, and the value for Network is set from the selection menu to allowing access to
internalnet (by default 10.141.0.0/16 in CIDR notation).
By having the Write option disabled, read-only access is kept.
Saving this preceding configuration means the NFS server now provides NFS access to this filesystem for internalnet .

The network can be set to other network values using CIDR notation. It can also be set to particular
hosts such as just node001 and node002, by specifying a value of “ node001 node002 ” instead. Other
settings and options are also possible and are given in detail in the man pages for exports(5) .


**Exporting A Filesystem Using** cmsh
The equivalent to the preceding Base View NFS export procedure can be done in cmsh by using the
fsexports submode on the head node (some output elided):


**158** **Configuring The Cluster**


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use basecm11

[basecm11->device[basecm11]]% fsexports

[...->fsexports]% add "Fluid Model Data"

[...->fsexports*[Fluid Model Data*]]% set path /modeldata

[...[Fluid Model Data*]]% set hosts 10.141.0.0/16

[...[Fluid Model Data*]]% commit

[...->fsexports[Fluid Model Data]]% list | grep Fluid
Name (key) Path Hosts Write

------------------- ------------- --------------- -----
Fluid Model Data /modeldata 10.141.0.0/16 no


**General Considerations On Exporting A Filesystem**
**Built-in exports:** In versions of NVIDIA Base Command Manager prior to version 9.0, all filesystem
exports could be removed from the fsexports submode, simply by using the remove command with
the name of the export.
From version 9.0 onward however, the following filesystem exports:


 - /var/spool/burn


 - /home


 - /cm/shared


are treated as special built-ins.


**Head node role and** disableautomaticexports **:** Built-ins are exported automatically as part of the
headnode role, also introduced in NVIDIA Base Command Manager 9.0, and cannot simply be removed.
To disable export of the built-in file systems, the disableautomaticexports command must be run
in the headnode role for that node:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use basecm11

[basecm11->device[basecm11]]% roles

[basecm11->device[basecm11]->roles]% use headnode

[basecm11->device[basecm11]->roles[headnode]]% show

Parameter Value

-------------------------------- ----------------------
Name headnode

Revision

Type HeadNodeRole

Add services yes

Disable automatic exports no

Provisioning associations <2 internally used>

role use headnode

[basecm11->device[basecm11]->roles[headnode]]% set disableautomaticexports yes ; commit


**Disabling exports that are not built-ins:** Exports that are not built-ins can still simply be removed.
However, also from NVIDIA Base Command Manager 9.0 onward they can also simply be disabled in
the fsexports submode. For example there is an export created by the cluster administrator for /opt, it
can be disabled as follows:


**3.13 Configuring NFS Volume Exports And Mounts** **159**


**Example**


[basecm11->device[basecm11]->fsexports]% list
Name (key) Path Network Disabled

---------------- ------- ... ----------- -------
opt /opt internalnet no

[basecm11->device[basecm11]->fsexports]% set opt disabled yes; commit


The reason for automating the export for nodes via a headnode role is that NVIDIA Base Command Manager 9.0 onward has multidistro and multiarch capabilities (section 9.7), which would
make manual management of exports harder for such nodes. The reason for the extra hurdle of
disableautomaticexports for built-ins is that that disabling these exports can result in an unbootable
system.


**3.13.2** **Mounting A Filesystem Using Base View And** cmsh
Continuing on with the Fluid Model Data export example from the preceding section, the administrator decides to mount the remote filesystem over the default category of nodes. Nodes can also mount
the remote filesystem individually, but that is usually not a common requirement in a cluster. The administrator also decides not to re-use the exported name from the head node. That is, the remote mount
name modeldata is not used locally, even though NFS allows this and many administrators prefer to do
this. Instead, a local mount name of /modeldatagpu is used, perhaps because it avoids confusion about
which filesystem is local to a person who is logged in, and perhaps to emphasize the volume is being
mounted by nodes with GPUs.


**Mounting A Filesystem Using Base View**
In Base View the navigation path to manage the mount points of a category such as default is:
Grouping  - Categories [default] > Edit  - Settings[JUMP TO]  - Filesystem mounts


A mount point can be added with the ADD button, and clicking on the popup FSMount . Values for
the remote mount point ( basecm11:/modeldata ), the filesystem type ( nfs ), and the local mount point
( /modeldatagpu ) can then be set in category mode, while the remaining options stay at their default
values (figure 3.20):


**160** **Configuring The Cluster**


Figure 3.20: Setting up NFS mounts on a node category using Base View


Saving the configuration saves the values and creates the local mount point, so that the volume can
then be accessed by nodes within that category.


**Mounting A Filesystem Using** cmsh
The equivalent to the preceding Base View NFS mount procedure can be done in cmsh by using the
fsmounts submode, for example on the default category. The add method under the fsmounts submode
sets the mountpoint path, in this case /modeldatagpu (some output elided):


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% category use default

[basecm11->category[default]]% fsmounts

[basecm11->category[default]->fsmounts]% add /modeldatagpu

[basecm11->...*[/modeldatagpu*]]% set device basecm11:/modeldata

[basecm11->...*[/modeldatagpu*]]% set filesystem nfs

[basecm11->category*[default*]->fsmounts*[/modeldatagpu*]]% commit

[basecm11->category[default]->fsmounts[/modeldatagpu]]%
Device Mountpoint (key) Filesystem

--------------------- ------------------ ---------
...

basecm11:/modeldata /modeldatagpu nfs

[basecm11->category[default]->fsmounts[/modeldatagpu]]% show

Parameter Value

------------------- --------------------
Device basecm11:/modeldata


**3.13 Configuring NFS Volume Exports And Mounts** **161**


Dump no

Filesystem nfs

Filesystem Check NONE

Mount options defaults
Mountpoint /modeldatagpu


Values can be set for Mount options other than default. For example, the noac flag can be added as
follows:


[basecm11->...[/modeldatagpu]]% set mountoptions defaults,noac; commit


Mounting a CIFS might use:


[basecm11->...[/modeldatagpu]]% set mountoptions gid,users,file_mode=0666,dir_mode=0777, _\_
iocharset=iso8859-15,credentials=/path/to/credential

[basecm11->...[/modeldatagpu*]]% commit


A _netdev mount option to make systemd wait until the network is up before it is mounted can be
added as follows:


[basecm11->...[/modeldatagpu]]% append mountoptions,_netdev; commit


**General Considerations On Mounting A Filesystem**
There may be a requirement to segregate the access of nodes. For example, in the case of the preceding,
because some nodes have no associated GPUs.

Besides the “ Allowed hosts ” options of NFS exports mentioned earlier in section 3.13.1, BCM offers
two more methods to fine tune node access to mount points:


  - Nodes can be placed in another category that does not have the mount point.


  - Nodes can have the mount point set, not by category, but per device within the Nodes resource.
For this, the administrator must ensure that nodes that should have access have the mount point
explicitly set.


Other considerations on mounting are that:


  - When adding a mount point object:


**–**
The settings take effect right away by default on the nodes or node categories.


**–** If noauto is set as a mount option, then the option only takes effect on explicitly mounting
the filesystem.


**–** If “ AutomaticMountAll=0 ” is set as a CMDaemon directive (Appendix C), then CMDaemon
changes for /etc/fstab are written to the file, but the mount -a command is not run by
CMDaemon. However, the administrator should be aware that since mount -a is run by the
distribution during booting, a node reboot implements the mount change.


  - While a mount point object may have been removed, umount does not take place until reboot,
to prevent mount changes outside of the cluster manager. If a umount needs to be to done without a reboot, then it should be done manually, for example, using the pdsh or pexec command
(section 14.1), to allow the administrator to take appropriate action if umounting goes wrong.


  - When manipulating mount points, the administrator should be aware which mount points are
inherited by category, and which are set for the individual node.


**–** In Base View, for a node, inheritance by category is indicated in the navigation path Devices
    - Nodes[ _node name_ ]     - Edit     - Settings     - Filesystem mounts, under the INHERITED column,
with the entry (Category) .


**162** **Configuring The Cluster**


**–** In cmsh, the category a mount belongs to is displayed in brackets. This is displayed from
within the fsmounts submode of the device mode for a specified node:


**Example**


[root@basecm11 ~]# cmsh -c "device; fsmounts node001; list"


Device Mountpoint (key) Filesystem

------------------------ -------------------- ---------
[default] none /dev/pts devpts

[default] none /proc proc

[default] none /sys sysfs

[default] none /dev/shm tmpfs

[default] $localnfsserv+ /cm/shared nfs

[default] basecm11:/home /home nfs

basecm11:/cm/shared/exa+ /home/examples nfs

[root@basecm11 ~]#


To remove a mount point defined at category level for a node, it must be removed from within the
category, and not from the specific node.


**Mount Order Considerations**

Care is sometimes needed in deciding the order in which mounts are carried out.


  - For example, if both /usr/share/doc and a replacement directory subtree /usr/share/doc/
compat-gcc-34-3.4.6java are to be used, then the stacking order should be that /usr/share/doc
is mounted first. This order ensures that the replacement directory subtree overlays the first
mount. If, instead, the replacement directory were the first mount, then it would be overlaid,
inaccessible, and inactive.


  - There may also be dependencies between the subtrees to consider, some of which may prevent
the start up of applications and services until they are resolved. In some cases, resolution may be
quite involved.


The order in which such mounts are mounted can be modified with the up and down commands
within the fsmounts submode of cmsh .


**3.13.3** **Mounting A Filesystem Subtree For A Diskless Node Over NFS**

**NFS Vs** tmpfs **For Diskless Nodes**
For diskless nodes (Appendix D.9), the software image (section 2.1.2) is typically installed from a provisioning node by the node-installer during the provisioning stage, and held as a filesystem in RAM on
the diskless node with the tmpfs filesystem type.
It can be worthwhile to replace subtrees under the diskless node filesystem held in RAM with subtrees provided over NFS. This can be particularly worthwhile for less frequently accessed parts of the
diskless node filesystem. This is because, although providing the files over NFS is much slower than accessing it from RAM, it has the benefit of freeing up RAM for tasks and jobs that run on diskless nodes,
thereby increasing the cluster capacity.
An alternative “semi-diskless” way to free up RAM is to use a local disk on the node itself for supplying the subtrees. This is outlined in Appendix D.10.


**Moving A Filesystem Subtree Out Of** tmpfs **To NFS**
To carry out subtree provisioning over NFS, the subtrees are exported and mounted using the methods
outlined in the previous examples in sections 3.13.1 and 3.13.2. For the diskless case, the exported
filesystem subtree is thus a particular path under /cm/images/<image> [2] on the provisioning node, and
the subtree is mounted accordingly under / on the diskless node.


2 by default _<image>_ is default-image on a newly-installed cluster


**3.13 Configuring NFS Volume Exports And Mounts** **163**


While there are no restrictions placed on the paths that may be mounted in NVIDIA Base Command
Manager 11, the administrator should be aware that mounting certain paths such as /bin is not possible.
When Base View or cmsh are used to manage the NFS export and mount of the subtree filesystem,
then tmpfs on the diskless node is reduced in size due to the administrator explicitly excluding the
subtree from tmpfs during provisioning.
An example might be to export /cm/images/default-image from the head node, and mount the
directory available under it, usr/share/doc, at a mount point /usr/share/doc on the diskless node. In
cmsh, such an export can be done by creating an FS export object corresponding to the software image
object defaultimage with the following indicated properties (some prompt output elided):


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use basecm11; fsexports

[basecm11->device[basecm11]->fsexports]% add defaultimage

[basecm11...defaultimage*]]% set path /cm/images/default-image

[basecm11...defaultimage*]]% set hosts 10.141.0.0/16

[basecm11...defaultimage*]]% commit

[basecm11...defaultimage]]% list | grep defaultimage
Name (key) Path Hosts Write

---------------- ------------------------ ------------- ----
defaultimage /cm/images/default-image 10.141.0.0/16 no


As the output to list shows, the NFS export should be kept read-only, which is the default. Appropriate parts of the export can then be mounted by a node or node category. The mount is defined
by setting the mount point, the nfs filesystem property, and the export device. For example, for a node
category (some output elided):


[br...defaultimage]]% category use default

[basecm11->category[default]]% fsmounts

[basecm11->category[default]->fsmounts]% add /usr/share/doc

[basecm11->...*[/usr/share/doc*]]% set device basecm11:/cm/images/default-image/user/share/doc

[basecm11->...*[/usr/share/doc*]]% set filesystem nfs

[basecm11->category*[default*]->fsmounts*[/usr/share/doc*]]% commit

[basecm11->category[default]->fsmounts[/usr/share/doc]]% list
Device Mountpoint (key) Filesystem

--------------------- ------------------ ---------
... ... ...

basecm11:/cm/images/usr/share/doc /usr/share/doc nfs

[basecm11->category[default]->fsmounts[/usr/share/doc]]% show

Parameter Value

---------------- ----------------------------------------------
Device basecm11:/cm/images/default-image/usr/share/doc

Dump no

Filesystem nfs

Filesystem Check 0

Mount options defaults
Mountpoint /usr/share/doc


Other mount points can be also be added according to the judgment of the system administrator.
Some consideration of mount order may be needed, as discussed on page 162 under the subheading
“Mount Order Considerations”.


**An Example Of Several NFS Subtree Mounts**
The following mounts save about 440MB from tmpfs on a diskless node with Rocky Linux 8, as can be
worked out from the following subtree sizes:


**164** **Configuring The Cluster**


[root@basecm11 ~]# cd /cm/images/default-image/

[root@basecm11 default-image]# du -sh usr/share/locale usr/lib/jvm usr/share/doc usr/src

160M usr/share/locale

118M usr/lib/jvm

88M usr/share/doc

77M usr/src


The filesystem mounts can then be created using the techniques in this section. After doing that, the
result is then something like (some lines omitted):


[root@basecm11 default-image]# cmsh

[basecm11]% category use default; fsmounts

[basecm11->category[default]->fsmounts]% list -f device:53,mountpoint:17
device mountpoint (key)

-------------------------------------------------- ----------------
... ...

master:/cm/shared /cm/shared

master:/home /home

basecm11:/cm/images/default-image/usr/share/locale /usr/share/locale
basecm11:/cm/images/default-image/usr/lib/jvm /usr/lib/jvm
basecm11:/cm/images/default-image/usr/share/doc /usr/share/doc
basecm11:/cm/images/default-image/usr/src /usr/src

[basecm11->category[default]->fsmounts]%


Diskless nodes that have NFS subtree configuration carried out on them can be rebooted to start
them up with the new configuration.


**3.13.4** **Configuring NFS Volume Exports And Mounts Over RDMA With OFED Drivers**
If running NFS over RDMA, then at least NFS version 4.0 is recommended. NFS version 3 will also
work with RDMA, but uses IPoIB encapsulation instead of native verbs. NFS version 4.1 uses the RDMA
Connection Manager ( librdmacm ), instead of the InfiniBand Connection Manager ( ib_cm ) and is thereby
also able to provide pNFS.
The administrator can set the version of NFS used by the cluster by setting the value of Nfsvers in
the file /etc/nfsmount.conf on all the nodes, including the head node.


**Drivers To Use For NFS Over RDMA**

The DOCA Mellanox OFED drivers (chapter 10 of the _Installation Manual_ ) can support using the RDMA
protocol (section 3.6) to provide NFS.
The distribution OFED drivers also support NFS over RDMA.
When using NFS over RDMA, ibnet, the IP network used for InfiniBand, should be set. Section 3.6.3
explains how that can be done.


**Exporting With Base View And** cmsh **Using NFS Over RDMA**
With the drivers installed, a volume export can be carried out using NFS over RDMA.
The procedure using Base View is much the same as done in section 3.13.1 (“Exporting A Filesystem Using Base View”), except for that the ibnet network should be selected instead of the default
internalnet, and the “ RDMA ” option should be enabled.
The procedure using cmsh is much the same as done in section 3.13.1 (“Exporting A Filesystem Using
cmsh ”), except that the ibnet network (normally with a recommended value of 10.149.0.0/16) should be
set, and the rdma option should be set.


**Example**


(based on the example in section 3.13.1)


**3.14 Managing And Configuring Services** **165**


...

[...->fsexports*[Fluid Model Data*]]% set path /modeldata

[...[Fluid Model Data*]]% set hosts ibnet

[...[Fluid Model Data*]]% set rdma yes

[...[Fluid Model Data*]]% commit

...


**Mounting With Base View And** cmsh **Using NFS Over RDMA**
The mounting of the exported filesystems using NFS over RDMA can then be done.
The procedure using Base View is largely like that in section 3.13.2, (“Mounting A Filesystem Using
Base View”), except that the Device entry must point to master.ib.cluster so that it resolves to the
correct NFS server address for RDMA, and the checkbox for NFS over RDMA must be ticked.
The procedure using cmsh is similar to that in section 3.13.2, (“Mounting A Filesystem Using cmsh ”),
except that device must be mounted to the ibnet, and the rdma option must be set, as shown:


**Example**


(based on the example in section 3.13.2)


...

[basecm11->category[default]->fsmounts]% add /modeldatagpu

[basecm11->...*[/modeldatagpu*]]% set device basecm11.ib.cluster:/modeldata

[basecm11->...*[/modeldatagpu*]]% set filesystem nfs

[basecm11->...*[/modeldatagpu*]]% set rdma yes

[basecm11->category*[default*]->fsmounts*[/modeldatagpu*]]% commit

...


**3.14** **Managing And Configuring Services**


**3.14.1** **Why Use The Cluster Manager For Services?**
Linux administrators should be familiar with managing services from the command line using systemctl :


**Example**


systemctl start < _service~name_ >.service


where _<service name>_ indicates a service such as mysqld, mariabd, nfs, postfix and so on.
Services can also be managed with BCM. That is, they can also be started and stopped with Base
View and cmsh tools.

An additional convenience that comes with the cluster manager tools is that some CMDaemon parameters useful for managing services in a cluster are very easily configured, whether on the head node,
a regular node, or for a node category. These parameters are:


 - monitored : checks periodically if a service is running. Information is displayed and logged the
first time it starts or the first time it dies


 - autostart : restarts a failed service that is being monitored .


**–** If autostart is set to on, and a service is stopped using BCM, then no attempts are made
to restart the service. Attempted autostarts become possible again only after BCM starts the
service again.


**–** If autostart is set to on, and if a service is removed using BCM, then the service is stopped
before removal.


**–** If autostart is off, then a service that has not been stopped by CMDaemon still undergoes
an attempt to restart it, if


**166** **Configuring The Cluster**


       - [CMDaemon is restarted]


       - [its configuration files are updated by CMDaemon, for example in other modes, as in the]
example on page 99.


 - runif : (only honored for nodes used as part of a high availability configuration (chapter 15))
whether the service should run with a state of:


**–** active : run on the active node only


**–**
passive : run on the passive only


**–**
always : run both on the active and passive


**–**
preferpassive : preferentially run on the passive if it is available. Valid only for head nodes.
Invalid for failover groups (section 15.5.3).


The details of a service configuration remain part of the configuration methods of the service software itself.


  - Thus BCM can run actions on typical services only at the generic service level to which all the unix
services conform. This means that CMDaemon can run actions such as starting and stopping the
service. If the restarting action is available in the script, then CMDaemon can also run that.


  - The operating system configuration of the service itself, including its persistence on reboot, remains under control of the operating system, and is not handled by CMDaemon. So, stopping a
service within CMDaemon means that by default the service may start up on reboot. Running


systemctl disable < _service name>_ .service


from the command line can be used to configure the service to no longer start up on reboot.


BCM can be used to keep a service working across a failover event with an appropriate runif setting and appropriate failover scripts such as the Prefailover script and the Postfailover script
(section 15.4.6). The details of how to do this will depend on the service.


**3.14.2** **Managing And Configuring Services—Examples**
If, for example, the CUPS software is installed (“ yum install cups ”), then the CUPS service can be
managed in several ways:


**Managing The Service From The Regular Shell, Outside Of CMDaemon**
Standard unix commands from the bash prompt work, as shown by this session:


[root@basecm11 ~]# systemctl enable cups.service

... symlinks created...

[root@basecm11 ~]# systemctl start cups


**Managing The Service From** cmsh
**Starting the service in** cmsh **:** The following session illustrates adding the CUPS service from within
device mode and the services submode. The device in this case is a regular node, node001, but a head
node can also be chosen. Monitoring and auto-starting are also set in the session (some lines elided):


[basecm11]% device services node001

[basecm11->device[node001]->services]% add cups

[basecm11->device*[node001*]->services*[cups*]]% show

Parameter Value

------------------------------ -----------------------
Autostart no

Belongs to role no

Monitored no


**3.14 Managing And Configuring Services** **167**


...

Run if ALWAYS

Service cups

...

[basecm11->device*[node001*]->services*[cups*]]% set monitored on

[basecm11->device*[node001*]->services*[cups*]]% set autostart on

[basecm11->device*[node001*]->services*[cups*]]% commit

[basecm11->device[node001]->services[cups]]%
Apr 14 14:02:16 2017 [notice] node001: Service cups was started

[basecm11->device[node001]->services[cups]]%


**Other service options in** cmsh **:** Within cmsh, the start, stop, restart, and reload options to the
service < _service name_  - start|stop|restart|...
command can be used to manage the service at the services submode level. For example, continuing with the preceding session, stopping the CUPS service can be done by running the cups service
command with the stop option as follows:


[basecm11->device[node001]->services[cups]]% stop
Fri Apr 14 14:03:40 2017 [notice] node001: Service cups was stopped

Successfully stopped service cups on: node001

[basecm11->device[node001]->services[cups]]%


The service is then in a STOPPED state according to the status command.


[basecm11->device[node001]->services[cups]]% status
cups [STOPPED]


Details on how a state is used when monitoring a service are given in the section “Monitoring A
Service With cmsh And Base View” on page 170.
Continuing from the preceding session, the CUPS service can also be added for a node category from
category mode:


[basecm11->device[node001]->services[cups]]% category

[basecm11->category]% services default

[basecm11->category[default]->services]% add cups


As before, after adding the service, the monitoring and autostart parameters can be set for the service.
Also as before, the options to the service < _service name_ - start|stop|restart|... command can
be used to manage the service at the services submode level. The settings apply to the entire node
category (some lines elided):


**Example**


[basecm11->category*[default*]->services*[cups*]]% show

...

[basecm11->category*[default*]->services*[cups*]]% set autostart yes

[basecm11->category*[default*]->services*[cups*]]% set monitored yes

[basecm11->category*[default*]->services*[cups*]]% commit

[basecm11->category[default]->services[cups]]%
Fri Apr 14 14:06:27 2017 [notice] node002: Service cups was started
Fri Apr 14 14:06:27 2017 [notice] node005: Service cups was started
Fri Apr 14 14:06:27 2017 [notice] node004: Service cups was started
Fri Apr 14 14:06:27 2017 [notice] node003: Service cups was started

[basecm11->category[default]->services[cups]]% status
node001.................. cups [STOPPED ]
node002.................. cups [ UP ]
node003.................. cups [ UP ]
node004.................. cups [ UP ]
node005.................. cups [ UP ]


**168** **Configuring The Cluster**


**Managing The Service From Base View**
Using Base View, a service can be managed from an OSServiceConfig list window, accessible via the
Services button from the JUMP TO section of the Settings . The window is accessible for


 - Head Nodes, for example via a navigation path of
Devices   - Head Nodes[basecm11]   - Settings   - Services


 - Nodes, for example via a navigation path of
Devices   - Nodes[node001]   - Settings   - Services
(figure 3.21):


Figure 3.21: Operating system service configuration list window for nodes in Base View


 - Node categories, for example via a navigation path of
Grouping   - Node categories[default]   - Settings   - Services


By default, with the default software image, there are no services set at category level for nodes
(figure 3.22):


Figure 3.22: Operating system service configuration list window for the default category in Base View


The Service < _service name_  - start|stop|restart... command options start, stop, restart, and
so on, are displayed as selection options to an OSService popup that appears when the ACTIONS button
is clicked (figure 3.23):


**3.14 Managing And Configuring Services** **169**


Figure 3.23: Operating system service actions in Base View


A service can be added with the ADD button, and clicking on the OSServiceConfig popup. The fields
of the service can then be edited. The REVERT button reverts unsaved changes, while the DELETE button
removes the saved changes.
Figure 3.24 shows CUPS being set up from an Add dialog in the services window. The window is
accessible via the ADD button of figure 3.22.


**170** **Configuring The Cluster**


Figure 3.24: Setting up a service using Base View


For a service in the services subwindow, clicking on the Status button in figure 3.22 displays a grid
of the state of services on a running node as either Up or Down .


**Monitoring A Service With** cmsh **And Base View**
The service is in a DOWN state if it is not running, and in a FAILING state if it is unable to run after 10 autostarts in a row. Event messages are sent during these first 10 auto-starts. After the first 10 auto-starts, no
more event messages are sent, but autostart attempts continue.
In case an autostart attempt has not yet restarted the service, the reset option may be used to attempt
an immediate restart. The reset option is not a service option in the regular shell, but is used by
CMDaemon (within cmsh and Base View) to clear a FAILING state of a service, reset the attempted autostarts count to zero, and attempt a restart of the service.
The monitoring system sets the ManagedServicesOk health check (Appendix G.2.1) to a state of FAIL
if any of the services it monitors is in the FAILING state. In cmsh, the statuses of the services are listed by
running the latesthealthdata command (section 10.6.3) from device mode.
Standard init.d script behavior is that the script return a non-zero exit code if the service is down,
and a zero exit code if the service is up. A non-zero exit code makes BCM decide that the service is
down, and should be restarted.
However, some scripts return a non-zero exit code even if the service is up. These services therefore
have BCM attempt to start them repetitively, even though they are actually running.
This behavior is normally best fixed by setting a zero exit code for when the service is up, and a
non-zero exit code for when the service is down.


**3.15 Managing And Configuring A Rack** **171**


**Removing A Service From CMDaemon Control Without Shutting It Down**
Removing a service from BCM control while autostart is set to on stops the service on the nodes:


[basecm11->category[default]->services]% add cups

[basecm11->category*[default*]->services*[cups*]]% set monitored on

[basecm11->category*[default*]->services*[cups*]]% set autostart on

[basecm11->category*[default*]->services*[cups*]]% commit; exit

[basecm11->category[default]->services]% remove cups; commit
Wed May 23 12:53:58 2012 [notice] node001: Service cups was stopped


In the preceding cmsh session, cups starts up when the autostart parameter is committed, if cups is
not already up.
The behavior of having the service stop on removal is implemented because it is usually what is
wanted.

However, sometimes the administrator would like to remove the service from CMDaemon control
without it shutting down. To do this, autostart must be set to off first.


[basecm11->category[default]->services]% add cups

[basecm11->category*[default*]->services*[cups*]]% set monitored on

[basecm11->category*[default*]->services*[cups*]]% set autostart off

[basecm11->category*[default*]->services*[cups*]]% commit; exit
Wed May 23 12:54:40 2012 [notice] node001: Service cups was started

[basecm11->category[default]->services]% remove cups; commit

[basecm11->category[default]->services]% !# no change: cups stays up


**3.15** **Managing And Configuring A Rack**


**3.15.1** **Racks**

A cluster may have local nodes grouped physically into racks. A rack is 42 units in height by default,
and nodes normally take up one unit.


**Rack List**

**Rack list in Base View:** The Rack list pane can be opened up in Base View via the navigation path
Datacenter Infrastructure - Racks (figure 3.25):


Figure 3.25: Rack list using Base View


Racks can then be added, removed, or edited from the pane.
Within the Rack list pane:


  - a new rack item can be added with the ADD button, and then clicking on the Rack popup. This
opens a Settings tab in the rack item window pane where rack configuration can be carried out
and saved (figure 3.26).


  - an existing rack item can be edited with the Edit menu option, or by double-clicking on the item
itself. This also opens up the Settings tab in the rack item window pane where rack configuration
can be managed.


**172** **Configuring The Cluster**


**Racks overviews in** cmsh **:**


  - The list command in rack mode in cmsh allows racks defined in the cluster manager to be listed:


[basecm11->rack]% list

Name (key) Room x-Coordinate y-Coordinate Height

-------------- ------------- ------------- ------------- -----
rack2 skonk works 2 0 42

racknroll 1 0 42


  - The rackoverview command displays information about the types of entities in a specified rack.
It also lists some more detailed information about some of the entity types:


**Example**


[basecm11->rack]% rackoverview _<TAB><TAB>_

a01 a02 a03 a04 a05 a06 a07 a08 a09 a10 a11 a12 b01 b02 b03 b04...

[basecm11->rack]% rackoverview a05

Type Up Down Closed Total

----------------- --------------- --------------- --------------- --------------
Nodes 18 0 0 18

DPU nodes 0 0 0 0

Managed switches 0 0 0 0

NVLink switches 0 9 0 9

Power shelves 8 0 0 8

Devices 0 0 0 0

Cores 2,592   -   - 2,592

GPUs 72   -   - 72


Name Value

--------------------------- ----------------
User CPU 0.03%

System CPU 0.07%

Idle CPU 99.9%

Other CPU 0.0%

Memory used 1.28 TiB (4.53%)
Memory unused 27.4 TiB (96.6%)

Memory total 28.3 TiB

Total GPU utilization 0 W

Total GPU power usage 10.9 KW

Total GPU NVlink bandwidth 0 W

Average GPU temperature 30.5588 C


Node GPU Utilization Temperature Power usage Memory used Memory free Fabric status

------------------ ---- ------------ ------------ ------------ ------------ ------------ ------------
a05-p1-dgx-01-c01 gpu0 0.0% 30 C 166.551 W 0 B 185 GiB success
a05-p1-dgx-01-c01 gpu1 0.0% 30 C 158.166 W 1.00 MiB 185 GiB success

...


Switch Utilization Temperature Power usage Fan speed Links active Links inactive

--------------- ------------ ------------ ------------ ------------ ------------ -------------
a05-p1-nvsw-01 35.7% 0 C 0 W 0 RPM 0 0
a05-p1-nvsw-02 26.9% 0 C 0 W 0 RPM 0 0

...


**3.15 Managing And Configuring A Rack** **173**


Power Input Output Fan Active Total

shelf power power Temperature speed PSU PSU

--------------- -------- -------- ---------- --------- ------- -----
a05-p1-pwr-01 0 W 0 W 0 C 0 RPM 0 6

a05-p1-pwr-02 0 W 0 W 0 C 0 RPM 0 6

...

[basecm11->rack]%


  - The display command in rack mode is useful for visualizing where devices are located in the
rack, if the cluster administrator has recorded the device positions


**Example**


[basecm11->rack]% display |less -R

...

A05 B05


48 48

47 47

46 46

45 45

44 44

43 43

42 a05-p1-pwr-08 42 B05-P1-PWR-08

41 a05-p1-pwr-07 41 B05-P1-PWR-07

40 a05-p1-pwr-06 40 B05-P1-PWR-06

39 a05-p1-pwr-05 39 B05-P1-PWR-05

38 38

37 a05-p1-dgx-01-c18 37 b05-p1-dgx-05-c18

36 a05-p1-dgx-01-c17 36 b05-p1-dgx-05-c17

35 a05-p1-dgx-01-c16 35 b05-p1-dgx-05-c16

34 a05-p1-dgx-01-c15 34 b05-p1-dgx-05-c15

33 a05-p1-dgx-01-c14 33 b05-p1-dgx-05-c14

32 a05-p1-dgx-01-c13 32 b05-p1-dgx-05-c13

31 a05-p1-dgx-01-c12 31 b05-p1-dgx-05-c12

30 a05-p1-dgx-01-c11 30 b05-p1-dgx-05-c11

29 a05-p1-dgx-01-c10 29 b05-p1-dgx-05-c10

28 a05-p1-dgx-01-c09 28 b05-p1-dgx-05-c09

27 a05-p1-nvsw-09 27 B05-P1-NVSW-09

26 a05-p1-nvsw-08 26 B05-P1-NVSW-08

25 a05-p1-nvsw-07 25 B05-P1-NVSW-07

24 a05-p1-nvsw-06 24 B05-P1-NVSW-06

23 a05-p1-nvsw-05 23 B05-P1-NVSW-05

22 a05-p1-nvsw-04 22 B05-P1-NVSW-04

21 a05-p1-nvsw-03 21 B05-P1-NVSW-03

20 a05-p1-nvsw-02 20 B05-P1-NVSW-02

19 a05-p1-nvsw-01 19 B05-P1-NVSW-01

18 a05-p1-dgx-01-c08 18 b05-p1-dgx-05-c08

17 a05-p1-dgx-01-c07 17 b05-p1-dgx-05-c07

16 a05-p1-dgx-01-c06 16 b05-p1-dgx-05-c06

15 a05-p1-dgx-01-c05 15 b05-p1-dgx-05-c05

14 a05-p1-dgx-01-c04 14 b05-p1-dgx-05-c04

13 a05-p1-dgx-01-c03 13 b05-p1-dgx-05-c03

12 a05-p1-dgx-01-c02 12 b05-p1-dgx-05-c02

11 a05-p1-dgx-01-c01 11 b05-p1-dgx-05-c01


**174** **Configuring The Cluster**


10 10

09 a05-p1-pwr-04 09 B05-P1-PWR-04

08 a05-p1-pwr-03 08 B05-P1-PWR-03

07 a05-p1-pwr-02 07 B05-P1-PWR-02

06 a05-p1-pwr-01 06 B05-P1-PWR-01

05 05

04 04

03 03

02 02

01 01


Other rack overview commands allow the electrical supply, liquid cooling, leak detection, and leak
detection-related actions to be viewed at rack level (section 3.3 of the _NVIDIA Mission Control Manual_ ).


**Rack Configuration Settings**
**Rack configuration settings in Base View:** A Settings tab for editing a rack item selected from the
Rack list pane is shown in figure 3.26.


Figure 3.26: Rack configuration settings using Base View


Among the rack configuration attributes are:


**3.15 Managing And Configuring A Rack** **175**


 - Name : A unique name for the rack item. Names such as rack001, rack002 are a sensible choice.


 - Room : A unique name for the room the rack is in.


 - Position : The _x_  - and _y_ -coordinates of the rack in a room. These coordinates are meant to be a
hint for the administrator about the positioning of the racks in the room, and as such are optional,
and can be arbitrary numbers. The Notes field can be used as a supplement or as an alternative
for hints.


 - Height : by default this is the standard rack size of 42U.


 - Inverted : Normally, a rack uses the number 1 to mark the top and 42 to mark the bottom position
for the places that a device can be positioned in a rack. However, some manufacturers invert this
and use 1 to mark the bottom instead. Enabling the Inverted setting records the numbering layout
accordingly for all racks, if the inverted rack is the first rack seen in Rackview .


**Rack configuration settings in** cmsh **:** In cmsh, tab-completion suggestions for the set command in
rack mode display the racks available for configuration. On selecting a particular rack (for example,
rack2 as in the following example), tab-completion suggestions then display the configuration settings
available for that rack:


**Example**


[basecm11->rack]% set rack

rack1 rack2 rack3

[basecm11->rack]% set rack2

angle inverted notes twin y-coordinate

building location revision type

depth model room width

height name row x-coordinate


The configuration settings for a particular rack obviously match with the parameters associated with
and discussed in figure 3.26.
Setting the values can be done as in this example:


**Example**


[basecm11->rack]% use rack2

[basecm11->rack[rack2]]% set room "skonk works"

[basecm11->rack*[rack2*]]% set x-coordinate 2

[basecm11->rack*[rack2*]]% set y-coordinate 0

[basecm11->rack*[rack2*]]% set inverted no

[basecm11->rack*[rack2*]]% commit

[basecm11->rack[rack2]]%


**3.15.2** **Assigning Devices To A Rack**
Devices such as nodes, switches, and chassis, can be assigned to racks.
By default, no such devices are assigned to a rack.
Devices can be assigned to a particular rack and to a particular position within the rack as follows:


**Assigning Devices To A Rack Using Base View**
Using Base View, a device such as a node node001 can be assigned to a rack via the navigation path
Devices - Nodes[node001] - Settings - JUMP TO - Rack (figure 3.27):


**176** **Configuring The Cluster**


Figure 3.27: Rack assignment using Base View


**Assigning Devices To A Rack Using** cmsh

  - In device mode, nodes can be assigned to a position in a rack. For example:


**–** node001 to position 1


**–** node002 to position 2


**–** node003 to position 3


A looping instruction to do this in a rack rack2 is:


root@basecm11:~# for i in 1..3 ; do cmsh -c "device use node00$i; get hostname; set rack rack2; _\_
get rack; set deviceposition $i; get deviceposition; commit"; done


  - The addrackposition command fills devices into a rack object more implicitly. By default the
command fills devices into the first free slots on the rack.


root@basecm11:~# cmsh-c "device; addrackposition -n node001.node010 --position 1 rack rack2


The first free deviceposition value that it uses can be set with the --position option. Forcing a
device into the the same position as another device is also possible, with the --force option.


More options can be found using the help text for the command.


[basecm11->device]% help addrackposition

Name:

addrackposition - Add a rack position information to one or more nodes


...

Examples:

addrackposition -n node001..node010 rack1

addrackposition -n node001..node010 --height 2 --position 4 rack rack2


**3.15 Managing And Configuring A Rack** **177**


  - The rackposition submode allows individual nodes to be managed directly:


[basecm11->device[node002]->rackposition]% show

Parameter Value

-------------------------------- -----------------------------------------------
Rack rack2

Revision

Device position 2

Device height 1

Tray ID

Tray name


**The Convention Of The Top Of The Device Being Its Position**
Since rack manufacturers usually number their racks from top to bottom, the position of a device in a
rack (using the parameter Position in Base View, and the parameter deviceposition in cmsh ) is always
taken to be where the top of the device is located. This is the convention followed even for the less usual
case where the rack numbering is from bottom to top.
A position on a rack is 1U of space. Most devices have a height that fits in that 1U, so that the top of
the device is located at the same position as the bottom of the device, and no confusion is possible. The
administrator should however be aware that for any device that is greater than 1U in height such as, for
example, a blade enclosure chassis (section 3.15.3), the convention means that it is the position of the
top of the device that is where the device is considered to be. The position of the bottom of the device is
ignored.


**3.15.3** **Assigning Devices To A Chassis**

**A Chassis As A Physical Part Of A Cluster**
In a cluster, several local nodes may be grouped together physically into a chassis. This is common for
clusters using blade systems. Clusters made up of blade systems use less space, less hardware, and less
electrical power than non-blade clusters with the same computing power. In blade systems, the blades
are the nodes, and the chassis is the blade enclosure.
A blade enclosure chassis is typically 6 to 10U in size, and the node density for server blades is
typically 2 blades per unit with 2014 technology.


**Chassis Configuration And Node Assignment**
**Chassis list in Base View:** The Chassis list pane can be opened up in Base View via the navigation
path

Datacenter Infrastructure - Chassis

or

Devices - Chassis


A chassis can then be added, removed, or edited from the pane.
Within the Chassis list pane:


  - a new chassis item can be added with the ADD button, and then clicking on the Chassis popup.
This opens a Chassis pane where chassis configuration can be carried out and saved (figure 3.28).


  - an existing chassis item can be edited with the Edit menu option, or by double-clicking on the
item itself. This also opens up the Chassis pane for chassis configuration.


**178** **Configuring The Cluster**


Figure 3.28: Base View chassis configuration


The options that can be set within the Chassis pane include the following:


 - Hostname : a name that can be assigned to the chassis operating system


 - Tag : a hardware tag for the chassis


 - Mac : the MAC address of the chassis


 - Model : the hardware model name


 - Rack : the rack in which the chassis is placed


 - Members : the Members menu option allows devices to be assigned to a chassis (figure 3.29). An
item within the Device set can be any item from the subsets of Node, Switch, Power Distribution
Unit, Generic Device, Rack Sensor, and Gpu Unit . These items can be filtered for viewing, depending on whether they are Assigned (members of the chassis), Not Assigned (not members of
the chassis), or they can All be viewed (both Assigned and Not Assigned items).


 - Layout : how the nodes in a chassis are laid out visually.


 - Network : which network the chassis is attached to.


 - Username, Password : the user name and password to access the chassis operating system


 - Power control, Custom power script, Custom power script argument : power-related items for
the chassis.


 - Userdefined1, Userdefined2 : administrator-defined variables that can be used by CMDaemon.


**3.15 Managing And Configuring A Rack** **179**


Figure 3.29: Base View Chassis Members Menu Options


**Basic chassis configuration and node assignment with** cmsh **:** The chassis mode in cmsh allows configuration related to a particular chassis. Tab-completion suggestions for a selected chassis with the set
command show possible parameters that may be set:


**Example**


[basecm11->device[chassis1]]% set

containerindex hostname partition switchports

custompingscript ip password tag

custompingscriptargument layout powercontrol userdefined1

custompowerscript mac powerdistributionunits userdefined2

custompowerscriptargument members rack userdefinedresources

defaultgateway model revision username

deviceheight network slots

deviceposition notes supportsgnss


Whether the suggested parameters are actually supported depends on the chassis hardware. For
example, if the chassis has no network interface of its own, then the ip and mac address settings may be
set, but cannot function.
The positioning parameters of the chassis within the rack can be set as follows with cmsh :


**Example**


[basecm11->device[chassis1]]% set rack rack2

[basecm11->device*[chassis1*]]% set deviceposition 1; set deviceheight 6

[basecm11->device*[chassis1*]]% commit


The members of the chassis can be set as follows with cmsh :


**Example**


[basecm11->device[chassis1]]% append members basecm11 node001..node005

[basecm11->device*[chassis1*]]% commit


**180** **Configuring The Cluster**


**3.16** **Configuring GPU Settings**


**3.16.1** **GPUs And GPU Units**

GPUs (Graphics Processing Units) are processors that are heavily optimized for executing certain types
of parallel processing tasks. GPUs were originally used for rendering graphics, and one GPU typically
has hundreds of cores. When used for general processing, they are sometimes called General Processing
GPUs, or GPGPUs. For convenience, the “GP” prefix for General Processing is not used in this manual.
A GPU is typically placed on a PCIe card. GPUs can be physically inside the node that uses them, or
they can be physically external to the node that uses them. As far as the operating system on the node
making use of the physically external GPUs is concerned, the GPUs are internal to the node.
If the GPUs are physically external to the node, then they are typically in a _GPU unit_ . A GPU unit is
a chassis that hosts only GPUs. It is typically able to provide GPU access to several nodes, usually via
PCIe extender connections. This ability means that external GPUs typically require more configuration
than internal GPUs. GPU units are not covered in this manual because they are not very popular due to
their greater cost and slowness.
Configuring GPU settings for GPUs—that is, for devices internal to a node—is covered next.


**3.16.2** **Configuring GPU Settings**

**The** gpusettings **Submode In** cmsh
In cmsh, GPUs can be configured for a specified node via device mode.
Going into the gpusettings submode for that node then allows a type of GPU to be set, from the amd
or nvidia types, and a range to be specified for the GPU slots for that particular node:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% gpusettings

[basecm11->device[node001]->gpusettings]% add nvidia 1-3 ; commit


The range can be specified as


  - a single number, for a particular slot, for example: 3


  - a range, for a range of slots, for example: 0-2


  - all, for all GPU slots on that node, using:


all


or


    

GPUs can also be configured for a specified category via category mode. For example, using the
category default, then entering into the gpusettings submode allows a type ( nvidia or amd ) and a
range to be set for the range of GPUs:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% category use default

[basecm11->category[default]]% gpusettings

[basecm11->category[default]->gpusettings]% list
GPU range (key) Power limit ECC mode Compute mode Clock speeds

---------------- ------------ ------------ ------------- ------------
[basecm11->category[default]->gpusettings]% add nvidia 1-3 ; commit

[basecm11->category[default]->gpusettings[nvidia:1-3]]% show


**3.16 Configuring GPU Settings** **181**


Parameter Value

------------------------------ ---------------------------------
Clock speeds

Clock sync boost mode

Compute mode

ECC mode

...


As usual, GPU settings for a node override those for a category (section 2.1.3).


**GPU Settings With NVIDIA GPUs**
The installation of the NVIDIA GPU software driver packages is covered in section 9.1 of the _Installation_
_Manual_ . It should be noted that the cuda-dcgm package must be installed to access NVIDIA GPU metrics.
The present section is about configuring NVIDIA GPUs in BCM. The driver itself does not necessarily
have to be in place for the configuration to be done, although the configuration only becomes active
when the driver is installed.

After a GPU type has been set, the following NVIDIA GPU settings may be specified, if supported,
from within the gpusettings submode:


 - clockspeeds : The pair of clock speeds (frequency in MHz) to be set for this parameter can be
selected from the list of available speeds. The available speeds can be seen by running the status
command. The values are specified in the form: < _number for GPU processor_ >,< _number for memory_   

 - clocksyncboostmode : GPU boosting. Exceed the maximum core and memory clock speeds if it is
safe. Choices are:


**–** enabled


**–** disabled


 - computemode : Contexts can be computed with the following values for this mode:


**–** Default : Multiple contexts are allowed


**–** Exclusive thread : Only one context is allowed per device, usable from one thread at a time


**–**
Exclusive process : Only one context is allowed per device, usable from multiple threads at
a time. This mode option is valid for CUDA 4.0 and higher. Earlier CUDA versions ran only
in this mode.


**–** Prohibited : No contexts are allowed per device


 - eccmode : Sets the ECC bit error check, with:


**–** enabled


**–** disabled


When ECC is enabled:


**–** Single bit errors are detected, using the EccSBitGPU metric (page 929), and corrected automatically.


**–** Double bit errors are also detected, using the EccDBitGPU metric (page 929), but cannot be
corrected.


 - GPU range : range values can be set as follows:


**–** all : The GPU settings apply to all GPUs on the node.


**–** < _number_ >: The GPU settings apply to an individual GPU, for example: 1


**182** **Configuring The Cluster**


**–** < _number range_ >: The GPU settings apply to a range of GPUs, for example: 1,3-5


 - powerlimit : The administrator-defined upper power limit for the GPU. Only valid if powermode
is Supported .


**–** min : The minimum upper power limit that the hardware supports.


**–** max : The maximum upper power limit that the hardware supports.


**–** < _number_ >: An arbitrary upper power limit, specified as a number between min and max


**–** default : Upper power limit based on the default hardware value.


If no value is specified for a GPU setting, then the hardware default is used.


**The** updatenodegpuconfig **Command For Controlling Power Consumption**
Above the gpusettings submode, within device mode, nodes with GPUs can have their power consumption limited per specified GPU:
Without arguments, the updatenodegpuconfig command shows the current status:


**Example**


[basecm11->device[node001]]% updatenodegpuconfig

Node GPU Power limit Processor speed Memory speed

------------ ------------ ---------------- ---------------- ---------------
node001 0 350 W 135 MHz 958 MHz

node001 1 350 W 135 MHz 958 MHz


In the preceding example, the only node with a GPU is node001. The same result is therefore shown
if the command is run as updatenodegpuconfig -n node001 .
The first and second GPUs on node001 can have their power limits set to the same value with a range
syntax:


[basecm11->device]% updatenodegpuconfig node001:0-1:330

Node GPU Power limit Processor speed Memory speed

------------ ------------ ---------------- ---------------- ---------------
node001 0 330 W 135 MHz 958 MHz

node001 1 330 W 135 MHz 958 MHz


For the first and second GPUs on node001, the power limit, in watts, can be set to different values:


**Example**


[basecm11->device]% updatenodegpuconfig node001:1:300 node001:0:330

Node GPU Power limit Processor speed Memory speed

------------ ------------ ---------------- ---------------- ---------------
node001 0 330 W 135 MHz 958 MHz

node001 1 300 W 135 MHz 958 MHz


A dry-run option shows the effect on both the GPUs:


[basecm11->device]% updatenodegpuconfig node001:0-1:350 --dry-run

Node GPU Power limit Processor speed Memory speed

------------ ------------ ---------------- ---------------- ---------------
node001 0 350 W - 
node001 1 350 W - 

The clock speed can be set with a 3rd colon delimited field, in Hz:


**3.16 Configuring GPU Settings** **183**


[basecm11->device]% updatenodegpuconfig node001:0:350:142M

Node GPU Power limit Processor speed Memory speed

------------ ------------ ---------------- ---------------- ---------------
node001 0 350 W 135 MHz 142 MHz


Using both gpusettings values and updatenodegpuconfigs may cause conflict. For example with
the processor speed setting of updatenodgpuconfig and the value of clockspeeds in gpusettings .
If the clocks cannot be changed, then the driver is handling them dynamically.


**GPU Settings With AMD GPUs**
GPU settings for AMD Radeon GPUs are accessed via cmsh in the same way as NVIDIA GPU settings.
The AMD GPU setting parameters do differ from the NVIDIA ones.
The AMD GPUs supported are Radeon cards. A list of cards and operating systems compatible with the Linux driver used is at [https://support.amd.com/en-us/kb-articles/Pages/](https://support.amd.com/en-us/kb-articles/Pages/Radeon-Software-for-Linux-Release-Notes.aspx)
[Radeon-Software-for-Linux-Release-Notes.aspx](https://support.amd.com/en-us/kb-articles/Pages/Radeon-Software-for-Linux-Release-Notes.aspx)
AMD GPU driver installation is described in section 7.4 of the _Installation Manual_ .

The Radeon Instinct MI25 shows the following settings in Ubuntu 16_06 running a Linux 4.4.0-72generic kernel:


**Example**


[basecm11->device[node001]->gpusettings]% list

Type GPU range Info

---- --------- -----------------
AMD 0 PowerPlay: manual

[basecm11->device[node001]->gpusettings]% use amd:0

[basecm11->device[node001]->gpusettings[amd:0]]% show

Parameter Value

-------------------------------- ----------------------------
Activity threshold 1

Fan speed 255

GPU clock level 5

GPU range 0

Hysteresis down 0

Hysteresis up 0

Info PowerPlay: manual

Memory clock level 3

Minimum GPU clock 0

Minimum memory clock 0

Overdrive percentage 1

PowerPlay mode manual

Revision

Type AMD


The possible values here are:


 - activitythreshold : Percent GPU usage at a clock level that is required before clock levels change.
From 0 to 100.


 - fanspeed : Maximum fan speed. From 0 to 255


 - gpuclocklevel : GPU clock level setting. From 0 to 7.


 - gpurange : The slots used.


 - hysteresisdown : Delay in milliseconds before a clock level decrease is carried out.


**184** **Configuring The Cluster**


 - hysteresisup : Delay in milliseconds before a clock level increase is carried out.


 - info : A compact informative line about the GPU status.


 - memoryclocklevel : Memory clock speed setting. From 0-3. Other cards can show other values.


 - minimumgpuclock : Minimum clock frequency for GPU, in MHz. The kernel only allows certain
values. Supported values can be seen using the status command.


 - minimummemoryclock : Minimum clock frequency for the memory, in MHz. The kernel only allows
certain values. Supported values can be seen using the status command.


 - overdrivepercentage : Percent overclocking. From 0 to 20%


 - powerplaymode : Decides how the performance level power setting should be implemented.


**–**
high : keep performance high, regardless of GPU workload


**–** low : keep performance low, regardless of GPU workload


**–** auto : Switch clock rates according to GPU workload


**–** manual : Use the memory clock level and GPU clock values.


The status command displays supported clock frequencies (some values ellipsized):


**Example**


[basecm11->device[node001]->gpusettings[amd:0]]% status

Index Name Property Value Supported

----- --------------------- ------------ ------------ ------------------------------------
0 Radeon Instinct MI25 Clock 1399Mhz 852Mhz, 991Mhz, ..., 1440Mhz, 1515Mhz

0 Radeon Instinct MI25 Memory 945Mhz 167Mhz, 500Mhz, 800Mhz, 945Mhz


**GPU Settings In Base View**
In Base View, GPU settings can be accessed within the settings options for a category or a device. This
brings up a GPU settings list.


**GPU settings list in Base View:** A GPU Settings list pane can be opened up in Base View for a
regular node, for example node001, with the navigation path:
Devices - Nodes[node001] - Edit - Settings - JUMP TO - GPU Settings


Similarly, a GPU Settings list pane can be opened up in Base View for nodes in a category, for
example gpunodes, with the navigation path:
Grouping - Categories[gpunodes] - Edit - Settings - JUMP TO - GPU Settings


Within the GPU Settings list pane:


  - a new GPU settings item can be added with the ADD button, and then clicking on either the
AMDGPUSettings or the NVIDIAGPUSettings item in the popup. This opens an AMDGPU Settings
pane or an NVIDIA GPU Settings pane, where GPU configuration can be carried out and saved
(figure 3.30).


**3.16 Configuring GPU Settings** **185**


Figure 3.30: GPU settings window for a node


  - an existing GPU settings item can be edited with the Edit menu option, or by double-clicking
on the item itself. This also opens up the GPU Settings pane where GPU configuration can be
managed.


**GPU Configuration For HPC Workload Managers**
**Slurm GPU configuration via direct** slurm.conf **changes:** To configure NVIDIA GPUs for Slurm,
changes are made in slurm.conf when cm-wlm-setup configures GPUs for Slurm (section 7.3).
Changes made are kept in the AUTOGENERATED section and can be worked out by checking the difference between the slurm.conf.template file and the actual slurm.conf file. Changes made include
defining the GresTypes gpu and mps, and setting GPU plugins that allow Slurm generic resources to
work.

The configured gres options can be seen by running sbatch --gres=help :


**Example**


[fred@basecm11 ~]$ sbatch --gres=help

Valid gres options are:
gpu[[:type]:count]
mps[[:type]:count]


This means that a GPU can be requested in a job script with the Slurm gres option:


**186** **Configuring The Cluster**


#SBATCH --gres=gpu:1


Similarly, MPS resources ( [https://slurm.schedmd.com/gres.html#MPS_Management](https://slurm.schedmd.com/gres.html#MPS_Management) ) can be requested
with:


#SBATCH --gres=mps:100


If adding new parameters manually, care must be taken to avoid duplication of parameters already
in the file, because slurmd is unlikely to work properly with duplicated parameters.
The Slurm client role can be configured at configuration overlay, category, or node level. If configuring the Slurm client role for GPU gres resources manually, then each GPU can be configured within the
role:


**Example**


[basecm11->configurationoverlay]% list
Name (key) Priority All head nodes Nodes Categories Roles

-------------------- ---------- -------------- ---------------- ---------------- ---------------
slurm-accounting 500 yes slurmaccounting

slurm-client 500 no default slurmclient

slurm-server 500 yes slurmserver

slurm-submit 500 no default slurmsubmit

wlm-headnode-submit 600 yes slurmsubmit

[basecm11->configurationoverlay]% use slurm-client

[basecm11->configurationoverlay[slurm-client]]% roles

[basecm11->configurationoverlay[slurm-client]->roles]% use slurmclient

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]% genericresources

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]->genericresources]%

[basecm11->...->roles[slurmclient]->genericresources]% add gpu0

[basecm11->...->roles*[slurmclient*]->genericresources*[gpu0*]]% set name gpu

[basecm11->...->roles*[slurmclient*]->genericresources*[gpu0*]]% set file /dev/nvidia0

[basecm11->...->roles*[slurmclient*]->genericresources*[gpu0*]]% commit

[basecm11->...->roles[slurmclient]->genericresources[gpu0]]%
(Repeat similar settings for the other GPUs, gpu1...gpu7)

[basecm11->...->roles[slurmclient]->genericresources]% list
Alias (key) Name Type Count File

----------- -------- -------- -------- ---------------
gpu0 gpu /dev/nvidia0
gpu1 gpu /dev/nvidia1
gpu2 gpu /dev/nvidia2
gpu3 gpu /dev/nvidia3
gpu4 gpu /dev/nvidia4
gpu5 gpu /dev/nvidia5
gpu6 gpu /dev/nvidia6
gpu7 gpu /dev/nvidia7

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]->genericresources]%


By default, Slurm just allows a single job to be executed per node. To change this behavior, it is
necessary to allow oversubscription. For example, to allow 8 jobs per node:


**Example**


[basecm11->wlm[slurm]]% jobqueue

[basecm11->wlm[slurm]->jobqueue]% use defq

[basecm11->wlm[slurm]->jobqueue[defq]]% set oversubscribe yes:8

[basecm11->wlm[slurm]->jobqueue*[defq*]]% commit

[basecm11->wlm[slurm]->jobqueue[defq]]%


**3.16 Configuring GPU Settings** **187**


**Slurm GPU configuration via auto-detection:** Instead of carrying out Slurm configuration by modifying slurm.conf by hand, it may be configured via auto-detection. More details on this are to be found
starting at page 390.


**PBS:** NVIDIA Base Command Manager version 9.0 onward supports GPU configuration in PBS via
the cm-wlm-setup tool after installation (section 7.3.2).


**LSF:** Within LSF cluster configuration, GPU devices can be autodetected by setting the gpuautoconfig
parameter to yes . In cmsh this can be carried out with:


**Example**


[basecm11->wlm[lsf]]% set gpuautoconfig yes

[basecm11->wlm*[lsf*]]%


The parameter can also be set during LSF configuration via cm-wlm-setup (figure 3.31):


Figure 3.31: GPU settings screen for LSF in cm-wlm-setup


GPU resource enforcement can be configured for LSF as follows:


**Example**


[basecm11->wlm[lsf]->cgroups]% append resourceenforce gpu

[basecm11->wlm*[lsf*]->cgroups*]% commit

[basecm11->wlm[lsf]->cgroups]%


**3.16.3** **MIG Configuration**
MIG configuration can be carried out for the cluster using the BCM MIG management as described in
this section.

An alternative for MIG configuration is to not use the BCM MIG management tool ( cmsh ), and to
instead use other MIG management tools, such as the DGX native nvidia-migmanager.service, or the
GPU operator-provided nvidia-mig-manager . If non-BCM MIG management tools are used, then BCM
leaves the MIG configuration alone. Using multiple MIG management tools simultaneously to configure
MIG should not be done.


**What Is MIG?**

An Ampere NVIDIA GPU is a GPU based on the GA100 microarchitecture. It has compute capability 8.0,
which means it can be configured into multiple logical GPU instances if it uses CUDA 11 and NVIDIA
driver 450.80.02 or later.

This configuration of multiple logical GPU instances is called Multi-Instance GPU (MIG). The logical
GPU instances are MIG devices, that are enabled by setting up the physical GPU to switch to MIG mode.


**188** **Configuring The Cluster**


**As a sanity check to see if MIG is supported:** If the hardware and drivers are in place, then running
the nvidia-smi command on the node with the physical GPU should display its MIG capability:


root@basecm11:~# ssh node001 "nvidia-smi" | grep MIG

| | | MIG M. |

| MIG devices: |

| GPU GI CI MIG | Memory-Usage | Vol| Shared |


**GPU utilization information changes on enabling MIG:** Once enabled, the full physical GPU is no
longer available as a device, and GPU utilization metrics become unavailable by default.
GPU profiling metrics (section G.1.7) for the physical GPU can however still be enabled. For example,
it can be carried out with cmsh as follows, for a GPU on node001 :


**Example**


basecm11->device[node001]]% gpuprofiling show

Hostname GPU Major ID Minor ID Field ID Metric Watched

----------- -------- ------------ ------------ ------------ ------------------------------ ---------
node001 0 0 1 1002 gpu_profiling_sm_active no

node001 0 0 1 1003 gpu_profiling_sm_occupancy no

...

basecm11->device[node001]]% gpuprofiling watch 1003

Hostname GPU Major ID Minor ID Field ID Metric Watched

----------- -------- ------------ ------------ ------------ ------------------------------ ---------
...

node001 0 0 1 1003 gpu_profiling_sm_occupancy yes

...


[basecm11->device[node001]]% metrics | grep gpu_profiling

Metric gpu_profiling_sm_occupancy gpu0 GPU GPUSampler


Enabling physical GPU profiling after MIG enablement should be done with caution, because:


  - it may affect the performance


  - newer drivers may support MIG profiling, which may be confusing


**Overview Of MIG Concepts And Terminology**
The logical GPU instances are composed of _slices_ of GPU resources. Slices are the smallest fraction
possible of the resource that can be allocated in a logical GPU instance. Thus:


  - memory slice: this is the smallest fraction of the memory of the physical GPU that can be allocated
to the GPU instance. For the Ampere architecture this is 1/8 [th] of the total physical GPU memory.


  - SM slice: this is the smallest fraction of the streaming multiprocessors (SMs) on the GPU that can
be allocated as a logical SM. An SM is composed of multiple cores (streaming processors). For the
Ampere architecture an SM slice is 1/7 [th] of the total physical GPU SMs.


  - GPU slice: this is the smallest fraction of the physical GPU that has a single GPU memory slice
and a single GPU SM slice. A maximum of 7 GPU slices can be specified from the original physical
GPU.


The preceding fractional slices can be combined in various mixes to compose a logical GPU instance :


  - GPU instance: a combination of GPU slices and GPU engines. GPU engines are hardware components that execute other work on the GPU, and can be encoders/decoders (NVENCs/NVDECs),
shortcut connectors (CE (copy engine) for DMA), etc.


**3.16 Configuring GPU Settings** **189**


  - compute instance: a part of a GPU instance. It consists of a subset of the parent GPU instance’s
SM slices and other GPU engines (DMAs, NVENCs ...). The compute instances can share memory
and GPU engines with other compute instances within their GPU instance.


Further details on the terminology and how slices can be allocated to GPU instances are given
in the NVIDIA documentation at [https://docs.nvidia.com/datacenter/tesla/mig-user-guide/](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/#concepts)

[#concepts](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/#concepts) .
A use case for creating several GPU instances from a full physical GPU is when allocation of the full
physical GPU is wasteful.
For example, if a full physical GPU is allocated to a job, but the job only uses a fraction of the full
set of GPU cores, then the allocation is wasteful, because no other job can then be processed on the
remaining idle cores. Instead, if the physical GPU is split into several instances and the job allocated to
an instance with a closer match in resources, then it means that other GPU instances are still available
for processing other jobs.
When configuring GPU instances for the cluster, the administrator typically allocates all available
slices to all the GPU instances that are being configured. Leaving a slice unallocated means that that
slice cannot be available to jobs, and it means that the physical resources of that slice are lying idle. For
example, if some of the 7 SM slices from the physical GPU are not used, then they are wasted as their
processors are never available to jobs, and so that slice stays idle.
Cluster management of GPU instances is described in the following sections.


**MIG Status Of Physical GPUs**
The MIG status on a GPU can be viewed with the mig status command. For example, the following
shows 8 physical GPUs on node001 that have not yet become MIG enabled:


**Example**


[basecm11->device[node001]]% mig status

Node GPU Active Pending

---------------- -------- -------------------------------- -------------------------------
node001 0 no no

node001 1 no no

node001 2 no no

node001 3 no no

node001 4 no no

node001 5 no no

node001 6 no no

node001 7 no no


**MIG** enable **And** disable **Options To Set Up Pending States For The Physical GPUs**
If the enable or disable options are run, then by default all the physical GPUs are set to a pending state
for enabled ( yes ) and disabled ( no ) respectively:


**Example**


[basecm11->device[node001]]% mig enable

Node GPU Active Pending

---------------- -------- -------------------------------- -------------------------------
node001 0 no yes

node001 1 no yes

node001 2 no yes

node001 3 no yes

node001 4 no yes

node001 5 no yes

node001 6 no yes

node001 7 no yes


**190** **Configuring The Cluster**


Individual physical GPUs can also be set to a pending state of enabled or disabled, following the
node list syntax (section 2.5.5):


[basecm11->device[node001]]% mig disable 3,5-7

Node GPU Active Pending

---------------- -------- -------------------------------- -------------------------------
node001 0 no yes

node001 1 no yes

node001 2 no yes

node001 3 no no

node001 4 no yes

node001 5 no no

node001 6 no no

node001 7 no no


**Rebooting The MIG Instances To Activate/Deactivate Instances According To Pending State Settings**
The pending states only become active after the node is rebooted for A100 GPUs:


**Example**


[basecm11->device[node001]]% reboot

Reboot in progress for: node001

...

node001 [ UP ]

[basecm11->device[node001]]% mig status


Node GPU Active Pending

---------------- -------- -------------------------------- -------------------------------
node001 0 yes yes

node001 1 yes yes

node001 2 yes yes

node001 3 no no

node001 4 yes yes

node001 5 no no

node001 6 no no

node001 7 no no


The effect of enable and disable persists after reboots, until the pending value changes once more.
For H100 GPUs, the changes do not require a reboot.


**The MIG Profiles**
**Listing MIG Profiles:** The full list of the existing available MIG profiles for each physical GPU is
displayed with the mig profiles command for the node. If there are 7 physical GPUs at the node, then
the listing might look something like:


**Example**


[basecm11->device[node001]]% mig profiles

Node GPU ID Name Instances Memory

---------------- -------- -------- ---------- --------- -------
node001 0 1 1g.5gb 7 4.7GiB

node001 0 1 1g.5gb+me 1 4.7GiB

node001 0 2 2g.10gb 3 9.7GiB

node001 0 3 3g.20gb 1 19.6GiB

node001 0 4 4g.20gb 1 19.6GiB

node001 0 7 7g.40gb 1 39GiB

...


**3.16 Configuring GPU Settings** **191**


node001 7 2 2g.10gb 3 9.7GiB

node001 7 3 3g.20gb 1 19.6GiB

node001 7 4 4g.20gb 1 19.6GiB

node001 7 7 7g.40gb 1 39GiB


A list for physical GPU 1 can be displayed with:


**Example**


[basecm11->device[node001]]% mig profiles 1

Node GPU ID Name Instances Memory

---------------- -------- -------- ---------- --------- -------
node001 1 1 1g.5gb 7 4.7GiB

node001 1 1 1g.5gb+me 1 4.7GiB

node001 1 2 2g.10gb 3 9.7GiB

node001 1 3 3g.20gb 1 19.6GiB

node001 1 4 4g.20gb 1 19.6GiB

node001 1 7 7g.40gb 1 39GiB


**MIG Profiles Naming Convention:** The naming format for the profile takes the form


< _number of GPU slices in the physical GPU_ >g.< _memory for slice in GB_ >gb


The +me suffix implies media extensions being active. The number of GPU instances, the number of
GPU slices used, and the memory used by the instance can thus be worked out from the name.
For example:


 - 1g.5gb implies that the size of the GPU slice used for the instances is 1. 4.7GiB of memory is used
by each of the 7 GPU instances,


 - 2g.10gb implies that the size of the GPU slice used for the instances is 2. 9.7GiB of memory is used
by each of the 3 GPU instances.


**Creating GPU instances, by setting the MIG profile for a GPU:** The MIG profile is an attribute that
can be set within the GPU settings for its physical GPU. This can be done after having set up a CMDaemon entity for a physical GPU 0 (section 3.16.2):


**Example**


[basecm11->device[node001]]% gpusettings

[basecm11->device*[node001]->gpusettings]% list

Type GPU range Info

------ --------- -------
Nvidia 0 default

[basecm11->device[node001]->gpusettings]% use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% show

Parameter Value

-------------------------------- -----------------------------------------------
...

MIG profiles


 - **A simple existing set of profiles** with 7 GPU instances with 1 GPU slice each, and 5 GB of memory
for each slice can be specified with:


**Example**


**192** **Configuring The Cluster**


[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 1g.5gb; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% show

Parameter Value

-------------------------------- -----------------------------------------------
...

MIG profiles 1g.5gb


Setting the profiles, and carrying out the commit configures the GPU instances, but does not yet
apply them:


**Example**


[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig show

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------

Applying the profile deploys the configuration, and shows the configuration:


**Example**


[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------
node001 0 13   - 1g.5gb 19 6 1

node001 0 13 0 1g.5gb 0 0 1


In the preceding, 1 GPU instance has been deployed, with 1 compute instance slice using 5GB. The
instance with the    - represents the hosting GPU instance, while the subsequent row represents the
compute instance.


 - **Setting a profile with** mig apply --profile is an alternative to setting it within gpusettings .
However, only a profile set within gpusettings is persistent. The profile set with the --profile
option is lost if its node reboots. Multiple profiles can be set using comma-separation (instead of
using space-separation). Using multiple --profile options is also possible.


**Example**


[basecm11->device[node001]]% mig apply --profile 1g.5gb,2g.10gb

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------
node001 0 5   - 2g.10gb 14 4 2

node001 0 5 0 2g.10gb 1 0 2

node001 0 13   - 1g.5gb 19 6 1

node001 0 13 0 1g.5gb 0 0 1

[basecm11->device[node001]]% mig apply --profile 1g.5gb --profile 2g.10gb

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------
node001 0 5   - 2g.10gb 14 4 2

node001 0 5 0 2g.10gb 1 0 2

node001 0 13   - 1g.5gb 19 6 1

node001 0 13 0 1g.5gb 0 0 1


**3.16 Configuring GPU Settings** **193**


 - **Multiple GPU instances** can be specified, if the GPU allows it, using a < _number_ >* prefix syntax.
So, to deploy 7 GPU instances, each hosting 1 compute instance with 5gb slices, the specification
can be:


**Example**


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 7*1g.5gb; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

--------------- -------- -------- -------- -------- -------- -------- -------
node001 0 7   - 1g.5gb 19 0 1

node001 0 7 0 1g.5gb 0 0 1

node001 0 8   - 1g.5gb 19 1 1

node001 0 8 0 1g.5gb 0 0 1

node001 0 9   - 1g.5gb 19 2 1

node001 0 9 0 1g.5gb 0 0 1

node001 0 10 0 1g.5gb 19 3 1

node001 0 10 0 1g.5gb 0 0 1

node001 0 11   - 1g.5gb 19 4 1

node001 0 11 0 1g.5gb 0 0 1

node001 0 12   - 1g.5gb 19 5 1

node001 0 12 0 1g.5gb 0 0 1

node001 0 13   - 1g.5gb 19 6 1

node001 0 13 0 1g.5gb 0 0 1


 - **GPU slices** can be implied by default by the profile, and subsets of these slices can be specified
explicitly.


To deploy 1 GPU instance, with 7 GPU slices of compute instance resources, the specification can
be:


**Example**


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 7g.40gb; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------
node001 0 0   - 7g.40gb 0 0 8

node001 0 0 0 7g.40gb 4 0 7


If a profile with a more than 1 GPU slice is chosen, then GPU slice subsets can be set up via the
following syntax:


**Example**


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 2g.10gb; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------
node001 0 5   - 2g.10gb 14 4 2

node001 0 5 0 2g.10gb 1 0 2


**194** **Configuring The Cluster**


 - **GPU slices use a colon syntax** to explicitly specify subsets of GPU slices.


The configuration specification 2g.10gb can also be specified as 2g.10gb:1, where that :1 indicates
the number of GPU slices for the compute instance, counting from zero. That means the compute
instance has 2 GPU slices. The resulting configuration is exactly the same as 2g.10g .


If the specification 2g.10gb:0 is used instead, then the compute instance ends up looking like:


**Example**


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 2g.10gb:0; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- ----------- -------- -------- -------
node001 0 5   - 2g.10gb 14 4 2

node001 0 5 0 1c.2g.10gb 0 0 1


Here the 1c indicates 1 GPU slice (here it is counting from 1).


Adding another slice to a separate compute instance within the same GPU instance can be specified with:


**Example**


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 2g.10gb:0:0; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- ----------- -------- -------- -------
node001 0 5   - 2g.10gb 14 4 2

node001 0 5 0 1c.2g.10gb 0 0 1

node001 0 5 1 1c.2g.10gb 0 1 1


In the preceding set migprofiles command, the specification


2g.10gb:0:0


can alternatively be expanded out and written in the form:


2g.10gb:1c.2g.10gb:1c.2g.10gb


for more clarity, at the expense of more typing.


For a general profile that allows N GPU slices for an instance (with _N_ _≤_ 7), the mapping for the
colon syntax takes the form:


**compact colon form** **expanded form**


:0 1c.< _profile_    

:1 2c.< _profile_    

... ...


:N-1 Nc.< _profile_    - or
< _profile_            

**3.16 Configuring GPU Settings** **195**


In practice, there are hardware-based restrictions for what is permitted to be allocated. So for
example on the NVIDIA A100-PCIE-40GB:


7g.40gb:3 is allowed but


7g.40gb:4 is not.


Details on supported profiles for hardware can be found in the NVIDIA documentation. For example, for the A30 profiles at:


[https://docs.nvidia.com/datacenter/tesla/mig-user-guide/#a30-profiles](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/#a30-profiles)


and for the A100 profiles at:


[https://docs.nvidia.com/datacenter/tesla/mig-user-guide/#a100-profiles](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/#a100-profiles) .


Increasing the number of GPU instances can also still be done using the earlier < _number_ >* prefix
syntax together with the colon syntax, if the GPU allows it:


**Example**


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 3*2g.10gb:0:0; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device[node001]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- ----------- -------- -------- -------
node001 0 3   - 2g.10gb 14 0 2

node001 0 3 0 1c.2g.10gb 0 0 1

node001 0 3 1 1c.2g.10gb 0 1 1

node001 0 4   - 2g.10gb 14 2 2

node001 0 4 0 1c.2g.10gb 0 0 1

node001 0 4 1 1c.2g.10gb 0 1 1

node001 0 5   - 2g.10gb 14 4 2

node001 0 5 0 1c.2g.10gb 0 0 1

node001 0 5 1 1c.2g.10gb 0 1 1


 - **A heterogeneous set of existing profiles** for GPU instances can also be defined for the GPU with
MIG profiles.


For example, 2 instances with the MIG profile 1g.5gb, and 1 instance with the MIG profile 2g.10gb
can be specified with:


[basecm11->device[node001]]% gpusettings; use nvidia:0

[basecm11->device[node001]->gpusettings[nvidia:0]]% set migprofiles 2*1g.5gb 2g.10gb; commit

[basecm11->device[node001]->gpusettings[nvidia:0]]% show

Parameter Value

-------------------------------- -----------------------------------------------
...

MIG profiles 2*1g.5gb,2g.10gb

[basecm11->device[node001]->gpusettings[nvidia:0]]% ..;..

[basecm11->device*[node001*]]% mig apply

Node GPU MIG Instance Name Profile Start Size

---------------- -------- -------- -------- -------- -------- -------- -------
node001 0 3   - 2g.10gb 14 0 2

node001 0 3 0 2g.10gb 1 0 2

node001 0 11   - 1g.5gb 19 4 1

node001 0 11 0 1g.5gb 0 0 1

node001 0 13   - 1g.5gb 19 6 1

node001 0 13 0 1g.5gb 0 0 1


**196** **Configuring The Cluster**


 - **heterogeneous sets are useful when trying to use up all the slices available**, to make the maximum resources available. So, while an administrator can carry out the preceding specification:


2*1g.5gb 2g.10gb


this is not a good allocation of resources since it only makes 4/7 of the GPU slices available, and
4/8 of the memory slices available. An administrator would more sensibly specify something like,
for example:


5*1g.5gb,2g.10gb


which uses up the full 7 GPU slices and 35GB (6/8 slices) of memory available from the physical
GPU. This makes full use of the SM resources derived from the physical GPU, so that these SM
resources are fully available to workloads.


 - **Overallocating slices for MIG configuration is not possible** . If there is an attempt to overallocate,
then the slices that are allocated too late are simply not allocated. This can lead to unexpected
results for the unwary cluster administrator. For example:


**–**
5*1g.5gb,2g.10gb allocates the 5 slices of the 1g instance and the 2 slices of the 2g instance.

But


**–**
6*1g.5gb,2g.10gb allocates the 6 slices of the 1g instance and none of the 2g instance.


**–**
7*1g.5gb,2g.10gb allocates the 7 slices of the 1g instance and none of the 2g instance.


**–**
70*1g.5gb,2g.10gb allocates 7 slices of the 1g instance and none of the 2g instance.


**3.17** **Configuring Sampling From A Prometheus Exporter**


CMDaemon can be configured to sample a Prometheus exporter, for example from the NVIDIA Unified
Fabric Manager (UFM) platform. A CMDaemon front end such as cmsh can have a data producer, for
example UFM, configured within the monitoring setup mode (section 10.5.4) to allow sampling of the
Prometheus exporter:


**Example**


[root@basecm11]# cmsh

[basecm11]% monitoring setup

[basecm11->monitoring->setup]% add prometheus UFM #create a data producer of type Prometheus

[basecm11->monitoring->setup*[UFM*]]% set urls http://10.180.217.170:9001/metrics #end point

[basecm11->monitoring->setup*[UFM*]]% set -e NoPostAllowed yes #HTTP GET only, use for older exporters

[basecm11->monitoring->setup*[UFM*]]% nodeexecutionfilters

[basecm11->monitoring->setup*[UFM*]->nodeexecutionfilters]% active #run on active head node only

Added active resource filter

[basecm11->monitoring->setup*[UFM*]->nodeexecutionfilters]% commit


In the example, the URL needs to be set to the Prometheus export server endpoint. The value of
NoPostAllowed only needs to be set to yes for some older Prometheus versions that do not work with
HTTP POST. The data producer is set to run on only the active head node with the nodeexecutionfilter
setting (page 586).
The preceding example configures CMDaemon to sample from a Prometheus exporter. The other
way around, that is to have CMDaemon be the exporter of Prometheus data, can be achieved via the
EnablePrometheusExporterService directive (page 850).


**3.18** **Configuring Custom Scripts**


Some scripts are used for custom purposes. These are used as replacements for certain default scripts,
for example, in the case of non-standard hardware where the default script does not do what is expected.
The custom scripts that can be set, along with their associated arguments are:


**3.18 Configuring Custom Scripts** **197**


 - custompowerscript and custompowerscriptargument (section 4.1.4)


 - custompingscript and custompingscriptargument (section 3.18.2)


 - customremoteconsolescript and customremoteconsolescriptargument (section 3.18.3)


In addition to the preceding custom* scripts, system information scripts can be set that provide extra
information to the sysinfo command in BCM (section 3.18.4).
The environment variables of CMDaemon (section 3.3.1 of the _Developer Manual_ ) can be used in the
scripts. Successful scripts, as is the norm, return 0 on exit.


**3.18.1** custompowerscript
The use of custom power scripts is described in section 4.1.4.


**3.18.2** custompingscript
The following example script:


**Example**


#!/bin/bash

/bin/ping -c1 $CMD_IP


can be defined and set for the cases where the default built-in ping script, cannot be used.
By default, the node device states are detected by the built-in ping script (section 5.5) using ICMP
ping. This results in the statuses that can be seen on running the list command of cmsh in device mode.
An example output, formatted for convenience, is:


**Example**


[root@basecm11]# cmsh -c "device; format hostname:15, status:15; list"

hostname (key) status

--------------- -------------
basecm11 [ UP ]

node001 [ UP ]

node002 [ UP ]


If some device is added to the cluster that blocks such pings, then the built-in ping can be replaced
by the custom ping of the example, which relies on standard ICMP ping.
However, the replacement custom ping script need not actually use a variety of ping at all. It could
be a script running web commands to query a chassis controller, asking if all its devices are up. The
script simply has to provide an exit status compatible with expected ping behavior. Thus an exit status
of 0 means all the devices are indeed up.


**3.18.3** customremoteconsolescript
A custom remote console script can be used to run in the built-in remote console utility. This might be
used, for example, to allow the administrator remote console access through a proprietary KVM switch
client.

For example, a user may want to run a KVM console access script that is on the head node and with
an absolute path on the head node of /root/kvmaccesshack . The script is to run on the console, and
intended to be used for node node001, and takes the argument 1 . This can then be set in cmsh as follows:


**Example**


**198** **Configuring The Cluster**


[root@basecm11]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% get customremoteconsolescript; get customremoteconsolescriptargument


[basecm11->device[node001]]% set customremoteconsolescript /root/kvmaccesshack

[basecm11->device[node001]]% set customremoteconsolescriptargument 1

[basecm11->device[node001]]% rconsole

_KVM console access session using the_ 1 _argument option is displayed_


In Base View, the corresponding navigation paths to access these script settings are:
Devices  - Nodes  - Edit  - Settings  - Custom remote console script
and

Devices  - Nodes  - Edit  - Settings  - Custom remote console script argument
while the remote console can be launched via the navigation path:

Devices  - Nodes  - Edit  - Connect  - Remote console


**3.18.4** sysinfo **Custom Scripts**
**Standard** sysinfo
The sysinfo command in BCM is run from device mode in cmsh for a node. By default, sysinfo returns
some basic hardware information for the node.


**Overview Of Running Custom Scripts In** sysinfo
A cluster administrator may however wish to extract some additional hardware-related information
from the cluster. To do this, custom scripts associated with the sysinfo command can be created by the
cluster administrator. These sysinfo custom scripts run when the sysinfo command is executed via
cmsh, and they pick up the additional information.


**Custom script types:** The scripts can be of three types, with corresponding directory locations. as indicated by the following table:


**Type of script** **Script directory** **path on node**


local /cm/local/apps/cmd/scripts/sysinfo/local/


director /cm/local/apps/cmd/scripts/sysinfo/director/


head /cm/local/apps/cmd/scripts/sysinfo/head/


**Custom script process:** When sysinfo runs for a particular node, the scripts that are called have the
following characteristics, and are run as follows:


  - Any scripts of the local type are run on the node that sysinfo is executed on. The scripts must
be placed by the cluster administrator on the node itself. The node could be a head node, director
node, a regular node, or a cloud node. The output from the local scripts is picked up.


  - Any scripts of the director type are run on the director node. The scripts must be placed by the
cluster administrator on the director node itself. The output from the scripts is picked up.


  - Any scripts of the head type are run on the head node. The scripts themselves must be placed by
the cluster administrator on the head node. The output from the scripts is picked up.


**3.18 Configuring Custom Scripts** **199**


**Custom script output format:** The script outputs are JSON format key value pairs (JSON object literals).
The simplest standard JSON output form supported for sysinfo is:


{

"key":"value"

}


The format if getting output for N key-value pairs is:


{

"key1":"value1",

"key2":"value2",

...

"keyN":"valueN"

}


**Nested sysinfo output:** The key-value pairs can also be grouped, with the output presented in the
following format for a group:


{

"group":{

"key1":"value1",

"key2":"value2",

...

"keyN":"valueN"

}

}


The key-value pairs can also be structured with multiple groups. In the following example there are
two groups:


**Example**


{

"group1":{

"key1.1":"value1.1",

"key1.2":"value1.2"

}

"group2":{

"key2.1":"value2.1",

"key2.2":"value2.2",

"key2.3":"value2.3"

}

}


The nested multilayer output format can be useful for grouped. For example, dmidecode can output
key-value pairs that specify starting and ending ranges, which can be grouped according to the various
DMI types that are also available in the output.


**Simple** sysinfo **custom script construction:** For example, the following bash script can be run on the
head node:


**Example**


**200** **Configuring The Cluster**


[root@basecm11 ~]# cat /cm/local/apps/cmd/scripts/sysinfo/head/outputscript.sh

#!/bin/bash

myhostname=$(hostname)

#next line extracts just the UUID value from the dmidecode output for the system for this particular hardware
myuuid=$(dmidecode | grep -A6 "^System Information" | grep UUID | sed -e 's/^ _\_ W*UUID: //')
echo '{'

echo '"script path is":"'$0'",'
echo '"CMDaemon running on":"'$CMD_HOSTNAME'",'
echo '"script running on":"'$myhostname'"',
echo '"'$myhostname' UUID":"'$myuuid'"'

echo '}'


If run directly, outside of CMDaemon, then this would display a JSON key-value output similar to
the following:


**Example**


[root@basecm11 ~]# /cm/local/apps/cmd/scripts/sysinfo/head/outputscript.sh

{

"script path is":"/cm/local/apps/cmd/scripts/sysinfo/head/outputscript.sh",

"CMDaemon running on":"",

"script running on":"basecm11",

"basecm11 UUID":"6733d33a-2933-41ea-aa3c-b218e784c8b9"

}


**Custom script placement—overview for placing on a regular node:** Placing this head script on a
regular node can be done by copying the script into a local directory on the node image, and rebooting
the regular node so that it picks up the image with the new local type script. After CMDaemon is
updated with the new sysinfo information, then, whenever sysinfo is run, the script is automatically
run by CMDaemon.


**Examples Of Running Custom Scripts In** sysinfo
The following example session makes the preceding concepts more explicit: the script is copied over
from the head node to the default image of a regular node. It goes into the directory location for custom
sysinfo scripts of the local type. Rebooting a node then installs the new script on the node:


**Example**


[root@basecm11 ~]# cp -r /cm/local/apps/cmd/scripts/sysinfo/head/outputscript.sh _\_
/cm/images/default-image/cm/local/apps/cmd/scripts/sysinfo/local/

[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% reboot node001

[the reboot of the node has to complete]


To update cmdaemon with the values from the new scripts for the node, the --update option to the
sysinfo command can be run for the node. Running sysinfo for the node then displays the output of
the scripts for the node. The sysinfo output value for Age shows how long it has been since CMDaemon
was updated by the scripts for the node:


**Example**


[basecm11->device]% sysinfo node001 --update

[basecm11->device]% sysinfo node001

...


**3.19 Cluster Configuration Without Execution By CMDaemon** **201**



Age 11s
CMDaemon running onscript running onnode001 UUID node001node0013b1c7973-07ef-419f-9324-4edf999690d5 



script running on node001
node001 UUIDscript path is 3b1c7973-07ef-419f-9324-4edf999690d5/cm/local/apps/cmd/scripts/sysinfo/local/outputscript.sh  local script







CMDaemon running onscript running onbasecm11 UUID node001basecm116733d33a-2933-41ea-aa3c-b218e784c8b9 



script running on basecm11
basecm11 UUIDscript path is 6733d33a-2933-41ea-aa3c-b218e784c8b9/cm/local/apps/cmd/scripts/sysinfo/head/outputscript.sh  head script







In the preceding example, the grouping braces are not part of the actual output. They are just part of
this explanation, and show that the first four lines after the Age line are from the local type script running
on node001. The four lines after that are from the head type script running on head, even though its
corresponding CMDaemon is running on node001 .


**Considerations Before Running Custom Scripts With** sysinfo
Although BCM gives the administrator the freedom to construct all kinds of custom sysinfo scripts,
some caution is urged before implementing the scripts. The following issues should at least be considered:


  - The scripts should be speedy. The scripts run asynchronously, but a script is expected to take less
than 15 seconds to run.


  - The data output should be small. JSON objects allow, for example, that megabyte-sized text could
be output by the sysinfo scripts. However, this is often unwise, given the nature of clusters. A
cluster with a 1000 nodes and 1MB blobs would mean that 1GB of memory is being moved around.


**3.19** **Cluster Configuration Without Execution By CMDaemon**


**3.19.1** **Cluster Configuration: The Bigger Picture**
The configurations carried out in this chapter so far are based almost entirely on configuring nodes, via
a CMDaemon front end ( cmsh or Base View), using CMDaemon to execute the change. Indeed, much of
this manual is about this too because it is the preferred technique. It is preferred:


  - because it is intended by design to be the easiest way to do common cluster tasks,


  - and also generally keeps administration overhead minimal in the long run since it is CMDaemon
rather than the system administrator that then takes care of tracking the cluster state.


There are however other cluster configuration techniques besides execution by CMDaemon. To get some
perspective on these, it should be noted that cluster configuration techniques are always fundamentally
about modifying a cluster so that it functions in a different way. The techniques can then for convenience
be separated out into modification techniques that rely on CMDaemon execution and techniques that
do not, as follows:


1. **Configuring nodes with execution by CMDaemon:** As explained, this is the preferred technique.
The remaining techniques listed here should therefore usually only be considered if the task cannot
be done with Base View or cmsh .


2. **Replacing the node image:** The image on a node can be replaced by an entirely different one, so
that the node can function in another way. This is covered in section 3.19.2. It can be claimed that
since it is CMDaemon that selects the image, this technique should perhaps be classed as under


**202** **Configuring The Cluster**


item 1. However, since the execution of the change is really carried out by the changed image
without CMDaemon running on the image, and because changing the entire image to implement
a change of functionality is rather extreme, this technique can be given a special mention outside
of CMDaemon execution.


3. **Using a** FrozenFile **directive:** Applied to a configuration file, this directive prevents CMDaemon from executing changes on that file for nodes. During updates, the frozen configuration may
therefore need to be changed manually. The prevention of CMDaemon acting on that file prevents the standard cluster functionality that would run based on a fully CMDaemon-controlled
cluster configuration. The FrozenFile directive is introduced in section 2.6.5, and covered in the
configuration context in section 3.19.3.


4. **Using an** initialize **or** finalize **script:** This type of script is run during the initrd stage, much
before CMDaemon on the regular node starts up. It is run if the functionality provided by the
script is needed before CMDaemon starts up, or if the functionality that is needed cannot be made
available later on when CMDaemon is started on the regular nodes. CMDaemon does not execute
the functionality of the script itself, but the script is accessed and set on the initrd via a CMDaemon
front end (Appendix E.2), and executed during the initrd stage. It is often convenient to carry out
minor changes to configuration files inside a specific image in this way, as shown by the example
in Appendix E.5. The initialize and finalize scripts are introduced in section 3.19.4.


5. **A shared directory:** Nodes can be configured to access and execute a particular software stored
on a shared directory of the cluster. CMDaemon does not execute the functionality of the software
itself, but is able to mount and share directories, as covered in section 3.13.


Finally, outside the stricter scope of cluster configuration adjustment, but nonetheless a broader way to
modify how a cluster functions, and therefore mentioned here for more completeness, is:


6. **Software management:** the installation, maintenance, and removal of software packages. Standard post-installation software management based on repositories is covered in sections 9.2–9.6.
Third-party software management from outside the repositories, for software that is part of BCM
is covered in Chapter 7 of the _Installation Manual_ .


Third-party software that is not part of BCM can be managed on the head node as on any other
Linux system, and is often placed under /opt or other recommended locations. If required by the
other nodes, then the software should typically be set up by the administrator so that it can be
accessed via a shared filesystem.


**3.19.2** **Making Nodes Function Differently By Image**

**Making All Nodes Function Differently By Image**
To change the name of the image used for an entire cluster, for example after cloning the image and
modifying it (section 3.19.2), the following methods can be used:


  - in Base View, via Cluster  - Settings  - Cluster name


  - or in cmsh from within the base object of partition mode


A system administrator more commonly sets the software image on a per-category or per-node basis
(section 3.19.2).


**Making Some Nodes Function Differently By Image**
For minor changes, adjustments can often be made to node settings via initialize and finalize scripts so
that nodes or node categories function differently (section 3.19.4).
For major changes on a category of nodes, it is usually more appropriate to have nodes function
differently from each other by simply carrying out image changes per node category with CMDaemon.
Carrying out image changes per node is also possible. As usual, node settings override category settings.


**3.19 Cluster Configuration Without Execution By CMDaemon** **203**


**Modifying images via cloning primitives for a node or category:** Setting a changed image for a category can be done as follows with cmsh :


1. The image on which the new one will be based is cloned. The cloning operation not only copies
all the settings of the original (apart from the name), but also the data of the image:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% softwareimage

[basecm11->softwareimage]% clone default-image imagetwo

[basecm11->softwareimage*[imagetwo*]]% commit
... [notice] basecm11: Started to copy: /cm/images/default-image -> /cm/images/imagetwo

[basecm11->softwareimage*[imagetwo*]]%
... [notice] basecm11: Copied: /cm/images/default-image -> /cm/images/imagetwo

[basecm11->softwareimage[imagetwo]]%


2. After cloning, the settings can be modified in the new object. For example, if the kernel needs to be
changed to suit nodes with different hardware, kernel modules settings are changed (section 5.3.2)
and committed. This creates a new image with a new ramdisk.


Other ways of modifying and committing the image for the nodes are also possible, as discussed
in sections 9.2–9.6.


3. The modified image that is to be used by the differently functioning nodes is placed in a new
category in order to have the nodes be able to choose the image. To create a new category easily, it
can simply be cloned. The image that the category uses is then set:


[basecm11->softwareimage[imagetwo]]% category

[basecm11->category]% clone default categorytwo

[basecm11->category*[categorytwo*]]% set softwareimage imagetwo

[basecm11->category*[categorytwo*]]% commit

[basecm11->category[categorytwo]]%


4.  - For just one node, or a few nodes, the node can be set from device mode to the new category
(which has the new image):


[basecm11->category[categorytwo]]% device

[basecm11->device]% use node099

[basecm11->device[node099]]% set category categorytwo

[basecm11->device*[node099*]]% commit; exit


    - If there are many nodes, for example node100 sequentially up to node200, they can be set to
that category using a foreach loop like this:


**Example**


[basecm11->device]% foreach -n node100..node200 (set category categorytwo)

[basecm11->device*]% commit


5. Rebooting restarts the nodes that are assigned to the new category with the new image.


**Modifying images by adding files in the** cm/conf **directory, for a category, node, or MAC address:**
The preceding 5-step method is understandable. For just a few file changes it is perhaps overkill and
not very elegant. BCM has a more structured and efficient way to make some nodes function differently
by image if only a few file additions are to be carried out. The specification adds the files in the image
via a target path that is specified in special configuration locations in the image. It can be configured per
node, but also per category and MAC address.


**204** **Configuring The Cluster**


  - For a category, the specification takes the form:


/cm/images/< _image_ >/cm/conf/category/< _category_ >/< _target_   

Thus, if some file on the node is to be placed so that on a running node it is at /path/to/some.file,
and this needs to be configured for an image default-image, and a category default, then it
would be placed at this location on the head node:


**Example**


/cm/images/default-image/cm/conf/category/default/path/to/some.file


The file on the target node would be placed in the absolute directory /path/to/some.file


Multiple categories can be configured per image. Thus, for example, beside the default category,
an additional gpu category can exist:


**Example**


/cm/images/default-image/cm/conf/category/gpu/path/to/some.file


Also, multiple files can be specified per category per image. Thus, beside the file some.file, an
additional file some.other.file could be placed:


**Example**


/cm/images/default-image/cm/conf/category/gpu/path/to/some.file
/cm/images/default-image/cm/conf/category/gpu/path/to/some.other.file


  - For a node, the configuration form is:


/cm/images/< _image_ >/cm/conf/node/< _node name_ >/< _target_   

An example for a node called node001 could then be:


**Example**


/cm/images/default-image/cm/conf/node/node001/path/to/some.file


  - For a MAC address, the configuration form is:


/cm/images/< _image_ >/cm/conf/node/< _MAC address_ >/< _target_   

An example for a node with MAC address 00:aa:bb:cc:dd:ee could then be:


**Example**


/cm/images/default-image/cm/conf/node/00-aa-bb-cc-dd-ee/path/to/some.file


The copying of the specified files to the image is done just before the finalize stage of the nodeinstaller (section 5.4.11) during node provisioning.
A common theme in BCM is that node-level configuration overrides category-level configuration. In
keeping with this behavior, a file configuration at category level could be applied to the many nodes in
a category. And, a file configuration copy at node level (for a node that is in the category) overrides the
category level value for just that particular node.


**3.19 Cluster Configuration Without Execution By CMDaemon** **205**


**3.19.3** **Making All Nodes Function Differently From Normal Cluster Behavior With**

FrozenFile

Configuration changes carried out by Base View or cmsh often generate, restore, or modify configuration
files (Appendix A).
However, sometimes an administrator may need to make a direct change (without using Base View
or cmsh ) to a configuration file to set up a special configuration that cannot otherwise be done.
The FrozenFile directive to CMDaemon (Appendix C, page 857) applied to such a configuration file
stops CMDaemon from altering the file. The frozen configuration file is generally applicable to all nodes
and is therefore a possible way of making all nodes function differently from their standard behavior.
Freezing files is however best avoided, if possible, in favor of a CMDaemon-based method of configuring nodes, for the sake of administrative maintainability.


**3.19.4** **Adding Functionality To Nodes Via An** initialize **Or** finalize **Script**
CMDaemon can normally be used to allocate different images per node or node category as explained
in section 3.19.2. However, some configuration files do not survive a reboot (Appendix A), sometimes
hardware issues can prevent a consistent end configuration, and sometimes drivers need to be initialized before provisioning of an image can happen. In such cases, an initialize or finalize script
(sections 5.4.5, 5.4.11, and Appendix E.5) can be used to initialize or configure nodes or node categories.
These scripts are also useful because they can be used to implement minor changes across nodes:


**Example**


Supposing that some nodes with a particular network interface have a problem auto-negotiating
their network speed, and default to 100Mbps instead of the maximum speed of 1000Mbps.
Such nodes can be set to ignore auto-negotiation and be forced to use the 1000Mbps speed
by using the ETHTOOL_OPTS configuration parameter in their network interface configuration file:
/etc/sysconfig/network-scripts/ifcfg-eth0 (or /etc/sysconfig/network/ifcfg-eth0 in SUSE).
The ETHTOOL_OPTS parameter takes the options to the “ ethtool -s <device> ” command as options.
The value of _<device>_ (for example eth0 ) is specified by the filename that is used by the configuration file
itself (for example /etc/sysconfig/network-scripts/ifcfg-eth0 ). The ethtool package is installed
by default with BCM. Running the command:


ethtool -s autoneg off speed 1000 duplex full


turns out after some testing to be enough to reliably get the network card up and running at 1000Mbps
on the problem hardware.
However, since the network configuration file is overwritten by node-installer settings during reboot,
a way to bring persistence to the file setting is needed. One way to ensure persistence is to append
the configuration setting to the file with a finalize script, so that it gets tagged onto the end of the
configuration setting that the node-installer places for the file, just before the network interfaces are
taken down again in preparation for init .
The script may thus look something like this for a Red Hat system:


#!/bin/bash