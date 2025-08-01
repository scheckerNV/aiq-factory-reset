**NVIDIA Base Command Manager 11**

###### **Administrator Manual**


Revision: 8a9e3ea16


Date: Wed Jul 23 2025


©2025 NVIDIA Corporation & affiliates. All Rights Reserved. This manual or parts thereof may not be
reproduced in any form unless permitted by contract or by written permission of NVIDIA Corporation.


**Trademarks**


Linux is a registered trademark of Linus Torvalds. PathScale is a registered trademark of Cray, Inc.
Red Hat and all Red Hat-based trademarks are trademarks or registered trademarks of Red Hat, Inc.
SUSE is a registered trademark of SUSE LLC. NVIDIA, CUDA, GPUDirect, HPC SDK, NVIDIA DGX,
NVIDIA Nsight, and NVLink are registered trademarks of NVIDIA Corporation. FLEXlm is a registered
trademark of Flexera Software, Inc. PBS Professional, and Green Provisioning are trademarks of Altair
Engineering, Inc. All other trademarks are the property of their respective owners.


**Rights and Restrictions**


All statements, specifications, recommendations, and technical information contained herein are current
or planned as of the date of publication of this document. They are reliable as of the time of this writing
and are presented without warranty of any kind, expressed or implied. NVIDIA Corporation shall
not be liable for technical or editorial errors or omissions which may occur in this document. NVIDIA
Corporation shall not be liable for any damages resulting from the use of this document.


**Limitation of Liability and Damages Pertaining to NVIDIA Corporation**


The NVIDIA Base Command Manager product principally consists of free software that is licensed by
the Linux authors free of charge. NVIDIA Corporation shall have no liability nor will NVIDIA Corporation provide any warranty for the NVIDIA Base Command Manager to the extent that is permitted
by law. Unless confirmed in writing, the Linux authors and/or third parties provide the program as is
without any warranty, either expressed or implied, including, but not limited to, marketability or suitability for a specific purpose. The user of the NVIDIA Base Command Manager product shall accept
the full risk for the quality or performance of the product. Should the product malfunction, the costs for
repair, service, or correction will be borne by the user of the NVIDIA Base Command Manager product. No copyright owner or third party who has modified or distributed the program as permitted in
this license shall be held liable for damages, including general or specific damages, damages caused by
side effects or consequential damages, resulting from the use of the program or the un-usability of the
program (including, but not limited to, loss of data, incorrect processing of data, losses that must be
borne by you or others, or the inability of the program to work together with any other program), even
if a copyright owner or third party had been advised about the possibility of such damages unless such
copyright owner or third party has signed a writing to the contrary.


#### **Table of Contents**

Table of Contents . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3

0.1 Quickstart . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

0.2 About This Manual . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

0.3 About The Manuals In General . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19

0.4 Getting Administrator-Level Support . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
0.5 Getting Professional Services . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20


**1** **Introduction** **21**

1.1 NVIDIA Base Command Manager Functions And Aims . . . . . . . . . . . . . . . . . . . . 21
1.2 The Scope Of The Administrator Manual (This Manual) . . . . . . . . . . . . . . . . . . . . 21

1.2.1 Installation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21

1.2.2 Configuration, Management, And Monitoring Via BCM Tools And Applications . 22
1.3 Outside The Direct Scope Of The Administrator Manual . . . . . . . . . . . . . . . . . . . 23


**2** **Cluster Management With NVIDIA Base Command Manager** **25**
2.1 Concepts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

2.1.1 Devices . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25

2.1.2 Software Images . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
2.1.3 Node Categories . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
2.1.4 Node Groups . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

2.1.5 Roles . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

2.1.6 Configuration Overlay . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28

2.2 Modules Environment . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29

2.2.1 Adding And Removing Modules . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29
2.2.2 Using Local And Shared Modules . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
2.2.3 Setting Up A Default Environment For All Users . . . . . . . . . . . . . . . . . . . . 30
2.2.4 Creating A Modules Environment Module . . . . . . . . . . . . . . . . . . . . . . . 31
2.2.5 Lua Modules Environment (LMod) . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

2.3 Authentication . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32

2.3.1 Changing Administrative Passwords On The Cluster . . . . . . . . . . . . . . . . . 32
2.3.2 Logins Using ssh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
2.3.3 Certificates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34
2.3.4 Profiles . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

2.4 Base View GUI . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35

2.4.1 Installing The Cluster Management GUI Service . . . . . . . . . . . . . . . . . . . . 36
2.4.2 Navigating The Cluster With Base View . . . . . . . . . . . . . . . . . . . . . . . . . 38
2.5 Cluster Management Shell . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41
2.5.1 Invoking cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41
2.5.2 Levels, Modes, Help, And Commands Syntax In cmsh . . . . . . . . . . . . . . . . . 45
2.5.3 Working With Objects . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 49
2.5.4 Accessing Cluster Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60


**4** **Table of Contents**


2.5.5 Advanced cmsh Features . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61

2.6 Cluster Management Daemon . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 73
2.6.1 Managing And Inspecting The Cluster Management Daemon . . . . . . . . . . . . 74
2.6.2 Configuring The Cluster Management Daemon . . . . . . . . . . . . . . . . . . . . 75

2.6.3 CMDaemon Versions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 75

2.6.4 Configuring The Cluster Management Daemon Logging Facilities . . . . . . . . . 76
2.6.5 Configuration File Modification, And The FrozenFile Directive . . . . . . . . . . . 77
2.6.6 Configuration File Conflicts Between The Standard Distribution And BCM For

Generated And Non-Generated Files . . . . . . . . . . . . . . . . . . . . . . . . . . 78

2.6.7 CMDaemon Lite . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78


**3** **Configuring The Cluster** **83**
3.1 Main Cluster Configuration Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83
3.1.1 Cluster Configuration: Various Name-Related Settings . . . . . . . . . . . . . . . . 84
3.1.2 Cluster Configuration: Some Network-Related Settings . . . . . . . . . . . . . . . . 85
3.1.3 Miscellaneous Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 87
3.1.4 Limiting The Maximum Number Of Open Files . . . . . . . . . . . . . . . . . . . . 90
3.2 Network Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 91
3.2.1 Configuring Networks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92
3.2.2 Adding Networks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 96
3.2.3 Changing Network Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 97
3.2.4 Tools For Viewing Cluster Connections And Connectivity . . . . . . . . . . . . . . 111
3.3 Configuring Bridge Interfaces . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114
3.4 Configuring VLAN interfaces . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 115
3.4.1 Configuring A VLAN Interface Using cmsh . . . . . . . . . . . . . . . . . . . . . . . 115
3.4.2 Configuring A VLAN Interface Using Base View . . . . . . . . . . . . . . . . . . . . 116
3.5 Configuring Bonded Interfaces . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116
3.5.1 Adding A Bonded Interface . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116
3.5.2 Single Bonded Interface On A Regular Node . . . . . . . . . . . . . . . . . . . . . . 117
3.5.3 Multiple Bonded Interface On A Regular Node . . . . . . . . . . . . . . . . . . . . . 117

3.5.4 Bonded Interfaces On Head Nodes And HA Head Nodes . . . . . . . . . . . . . . 118

3.5.5 Tagged VLAN On Top Of a Bonded Interface . . . . . . . . . . . . . . . . . . . . . . 118

3.5.6 Association Of MAC Address With A Bonded Interface . . . . . . . . . . . . . . . . 119

3.5.7 Further Notes On Bonding . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119
3.6 Configuring InfiniBand Interfaces . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120
3.6.1 Installing Software Packages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120
3.6.2 Subnet Managers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120
3.6.3 InfiniBand Network Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 121
3.6.4 Verifying Connectivity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 122
3.7 Configuring BMC (IPMI/iLO/DRAC/CIMC/Redfish) Interfaces . . . . . . . . . . . . . . 124
3.7.1 BMC Network Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124

3.7.2 BMC Authentication . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126

3.7.3 Interfaces Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
3.7.4 Identification With A BMC . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
3.8 Configuring BlueField DPUs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
3.8.1 Assumptions And Limitations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
3.8.2 Preparation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128


**Table of Contents** **5**


3.8.3 Installation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 129

3.8.4 Managing DPU Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 133
3.9 Configuring Switches And PDUs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 136
3.9.1 Configuring With The Manufacturer’s Configuration Interface . . . . . . . . . . . . 136
3.9.2 Configuring SNMP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 138
3.10 Configuring Cumulus Switches . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140

3.10.1 Cumulus Switches Access Configuration, Initialization And Network Device Discovery . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
3.10.2 Custom Service Setups For Cumulus Linux . . . . . . . . . . . . . . . . . . . . . . . 142
3.10.3 Uplink Ports . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 148
3.10.4 The showport MAC Address to Port Matching Tool . . . . . . . . . . . . . . . . . . 149
3.10.5 Disabling Port Detection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 149

3.10.6 The switchoverview Command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 150

3.11 Configuring NetQ Network Management System . . . . . . . . . . . . . . . . . . . . . . . 151
3.12 Disk Layouts: Disked, Semi-Diskless, And Diskless Node Configuration . . . . . . . . . . 151

3.12.1 Disk Layouts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 151
3.12.2 Disk Layout Assertions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 151
3.12.3 Changing Disk Layouts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 152
3.12.4 Changing A Disk Layout From Disked To Diskless . . . . . . . . . . . . . . . . . . 152
3.13 Configuring NFS Volume Exports And Mounts . . . . . . . . . . . . . . . . . . . . . . . . . 154

3.13.1 Exporting A Filesystem Using Base View And cmsh . . . . . . . . . . . . . . . . . . 156
3.13.2 Mounting A Filesystem Using Base View And cmsh . . . . . . . . . . . . . . . . . . 159
3.13.3 Mounting A Filesystem Subtree For A Diskless Node Over NFS . . . . . . . . . . . 162
3.13.4 Configuring NFS Volume Exports And Mounts Over RDMA With OFED Drivers . 164
3.14 Managing And Configuring Services . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 165

3.14.1 Why Use The Cluster Manager For Services? . . . . . . . . . . . . . . . . . . . . . . 165
3.14.2 Managing And Configuring Services—Examples . . . . . . . . . . . . . . . . . . . 166
3.15 Managing And Configuring A Rack . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 171

3.15.1 Racks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 171

3.15.2 Assigning Devices To A Rack . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 175
3.15.3 Assigning Devices To A Chassis . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177
3.16 Configuring GPU Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 180


3.16.1 GPUs And GPU Units . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 180

3.16.2 Configuring GPU Settings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 180
3.16.3 MIG Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 187
3.17 Configuring Sampling From A Prometheus Exporter . . . . . . . . . . . . . . . . . . . . . 196
3.18 Configuring Custom Scripts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 196


3.18.1 custompowerscript . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 197

3.18.2 custompingscript . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 197

3.18.3 customremoteconsolescript . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 197

3.18.4 sysinfo Custom Scripts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 198
3.19 Cluster Configuration Without Execution By CMDaemon . . . . . . . . . . . . . . . . . . . 201

3.19.1 Cluster Configuration: The Bigger Picture . . . . . . . . . . . . . . . . . . . . . . . . 201
3.19.2 Making Nodes Function Differently By Image . . . . . . . . . . . . . . . . . . . . . 202
3.19.3 Making All Nodes Function Differently From Normal Cluster Behavior With

FrozenFile . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 205


**6** **Table of Contents**


3.19.4 Adding Functionality To Nodes Via An initialize Or finalize Script . . . . . . 205
3.19.5 Examples Of Configuring Nodes With Or Without CMDaemon . . . . . . . . . . . 206
3.20 Saving A Backup Of Configuration Files With versionconfigfiles . . . . . . . . . . . . . 207


**4** **Power Management** **209**
4.1 Configuring Power Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 209

4.1.1 PDU-based Power Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 210

4.1.2 IPMI-Based Power Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 212

4.1.3 Combining PDU- and IPMI-Based Power Control . . . . . . . . . . . . . . . . . . . 213

4.1.4 Custom Power Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 213

4.1.5 Hewlett Packard iLO-Based Power Control . . . . . . . . . . . . . . . . . . . . . . . 215

4.1.6 Dell drac -based Power Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 215

4.1.7 Redfish-Based and CIMC-Based Power Control . . . . . . . . . . . . . . . . . . . . 215
4.2 Power Operations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 215
4.2.1 Power Operations Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 215
4.2.2 Power Operations With Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . 216
4.2.3 Power Operations Through cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 217
4.3 Monitoring Power . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 221
4.4 Switch Configuration To Survive Power Downs . . . . . . . . . . . . . . . . . . . . . . . . 221


**5** **Node Provisioning** **223**

5.1 Before The Kernel Loads . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 223

5.1.1 PXE Booting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 223
5.1.2 iPXE Booting From A Disk Drive . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 226
5.1.3 iPXE Booting Using InfiniBand . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 226
5.1.4 Using PXE To Boot From The Drive . . . . . . . . . . . . . . . . . . . . . . . . . . . 227
5.1.5 Network Booting Without PXE On The ARMv8 Architecture . . . . . . . . . . . . . 227
5.1.6 Network Booting Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 227

5.1.7 The Boot Role . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 228

5.2 Provisioning Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 228
5.2.1 Provisioning Nodes: Configuration Settings . . . . . . . . . . . . . . . . . . . . . . 228
5.2.2 Provisioning Nodes: Role Setup With cmsh . . . . . . . . . . . . . . . . . . . . . . . 229
5.2.3 Provisioning Nodes: Role Setup With Base View . . . . . . . . . . . . . . . . . . . . 230
5.2.4 Provisioning Nodes: Housekeeping . . . . . . . . . . . . . . . . . . . . . . . . . . . 232
5.3 The Kernel Image, Ramdisk And Kernel Modules . . . . . . . . . . . . . . . . . . . . . . . 237
5.3.1 Booting To A “Good State” Software Image . . . . . . . . . . . . . . . . . . . . . . . 237
5.3.2 Selecting Kernel Driver Modules To Load Onto Nodes . . . . . . . . . . . . . . . . 237
5.3.3 InfiniBand Provisioning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 239
5.3.4 VLAN Provisioning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 241

5.4 Node-Installer . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 242

5.4.1 Requesting A Node Certificate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 243
5.4.2 Deciding Or Selecting Node Configuration . . . . . . . . . . . . . . . . . . . . . . . 245
5.4.3 Starting Up All Network Interfaces . . . . . . . . . . . . . . . . . . . . . . . . . . . 256
5.4.4 Determining Install-mode Type And Execution Mode . . . . . . . . . . . . . . . . . 258
5.4.5 Running Initialize Scripts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 263
5.4.6 Checking Partitions, RAID Configuration, Mounting Filesystems . . . . . . . . . . 263
5.4.7 Synchronizing The Local Drive With The Software Image . . . . . . . . . . . . . . . 264


**Table of Contents** **7**


5.4.8 Writing Network Configuration Files . . . . . . . . . . . . . . . . . . . . . . . . . . 268
5.4.9 Creating A Local /etc/fstab File . . . . . . . . . . . . . . . . . . . . . . . . . . . . 268
5.4.10 Booting From The Local Hard Drive . . . . . . . . . . . . . . . . . . . . . . . . . . . 269
5.4.11 Running Finalize Scripts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 271
5.4.12 Unloading Specific Drivers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 272
5.4.13 Switching To The Local init Process . . . . . . . . . . . . . . . . . . . . . . . . . . . 272

5.5 Node States . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 272

5.5.1 Node States Icons In Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 272

5.5.2 Node States Shown In cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 272

5.5.3 Node States Indicating Regular Start Up . . . . . . . . . . . . . . . . . . . . . . . . 273
5.5.4 Node States That May Indicate Problems . . . . . . . . . . . . . . . . . . . . . . . . 274
5.6 Updating Running Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 276
5.6.1 Updating Running Nodes: Configuration With excludelistupdate . . . . . . . . 276
5.6.2 Updating Running Nodes: With cmsh Using imageupdate . . . . . . . . . . . . . . 284
5.6.3 Updating Running Nodes: With Base View Using the Update node Option . . . . 284
5.6.4 Updating Running Nodes: Considerations . . . . . . . . . . . . . . . . . . . . . . . 284
5.7 Adding New Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 285
5.7.1 Adding New Nodes With cmsh And Base View Add Functions . . . . . . . . . . . 285
5.7.2 Adding New Nodes With The Node Creation Wizard . . . . . . . . . . . . . . . . . 285
5.8 Troubleshooting The Node Boot Process . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 287

5.8.1 Node Fails To PXE Boot . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 287

5.8.2 Node-installer Logging . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 291
5.8.3 Provisioning Logging . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 292
5.8.4 Ramdisk Fails During Loading Or Sometime Later . . . . . . . . . . . . . . . . . . 292

5.8.5 Ramdisk Cannot Start Network . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 292

5.8.6 Node-Installer Cannot Create Disk Layout . . . . . . . . . . . . . . . . . . . . . . . 293
5.8.7 Node-Installer Cannot Start BMC (IPMI/iLO) Interface . . . . . . . . . . . . . . . . 296


**6** **User Management** **301**
6.1 Managing Users And Groups With Base View . . . . . . . . . . . . . . . . . . . . . . . . . 301
6.2 Managing Users And Groups With cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 303
6.2.1 Adding A User . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 303
6.2.2 Saving The Modified State . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 304
6.2.3 Editing Properties Of Users And Groups . . . . . . . . . . . . . . . . . . . . . . . . 305
6.2.4 Reverting To The Unmodified State . . . . . . . . . . . . . . . . . . . . . . . . . . . 308
6.2.5 Removing A User . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 308
6.3 Using An External LDAP Server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 309
6.3.1 External LDAP Server Replication . . . . . . . . . . . . . . . . . . . . . . . . . . . . 311
6.3.2 High Availability . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 313
6.4 Tokens And Profiles . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 314
6.4.1 Modifying Profiles . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 315
6.4.2 Creation Of Custom Certificates With Profiles, For Users Managed By BCM’s In
ternal LDAP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 316

6.4.3 Creation Of Custom Certificates With Profiles, For Users Managed By An External

LDAP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 319

6.4.4 Logging The Actions Of CMDaemon Users . . . . . . . . . . . . . . . . . . . . . . . 320
6.4.5 Creation Of Certificates For Nodes With cm-component-certificate . . . . . . . 321


**8** **Table of Contents**


**7** **Workload Management** **323**
7.1 Workload Managers Choices . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 323
7.2 Forcing Jobs To Run In A Workload Management System . . . . . . . . . . . . . . . . . . . 324
7.2.1 Disallowing User Logins To Regular Nodes Via cmsh . . . . . . . . . . . . . . . . . 324
7.2.2 Disallowing User Logins To Regular Nodes Via Base View . . . . . . . . . . . . . . 325
7.2.3 Disallowing Other User Processes Outside Of Workload Manager User Processes . 326
7.2.4 High Availability By Workload Managers . . . . . . . . . . . . . . . . . . . . . . . . 326
7.3 Installation Of Workload Managers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 329
7.3.1 Running cm-wlm-setup In CLI Mode . . . . . . . . . . . . . . . . . . . . . . . . . . 329
7.3.2 Running cm-wlm-setup As A TUI . . . . . . . . . . . . . . . . . . . . . . . . . . . . 332
7.3.3 Installation And Configuration Of Enroot And Pyxis With Slurm To Run Containerized Jobs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 336

7.3.4 Prolog And Epilog Scripts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 342
7.4 Enabling, Disabling, And Monitoring Workload Managers . . . . . . . . . . . . . . . . . . 346
7.4.1 Enabling And Disabling A WLM With Base View . . . . . . . . . . . . . . . . . . . 347
7.4.2 Enabling And Disabling A Workload Manager With cmsh . . . . . . . . . . . . . . 349
7.4.3 Monitoring The Workload Manager Services . . . . . . . . . . . . . . . . . . . . . . 354
7.5 Configuring And Running Individual Workload Managers . . . . . . . . . . . . . . . . . . 357
7.5.1 Configuring And Running Slurm . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 357
7.5.2 Configuring And Running PBS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 397
7.5.3 Installing, Configuring, And Running LSF . . . . . . . . . . . . . . . . . . . . . . . 406
7.6 Using Base View With Workload Management . . . . . . . . . . . . . . . . . . . . . . . . . 414
7.6.1 Jobs Display And Handling In Base View . . . . . . . . . . . . . . . . . . . . . . . . 415
7.6.2 Queues Display And Handling In Base View . . . . . . . . . . . . . . . . . . . . . . 415
7.7 Using cmsh With Workload Management . . . . . . . . . . . . . . . . . . . . . . . . . . . . 416
7.7.1 The jobs Submode In cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 418
7.7.2 Job Queue Display And Handling In cmsh : jobqueue Mode . . . . . . . . . . . . . 424
7.7.3 Nodes Drainage Status And Handling In cmsh . . . . . . . . . . . . . . . . . . . . . 425
7.8 Examples Of Workload Management Assignment . . . . . . . . . . . . . . . . . . . . . . . 428
7.8.1 Setting Up A New Category And A New Queue For It . . . . . . . . . . . . . . . . 428
7.8.2 Setting Up A Prejob Or Postjob Check . . . . . . . . . . . . . . . . . . . . . . . . . . 431
7.9 Power Saving With cm-scale . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 433
7.10 Cgroups . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 434
7.10.1 Cgroups Settings For Workload Managers . . . . . . . . . . . . . . . . . . . . . . . 434

7.11 Custom Node Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 439


7.11.1 Other PBS Professional Customizations Examples . . . . . . . . . . . . . . . . . . . 441


**8** **NVIDIA Base Command Manager Auto Scaler** **443**

8.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 443

8.1.1 Use Cases . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 443

8.1.2 Resource Constraints . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 444

8.1.3 Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 448
8.1.4 Workload Roles Assignment Limitations Per Node With cm-scale . . . . . . . . . 457
8.2 Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 457

8.2.1 The ScaleServer Role . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 457

8.2.2 Resource Providers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 459

8.2.3 Time Quanta Optimization . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 462


**Table of Contents** **9**


8.2.4 Fairsharing Priority Calculation And Node Management . . . . . . . . . . . . . . . 464
8.2.5 Engines . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 465

8.2.6 Trackers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 466

8.3 Examples Of cm-scale Use . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 473
8.3.1 Simple Static Node Provider Usage Example . . . . . . . . . . . . . . . . . . . . . . 473
8.3.2 Simple Dynamic Node Provider Usage Example . . . . . . . . . . . . . . . . . . . . 476
8.4 Further cm-scale Configuration And Examples . . . . . . . . . . . . . . . . . . . . . . . . 482
8.4.1 Dynamic Nodes Re-purposing . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 482
8.4.2 Pending Reasons . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 483

8.4.3 Locations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 484

8.4.4 Azure Storage Accounts Assignment . . . . . . . . . . . . . . . . . . . . . . . . . . 486
8.4.5 Uptake of HPC Jobs By Particular Types Of Nodes . . . . . . . . . . . . . . . . . . . 486
8.4.6 How To Exclude Unused Nodes From Being Stopped . . . . . . . . . . . . . . . . . 488
8.4.7 Prolog And Epilog Scripts With Auto Scaler . . . . . . . . . . . . . . . . . . . . . . 488
8.4.8 Queue Node Placeholders . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 489

8.4.9 Auto Scaling A Job On-premises To A Workload Manager And Kubernetes . . . . 490
8.4.10 AWS Spot Instances And Availability Zones . . . . . . . . . . . . . . . . . . . . . . 492

8.4.11 Auto Scaler Statistics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 493


**9** **Post-installation Software Management** **495**
9.1 NVIDIA Base Command Manager Packages, Their Naming Convention And Version . . 497
9.1.1 The packages Command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 499
9.1.2 BCM Package Point Release Versions And The cm-package-release-info Com
mand . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 499

9.2 Managing Packages On The Head Node . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 501
9.2.1 Managing RPM Or .deb Packages On The Head Node . . . . . . . . . . . . . . . . 501
9.2.2 Installation Of Packages On The Head Node That Are Not .deb And Not .rpm
Packages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 503
9.3 Kernel Management On A Head Node Or Image . . . . . . . . . . . . . . . . . . . . . . . . 503
9.3.1 Installing A Standard Distribution Kernel Into An Image Or On A Head Node . . 504
9.3.2 Excluding Kernels And Other Packages From Updates . . . . . . . . . . . . . . . . 505
9.3.3 Updating A Kernel In A Software Image . . . . . . . . . . . . . . . . . . . . . . . . 506
9.3.4 Setting Kernel Options For Software Images . . . . . . . . . . . . . . . . . . . . . . 507

9.3.5 Kernel Driver Modules . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 507

9.4 Managing A Package In A Software Image And Running It On Nodes . . . . . . . . . . . 509
9.4.1 Installing From Head Into The Image: Changing The Root Directory Into Which
The Packages Are Deployed . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 509
9.4.2 Installing From Head Into The Image: Updating The Node . . . . . . . . . . . . . . 511
9.4.3 Installing From Head Into The Image: Possible Issues When Using rpm --root,
yum --installroot Or chroot . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 512
9.4.4 Managing A Package In The Node-Installer Image . . . . . . . . . . . . . . . . . . . 513
9.5 Managing Non-RPM Software In A Software Image And Running It On Nodes . . . . . . 513
9.5.1 Managing The Software Directly On An Image . . . . . . . . . . . . . . . . . . . . . 513
9.5.2 Managing The Software Directly On A Node, Then Syncing Node-To-Image . . . 514
9.6 Creating A Custom Software Image . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 517
9.6.1 Creating A Base Distribution Archive From A Base Host . . . . . . . . . . . . . . . 517
9.6.2 Creating The Software Image With cm-create-image . . . . . . . . . . . . . . . . . 519


**10** **Table of Contents**


9.6.3 Configuring Local Repositories For Linux Distributions, And For The BCM Package Repository, For A Software Image . . . . . . . . . . . . . . . . . . . . . . . . . . 523
9.6.4 Creating A Custom Image From The Local Repository . . . . . . . . . . . . . . . . 525
9.7 Creating Images For Other Distributions And Architectures (Multidistro And Multiarch) 525
9.7.1 The cm-image Tool . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 526
9.7.2 Multidistro Examples: Provisioning From Rocky 8 Head Node To Ubuntu 24.04
Regular Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 529
9.7.3 Multiarch Example: Creating An Image From A Centos 8 Head Node For ARMv8
Architecture Regular Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 530


**10 Monitoring: Monitoring Cluster Devices** **535**
10.1 A Basic Monitoring Example And Action . . . . . . . . . . . . . . . . . . . . . . . . . . . . 535

10.1.1 Synopsis Of Basic Monitoring Example . . . . . . . . . . . . . . . . . . . . . . . . . 535
10.1.2 Before Using The Basic Monitoring Example—Setting Up The Pieces . . . . . . . . 536
10.1.3 Using The Basic Monitoring Example . . . . . . . . . . . . . . . . . . . . . . . . . . 537
10.2 Monitoring Concepts And Definitions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 540


10.2.1 Measurables . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 540

10.2.2 Enummetrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 543

10.2.3 Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 544

10.2.4 Health Check . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 545

10.2.5 Trigger . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 547

10.2.6 Action . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 547

10.2.7 Severity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 548

10.2.8 AlertLevel . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 548

10.2.9 Flapping . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 548

10.2.10 Data Producer . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 548

10.2.11 Conceptual Overview: The Main Monitoring Interfaces Of Base View . . . . . . . 552
10.3 Monitoring Visualization With Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . 553

10.3.1 The Monitoring Window . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 553
10.4 Monitoring Configuration With Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . 555
10.4.1 Monitoring Configuration: Data Producers . . . . . . . . . . . . . . . . . . . . . . . 556
10.4.2 Monitoring Configuration: Measurables . . . . . . . . . . . . . . . . . . . . . . . . . 558
10.4.3 Monitoring Configuration: Consolidators . . . . . . . . . . . . . . . . . . . . . . . . 560
10.4.4 Monitoring Configuration: Actions . . . . . . . . . . . . . . . . . . . . . . . . . . . 564
10.4.5 Monitoring Configuration: Triggers . . . . . . . . . . . . . . . . . . . . . . . . . . . 567
10.4.6 Monitoring Configuration: Health status . . . . . . . . . . . . . . . . . . . . . . . . 570
10.4.7 Monitoring Configuration: All Health Checks . . . . . . . . . . . . . . . . . . . . . 571
10.4.8 Monitoring Configuration: Standalone Monitored Entities . . . . . . . . . . . . . . 572
10.4.9 Monitoring Configuration: PromQL Queries . . . . . . . . . . . . . . . . . . . . . . 572
10.4.10 Monitoring Configuration: Resources . . . . . . . . . . . . . . . . . . . . . . . . . . 572
10.4.11 Monitoring Configuration: Types . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 573
10.5 The monitoring Mode Of cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 574


10.5.1 The action Submode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 575

10.5.2 The consolidator Submode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 577

10.5.3 The measurable Submode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 579

10.5.4 The setup Submode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 583

10.5.5 The standalone Submode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 589


**Table of Contents** **11**


10.5.6 The trigger Submode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 589
10.6 Obtaining Monitoring Data Values . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 592

10.6.1 Getting The List Of Measurables For An Entity: The measurables, metrics,

healthchecks And enummetrics Commands . . . . . . . . . . . . . . . . . . . . . . 592

10.6.2 On-Demand Metric Sampling And Health Checks . . . . . . . . . . . . . . . . . . . 593

10.6.3 The Latest Data And Counter Values—The latest*data And

latestmetriccounters Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . 596

10.6.4 Data Values Over A Period—The dumpmonitoringdata Command . . . . . . . . . 599
10.6.5 Monitoring Data Health Overview–The healthoverview Command . . . . . . . . 608
10.6.6 Monitoring Data About The Monitoring System—The monitoringinfo Command 609
10.6.7 Dropping Monitoring Data With The monitoringdrop Command . . . . . . . . . . 610
10.6.8 Monitoring Suspension And Resumption—The monitoringsuspend And
monitoringresume Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 611
10.6.9 Monitoring Pickup Intervals . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 612
10.7 Offloaded Monitoring . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 614
10.7.1 Why Offloaded Monitoring? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 614
10.7.2 Implementing Offloaded Monitoring . . . . . . . . . . . . . . . . . . . . . . . . . . 615
10.7.3 Background Details . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 615
10.7.4 Examining Offloaded Monitoring With monitoringoffloadinformation . . . . . 619

10.8 The User Portal . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 619


10.8.1 Accessing The User Portal . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 620
10.8.2 Setting A Common Username/Password For The User Portal . . . . . . . . . . . . 620

10.8.3 User Portal Access . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 621

10.8.4 User Portal Home Page . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 621
10.9 Cloud Job Tagging . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 622

10.10Event Viewer . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 623

10.10.1 Viewing Events In Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 623
10.10.2 Viewing Events In cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 624
10.10.3 Using The Event Bucket From The Shell For Events And For Tagging Device States 625
10.10.4 InfoMessages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 626
10.11Monitoring Location With GNSS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 628
10.12Monitoring Report Queries . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 628
10.12.1 Monitoring Report Queries In cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . 628
10.13Monitoring With nvsm . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 630


**11 Monitoring: Job Monitoring** **635**
11.1 Job Metrics Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 635

11.2 Job Metrics With Cgroups . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 635
11.3 Job Information Retention . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 636

11.4 Job Metrics Sampling Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 637

11.4.1 The Job Metrics Collection Processing Mechanism . . . . . . . . . . . . . . . . . . . 638
11.5 Job Monitoring In cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 639


**12 Monitoring: Job Accounting** **643**

12.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 643

12.2 Labeled Entities . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 643


12.2.1 Dataproducers For Labeled Entities . . . . . . . . . . . . . . . . . . . . . . . . . . . 644


**12** **Table of Contents**


12.2.2 PromQL And Labeled Entities . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 644

12.2.3 Job IDs And Labeled Entities . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 644

12.2.4 Measurables And Labeled Entities . . . . . . . . . . . . . . . . . . . . . . . . . . . . 644

12.3 PromQL Queries . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 645

12.3.1 The Default PromQL Queries... . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 645

12.3.2 ...And A Short Description Of Them . . . . . . . . . . . . . . . . . . . . . . . . . . . 646
12.3.3 Modifying The Default PromQL Query Properties . . . . . . . . . . . . . . . . . . . 650
12.3.4 An Example PromQL Query, Properties, And Disassembly . . . . . . . . . . . . . . 651
12.3.5 Aside: Getting Raw Values For A Prometheus Class Metric . . . . . . . . . . . . . . 652
12.3.6 ...An Example PromQL Query, Properties, And Disassembly (Continued) . . . . . 653
12.4 Parameterized PromQL Queries . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 654

12.4.1 Two Job GPU Metrics Used In PromQL Queries . . . . . . . . . . . . . . . . . . . . 656

12.5 Job Accounting In Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 657
12.5.1 Management And Use Of The Accounting Panel . . . . . . . . . . . . . . . . . . . . 658
12.6 PromQL Query Modes And Specification In Base View . . . . . . . . . . . . . . . . . . . . 660
12.7 Access Control For Workload Accounting And Reporting . . . . . . . . . . . . . . . . . . . 663

12.7.1 Defining Project Managers Using Internal User Management . . . . . . . . . . . . 663
12.7.2 Defining Project Managers Using External User Management . . . . . . . . . . . . 664
12.8 Drilldown Queries For Workload Accounting And Reporting . . . . . . . . . . . . . . . . 665

