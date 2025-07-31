# This and next line added by category excludelistmanipulatescript.
# The command line arguments were: update /


**282** **Node Provisioning**


Rsync output:

sending incremental file list
cm/local/apps/cmd/scripts/healthchecks/configfiles/

...


Here, the sync mode is update and the destination path is “ / ”. Which of the exclude lists is being
modified can be determined by the excludelistmanipulatescript by parsing the sync mode.
The bash variable that accepts the exclude list text is set to a safely-marked form using curly braces.
This is done to avoid expansion surprises, due to wild card characters in the exclude lists. For example,
if $REPLY were used instead of ${REPLY}, and the script were to accept an exclude list line containing “ /proc/* ”, then it would give quite confusing output.


**Other Exclude List Handling Options**
**The** excludelistfailover **and** excludelistnormal **files:** are two further exclude list files that modify
standard provisioning behavior. These are discussed in section 15.4.8.


**The** excludelistsnippets **tool:** When synchronizing to a cloud director, or to an edge director, it is
sometimes useful to exclude unneeded files and paths from the synchronization, in order to speed it up.
The excludelistsmanipulatescript tool is powerful enough to do it, but it has some issues due to its
power. For example, it is a script, which means that it is called whenever it is used, and so uses up some
extra resources. Also, it is a bit tricky to set up.
An easier way to manipulate exclude lists for the unneeded files and paths is via the
excludelistsnippets tool, described in section 4.3.1 of the _Cloudbursting Manual_ . This tool allows
additional exclusion to be specified in a simpler way.


**The** provisioningassociations **mode:** Somewhat related to excludelistsnippets is the use of the
provisioningassociations mode. This is described in section 4.3.2 of the _Cloudbursting Manual_ . This
mode is used to modify some properties of provisioned file systems.


**Exclude List State At Node Level**

**Exclude lists at category level and node level:** An exclude list can be set at node level, as well as at
category level. Roles and overlays can add implied exclude lists too.
At category level, an exclude list such as excludelistfullinstall can be set up explicitly with:


**Example**


[basecm11->category[default]]% set excludelistfullinstall
... _a text editor such as vi opens up and the list can be edited_ ...

[basecm11->category*[default*]]% commit


At node level, an exclude list can be set in the same way:


**Example**


[basecm11->device[node001]]% set excludelistfullinstall

... _a text editor such as vi opens up and the list can be edited_ ...

[basecm11->device*[node001*]]% commit


An exclude list that is not empty at node level overrules its corresponding category list. Exclude lists
brought in via roles are however simply included in the exclude list.


**5.6 Updating Running Nodes** **283**


**The** excludelist **command:** At node level it can be unclear what the resulting exclude list (“operational exclude list”) actually is. The exclude list state at node level can therefore be viewed using the
excludelist command options. The excludelist command becomes active if a software image has
been set at the node level.


  - The list option to excludelist lists the source and destination paths:


**Example**


[basecm11->device[node001]]% excludelist list

Source path (on the head node) Destination path (on the node)

-------------------------------- -------------------------------
/cm/images/default-image /


  - The get option to the excludelist command has synchronization mode and destination suboptions for a node.


Earlier on (page 277), the intention behind the various exclude lists, according to the type of update
or synchronization, were distinguished.


The excludelist get command can have a destination path specified, and have the type of update or synchronization specified according to those distinguishing concepts.


The output to the excludelist get command then shows the operational exclude list as seen by
a node for that path and for that update or synchronization.


Thus, for example:


**–** The full install operational exclude list for the path / on node node001, intended for a full
installation to a node that is starting up, can be found as follows:


**Example**


[basecm11->device[node001]]% excludelist get full /

# For details on the exclude patterns defined here please refer to

# the FILTER RULES section of the rsync man page.

#

# Files that match these patterns will not be installed onto the node.

      - lost+found/

      - /proc/*

      - /sys/*

      - /boot/efi


# extra defaults

      - /proc/*

      - /sys/*


**–** Similarly, the sync install operational exclude list for the path / on node node001, intended
for a sync installation to a node that is starting up, can be found as follows:


[basecm11->device[node001]]% excludelist get sync /


# For details on the exclude patterns defined here please refer to

# the FILTER RULES section of the rsync man page.

#

# Files that exist on a node and match one of these patterns will not be

# modified or deleted. Any files that match one of these patterns and that


**284** **Node Provisioning**


# exist in the image but are absent on the node, will be copied to the node.

     - /.autofsck

     - /boot/grub*/grub.cfg

     - /cm/local/apps/openldap/etc/certs/ldap.key

     - /cm/local/apps/openldap/etc/certs/ldap.pem

     - /data/*

     - /home/*

...


**–** Other excludelist get options, besides full and sync, are:


        - [grab] [ (a grab from a running node for a sync back to an existing image)]

        - [grabnew] [ (a grab from a running node for a full install to a new image)]

        - [update] [ (a sync update of a running node from an image).]


All excludelist get options correspond to the intentions of the associated exclude list types
as distinguished on page 277.


**5.6.2** **Updating Running Nodes: With** cmsh **Using** imageupdate
Using a defined excludelistupdate property (section 5.6.1), the imageupdate command of cmsh is used
to start an update on a running node:


**Example**


[basecm11->device]% imageupdate -n node001
Performing dry run (use synclog command to review result, then pass -w to perform real update)...

Tue Jan 11 12:13:33 2011 basecm11: Provisioning started on node node001

[basecm11->device]% imageupdate -n node001: image update in progress ...

[basecm11->device]%

Tue Jan 11 12:13:44 2011 basecm11: Provisioning completed on node node001


By default the imageupdate command performs a dry run, which means no data on the node is
actually written. Before passing the “ -w ” switch, it is recommended to analyze the rsync output using
the synclog command (section 5.4.7).
If the user is now satisfied with the changes that are to be made, the imageupdate command is
invoked again with the “ -w ” switch to implement them:


**Example**


[basecm11->device]% imageupdate -n node001 -w

Provisioning started on node node001

node001: image update in progress ...

[basecm11->device]% Provisioning completed on node node001


**5.6.3** **Updating Running Nodes: With Base View Using the** Update node **Option**
In Base View, an image update can be carried out by selecting the specific node or category, for example
node001, and updating it via the navigation path:
Devices - Nodes[node001] - Edit - Software image - Update node


**5.6.4** **Updating Running Nodes: Considerations**
An attempt to update the image on a running node can run into some issues:


  - Updating an image via cmsh or Base View automatically updates the provisioners first via the
updateprovisioners command (section 5.2.4) if the provisioners have not been updated in the last
5 minutes. The conditional update period can be set with the dirtyautoupdatetimeout parameter
(section 5.2.4).


**5.7 Adding New Nodes** **285**


So, with the default setting of 5 minutes, if there has been a new image created within the last 5
minutes, then provisioners do not get the updated image when doing the updates, which means
that nodes in turn do not get those updates. Running the updateprovisioners command just
before running the imageupdate command therefore usually makes sense.


  - By default, BCM does not allow provisioning if automount (page 868) is running.


  - Also, when updating services, the services on the nodes may not restart since the init process
may not notice the replacement.


For these reasons, especially for more extensive changes, it can be safer for the administrator to simply
reboot the nodes instead of using imageupdate to provision the images to the nodes. A reboot by default
ensures that a node places the latest image with an AUTO install (section 5.4.7), and restarts all services.
The Reinstall node option, which can be run, for example, on a node node001, using a navigation
path of Devices - Nodes[node001] - Edit - Software image - Reinstall node also does the same as a
reboot with default settings, except for that it unconditionally places the latest image with a FULL install,
and so may take longer to complete.


**5.7** **Adding New Nodes**


How the administrator can add a single node to a cluster is described in section 1.3 of the _Installation_
_Manual_ . This section explains how nodes can be added in ways that are more convenient for larger
numbers of nodes.


**5.7.1** **Adding New Nodes With** cmsh **And Base View Add Functions**
Node objects can be added from within the device mode of cmsh by running the add command:


**Example**


[basecm11->device]% add physicalnode node002 10.141.0.2

[basecm11->device*[node002*]% commit


The Base View equivalent of this is following the navigation path:
Devices - Nodes - ADD - PhysicalNode [Settings] > Hostname
then adding the value node002 to Hostname, and saving it.
When adding the node objects in cmsh and Base View, some values (the MAC addresses for example)
may need to be filled in before the object validates. For regular nodes, there should be an interface and
an IP address for the network that it boots from, as well as for the network that manages the nodes. A
regular node typically has only one interface, which means that the same interface provides boot and
management services. This interface is then the boot interface, BOOTIF, during the pre-init stage, but is
also the management interface, typically eth0 or whatever the device is called, after the pre-init stage.
The IP address for BOOTIF is normally provided via DHCP, while the IP address for the management
interface can be set to a static IP address via cmsh or Base View by the administrator.
Adding new node objects as “placeholders” can also be done from cmsh or Base View. By placeholders, here it is meant that an incomplete node object is set. For example, sometimes it is useful to create a
node object with the MAC address setting unfilled because it is still unknown. Why this can be useful
is covered shortly.


**5.7.2** **Adding New Nodes With The Node Creation Wizard**
Besides adding nodes using the add command of cmsh or the ADD button of Base View as in the preceding
text, there is also a Base View wizard that guides the administrator through the process—the _node creation_
_wizard_ . This is useful when adding many nodes at a time. It is available via the navigation path:

Devices  - Nodes  - CREATE NODES


**286** **Node Provisioning**


This wizard should not be confused with the closely-related node _identification_ resource described in
section 5.4.2, which identifies unassigned MAC addresses and switch ports, and helps assign them node

names.


  - The node _creation_ wizard creates an object for nodes, assigns them node names, but it leaves the
MAC address field for these nodes unfilled, keeping the node object as a “placeholder”.


  - The node _identification_ resource assigns MAC addresses so that node names are associated with a
MAC address.


If a node is left with an unassigned MAC address—that is, in a “placeholder” state—then it means
that when the node starts up, the provisioning system lets the administrator associate a MAC address
and switch port number at the node console for the node. This occurs when the node-installer reaches
the node configuration stage during node boot as described in section 5.4.2. This is sometimes preferable
to associating the node name with a MAC address remotely with the node identification resource.
In the first screen of the node creation wizard, IP address range suggestions are displayed for the new
placeholder nodes. The administrator can override the range. The same screen also allows a category to
be selected for the nodes (figure 5.18).


Figure 5.18: Node Creation Wizard: Setting Interfaces


The remaining screens of the wizard configure the interface assignment and excutes the object creation. Once the object has been created, node identification (section 5.4.2) can be carried out.
The cmsh equivalent of the node creation wizard is running foreach --clone on a node that is to be
cloned over a node range (section 2.5.5, page 65).


**5.8 Troubleshooting The Node Boot Process** **287**


**5.8** **Troubleshooting The Node Boot Process**


During the node boot process there are several common issues that can lead to an unsuccessful boot.
This section describes these issues and their solutions. It also provides general hints on how to analyze
boot problems.
Before looking at the various stages in detail, the administrator may find that simply updating software or firmware may fix the issue. In general, it is recommended that all available updates are deployed
on a cluster.


  - Updating software is covered in Chapter 9.


**–** On the head node, the most relevant software can be updated with yum, zypper, or apt, as
explained in section 9.2. For example, with yum :


**Example**


yum update cmdaemon node-installer


**–**
Similarly for the software image, the most relevant software can be updated too. This is done
via a procedure involving a chroot installation., as described in section 9.4. If using yum, then
the update can be carried out within the image, < _software image_      -, with:


**Example**


yum update --installroot=/cm/images/< _software image_      - cmdaemon node-installer-slave


  - UEFI or BIOS firmware should be updated as per the vendor recommendation


The various stages that may fail during node boot are now examined.


**5.8.1** **Node Fails To PXE Boot**

Possible reasons to consider if a node is not even starting to network boot (PXE boot for x86 nodes) in
the first place:


  - DHCP may not be running. A check can be done to confirm that DHCP is running on the internal
network interface (usually eth0):


[root@basecm11 ~]# ps u -C dhcpd

USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND

root 2448 0.0 0.0 11208 436 ? Ss Jan22 0:05 /usr/sbin/dhcpd eth0


This may indicate that Node booting is disabled in Base View (figure 3.5, page 94) and needs to be
enabled. The equivalent in cmsh is to check if the response to:


cmsh -c "network use internalnet; get nodebooting"


needs to be set to yes .


  - The DHCP daemon may be “locked down” (section 3.2.1: figure 3.5 and table 3.1). New nodes are
granted leases only after lockdowndhcpd is set to no in cmsh, or Lock down dhcpd is disabled in
Base View for the network.


  - A rogue DHCP server may be running. If there are all sorts of other machines on the network the
nodes are on, then it is possible that there is a rogue DHCP server active on it, perhaps on an IP
address that the administrator has forgotten, and interfering with the expected PXE booting. Such
stray DHCP servers should be eliminated.


**288** **Node Provisioning**


**–**
One way to identify the problem is to remove all the connections and switches and just connect the head node directly to a problem node, NIC-to-NIC. This should allow a normal network boot to happen. If a normal network boot then does happen, it indicates the problem is
indeed due to a rogue DHCP server on the more-connected network.


**–** For a more cerebral approach, which avoids recabling, the nmap utility may be useful.
The nmap utility since version 7.90 can discover and list multiple DHCP servers using its
broadcast-dhcp-discover script. The following session output shows the configuration and
installation of the utility on to node002 on the internal network. It then runs it for the internal
network interface ens3 . If it finds a second DHCP server on the network (in this test case
on node001 at 10.141.0.1), then it may show responses in the output similar to the following
(some output ellipsized):


**Example**


[root@node002 ~]# wget https://nmap.org/dist/nmap-7.90.tgz

...

[root@node002 ~]# tar xvzf nmap-7.90

...

[root@node002 ~]# cd nmap-7.90

[root@node002 nmap-7.90]# make distclean && ./configure --disable-rdma && make

...

[root@node002 nmap-7.90]# ./nmap --script broadcast-dhcp-discover -e ens3
Starting Nmap 7.90 ( https://nmap.org ) at 2022-09-08 16:55 CEST

Pre-scan script results:
| broadcast-dhcp-discover:
| Response 1 of 2:

| IP Offered: 10.141.163.254

| DHCP Message Type: DHCPOFFER

| Server Identifier: 10.141.0.1

...

| Response 2 of 2:

| IP Offered: 10.141.167.255

| DHCP Message Type: DHCPOFFER

| Server Identifier: 10.141.255.254

...

[root@node002 nmap-7.90]#


  - The boot sequence may be set wrongly in the BIOS. The boot interface should normally be set to
be the first boot item in the BIOS.


  - The node may be set to boot from UEFI mode. If UEFI mode has a buggy network boot implementation, then it may fail to network boot. For x86 nodes, setting the node to PXE boot using the
legacy BIOS mode can be tried instead, or perhaps the UEFI firmware can be updated.


  - There may a bad cable connection. This can be due to moving the machine, or heat creep, or
another physical connection problem. Firmly inserting the cable into its slot may help. Replacing
the cable or interface as appropriate may be required.


  - There may a problem with the switch. Removing the switch and connecting a head node and a
regular node directly with a cable can help troubleshoot this.


Disabling the Spanning Tree Protocol (STP) functions of a managed switch is recommended. With
STP on, nodes may randomly fail to network boot.


  - The cable may be connected to the wrong interface. By default, on the head node, for a type 1
network, the first consistent network device name, for example eno1, is normally assigned the


**5.8 Troubleshooting The Node Boot Process** **289**


internal network interface, and the second one, for example en02, is assigned the external network
interface. However, the following possibilities should be considered during troubleshooting:


**–**
The two interfaces can be confused when physically viewing them and a connection to the
wrong interface can therefore be made.


**–**
It is also possible that the administrator has changed the default assignment.


**–**
The interface may have been set by the administrator to follow the network device naming
scheme that has been used prior to RHEL7. Interfaces with names such as eth0 and eth1 on
the head node are suggestive of this. The problem with the pre-RHEL7 scheme is that it can
sometimes lead to network interfaces swapping after reboot, which is why the scheme is no
longer recommended. The workaround for this issue in pre-RHEL7 schemes was to define a
persistent name in the udev ruleset for network interfaces.
From NVIDIA Base Command Manager version 9.0 onward, the default scheme is the consistent network device naming scheme, and it is recommended.


**Interface Naming Conventions Post-RHEL7 (Recommended)**

[https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/ch-Consistent_Network_Device_Naming.html)
[Networking_Guide/ch-Consistent_Network_Device_Naming.html](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/ch-Consistent_Network_Device_Naming.html) describes the consistent
network device scheme for interfaces post-RHEL7. This scheme sets an interface assignment
on iPXE boot for multiple interfaces that is also valid by default during the very first iPXE
boot. This means that an administrator can know which interface is used for provisioning
and can connect the provisioning cable accordingly.
Some care may need to be taken in unusual naming assignments, in order to avoid exceeding
the 16-character limit that Linux has for the naming of network interfaces.


**Reverting To The Pre-RHEL7 Interface Naming Conventions (Not Recommended)**

To revert to the pre-RHEL7 behavior, the text:


net.ifnames=0 biosdevname=0


can be appended to the line starting with GRUB_CMDLINE_LINUX in /etc/default/grub within
the head node. For this:


       - [The] [ biosdevname] [ parameter only works if the dev helper is installed. The dev helper]
is available from the biosdevname RPM package. The parameter also requires that the
system supports SMBIOS 2.6 or ACPI DSM.

       - [The] [ net.ifnames] [ parameter is needed if] [ biosdevname] [ is not installed.]


**Example**


GRUB_CMDLINE_LINUX="rd.lvm.lv=centos/swap vconsole.keymap=us \
crashkernel=auto rd.lvm.lv=centos/root vconsole.font=latarcyr\

heb-sun16 rhgb quiet net.ifnames=0 biosdevname=0"


A cautious system administrator may back up the original grub.cfg file:


[root@basecm11 ~]# cp --preserve /boot/grub2/grub.cfg /boot/grub2/grub.cfg.orig


The GRUB configuration should be generated with:


[root@basecm11 ~]# grub2-mkconfig -o /boot/grub2/grub.cfg


If for some reason the administrator would like to carry out the pre-RHEL7 naming convention on a regular node, then the text net.ifnames=0 biosdevname=0 can be appended to the
kernelparameters property, for an image selected from softwareimage mode.


**Example**


**290** **Node Provisioning**


[basecm11->softwareimage]% list
Name (key) Path

-------------------- -----------------------------
default-image /cm/images/default-image
openstack-image /cm/images/openstack-image

[basecm11->softwareimage]% use default-image

[basecm11->softwareimage[default-image]]% append kernelparame _\_

ters " net.ifnames=0 biosdevname=0"

[basecm11->softwareimage*[default-image*]]% commit


The append command requires a space at the start of the quote, in order to separate the kernel
parameters from any pre-existing ones.


  - The TFTP server that sends out the image may have hung. During a normal run, an output similar
to this appears when an image is in the process of being served:


[root@basecm11 ~]# ps ax | grep [t]ftp
7512 ? Ss 0:03 in.tftpd --maxthread 500 /tftpboot


If the TFTP server is in a zombie state, the head node should be rebooted. If the TFTP service
hangs regularly, there is likely a networking hardware issue that requires resolution.


Incidentally, grepping the process list for a TFTP service returns nothing when the head node
is listening for TFTP requests, but not actively serving a TFTP image. This is because the TFTP
service runs under xinet.d and is called on demand. Running


[root@basecm11 ~]# chkconfig --list


should include in its output the line:


tftp: on


if TFTP is running under xinet.d.


  - The switchover process from TFTP to HTTP may have hung. During a normal provisioning run,
assuming that CMDaemon uses the default bootloaderprotocol setting of HTTP, then TFTP is
used to load the initial boot loader, but the kernel and ramdisk are loaded up via HTTP for speed.
Some hardware has problems with switching over to using HTTP.


In that case, setting bootloaderprotocol to TFTP keeps the node using TFTP for loading the kernel
and ramdisk, and should work. Another possible way to solve this is to upgrade the PXE boot
BIOS to a version that does not have this problem.


ARMv8 hardware can boot only via TFTP .


Setting bootloaderprotocol to HTTPS only works for some special hardware.


  - VLAN tagging may have been set up incorrectly in the BIOS of the node. VLAN provisioning
(section 5.3.4) requires several changes in VLAN configuration for it to work.


  - Sometimes a manufacturer releases hardware with buggy drivers that have a variety of problems.
For instance: Ethernet frames may be detected at the interface (for example, by ethtool ), but
TCP/IP packets may not be detected (for example, by wireshark ). In that case, the manufacturer
should be contacted to upgrade their driver.


  - The interface may have a hardware failure. In that case, the interface should be replaced.


**5.8 Troubleshooting The Node Boot Process** **291**


**5.8.2** **Node-installer Logging**
If the node manages to get beyond the net booting stage to the node-installer stage, then the first place
to look for hints on node boot failure is usually the node-installer log file. The node-installer runs on the
node that is being provisioned, and sends logging output to the syslog daemon running on that node.
This forwards all log data to the IP address from which the node received its DHCP lease, which is
typically the IP address of the head node or failover node. In a default BCM setup, the local5 facility of
the syslog daemon is used on the node that is being provisioned to forward all node-installer messages
to the log file /var/log/node-installer on the head node.
After the node-installer has finished running, its log is also stored in /var/log/node-installer on
the regular nodes.
If there is no node-installer log file anywhere yet, then it is possible that the node-installer is not yet
deployed on the node. Sometimes this is due to a system administrator having forgotten to change a
provisioning-related configuration setting. One possibility is that the nodegroups setting (section 5.2.1),
if used, may be misconfigured. Another possibility is that the image was set to a locked state (section 5.4.7). The provisioningstatus -a command can indicate this:


**Example**


[basecm11->softwareimage]% provisioningstatus -a | grep locked

Scheduler info: requested software image is locked, request deferred


To get the image to install properly, the locked state should be removed for a locked image.


**Example**


[root@basecm11 ~]# cmsh -c "softwareimage islocked"

Name Locked

-------------- -------
default-image yes

[root@basecm11 ~]# cmsh -c "softwareimage unlock default-image"

[root@basecm11 ~]# cmsh -c "softwareimage islocked"

Name Locked

-------------- -------
default-image no


The node automatically picks up the image after it is unlocked.
Optionally, extra log information can be written by enabling debug logging, which sets the
syslog importance level at LOG_DEBUG . To enable debug logging, the debug field is changed in
/cm/node-installer/scripts/node-installer.conf .
For the node-installer.conf file in multidistro and multiarch (section 9.7) configurations, the directory path /cm/node-installer takes the form:
/cm/node-installer- _<distribution>-<architecture>_
The values for _<distribution>_ and _<architecture>_ can take the values outlined on page 528.
From the console of the booting node the log file is generally accessible by pressing Alt+F7 on the
keyboard. Debug logging is however excluded from being viewed in this way, due to the output volume
making this impractical.
A booting node console can be accessed remotely if Serial Over LAN (SOL) is enabled (section 14.7),
to allow the viewing of console messages directly. A further depth in logging can be achieved by setting
the kernel option loglevel=N, where N is a number from 0 ( KERN_EMERG ) to 7 ( KERN_DEBUG ).
One possible point at which the node-installer can fail on some hardware is if SOL (section 14.7)
is enabled in the BIOS, but the hardware is unable to cope with the flow. The installation can freeze
completely at that point. This should not be confused with the viewing quirk described in section 14.7.4,
even though the freeze typically appears to take place at the same point, that point being when the
console shows “ freeing unused kernel memory ” as the last text. One workaround to the freeze would
be to disable SOL.


**292** **Node Provisioning**


**5.8.3** **Provisioning Logging**
The provisioning system sends log information to the CMDaemon log file. By default this is in
/var/log/cmdaemon on the local host, that is, the provisioning host. The host this log runs on can be
configured with the CMDaemon directive SyslogHost (Appendix C).
The image synchronization log file can be retrieved with the synclog command (page 267) running
from device mode in cmsh . Hints on provisioning problems are often found by looking at the tail end of
the log.
If the tail end of the log shows an rsync exit code of 23, then it suggests a transfer error. Sometimes
the cause of the error can be determined by examining the file or filesystem for which the error occurs.
For the rsync transport, logs for node installation are kept under /var/spool/cmd/, with a log written
for each node during provisioning. The name of the node is set as the prefix to the log name. For
example node002 generates the log:


/var/spool/cmd/node002-\.rsync


**5.8.4** **Ramdisk Fails During Loading Or Sometime Later**
One issue that may come up after a software image update via yum, zypper, or apt (section 9.4), is
that the ramdisk stage may fail during loading or sometime later, for a node that is rebooted after the
update. This occurs if there are instructions to modify the ramdisk by the update. In a normal machine
the ramdisk would be regenerated. In a cluster, the extended ramdisk that is used requires an update,
but BCM is not aware of this. Running the createramdisk command from cmsh or the Recreate Initrd
command via the Base View navigation paths:


 - Devices  - Nodes  - Edit  - Kernel  - Recreate Initrd


 - Grouping  - Node Categories  - Edit  - Kernel  - Recreate Initrd


 - Provisioning  - Software Images  - Edit  - Recreate Initrd


(section 5.3.2) generates an updated ramdisk for the cluster, and solves the failure for this case.


Another, somewhat related possible cause of a halt at this stage, is that the kernel modules that are
to be loaded may have been specified at a wrongly by the administrator in the hierarchy of software
image, category, or node (page 237). A check of the kernel modules specified in softwareimage mode,
category mode, or device mode (for the particular node) may reveal a misconfiguration.


**5.8.5** **Ramdisk Cannot Start Network**

The ramdisk must activate the node’s network interface in order to fetch the node-installer. To activate

the network device, the correct kernel module needs to be loaded. If this does not happen, booting fails,
and the console of the node displays something similar to figure 5.19.


**5.8 Troubleshooting The Node Boot Process** **293**


Figure 5.19: No Network Interface


To solve this issue the correct kernel module should be added to the software image’s kernel module
configuration (section 5.3.2). For example, to add the e1000 module to the default image using cmsh :


**Example**


[mc]% softwareimage use default-image

[mc->softwareimage[default-image]]% kernelmodules

[mc->softwareimage[default-image]->kernelmodules]% add e1000

[mc->softwareimage[default-image]->kernelmodules[e1000]]% commit

Initial ramdisk for image default-image was regenerated successfully

[mc->softwareimage[default-image]->kernelmodules[e1000]]%


After committing the change it typically takes about a minute before the initial ramdisk creation is
completed via a mkinitrd run by CMDaemon.


**5.8.6** **Node-Installer Cannot Create Disk Layout**
When the node-installer is not able to create a drive layout it displays a message similar to figure 5.20.
The node-installer log file (section 5.8.2) contains something like:


Mar 24 13:55:31 10.141.0.1 node-installer: Installmode is: AUTO

Mar 24 13:55:31 10.141.0.1 node-installer: Fetching disks setup.

Mar 24 13:55:31 10.141.0.1 node-installer: Checking partitions and

filesystems.
Mar 24 13:55:32 10.141.0.1 node-installer: Detecting device '/dev/sda':

not found

Mar 24 13:55:32 10.141.0.1 node-installer: Detecting device '/dev/hda':

not found

Mar 24 13:55:32 10.141.0.1 node-installer: Can not find device(s) (/dev/sda /dev/hda).

Mar 24 13:55:32 10.141.0.1 node-installer: Partitions and/or filesystems
are missing/corrupt. (Exit code 4, signal 0)

Mar 24 13:55:32 10.141.0.1 node-installer: Creating new disk layout.


**294** **Node Provisioning**


Mar 24 13:55:32 10.141.0.1 node-installer: Detecting device '/dev/sda':

not found

Mar 24 13:55:32 10.141.0.1 node-installer: Detecting device '/dev/hda':

not found

Mar 24 13:55:32 10.141.0.1 node-installer: Can not find device(s) (/dev/sda /dev/hda).

Mar 24 13:55:32 10.141.0.1 node-installer: Failed to create disk layout.
(Exit code 4, signal 0)
Mar 24 13:55:32 10.141.0.1 node-installer: There was a fatal problem. This node can not be\

installed until the problem is corrected.


Figure 5.20: No Disk


Disk layout failures can have several reasons.


**BIOS And Order Issues**

One reason may be that the drive may be disabled in the BIOS. It should be enabled.
Another reason may be that the drive order was changed. This could happen if, for example, a
defective motherboard has been replaced. The drive order should be kept the same as it was before a
motherboard change.


**Read-only Mode Issues**
Another reason may be due to SSDs that have a hardware jumper or toggle switch that sets a drive to
read-only mode. A read-only mode drive will typically fail at this point. The drive should be made
writeable.


**Hardware Issues**

If the node-installer log for the node shows lines with the text Input/output error, then it generally
indicates a hardware issue. Possible hardware issues include:


  - a drive failure


  - a faulty cable between storage and controller


**5.8 Troubleshooting The Node Boot Process** **295**


  - a faulty storage controller


  - a faulty backplane in the server


If the node has enough RAM, then it is possible to boot up the node up as a diskless node, to carry out
further diagnosis with disk tools such as smartmontools .


**Software Driver Issues**

One of the most common software issues is that the correct storage driver is not being loaded. To
solve this issue, the correct kernel module should be added to the software image’s kernel module
configuration (section 5.3.2).
Experienced system administrators work out what drivers may be missing by checking the results
of hardware probes. For example, going into the node-installer shell using Alt-F2, and then looking at
the output of lspci, shows a list of hardware detected in the PCI slots and gives the chipset name of the
storage controller hardware in this case:


**Example**


[<installer> root@node001 ~]# lspci | grep SCSI
00:10.0 Serial Attached SCSI controller: LSI Logic / Symbios Logic SAS2 _\_
008 PCI-Express Fusion-MPT SAS-2 [Falcon] (rev 03)


The next step is to Google with likely search strings based on that output.
The Linux Kernel Driver DataBase (LKDDb) is a hardware database built from kernel sources that
lists driver availability for Linux. It is available at [http://cateee.net/lkddb/](http://cateee.net/lkddb/) . Using the Google search
engine’s “ site ” operator to restrict results to the cateee.net web site only, a likely string to try might
be:


**Example**


SAS2008 site:cateee.net


The search result indicates that the mpt2sas kernel module needs to be added to the node kernels. A
look in the modules directory of the software image shows if it is available:


**Example**


find /cm/images/default-image/lib/modules/ -name "*mpt2sas*"


If it is not available, the driver module must then be obtained. If it is a source file, it will need to
be compiled. By default, nodes run on standard distribution kernels, so that only standard procedures
need to be followed to compile modules.
If the module is available, it can be added to the default image, by using cmsh in softwareimage
mode to create the associated object. The object is given the same name as the module, i.e. mp2sas in
this case:


**Example**


[basecm11]% softwareimage use default-image

[basecm11->softwareimage[default-image]]% kernelmodules

[basecm11->softwareimage[default-image]->kernelmodules]% add mpt2sas

[basecm11->softwareimage[default-image]->kernelmodules*[mpt2sas*]]% commit

[basecm11->softwareimage[default-image]->kernelmodules[mpt2sas]]%
Thu May 19 16:54:52 2011 [notice] basecm11: Initial ramdisk for image de _\_

fault-image is being generated

[basecm11->softwareimage[default-image]->kernelmodules[mpt2sas]]%
Thu May 19 16:55:43 2011 [notice] basecm11: Initial ramdisk for image de _\_

fault-image was regenerated successfully.

[basecm11->softwareimage[default-image]->kernelmodules[mpt2sas]]%


**296** **Node Provisioning**


After committing the change it can take some time before ramdisk creation is completed—typically
about a minute, as the example shows. Once the ramdisk is created, the module can be seen in the list
displayed from kernelmodules mode. On rebooting the node, it should now continue past the disk
layout stage.


**5.8.7** **Node-Installer Cannot Start BMC (IPMI/iLO) Interface**
In some cases the node-installer is not able to configure a node’s BMC interface, and displays an error
message similar to figure 5.21.


Figure 5.21: No BMC Interface


Usually the issue can be solved by adding the correct BMC (IPMI/iLO) kernel modules to the software image’s kernel module configuration. However, in some cases the node-installer is still not able to
configure the BMC interface. If this is the case the BMC probably does not support one of the commands
the node-installer uses to set specific settings, or there may be a hardware glitch in the BMC.


**The** setupBmc **Node-Installer Configuration Setting**
To solve this issue, setting up BMC interfaces can be disabled globally by setting the setupBmc field
to false in the node-installer configuration file /cm/node-installer/scripts/node-installer.conf
(for multiarch/multidistro configurations the path takes the form: /cm/node-installer- _<distribution>-_
_<architecture>_ /scripts/node-installer.conf ).
Doing this disables configuration of all BMC interfaces by the node-installer. A custom finalize
script (Appendix E) can then be used to run the required commands instead.
The setupBmc field in the node-installer should not be confused with the SetupBMC directive in
cmd.conf (Appendix C). The former is about enabling the BMC interface, while the latter is about enabling automated passwords to the BMC interface (an interface that must of course be enabled in the
first place to work).


**The** failOnMissingBmc **Node-Installer Configuration Setting**
If the kernel modules for the BMC are loaded up correctly, and the BMC is configured, but it is not
detected by the node-installer, then the node-installer halts by default. This corresponds to the set

**5.8 Troubleshooting The Node Boot Process** **297**


ting failOnMissingBmc = true in the node-installer configuration file /cm/node-installer/scripts/
node-installer.conf . Toggling this to false skips BMC network device detection, and lets the nodeinstaller continue past the BMC detection and configuration stage. This can be convenient, for example,
if the BMC is not yet configured and the aim is to get on with setting up the rest of the cluster.


**The** failOnFailedBmcCommand **Node-Installer Configuration Setting**
If a BMC command fails, then the node-installer by default terminates node installation. The idea behind
this is to allow the administrator to fix the problem. Sometimes, however, hardware can wrongly signal
a failure. That is, it can signal a false failure, as opposed to a true failure.
A common case is the case of ipmitool . ipmitool is used by BCM to configure the BMC. With
most hardware vendors it works as expected, signaling success and failure correctly. As per the default
behavior: with success, node installation proceeds, while with failure, it terminates.
With certain hardware vendors however ipmitool fails with an exit code 1, even though the BMC
is properly configured. Again, as per the default behavior: success has node installation proceed, while
failure has node installation terminate. Only this time, because the failure signal is incorrect, the termination on failure is also incorrect behavior.

To get around the default behavior for false failure cases, the administrator can force
the node-installer to set the value of failOnFailedBmcCommand to false in the node
installer configuration file /cm/node-installer/scripts/node-installer.conf (for multiarch/multidistro configurations the path takes the form: /cm/node-installer- _<distribution>-_
_<architecture>_ /scripts/node-installer.conf ). The installation then skips past the false failure.


**BMC Hardware Glitch And Cold Reset**

Sometimes, typically due to a hardware glitch, a BMC can get into a state where it is not providing
services, but the BMC is still up (responding to pings). Contrariwise, a BMC may not respond to pings,
but still respond to IPMI commands. A fix for such glitchy states is usually to power cycle the BMC.
This is typically done, either physically, or by using a BMC management tool such as ipmitool .
Physically resetting the power supply to the BMC is done typically by pulling the power cable out
and then pushing it in again. For typical rack-based servers the server can just be pulled out and in
again. Just doing a shutdown of the server with the power cable still in place normally does not power
down the BMC.

BMC management does allow the BMC to power down and be reset from software, without having
to physically handle the server. This software-based _cold reset_ is a BIOS-manufacturer-dependent feature.
A popular tool used for managing BMCs that can do such a cold reset is ipmitool . This can be run
remotely, but also on the node console if the node cannot be reached remotely.
With ipmitool, a cold reset is typically carried out with a command such as:


[root@basecm11 ~]# module load ipmitool

[root@basecm11 ~]# ipmitool -U < _bmcusername_ - -P < _bmcpassword_ - -H < _host IP_ - -I lanplus mc reset cold


The values for < _bmcusername_  - and < _bmcpassword_  - can be obtained as shown in section 3.7.2.


**BMC Troubleshooting With The System Event Log**
The System Event Log (SEL) can be read with:


[root@basecm11 ~]# module load ipmitool

[root@basecm11 ~]# ipmitool -U < _bmcusername_ - -P < _bmcpassword_ - -H < _host IP_ - -I lanplus sel list


The timestamped output can be inspected for errors related to the CPU, ECC, or memory.


**Other BMC Troubleshooting**
Some more specific commands for handling IPMI might be via the service ipmi < _option_ - commands,
which can show the IPMI service has failed to start up:


**298** **Node Provisioning**


**Example**


[root@basecm11 ~]# service ipmi status
Redirecting to /bin/systemctl status ipmi.service

ipmi.service - IPMI Driver
Loaded: loaded (/usr/lib/systemd/system/ipmi.service; disabled; vendor preset: enabled)

Active: inactive (dead)


In the preceding session the driver has simply not been started up. It can be started up with the start
option:


**Example**


[root@basecm11 ~]# service ipmi start
Redirecting to /bin/systemctl start ipmi.service
Job for ipmi.service failed because the control process exited with error code. See "systemctl _\_

status ipmi.service" and "journalctl -xe" for details.


In the preceding session, the start up failed. The service status output shows:


**Example**


[root@basecm11 ~]# service ipmi status -l
Redirecting to /bin/systemctl status -l ipmi.service

ipmi.service - IPMI Driver
Loaded: loaded (/usr/lib/systemd/system/ipmi.service; disabled; vendor preset: enabled)
Active: failed (Result: exit-code) since Mon 2016-12-19 14:34:27 CET; 2min 3s ago
Process: 8930 ExecStart=/usr/libexec/openipmi-helper start (code=exited, status=1/FAILURE)
Main PID: 8930 (code=exited, status=1/FAILURE)


Dec 19 14:34:27 basecm11 systemd[1]: Starting IPMI Driver...
Dec 19 14:34:27 basecm11 openipmi-helper[8930]: Startup failed.
Dec 19 14:34:27 basecm11 systemd[1]: ipmi.service: main process exited, code=exited, status=1/ _\_

FAILURE

Dec 19 14:34:27 basecm11 systemd[1]: Failed to start IPMI Driver.
Dec 19 14:34:27 basecm11 systemd[1]: Unit ipmi.service entered failed state.
Dec 19 14:34:27 basecm11 systemd[1]: ipmi.service failed.


Further details can be found in the journal:


**Example**


[root@basecm11 ~]# journalctl -xe | grep -i ipmi

...

-- Unit ipmi.service has begun starting up.

Dec 19 14:34:27 basecm11 kernel: ipmi message handler version 39.2

Dec 19 14:34:27 basecm11 kernel: IPMI System Interface driver.
Dec 19 14:34:27 basecm11 kernel: ipmi_si: Unable to find any System Interface(s)
Dec 19 14:34:27 basecm11 openipmi-helper[8930]: Startup failed.

...


In the preceding session, the failure is due to a missing BMC interface ( Unable to find any System
Interface(s) ). A configured BMC interface should show an output status similar to:


**Example**


**5.8 Troubleshooting The Node Boot Process** **299**


[root@basecm11 ~]# service ipmi status
Redirecting to /bin/systemctl status ipmi.service

ipmi.service - IPMI Driver
Loaded: loaded (/usr/lib/systemd/system/ipmi.service; disabled; vendor preset: enabled)
Active: active (exited) since Mon 2016-12-19 14:37:10 CET; 2min 0s ago
Process: 61019 ExecStart=/usr/libexec/openipmi-helper start (code=exited, status=0/SUCCESS)
Main PID: 61019 (code=exited, status=0/SUCCESS)

Dec 19 14:37:10 basecm11 systemd[1]: Starting IPMI Driver...
Dec 19 14:37:10 basecm11 systemd[1]: Started IPMI Driver.


Sometimes the issue may be an incorrect networking specification for the BMC interfaces. MAC and
IP details that have been set for the BMC interface can be viewed with the lan print option to ipmitool
if the service has been started:


**Example**


[root@basecm11 ~]# module load ipmitool

[root@basecm11 ~]# ipmitool lan print

Set in Progress : Set Complete

Auth Type Support : MD5 PASSWORD

Auth Type Enable : Callback : MD5 PASSWORD

: User : MD5 PASSWORD

: Operator : MD5 PASSWORD

: Admin : MD5 PASSWORD

: OEM :

IP Address Source : Static Address

IP Address : 93.184.216.34

Subnet Mask : 255.255.255.0

MAC Address : aa:bb:01:02:cd:ef

SNMP Community String : public

IP Header : TTL=0x00 Flags=0x00 Precedence=0x00 TOS=0x00

BMC ARP Control : ARP Responses Enabled, Gratuitous ARP Disabled

Gratituous ARP Intrvl : 0.0 seconds

Default Gateway IP : 93.184.216.1

Default Gateway MAC : 00:00:00:00:00:00

Backup Gateway IP : 0.0.0.0

Backup Gateway MAC : 00:00:00:00:00:00

802.1q VLAN ID : Disabled

802.1q VLAN Priority : 0

RMCP+ Cipher Suites : 0,1,2,3,4,6,7,8,9,11,12,13,15,16,17,18

Cipher Suite Priv Max : caaaaaaaaaaaaaa

: X=Cipher Suite Unused

: c=CALLBACK

: u=USER

: o=OPERATOR

: a=ADMIN

: O=OEM


During normal operation the metrics (Appendix G) displayed by BCM are useful. However, if those
are not available for some reason, then the direct output from BMC sensor metrics may be helpful for
troubleshooting:


**Example**


[root@basecm11 ~]# module load ipmitool

[root@basecm11 ~]# ipmitool sensor list all


**300** **Node Provisioning**


# ipmitool sensor list
Ambient Temp | 22.000 | degrees C | ok | na | na | na | 38.000 | 41.000 | 45.000

AVG Power | 300.000 | Watts | ok | na | na | na | na | na | na

Fan 1 Tach | 4125.000 | RPM | ok | na | 750.000 | na | na | na | na

...


# **6**

### **User Management**

Users and groups for the cluster are presented to the administrator in a single system paradigm. That
is, if the administrator manages them with BCM, then the changes are automatically shared across the
cluster (the single system).
BCM runs its own LDAP service to manage users, rather than using unix user and group files. In
other words, users and groups are managed via the centralizing LDAP database server running on the
head node, and not via entries in /etc/passwd or /etc/group files.
Sections 6.1 and 6.2 cover the most basic aspects of how to add, remove and edit users and groups
using BCM.
Section 6.3 describes how an external LDAP server can be used for authentication services instead of

the one provided by BCM.
Section 6.4 discusses how users can be assigned only selected capabilities when using Base View or
cmsh, using profiles with sets of tokens.


**6.1** **Managing Users And Groups With Base View**


Within Base View:


  - users can be managed via the navigation path Identity Management  - Users


  - groups can be managed via the navigation path Identity Management  - Groups .


For users (figure 6.1) the LDAP entries for users are displayed. These entries are editable and each user
can then be managed in further detail.
There is already one user on a newly-installed BCM: cmsupport . This user has no password set by
default, which means (section 6.2.2) no logins to this account are allowed by default. BCM uses the user
cmsupport to run various diagnostics utilities, so it should not be removed, and the default contents of
its home directory should not be removed.
The + ADD button allows users to be added via a User parameters window (figure 6.2). The changes
in parameter values can be committed via the SAVE button in the User parameter window.


**302** **User Management**


Figure 6.1: Base View User Management


Figure 6.2: Base View User Management: Add Dialog


When saving an addition or modification:


  - User and group ID numbers are automatically assigned from UID and GID 1000 onward.


  - A home directory is created and a login shell is set. Users with unset passwords cannot log in.


Group management in Base View is carried out via the navigation path Identity Management  Groups . Clickable LDAP object entries for regular groups then show up, similar to the user entries
already covered. Management of these entries is done with the same functions as for user management.


**6.2 Managing Users And Groups With** cmsh **303**


**6.2** **Managing Users And Groups With** cmsh


User management tasks as carried out by Base View in section 6.1, can be carried with the same end
results in cmsh too.

A cmsh session is run here in order to cover the functions corresponding to the user management
functions of Base View of section 6.1. These functions are run from within the user mode of cmsh :


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% user

[basecm11->user]%


**6.2.1** **Adding A User**
This part of the session corresponds to the functionality of the Add button operation in section 6.1. In user
mode, the process of adding a user maureen to the LDAP directory is started with the add command:


**Example**


[basecm11->user]% add maureen

[basecm11->user*[maureen*]]%


The cmsh utility helpfully drops into the user object just added, and the prompt shows the user name
to reflect this. Going into user object would otherwise be done manually by typing use maureen at the
user mode level.

Asterisks in the prompt are a helpful reminder of a modified state, with each asterisk indicating that
there is an unsaved, modified property at that asterisk’s level.
The modified command displays a list of modified objects that have not yet been committed:


**Example**


[basecm11->user*[maureen*]]% modified

State Type Name

------ ----------------------- --------------
+ User maureen


This corresponds roughly to what is displayed by the Unsaved entities icon in the top right corner of
the Base View standard display (figure 10.5).
Running show at this point reveals a user name entry, but empty fields for the other properties of
user maureen . So the account in preparation, while it is modified, is clearly not yet ready for use:


**Example**


[basecm11->user*[maureen*]]% show

Parameter Value

----------------------------------- -----------------------------------------------
Accounts

Managees

Name maureen

Primary group

Revision

Secondary groups

ID

Common name

Surname

Group ID

Login shell


**304** **User Management**


Password < not set >

Home directory

Home directory operation yes

Email

Profile

Write ssh proxy config no

Create ssh key no

Disable password ssh no

Allow GPU workload power profiles no

Authorized ssh keys <0B>

Shadow min 0

Shadow max 999999

Shadow warning 7

Shadow inactive 0

Last change 1970/1/1
Expiration date 2038/1/1

Project manager <submode>

Notes <0B>


**6.2.2** **Saving The Modified State**
This part of the session corresponds to the functionality of the SAVE button operation in section 6.1.
In section 6.2.1 above, user maureen was added. maureen now exists as a proposed modification, but
has not yet been committed to the LDAP database.
Running the commit command now at the maureen prompt stores the modified state at the user
maureen object level:


**Example**


[basecm11->user*[maureen*]]% commit

[basecm11->user[maureen]]% show

Parameter Value

----------------------------------- -----------------------------------------------
Accounts

Managees

Name maureen

Primary group 1001

Revision

Secondary groups

ID 1001

Common name maureen

Surname maureen

Group ID 1001
Login shell /bin/bash

Password ********

Home directory /home/maureen

Home directory operation yes

Email

Profile

Write ssh proxy config no

Create ssh key no

Disable password ssh no

Allow GPU workload power profiles no

Authorized ssh keys <0B>

Shadow min 0

Shadow max 999999

Shadow warning 7


**6.2 Managing Users And Groups With** cmsh **305**


Shadow inactive 0

Last change 2025/5/20
Expiration date 2038/1/1

Project manager <submode>

Notes <0B>


If, however, commit were to be run at the user mode level without dropping into the maureen object
level, then instead of just that modified user, all modified users would be committed.
When the commit is done, all the empty fields for the user are automatically filled in with defaults
based the underlying Linux distribution used. Also, as a security precaution, if an empty field (that is, a
“not set”) password entry is committed, then a login to the account is not allowed. So, in the example,
the account for user maureen exists at this stage, but still cannot be logged into until the password is set.
Editing passwords and other properties is covered in section 6.2.3.
The default permissions for file and directories under the home directory of the user are defined by
the umask settings in /etc/login.defs, as would be expected if the administrator were to use the standard useradd command. Setting a path for the homedirectory parameter for a user sets a default home
directory path. By default the default path is /home/ < _username_ - for a user < _username_ >. If homedirectory
is unset, then the default is determined by the HomeRoot directive (Appendix C).


**6.2.3** **Editing Properties Of Users And Groups**
This corresponds roughly to the functionality of the Edit operation in section 6.1.
In the preceding section 6.2.2, a user account maureen was made, with an unset password as one of
its properties. Logins to accounts with an unset password are refused. The password therefore needs to
be set if the account is to function.


**Editing Users With** set **And** clear
The tool used to set user and group properties is the set command. Typing set and then either using
tab to see the possible completions, or following it up with the enter key, suggests several parameters
that can be set, one of which is password :


**Example**


[basecm11->user[maureen]]% set

Name:

set - Set specific user property


Usage:
set [OPTIONS] [user] <parameter> <value> [<value> ...]


Options:

-e, --extra

Set an extra free key/value parameter


-v, --vector

Set extra parameter values as a vector even for a single value


-t, --type <type>
Convert extra parameter values, type: [i]nt, [u]unsigned, f[float], d[double]


Arguments:

user name of the user, omit if current is set


Parameters:

name ................ User login (e.g. donald)

id .................. User ID number


**306** **User Management**


commonname .......... Full name (e.g. Donald Duck)
surname ............. Surname (e.g. Duck)

groupid ............. Base group of this user

loginshell .......... Login shell

homedirectory ....... Home directory

password ............ Password

homedirectoryoperation Set to false to not create or move home directory

shadowmin ........... Minimum number of days required between password changes

shadowmax ........... Maximum number of days for which the user password remains valid.

shadowwarning ....... Number of days of advance warning given to the user before the user password expire

shadowinactive ...... Number of days of inactivity allowed for the user

expirationdate ...... Date on which the user login will be disabled

email ............... Email

profile ............. Profile for Authorization

projectmanager ...... Project manager

notes ............... Administrator notes

writesshproxyconfig . Write ssh proxy config

createsshkey ........ Create ssh key for added users

disablepasswordssh .. Disable password ssh

authorizedsshkeys ... Authorized ssh keys

allowgpuworkloadpowerprofiles Allow changing GPU workload power profiles from jobs

revision ............ Entity revision

[basecm11->user[maureen]]%


Continuing the session from the end of section 6.2.2, the password can be set at the user context
prompt like this:


**Example**


[basecm11->user[maureen]]% set password seteca5tr0n0my

[basecm11->user*[maureen*]]% commit

[basecm11->user[maureen]]%


At this point, the account maureen is finally ready for use.
The converse of the set command is the clear command, which clears properties:


**Example**


[basecm11->user[maureen]]% clear password; commit


Setting a password in cmsh is also possible by setting the LDAP hash (the encrypted storage format)
that is generated from the password within cmsh . When setting passwords in cmsh, a string starting with
{MD5}, {CRYPT} or {SSHA} is considered to be the hash of the password:


**Example**


[root@basecm11 ~]# _#first create the LDAP salted SHA-1 hash of the password:_

[root@basecm11 ~]# /cm/local/apps/openldap/sbin/slappasswd -h {SSHA} -s seteca5tr0n0my

[root@basecm11 ~]# {SSHA}sViD+lfSTtlIy0MuGwPGfGd5XKHgEm5d

[root@basecm11 ~]# cmsh

[basecm11]% user use maureen

[basecm11->user[maureen]]% set password
enter new password: _#here and in the next line_ {SSHA}sViD+lfSTtlIy0MuGwPGfGd5XKHgEm5d _is typed in_

retype new password:

[basecm11->user[maureen]]% commit

[basecm11->user[maureen]]% !ssh maureen@node001 _#now will test the password that generated the hash_
Warning: Permanently added 'node001' (ECDSA) to the list of known hosts.


**6.2 Managing Users And Groups With** cmsh **307**


maureen@node001's password: _#here_ seteca5tr0n0my _is typed in_
Creating ECDSA key for ssh

[maureen@node001 ~]$ _#successfully logged in with the password associated with the hash_


Managing passwords in cmsh via direct LDAP hash entry is not normally done.


**Editing Groups With** append **And** removefrom
While the preceding commands set and clear also work with groups, there are two other commands
available which suit the special nature of groups. These supplementary commands are append and
removefrom . They are used to add extra users to, and remove extra users from a group.
For example, it may be useful to have a printer group so that several users can share access to a
printer. For the sake of this example (continuing the session from where it was left off in the preceding),
tim and fred are now added to the LDAP directory, along with a group printer :


**Example**


[basecm11->user[maureen]]% add tim; add fred

[basecm11->user*[fred*]]% exit; group; add printer

[basecm11->group*[printer*]]% commit

[basecm11->group[printer]]% exit; exit; user

[basecm11->user*]%


The context switch that takes place in the preceding session should be noted: The context of user
maureen was eventually replaced by the context of group printer . As a result, the group printer is
committed, but the users tim and fred are not yet committed, which is indicated by the asterisk at the
user mode level.

Continuing onward, to add users to a group the append command is used. A list of users maureen,
tim and fred can be added to the group printer like this:


**Example**


[basecm11->user*]% commit

Successfully committed 2 Users

[basecm11->user]% group use printer

[basecm11->group[printer]]% append members maureen tim fred; commit

[basecm11->group[printer]]% show

Parameter Value

------------------------ -------------------------
ID 1002

Revision

Name printer

Members maureen,tim,fred


To remove users from a group, the removefrom command is used. A list of specific users, for example,
tim and fred, can be removed from a group like this:


[basecm11->group[printer]]% removefrom members tim fred; commit

[basecm11->group[printer]]% show

Parameter Value

------------------------ -------------------------
ID 1002

Revision

Name printer

Members maureen


The clear command can also be used to clear members—but it also clears all of the extras from the

group:


**308** **User Management**


**Example**


[basecm11->group[printer]]% clear members

[basecm11->group*[printer*]]% show

Parameter Value

------------------------ -------------------------
ID 1002

Revision

Name printer

Members


The commit command is intentionally left out at this point in the session in order to illustrate how
reversion is used in the next section.


**6.2.4** **Reverting To The Unmodified State**
This corresponds roughly to the functionality of the Revert operation in section 6.1.
This section (6.2.4) continues on from the state of the session at the end of section 6.2.3. There, the
state of group printers was cleared so that the extra added members were removed. This state (the
state with no group members showing) was however not yet committed.
The refresh command reverts an uncommitted object back to the last committed state.
This happens at the level of the object it is using. For example, the object that is being handled here is
the properties of the group object printer . Running revert at a higher level prompt—say, in the group
mode level—would revert everything at that level and below. So, in order to affect only the properties
of the group object printer, the refresh command is used at the group object printer level prompt.
It then reverts the properties of group object printer back to their last committed state, and does not
affect other objects:


**Example**


[basecm11->group*[printer*]]% refresh

[basecm11->group[printer]]% show

Parameter Value

------------------------ -------------------------
ID 1002

Revision

Name printer

Members maureen


Here, the user maureen reappears because she was stored in the last save. Also, because only the
group object printer has been committed, the asterisk indicates the existence of other uncommitted,
modified objects.


**6.2.5** **Removing A User**
Removing a user using cmsh corresponds roughly to the functionality of the Delete operation in section 6.1.

The remove command removes a user or group. The useful “ -d|--data ” flag added to the end of
the username removes the user’s home directory too. For example, within user mode, the command
“ remove user maureen -d; commit ” removes user maureen, along with her home directory. Continuing the session at the end of section 6.2.4 from where it was left off, as follows, shows this result:


**Example**


[basecm11->group[printer]]% user use maureen

[basecm11->user[maureen]]% remove -d; commit

Successfully removed 1 Users


**6.3 Using An External LDAP Server** **309**


Successfully committed 0 Users

[basecm11->user]% !ls -d /home/*| grep maureen #no maureen left behind

[basecm11->user]%


**6.3** **Using An External LDAP Server**


Sometimes, an external LDAP server is used to serve the user database. If, instead of just using the
database for authentication, the user database is also to be managed, then its LDAP schema must match
the BCM LDAP schema.

For RHEL8, the /etc/nslcd.conf, /etc/openldap/ldap.conf, and the certificate files under /cm/
local/apps/openldap/etc/certs/ should be copied over. For RHEL9, /etc/sssd/sssd.conf is copied
over instead of /etc/nslcd.conf .
Port 636 on ShoreWall running on the head node should be open for LDAP communication over the
external network, if external nodes are using it on the external network. In addition, the external nodes
and the head node must be able to resolve each other.

By default, BCM runs an LDAP health check using the cmsupport user on the LDAP server. The
LDAP health check may need to be modified or disabled by the administrator to prevent spurious health
warnings with an external LDAP server:


**Modifying Or Disabling The** ldap **Healthcheck**
**Modifying the** ldap **health check:** To keep a functional ldap health check with an external LDAP
server, a permanent external LDAP user name, for example ldapcheck, can be added. This user can
then be set as the parameter for BCM’s ldap health check object that is used to monitor the LDAP
service. Health checks and health check objects are discussed in Chapter 10.


  - If user management is not configured to work on CMDaemon for the external LDAP server, then
the user management tool that is used with the external LDAP server should be used by the administrator to create the ldapcheck user instead.


  - If user management is still being done via CMDaemon, then an example session for configuring
the ldap script object to work with the new external LDAP user is (some prompt text elided):


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% user

[basecm11->user]% add ldapcheck; commit

[basecm11->user[ldapcheck]]% monitoring setup use ldap

[basecm11->monitoring->setup[ldap]]% show

Parameter Value

-------------------------------- ----------------------------------------
...

Arguments

...

[basecm11->monitoring->setup[ldap]]% set arguments "ldapcheck"; commit

[basecm11->monitoring->setup[ldap:ldapcheck]]%


**Disabling the** ldap **health check:** Instead of modifying the ldap health check to work when using an
external LDAP server, it can be disabled entirely via Base View or cmsh .


  - Base View: the ldap health check is disabled via the navigation path:


Monitoring   - Data Producers   - ldap   - Edit


**310** **User Management**


 - cmsh : the disabled parameter of the ldap health check object is set to yes . The disabled parameter
for the ldap health check can be set as follows:


[root@basecm11 ~]# cmsh -c "monitoring setup use ldap; set disabled yes; commit"


**Configuring The Cluster To Authenticate Against An External LDAP Server**
The cluster can be configured in different ways to authenticate against an external LDAP server.
For smaller clusters, a configuration where LDAP clients on all nodes point directly to the external
server is recommended. An easy way to set this up is as follows:


  - On the head node:


**–** In distributions that are derived from the RHEL 8. _x_ series: The files in which the changes need
to be made are /etc/nslcd.conf and /etc/openldap/ldap.conf . To implement the changes,
the nslcd daemon must then be restarted, for example with systemctl nslcd restart .
For the RHEL 9. _x_ series, /etc/nslcd.conf is replaced by /etc/sssd/sssd.conf, and it is the
sssd daemon that must be restarted, for example with: /bin/systemctl restart sssd .


**–** the updateprovisioners command (section 5.2.4) is run to update any other provisioners.


  - Then, the configuration files are updated in the software images that the nodes use. If the nodes
use the default-image, and if the nodes are based on RHEL8 and derivatives, then the files to update are /cm/images/default-image/etc/nslcd.conf and /cm/images/default/etc/openldap/

ldap.conf .


For RHEL9 and derivatives /cm/images/default-image/etc/sssd/sssd.conf is used instead
/cm/images/default-image/etc/nslcd.conf .


After the configuration change has been made, and the nodes have picked up the new configuration, the regular nodes can then carry out LDAP lookups.


**–**
Nodes can simply be rebooted to pick up the updated configuration, along with the new
software image.


**–**
Alternatively, to avoid a reboot, the imageupdate command (section 5.6.2) can be run to pick
up the new software image from a provisioner.


  - The CMDaemon configuration file cmd.conf (Appendix C) has LDAP user management directives. These may need to be adjusted:


**–**
If another LDAP tool is to be used for external LDAP user management instead of Base View
or cmsh, then altering cmd.conf is not required, and BCM’s user management capabilities do
nothing in any case.


**–** If, however, system users and groups are to be managed via Base View or cmsh, then CMDaemon, too, must refer to the external LDAP server instead of the default LDAP server. This
configuration change is actually rare, because the external LDAP database schema is usually
an existing schema generated outside of BCM, and so it is very unlikely to match BCM LDAP
database schema. To implement the changes:


       - [On the node that is to manage the database, which is normally the head node, the]
LDAPHost, LDAPUser, LDAPPass, and LDAPSearchDN directives in cmd.conf are changed
so that they refer to the external LDAP server.

       - [CMDaemon is restarted to enable the new configurations.]


For larger clusters the preceding solution can cause issues due to traffic, latency, security and connectivity fault tolerance. If such occur, a better solution is to replicate the external LDAP server onto the
head node, hence keeping all cluster authentication local, and making the presence of the external LDAP
server unnecessary except for updates. This optimization is described in the next section.


**6.3 Using An External LDAP Server** **311**


**6.3.1** **External LDAP Server Replication**
This section explains how to set up replication for an external LDAP server to an LDAP server that is
local to the cluster, if improved LDAP services are needed. Section 6.3.2 then explains how this can then
be made to work with a high availability setup.
Typically, the BCM LDAP server is configured as a replica (consumer) to the external LDAP server
(provider), with the consumer refreshing its local database at set timed intervals. How the configuration
is done varies according to the LDAP server used. The description in this section assumes the provider
and consumer both use OpenLDAP.


**External LDAP Server Replication: Configuring The Provider**
It is advisable to back up any configuration files before editing them.
The provider is assumed to be an external LDAP server, and not necessarily part of the BCM cluster.
The LDAP TCP ports 389 and 689 may therefore need to be made accessible between the consumer and
the provider by changing firewall settings.
If a provider LDAP server is already configured then the following synchronization directives must be
in the slapd.conf file to allow replication:


index entryCSN eq

index entryUUID eq

overlay syncprov

syncprov-checkpoint <ops> <minutes>

syncprov-sessionlog <size>


The openldap documentation ( [http://www.openldap.org/doc/](http://www.openldap.org/doc/) ) has more on the meanings of these
directives. If the values for < _ops_ >, < _minutes_ >, and < _size_ - are not already set, typical values are:


syncprov-checkpoint 1000 60


and:


syncprov-sessionlog 100


To allow the consumer to read the provider database, the consumer’s access rights need to be configured. In particular, the userPassword attribute must be accessible. LDAP servers are often configured
to prevent unauthorized users reading the userPassword attribute.
Read access to all attributes is available to users with replication privileges. So one way to allow the
consumer to read the provider database is to bind it to replication requests.
Sometimes a user for replication requests already exists on the provider, or the root account is used
for consumer access. If not, a user for replication access must be configured.
A replication user, syncuser with password secret can be added to the provider LDAP with adequate rights using the following syncuser.ldif file:


dn: cn=syncuser,<suffix>

objectClass: person

cn: syncuser

sn: syncuser

userPassword: secret


Here, < _suffix_ - is the suffix set in slapd.conf, which is originally something like dc=example,dc=com .
The syncuser is added using:


ldapadd -x -D "cn=root,<suffix>" -W -f syncuser.ldif


This prompts for the root password configured in slapd.conf .
To verify syncuser is in the LDAP database the output of ldapsearch can be checked:


ldapsearch -x "(sn=syncuser)"


**312** **User Management**


To allow access to the userPassword attribute for syncuser the following lines in slapd.conf are
changed, from:


access to attrs=userPassword

by self write

by anonymous auth

by * none


to:


access to attrs=userPassword

by self write

by dn="cn=syncuser,<suffix>" read

by anonymous auth

by * none


Provider configuration is now complete. The server can be restarted using


systemctl restart slapd.service


in RHEL8. _x_ and RHEL9. _x_ .


**External LDAP Server Replication: Configuring The Consumer(s)**
The consumer is an LDAP server on a BCM head node. It is configured to replicate with the provider
by adding the following lines to /cm/local/apps/openldap/etc/slapd.conf :


syncrepl rid=2
provider=ldap://external.ldap.server

type=refreshOnly

interval=01:00:00:00

searchbase=<suffix>

scope=sub

schemachecking=off

binddn="cn=syncuser,<suffix>"

bindmethod=simple

credentials=secret


Here:


  - The rid=2 value is chosen to avoid conflict with the rid=1 setting used during high availability
configuration (section 6.3.2).


  - The provider argument points to the external LDAP server.


  - The interval argument (format DD:HH:MM:SS) specifies the time interval before the consumer
refreshes the database from the external LDAP. Here, the database is updated once a day.


  - The credentials argument specifies the password chosen for the syncuser on the external LDAP

server.


More on the syncrepl directive can be found in the openldap documentation ( [http://www.openldap.](http://www.openldap.org/doc/)
[org/doc/](http://www.openldap.org/doc/) ).
The configuration files must also be edited so that:


  - The < _suffix_  - and rootdn settings in slapd.conf both use the correct < _suffix_  - value, as used by the
provider.


  - The base value in /etc/ldap.conf uses the correct < _suffix_  - value as used by the provider. This is
set on all BCM nodes including the head node(s). If the /etc/ldap.conf file does not exist, then
the note on page 310 applies.


**6.3 Using An External LDAP Server** **313**


Finally, before replication takes place, the consumer database is cleared. This can be done by removing all files, except for the DB_CONFIG file, from under the configured database directory, which by
default is at /var/lib/ldap/ .
The consumer is restarted using systemctl restart slapd . This replicates the provider’s LDAP
database, and continues to do so at the specified intervals.


**6.3.2** **High Availability**

**No External LDAP Server Case**

If the LDAP server is not external—that is, if BCM is set to its high availability configuration, with its
LDAP servers running internally, on its own head nodes—then by default LDAP services are provided
from both the active and the passive node. The high-availability setting ensures that CMDaemon takes
care of any changes needed in the slapd.conf file when a head node changes state from passive to
active or vice versa, and also ensures that the active head node propagates its LDAP database changes
to the passive node via a syncprov / syncrepl configuration in slapd.conf .


**External LDAP Server With No Replication Locally Case**
In the case of an external LDAP server being used, but with no local replication involved, no special
high-availability configuration is required. The LDAP client configuration in /etc/ldap.conf simply
remains the same for both active and passive head nodes, pointing to the external LDAP server. The
file /cm/images/default-image/etc/ldap.conf, in each software image also point to the same external
LDAP server. If the /etc/ldap.conf files referred to here in the head and software images do not exist,
then the note on page 310 applies.


**External LDAP Server With Replication Locally Case**
In the case of an external LDAP server being used, with the external LDAP provider being replicated to
the high-availability cluster, it is generally more efficient for the passive node to have its LDAP database
propagated and updated only from the active node to the passive node, and not updated from the
external LDAP server.

The configuration should therefore be:


  - an active head node that updates its consumer LDAP database from the external provider LDAP

server


  - a passive head node that updates its LDAP database from the active head node’s LDAP database


Although the final configuration is the same, the sequence in which LDAP replication configuration
and high availability configuration are done has implications on what configuration files need to be
adjusted.


1. For LDAP replication configuration done after high availability configuration, adjusting the new
suffix in /cm/local/apps/openldap/etc/slapd.conf and in /etc/ldap.conf on the passive node
to the local cluster suffix suffices as a configuration. If the ldap.conf file does not exist, then the
note on page 310 applies.


2. For high availability configuration done after LDAP replication configuration, the initial LDAP
configurations and database are propagated to the passive node. To set replication to the passive
node from the active node, and not to the passive node from an external server, the provider option
in the syncrepl directive on the passive node must be changed to point to the active node, and the
suffix in /cm/local/apps/openldap/etc/slapd.conf on the passive node must be set identical to
the head node.


The high availability replication event occurs once only for configuration and database files in BCM’s
high availability system. Configuration changes made on the passive node after the event are therefore
persistent.


**314** **User Management**


**6.4** **Tokens And Profiles**


Access to Base View and cmsh is based on user certificates (section 2.3.3).
_Tokens_ can be assigned by the administrator to users so that users can carry out some of the operations
that the administrator does with Base View or cmsh . Every cluster management operation requires that
each user, including the administrator, has the relevant tokens in their _profile_ for the operation.
The tokens for a user are grouped into a profile, and such a profile is typically given a name
by the administrator according to the assigned capabilities. For example the profile might be called
readmonitoringonly if it allows the user to read the monitoring data only, or it may be called
powerhandler if the user is only allowed to carry out power operations. Each profile thus consists
of a set of tokens, typically relevant to the name of the profile, and is typically assigned to several users.
The profile is stored as part of the authentication certificate (section 2.3) which is generated for running authentication operations to the cluster manager for the certificate owner.
Profiles are handled with the profiles mode of cmsh, or from the Base View Profiles window,
accessible via a navigation path of Identity Management - Profiles
The following preconfigured profiles are available from cmsh :


**Profile name** **Default Tasks Allowed** nonuser **?**


admin all tasks no


autonomous-hardware-recovery autonomous hardware recovery tasks yes


autonomous-job-recovery autonomous job recovery tasks yes


bootstrap bootstrap tasks yes


cmhealth health-related prejob tasks yes


cmpam BCM PAM tasks yes


litenode CMDaemon Lite (section 2.6.7) tasks yes


monitoringpush pushing raw monitoring data to CMDaemon via yes
a JSON POST (page 67 of the _Developer Manual_ )


mqtt MQTT tasks yes


node node-related tasks, for example by the node- yes
installer


portal user portal viewing no


power device power yes


prs PRS tasks yes


readonly view-only no


The last column in the preceding table indicates whether the preconfigured profile is a nonuser
profile or not. A cmsh one-liner that indicates this is:


[root@basecm11 ~]# cmsh -c "profile; foreach * (get name; get nonuser)" | paste - 

  - Most of the preconfigured profiles are nonuser profiles. Such a profile is used by cluster manager
clients, and should never be modified by the cluster administrator.


  - The preconfigured profiles that are not nonuser profiles are admin, readonly, and portal . These
can be modified by the cluster administrator and used for human users.


The cluster manager services that use the available preconfigured profiles can be viewed in cmsh the
list command in profile mode.
The tokens, and other properties of a particular profile can be seen within profile mode as follows:


**Example**


**6.4 Tokens And Profiles** **315**


[basecm11->profile]% show readonly

Parameter Value

------------ ---------------------------------------------------------------------------------
Name readonly

Non user no

Revision

Services CMDevice CMNet CMPart CMMon CMJob CMAuth CMServ CMUser CMSession CMMain CMGui CMP+

Tokens GET_DEVICE_TOKEN GET_CATEGORY_TOKEN GET_NODEGROUP_TOKEN POWER_STATUS_TOKEN GET_DE+


For screens that are not wide enough to view the parameter values, the values can also be listed:


**Example**


[basecm11->profile]% get readonly tokens

GET_DEVICE_TOKEN

GET_CATEGORY_TOKEN

GET_NODEGROUP_TOKEN

...


A profile can be set with cmsh for a user within user mode as follows:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% user use conner

[basecm11->user[conner]]% get profile


[basecm11->user[conner]]% set profile readonly; commit


Only a subset of the predefined profiles are available to users. The ones that are made available to users
are readonly, admin, and portal .


**6.4.1** **Modifying Profiles**
A profile can be modified by adding or removing appropriate tokens to it. For example, the readonly
group by default has access to the burn status and burn log results. Removing the appropriate tokens
stops users in that group from seeing these results.
In cmsh the removal can be done from within profile mode as follows:


[root@basecm11 ~]# cmsh

[basecm11]% profile use readonly

[...[readonly]]% removefrom tokens burn_status_token get_burn_log_token

[basecm11]%->profile*[readonly*]]% commit


Tab-completion after typing in removefrom tokens helps in filling in the tokens that can be removed.
In Base View (figure 6.3), the same removal action can be carried out via the navigation path:
Identity Management - Profiles - readonly - Edit - Tokens


In the resulting display it is convenient to maximize the window. Also convenient is running a search
for burn, which will show the relevant tokens:

BURN_STATUS_TOKEN and GET_BURN_LOG_TOKEN
as well as the subgroup they are in, which is the device subgroup.
The ticks can be removed from the BURN_STATUS_TOKEN and GET_BURN_LOG_TOKEN checkboxes, and
the changed settings can then be saved.


**316** **User Management**


Figure 6.3: Base View Profile Token Management


**6.4.2** **Creation Of Custom Certificates With Profiles, For Users Managed By BCM’s Internal**
**LDAP**

Custom profiles can be created to include a custom collection of capabilities in cmsh and Base View.
Cloning of profiles is also possible from cmsh .
A certificate file, with an associated expiry date, can be created based on a profile. The time of expiry
for a certificate cannot be extended after creation. An entirely new certificate is required after expiry of
the old one.

The creation of custom certificates using cmsh (page 318) or Base View (page 319) is described later on.
After creating such a certificate, the openssl utility can be used to examine its structure and properties.
In the following example most of the output has been elided in order to highlight the expiry date (30
days from the time of generation), the common name ( democert ), the key size ( 2048 ), profile properties
( readonly ), and system login name ( peter ), for such a certificate:


[root@basecm11]# openssl x509 -in peterfile.pem -text -noout

Data:

...

Not After : Sep 21 13:18:27 2014 GMT

Subject: ... CN=democert
Public-Key: (2048 bit)

...

X509v3 extensions:

1.3.6.1.4.4324.1:

..readonly

1.3.6.1.4.4324.2:

..peter

[root@basecm11]#


However, using the openssl utility for managing certificates is rather inconvenient. BCM provides
more convenient ways to do so, as described next.


**Listing Certificates**
All certificates that have been generated by the cluster are noted by CMDaemon.


**6.4 Tokens And Profiles** **317**


**Listing certificates with** cmsh **:** Within the cert mode of cmsh, the listcertificates command lists
all cluster certificates and their properties:


[root@basecm11 ~]# cmsh

[basecm11]% cert

[basecm11-> cert]% listcertificates

Serial Revoked Time left Profile System log in Name

------ -------- ------------ ---------------- ---------------- -----------------------------
1 No 5214w 1d admin root Administrator

2 No 5214w 1d cmhealth CMHealth

3 No 5214w 1d cmhealth CMHealth

4 No 5214w 1d power Slurm

5 No 5214w 1d bootstrap CertificateRequest

6 No 5214w 1d cmpam CMPam

7 No 5214w 1d portal WebPortal

...


**Listing certificates with Base View:** The Base View equivalent for listing certificates is via the navigation path Identity Management - Certificates (figure 6.4):


Figure 6.4: Base View Certificates List Window


**Node Certificates**
In the certificates list, node certificates that are generated by the node-installer (section 5.4.1) for each
node for CMDaemon use are listed. These are entries that look like:


[basecm11-> cert]% listcertificates

Serial Revoked Time left Profile System log in Name

------ -------- ------------ ---------------- ---------------- -----------------------------
...

10 No 5214w 1d node fa-16-3e-74-24-dc

11 No 5214w 1d node fa-16-3e-57-2c-8e

12 No 5214w 1d node fa-16-3e-b6-c7-4a


**318** **User Management**


13 No 5214w 1d node fa-16-3e-bd-cd-05

14 No 5214w 1d node fa-16-3e-0d-ab-ea

...


**Creating A Custom Certificate**
Custom certificates are also listed in the certificates list.
Unlike node certificates, which are normally system-generated, custom certificates are typically generated by a user with the appropriate tokens in their profile, such as root with the admin profile. Such a
user can create a certificate containing a specified profile, as discussed in the next section, by using:


 - cmsh : with the createcertificate operation from within cert mode


  - Base View: via the navigation path Identity Management  - Users  - Edit  - Profile to set the

Profile .


**Creating a new certificate for** cmsh **users:** Creating a new certificate in cmsh is done from cert mode
using the createcertificate command, which has the following help text:


[basecm11->cert]% help createcertificate

Name:

createcertificate - Create a new certificate


Usage:
createcertificate <key-length> <common-name> <organization> <organizational-unit> <loca _\_

lity> <state> <country> <profile> <sys-login> <days> <key-file> <cert-file>


Arguments:

key-file

Path to key file that will be generated


cert-file

Path to pem file that will be generated


Accordingly, as an example, a certificate file with a read-only profile set to expire in 30 days, to be
run with the privileges of user peter, can be created with:


**Example**


[basecm11->cert]% createcertificate 2048 democert a b c d ef readonly peter 30 /home/peter _\_
/peterfile.key /home/peter/peterfile.pem


Thu Jan 5 15:13:01 2023 [notice] basecm11: New certificate request with ID: 16

[basecm11->cert]% createcertificate 2048 democert a b c d ef readonly peter 30 /home/peter _\_
/peterfile.key /home/peter/peterfile.pem
Certificate key written to file: /home/peter/peterfile.key
Certificate pem written to file: /home/peter/peterfile.pem


The certificate list would show it as something like:


[basecm11-> cert]% listcertificates

Serial Revoked Time left Profile System log in Name

------ -------- ------------ ---------------- ---------------- -----------------------------
...

23 No 4w 1d readonly peter democert


**6.4 Tokens And Profiles** **319**


**Setting the ownership of the new custom certificate:** The certificates are owned by the owner generating them, so they are root-owned if root was running cmsh . This means that user peter cannot use
them until their ownership is changed to user peter :


**Example**


[root@basecm11 ~]# cd /home/peter

[root@basecm11 peter]# ls -l peterfile.*

-rw------- 1 root root 1704 Aug 22 06:18 peterfile.key

-rw------- 1 root root 1107 Aug 22 06:18 peterfile.pem

[root@basecm11 peter]# chown peter:peter peterfile.*


Other users must have the certificate ownership changed to their own user names.


**Associating users with paths to the new custom certificate:** Users associated with such a certificate
can then carry out cmdaemon tasks that have a read-only profile, and CMDaemon sees such users as
being user peter . Two ways of being associated with the certificate are:


1. The paths to the pem and key files can be set with the -i and -k options respectively of cmsh . For
example, in the home directory of peter, for the files generated in the preceding session, cmsh can
be launched with these keys with:


[peter@basecm11 ~] cmsh -i peterfile.pem -k peterfile.key

[basecm11]% quit


2. If the -i and -k options are not used, then cmsh searches for default keys. The default keys for
cmsh are under these paths under $HOME, in the following order of priority:


(a) .cm/admin.{pem,key}


(b) .cm/cert.{pem,key}


**Creating a custom certificate for Base View users:** As in the case of cmsh, a Base View user having a
sufficiently privileged tokens profile, such as the admin profile, can create a certificate and key file for
themselves or another user. This is done by associating a value for the Profile from the Add or Edit
dialog for the user (figure 6.2).
The certificate files, cert.pem and cert.key, are then automatically placed in the following paths
and names, under $HOME for the user:


 - .cm/admin.{pem,key}


 - .cm/cert.{pem,key}


Users that authenticate with their user name and password when running Base View use this certificate for their Base View clients, and are then restricted to the set of tasks allowed by their associated
profile.


**6.4.3** **Creation Of Custom Certificates With Profiles, For Users Managed By An External**
**LDAP**

The use of an external LDAP server instead of BCM’s for user management is described in section 6.3.
Generating a certificate for an external LDAP user must be done explicitly in BCM. This can be carried
out with the external-user-cert script, which is provided with the cluster-tools package. The
package is installed by default with BCM.
Running the external-user-cert script embeds the user and profile in the certificate during certificate generation. The script has the following usage:


**320** **User Management**


external-user-cert -h

Usage: for a single profile: external-user-cert <profile> <user> [<user> ... ]
--home=<home-prefix> [-g <group>] [-o]

for several profiles: external-user-cert --home=<home-prefix>
--file=<inputfile> [-g <group>]

where lines of <inputfile> have the syntax
<profile> <user> [<user> ... ]


Options:

-h, --help show this help message and exit

--file=FILE input FILE
--home=HOME_PATH path for home directories, default /home/

-g GROUP name of primary group, e.g. wheel

-o overwrite existing certificates


Here,


 - <profile> should be a valid profile


 - <user> should be an existing user


 - <home-prefix> is usually /home


 - <group> is a group, such as wheel


 - <inputfile> is a file with each line having the syntax


<profile> <user> [<user> ... ]


One or more external LDAP user certificates can be created by the script. The certificate files generated
are cert.pem and cert.key . They are stored in the home directory of the user.
For example, a user spongebob that is managed on the external server, can have a read-only certificate
generated with: