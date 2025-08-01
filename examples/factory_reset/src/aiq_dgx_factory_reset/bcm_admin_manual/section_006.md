# no need for rescue on nodes with a boot role

/rescue

/rescue/*


**5.3** **The Kernel Image, Ramdisk And Kernel Modules**


A _software image_ is a complete Linux filesystem that is to be installed on a non-head node. Chapter 9
describes images and their management in detail.
The head node holds the head copy of the software images. Whenever files in the head copy are
changed using CMDaemon, the changes automatically propagate to all provisioning nodes via the
updateprovisioners command (section 5.2.4).


**5.3.1** **Booting To A “Good State” Software Image**
When nodes boot from the network in simple clusters, the head node supplies them with a _known good_
_state_ during node start up. The known good state is maintained by the administrator and is defined
using a software image that is kept in a directory of the filesystem on the head node. Supplementary
filesystems such as /home are served via NFS from the head node by default.
For a diskless node the known good state is copied over from the head node, after which the node
becomes available to cluster users.

For a disked node, by default, the hard disk contents on specified local directories of the node are
checked against the known good state on the head node. Content that differs on the node is changed to
that of the known good state. After the changes are done, the node becomes available to cluster users.
Each software image contains a Linux kernel and a ramdisk. These are the first parts of the image
that are loaded onto a node during early boot. The kernel is loaded first. The ramdisk is loaded next,
and contains driver modules for the node’s network card and local storage. The rest of the image is
loaded after that, during the node-installer stage (section 5.4).


**5.3.2** **Selecting Kernel Driver Modules To Load Onto Nodes**
Kernel modules can be managed in softwareimage mode (using an image), in category mode (using a
category), or in device mode (using a node), as indicated by the following cmsh tree view of a newly

**238** **Node Provisioning**


installed cluster with default values:


cmsh

|-- category[default]

| |-- kernelmodules

...

|-- device][node001]

| |-- kernelmodules

...

|-- softwareimage[default-image]

| |-- kernelmodules

...


As is usual in BCM, if there are values specified at the lower levels in the hierarchy, then their values
override the values set higher up in the hierarchy. For example, modules specified at node level override
modules specified at category or software image level. Similarly modules specified at the category level
override whatever is specified at the software image level. The cluster administrators should be aware
that “override” for kernel modules appended to a kernel image means that any kernel modules defined
at a higher level are totally ignored—the modules from a lower level exclude the modules at the higher
level. A misconfiguration of kernel modules in the lower levels can thus prevent the node from starting

up.
Modules are normally just set at softwareimage level, using cmsh or Base View.


**Kernel Driver Modules With** cmsh

In cmsh, the modules that are to go on the ramdisk can be placed using the kernelmodules submode of
the softwareimage mode. The order in which they are listed is the attempted load order.
Within the kernelmodules submode, the import command can be used to import the kernel modules
list from a software image, from a node, or from a category, replacing the original kernel modules list.
Whenever a change is made via the kernelmodules submode to the kernel module selection of a
software image, CMDaemon automatically runs the createramdisk command. The createramdisk
command regenerates the ramdisk inside the initrd image and sends the updated image to all provisioning nodes, to the image directory, set by default to /cm/images/default-image/boot/ . The original
initrd image is saved as a file with suffix “ .orig ” in that directory. An attempt is made to generate the
image for all software images that CMDaemon is aware of, regardless of category assignment, unless
the image is protected from modification by CMDaemon with a FrozenFile directive (Appendix C).
The createramdisk command can also be run manually from within the softwareimage mode.


**Kernel Driver Modules With Base View**

In Base View the kernel modules for a particular image are managed through the Software images
resource, and then choosing the Kernel modules menu option of that image. For example, for the image
default-image, the navigation path that can be followed is:
Provisioning - Software images[default-image] - Edit - Settings - Kernel modules
which opens up the Kernel Module list screen, which allows kernel modules to be removed or added
(figure 5.6):


**5.3 The Kernel Image, Ramdisk And Kernel Modules** **239**


Figure 5.6: Base View: Selecting Kernel Modules For Software Images


New kernel modules can be added using the Add button, existing kernel modules can be removed
using the Delete button, and kernel module parameters can be edited using the Edit button.


**Manually Regenerating A Ramdisk**
Regenerating a ramdisk manually via cmsh or Base View is useful if the kernel or modules have changed
without using CMDaemon. For example, after running a YUM update which has modified the kernel or
modules of the nodes (section 9.3). In such a case, the distribution would normally update the ramdisk
on the machine, but this is not done for the extended ramdisk for nodes in BCM. Not regenerating the
BCM ramdisk for nodes after such an update means the nodes may fail on rebooting during the loading
of the ramdisk (section 5.8.4).
An example of regenerating the ramdisk is seen in section 5.8.5.


**Implementation Of Kernel Driver Via Ramdisk Or Kernel Parameter**
Sometimes, testing or setting a kernel driver as a kernel parameter may be more convenient. How to do
that is covered in section 9.3.4.


**5.3.3** **InfiniBand Provisioning**
On clusters that have InfiniBand hardware, it is normally used for data transfer as a service after the
nodes have fully booted up (section 3.6). It can also be used for PXE booting (section 5.1.3) and for node
provisioning (described here), but these are not normally a requirement. This section (about InfiniBand
node provisioning) may therefore safely be skipped in almost all cases when first configuring a cluster.
During node start-up on a setup for which InfiniBand networking has been enabled, the init process
runs the rdma script. For SLES the openib script is used instead of the rdma script. The script loads
up InfiniBand modules into the kernel. When the cluster is finally fully up and running, the use of
InfiniBand is thus available for all processes that request it.
Provisioning nodes over InfiniBand is not implemented by default, because the init process, which
handles initialization scripts and daemons, takes place only after the node-provisioning stage launches.
InfiniBand modules are therefore not available for use during provisioning, which is why, for default
kernels, provisioning in BCM is done via Ethernet.
Provisioning at the faster InfiniBand speeds rather than Ethernet speeds is however a requirement
for some clusters. To get the cluster to provision using InfiniBand requires both of the following two
configuration changes to be carried out:


**240** **Node Provisioning**


1. configuring InfiniBand drivers for the ramdisk image that the nodes first boot into, so that provisioning via InfiniBand is possible during this pre- init stage


2. defining the provisioning interface of nodes that are to be provisioned with InfiniBand. It is assumed that InfiniBand networking is already configured, as described in section 3.6.


The administrator should be aware that the interface from which a node boots, (conveniently labeled BOOTIF ), must not be an interface that is already configured for that node in CMDaemon.
For example, if BOOTIF is the device ib0, then ib0 must not already be configured in CMDaemon.
Either BOOTIF or the ib0 configuration should be changed so that node installation can succeed.


How these two changes are carried out is described next:


**InfiniBand Provisioning: Ramdisk Image Configuration**
An easy way to see what modules must be added to the ramdisk for a particular HCA can be found by
running rdma (or openibd ), and seeing what modules do load up on a fully booted regular node.
One way to do this is to run the following lines as root:


[root@basecm11 ~]# { service rdma stop; lsmod | cut -f1 -d" "; }>/tmp/a

[root@basecm11 ~]# { service rdma start; lsmod | cut -f1 -d" "; }>/tmp/b


The rdma service in the two lines should be replaced by openibd service instead when using SLES, or
distributions based on versions of Red Hat prior to version 6.
The first line stops the InfiniBand service, just in case it is running, in order to unload its modules,
and then lists the modules on the node.

The second line starts the service, so that the appropriate modules are loaded, and then lists the
modules on the node again. The output of the first step is stored in a file a, and the output from the
second step is stored in a file b .
Running diff on the output of these two steps then reveals the modules that get loaded. For rdma,
the output may display something like:


**Example**


[root@basecm11 ~]# diff /tmp/a /tmp/b

1,3c1

< Unloading OpenIB kernel modules:

< Failed to unload ib_core

< [FAILED]

--
- Loading OpenIB kernel modules: [ OK ]

4a3,14

- ib_ipoib

- rdma_ucm

- ib_ucm

- ib_uverbs

- ib_umad

- rdma_cm

- ib_cm

- iw_cm

- ib_addr

- ib_sa

- ib_mad

- ib_core


As suggested by the output, the modules ib_ipoib, rdma_ucm and so on are the modules loaded
when rdma starts, and are therefore the modules that are needed for this particular HCA. Other HCAs
may cause different modules to be loaded.


**5.3 The Kernel Image, Ramdisk And Kernel Modules** **241**


For a default Red Hat from version 7 onward, the rdma service can only be started; it cannot be
stopped. Finding the modules that load can therefore only be done once for the default configuration,
until the next reboot.

The preceding lsmod lines in that case can be generated with:


**Example**


[root@basecm11 ~]# { lsmod | cut -f1 -d" "; }>/tmp/a

[root@basecm11 ~]# { systemctl start rdma-load-modules@rdma; lsmod | cut -f1 -d" "; }>/tmp/b


Here, systemctl is used instead of the older service command just because it is the modern way to
run such commands.

The InfiniBand modules that load are the ones that the initrd image needs, so that InfiniBand can be
used during the node provisioning stage. The administrator can therefore now create an initrd image
with the required InfiniBand modules.
Loading kernel modules into a ramdisk is covered in general in section 5.3.2. A typical Mellanox
HCA may have an initrd image created as follows (some text ellipsized in the following example):


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% softwareimage use default-image

[basecm11->softwareimage[default-image]]% kernelmodules

[basecm11...age[default-image]->kernelmodules]% add mlx4_ib

[basecm11...age*[default-image*]->kernelmodules*[mlx4_ib*]]% add ib_ipoib

[basecm11...age*[default-image*]->kernelmodules*[ib_ipoib*]]% add ib_umad

[basecm11...age*[default-image*]->kernelmodules*[ib_umad*]]% commit

[basecm11->softwareimage[default-image]->kernelmodules[ib_umad]]%

Tue May 24 03:45:35 2011 basecm11: Initial ramdisk for image default-image was regenerated successfully.


If the modules are put in another image instead of default-image, then the default image that nodes
boot from should be set to the new image (section 3.19.2).


**InfiniBand Provisioning: Network Configuration**
It is assumed that the networking configuration for the final system for InfiniBand is configured following the general guidelines of section 3.6. If it is not, that should be checked first to see if all is well with
the InfiniBand network.
The provisioning aspect is set by defining the provisioning interface. An example of how it may be
set up for 150 nodes with a working InfiniBand interface ib0 in cmsh is:


**Example**


[root@basecm11~]# cmsh

[basecm11]% device

[basecm11->device]% foreach -n node001..node150 (set provisioninginterface ib0)

[basecm11->device*]% commit


**5.3.4** **VLAN Provisioning**
Nodes can be configured for provisioning over a VLAN interface, starting in NVIDIA Base Command
Manager version 8.2.
This requires:


  - A VLAN network and node interface. The VLAN network is typically specified by the network
switch. The interface that connects the node to the switch can be configured as a VLAN interface
as outlined in section 3.4.


**242** **Node Provisioning**


  - The 8021q ( rtnl-link-vlan ) driver to be available in the software image that is provisioned. In
recent distributions this driver is not part of the base kernel, and is instead available as a module.
The module should be loaded into the software image that is to be provisioned. For example, for
node001 that is missing the module in the software image, the module could be configured to run
on the node from the software image as follows:


**Example**


[root@basecm11 ~]# ssh node001 "lsmod | grep 8021q"

[root@basecm11 ~]# cmsh

[basecm11]% softwareimage

[basecm11]->softwareimage% use default-image

[basecm11->softwareimage[default-image]]% kernelmodules

[basecm11->softwareimage[default-image]->kernelmodules]% list | grep 8021q

[basecm11->softwareimage[default-image]->kernelmodules]% add 8021q

[basecm11->softwareimage*[default-image*]->kernelmodules*[8021q*]]% commit


[basecm11->softwareimage[default-image]->kernelmodules[8021q]]% device use node001

[basecm11->device[node001]]% reboot

...

_some time after boot_

[root@basecm11 ~]# ssh node001 "lsmod | grep 8021q"

8021q 40960 0

garp 16384 1 8021q

mrp 20480 1 8021q


Rebooted nodes that use the modified software image then have the VLAN module available in
the running kernel.


  - The BIOS of the node must have the VLANID value set within the BIOS network options. If the
BIOS does not support this setting, then PXE over VLAN cannot work. For a NIC that is missing
this in the BIOS, the NIC hardware provider may sometimes have a BIOS update that supports
this setting.


  - The VLANID value should be set in the kernel parameters. Kernel parameters for a node can be
specified in cmsh with the kernelparameters setting of softwareimage mode (section 9.3.4). An
example where the VLANID is appended to some existing parameters could be:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% softwareimage use default-image

[basecm11->softwareimage[default-image]]% append kernelparameters " VLANID=89"

[basecm11->softwareimage*[default-image*]]% commit


**5.4** **Node-Installer**


After the kernel has started up, and the ramdisk kernel modules are in place on the node, the node
launches the node-installer.

The node-installer is a software image (section 9.4.4) provided by the head node. It interacts with
CMDaemon on the head node and takes care of the rest of the boot process.
As an aside, the node-installer modifies some files (Appendix A.2.3) on the node it is installing to,
so that they differ from the otherwise-expected pre-init stage Linux system. Such modifications can be
prevented by a frozenFilesPerNode or frozenFilesPerCategory directive, as documented within the
node-installer.conf file, and explained in greater detail on page 858.


**5.4 Node-Installer** **243**


Once the node-installer has completed its tasks, the local drive of the node has a complete Linux
pre-init stage system. The node-installer ends by calling /sbin/init from the local drive and the boot
process then proceeds as a normal Linux boot.
The steps the node-installer goes through for each node are:


1. requesting a node certificate (section 5.4.1)


2. deciding or selecting node configuration (section 5.4.2)


3. starting up all network interfaces (section 5.4.3)


4. determining install-mode type and execution mode (section 5.4.4)


5. running initialize scripts (section 5.4.5)


6. checking partitions, mounting filesystems (section 5.4.6)


7. synchronizing the local drive with the correct software image (section 5.4.7)


8. writing network configuration files to the local drive (section 5.4.8)


9. creating an /etc/fstab file on the local drive (section 5.4.9)


10. installing GRUB bootloader if configured by BCM (section 5.4.10), and initializing SELinux if it has
been installed and configured (Chapter 12 of the _Installation Manual_ )


11. running finalize scripts (section 5.4.11)


12. unloading specific drivers no longer needed (section 5.4.12)


13. switching the root device to the local drive and calling /sbin/init (section 5.4.13)


These 13 node-installer steps and related matters are described in detail in the corresponding sections
5.4.1–5.4.13.


**5.4.1** **Requesting A Node Certificate**
Each node communicates with the CMDaemon on the head node using a certificate. If no certificate is
found, it automatically requests one from CMDaemon running on the head node (figure 5.7).


**244** **Node Provisioning**


Figure 5.7: Certificate Request


The certificate is stored on the head node in /cm/node-installer/certificates/ by MAC address.


**Certificate Auto-signing**
_Certificate auto-signing_ means the cluster management daemon automatically signs a certificate signing
request (CSR) that has been requested by a node. Certificate auto-signing can be configured from within
partition mode of cmsh, with the signinstallercertificates parameter. It can take one of the following values:


 - AUTO (the default)


 - MANUAL


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% partition

[basecm11->partition[base]]% set signinstallercertificates auto


For untrusted networks, it may be wiser to approve certificate requests manually to prevent new nodes
being added automatically without getting noticed.
Disabling certificate auto-signing for all networks can be done by setting
signinstallercertificates to MANUAL .
Instead of disabling certificate autosigning for all networks, a finer tuning can be carried out for
individual networks. This requires that signinstallercertificates be set to AUTO in partition mode.
The allowautosign parameter in network mode can then be set for a particular network, and it can take
one of the following values:


 - Always


 - Automatic (the default)


 - Never


**5.4 Node-Installer** **245**


 - Secret


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% network use internalnet

[basecm11->network[internalnet]]% set allowautosign automatic _<TAB><TAB>_

always automatic never secret


If Always is set, then incoming CSRs from all types of networks are automatically auto-signed.
If Automatic is set, then only networks that are of type internal are automatically auto-signed.
If Never is set, then all incoming CSRs that come in for that network have to be manually approved.
The value Secret is required for the globalnet network, for edge sites. A node on an edge site uses
a shared secret that is passed along with the node request. The secret is set during edge site setup by
BCM (section 2.1.1 of the _Edge Manual_ ).


**Manual Approval Of A CSR**
**Approval of the CSR from a regular node (not an edge node):** Manual approval of a CSR is typically done from within certs mode. A list of requests can be found, and from the list, the appropriate
unsigned request can be signed and issued. The following session illustrates the process:


[basecm11->cert]% listrequests

Request ID Client type Session ID Autosign Name

------------ ------------ ------------ -------- -----------------
6 installer 42949672986 No fa-16-3e-22-cd-13

[basecm11->cert]% issuecertificate 6

Issued 6


**Approval of the CSR from an edge node:** If the shared secret has not been set for the edge director—
that is, if it has not been stored locally on the edge director, or if it has not been passed on via the
installation medium—then the node-installer prompts for the secret the first time that it boots. If the
secret that is typed in matches the site secret, then a CSR from the edge director is handled by the head
node, and a signed certificate is issued.
The edge compute nodes pick up their secret from the director. If the director does not have the
secret, then the compute node’s node-installer prompts for the secret on first boot. Once the secret is
set, then edge compute node sends its CSR to the head node (via the edge director) and gets a signed
certificate automatically.


Section 2.3 has more information on certificate management in general.


**Certificate Storage And Removal Implications**
After receiving a valid certificate, the node-installer stores it in
/cm/node-installer/certificates/< _node mac address_ >/ on the head node. This directory is NFS
exported to the nodes, but can only be accessed by the root user. The node-installer does not request a
new certificate if it finds a certificate in this directory, valid or invalid.
If an invalid certificate is received, the screen displays a communication error. Removing the node’s
corresponding certificate directory allows the node-installer to request a new certificate and proceed
further.


**5.4.2** **Deciding Or Selecting Node Configuration**
Once communication with the head node CMDaemon is established, the node-installer tries to identify
the node it is running on so that it can select a configuration from CMDaemon’s record for it, if any such
record exists. It correlates any node configuration the node is expected to have according to network
hardware detected. If there are issues during this correlation process then the administrator is prompted
to select a node configuration until all nodes finally have a configuration.


**246** **Node Provisioning**


**Possible Node Configuration Scenarios**
The correlations process and corresponding scenarios are now covered in more detail:
It starts with the node-installer sending a query to CMDaemon to check if the MAC address used
for net booting the node is already associated with a node in the records of CMDaemon. In particular,
it checks the MAC address for a match against the existing _node configuration_ properties, and decides
whether the node is _known_ or _new_ .


  - the node is **known** if the query matches a node configuration. It means that node has been booted
before.


  - the node is **new** if no configuration is found.


In both cases the node-installer then asks CMDaemon to find out if the node is connected to an
Ethernet switch, and if so, to which port. Setting up Ethernet switches for port detection is covered in
section 3.9.

If a port is detected for the node, the node-installer queries CMDaemon for a node configuration
associated with the detected Ethernet switch port. If a port is not detected for the node, then either
the hardware involved with port detection needs checking, or a node configuration must be selected
manually.
There are thus several scenarios:


1. The node is new, and an Ethernet switch port is detected. A node configuration associated with
the port is found. The node-installer suggests to the administrator that the new node should use
this configuration, and displays the configuration along with a confirmation dialog (figure 5.8).
This suggestion can be interrupted, and other node configurations can be selected manually instead through a sub-dialog (figure 5.9). By default (in the main dialog), the original suggestion is
accepted after a timeout.


Figure 5.8: Scenarios: Configuration Found, Confirm Node Configuration


**5.4 Node-Installer** **247**


Figure 5.9: Scenarios: Node Selection Sub-Dialog


2. The node is new, and an Ethernet switch port is detected. A node configuration associated with
the port is not found. The node-installer then displays a dialog that allows the administrator to
either retry Ethernet switch port detection (figure 5.10) or to drop into a sub-dialog to manually
select a node configuration (figure 5.9). By default, port detection is retried after a timeout.


Figure 5.10: Scenarios: Unknown Node, Ethernet Port Detected


3. The node is new, and an Ethernet switch port is not detected. The node-installer then displays a


**248** **Node Provisioning**


dialog that allows the user to either retry Ethernet switch port detection (figure 5.11) or to drop
into a sub-dialog to manually select a node configuration (figure 5.9). By default, port detection is
retried after a timeout.


Figure 5.11: Scenarios: Unknown Node, No Ethernet Port Detected


4. The node is known, and an Ethernet switch port is detected. The configuration associated with the
port is the same as the configuration associated with the node’s MAC address. The node-installer
then displays the configuration as a suggestion along with a confirmation dialog (figure 5.8). The
suggestion can be interrupted, and other node configurations can be selected manually instead
through a sub-dialog (figure 5.9). By default (in the main dialog), the original suggestion is accepted after a timeout.


5. The node is known, and an Ethernet switch port is detected. However, the configuration associated
with the port is not the same as the configuration associated with the node’s MAC address. This is
called a _port mismatch_ . This type of port mismatch situation occurs typically during a mistaken _node_
_swap_, when two nodes are taken out of the cluster and returned, but their positions are swapped
by mistake (or equivalently, they are returned to the correct place in the cluster, but the switch
ports they connect to are swapped by mistake). To prevent configuration mistakes, the nodeinstaller displays a port mismatch dialog (figure 5.12) allowing the user to retry, accept a node
configuration that is associated with the detected Ethernet port, or to manually select another
node configuration via a sub-dialog (figure 5.9). By default (in the main port mismatch dialog),
port detection is retried after a timeout.


**5.4 Node-Installer** **249**


Figure 5.12: Scenarios: Port Mismatch Dialog


6. The node is known, and an Ethernet switch port is not detected. However, the configuration
associated with the node’s MAC address does have an Ethernet port associated with it. This is
also considered a port mismatch. To prevent configuration mistakes, the node-installer displays a
port mismatch dialog similar to figure 5.12, allowing the user to retry or to drop into a sub-dialog
and manually select a node configuration that may work.


However, a more likely solution in most cases is to:


    - either clear the switch port configuration in the cluster manager so that switch port detection
is not attempted. For example, for node001, this can be done by running this cmsh command
on the head node:

cmsh -c "device clear node001 switchports; commit"


    - or enable switch port detection on the switch. This is usually quite straightforward, but may
require going through the manuals or software application that the switch manufacturer has
provided.


By default (in the port mismatch dialog), port detection is retried after a timeout. This means
that if the administrator clears the switch port configuration or enables switch port detection, the
node-installer is able to continue automatically with a consistent configuration.


7. The node is known, and an Ethernet switch port is detected. However, the configuration associated
with the node’s MAC address has no Ethernet switch port associated with it. This is not considered
a port mismatch but an unset switch port configuration, and it typically occurs if switch port
configuration has not been carried out, whether by mistake or deliberately. The node-installer
displays the configuration as a suggestion along with a confirmation dialog (figure 5.13). The
suggestion can be interrupted, and other node configurations can be selected manually instead
using a sub-dialog. By default (in the main dialog) the configuration is accepted after a timeout.


**250** **Node Provisioning**


Figure 5.13: Scenarios: Port Unset Dialog


A truth table summarizing the scenarios is helpful:



~~**Switch**~~

**port**
**config-**
**uration**

**found?**



**Node**
**Scenario**
**known?**



**Switch**

**port de-**
**tected?**



**Switch port configuration conflicts with node configu-**
**ration?**



1 No Yes Yes No


2 No Yes No No


3 No No No No


4 Yes Yes Yes No


5 Yes Yes Yes Yes (configurations differ)


6 Yes No Yes Yes (port expected by MAC configuration not found)


7 Yes Yes No No (port not expected by MAC configuration)


In these scenarios, whenever the user manually selects a node configuration in the prompt dialog,
an attempt to detect an Ethernet switch port is repeated. If a port mismatch still occurs, it is handled by
the system as if the user has not made a selection.


**Summary Of Behavior During Hardware Changes**
The logic of the scenarios means that an unpreconfigured node always boots to a dialog loop requiring
manual intervention during a first install (scenarios 2 and 3). For subsequent boots the behavior is:


  - If the node MAC hardware has changed (scenarios 1, 2, 3):


**–**
if the node is new and the detected port has a configuration, the node automatically boots to
that configuration (scenario 1).


**–**
else manual intervention is needed (scenarios 2, 3)


**5.4 Node-Installer** **251**


  - If the node MAC hardware has not changed (scenarios 4, 5, 6, 7):


**–**
if there is no port mismatch, the node automatically boots to its last configuration (scenarios
4, 7).


**–**
else manual intervention is needed (scenarios 5, 6).


**The** newnodes **Command**

newnodes **basic use:** New nodes that have not been configured yet can be detected using the newnodes
command from within the device mode of cmsh . A new node is detected when it reaches the node
installer stage after booting, and contacts the head node.


**Example**


[basecm11->device]% newnodes

The following nodes (in order of appearance) are waiting to be assigned:

MAC First appeared Detected on switch port

----------------- ----------------------------- ----------------------
00:0C:29:01:0F:F8 Mon, 14 Feb 2011 10:16:00 CET [no port detected]


At this point the node-installer is seen by the administrator to be looping, waiting for input on what
node name is to be assigned to the new node.
The nodes can be uniquely identified by their MAC address or switch port address.
The port and switch to which a particular MAC address is connected can be discovered by using
the showport command (section 3.10.4). After confirming that they are appropriate, the switchports
property for the specified device can be set to the port and switch values.


**Example**


[basecm11->device]% showport 00:0C:29:01:0F:F8

switch01:8

[basecm11->device]% set node003 switchports switch01:8

[basecm11->device*]% commit


When the node name ( node003 in the preceding example) is assigned, the node-installer stops looping and goes ahead with the installation to the node.
The preceding basic use of newnodes is useful for small numbers of nodes. For larger number of
nodes, the advanced options of newnodes may help carry out node-to-MAC assignment with less effort.


newnodes **advanced use—options:** The list of MAC addresses discovered by a newnodes command can
be assigned in various ways to nodes specified by the administrator. Node objects should be created in
advance to allow the assignment to take place. The easiest way to set up node objects in cmsh is to use
the --clone option of the foreach command (section 2.5.5, page 65).
The advanced options of newnodes are particularly useful for quickly assigning node names to specific physical nodes. All that is needed is to power the nodes up in the right order. For nodes with the
same hardware, the node that is powered up first reaches the stage where it tries to connect with the
node-installer first. So its MAC address is detected first, and arrives on the list generated by newnodes
first. If some time after the first node is powered up, the second node is powered up, then its MAC
address becomes the second MAC address on the list, and so on for the third, fourth, and further nodes.
When assigning node names to a physical node, on a cluster that has no such assignment already,
the first node that arrived on the list gets assigned the name node001, the second node that arrived on
the list gets assigned the name node002 and so on.
The advanced options are shown in device mode by running the help newnodes command. The
options can be introduced as being of three kinds: straightforward, grouping, and miscellaneous:


  - The straightforward options:


**252** **Node Provisioning**


-n|--nodes


-w|--write


-s|--save


Usually the most straightforward way to assign the nodes is to use the -n option, which accepts
a list of nodes, together with a -w or -s option. The -w ( --write ) option sets the order of nodes
to the corresponding order of listed MAC addresses, and is the same as setting an object in cmsh .
The -s ( --save ) option is the same as setting and committing an object in cmsh, so -s implies a -w
option is run at the same time.


So, for example, if 8 new nodes are discovered by the node-installer on a cluster with no nodes so
far, then:


**Example**


[basecm11->device]% newnodes -w -n node001..node008


assigns (but does not commit) the sequence node001 to node008 the new MAC address according
to the sequence of MAC addresses displaying on the list.


  - The grouping options:


-g|--group


-c|--category


-h|--chassis


-r|--rack


The “ help newnodes ” command in device mode shows assignment options other than -n for a
node range are possible. For example, the assignments can also be made for a group ( -g ), per
category ( -c ), per chassis ( -h ), and per rack ( -r ).


  - The miscellaneous options:


-f|--force


-o|--offset


By default, the newnodes command fails when it attempts to set a node name that is already taken.
The -f ( --force ) option forces the new MAC address to be associated with the old node name.
When used with an assignment grouping, (node range, group, category, chassis, or rack) all the
nodes in the grouping lose their node-to-MAC assignments and get new assignments. The -f
option should therefore be used with care.


The -o ( --offset ) option takes a number _<number>_ and skips _<number>_ nodes in the list of detected unknown nodes, before setting or saving values from the assignment grouping.


Examples of how to use the advanced options follow.


newnodes **advanced use—range assignment behavior example:** For example, supposing there is a
cluster with nodes assigned all the way up to node022. That is, CMDaemon knows what node is
assigned to what MAC address. For the discussion that follows, the three nodes node020, node021,
node022 can be imagined as being physically in a rack of their own. This is simply to help to visualize a
layout in the discussion and tables that follow and has no other significance. An additional 3 new, that
is unassigned, nodes are placed in the rack, and allowed to boot and get to the node-installer stage.
The newnodes command discovers the new MAC addresses of the new nodes when they reach their
node-installer stage, as before (the switch port column is omitted in the following text for convenience):


**5.4 Node-Installer** **253**


**Example**


[basecm11->device]% newnodes

MAC First appeared

----------------- ----------------------------
00:0C:29:EF:40:2A Tue, 01 Nov 2011 11:42:31 CET

00:0C:29:95:D3:5B Tue, 01 Nov 2011 11:46:25 CET

00:0C:29:65:9A:3C Tue, 01 Nov 2011 11:47:13 CET


The assignment of MAC to node address could be carried out as follows:


**Example**


[basecm11->device]% newnodes -s -n node023..node025

MAC First appeared Hostname

-------------------- ----------------------------- -------
00:0C:29:EF:40:2A Tue, 01 Nov 2011 11:42:31 CET node023

00:0C:29:95:D3:5B Tue, 01 Nov 2011 11:46:25 CET node024

00:0C:29:65:9A:3C Tue, 01 Nov 2011 11:47:13 CET node025


Once this is done, the node-installer is able to stop looping, and to go ahead and install the new
nodes with an image.
The physical layout in the rack may then look as indicated by this:


node023 ...A


node024 ...B


node025 ...C

|before after|Col2|
|---|---|
|node020|node020|
|node021|node021|
|node022|node022|
||node023|
||node024|
||node025|



Here, node023 is the node with the MAC address ending in A .
If instead of the previous newnodes command, an offset of 1 is used to skip assigning the first new
node:


**Example**


[basecm11->device]% newnodes -s -o 1 node024..node025


then the rack layout looks like:

|before after|Col2|
|---|---|
|node020|node020|
|node021|node021|
|node022|node022|
||_unassigned_|
||node024|
||node025|



Here, _unassigned_ is where node023 of the previous example is physically located, that is, the node
with the MAC address ...A . The lack of assignment means there is actually no association of the name


**254** **Node Provisioning**


node023 with that MAC address, due to the newnodes command having skipped over it with the -o
option.
If instead the assignment is done with:


**Example**


[basecm11->device]% newnodes -s 1 node024..node026


then the node023 name is unassigned, and the name node024 is assigned instead to the node with the
MAC address ...A, so that the rack layout looks like:


node024 ...A


node025 ...B


node026 ...C

|before after|Col2|
|---|---|
|node020|node020|
|node021|node021|
|node022|node022|
||node024|
||node025|
||node026|



newnodes **advanced use—assignment grouping example:** Node range assignments are one way of
using newnodes . However assignments can also be made to a category, a rack, or a chassis. For example,
with Base View assigning node names to a rack can be done from the Racks option of the node. For
example, to add a node001 to a rack1, the navigation path would be:
Devices - Settings[node001] - Rack[rack1] .
In cmsh, the assignment of multiple node names to a rack can conveniently be done with a foreach
loop from within device mode:


**Example**


[basecm11->device]% foreach -n node020..node029 (set rack rack02)

[basecm11->device*]% commit

[basecm11->device]% foreach -n node030..node039 (set rack rack03)

[basecm11->device*]% commit


The assignment of node names with the physical node in the rack can then be arranged as follows: If
the nodes are identical hardware, and are powered up in numerical sequence, from node020 to node039,
with a few seconds in between, then the list that the basic newnodes command (without options) displays
is arranged in the same numerical sequence. Assigning the list in the rack order can then be done by
running:


**Example**


[basecm11->device]% newnodes -s -r rack02..rack03


If it turns out that the boot order was done very randomly and incorrectly for all of rack02, and that
the assignment for rack02 needs to be done again, then a simple way to deal with it is to bring down the
nodes of rack02, then clear out all of the rack02 current MAC associations, and redo them according to
the correct boot order:


**Example**


**5.4 Node-Installer** **255**


[basecm11->device]% foreach -r rack02 ( clear mac ) ; commit

...removes MAC association with nodes from CMDaemon...


...now reboot nodes in rack02 in sequence (not with BCM)...


[basecm11->device]% newnodes


...shows sequence as the nodes come up...


[basecm11->device]% newnodes -s -r rack02


...assigns sequence in boot order...


newnodes **advanced use—assignment forcing example:** The --force option can be used in the following case: Supposing that node022 fails, and a new node hardware comes in to replace it. The new regular
node has a new MAC address. So, as explained by scenario 3 (section 5.4.2), if there is no switch port
assignment in operation for the nodes, then the node-installer loops around, waiting for intervention. [1]

This situation can be dealt with from the command line by:


  - accepting the node configuration at the regular node console, via a sub-dialog


  - accepting the node configuration via cmsh, without needing to be at the regular node console:


[basecm11->device]% newnodes -s -f -n node022


**Node Identification**
The _node identification_ resource can be accessed via the Base View navigation path:

Devices  - Nodes Identification .

The node identification resource is roughly the Base View equivalent to the newnodes command of
cmsh, and it opens up the New Node list window (figure 5.14).
As is the case for newnodes in cmsh, the New Node list window of Base View lists the MAC address
of any unassigned node that the head node detects, and shows the associated detected switch port for
the node. Also, just as for newnodes, New Node list can help assign a node name to the node, assuming
the node object exists. After assignment is done, the new status should be saved.


1 with switch port assignment in place, scenario 1 means the new node simply boots up by default and becomes the new
node022 without further intervention


**256** **Node Provisioning**


Figure 5.14: Node Identification Resource


The most useful way of using the node identification resource is for node assignment in large clus
ters.

To do this, it is assumed that the node objects have already been created for the new nodes. The
creation of the node objects means that the node names exist, and so assignment to the node names is
able to take place. An easy way to create many nodes in Base View, set their provisioning interface, and
set their IP addresses is described in the section on the _node creation wizard_ (section 5.7.2). Node objects
can also be created easily in large numbers by using cmsh ’s foreach loop command on a node with the
--clone option (section 2.5.5, page 65).
The nodes are also assumed to be set for net booting, typically set from a BIOS setting.
The physical nodes are then powered up in an arranged order. Because they are unknown new
nodes, the node-installer keeps looping after a timeout. The head node in the meantime detects the new
MAC addresses and switch ports in the sequence in which they first have come up and lists them in that
order.

By default, all these newly detected nodes are set to an install mode of auto (section 5.4.4), which
means that their numbering goes up sequentially from whatever number is assigned to the preceding
node in the list. Thus, if there are 10 new unassigned nodes that are brought into the cluster, and
the first node in the list is assigned to the first available number, say node327 ; then clicking on assign
automatically assigns the remaining nodes to the next 9 available numbers, say node328node336 .
After the assignment, the node-installer looping process on the new nodes notices that the nodes are
now known. The node-installer then breaks out of the loop, and installation goes ahead without any
intervention needed at the node console.


**5.4.3** **Starting Up All Network Interfaces**
At the end of section 5.4.2, the node-installer knows which node it is running on, and has decided what
its node configuration is.


**Starting Up All Provisioning Network Interfaces**
It now gets on with setting up the IP addresses on the provisioning interfaces required for the nodeinstaller, while taking care of matters that come up on the way:


**Avoiding duplicate IP addresses:** The node-installer brings up all the network interfaces configured
for the node. Before starting each interface, the node-installer first checks if the IP address that is about
to be used is not already in use by another device. If it is, then a warning and retry dialog is displayed
until the IP address conflict is resolved.


**5.4 Node-Installer** **257**


**Using** BOOTIF **to specify the boot interface:** BOOTIF is a special name for one of the possible interfaces.
The node-installer automatically translates BOOTIF into the name of the device, such as eth0 or eth1,
used for network booting. This is useful for a machine with multiple network interfaces where it can be
unclear whether to specify, for example, eth0 or eth1 for the interface that was used for booting. Using
the name BOOTIF instead means that the underlying device, eth0 or eth1 in this example, does not need
to be specified in the first place.


**Halting on missing kernel modules for the interface:** For some interface types like VLAN and channel bonding, the node-installer halts if the required kernel modules are not loaded or are loaded with the
wrong module options. In this case the kernel modules configuration for the relevant software image
should be reviewed. Recreating the ramdisk and rebooting the node to get the interfaces up again may
be necessary, as described in section 5.8.5.


**Bringing Up Non-Provisioning Network Interfaces**
Provisioning interfaces are by default automatically brought up during the init stage, as the node is fully
booted up. The BMC and non-provisioning interfaces on the other hand have a different behavior:


**Bringing Up And Initializing BMC Interfaces:** If a BMC interface is present and powered up, then it
is expected to be running at least with layer 2 activity (ethernet). It can be initialized in the node configuration (section 3.7) with an IP address, netmask and user/password settings so that layer 3 (TCP/IP)
networking works for it. BMC networking runs independently of node networking.


**Bringing up non-BMC, non-provisioning network interfaces:** Non-provisioning interfaces are inactive unless they are explicitly brought up. BCM can configure how these non-provisioning interfaces are
brought up by using the bringupduringinstall parameter, which can take the following values:


 - yes : Brings the interface up during the pre-init stage


 - no : Keeps the interface down during the pre-init stage. This is the default for non-provisioning
interfaces.


 - yesandkeep : Brings the interface up during the pre-init stage, and keeps it up during the transition
to the init stage.


**Bringing Up And Keeping Up Provisioning Network Interfaces**
The preceding bringupduringinstall parameter is not generally supported for provisioning interfaces.
However the yesandkeep value does work for provisioning interfaces too, under some conditions:


 - yesandkeep : Brings the interface up during the pre-init stage, and keeps it up during the transition
to the init stage, for the following provisioning devices:


**–**
Ethernet device interfaces using a leased DHCP address


**–**
InfiniBand device interfaces running with distribution OFED stacks


**Restarting The Network Interfaces**
At the end of this step (i.e. section 5.4.3) the network interfaces are up. When the node-installer has
completed the remainder of its 13 steps (sections 5.4.4–5.4.13), control is handed over to the local init
process running on the local drive. During this handover, the node-installer brings down all network
devices. These are then brought back up again by init by the distribution’s standard networking init
scripts, which run from the local drive and expect networking devices to be down to begin with.


**258** **Node Provisioning**


**5.4.4** **Determining Install-mode Type And Execution Mode**
Stored _install-mode_ values decide whether synchronization is to be applied fully to the local drive of the
node, only for some parts of its filesystem, not at all, or even whether to drop into a maintenance mode
instead.

Related to install-mode values are execution mode values (page 259) that determine whether to apply
the install-mode values to the next boot, to new nodes only, to individual nodes or to a category of nodes.
Related to execution mode values is the confirmation requirement toggle value (page 261) in case a
full installation is to take place.
These values are merely determined at this stage; nothing is executed yet.


**Install-mode Values**

The install-mode can have one of five values: AUTO, FULL, MAIN, NOSYNC, and SKIP . It should be understood that the term “install-mode” implies that these values operate only during the node-installer
phase. [2]


  - If the install-mode is set to FULL, then the node-installer re-partitions, creates new filesystems and
synchronizes a full image onto the local drive according a _partition layout_ . This process wipes out
all pre-boot drive content.


A partition layout (Appendix D) includes defined values for the partitions, sizes, and filesystem
types for the nodes being installed. An example of a partition layout is the default partition layout
(Appendix D.3).


  - If the install-mode is set to AUTO, then the node-installer checks the partition layout of the local
drive against the node’s stored configuration. If these do not match because, for example, the node
is new, or if they are corrupted, then the node-installer recreates the partitions and filesystems by
carrying out a FULL install. If however the drive partitions and filesystems are healthy, the nodeinstaller only does an incremental software image synchronization. Synchronization tends to be
quick because the software image and the local drive usually do not differ much.


Synchronization also removes any extra local files that do not exist on the image, for the files and
directories considered. Section 5.4.7 gives details on how it is decided what files and directories
are considered.


  - If the install-mode is set to MAIN, then the node-installer does not carry out a disk check, and goes
on to maintenance mode, allowing manual investigation of specific problems. The local drive is
untouched.


  - If the install-mode is set to NOSYNC, and the partition layout check matches the stored XML configuration, then the node-installer skips synchronizing the image to the node, so that contents on the
local drive persist from the previous boot. An exception to this is the node certificate and key, that
is the files /cm/local/apps/cmd/etc/cert.{pem|key} . These are updated from the head node if
missing.


If however the partition layout does not match the stored configuration, a FULL image sync is
triggered. Thus, for example, a burn session (Chapter 11 of the _Installation Manual_ ), with the
default burn configuration which destroys the existing partition layout on a node, will trigger
a FULL image sync on reboot after the burn session.


The NOSYNC setting should therefore not be regarded as a way to protect data. Ways to preserve
data across node reboots are discussed in the section that discusses the FULL install confirmation
settings (page 261).


2 For example, imageupdate (section 5.6.2), which is run by CMDaemon, ignores these settings, which is as expected. This
means that, for example, if imageupdate is run with NOSYNC set, then the head node image is still synchronized over as usual
to the regular node while the node is up. It is only during node boot, during the installer stage, that setting NOSYNC prevents
synchronization.


**5.4 Node-Installer** **259**


NOSYNC is useful during mass planned node reboots when set with the nextinstallmode option
of device mode. This sets the nodes to use the OS on the hard drive, during the next boot only,
without an image sync:


**Example**


[basecm11]% device foreach -n node001..node999 (set nextinstallmode nosync)

[basecm11]% device commit


  - If the install-mode is set to SKIP, then the node-installer does not carry out a check of the partitions
and filesystems, and it also does not carry out a software image synchronization. If a node runs
into problems with its drive content during a normal start up attempt, then this mode can perhaps
be used to attempt data recovery on the node.


**Install-mode Logging**
The decision that is made is normally logged to the node-installer file, /var/log/node-installer on
the head node.


**Example**


08:40:58 node001 node-installer: Installmode is: AUTO

08:40:58 node001 node-installer: Fetching disks setup.

08:40:58 node001 node-installer: Setting up environment for initialize scripts.

08:40:58 node001 node-installer: Initialize script for category default is empty.

08:40:59 node001 node-installer: Checking partitions and filesystems.

08:40:59 node001 node-installer: Updating device status: checking disks
08:40:59 node001 node-installer: Detecting device '/dev/sda': found

08:41:00 node001 node-installer: Number of partitions on sda is ok.

08:41:00 node001 node-installer: Size for /dev/sda1 is ok.

08:41:00 node001 node-installer: Checking if /dev/sda1 contains ext3 filesystem.

08:41:01 node001 node-installer: fsck.ext3 -a /dev/sda1

08:41:01 node001 node-installer: /dev/sda1: recovering journal
08:41:02 node001 node-installer: /dev/sda1: clean, 129522/1250928 files, 886932/5000000 blocks

08:41:02 node001 node-installer: Filesystem check on /dev/sda1 is ok.
08:41:02 node001 node-installer: Size for /dev/sda2 is wrong.
08:41:02 node001 node-installer: Partitions and/or filesystems are missing/corrupt. (Exit code\
18, signal 0)

08:41:03 node001 node-installer: Creating new disk layout.


In this case the node-installer detects that the size of /dev/sda2 on the disk no longer matches the
stored configuration, and triggers a full re-install. For further detail beyond that given by the nodeinstaller log, the disks script at /cm/node-installer/scripts/disks on the head node can be examined. The node-installer checks the disk by calling the disks script. Exit codes, such as the 18 reported
in the log example, are defined near the top of the disks script.


**Install-mode’s Execution Modes**

Execution of an install-mode setting is possible in several ways, both permanently or just temporarily
for the next boot. Execution can be set to apply to categories or individual nodes. The node-installer
looks for install-mode execution settings in this order:


1. The “ New node installmode ” property of the node’s category. This decides the install mode for a
node that is detected to be new.


It can be set for the default category using a Base View navigation path such as:


Grouping   - Node categories[default]   - Edit   - Settings   - Install mode


or using cmsh with a one-liner such as:


**260** **Node Provisioning**


cmsh -c "category use default; set newnodeinstallmode FULL; commit"


By default, the “ New node installmode ” property is set to FULL .


2. The Install-mode setting as set by choosing a PXE menu option on the console of the node before
it loads the kernel and ramdisk (figure 5.15). This only affects the current boot. By default the PXE
menu install mode option is set to AUTO .


Figure 5.15: PXE Menu With Install-mode Set To AUTO


3. The “ Next boot install-mode ” property of the node configuration. This can be set for a node
such as node001 using a Base View navigation path such as:
Devices   - Nodes[node001]   - Edit   - Settings   - Install mode


It can also be set using cmsh with a one-liner:


cmsh -c "device use node001; set nextinstallmode FULL; commit"


The property is cleared when the node starts up again, after the node-installer finishes its installation tasks. So it is empty unless specifically set by the administrator during the current uptime for
the node.


4. The install-mode property can be set in the node configuration using Base View via
Devices   - Nodes[node001]   - Edit   - Settings   - Install mode or using cmsh with a one-liner
such as:


cmsh -c "device use node001; set installmode FULL; commit"


By default, the install-mode property is auto-linked to the property set for install-mode for that
category of node. Since the property for that node’s category defaults to AUTO, the property for the
install-mode of the node configuration defaults to “ AUTO (Category) ”.


5. The install-mode property of the node’s category. This can be set using Base View with a navigation path such as:
Grouping   - Node categories[default]   - Edit   - Settings   - Install mode
or using cmsh with a one-liner such as:


cmsh -c "category use default; set installmode FULL; commit"


**5.4 Node-Installer** **261**


As already mentioned in a previous point, the install-mode is set by default to AUTO .


6. A dialog on the console of the node (figure 5.16) gives the user a last opportunity to overrule the
install-mode value as determined by the node-installer. By default, it is set to AUTO :


Figure 5.16: Install-mode Setting Option During Node-Installer Run


**FULL Install Confirmation via** datanode **Setting**
Related to execution mode values is the ability to carry out a FULL install only after explicit confirmation, via the datanode property. This must be set in order to prompt for a confirmation, when a FULL
installation is about to take place. If it is set, then the node-installer only goes ahead with the FULL
install after the administrator has explicitly confirmed it.
The datanode property can be set in the node configuration of, for example, node001 with Base View
via the navigation path:
Devices - Nodes[node001] - Edit - Settings - Data node[Yes]
Alternatively, the parameter datanode can be set using a cmsh one-liner as follows:


[root@basecm11 ~]# cmsh -c "device use node001; set datanode yes; commit"


The property can also be set at a category level. Since datanode is a boolean value, the actual value
that is used used for a node is the result of the or operation for that value across the levels. The level at
which a value works due to its boolean or non-boolean type is explained more on page 27.


**Why the FULL install confirmation is useful:** The reason for such a setting is that a FULL installation
can be triggered by disk or partition changes, or by a change in the MAC address. If that happens, then:


  - considering a drive, say, /dev/sda that fails, this means that any drive /dev/sdb would then normally become /dev/sda upon reboot. In that case an unwanted FULL install would not only be
triggered by an install-mode settings of FULL, but also by the install-mode settings of AUTO or
NOSYNC. Having the new, “accidental” /dev/sda have a FULL install is unlikely to be the intention, since it would probably contain useful data that the node-installer earlier left untouched.


**262** **Node Provisioning**


  - considering a node with a new MAC address, but with local storage containing useful data from
earlier. In this case, too, an unwanted FULL install would not only be triggered by an install-mode
setting of FULL, but also by the install-mode settings AUTO or NOSYNC.


Thus, in cases where nodes are used to store data, an explicit confirmation before overwriting local storage contents is a good idea. However, by default, no confirmation is asked for when a FULL
installation is about to take place.


**Carrying out the confirmation:** When the confirmation is required, then it can be carried out by the
administrator as follows:


  - From the node console. A remote console launched from Base View or cmsh will also work if SOL

connectivity has been configured.


 - From cmsh, within device mode, using the installerinteractions command (some output
elided):


**Example**


[basecm11->device]% installerinteractions -w -n node001 --confirm

Hostname Action

--------- --------------------------------------------
node001 Requesting FULL Install (partition mismatch)

[basecm11->device]%

...07:57:36 [notice] basecm11: node001 [ INSTALLER_CALLINGINIT ]...

[basecm11->device]%

...07:58:20 [notice] basecm11: node001 [ UP ]


The installerinteractions command then sets the node to a confirmed state. The other possible
states are deny and pending .


Besides confirmation, the installerinteractions command has options that include letting it:


**–**
deny the installation, and put it into maintenance mode


**–**
carry out a dry-run


**–**
carry out its actions for node groupings such as: node lists, node categories, node groups,
chassis, racks, as are possible in the grouping options (page 64).


Further details on the command can be viewed by running help installerinteractions .


**An alternative way to avoid overwriting node storage:** Besides the method of FULL install confirmation for datanode, there is a method based on XML assertions, that can also be used to prevent data loss
on nodes.

It uses XML assertions to confirm that the physical drive is recognized (Appendix D.11).


**A way to overwrite a specified block device:** A related method is that sometimes, for reasons of performance or convenience, it may be desirable to clear data on particular block devices for a node, and
carry it out during the next boot only. This can done by setting the block device names to be cleared
as values to the parameter Block devices cleared on next boot . The values can be set in cmsh as
follows:


[basecm11->device[node001]]% append blockdevicesclearedonnextboot /dev/sda /dev/sdb ; commit


The value of blockdevicesclearedonnextboot is automatically cleared after the node is rebooted.
Clearing data in this way ignores any datanode or nextinstallmode settings, and should therefore be
used with due care.


**5.4 Node-Installer** **263**


**5.4.5** **Running Initialize Scripts**
An _initialize script_ is used when custom commands need to be executed before checking partitions and
mounting devices (section 3.19.4). For example, to initialize some not explicitly supported hardware, or
to do a RAID configuration lookup for a particular node. In such cases the custom commands are added
to an initialize script. How to edit an initialize script is described in Appendix E.2.
An initialize script can be added to both a node’s category and the node configuration. The nodeinstaller first runs an initialize script, if it exists, from the node’s category, and then an initialize
script, if it exists, from the node’s configuration.
The node-installer sets several environment variables which can be used by the initialize script.
Appendix E contains an example script documenting these variables.
Related to the initialize script is the finalize script (section 5.4.11). This may run after node
provisioning is done, but just before the init process on the node runs.


**5.4.6** **Checking Partitions, RAID Configuration, Mounting Filesystems**

**Behavior As Decided By The Install-Mode Value**
In section 5.4.4 the node-installer determines the install-mode value, along with when to apply it to a
node.


**AUTO:** The install-mode value is typically set to default to AUTO . If AUTO applies to the current node,
it means the node-installer then checks the partitions of the local drive and its filesystems and recreates
them in case of errors. Partitions are checked by comparing the partition layout of the local drive(s)
against the drive layout as configured in the node’s category configuration and the node configuration.
After the node-installer checks the drive(s) and, if required, recreates the layout, it mounts all filesystems to allow the drive contents to be synchronized with the contents of the software image.


**FULL, MAIN, or SKIP:** If install-mode values of FULL, MAIN, or SKIP apply to the current node instead,
then no partition checking or filesystem checking is done by the node-installer.


**NOSYNC:** If the install-mode value of NOSYNC applies, then if the partition and filesystem checks both
show no errors, the node starts up without getting an image synced to it from the provisioning node.
If the partition or the filesystem check show errors, then the node partition is rewritten, and a known
good image is synced across.


**Behavior As Decided By XML Configuration Settings**
The node-installer is capable of creating advanced drive layouts, including LVM setups, and hardware
and software RAID setups. Drive layout examples and relevant documentation are in Appendix D.
The XML description used to set the drive layouts can be deployed for a single device or to a category
of devices.


**Hardware RAID:** BCM supports hardware RAID levels 0, 1, 5, 10, and 50, and supports the following
options:


**Option**


64kB




- **stripe size:**



128kB


256kB


512kB


1024kB


**264** **Node Provisioning**


**Option**




- **cache policy:**


- **read policy:**


- **write policy:**



Cached


Direct


**Option** **Description**


NORA No Read Ahead


RA Read Ahead


ADRA Adaptive Read


**Option** **Description**


WT Write Through


WB Write Back



**5.4.7** **Synchronizing The Local Drive With The Software Image**
After having mounted the local filesystems, these can be synchronized with the contents of the software
image associated with the node (through its category). Synchronization is skipped if the install-mode
values of NOSYNC or SKIP are set, and takes place FULL or AUTO are set. Synchronization is delegated by
the node-installer to the CMDaemon provisioning system. The node-installer just sends a provisioning
request to CMDaemon on the head node.
For an install-mode of FULL, or for an install-mode of AUTO where the local filesystem is detected as
being corrupted, full provisioning is done. For an install-mode of AUTO where the local filesystem is
healthy and agrees with that of the software image, sync provisioning is done.


**The** lock **,** unlock **, And** islocked **Commands For Software Images**
The software image that is requested is available to nodes by default. Its availability can be altered and
checked with the following commands:


 - lock : this _locks_ an image so that the image cannot be provisioned until the image is _unlocked_ .


 - unlock : this _unlocks_ a locked image, so that request for provisioning the image is no longer prevented by a lock


 - islocked : this lists the locked or unlocked states of images.


Locking an image is sometimes useful, for example, to make changes to an image when nodes are
booting:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% softwareimage list
Name (key) Path Kernel version Nodes

-------------------- ---------------------------------------- ---------------------------- -------
default-image /cm/images/default-image 3.10.0-1062.12.1.el7.x86_64 3

[basecm11]% softwareimage

[basecm11->softwareimage]% lock default-image

[basecm11->softwareimage]% islocked

Name Locked

-------------- -------
default-image yes


**5.4 Node-Installer** **265**


[basecm11->softwareimage]% lock default-image

[basecm11->softwareimage]% device

[basecm11->device]% reboot node001

_...the cluster administrator makes changes to the node image during a boot, as it waits for_
_the image to unlock..._

[basecm11->device]% softwareimage unlock default-image


For an unlocked image, on receiving the provisioning request, CMDaemon assigns the provisioning
task to one of the provisioning nodes. The node-installer is notified when image synchronization starts,
and also when the image synchronization task ends—whether it is completed successfully or not.


**Exclude Lists:** excludelistsyncinstall **And** excludelistfullinstall
What files are synchronized is decided by an _exclude list_ . An exclude list is a property of the node category, and is a list of directories and files that are excluded from consideration during synchronization.
The excluded list that is used is decided by the type of synchronization chosen: full or sync :


 - A full type of synchronization rewrites the partition table of the node, then copies the filesystem
from a software image to the node, using a list to specify files and directories to exclude from
consideration when copying over the filesystem. The list of exclusions used is specified by the
excludelistfullinstall property.


The intention of full synchronization is to allow a complete working filesystem to be copied
over from a known good software image to the node. By default the excludelistfullinstall
list contains /proc/, /sys/, and lost+found/, which have no content in BCM’s default software
image. The list can be modified to suit the requirements of a cluster, but it is recommended to have
the list adhere to the principle of allowing a complete working node filesystem to be copied over
from a known good software image.


 - A sync type of synchronization uses the property excludelistsyncinstall to specify what files
and directories to exclude from consideration when copying parts of the filesystem from a known
good software image to the node. The excludelistsyncinstall property is in the form of a list
of exclusions, or more accurately in the form of two sub-lists.


The contents of the sub-lists specify the parts of the filesystem that should be retained or not
copied over from the software image during sync synchronization when the node is booting. The
intention behind this is to have the node boot up quickly, updating only the files from the image
to the node that need updating due to the reboot of the node, and otherwise keeping files that are
already on the node hard disk unchanged. The contents of the sub-lists are thus items such as the
node log files, or items such as the /proc and /sys pseudo-filesystems which are generated during
node boot.


The administrator should be aware that nothing on a node hard drive can be regarded as persistent
because a FULL sync takes place if any error is noticed during a partition or filesystem check.


Anything already on the node that matches the content of these sub-lists is not overwritten by
image content during an excludelistsyncinstall sync. However, image content that is not on
the node is copied over to the node only for items matching the first sub-list. The remaining files
and directories on the node, that is, the ones that are not in the sub-lists, lose their original contents,
and are copied over from the software image.


A cmsh one-liner to get an exclude list for a category is:


cmsh -c "category use default; get excludelistfullinstall"


Similarly, to set the list:


cmsh -c "category use default; set excludelistfullinstall; commit"


**266** **Node Provisioning**


where a text-editor opens up to allow changes to be made to the list. In Base View the navigation path is:


Grouping - Node Categories - Edit - Node Category - Settings - Exclude list full install
Image synchronization is done using rsync, and the syntax of the items in the exclude lists conforms
to the “ INCLUDE/EXCLUDE PATTERN RULES ” section of the rsync(1) man page, which includes patterns
such as “ ** ”, “ ? ”, and “ [[:alpha:]] ”.
The excludelistfullinstall and excludelistsyncinstall properties decide how a node synchronizes to an image during boot. For a node that is already fully up, the related excludelistupdate
property decides how a running node synchronizes to an image without a reboot event, and is discussed
in section 5.6.


**Interface Used To Receive Image Data:** provisioninginterface
For regular nodes with multiple interfaces, one interface may be faster than the others. If so,
it can be convenient to receive the image data via the fastest interface. Setting the value of
provisioninginterface, which is a property of the node configuration, allows this.
By default it is set to BOOTIF for regular nodes. Using BOOTIF is not recommended for node configurations with multiple interfaces.
When listing the network interfaces in cmsh, the provisioning interface has a [prov] flag appended
to its name.


**Example**


[basecm11->device[node001]->interfaces]% list

Type Network device name IP Network

------------ -------------------- ---------------- ---------------
physical BOOTIF [prov] 10.141.0.1 internalnet

physical eth1 10.141.1.1 internalnet

physical eth2 10.141.2.1 internalnet


**Head nodes and** provisioninginterface **:** A head node in a single-head cluster does not use the
provisioninginterface setting.
Head nodes in a failover configuration (Chapter 15), however, do have a value set for
provisioninginterface, corresponding to the interface on the head that is being provisioned over
internalnet by the other head ( eth0 in figure 15.1).


**Transport Protocol Used For Image Data:** provisioningtransport
The provisioningtransport property of the node sets whether the image data is sent encrypted or
unencrypted to the node from the provisioner. The property value is set via the device mode for the
receiving node to one of these values:


 - rsyncdaemon, which sends the data unencrypted


 - rsyncssh, which sends the data encrypted


The provisioningtransport value can be set for all nodes, including provisioning nodes, head nodes,
and cloud-director (section 3.2 of the _Cloudbursting Manual_ ) nodes. Because encryption severely increases the load on the provisioning node, using rsyncssh is only suggested if the users on the network cannot be trusted. By default, provisioningtransport is set to rsyncdaemon . If high availability
(Chapter 15) is set up with the head nodes exposed to the outside world on the external network, the
administrator should consider setting up rsyncssh for the head nodes.
The rsyncssh transport requires passwordless root access via ssh from the provisioner to the node
being provisioned. This is configured by default in the default BCM nodes. However, if a new image is
created with the --exclude options for cm-create-image as explained in (section 9.6.2), the keys must
be copied over from /root/.ssh/ on the existing nodes.


**5.4 Node-Installer** **267**


**Tracking The Status Of Image Data Provisioning:** provisioningstatus
The provisioningstatus command within the softwareimage mode of cmsh displays an updated state
of the provisioning system. As a one-liner, it can be run as:


basecm11:~ # cmsh -c "softwareimage provisioningstatus"

Provisioning subsystem status: idle, accepting requests

Update of provisioning nodes requested: no

Maximum number of nodes provisioning: 10000

Nodes currently provisioning: 0

Nodes waiting to be provisioned: <none>

Provisioning node basecm11:

Max number of provisioning nodes: 10

Nodes provisioning: 0

Nodes currently being provisioned: <none>


The provisioningstatus command has several options that allow the requests to be tracked. The -r
option displays the basic status information on provisioning requests, while the -a option displays all
status information on provisioning requests. Both of these options display the request IDs.
The Base View equivalent to provisioningstatus is accessed via the navigation path:
Provisioning - Provisioning nodes
By default, it displays basic status information on provisioning requests.


**Tracking The Provisioning Log Changes:** synclog
For a closer look into the image file changes carried out during provisioning requests, the synclog
command from device mode can be used (lines elided in the following output):


**Example**


[basecm11->device]% synclog node001

Tue, 11 Jan 2011 13:27:17 CET - Starting rsync daemon based provisioning. Mode is SYNC.


sending incremental file list

./

...

deleting var/lib/ntp/etc/localtime
var/lib/ntp/var/run/ntp/

...

sent 2258383 bytes received 6989 bytes 156232.55 bytes/sec

total size is 1797091769 speedup is 793.29


Tue, 11 Jan 2011 13:27:31 CET - Rsync completed.


**Path Of The Provisioning Log File**
The path of the log file can be found with the -p option:


**Example**


[basecm11->device]% synclog -p node001
/var/spool/cmd/node001rsync

[basecm11->device]%


**Statistical Analysis Of Provisioning Sessions:** syncinfo
A provisioning session takes place between a provisioning image and a filesystem partition on a node.
Statistics can be presented for the sessions using the syncinfo command. The statistical information
presented is for number of files considered for transfer, the number of files that were actually transfered,
how long the transfer took, which image and node were involved, and so on. The syncinfo command
is run in device mode (output ellipsized and truncated):


**268** **Node Provisioning**


**Example**


[head->device]% syncinfo

Node Path Provisioner Age Duration Total files Transfered files ...

------- ------------------------ ----------- ---- -------- ----------- ---------------- ...

node001 /cm/images/default-image head 34s 21s 171,504 328 ...
node002 /cm/images/default-image head 34s 22s 171,504 328 ...

...


The syncinfo command has options to run it per node, category, rack, and so on. Details on the
options can be seen by running the help command ( help syncinfo ).


**Aborting Provisioning With** cancelprovisioningrequest
The cancelprovisioningrequest command cancels provisioning.
Its usage is:


cancelprovisioningrequest [OPTIONS] [<requestid> ...]


To cancel all provisioning requests, it can be run as:


basecm11:~ # cmsh -c "softwareimage cancelprovisioningrequest -a"


The provisioningstatus command of cmsh, can be used to find request IDs. Individual request IDs,
for example 10 and 13, can then be specified in the cancelprovisioningrequest command, as:


basecm11:~ # cmsh -c "softwareimage cancelprovisioningrequest 10 13"


The help page for cancelprovisioningrequest shows how to run the command on node ranges,
groups, categories, racks, chassis, and so on.
The Base View equivalents to the cmsh versions for managing provisioning requests can be accessed
via the navigation path Provisioning - Provisioning Requests


**5.4.8** **Writing Network Configuration Files**
In the previous section, the local drive of the node is synchronized according to install-mode settings
with the software image from the provisioning node. The node-installer now sets up configuration files
for each configured network interface. These are files like:
/etc/sysconfig/network-scripts/ifcfg-eth0
for Red Hat, Scientific Linux, CentOS, and Rocky Linux, while SUSE would use:
/etc/sysconfig/network/ifcfg-eth0
These files are placed on the local drive.
When the node-installer finishes its remaining tasks (sections 5.4.9–5.4.13) it brings down all network
devices and hands over control to the local /sbin/init process. Eventually a local init script uses the
network configuration files to bring the interfaces back up.


**5.4.9** **Creating A Local** /etc/fstab **File**
The /etc/fstab file on the local drive contains local partitions on which filesystems are mounted as
the init process runs. The actual drive layout is configured in the category configuration or the node
configuration, so the node-installer is able to generate and place a valid local /etc/fstab file. In addition
to all the mount points defined in the drive layout, several extra mount points can be added. These
extra mount points, such as NFS imports, /proc, /sys and /dev/shm, can be defined and managed in
the node’s category and in the specific configuration of the node configuration, using Base View or cmsh
(section 3.13.2).


**5.4 Node-Installer** **269**


**5.4.10** **Booting From The Local Hard Drive**
By default, a node-installer boots from the software image on the head node via the network.
The node-installer can, optionally, during image synchronization, install a local drive boot record
on the local hard drive if the installbootrecord boolean property of the node configuration or node
category is set to on . Setting the local drive boot record means that the node tries to use a local hard
drive boot installer during the next boot. This is a step toward having it become a standalone node that
does not boot from the network. This step, and the other steps needed to allow booting from the local
hard drive are covered next.


**Setting The Boot Record To Allow The Node To Be Standalone**
The local drive boot record is installed in the MBR of the local drive, overwriting the default iPXE boot
record (section 5.1.2).
With a working custom software image, the boot record can be installed with cmsh commands for a
node node001 with:


cmsh -c "device use node001; set installbootrecord yes; commit"


or for a category default with:


cmsh -c "category use default; set installbootrecord yes; commit"


Since installbootrecord is a boolean property, it means that if the node or if the node category
have the value set, then the node uses that value.
In Base View, the equivalent is the Install boot record option. This can similarly be enabled and
saved in the Base View node configuration or node category.
Setting the local drive boot record allows the next boot to be from the local hard drive, if the node is
set up right to boot from the local hard drive.
Booting from the local hard drive often requires some further changes, as explained next.


**Managing Boot Sequence And Bootloader To Ensure The Node Can Be Standalone**

For a local hard drive boot to work:


1. hard drive booting must be set to have a higher priority than network booting in the BIOS of the
node. Otherwise regular PXE booting is attempted, despite whatever value installbootrecord
has.


2. A working bootloader must be present.


By default, the node image for BCM has nodes set to use a SYSLINUX bootloader.


If the administrator is not using the default software image, but is using a custom software image
(section 9.6.1), and if the image is based on a running node filessystem that has not been built
directly from a parent distribution, then the GRUB boot configuration may not be appropriate
for a standalone GRUB boot to work. This is because the parent distribution installers often use
special logic for setting up the GRUB boot configuration. Carrying out this same special logic for
all distributions using the custom software image creation tool cm-create-image (section 9.6.2) is
impractical.


Providing a custom working image from a standalone node that has been customized after direct
installation from the parent distribution, ensures the GRUB boot configuration layout of the custom image is as expected by the parent distribution. This then allows a standalone GRUB boot on
the node to run properly.


Nodes can be set to use a GRUB bootloader from within device mode, or from within category
mode, by changing the bootloader parameter within the mode. For example, for a node node001 :


**Example**


**270** **Node Provisioning**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% get bootloader
syslinux (default)

[basecm11->device[node001]]% set bootloader grub

[basecm11->device*[node001*]]% commit


or, for the default category:


[root@basecm11 ~]# cmsh

[basecm11]% category use default

[basecm11->category[default]]% get bootloader

syslinux

[basecm11->category[default]]% set bootloader grub

[basecm11->category*[default*]]% commit


Arranging for the two items in the preceding list ensures that the next boot is from GRUB on the
hard drive. However, the BOOTIF also needs to be changed for booting to be successful. How it can be
changed, and why it needs to be changed, is described next.


**Changing** BOOTIF **To Ensure The Node Can Be Standalone**
If the BIOS is set to boot from the hard drive, and if there is a working boot loader, and if the boot record
has been installed, then the node boots via the boot record on the hard drive.
BOOTIF is the default value for the network interface for a node that is configured as a BCM software
image. However, the BOOTIF interface is undefined during hard drive booting, because it depends on
the network provisioning setup, which is not running. This means that the networking interface would
fail during hard drive boot for a standard image. To remedy this, the interface should be set to a defined
network device name, such as eth0, or the modern equivalents such as en01 (section 5.8.1). The defined
network device name, as the kernel sees it, can be found by logging into the node and taking a look at
the output of ip link :


**Example**


[root@basecm11 ~]# ssh node001 ip link

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue...

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc ...


In BCM the provisioning interface is mandatory, even if it is not provisioning. So it is set to the value
of kernel-defined network device name instead of BOOTIF :


**Example**


[basecm11]% device interfaces node001

[basecm11->device[node001]->interfaces]% list

Type Network device name IP Network

------------ -------------------- ---------------- ---------------
physical BOOTIF [prov] 10.141.0.1 internalnet

[basecm11->device[node001]->interfaces]% set bootif networkdevicename eth0

[basecm11->device*[node001*]->interfaces*]% commit

[basecm11->device[node001]->interfaces]% list

Type Network device name IP Network

------------ -------------------- ---------------- ---------------
physical eth0 [prov] 10.141.0.1 internalnet
Tue Mar 31 13:46:44 2020 [notice] basecm11: node001 [ UP ], restart required (eth0)


**5.4 Node-Installer** **271**


In the preceding example, the kernel-defined network device name is assumed to be eth0 . It should
be modified as required.
In addition, the new IP address is assumed to be on the same internal network. If the administrator
intends the node to be standalone on another network, then the network and the IP address can be set
to appropriate values.
When interface changes are carried out to make the node standalone, warnings show up saying that
a reboot is required. A reboot of the node should be done when the interface configuration is complete.
During reboot, the node then boots from the hard drive as a standalone, with a non- BOOTIF network
interface.


**Bringing A Node That Boots From Its Hard Drive Back Into A Cluster**
If the node is to be brought back into the cluster, then simply unsetting “Install boot record” and rebooting the node does not restore its iPXE boot record and hence its ability to iPXE boot. To restore the iPXE
boot record, the node can be booted from the default image copy on the head node via a network boot
again. Typically this is done by manual intervention during node boot to select network booting from
the BIOS of the node.

Setting the value of provisioninginterface in cmsh for the node to BOOTIF is also recommended.
As suggested by the BCM iPXE boot prompt, setting network booting to work from the BIOS (regular
“PXE” booting) is preferred to the relatively roundabout way of iPXE booting from the disk.


**SELinux Initialization For Hard Drive Boot And PXE Boot**

If configured, SELinux (Chapter 12 of the _Installation Manual_ ) is initialized at this point. For a boot
from the hard drive, the initialization occurs if an SELinux filesystem has been saved to disk previously.
For a PXE boot, the initialization takes place if the SELinuxInitialize directive is set to true in the
node-installer.conf file.


**5.4.11** **Running Finalize Scripts**
A _finalize script_ is similar to an initialize script (section 5.4.5), only it runs a few stages later in the
node-provisioning process.
In the context of configuration (section 3.19.4) it is used when custom commands need to be executed
after the preceding mounting, provisioning, and housekeeping steps, but before handing over control
to the node’s local init process. For example, custom commands may be needed to:


  - initialize some not explicitly supported hardware before init takes over


  - supply a configuration file for the software image that cannot simply be added to the software
image and used by init because it needs node-specific settings


  - load a slightly altered standard software image on particular nodes, typically with the change
depending on automatically detecting the hardware of the node it is being loaded onto. While this
could also be done by creating a full new software image and loading it on to the nodes according
to the hardware, it usually turns out to be better for simplicity’s sake (future maintainability) to
minimize the number of software images for the cluster.


The custom commands used to implement such changes are then added to the finalize script. How
to edit a finalize script is described in Appendix E.2.
A finalize script can be added to both a node’s category and the node configuration. The nodeinstaller first runs a finalize script, if it exists, from the node’s category, and then a finalize script, if
it exists, from the node’s configuration.
The node-installer sets several environment variables which can be used by the finalize script.
Appendix E contains an example script which documents these variables.


**272** **Node Provisioning**


**5.4.12** **Unloading Specific Drivers**
Many kernel drivers are only required during the installation of the node. After installation they are not
needed and can degrade node performance.
Baseboard Management Controllers (BMCs, section 3.7) that use IPMI drivers are an egregious example of this. The IPMI drivers are required to have the node-installer configure the IP address of any IPMI
cards. Once the node is configured, these drivers are no longer needed, but they continue to consume
significant CPU cycles and power if they stay loaded, which can affect job performance.
To solve this, the node-installer can be configured to unload a specified set of drivers just before
it hands over control to the local init process. This is done by editing the removeModulesBeforeInit
setting in the node-installer configuration file
/cm/node-installer/scripts/node-installer.conf,
For the node-installer.conf file in multidistro and multiarch (section 9.7) configurations, the directory path /cm/node-installer takes the form:
/cm/node-installer- _<distribution>-<architecture>_
The values for _<distribution>_ and _<architecture>_ can take the values outlined on page 528.
By default, the IPMI drivers are placed in the removeModulesBeforeInit setting.
To pick up IPMI-related data values, IPMI access is then carried out over the network without the
drivers.


**5.4.13** **Switching To The Local** init **Process**
At this point the node-installer is done. The node’s local drive now contains a complete Linux installation and is ready to be started. The node-installer hands over control to the local /sbin/init process,
which continues the boot process and starts all runlevel services. From here on the boot process continues as if the machine was started from the drive just like any other regular Linux machine.


**5.5** **Node States**


During the boot process, several state change messages are sent to the head node CMDaemon or detected by polling from the head node CMDaemon. The most important node states for a cluster after
boot up are introduced in section 2.1.1. These states are described again, along with some less common
ones to give a more complete picture of node states.


**5.5.1** **Node States Icons In Base View**

In the node icons used by Base View:


  - Nodes in the UP state are indicated by an up-arrow.


**–**
If all health checks (section 10.2.4) for the node are successful, the up-arrow is green.


**–**
If there is a health check that fails or if the node requires a reboot, the up-arrow is red.


  - Nodes in the DOWN state are indicated by a blue down-arrow.


  - There are some other states, including:


**–** Nodes in a CLOSED state are indicated by an X


**–** Nodes in a DOWN state that are installing are indicated by a underscored down-arrow icon: _↓_ _


**5.5.2** **Node States Shown In** cmsh

In cmsh, the node state can be found using the status command from device mode for a node:


**Example**


[basecm11->device]% status -n node001..node002

node001 ............. [ UP ] restart-required, health check failed
node002 ............. [ DOWN ] (hostname changed) restart-required


**5.5 Node States** **273**


Devices in general can have their states conveniently listed with the list -f (page 54) command:


**Example**


[basecm11->device]% list -f "hostname:10, status:48"

hostname ( status

---------- -----------------------------------------------
apc01 [ UP ]

basecm11 [ UP ]

devhp [ UP ]
node001 [ UP ] restart-required, health check failed
node002 [ DOWN ] (hostname changed) restart-required


The reason for a red icon as shown in section 5.5.1 can be found within the parentheses. In this
example it is (hostname changed) .


**5.5.3** **Node States Indicating Regular Start Up**
During a successful boot process the node goes through the following states:


 - BOOTING . This is the state while the kernel and initrd are being downloaded by the node during
network booting.


To allow the BOOTING state to be detected for a node:


**–** BOOTIF must be defined as an interface, or


**–** if there is no interface with the value BOOTIF, but a particular network device, such as eth0,
is the boot interface, then a special revision tag of bootif can be used for no more than one
interface:


**Example**


[basecm11->device[node001]->interfaces[eth0]]% set revision bootif


 - INSTALLING . This state is normally entered as soon as the node-installer has determined on which
node the node-installer is running. Within this state, information messages display indicating
what is being done while the node is in the INSTALLING state. Possible messages under the status
column for the node within cmsh and Base View are normally, in sequence:


1. node-installer started


2. Optionally, the following two messages:


(a) waiting for user input


(b) installation was resumed


3. checking disks


4. recreating partitions and filesystems


5. mounting disks


6. One of these following two messages:


(a) waiting for FULL provisioning to start


(b) waiting for SYNC provisioning to start


7. provisioning started, waiting for completion


8. provisioning complete


9. initializing SELinux


Between steps 1 and 3 in the preceding, these optional messages can also show up:


**274** **Node Provisioning**


**–** If burn mode is entered or left:


running burn-in tests

burn-in test completed successfully


**–** If maintenance mode is entered:


entered maintenance mode


 - INSTALLER_CALLINGINIT . This state is entered as soon as the node-installer has handed over control to the local init process. The associated message normally seen with it in cmsh and Base View
is:


**–**
switching to local root


 - UP . This state is entered as soon as the CMDaemon of the node connects to the head node CMDae
mon.


**5.5.4** **Node States That May Indicate Problems**
Other node states are often associated with problems in the boot process:


 - DOWN . This state is registered as soon as the CMDaemon on the regular node is no longer detected
by CMDaemon on the head node. In this state, the state of the regular node is still tracked, so that
CMDaemon is aware if the node state changes.


 - CLOSED . This state is appended to the UP or DOWN state of the regular node by the administrator,
and causes most CMDaemon monitoring actions for the node to cease. The state of the node is
however still tracked by default, so that CMDaemon is aware if the node state changes.


The CLOSED state can be set from the device mode of cmsh using the close command. The help
text for the command gives details on how it can be applied to categories, groups and so on. The
-m option sets a message by the administrator for the closed node or nodes.


**Example**


root@headymcheadface ~]# cmsh

[headymcheadface]% device

[headymcheadface->device]% close -m "fan dead" -n node001,node009,node020
Mon May 2 16:32:01 [notice] headymcheadface: node001 ...[ DOWN/CLOSED ] (fan dead)
Mon May 2 16:32:01 [notice] headymcheadface: node009 ...[ DOWN/CLOSED ] (fan dead)
Mon May 2 16:32:01 [notice] headymcheadface: node020 ...[ DOWN/CLOSED ] (fan dead)


The CLOSED state can also be set from Base View via the navigation path


Devices   - Nodes   - Edit   - Monitored state   - Open / Close .


When the CLOSED state is set for a device, CMDaemon commands can still attempt to act upon it.
For example, in the device mode of cmsh :


**–** open : This is the converse to the close command. It has the same options, including the -m
option that logs a message. It also has the following extra options:


        - [--reset] [: Resets whatever the status is of the] [ devicestatus] [ check. However, this reset]
by itself does not solve any underlying issue. The issue may still require a fix, despite the
status having been reset.
For example, the --reset option can be used to reset the restart-required flag (section 5.5.2).
However, the reason that set the restart-required flag is not solved by the reset. Restarts
are required for regular nodes if there have been changes in the following: network settings, disk setup, software image, or category.


**5.5 Node States** **275**


        - [-f|--failbeforedown <] _[count]_ [>] [: Specifies the number of failed pings before a device is]
marked as down (default is 1).


**–** drain and undrain (Appendix G.4.1)

**–** For nodes that have power control [3] :


        - [power -f on]


        - [power -f off]


        - [power -f reset]


In Base View, the equivalents for a node node001 for example, are via the navigation paths:


**–** Devices    - Nodes[node001]    - Edit    - Monitored state    - Open / Close


**–** Devices    - Nodes[node001]    - Edit    - Workload    - Drain / Undrain


**–** Devices    - Nodes[node001]    - Edit    - Power    - On/Off/Reset .


CMDaemon on the head node only maintains device monitoring logs for a device that is in the UP
state. If the device is in a state other than UP, then CMDaemon only tracks its state, and can display
the state if queried.


For example: if a node displays the state UP when queried about its state, and is given a ‘close’ command, it then goes into a CLOSED state. Querying the node state then displays the state UP/CLOSED .
It remains in that CLOSED state when the node is powered down. Querying the node state after
being powered down displays DOWN/CLOSED . Next, powering up the node from that state, and having it go through the boot process, has the node displaying various CLOSED states during queries.
Typically the query responses show it transitioning from DOWN/CLOSED, to INSTALLING/CLOSED, to
INSTALLER_CALLINGINIT/CLOSED, and ending up displaying the UP/CLOSED state.


Thus, a node set to a CLOSED state remains in a CLOSED state regardless of whether the node is in
an UP or DOWN state. The only way out of a CLOSED state is for the administrator to tell the node to
open via the cmsh “open” option discussed earlier. The node, as far as CMDaemon is concerned,
then switches from the CLOSED state to the OPEN state. Whether the node listens or not does not

matter—the head node records it as being in an OPENING state for a short time, and during this
time the next OPEN state ( UP/OPEN, DOWN/OPEN, etc.) is agreed upon by the head node and the node.


When querying the state of a node, an OPEN tag is not displayed in the response, because it is the
“standard” state. For example, UP is displayed rather than UP/OPEN . In contrast, a CLOSED tag is
displayed when it is active, because it is a “special” state.


The CLOSED state is normally set to take a node that is unhealthy out of the cluster management
system. The node can then still be in the UP state, displaying UP/CLOSED . It can even continue
running workload jobs in this state, since workload managers run independent of CMDaemon.
So, if the workload manager is still running, the jobs themselves are still handled by the workload
manager, even if CMDaemon is no longer aware of the node state until the node is re-opened. For
this reason, draining a node is often done before closing a node, although it is not obligatory.


 - OPENING . This transitional state is entered as soon as the CMDaemon of the node rescinds the

CLOSED state with an “open” command from cmsh . The state usually lasts no more than about 5
seconds, and never more than 30 seconds in the default configuration settings of BCM. The help
text for the open command of cmsh gives details on its options.


 - INSTALLER_FAILED . This state is entered from the INSTALLING state when the node-installer has
detected an unrecoverable problem during the boot process. For instance, it cannot find the
local drive, or a network interface cannot be started. This state can also be entered from the


3 power control mechanisms such as PDUs, custom power scripts, and BMCs using IPMI/HP iLO/DRAC/CIMC/Redfish, are
described in Chapter 4


**276** **Node Provisioning**


INSTALLER_CALLINGINIT state when the node takes too long to enter the UP state. This could
indicate that handing over control to the local init process failed, or the local init process was
not able to start the CMDaemon on the node. Lastly, this state can be entered when the previous
state was INSTALLER_REBOOTING and the reboot takes too long.


 - INSTALLER_UNREACHABLE . This state is entered from the INSTALLING state when the head node
CMDaemon can no longer ping the node. It could indicate the node has crashed while running
the node-installer.


 - INSTALLER_REBOOTING . In some cases the node-installer has to reboot the node to load the correct
kernel. Before rebooting it sets this state. If the subsequent reboot takes too long, the head node
CMDaemon sets the state to INSTALLER_FAILED .


**5.6** **Updating Running Nodes**


**Updating Running Nodes From A Stored Image By Rebooting**
Changes made to the contents of the software image for nodes, kept on the head node, become a part of
any other provisioning nodes according to the housekeeping system on the head node (section 5.2.4).
Thus, when a regular node reboots, the latest image is installed from the provisioning system onto
the regular node via a provisioning request (section 5.4.7).


**Updating Running Nodes From A Stored Image Without Rebooting**
However, updating a running node with the latest software image changes is also possible without
rebooting it. Such an update can be requested using cmsh or Base View, and is queued and delegated to a provisioning node, just like a regular provisioning request. The properties that apply to
the regular provisioning of an image also apply to such an update. For example, the value of the
provisioninginterface setting (section 5.4.7) on the node being updated determines which interface
is used to receive the image.


  - In cmsh the request is submitted with the imageupdate option (section 5.6.2).


  - In Base View, it is submitted, for a node node001 for example, using the navigation path:


Devices   - Nodes[node001]   - Edit   - Software image   - Update node (section 5.6.3).


The imageupdate command and “ Update node ” menu option use a configuration file called
excludelistupdate, which is, as its name suggests, a list of exclusions to the update.
The running node is thus updated from a stored image with the help of that configuration file when
imageupdate or “ Update node ” are run. More details are given in the rest of this section (section 5.6).


**Updating A Stored Image From A Running Node**
The converse, that is, to update a stored image from what is on a running node, can be also be carried
out. This converse can be viewed as grabbing from a node, and synchronizing what is grabbed, to an
image. It can be done using grabimage ( cmsh ), or Grab to image (Base View), and involves further
exclude lists excludelistgrab or excludelistgrabnew . The grabimage command and Grab to image
option are covered in detail in section 9.5.2.


**5.6.1** **Updating Running Nodes: Configuration With** excludelistupdate
The exclude list excludelistupdate used by the imageupdate command is defined as a property of the
node’s category. It has the same structure and rsync patterns syntax as that used by the exclude lists for
provisioning the nodes during installation (section 5.4.7).


**5.6 Updating Running Nodes** **277**


**Distinguishing Between The Intention Behind The Various Exclude Lists**
The administrator should note that it is the excludelist _update_ list that is being discussed here, in contrast with the excludelistsync _install_ / excludelistfull _install_ lists which are discussed in section 5.4.7,
and also in contrast with the excludelist _grab_ / excludelist _grabnew_ lists of section 9.5.2.
So, for the imageupdate command the excludelistupdate list concerns an _update_ to a running system, while for installation sync or full provisioning, the corresponding exclude lists
( excludelistsyncinstall and excludelistfullinstall ) from section 5.4.7 are about an _install_ during
node start-up. Because the copying intention during updates is to be speedy, the imageupdate command
synchronizes files rather than unnecessarily overwriting unchanged files. Thus, the excludelistupdate
exclusion list it uses is actually analogous to the excludelistsyncinstall exclusion list used in the sync
case of section 5.4.7, rather than being analogous to the excludelistfullinstall list.
Similarly, the excludelistgrab / excludelistgrabnew lists of section 9.5.2 are about a _grab_ from the
running node to the image.


  - The excludelistgrab list here is intended for the case of synchronizing the existing image with
the running node, and is thus analogous to the excludelistsyncinstall exclusion list.


  - The excludelistgrabnew list here is intended for the case of copying a full image from the running
node, and is thus analogous to the excludelistfullinstall list.


The following table summarizes this:


**During:** **Exclude list used is:** **Copy intention:**


update excludelistupdate sync, image to running node


excludelistfullinstall full, image to starting node
install

excludelistsyncinstall sync, image to starting node


excludelistgrabnew full, running node to image
grab

excludelistgrab sync, running node to image


The preceding table is rather terse. It may help to understand it if is expanded with some in-place
footnotes, where the footnotes indicate what actions can cause the use of the exclude lists:


**278** **Node Provisioning**


**During:** **Exclude list used is:** **Copy intention:**


update
excludelistupdate sync, image to running node
eg: imageupdate


install excludelistfullinstall full, image to starting node


eg: node-provisioning eg: node provisioning


process during pre- with installmode FULL


init stage depending


on installmode decision excludelistsyncinstall sync, image to starting node


eg: node provisioning AUTO


with healthy partition


grab excludelistgrabnew full, running node to image


eg: grabimage ( cmsh ), grabimage -i / Grab to image for a new image


Grab to image


(Base View) excludelistgrab sync, running node to image


grabimage / Grab to image for the original image


**The Exclude List Logic For** excludelistupdate
During an imageupdate command, the synchronization process uses the excludelistupdate list, which
is a list of files and directories. One of the cross checking actions that may run during the synchronization is that the items on the list are excluded when copying parts of the filesystem from a known good
software image to the node. The detailed behavior is as follows:
The exludelistupdate list is in the form of two sublists. Both sublists are lists of paths, except that
the second sublist is prefixed with the text “ no-new-files: ” (without the double quotes). For the node
being updated, all of its files are looked at during an imageupdate synchronization run. During such a
run, the logic that is followed is:


  - if an excluded path from excludelistupdate exists on the node, then nothing from that path is
copied over from the software image to the node


  - if an excluded path from excludelistupdate does not exist on the node, then


**–**
if the path is on the first, non-prefixed list, then the path is copied over from the software
image to the node.


**–**
if the path is on the second, prefixed list, then the path is not copied over from the software
image to the node. That is, no new files are copied over, like the prefix text implies.


This is illustrated by figure 5.17.


**5.6 Updating Running Nodes** **279**





























Figure 5.17: Exclude list logic


The files and directories on the node that are not in the sub-lists lose their original contents, and are
copied over from the software image. So, content not covered by the sub-lists at that time is normally
not protected from deletion.
Thus, the provisioning system excludes paths described according to the excludelistupdate property.
The provisioning system also excludes a statically-imported filesystem on a node if the filesystem
is a member of the following special list: NFS, Lustre, FUSE, CephFS, CIFS, PanFS, FhGFS, BeeGFS,
GlusterFS, or GPFS. If this exclusion were not done, then all data on these imported filesystems would


**280** **Node Provisioning**


be wiped, since they are not part of the software image. The automatic exclusion for these imported
filesystems does not rely on the excludelist values maintained by CMDaemon—instead, CMDaemon
carries out the check on-the-fly when provisioning starts.
Statically-imported filesystems that have their mounts managed by BCM via the fsmounts mode
can be excluded from being mounted on the nodes in the first place, by removing them from the listed
mounts within the fsmounts mode.

Imported filesystems not on the special list can have their data wiped out during provisioning or
sync updates, if the statically-imported filesystems are placed in the image manually—that is, if the
filesystems are mounted manually into the image on the head node via /etc/fstab without using cmsh
or Base View.


**Filesystems mounted dynamically cannot have their appearance or disappearance detected reliably:**
Any filesystem that may be imported via an auto-mount operation must therefore explicitly be excluded
by the administrator manually adding the filesystem to the exclude list. This is to prevent an incorrect execution of imageupdate . Neglecting to do this may wipe out the filesystem, if it happens to be
mounted in the middle of an imageupdate operation.


**The** fstab **system is a statically mounting system, and not an auto-mounter:** While fstab mounts
filesystems automatically, system administrators should not confuse that with auto-mounting. Automounting as provided by autofs is designed for the dynamic mounting of filesystems on demand by
regular users. The fstab table is designed for mounting as carried out by the system, as occurs during
boot, which is why it is regarded as a static, non-auto-mounting system.


**Editing An Exclude List**
A sample cmsh one-liner which opens up a text editor in a category so that the exclude list for updates
can be edited is:


cmsh -c "category use default; set excludelistupdate; commit"


Similarly, the exclude list for updates can also be edited in Base View via the navigation path:
Grouping - Node categories - Edit - Settings - Exclude list update


**Provisioning Modifications Via** excludelistmanipulatescript
Sometimes the administrator has a need to slightly modify the execution of exclude lists during provisioning. The excludelistmanipulatescript file takes as an input the exclude list inherited from a
category, modifies it in some way, and then produces a new exclude list. Conceptually it is a bit like how
an administrator might use sed if it worked without a pipe. As usual, setting it for node level overrides
the category level.
A script that manipulates the exclude lists of a node can be specified as follows within cmsh :


[basecm11]% device use node001

[basecm11->device[node001]]% set excludelistmanipulatescript
_(a vi session will start. A script is edited and saved)_

[basecm11->device[node001*]]% commit


The script can be as simple as:


**Example**


#!/bin/bash


echo "- *"

echo 'no-new-files: - *'


**5.6 Updating Running Nodes** **281**


If provisioning a node from the head node, then the script modifies the node-provisioning exclude
lists— excludelistfullinstall, excludelistsyncinstall, and excludelistupdate —so that they appear to contain these items only:


- *

no-new-files: - *


The provisioning node then excludes everything during provisioning.
Careful editing and testing of the script is advised. Saving a script with just a single whitespace, for
example, usually has undesirable results.
A more useful script template is the following:


**Example**


#!/bin/bash


while read; do

echo "$REPLY"

done


echo "# This and next line added by category excludelistmanipulatescript."
echo "# The command line arguments were: $@"


The provisioning exclude lists are simply read in, then sent out again without any change, except
that the last two lines add comment lines to the exclude lists that are to be used.

Internally, the arguments taken by the excludelistmanipulatescript are the destination path and
the sync mode (one of install | update | full | grab | grabnew ). This can be seen in the output of $@, if
running an imageupdate command to execute a dry run with the preceding example:


[basecm11]% device use node001

[basecm11->device[node001]]% get excludelistmanipulatescript
(the script is put in)

[basecm11->device[node001*]]% commit; imageupdate
Performing dry run (use synclog command to review result, then pass -w to perform real update)...
Wed Apr 15 04:55:46 2015 [notice] basecm11: Provisioning started: sendi _\_
ng basecm11:/cm/images/default-image to node001:/, mode UPDATE, dry run _\_

= yes, no data changes!

[basecm11->device[node001]]%
Wed Apr 15 04:55:51 2015 [notice] basecm11: Provisioning completed: sen _\_
t basecm11:/cm/images/default-image to node001:/, mode UPDATE, dry run _\_

= yes, no data changes!
imageupdate [ COMPLETED ]


An excerpt from the sync log, after running the synclog command, then shows output similar to
(some output elided):


...

- /cm/shared/*

- /cm/shared/

- /home/*

- /home/

- /cm/shared/apps/slurm/*

- /cm/shared/apps/slurm/