12.8.1 The drilldownoverview Command . . . . . . . . . . . . . . . . . . . . . . . . . . . 666

12.9 The grid Command For Job Accounting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 668

12.9.1 The grid Command Help Text . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 668
12.9.2 Some grid Command Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 668
12.9.3 The grid Command Time Specification . . . . . . . . . . . . . . . . . . . . . . . . . 670


**13 Monitoring: Job Chargeback** **673**

13.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 673


13.1.1 The Word “Chargeback” . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 673
13.1.2 Comparison Of Job Chargeback Monitoring Measurement With Other Monitoring

Measurements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 673

13.2 Job Chargeback Measurement . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 674

13.2.1 Predefined Job Chargebacks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 674
13.2.2 Setting A Custom Job Chargeback . . . . . . . . . . . . . . . . . . . . . . . . . . . . 675
13.2.3 The report And request Commands . . . . . . . . . . . . . . . . . . . . . . . . . . 676
13.3 Job Chargeback Background Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . 680


**14 Day-to-day Administration** **681**
14.1 Parallel Shells: pdsh And pexec . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 681


14.1.1 pdsh In The OS Shell . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 682

14.1.2 pexec In cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 685

14.1.3 pexec In Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 686
14.1.4 Using The -j|--join Option Of pexec In cmsh . . . . . . . . . . . . . . . . . . . . . 686

14.1.5 Other Parallel Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 687

14.2 Getting Support With BCM Issues, And Notifications For Release Updates . . . . . . . . . 687

14.2.1 The Support Portal For BCM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 688
14.2.2 Reporting Cluster Manager Diagnostics With cm-diagnose . . . . . . . . . . . . . . 689
14.2.3 Requesting Remote Support With request-remote-assistance . . . . . . . . . . . 690


**Table of Contents** **13**


14.2.4 Getting Notified About Updates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 692
14.3 Backups . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 692
14.3.1 Cluster Installation Backup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 692
14.3.2 Local Database And Data Backups And Restoration . . . . . . . . . . . . . . . . . . 693
14.4 Revision Control For Images . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 695

14.4.1 Btrfs: The Concept And Why It Works Well In Revision Control For Images . . . . 695
14.4.2 Btrfs Availability And Distribution Support . . . . . . . . . . . . . . . . . . . . . . . 696
14.4.3 Installing Btrfs To Work With Revision Control Of Images In BCM . . . . . . . . . 696
14.4.4 Using cmsh For Revision Control Of Images . . . . . . . . . . . . . . . . . . . . . . . 698
14.5 BIOS And Firmware Management . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 700

14.5.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 700

14.5.2 BIOS Management With BCM JSON Configuration Templates In Redfish . . . . . 701
14.5.3 Updating BIOS And Firmware Versions . . . . . . . . . . . . . . . . . . . . . . . . . 707
14.6 Hardware Match Check With The hardware-profile Data Producer . . . . . . . . . . . . 716

14.7 Serial Over LAN Console Access . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 717


14.7.1 Background Notes On Serial Console And SOL . . . . . . . . . . . . . . . . . . . . 717
14.7.2 SOL Console Configuration With Base View . . . . . . . . . . . . . . . . . . . . . . 719
14.7.3 SOL Console Configuration And Access With cmsh . . . . . . . . . . . . . . . . . . 719
14.7.4 The conman Serial Console Logger And Viewer . . . . . . . . . . . . . . . . . . . . . 720
14.8 Managing Raw Monitoring Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 724

14.8.1 Monitoring Subsystem Disk Usage With The monitoringinfo --storage Option 724
14.8.2 Estimating The Required Size Of The Storage Device . . . . . . . . . . . . . . . . . 724
14.8.3 Moving Monitoring Data Elsewhere . . . . . . . . . . . . . . . . . . . . . . . . . . . 725
14.8.4 Reducing Monitoring Data By Reducing Samples . . . . . . . . . . . . . . . . . . . 725
14.8.5 Deleting All Monitoring Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 725
14.9 Node Replacement . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 727
14.10Ansible And NVIDIA Base Command Manager . . . . . . . . . . . . . . . . . . . . . . . . 727

14.10.1 An Overview Of Ansible . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 727

14.10.2 A Simple Playbook Example . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 728
14.10.3 An Intermediate Playbook Example: Setting Up A Cluster For Demonstration Purposes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 730
14.10.4 A More Complicated Playbook Example: Creating An Edge Site And Related
Properties . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 731


**15 High Availability** **739**

15.0 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 739


15.0.1 Why Have High Availability? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 739
15.0.2 High Availability—For What Nodes? . . . . . . . . . . . . . . . . . . . . . . . . . . 739
15.0.3 High Availability Usually Uses Shared Storage . . . . . . . . . . . . . . . . . . . . . 740
15.0.4 Organization Of This Chapter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 740
15.1 HA Concepts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 740
15.1.1 Primary, Secondary, Active, Passive . . . . . . . . . . . . . . . . . . . . . . . . . . . 740
15.1.2 Monitoring The Active Head Node, Initiating Failover . . . . . . . . . . . . . . . . 740
15.1.3 Services In BCM HA Setups . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 741
15.1.4 Failover Network Topology . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 742
15.1.5 Shared Storage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 743
15.1.6 Guaranteeing One Active Head At All Times . . . . . . . . . . . . . . . . . . . . . . 744


**14** **Table of Contents**


15.1.7 Automatic Vs Manual Failover . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 745

15.1.8 HA And Cloud Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 746

15.1.9 HA Using Virtual Head Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 746
15.2 HA Setup Procedure Using cmha-setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 746

15.2.1 Preparation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 747
15.2.2 Failover Cloning (Replacing A Passive Head) . . . . . . . . . . . . . . . . . . . . . . 749
15.2.3 Shared Storage Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 752
15.2.4 Automated Failover And Relevant Testing . . . . . . . . . . . . . . . . . . . . . . . 753
15.3 Running cmha-setup Without ncurses, Using An XML Specification . . . . . . . . . . . . . 754

15.3.1 Why Run It Without ncurses? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 754
15.3.2 The Syntax Of cmha-setup Without ncurses . . . . . . . . . . . . . . . . . . . . . . 754
15.3.3 Example cmha-setup Run Without ncurses . . . . . . . . . . . . . . . . . . . . . . . 755
15.4 Managing HA . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 756

15.4.1 Changing An Existing Failover Configuration . . . . . . . . . . . . . . . . . . . . . 756
15.4.2 cmha Utility . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 756

15.4.3 States . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 760

15.4.4 Failover Action Decisions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 760

15.4.5 Keeping Head Nodes In Sync . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 761
15.4.6 High Availability Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 763
15.4.7 Viewing Failover Via Base View . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 765
15.4.8 Re-cloning A Head Node . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 765
15.5 HA For Regular Nodes And Edge Director Nodes . . . . . . . . . . . . . . . . . . . . . . . 766

15.5.1 Why Have HA On Non-Head Nodes? . . . . . . . . . . . . . . . . . . . . . . . . . . 766
15.5.2 Comparing HA For Head Nodes, Regular Nodes And Edge Director Nodes . . . . 766
15.5.3 Setting Up A Regular Node HA Service . . . . . . . . . . . . . . . . . . . . . . . . . 767
15.5.4 The Sequence Of Events When Making Another HA Regular Node Active . . . . . 771
15.6 HA And Workload Manager Jobs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 772


**16 The Jupyter Notebook Environment Integration** **773**

16.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 773

16.2 Jupyter Environment Installation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 774

16.2.1 Jupyter Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 775
16.2.2 Jupyter Architecture . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 775
16.2.3 Verifying Jupyter Installation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 777
16.2.4 Login Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 777
16.2.5 JupyterHub Screen After Login . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 779
16.3 Jupyter Notebook Examples . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 780
16.4 Jupyter Kernels . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 781

16.4.1 Jupyter Kernel Provisioning Kernels . . . . . . . . . . . . . . . . . . . . . . . . . . . 782

16.4.2 Tunables For Kernel Provisioners . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 784

16.5 Jupyter Kernel Creator Extension . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 786

16.5.1 BCM Predefined Kernel Templates . . . . . . . . . . . . . . . . . . . . . . . . . . . . 787
16.5.2 Jupyter Kernel Starter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 792
16.5.3 Running Jupyter Kernels With Two Factor Authentication . . . . . . . . . . . . . . 793
16.5.4 Running Jupyter Kernels With Kubernetes . . . . . . . . . . . . . . . . . . . . . . . 794
16.5.5 Running Jupyter Kernels Based On NGC Containers . . . . . . . . . . . . . . . . . 794
16.5.6 Running Jupyter Kernels With Workload Managers . . . . . . . . . . . . . . . . . . 797


**Table of Contents** **15**


16.6 Jupyter Kernel Creator Extension Customization . . . . . . . . . . . . . . . . . . . . . . . . 798

16.6.1 Kernel Template Parameters Definition . . . . . . . . . . . . . . . . . . . . . . . . . 798
16.6.2 Kernel Template Parameters Usage . . . . . . . . . . . . . . . . . . . . . . . . . . . 801
16.6.3 Filtering Out Irrelevant Templates From The Interface For Users . . . . . . . . . . . 802
16.7 Jupyter VNC Extension . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 803

16.7.1 What Is Jupyter VNC Extension About? . . . . . . . . . . . . . . . . . . . . . . . . . 803
16.7.2 Enabling User Lingering . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 804
16.7.3 Starting A VNC Session With The Jupyter VNC Extension . . . . . . . . . . . . . . 804
16.7.4 Running Examples And Applications In The VNC Session With The Jupyter VNC

Extension . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 806

16.8 Jupyter WLM Magic Extension . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 807
16.9 Jupyter Kubernetes Operators Manager . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 809


16.9.1 Overview Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 810

16.9.2 Jupyter Kernel Overview Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 811
16.9.3 Jobs Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 812

16.9.4 Pods Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 813

16.9.5 PVCs Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 815

16.9.6 PSQL Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 817

16.9.7 Spark Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 819

16.9.8 Events Tab . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 827

16.10Jupyter Environment Removal . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 828


**A Generated Files** **829**

A.1 System Configuration Files Created Or Modified By CMDeamon On Head Nodes . . . . 829
A.2 System Configuration Files Created Or Modified Directly On The Node . . . . . . . . . . 832
A.2.1 Options To filewriteinfo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 833
A.2.2 Files Created On Regular Nodes By CMDaemon . . . . . . . . . . . . . . . . . . . . 834
A.2.3 Files Created On Regular Nodes By The Node-Installer . . . . . . . . . . . . . . . . 835
A.3 Files Not Generated, But Installed In RHEL And Derivatives . . . . . . . . . . . . . . . . . 836


**B** **Bright Computing Public Key** **841**


**C CMDaemon Configuration File Directives** **843**


**D Disk Partitioning And RAID Configuration** **875**
D.1 Structure Of Partitioning Definition—The Global Partitioning XML Schema Definition File 875
D.2 Structure Of Hardware RAID Definition—The Hardware RAID XML Schema Definition

File . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 883

D.3 Example: Default Node Partitioning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 886
D.4 Example: Hardware RAID Configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . 888

D.4.1 RAID level 0 And RAID 10 Example . . . . . . . . . . . . . . . . . . . . . . . . . . . 888
D.5 Example: Software RAID . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 890
D.6 Example: Software RAID With Swap . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 891
D.7 Example: Logical Volume Manager . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 891
D.8 Example: Logical Volume Manager With RAID 1 . . . . . . . . . . . . . . . . . . . . . . . . 893
D.9 Example: Diskless . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 894
D.10 Example: Semi-diskless . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 895


**16** **Table of Contents**


D.11 Example: Preventing Accidental Data Loss . . . . . . . . . . . . . . . . . . . . . . . . . . . 895
D.12 Example: Using Custom Assertions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 896
D.13 Example: Software RAID1 With One Big Partition . . . . . . . . . . . . . . . . . . . . . . . 897
D.14 Example: Software RAID5 With One Big Partition . . . . . . . . . . . . . . . . . . . . . . . 899
D.15 Example: Software RAID1 With Standard Partitioning . . . . . . . . . . . . . . . . . . . . . 901
D.16 Example: Software RAID5 With Standard Partitioning . . . . . . . . . . . . . . . . . . . . . 904
D.17 Example: LUKS Disk Encryption With Standard Partitioning . . . . . . . . . . . . . . . . . 906


D.17.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 907

D.17.2 Node Provisioned Over The Network: Encrypted Partition XML Example . . . . . 907
D.17.3 Standalone Node: Encrypted Partition XML Example . . . . . . . . . . . . . . . . . 910
D.17.4 Changing A Passphrase On An Encrypted Node . . . . . . . . . . . . . . . . . . . . 911


**E** **Example** initialize **And** finalize **Scripts** **913**
E.1 When Are They Used? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 913
E.2 Accessing From Base View And cmsh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 913
E.3 Environment Variables Available To initialize And finalize Scripts . . . . . . . . . . . 914
E.4 Using Environment Variables Stored In Multiple Variables . . . . . . . . . . . . . . . . . . 917
E.5 Storing A Configuration To A Filesystem . . . . . . . . . . . . . . . . . . . . . . . . . . . . 918
E.5.1 Storing With Initialize Scripts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 918
E.5.2 Ways Of Writing A Finalize Script To Configure The Destination Nodes . . . . . . 918
E.5.3 Restricting The Script To Nodes Or Node Categories . . . . . . . . . . . . . . . . . 921


**F** **Workload Managers Quick Reference** **923**

F.1 Slurm . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 923

F.2 PBS Professional . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 925


