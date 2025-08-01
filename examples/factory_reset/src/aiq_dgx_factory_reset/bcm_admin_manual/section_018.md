# MENU HIDE

MENU DEFAULT


**708** **Day-to-day Administration**


The bios/menu.conf file may contain multiple entries corresponding to several DOS images to allow
for flashing of multiple BIOS versions or configurations.


**Firmware Configuration And Updates Via CMDaemon**
For systems that support the Redfish protocol, such as HPE iLO5 and DGX H100, firmware management
requires setting firmwaremanagemode, within a bmcsettings submode.
In addition, for DGX hardware, after the firmware has been flashed over to it, an activation based
on an AC power cycle is required. Details on this are given (page 714) as part of the DGX installation
example later on (page 710).


**Setting** firmwaremanagemode **:** The value of firmwaremanagemode is selected appropriately by the administrator according to the node hardware:


**Example**


[basecm11->device*[node001*]->bmcsettings*]% set firmwaremanagemode < _TAB_ >< _TAB_ 
auto b200 gb200 gb200sw h100 ilo none


The bmcsettings submode can be accessed and set within an instance of the device, category, or
partition modes.


**Running** firmware **operations and options:** After firmwaremanagemode has been set, the firmware
command can be run under the device mode of cmsh to carry out Redfish protocol updates. Firmware
updated via Redfish need not be just the PC main system BIOS, but can also be the flashable software of
subsystems, for example: NICs.
The help firmware command provides a help page covering the operations and options for the
firmware command. Some of them are described next:


  - The firmware command includes the following operations:


**–** info : provides information on the firmwares available on the head node, available for uploading to nodes. By default these are files that the cluster administrator has picked up from
the vendor and has placed under /cm/local/apps/cmd/etc/htdocs/bios/firmware/ .


**–** list : (only for iLO) provides a list of firmware states on specified nodes.


**–** upload : (only for iLO) takes a specified firmware from the files listed by the info option, and
copies it over to the specified nodes. For an HPE iLO system, the upload is carried out to a
special flash storage, only visible to the BIOS and Redfish queries. After it is in that special
flash location, it can be flashed to where the firmware is actually run.


**–** remove : (only for iLO) removes a specified firmware from the special flash storage of specified
nodes


**–** flash : carries out the flashing of the firmware from the flash storage to the location where
the firmware runs, for the specified nodes


**–** status : shows the status of the flash operation. A table is displayed with rows listing the
component, version, and state, among other items. The State column of the output can show
the following values:


        - [pending] [: the flash operation is pending]


        - [exception] [: the flash operation failed during execution]


        - [flashing] [: the flash operation is being executed]


        - [completed] [: the flash operation succeeded]


        - [current] [: the firmware of the listed component with the listed version is activated]


**14.5 BIOS And Firmware Management** **709**


  - The firmware command also includes the following options:


**–** --targets : (only for DGX hosts) specifies names for particular component firmware targets.
Without this option, the default is that updates are carried out automatically only for newer
firmware components from the firmware package files. Overriding the default should not be
needed, and is typically not recommended. Specifying --targets list -v lists the possible
components.