**G Metrics, Health Checks, Enummetrics, And Actions** **927**

G.1 Metrics And Their Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 927


G.1.1 Regular Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 928

G.1.2 NFS Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 935

G.1.3 InfiniBand Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 937
G.1.4 Monitoring System Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 939
G.1.5 CPU Metrics Sampled By The CPUSampler And GPUSampler . . . . . . . . . . . . 941

G.1.6 GPU Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 941

G.1.7 GPU Profiling Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 943
G.1.8 Job Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 944

G.1.9 IPMI Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 951

G.1.10 Redfish Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 952

G.1.11 SMART Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 953

G.1.12 Prometheus Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 954

G.1.13 NetQ Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 956

G.1.14 Kubernetes Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 957

G.1.15 Parameters For Metrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 967

G.2 Health Checks And Their Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 970

G.2.1 Regular Health Checks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 971

G.2.2 GPU Health Checks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 977

G.2.3 Redfish Health Checks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 978


**Table of Contents** **17**


G.2.4 NetQ Health Checks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 978

G.2.5 Parameters For Health Checks . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 979

G.3 Enummetrics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 980

G.4 Actions And Their Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 982

G.4.1 Actions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 982

G.4.2 Parameters For A Monitoring Action . . . . . . . . . . . . . . . . . . . . . . . . . . 982


**H Workload Manager Configuration Files Updated By CMDaemon** **985**

H.1 Slurm . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 985

H.2 PBS Professional/OpenPBS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 985

H.3 LSF . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 985


**I** **Changing The LDAP Password** **987**
I.1 Setting A New Password For The LDAP Server . . . . . . . . . . . . . . . . . . . . . . . . . 987
I.2 Setting The New Password In cmd.conf . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 987
I.3 Checking LDAP Access . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 988


**J** **Tokens** **989**


**K Understanding Consolidation** **1005**

K.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1005

K.2 What Is Consolidation? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1005

K.3 Raw Data And Consolidation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1005

K.4 A Demonstration Of The Output . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1006


**L** **Node Execution Filters And Execution Multiplexers** **1009**
L.1 Data Producers: Default Configuration For Running And Sampling . . . . . . . . . . . . . 1010
L.1.1 Nodes That Data Producers Are Running On By Default—The nodes Command . 1010
L.1.2 Nodes That Data Producers Target By Default—The samplenow Command . . . . 1010
L.2 Data Producers: Configuration For Running And Targeting . . . . . . . . . . . . . . . . . . 1011
L.2.1 Custom Metrics From The fm.sh Custom Script . . . . . . . . . . . . . . . . . . . . 1011
L.3 Replacing A Resource With An Explicit Node Specification . . . . . . . . . . . . . . . . . . 1013
L.4 Excessive Sampling . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1014
L.5 Not Just For Nodes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1015

L.6 Lua Node Execution Filters . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1015


**M A Tree View Of** cmsh **1019**

M.1 Modes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1019


**N BCM And NVIDIA AI Enterprise** **1025**
N.0.1 Certified Features Of BCM For NVIDIA AI Enterprise . . . . . . . . . . . . . . . . . 1025
N.0.2 NVIDIA AI Enterprise Compatible Servers . . . . . . . . . . . . . . . . . . . . . . . 1025
N.0.3 NVIDIA Software Versions Supported . . . . . . . . . . . . . . . . . . . . . . . . . . 1025
N.0.4 NVIDIA AI Enterprise Product Support Matrix . . . . . . . . . . . . . . . . . . . . 1025


#### **Preface**

Welcome to the _Administrator Manual_ for the NVIDIA Base Command Manager 11 (BCM) environment.


**0.1** **Quickstart**


For readers who want to get a cluster up and running as quickly as possible with NVIDIA Base Command Manager, there is a quickstart installation guide in Chapter 1 of the _Installation Manual_ .


**0.2** **About This Manual**


The rest of this manual is aimed at helping system administrators configure, understand, and manage a
cluster running BCM so as to get the best out of it.
The _Administrator Manual_ covers administration topics which are specific to the BCM environment.
Readers should already be familiar with basic Linux system administration, which the manual does not
generally cover. Aspects of system administration that require a more advanced understanding of Linux
concepts for clusters are explained appropriately.
This manual is not intended for users interested only in interacting with the cluster to run compute
jobs. The _User Manual_ is intended to get such users up to speed with the user environment and workload
management system.


**0.3** **About The Manuals In General**


Regularly updated versions of the NVIDIA Base Command Manager 11 manuals are available on updated clusters by default at /cm/shared/docs/cm . The latest updates are always online at [https:](https://docs.nvidia.com/base-command-manager)
[//docs.nvidia.com/base-command-manager](https://docs.nvidia.com/base-command-manager) .


  - The _Administrator Manual_ describes the general administration of the cluster.


  - The _Installation Manual_ describes installation procedures.


  - The _User Manual_ describes the user environment and how to submit jobs for the end user.


  - The _Cloudbursting Manual_ describes how to deploy the cloud capabilities of the cluster.


  - The _Developer Manual_ has useful information for developers who would like to carry out programming tasks with BCM.


  - The _Edge Manual_ describes how to install and configure machine learning capabilities with BCM.


  - The _Containerization Manual_ describes how to manage containers with BCM.


  - The _NVIDIA Mission Control Manual_ describes NVIDIA Mission Control capabilities and integration with BCM.


If the manuals are downloaded and kept in one local directory, then in most pdf viewers, clicking
on a cross-reference in one manual that refers to a section in another manual opens and displays that
section in the second manual. Navigating back and forth between documents is usually possible with
keystrokes or mouse clicks.
For example: <Alt>-<Backarrow> in Acrobat Reader, or clicking on the bottom leftmost navigation
button of xpdf, both navigate back to the previous document.


**20** **Table of Contents**


The manuals constantly evolve to keep up with the development of the BCM environment and the
addition of new hardware and/or applications. The manuals also regularly incorporate feedback from
administrators and users, who can submit comments, suggestions or corrections via the website
[https://enterprise-support.nvidia.com/s/create-case](https://enterprise-support.nvidia.com/s/create-case)
Section 14.2 of the _Administration Manual_ has more details on submitting an issue.


**0.4** **Getting Administrator-Level Support**


Support for BCM subscriptions from version 10 onwards is available via the NVIDIA Enterprise Support
page at:
[https://www.nvidia.com/en-us/support/enterprise/](https://www.nvidia.com/en-us/support/enterprise/)
Section 14.2 has more details on working with support.


**0.5** **Getting Professional Services**


The BCM support team normally differentiates between


  - regular support (customer has a question or problem that requires an answer or resolution), and


  - professional services (customer asks for the team to do something or asks the team to provide
some service).


Professional services can be provided via the NVIDIA Enterprise Services page at:
[https://www.nvidia.com/en-us/support/enterprise/services/](https://www.nvidia.com/en-us/support/enterprise/services/)