**–** --force : (only for DGX hosts) needed to carry out a downgrade, and also needed
for some other DGX firmware cases as described in [https://docs.nvidia.com/dgx/](https://docs.nvidia.com/dgx/dgxh100-fw-update-guide/sequence.html#update-steps)
[dgxh100-fw-update-guide/sequence.html#update-steps](https://docs.nvidia.com/dgx/dgxh100-fw-update-guide/sequence.html#update-steps)


**–**
--dry-run : (only for DGX hosts) pretends to carry out an installation, so that the administrator can get an idea of what components are affected from the output of the mock installation

run


**An HP iLO5 firmware upgrade example:** The following session shows node001 getting uploaded and
flashed with a firmware, and then having the firmware removed.


**Example**


[basecm11->device]% firmware info

Device Filename Component Version State Progress Result Size Date

-------- ------------ ---------------- -------- ---------- -------- -------- -------- --------------------
basecm11 iLO5-2.42 iLO5 2.42 undefined N/A 8.6MiB 02/28/2022, 11:22:55

basecm11 iLO5-2.43 iLO5 2.43 undefined N/A 8.7MiB 02/28/2022, 11:22:55

basecm11 iLO5-2.44 iLO5 2.44 undefined N/A 8.8MiB 02/28/2022, 11:22:55

basecm11 iLO5-2.45 iLO5 2.45 undefined N/A 8.9MiB 02/28/2022, 11:22:55


[basecm11->device]% firmware list -n node001


[basecm11->device]% firmware upload iLO5-2.42 -n node001

Device Result Output Error

-------- -------- ---------------------- -------------------------------
node001 good uploading: iLO5-2.42


[basecm11->device]% firmware list -n node001

Device Filename Component Version State Progress Result Size Date

-------- ------------ ---------------- -------- ---------- -------- -------- -------- --------------------
node001 iLO5-2.42 iLO5 2.42 completed N/A 8.6MiB 02/28/2022, 11:23:31


[basecm11->device]% firmware flash iLO5-2.42 -n node001

Device Result Output Error

-------- -------- ---------------------- -------------------------------
node001 good flashing: iLO5-2.42


[basecm11->device]% firmware status -n node001

Device Filename Component Version State Progress Result Size Date

-------- ------------ ---------------- -------- --------- -------- -------- -------- --------------------
node001 iLO5 2.42 flashing 35.6% N/A 02/28/2022, 11:27:27


[basecm11->device]% firmware status -n node001

Device Filename Component Version State Progress Result Size Date

-------- ------------ ---------------- -------- ---------- -------- -------- -------- --------------------
node001 iLO5 2.42 completed N/A N/A 02/28/2022, 11:27:27


[basecm11->device]% firmware remove iLO5-2.42 -n node001


**710** **Day-to-day Administration**


Device Result Output Error

-------- -------- ---------------------- -------------------------------
node001 good removed: iLO5-2.42


[basecm11->device]% firmware list -n node001


**A GPU tray upgrade example on the DGX H100:**


**Obtaining and placing the firmware packages on the cluster:** Firmware for the DGX H100 is available for the motherboard tray (chassis) components, and for the GPU tray components.
Firmware packages for the DGX H100 can be obtained via the DGX support portal, which can be
reached from:

[https://docs.nvidia.com/dgx/dgxh100-fw-update-guide/about.html#firmware-update-prerequisites](https://docs.nvidia.com/dgx/dgxh100-fw-update-guide/about.html#firmware-update-prerequisites) .
The packages are available as .fwpkg packages. They should be placed in the head node directory at
/cm/local/apps/cmd/etc/htdocs/bios/firmware/
under the appropriate existing subdirectory for the platform type:


**Example**


[basecm11 ~]# ls -l /cm/local/apps/cmd/etc/htdocs/bios/firmware/h100

-rw-r--r-- 1 root root 135723563 Dec 12 14:27 nvfw_DGX-H100_0003_230817.1.1_custom_prod-signed.fwpkg

-rw-r--r-- 1 root root 135723563 Dec 12 14:27 nvfw_DGX-H100_0003_230905.1.0_custom_prod-signed.fwpkg

-rw-r--r-- 1 root root 135723563 Dec 12 14:27 nvfw_DGX-H100_0003_230920.1.0_custom_prod-signed.fwpkg

-rw-r--r-- 1 root root 106091440 Dec 12 14:27 nvfw_DGX-HGX-H100x8_0002_230705.1.1_prod-signed.fwpkg


**Configuring BMC settings in BCM:** The BMC interface and settings should be configured for the
DGX H100. Typically this requires:


  - adding a BMC network (section 3.2.2)


  - configuring its BMC settings (section 3.7.2) to be able to carry out the Redfish protocol. This means
setting the:


**–** username


**–** userid


**–**
password


**–**
firmware mode for Redfish


  - adding an interface to the network for the node (section 3.7.1).


**Example**


[basecm11 ~]# cmsh

[basecm11]% network

[basecm11->network]% add bmcnet

[basecm11->network*[bmcnet*]]% set baseaddress 10.148.0.0

[basecm11->network*[bmcnet*]]% set domainname bmc.cluster

[basecm11->network*[bmcnet*]]% commit

[basecm11->network[bmcnet]]% partition

[basecm11->partition[base]]% bmcsettings

[basecm11->partition[base]->bmcsettings]% set username admin

[basecm11->partition*[base*]->bmcsettings*]% set userid 0

[basecm11->partition*[base*]->bmcsettings*]% set password < _password_ 

**14.5 BIOS And Firmware Management** **711**


[basecm11->partition*[base*]->bmcsettings*]% set firmwaremanagemode < _TAB_ >< _TAB_ 
auto b200 gb200 gb200sw h100 ilo none

[basecm11->partition*[base*]->bmcsettings*]% set firmwaremanagemode h100

[basecm11->partition*[base*]->bmcsettings*]% commit

[basecm11->partition[base]->bmcsettings]% device

[basecm11->device]% interfaces node001

[basecm11->device[node001]->interfaces]% add bmc

[basecm11->device[node001]->interfaces]% add bmc ipmi0

[basecm11->device*[node001*]->interfaces*[ipmi0*]]% set network bmcnet

[basecm11->device*[node001*]->interfaces*[ipmi0*]]% set ip 10.148.0.1


**Managing, installing and updating the firmware package in BCM:** BCM can then display information about the files in that head node firmware directory with the firmware info command:


**Example**


[basecm11->device]% firmware info

Device Filename Component Version State Progress ...

-------- ---------------------------- ----------------- ------------------- ---------- -------
basecm11 nvfw_DGX-H100_...fwpkg DGX-H100-Chassis DGX-H100_0003_2... available N/A
basecm11 nvfw_DGX-H100_...fwpkg DGX-H100-Chassis DGX-H100_0003_2... available N/A
basecm11 nvfw_DGX-HGX-H100x8_...fwpkg DGX-H100-GPU DGX-HGX-H100x8_... available N/A


The firmware status command displays information on the state of the firmware components running on the node:


**Example**


[basecm11->device]% firmware status -n node001

Device Filename Component Version State Progress Result Size Date

------- -------- ------------------------- -------------------- ------- --------- ------ ---- ---
node001 CPLDMB_0 0.2.1.0 current N/A N/A

node001 CPLDMID_0 0.2.1.0 current N/A N/A

node001 EROT_BIOS_0 00.04.0020.0000_n00 current N/A N/A

node001 EROT_BMC_0 00.04.0020.0000_n00 current N/A N/A

node001 HGX_FW_BMC_0 HGX-22.10-1-rc1 current N/A N/A

node001 HGX_FW_ERoT_BMC_0 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_ERoT_FPGA_0 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_ERoT_NVSwitch_0 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_ERoT_NVSwitch_1 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_ERoT_NVSwitch_2 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_ERoT_NVSwitch_3 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_ERoT_PCIeSwitch_0 00.02.0100.0000_n00 current N/A N/A

node001 HGX_FW_FPGA_0 2.0A current N/A N/A

node001 HGX_FW_GPU_SXM_1 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_2 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_3 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_4 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_5 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_6 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_7 96.00.70.00.01 current N/A N/A

node001 HGX_FW_GPU_SXM_8 96.00.70.00.01 current N/A N/A

node001 HGX_FW_NVSwitch_0 96.00.3F.00.01 current N/A N/A

node001 HGX_FW_NVSwitch_1 96.00.3F.00.01 current N/A N/A

node001 HGX_FW_NVSwitch_2 96.00.3F.00.01 current N/A N/A

node001 HGX_FW_NVSwitch_3 96.00.3F.00.01 current N/A N/A


**712** **Day-to-day Administration**


node001 HGX_FW_PCIeRetimer_0 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_1 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_2 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_3 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_4 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_5 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_6 2.7.0 current N/A N/A

node001 HGX_FW_PCIeRetimer_7 2.7.0 current N/A N/A

node001 HGX_FW_PCIeSwitch_0 1.7.5A current N/A N/A

node001 HostBIOS_0 01.00.00 current N/A N/A

node001 HostBMC_0 23.00.00 current N/A N/A

node001 PCIeRetimer_0 1.30.0 current N/A N/A

node001 PCIeRetimer_1 1.30.0 current N/A N/A

node001 PCIeSwitch_0 0.0.1 current N/A N/A

node001 PCIeSwitch_1 1.0.1 current N/A N/A

node001 PSU_0 0202.0200.0200 current N/A N/A

node001 PSU_1 0202.0200.0200 current N/A N/A

node001 PSU_2 0202.0200.0200 current N/A N/A

node001 PSU_3 0202.0201.0202 current N/A N/A

node001 PSU_4 0202.0201.0203 current N/A N/A

node001 PSU_5 0202.0200.0200 current N/A N/A


Components can be updated by installing associated firmware packages with the firmware flash
command. For example, the GPU tray firmware can be installed with one of the nvfw_dgx-hgx-h100x8*
packages:


**Example**


[basecm11->device[node001]]% firmware flash < _TAB_ >< _TAB_ 
nvfw_dgx-h100_0003_230817.1.1.fwpkg

nvfw_dgx-h100_0003_230920.1.0.fwpkg

nvfw_dgx-hgx-h100x8_0002_230705.1.1.fwpkg

[basecm11->device[node001]]% firmware flash nvfw_dgx-hgx-h100x8_0002_230705.1.1.fwpkg

Device flashing Result Error

---------------- ------------------------------------------ -------- ---------
node001 nvfw_DGX-HGX-H100x8_0002_230705.1.1.fwpkg good


The firmware status command then shows the installation progress for the GPU tray components
during flashing:


**Example**


[basecm11->device]% firmware -n node001 status

Device Filename Component Version State Progress...

------- -------------------- ------------------------- -------------------- --------- -------
node001 CPLDMB_0 0.2.1.0 current N/A

node001 CPLDMID_0 0.2.1.0 current N/A

node001 EROT_BIOS_0 00.04.0020.0000_n00 current N/A

node001 EROT_BMC_0 00.04.0020.0000_n00 current N/A

node001 HostBIOS_0 01.00.00 current N/A

node001 HostBMC_0 23.00.00 current N/A

node001 PCIeRetimer_0 1.30.0 current N/A

node001 PCIeRetimer_1 1.30.0 current N/A

node001 PCIeSwitch_0 0.0.1 current N/A

node001 PCIeSwitch_1 1.0.1 current N/A

node001 PSU_0 0202.0200.0200 current N/A


**14.5 BIOS And Firmware Management** **713**


node001 PSU_1 0202.0200.0200 current N/A

node001 PSU_2 0202.0200.0200 current N/A

node001 PSU_3 0202.0201.0202 current N/A

node001 PSU_4 0202.0201.0203 current N/A

node001 PSU_5 0202.0200.0200 current N/A

node001 nvfw_DGX-HG...fwpkg HGX_FW_BMC_0 HGX-22.10-1-rc1 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_BMC_0 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_FPGA_0 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_NVSwitch_0 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_NVSwitch_1 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_NVSwitch_2 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_NVSwitch_3 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_ERoT_PCIeSwitch_0 00.02.0100.0000_n00 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_FPGA_0 2.0A flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_1 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_2 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_3 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_4 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_5 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_6 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_7 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_GPU_SXM_8 96.00.70.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_NVSwitch_0 96.00.3F.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_NVSwitch_1 96.00.3F.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_NVSwitch_2 96.00.3F.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_NVSwitch_3 96.00.3F.00.01 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_0 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_1 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_2 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_3 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_4 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_5 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_6 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeRetimer_7 2.7.0 flashing 39.1%
node001 nvfw_DGX-HG...fwpkg HGX_FW_PCIeSwitch_0 1.7.5A flashing 39.1%


The non-GPU-related firmware components are not updated.
If the firmware flash command stage has completed its run, then when the firmware status command is run, the Component and Version columns show output indicating that the firmware version
is transitioning. The rows that have to do with the GPU firmware status are the rows with the string
nvfw_DGX-HG in the Filename column. Those GPU firmware rows have Component and Version column
entries such as:


**Example**


[basecm11->device[node001]]% firmware status| head -2| cut -b66-133; firmware status| grep nvfw| cut -b66-133

Component Version

------------------------- -----------------------------------------
HGX_FW_BMC_0 HGX-22.10-1-rc1 -> HGX-22.10-1-rc44

HGX_FW_ERoT_BMC_0 00.02.0100.0000_n00 -> 00.02.0134.0000_n00

HGX_FW_ERoT_FPGA_0 00.02.0100.0000_n00 -> 00.02.0134.0000_n00

HGX_FW_ERoT_NVSwitch_0 00.02.0100.0000_n00 -> 00.02.0134.0000_n00

HGX_FW_ERoT_NVSwitch_1 00.02.0100.0000_n00 -> 00.02.0134.0000_n00

HGX_FW_ERoT_NVSwitch_2 00.02.0100.0000_n00 -> 00.02.0134.0000_n00

HGX_FW_ERoT_NVSwitch_3 00.02.0100.0000_n00 -> 00.02.0134.0000_n00

HGX_FW_ERoT_PCIeSwitch_0 00.02.0100.0000_n00 -> 00.02.0134.0000_n00


**714** **Day-to-day Administration**


HGX_FW_FPGA_0 2.0A -> 2.2C

HGX_FW_GPU_SXM_1 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_2 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_3 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_4 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_5 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_6 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_7 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_GPU_SXM_8 96.00.70.00.01 -> 96.00.74.00.01

HGX_FW_NVSwitch_0 96.00.3F.00.01 -> 96.10.3F.00.01

HGX_FW_NVSwitch_1 96.00.3F.00.01 -> 96.10.3F.00.01

HGX_FW_NVSwitch_2 96.00.3F.00.01 -> 96.10.3F.00.01

HGX_FW_NVSwitch_3 96.00.3F.00.01 -> 96.10.3F.00.01

HGX_FW_PCIeRetimer_0 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_1 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_2 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_3 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_4 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_5 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_6 2.7.0 -> 2.7.9

HGX_FW_PCIeRetimer_7 2.7.0 -> 2.7.9

HGX_FW_PCIeSwitch_0 1.7.5A -> 1.7.5F


In the preceding, the grep command is to select just the GPU-related rows, and the cut commands
are used to remove some columns, to make the output clearer to the reader.
The firmware status GPU firmware rows also have the following output columns:


  - the State column, which shows Pending if there are activation steps still required to complete the
firmware update


  - the Result column, which suggests the recommended action to take to activate the firmware


**Example**


[basecm11->device[node001]]% firmware status #other rows and columns omitted for readability

State Progress Result Size Date

-------- -------- ------------------------------------ -------- -------
pending N/A success: AC power cycle to activate 1.22KiB
pending N/A success: AC power cycle to activate 1.22KiB
pending N/A success: AC power cycle to activate 1.22KiB

...


**AC and DC power cycling:** As suggested in the Result column in the preceding example, an AC
power cycle must then be carried out on the node to activate the GPU firmware with the new versions.
The AC power cycle tag is a part of Redfish terminology, and it implies that all the AC power inputs
need to be cut off. This can be carried out via a PDU powering off the entire system, or it can be done
physically, by hand, by pulling out all the mains (AC) power leads to the system.
A regular power reset command run from the device mode of cmsh, which is a board level (DC)
power cycle by default, is not enough to initialize some of the components for the DGX H100.
Details on firmware activation for the DGX H100 can be found at [https://docs.nvidia.com/dgx/](https://docs.nvidia.com/dgx/dgxh100-fw-update-guide/about.html#firmware-update-activation)
[dgxh100-fw-update-guide/about.html#firmware-update-activation](https://docs.nvidia.com/dgx/dgxh100-fw-update-guide/about.html#firmware-update-activation) .


**Successful activation and completed state confirmations:** After the power cycle, the output from
firmware status indicates that the firmware now active on the node matches that of the .fwpkg file
version.


**14.5 BIOS And Firmware Management** **715**


It does this by displaying a value of

success: activated

in the Result column.

The output also now shows the new version value for the firmware component in the Version column, and indicates the firmware transition is now over with a value of completed in the State column:


[basecm11->device]% firmware -n node001 status

Device Filename Component Version State Progress Result

-------- -------------- ------------------------- -------------------------------- -------- ------------------
node001 CPLDMB_0 0.2.1.0 current N/A

node001 CPLDMID_0 0.2.1.0 current N/A

node001 EROT_BIOS_0 00.04.0020.0000_n00 current N/A

node001 EROT_BMC_0 00.04.0020.0000_n00 current N/A

node001 HostBIOS_0 01.00.00 current N/A

node001 HostBMC_0 23.00.00 current N/A

node001 PCIeRetimer_0 1.30.0 current N/A

node001 PCIeRetimer_1 1.30.0 current N/A

node001 PCIeSwitch_0 0.0.1 current N/A

node001 PCIeSwitch_1 1.0.1 current N/A

node001 PSU_0 0202.0200.0200 current N/A

node001 PSU_1 0202.0200.0200 current N/A

node001 PSU_2 0202.0200.0200 current N/A

node001 PSU_3 0202.0201.0202 current N/A

node001 PSU_4 0202.0201.0203 current N/A

node001 PSU_5 0202.0200.0200 current N/A

node001 nvfw_...fwpkg HGX_FW_BMC_0 HGX-22.10-1-rc44 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_BMC_0 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_FPGA_0 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_NVSwitch_0 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_NVSwitch_1 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_NVSwitch_2 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_NVSwitch_3 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_ERoT_PCIeSwitch_0 00.02.0134.0000_n00 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_FPGA_0 2.2C completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_1 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_2 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_3 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_4 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_5 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_6 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_7 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_GPU_SXM_8 96.00.74.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_NVSwitch_0 96.10.3F.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_NVSwitch_1 96.10.3F.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_NVSwitch_2 96.10.3F.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_NVSwitch_3 96.10.3F.00.01 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_0 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_1 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_2 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_3 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_4 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_5 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_6 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeRetimer_7 2.7.9 completed N/A success: activated
node001 nvfw_...fwpkg HGX_FW_PCIeSwitch_0 1.7.5F completed N/A success: activated


**716** **Day-to-day Administration**


**14.6** **Hardware Match Check With The** hardware-profile **Data Producer**


Often a large number of identical nodes may be added to a cluster. In such a case it is a good practice to
check that the hardware matches what is expected. This can be done easily as follows:


1. The new nodes, say node129 to node255, are committed to a newly-created category newbunch as
follows (output truncated):


[root@basecm11 ~]# cmsh -c "category add newbunch; commit"

[root@basecm11 ~]# for i in {129..255}

   - do

   - cmsh -c "device; set node00$i category newbunch; commit"

   - done

Successfully committed 1 Devices

Successfully committed 1 Devices


The preceding loop is easy to construct, and works, but it is quite slow for larger clusters, due to
the time wasted in opening up cmsh and carrying out a commit command during each iteration of
the for loop.


For larger clusters the offending for loop can be replaced with a more elegant, but slightly trickier:


(echo device;

for i in {129..255}; do

echo "set node00$i category newbunch"

done

echo "commit") | cmsh


2. The hardware profile of one of the new nodes, say node129, is saved into the category newbunch .
This is done using the node-hardware-profile health check script:


**Example**


[root@basecm11 ~]# /cm/local/apps/cmd/scripts/healthchecks/node-hardware-profile -n node129 -s newbunch


The profile is intended to be the reference hardware against which all the other nodes should
match, and is saved under the directory /cm/shared/apps/cmd/hardware-profiles/, and further
under the directory name specified by the -s option, which in this case is newbunch .


3. The hardware-profile data producer (section 10.2.10) can then be enabled, and the sampling
frequency set as follows:


[root@basecm11 ~]# cmsh

[basecm11]% monitoring setup use hardware-profile

[basecm11->monitoring->setup[hardware-profile]]% set interval 600; set disabled no; commit


The hardware-profile data producer should also be set to the category newbunch created in the
earlier step. This can be done by creating a category group within the nodeexecutionfilters
submode. Within that group, categories can be set for where the hardware check is to run. For the
example, it is just run on one category, newbunch :


[basecm11->monitoring->setup[hardware-profile]]% nodeexecutionfilters

[basecm11->...-profile]->nodeexecutionfilters]% add category filterhwp

[basecm11->...-profile]->nodeexecutionfilters*[filterhwp*]]% set categories newbunch

[basecm11->...-profile]->nodeexecutionfilters*[filterhwp*]]% commit


4. CMDaemon then automatically alerts the administrator if one of the nodes does not match the
hardware of that category during the first automated check. In the unlikely case that the reference
node is itself faulty, then that will also be obvious because all—or almost all, if more nodes are
faulty—of the other nodes in that category will then be reported “faulty” during the first check.


**14.7 Serial Over LAN Console Access** **717**


**14.7** **Serial Over LAN Console Access**


Direct console access to nodes is not always possible. Other possibilities to access the node are:


1. **SSH access via an ssh client.** This requires that an ssh server runs on the node and that it is
accessible via the network. Access can be via one of the following options:


    - a regular SSH client, run from a bash shell


    - via an ssh command run from the device mode of cmsh


    - via an ssh terminal launched from Base View via the navigation path:


Devices     - Nodes     - _node_     - Connect     - ssh .


2. **Remote shell via CMDaemon.** This is possible if CMDaemon is running on the node and accessible via Base View or cmsh .


    - In Base View, An interactive root shell session can be started up on a node via the navigation
path:


Devices     - Nodes     - _node_     - Connect     - Root shell .


This session is connected to the node via CMDaemon, and runs bash by default.


    - For cmsh, in device mode, running the command rshell node001 launches an interactive
bash session connected to node001 via CMDaemon.


3. **Connecting via a serial over LAN console.** If a serial console is configured, then a serial over LAN
(SOL) console can be accessed from cmsh ( rconsole ).


Item 3 in the preceding list, SOL access, is a useful low-level access method that is covered next more
thoroughly with:


  - some background notes on serial over LAN console access (section 14.7.1)


  - the configuration of SOL with Base View (section 14.7.2)


  - the configuration of SOL with cmsh (section 14.7.3)


  - the conman SOL logger and viewer (section 14.7.4)


**14.7.1** **Background Notes On Serial Console And SOL**
Serial ports are data ports that can usually be enabled or disabled for nodes in the BIOS.
If the serial port of a node is enabled, it can be configured in the node kernel to redirect a console
to the port. The serial port can thus provide what is called serial console access. That is, the console
can be viewed using a terminal software such as minicom (in Linux) or Hyperterminal (in Windows)
on another machine to communicate with the node via the serial port, using a null-modem serial cable.
This has traditionally been used by system administrators when remote access is otherwise disabled, for
example if ssh access is not possible, or if the TCP/IP network parameters are not set up right.
While traditional serial port console access as just described can be useful, it is inconvenient, because
of having to set arcane serial connection parameters, use the relatively slow serial port and use a special
serial cable. Serial Over LAN (SOL) is a more recent development of serial port console access, which
uses well-known TCP/IP networking over a faster Ethernet port, and uses a standard Ethernet cable.
SOL is thus generally more convenient than traditional serial port console access. The serial port DB-9 or
DB-25 connector and its associated 16550 UART chip rarely exist on modern servers that support SOL,
but they are nonetheless usually implied to exist in the BIOS, and can be “enabled” or “disabled” there,
thus enabling or disabling SOL.
SOL is a feature of the BMC (Baseboard Management Controller) for IPMI 2.0 and iLO. For DRAC,
CIMC, and Redfish, SOL via IPMI is used. SOL is enabled by configuring the BMC BIOS. When enabled,


**718** **Day-to-day Administration**


data that is going to the BMC serial port is sent to the BMC LAN port. SOL clients can then process the
LAN data to display the console. As far as the node kernel is concerned, the serial port is still just
behaving like a serial port, so no change needs to be made in kernel configuration in doing whatever
is traditionally done to configure serial connectivity. However, the console is now accessible to the
administrator using the SOL client on the LAN.
SOL thus allows SOL clients on the LAN to access the Linux serial console if


1. SOL is enabled and configured in the BMC BIOS


2. the serial console is enabled and configured in the node kernel


3. the serial port is enabled and configured in the node BIOS


The BMC BIOS, node kernel, and node BIOS therefore all need to be configured to implement SOL
console access.


**Background Notes: BMC BIOS Configuration**
The BMC BIOS SOL values are usually enabled and configured as a submenu or pop-up menu of the
node BIOS. These settings must be manually made to match the values in BCM, or vice versa.
During a factory reset of the node, it is likely that a SOL configuration in BCM will no longer match
the configuration on the node BIOS after the node boots. This is because BCM cannot configure these.
This is in contrast to the IP address and user authentication settings of the BMC (section 3.7), which
BCM is able to configure on reboot.


**Background Notes: Node Kernel Configuration**
Sections 14.7.2 and 14.7.3 explain how SOL access configuration is set up for the node kernel using
Base View or cmsh . SOL access configuration on the node kernel is serial access configuration on the
node kernel as far as the system administrator is concerned; the only difference is that the word “serial”
is replaced by “SOL” in BCM’s Base View and cmsh front ends to give a cluster perspective on the
configuration.


**Background Notes: Node BIOS Configuration**
Since BIOS implementations vary, and serial port access is linked with SOL access in various ways by
the BIOS designers, it is not possible to give short and precise details on how to enable and configure
them. The following rules-of-thumb, if followed carefully, should allow most BMCs to be configured for
SOL access with BCM:


  - Serial access, or remote access via serial ports, should be enabled in the BIOS, if such a setting
exists.


  - The node BIOS serial port settings should match the node configuration SOL settings (section 14.7.3). That means, items such as “ SOL speed ”, “ SOL Flow Control ”, and “ SOL port ” in
the node configuration must match the equivalent in the node BIOS. Reasonable values are:


**–**
SOL speed: 115200bps. Higher speeds are sometimes possible, but are more likely to have
problems.


**–**
SOL flow control: On. It is however unlikely to cause problems if flow control is off in both.


**–**
SOL port: COM1 (in the BIOS serial port configuration), corresponding to ttyS0 (in the node
kernel serial port configuration). Alternatively, COM2, corresponding to ttyS1. Sometimes,
the BIOS configuration display indicates SOL options with options such as: “ COM1 as SOL ”,
in which case such an option should be selected for SOL connectivity.


**–**
Terminal type: VT100 or ANSI.


  - If there is an option for BIOS console redirection after BIOS POST, it should be disabled.


**14.7 Serial Over LAN Console Access** **719**


  - If there is an option for BIOS console redirection before or during BIOS POST, it should be enabled.


  - The administrator should be aware that the BMC LAN traffic, which includes SOL traffic, can
typically run over a dedicated NIC or over a shared NIC. The choice of dedicated or shared is
toggled, either in the BIOS, or via a physical toggle, or both. If BMC LAN traffic is configured to
run on the shared NIC, then just connecting a SOL client with an Ethernet cable to the dedicated
BMC NIC port shows no console.


  - The node BIOS values should manually be made to match the values in BCM, or vice versa.


**14.7.2** **SOL Console Configuration With Base View**
In Base View, SOL configuration settings can be carried out per image via the navigation path
Provisioning - Software Images - _image_ - Edit - Settings
If the Enable SOL option is set to Yes then the kernel option to make the Linux serial console accessible is used after the node is rebooted.

This means that if the serial port and SOL are enabled for the node hardware, then after the node
reboots the Linux serial console is accessible over the LAN via an SOL client.

If SOL is correctly configured in the BIOS and in the image, then access to the Linux serial console
is possible via the minicom serial client running on the computer (from a bash shell for example), or via
the rconsole serial client running in cmsh .


**14.7.3** **SOL Console Configuration And Access With** cmsh
In cmsh, the serial console kernel option for a software image can be enabled within the softwareimage
mode of cmsh . For the default image of default-image, this can be done as follows:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% softwareimage use default-image


[basecm11->softwareimage[default-image]]% set enablesol yes

[basecm11->softwareimage*[default-image*]]% commit


The SOL settings for a particular image can be seen with the show command:


[basecm11->softwareimage[default-image]]% show | grep SOL

Parameter Value

------------------------------ -------------
Enable SOL yes

SOL Flow Control yes

SOL Port ttyS1

SOL Speed 115200


Values can be adjusted if needed with the set command.
On rebooting the node, the new values are used.
To access a node via an SOL client, the node can be specified from within the device mode of cmsh,
and the rconsole command run on cmsh on the head node:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% rconsole

screen cleared and the following conman output is displayed:

===============================================================================

conman


**720** **Day-to-day Administration**


To exit IPMI SOL, type <ENTER> "&" "."

===============================================================================


<ConMan> Connection to console [node001] opened.


If at this point, there is no further response in conman on the console after pressing the <ENTER> key,
then there is a communication failure, probably due to a misconfigured communication parameter. This
could happen, for example, if the serial port ttyS1 has been set, but the node is connected on ttyS0 .
Setting the value of SOL Port to ttyS0 and rebooting the node to pick up the new value, would solve
that issue, so that pressing the <ENTER> key, would display the node console:


**Example**


Ubuntu 18.04.2 LTS node001 ttyS0


node001 login:


**14.7.4** **The** conman **Serial Console Logger And Viewer**
In BCM, the console viewer and logger service conman is used to connect to an SOL console and log the
console output.
If the “ Enable SOL ” option in Base View, or if the enablesol parameter in cmsh is enabled for the
software image, then the conman configuration is written out and the conman service is started.


**Logging The Serial Console**
The data seen at the serial console is then logged via SOL to the head node after reboot. For each node
that has logging enabled, a log file is kept on the head node. For example, for node001 the log file would
be at /var/log/conman/node001.log . To view the logged console output without destroying terminal
settings, using less with the -R option is recommended, as in: less -R /var/log/conman/node001.log .


**Using The Serial Console Interactively**
**Viewing quirk during boot:** In contrast to the logs, the console viewer shows the initial booting stages
of the node as it happens. There is however a quirk the system administrator should be aware of:
Normally the display on the physical console is a copy of the remote console. However, during boot,
after the remote console has started up and been displaying the physical console for a while, the physical
console display freezes. For the Linux 2.6 kernel series, the freeze occurs just before the ramdisk is run,
and means that the display of the output of the launching init.d services is not seen on the physical
console (figure 14.2).


**14.7 Serial Over LAN Console Access** **721**


Figure 14.2: Physical Console Freeze During SOL Access


The freeze is only a freeze of the display, and should not be mistaken for a system freeze. It occurs
because the kernel is configured during that stage to send to only one console, and that console is the
remote console. The remote console continues to display its progress (figure 14.3) during the freeze of
the physical console display.


**722** **Day-to-day Administration**


Figure 14.3: Remote Console Continues During SOL Access During Physical Console Freeze


Finally, just before login is displayed, the physical console once more (figure 14.4) starts to display
what is on the remote console (figure 14.5).


**14.7 Serial Over LAN Console Access** **723**


Figure 14.4: Physical Console Resumes After Freeze During SOL Access


Figure 14.5: Remote Console End Display After Boot


The physical console thus misses displaying several parts of the boot progress.


**724** **Day-to-day Administration**


**Exit sequence:** The conman console viewer session can be exited with the sequence &. (the last entry
in the sequence being a period). Strictly speaking, the &. sequence must actually be preceded by an
_<ENTER>_ .


**The console buffer issue when accessing the remote console:** A feature of SOL console clients is that
the administrator is not presented with any text prompt from the node that is being accessed. This is
useful in some cases, and can be a problem in others.
An example of the issue is the case where the administrator has already logged into the console and
typed in a command in the console shell, but has no intention of pressing the _<ENTER>_ key until some
other tasks are first carried out. If the connection breaks at this point, then the command typed in is
held in the console shell command buffer, but is not displayed when a remote serial connection is reestablished to the console—the previously entered text is invisible to the client making the connection.
A subsequent _<ENTER>_ would then attempt to execute the command. This is why an _<ENTER>_ is not
sent as the last key sequence during automated SOL access, and it is left to the administrator to enter
the appropriate key strokes.
To avoid commands in the console shell buffer inadvertently being run when taking over the console
remotely, the administrator can start the session with a _<CTRL>_ -u to clear out text in the shell before
pressing _<ENTER>_ .


**14.8** **Managing Raw Monitoring Data**


From NVIDIA Base Command Manager version 8.0 onward, the raw monitoring data values are stored
as binary data under /var/spool/cmd/monitoring instead of as binary data within MySQL or MariaDB.
The reason behind this change was to significantly increase performance. The monitoring subsystem in
BCM was thoroughly rewritten for this change.


**14.8.1** **Monitoring Subsystem Disk Usage With The** monitoringinfo --storage **Option**
The disk usage by the monitoring subsystem can be viewed using the monitoringinfo command with
the --storage option:


**Example**


[basecm11->device]% monitoringinfo master --storage

Storage Elements Disk size Usage Free disk

--------------------------- ---------- ------------ -------- -----------
Mon::Storage::Engine 1,523 1.00 GiB 1.28% 14.1 GiB
Mon::Storage::Message 1 16.0 MiB 0.000% Mon::Storage::RepositoryId 1,528 47.7 KiB 100.0% 

The Engine component stores the raw monitoring data. It grows in 1GB increments each time its
usage reaches 100%.


**14.8.2** **Estimating The Required Size Of The Storage Device**
The final size of the monitoring directory can be estimated with the script cm-monitoring-disk-usage.

py .
The size estimate assumes that there are no changes in configuration, such as enabling advanced
metrics for jobs, or increasing the maximum number of labeled entities, or large numbers of running
jobs.
The size estimate value is the maximum value it will take if the cluster runs forever. It is therefore an

over-estimate in practice.


**Example**


**14.8 Managing Raw Monitoring Data** **725**


[root@basecm11 ~]# /cm/local/apps/cmd/scripts/monitoring/cm-monitoring-disk-usage.py

Number of used entities: 10

Number of used measurables: 286

Number of measurables: 286

Number of data producers: 98

Number of consolidators: 2


Current monitoring directory: /var/spool/cmd/monitoring

Monitoring directory size: 1.024 GB

Maximal directory size: 1.409 GB


**14.8.3** **Moving Monitoring Data Elsewhere**
A procedure to move monitoring data from the default /var/spool/cmd/monitoring/ directory to a
new directory is as follows:


1. A new directory in which monitoring should be saved is picked.


The block storage device for the directory should not be a shared DAS (Direct Attached Storage,
such as a locally attached drive) or a NAS (Network Attached Storage, such as NFS or Lustre
which work over a network connection). That is because if there is an outage, then:


    - If such a DAS storage becomes unavailable at some time, then CMDaemon assumes that no
monitoring data values exist, and creates an empty data file on the local storage. If the DAS
storage comes back and is mounted again, then it hides the underlying files, which would
lead to discontinuous values and related issues.


    - If such a NAS storage is used, then an outage of the NAS can make CMDaemon unresponsive
as it waits for input and output. In addition, when CMDaemon starts with a NAS storage,
and if the NAS is unavailable for some reason, then an inappropriate mount may happen as
in the DAS storage case, leading to discontinuous values and related issues.


2. The MonitoringPath directive (page 864) is given the new directory as its value.


3. CMDaemon is stopped ( systemctl stop cmd ).


4. The /var/spool/cmd/monitoring/ directory is moved to the new directory.


5. CMDaemon is restarted ( systemctl start cmd ).


**14.8.4** **Reducing Monitoring Data By Reducing Samples**
Options to reduce the amount of monitoring data gathered include reducing the Maximal age and
Maximal samples for data producers (section 10.4.1) to smaller, but still non-zero values. After reinitializing the monitoring data collection, so that existing data is removed, the values reported by the
cm-monitoring-disk-usage.py script (section 14.8.2) then show the new storage estimates for the monitoring data.


**14.8.5** **Deleting All Monitoring Data**
A procedure to delete all monitoring data from the default /var/spool/cmd/monitoring/ directory is
as follows:


1. The CMDaemon service on all nodes can be stopped by running the following on the active head
node:

pdsh -g all systemctl stop cmd


2. On both head nodes, the monitoring data is removed with:


**726** **Day-to-day Administration**


rm -f /var/spool/cmd/monitoring/*
rm -f /var/spool/cmd/backup/*/var/spool/cmd/monitoring/*


3. On both head nodes, the associated database tables for the CMDaemon user are cleared with a
mySQL session run on each head node.


The CMDaemon database user is cmdaemon by default, but the value can be checked with a grep
on the cmd.conf file:


[root@basecm11 ~]# grep ^DBUser /cm/local/apps/cmd/etc/cmd.conf

DBUser = "cmdaemon"


Similarly, the password for the cmdaemon user can be found with a grep as follows:


[root@basecm11 ~]# grep ^DBPass /cm/local/apps/cmd/etc/cmd.conf

DBPass = "slarti8813bartfahrt"


The monitoring measurables can then be deleted by running a session on each head node as follows:


**Example**


[root@basecm11 ~]# mysql -ucmdaemon -p

Enter password:
Welcome to the MariaDB monitor. Commands end with ; or _\_ g.

Your MariaDB connection id is 2909

Server version: 5.5.56-MariaDB MariaDB Server


Copyright (c) 2000, 2017, Oracle, MariaDB Corporation Ab and others.


Type 'help;' or ' _\_ h' for help. Type ' _\_ c' to clear the current input statement.


MariaDB [(none)]> use cmdaemon;

Database changed
MariaDB [cmdaemon]> truncate MonitoringMeasurables;
MariaDB [cmdaemon]> truncate MonitoringMeasurableMetrics;
MariaDB [cmdaemon]> truncate MonitoringMeasurableHealthChecks;
MariaDB [cmdaemon]> truncate MonitoringMeasurableEnums;
MariaDB [cmdaemon]> truncate EntityMeasurables;
MariaDB [cmdaemon]> truncate EnumMetricValues;

MariaDB [cmdaemon]> truncate LabeledEntities;

MariaDB [cmdaemon]> truncate JobInformation;

MariaDB [cmdaemon]> exit

_repeat on other head node_


4. On both head nodes, CMDaemon can then be restarted with:

systemctl start cmd


5. On the active head node, after the command:

cmha status

shows all is OK, the CMDaemon service can be started on all regular nodes again. The OK state
should be achieved in about 15 seconds.


The CMDaemon service is started with, for example:
pdsh -g computenode systemctl start cmd


**14.9 Node Replacement** **727**


**14.9** **Node Replacement**


To replace an existing node with a new node, the node information can be updated via cmsh .
If the new MAC address is known, then it can set that for the node. If the MAC address is not known,
then the existing entry can be cleared.
If the MAC address is not known ahead of time, then the node name for the machine should be
selected when it is provisioning for the first time. The steps for a new node node031 would be as follows:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node0031

_if new mac address is known, then:_

[basecm11->device[node031]]% set mac < _new mac address_ 
_else if new mac address is not known:_

[basecm11->device[node031]]% clear mac

_the changed setting in either case must be committed:_

[basecm11->device[node031]]% commit


If the disk is the same size as the one that is being replaced, and everything else matches up, then
this should be all that needs to be done

There is more information on the node installing system in section 5.4. How to add a large number
of nodes at a time efficiently is described in that section. The methods used can include the newnodes
command of cmsh (page 251) and the Nodes Identification resource of Base View (page 255).


**14.10** **Ansible And NVIDIA Base Command Manager**


This section describes using Ansible with BCM. Using Ansible to install NVIDIA Base Command Manager is described in section 3.4 of the _Installation Manual_ .


**14.10.1** **An Overview Of Ansible**

Ansible is a popular automated configuration management software.
The BCM administrator is expected to have some experience already with Ansible. The basic concepts are covered in the official Ansible documentation at [https://docs.ansible.com/ansible/latest/](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html)
[user_guide/basic_concepts.html](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html), and further details are accessible from that site too.
As a reminder:


  - Ansible is designed to administer groups of machines from an _[inventory](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#inventory)_ of machines.


[• An Ansible](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#modules) _module_ [is code, usually in Python, that is executed by Ansible to carry out Ansible](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#tasks)
_[tasks](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#tasks)_, usually on a remote node. The module returns values.


  - An Ansible _[playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html)_ is a YAML file. The file declares a configuration that is to be executed (“the
playbook is followed”) on selected machines. The execution is usually carried out over SSH, by
placing modules on the remote machine.


  - Traditionally, official Ansible content was obtained as a part of milestone releases of Ansible Engine, (the Red Hat version of Ansible for the enterprise).


  - Since Ansible version 2.10, the official way to distribute content is via Ansible content _[collections](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#collections)_ .
Collections are composed of Ansible playbooks, modules, module utilities and plugins. The collection is a formatted set of tools used to achieve automation with Ansible.


  - The official Ansible list of collections is at [https://docs.ansible.com/ansible/latest/](https://docs.ansible.com/ansible/latest/collections/index.html#list-of-collections)
[collections/index.html#list-of-collections](https://docs.ansible.com/ansible/latest/collections/index.html#list-of-collections) . At the time of writing of this section (March
2022) there were 100 collections.


  - Community-supported collections are also available, at galaxy.ansible.com .


**728** **Day-to-day Administration**


**Picking Up The BCM Ansible Collections**
In particular, the web interface at [https://galaxy.ansible.com/brightcomputing](https://galaxy.ansible.com/brightcomputing) shows the updated
list of BCM Ansible collections.

From version 9.1 onward of BCM, the BCM Ansible collection naming scheme has been changed
so that the name now indicates the BCM version number. This now makes it simpler for the cluster
administrator to choose the right Ansible collection.
For example, to install the latest version of the BCM Ansible collection for a NVIDIA Base Command
Manager 11 cluster, the following command can now be run:


[root@basecm11 ~]# ansible-galaxy collection install brightcomputing.bcm110


**14.10.2** **A Simple Playbook Example**
In this section, a playbook from the BCM collection is run.


**Preparations**
To start with, Python is loaded, and Ansible installed:


[root@basecm11 ~]# module load python3

[root@basecm11 ~]# pip install ansible


**Running A Simple Playbook**
The directory /cm/local/examples/cmd/ansible has several BCM Ansible playbook examples.
The Ansible playbook to add a user can be run. The playbook is simply:


[root@basecm11 ~]# cat /cm/local/examples/cmd/ansible/add-user.yaml

--
- hosts: all

gather_facts: false

tasks:

collections:

- brightcomputing.bcm110

tasks:

 - name: create test-user

user:

name: test-user

password: test-user-password

profile: readonly


[The latest NVIDIA Base Command Manager 11-compatible version of the BCM Ansible collection is](https://galaxy.ansible.com/brightcomputing/bcm110)
at [https://galaxy.ansible.com/brightcomputing/bcm110](https://galaxy.ansible.com/brightcomputing/bcm110) . It can be installed with the ansible-galaxy
tool from the galaxy.ansible.com repository directly with:


[root@basecm11 ~]# ansible-galaxy collection install brightcomputing.bcm110


**Documentation For The BCM Collection**

The brightcomputing.bcm110 documentation for modules can be explored using ansible-doc in the
usual way, using the namespace. For example, for the user module in the brightcomputing.bcm110
namespace, this would be (output truncated):


[root@basecm11 ~]# ansible-doc brightcomputing.bcm110.user

- BRIGHTCOMPUTING.BCM110.USER

- (/root/.ansible/collections/ansible_collections/brightcomputing/bcm110/plugins/modules/user.py)


User


ADDED IN: version 9.2.0 of brightcomputing.bcm110


**14.10 Ansible And NVIDIA Base Command Manager** **729**


 - note: This module has a corresponding action plugin.


OPTIONS (= is mandatory):


- ID

User ID number

[Default: (null)]

type: str


- cloneFrom

The id or name of the entity that the new entity will be cloned from.
(take effect only at entity creation)

[Default: ]

type: str


- email

...


The list of modules in the brightcomputing.bcm110 collection can be viewed with ansible-doc -l

brightcomputing.bcm110 .
Almost all the modules are available as a pair. For such a pair, one module out of the pair is to query
the attributes of the entity being dealt with by the pair, while the other module is to set the attributes.


**Running The Ansible Playbook**
The add-user playbook can now be run with:


**Example**


[root@basecm11 ~]# ansible-playbook -ilocalhost, /cm/local/examples/cmd/ansible/add-user.yaml


PLAY [all]

*********************************************************************************************


TASK [create test-user]

*********************************************************************************************

changed: [localhost]


PLAY RECAP

*********************************************************************************************

localhost : ok=1 changed=1 unreachable=0 failed=0 skipped=0

rescued=0 ignored=0


The YAML code shows a user should be created after execution of the playbook. If unsure, the
playbook can be run again. This should do no harm since well-formed playbooks are idempotent.
The new list of users can be verified with:


[root@basecm11 ~]# cmsh -c "user list"

Name (key) ID (key) Primary group Secondary groups

---------------- ---------------- ---------------- ---------------
cmsupport 1000 cmsupport

test-user 1001 test-user


**730** **Day-to-day Administration**


**14.10.3** **An Intermediate Playbook Example: Setting Up A Cluster For Demonstration**
**Purposes**
The simple playbook in the preceding section has the advantage of being a quick way for the administrator to be reasonably sure that Ansible is running as it should be.
An administrator who is intending to use Ansible is typically going to need to be more familiar with
how Ansible playbooks can be used to define BCM infrastructure.
This section (14.10.3) and the next (14.10.4) aim to provide this familiarity. They should be a guide
for users when they go about defining their own BCM infrastructure with Ansible, as well as a model
for how to carry out Ansible tasks for BCM.
The example session in this section (section 14.10.3) is about a cluster administrator who wishes to
prepare a playbook so that the default image is updated, and then have the cluster set up some new
objects with default values. This is useful for testing out changes in the new objects. The idea being
that the administrator has up-to-date nodes with default settings in the new objects, and which work
to begin with. That makes the new objects suitable for demonstrations and for making changes to see
how it affects the standard settings. It also provides the convenience of being able to refer back to the
working defaults in the original objects if things go wrong with the demonstration objects.
The tasks to bring the cluster to the “demo” state are described next.


**Cloning The Image**
The administrator now clones the default image. The idea being that further changes can be made
on the cloned image later on, with the default image instance remaining unchanged, and available for
comparison.
The YAML example clone-software-image.yaml provided with BCM can be displayed and used
to carry out the cloning as shown in the following session:


[root@basecm11 ~]# cat /cm/local/examples/cmd/ansible/clone-software-image.yaml

--
- hosts: all

gather_facts: false

tasks:

  - name: clone a software image

brightcomputing.bcm110.software_image:

name: cloned-image

cloneFrom: default-image
path: /cm/images/cloned-image


[root@basecm11 ~] ansible-playbook -i localhost, /cm/local/examples/cmd/ansible/clone-software-image.yaml


**Cloning The Category**
A clone of the default category, democategory, can be built with the brightcomputing.bcm110.category
module:


[root@basecm11 ~]# cat clonedefaultcat.yaml

- hosts: all

gather_facts: false


tasks:

  - name: clone category

brightcomputing.bcm110.category:

name: democategory

cloneFrom: default

[root@basecm11 ~] ansible-playbook -i localhost, clonedefaultcat.yaml


**14.10 Ansible And NVIDIA Base Command Manager** **731**


**Setting The Software Image In The Cloned Category To Be The Cloned Image**
The software image in the cloned category can then be set to the cloned-image from earlier with:


[root@basecm11 ~]# cat setimageincat.yaml

- hosts: all

gather_facts: false


tasks:

  - name: set image in category

brightcomputing.bcm110.category:

name: democategory

softwareImageProxy:

parentSoftwareImage: cloned-image

[root@basecm11 ~] ansible-playbook -i localhost, setimageincat.yaml


**Setting The Regular Nodes To Be In The Cloned Category**
The regular nodes node001 and node002 can be placed in the cloned category with:


[root@basecm11 ~]# cat setcatofnodes.yaml

- hosts: all

gather_facts: false


tasks:

  - name: list all nodes

brightcomputing.bcm110.node_info:

format: dict

include_id: false

for_update: true

register: result


  - name: set head_node

set_fact:

all_nodes: "{{ result.nodes }}"


  - name: assign compute nodes to cloned category

brightcomputing.bcm110.physical_node:

hostname: "{{ item }}"

mac: "{{ all_nodes[item].mac }}"

category: democategory

loop:

    - node001

    - node002

[root@basecm11 ~] ansible-playbook -i localhost, setcatofnodes.yaml


Without using Ansible, and using cmsh directly instead, the preceding placement could be carried
out with:


[root@basecm11 ~] for i in {001..002}

do cmsh -c "device use node$i; set category democategory; commit"

done


**14.10.4** **A More Complicated Playbook Example: Creating An Edge Site And Related**
**Properties**
This section provides a more complicated BCM Ansible collection-based playbook, and elaborates upon
how it is used.

The collection is first shown as a whole in the following section. Then less obvious portions from it
are explained, with the help of number labels, in the sections after that, starting on page 734.


**732** **Day-to-day Administration**


**The Collection**

The full collection is as follows:


--
- hosts: all

gather_facts: false

vars:

site:

name: test-site

secret: SECRET


director:

hostname: test-site-director

mac: 00:11:22:33:44:55

eth0_ip: 10.152.0.254

eth1_ip: 10.161.0.254


nodes:

   - hostname: edge-node-01

mac: 00:11:22:33:44:01

eth0_ip: 10.161.0.1


   - hostname: edge-node-02

mac: 00:11:22:33:44:02

eth0_ip: 10.161.0.2


   - hostname: edge-node-03

mac: 00:11:22:33:44:03

eth0_ip: 10.161.0.3


pre_tasks:


  - name: set compute nodes for site

set_fact:

site_compute_nodes: "{{nodes | map(attribute='hostname') | list}}"


  - name: set nodes for site

set_fact:

site_nodes: "{{[director.hostname] + site_compute_nodes}}"


tasks: