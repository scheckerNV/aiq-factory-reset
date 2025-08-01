# Rank 1 Pid 180379 on node002 device 0 [0x00] Tesla V100-SXM3-32GB

node001:175945:175945 [0] NCCL INFO Bootstrap : Using ens3:10.141.0.5<0>
node001:175945:175945 [0] NCCL INFO NET/Plugin : No plugin found (libnccl-net.so), using internal implementation
node001:175945:175945 [0] NCCL INFO NCCL_IB_DISABLE set by environment to 1.
node001:175945:175945 [0] NCCL INFO NET/Socket : Using [0]ens3:10.141.0.5<0>
node001:175945:175945 [0] NCCL INFO Using network Socket

NCCL version 2.11.4+cuda11.6

node002:180379:180379 [0] NCCL INFO Bootstrap : Using ens3:10.141.0.6<0>
node002:180379:180379 [0] NCCL INFO NET/Plugin : No plugin found (libnccl-net.so), using internal implementation
node002:180379:180379 [0] NCCL INFO NCCL_IB_DISABLE set by environment to 1.
node002:180379:180379 [0] NCCL INFO NET/Socket : Using [0]ens3:10.141.0.6<0>
node002:180379:180379 [0] NCCL INFO Using network Socket

node002:180379:182573 [0] NCCL INFO Trees [0] -1/-1/-1->1->0 [1] 0/-1/-1->1->-1

node001:175945:177561 [0] NCCL INFO Channel 00/02 : 0 1

node001:175945:177561 [0] NCCL INFO Channel 01/02 : 0 1

node001:175945:177561 [0] NCCL INFO Trees [0] 1/-1/-1->0->-1 [1] -1/-1/-1->0->1

node001:175945:177561 [0] NCCL INFO Channel 00 : 1[60] -> 0[60] [receive] via NET/Socket/0

node002:180379:182573 [0] NCCL INFO Channel 00 : 0[60] -> 1[60] [receive] via NET/Socket/0

node001:175945:177561 [0] NCCL INFO Channel 01 : 1[60] -> 0[60] [receive] via NET/Socket/0

node002:180379:182573 [0] NCCL INFO Channel 01 : 0[60] -> 1[60] [receive] via NET/Socket/0

node001:175945:177561 [0] NCCL INFO Channel 00 : 0[60] -> 1[60] [send] via NET/Socket/0

node002:180379:182573 [0] NCCL INFO Channel 00 : 1[60] -> 0[60] [send] via NET/Socket/0

node001:175945:177561 [0] NCCL INFO Channel 01 : 0[60] -> 1[60] [send] via NET/Socket/0

node002:180379:182573 [0] NCCL INFO Channel 01 : 1[60] -> 0[60] [send] via NET/Socket/0

node001:175945:177561 [0] NCCL INFO Connected all rings
node002:180379:182573 [0] NCCL INFO Connected all rings

node001:175945:177561 [0] NCCL INFO Connected all trees

node001:175945:177561 [0] NCCL INFO threadThresholds 8/8/64 | 16/8/64 | 8/8/512

node001:175945:177561 [0] NCCL INFO 2 coll channels, 2 p2p channels, 1 p2p channels per peer

node002:180379:182573 [0] NCCL INFO Connected all trees

node002:180379:182573 [0] NCCL INFO threadThresholds 8/8/64 | 16/8/64 | 8/8/512

node002:180379:182573 [0] NCCL INFO 2 coll channels, 2 p2p channels, 1 p2p channels per peer

node001:175945:177561 [0] NCCL INFO comm 0x1551f0001000 rank 0 nranks 2 cudaDev 0 busId 60 - Init COMPLETE

#

# out-of-place in-place

# size count type redop time algbw busbw error time algbw busbw error

# (B) (elements) (us) (GB/s) (GB/s) (us) (GB/s) (GB/s)

node001:175945:175945 [0] NCCL INFO Launch mode Parallel

node002:180379:182573 [0] NCCL INFO comm 0x1551f8001000 rank 1 nranks 2 cudaDev 0 busId 60 - Init COMPLETE

1048576 262144 float sum 1491.5 0.70 0.70 0e+00 1421.3 0.74 0.74 0e+00

2097152 524288 float sum 3077.5 0.68 0.68 0e+00 2568.8 0.82 0.82 0e+00

4194304 1048576 float sum 4617.3 0.91 0.91 0e+00 4622.5 0.91 0.91 0e+00

8388608 2097152 float sum 9483.1 0.88 0.88 0e+00 8911.9 0.94 0.94 0e+00

16777216 4194304 float sum 17516 0.96 0.96 0e+00 18613 0.90 0.90 0e+00

33554432 8388608 float sum 34799 0.96 0.96 0e+00 41837 0.80 0.80 0e+00

67108864 16777216 float sum 99790 0.67 0.67 0e+00 83126 0.81 0.81 0e+00

134217728 33554432 float sum 204614 0.66 0.66 0e+00 199530 0.67 0.67 0e+00

268435456 67108864 float sum 319701 0.84 0.84 0e+00 341630 0.79 0.79 0e+00

536870912 134217728 float sum 608809 0.88 0.88 0e+00 683016 0.79 0.79 0e+00

1073741824 268435456 float sum 1337187 0.80 0.80 0e+00 1247369 0.86 0.86 0e+00

2147483648 536870912 float sum 2638741 0.81 0.81 0e+00 2743454 0.78 0.78 0e+00

4294967296 1073741824 float sum 5996381 0.72 0.72 0e+00 5430549 0.79 0.79 0e+00

# Out of bounds values : 0 OK


**342** **Workload Management**


# Avg bus bandwidth : 0.810575

#


The test demonstrates the usage of PMIX, MPI, and GPU in Enroot containers on multiple nodes. In
the preceding example, 2 nodes with 1 GPU on each is requested by the job. For better results the cluster
administrator can tune the test parameters.
It should be noted that the image is quite large, and requires enough free space under /var . Also, the
transfer timeout ( ENROOT_TRANSFER_TIMEOUT ) in enroot.conf must be large enough to download such
a large container image to the compute nodes. A value of at least 600 seconds is recommended.
If there are issues when executing MPI jobs with PMIX, then to help debug the issues the Pyxis documentation ( [https://github.com/NVIDIA/pyxis/wiki/Setup](https://github.com/NVIDIA/pyxis/wiki/Setup) ) suggests setting up the following environment variables:


 - PMIX_MCA_ptl=^usock


 - PMIX_MCA_psec=none


 - PMIX_SYSTEM_TMPDIR=/var/empty


 - PMIX_MCA_gds=hash (as configured on page 340)


This configuration change is typically carried out in the software image of the regular nodes. For
example, for a node category called default :


[root@basecm11 ~]# category=default

[root@basecm11 ~]# cat <<EOF >> /cm/images/${category}/etc/default/slurmd

PMIX_MCA_ptl=^usock

PMIX_MCA_psec=none
PMIX_SYSTEM_TMPDIR=/var/empty

PMIX_MCA_gds=hash

EOF

[root@basecm11 ~]# systemctl restart slurmd

[root@basecm11 ~]# cmsh -c "device; imageupdate -c ${category} -w"


**7.3.4** **Prolog And Epilog Scripts**

**What Prolog And Epilog Scripts Do**
The workload manager runs prolog scripts before job execution, and epilog scripts after job execution.
The purpose of these scripts can include:


  - checking if a node is ready before submitting a job execution that may use it


  - preparing a node in some way to handle the job execution


  - cleaning up resources after job execution has ended.


The administrator can run custom prolog or epilog scripts for the queues from CMDaemon for LSF,
by setting such scripts in the Base View or cmsh front ends.


**Example**


[basecm11->wlm[lsf]->jobqueue]% use normal

[basecm11->wlm[lsf]->jobqueue[normal]]% show | grep -i epilog
Prolog/Epilog user root

Epilog
Host epilog /cm/local/apps/cmd/scripts/epilog


For PBS and Slurm, there are global prolog and epilog scripts, but editing them is not recommended.
Indeed, in order to discourage editing them, the scripts cannot be set via the cluster manager front ends.
Instead the scripts must be placed by the administrator in the software image, and the relevant nodes
updated from the image.


**7.3 Installation Of Workload Managers** **343**


**Detailed Workings Of Prolog And Epilog Scripts**
Even though it is not recommended, some administrators may nonetheless wish to link and edit the
scripts directly for their own needs, outside of the Base View or cmsh front ends. A more detailed
explanation of how the prolog scripts work therefore follows:
When a workload manager is configured via cm-wlm-setup or via the Base View setup wizard,
then the workload manager is configured to run the generic prolog located in /cm/local/apps/cmd/
scripts/prolog, and the generic epilog located in /cm/local/apps/cmd/scripts/epilog . The generic
prolog and epilog scripts call a sequence of scripts for a particular workload manager in special directories. The directories have paths in the format:


1. /cm/local/apps/< _workload manager_ >/var/prologs/


2. /cm/local/apps/< _workload manager_ >/var/epilogs/


In these directories, scripts are stored with names that have suffixes and prefixes associated with
them that make them run in special ways, as follows:


 - **suffixes used in the prolog/epilog directory:**


_◦_ -prejob script runs prior to all jobs


 - **prefixes used in the prolog/epilog directory:**


_◦_ 00- to


_◦_ 99

Number prefixes determine the order of script execution, with scripts with a lower number running earlier.


The script names can therefore look like:


**Example**


 - 01-prolog-prejob


 - 10-prolog-prejob


Return values for the prolog/epilog scripts have these meanings:


 - 0 : the next script in the directory is run.


 - _A non-zero return value_ : no further scripts are executed from the prolog/epilog directory.


Often, the script in a prolog/epilog directory is not a real script but a symlink, with the symlink
going to a real file located in a different directory. The general script is then able to take care of what is
expected of the symlink. The name of the symlink, and destination file, usually hints at what the script
is expected to do.
For example, if any health checks are marked to run as prejob checks during cm-wlm-setup configuration, then each of the PBS workload manager variants use the symlink 01-prolog-prejob within the
prolog directory /cm/local/apps/< _workload manager_ >/var/prologs/ . The symlink links to the script
/cm/local/apps/cmd/scripts/prolog-prejob . In this case, the script is expected to run prior to the
job.


**Example**


**344** **Workload Management**


[root@basecm11 apps]# pwd
/cm/local/apps

[root@basecm11 apps]# ls -l *pbs*/var/prologs/
openpbs/var/prologs/:

total 0

lrwxrwxrwx 1 root root ... 01-prolog-prejob -> /cm/local/apps/cmd/scripts/prolog-prejob


pbspro/var/prologs/:

total 0

lrwxrwxrwx 1 root root ... 01-prolog-prejob -> /cm/local/apps/cmd/scripts/prolog-prejob


Epilog scripts (which run after a job run) have the location /cm/local/apps/< _workload man-_
_ager_ >/var/epilogs/ . Epilog script names follow the same execution sequence pattern as prolog script

names.

It should be noted that that the 01-prolog-prejob symlink is created and removed by BCM on each
compute node where prejob is enabled in the workload manager entity. Each such entity provides a
Enable Prejob parameter that affects the symlink existence:


**Example**


[head->wlm[openpbs]]% get enableprejob

yes

[head->wlm[openpbs]]%


This parameter is set to yes by cm-wlm-setup when at least one health check is selected as a prejob one. If
any healthcheck was configured as a prejob check before cm-wlm-setup execution, and the administrator
had a checkmark for that health check, then the prejob is considered enabled.


**Workload Manager Configuration For Prolog And Epilog Scripts**
BCM configures generic prologs and epilogs during workload manager setup with cm-wlm-setup . The
administrator can configure prologs and epilogs using appropriate parameters in the configuration of
the workload managers, by creating the symlinks in the local prologs and epilogs directories.
Generic prologs and epilogs are configured by default to run on job compute nodes (one run per
each node per job) for Slurm, PBS variants and LSF.
The following parameters for prologs and epilogs can be configured with cmsh or Base View:


 - **Slurm**


**–**
Prolog Slurmctld : the fully qualified path of a program to execute before granting a new
job allocation. The program is executed on the same node where the slurmserver role is
assigned. The parth corresponds to the PrologSlurmctld parameter in slurm.conf .


**–**
Epilog Slurmctld : the fully qualified path of a program to execute upon termination of a
job allocation. The program is executed on the same node where the slurmserver role is
assigned. Corresponds with the EpilogSlurmctld parameter in slurm.conf .


**–**
Prolog : the fully qualified path of a program to execute on job compute nodes before granting
a new job or step allocation. The program corresponds to the Prolog parameter, and by
default points to the generic prolog. This prolog runs on every node of the job if the Prolog
flags parameter contains the flag Alloc (the default value), otherwise it is executed only on
the first node of the job.


**–**
Epilog : the fully qualified path of a program to execute on job compute nodes when the job
allocation is released.


 - **LSF**


**7.3 Installation Of Workload Managers** **345**


**–**
Prolog : the fully qualified path of a program to execute on the LSF server node on job allocation. As an LSF queue parameter, it corresponds to the PRE_EXEC parameter in lsb.queues .


**–**
Epilog : the fully qualified path of a program to execute on the LSF server node on job allocation release. As an LSF queue parameter, it corresponds to the POST_EXEC parameter in
lsb.queues


**–**
Host prolog : the fully qualified path of a program to execute on each node of a job before
the job is started. Corresponds to the HOST_PRE_EXEC parameter in lsb.queues . By default it
is configured to run the generic prolog


**–**
Host epilog : the fully qualified path of a program to execute on each node of a job after the
job is finished. Corresponds to the HOST_POST_EXEC parameter in lsb.queues . By default it
is configured to run the generic epilog.


 - **PBS variants**


**–** Pelogs : prolog and epilog hooks that emulate the classic PBS _p_ rologue and _e_ pilogue scripts
located in the pbs_mom directory. The pelogs are configured in the appropriate workload
manager instance, within pelogs mode when configuring the PBS cluster entity. For example,
in cmsh :


**Example**


[basecm11]% wlm use openpbs

[basecm11->wlm[openpbs]]% pelogs

[basecm11->wlm[openpbs]->pelogs]% list
Name (key) Enabled Order

---------- -------- -------
cm_epilog yes 99

cm_prolog yes 1

[basecm11->wlm[openpbs]->pelogs]%

[basecm11->wlm[openpbs]->pelogs]% show cm_prolog

Parameter Value

-------------------------------- -----------------------------------------------
Enabled yes

Name cm_prolog

Events execjob_begin
Path /cm/shared/apps/pbspro/var/cm/cm-pelog-hook.py

Default action RERUN

Enable parallel yes

Verbose user output no

Torque compatible no

Order 1

Alarm 35

Debug no

[basecm11->wlm[openpbs]->pelogs]% show cm_epilog

Parameter Value

-------------------------------- -----------------------------------------------
Enabled yes

Name cm_epilog

Events execjob_end
Path /cm/shared/apps/pbspro/var/cm/cm-pelog-hook.py

Default action RERUN

Enable parallel yes

Verbose user output no

Torque compatible no

Order 99


**346** **Workload Management**


Alarm 35

Debug no

[basecm11->wlm[openpbs]->pelogs]%


The parameters of each pelog correspond to appropriate parameters of PBS hooks:


       - [Name: hook name that will be used in PBS]


       - [Enabled: flag to enable the hook in PBS]


       - [Events: list of PBS events that the hook will run on]


       - [Path: path to the hook script that will be imported to PBS in case the hook is not found.]
The script will not be imported if a hook with the same name already exists in PBS

       - [Order: the hook execution order]


       - [Alarm: the hook alarm time (timeout), in seconds]


Additional parameters related to the prolog and epilog hooks only are:


       - [Default action: The PBS default action when a prolog or epilog fails]


       - [Enable parallel: enable parallel prologues and epilogues, that run on sister moms]


       - [Verbose user output: provide verbose hook output to the user’s] [ .o] [/] [.e] [ file]


       - [Torque compatible: make torque compatible from prolog/epilog command line argu-]
ments point of view


By default, two pelogs are added. These are to run the generic prolog and the generic epilog.
If needed, the administrator can add more pelog hooks that will run on different events.


**7.4** **Enabling, Disabling, And Monitoring Workload Managers**


**Enabling And Disabling A WLM**
A WLM can be disabled for all nodes with cm-wlm-setup . Disabling the WLM means the workload
management services are stopped by removing roles, and removing the WLM cluster object.
Alternatively, a WLM can be enabled or disabled by the administrator via role addition and role
removal with Base View or cmsh . This is described further on in this section.


**Multiple WLM instances of the same type:** Versions of NVIDIA Base Command Manager prior to 9.0
already had the ability to have different workload managers run at the same time. However, NVIDIA
Base Command Manager version 9.0 introduced the additional ability to run many workload managers
of the same kind at the same time.


**Example**


Two WLM instances, Slurm and OpenPBS, are already running at the same time in the cluster, with each
WLM assigned to one category. Then, BCM can start up a third WLM instance, such as another Slurm
WLM instance. These WLM instances are alternatively called WLM clusters, because they effectively
allow one cluster to function as many separate clusters as far as running WLMs is concerned.
From the Base View or cmsh point of view a WLM consists of


  - a WLM server, usually on the head node


  - WLM clients, usually on the compute nodes


For the administrator, enabling or disabling the servers or clients is then simply a matter of assigning or unassigning a particular WLM server or client role on the head or compute nodes, as deemed
appropriate.
The administrator typically also sets up an appropriate WLM environment module ( slurm, openpbs,
pbspro, lsf ), so that it is loaded up for the end user (section 2.2.3).


**7.4 Enabling, Disabling, And Monitoring Workload Managers** **347**


**7.4.1** **Enabling And Disabling A WLM With Base View**
A particular WLM package may be installed, but the WLM may not be enabled. This can happen, for
example, if disabling a WLM that was previously enabled.
If a WLM instance exists, then the WLM client, submission, and server roles can be enabled or disabled from Base View by assigning or removing the appropriate roles to nodes, categories, or configuration overlays. Within the role, the properties of the WLM may be further configured by setting options.


**Workload Manager Role Assignment To An Individual Node With Base View**
**Workload Manager Server** The following roles are WLM roles that can be assigned to a node:


  - server


  - submit


  - accounting (for the Slurm WLM only, to configure and run the slurmdbd service)


  - client


For example, a Slurm server role can be assigned to a head node, basecm11, via the navigation path:


Devices  - Head Nodes[basecm11]  - Edit  - Settings  - Role  - Role list[ADD]  - SlurmServerRole


Figure 7.14: Workload management role assignment on a head node


**348** **Workload Management**


The role window for the server then opens up, and allows role options to be set for the workload
manager server. For example, for Slurm, a builtin or backfill option can be set for the Scheduler
parameter. The workload manager server role is then saved with the selected options (figure 7.15).
To have the server start up on non-head nodes (but not for a head node), the imageupdate command
(section 5.6.2) can be run. The workload manager server process and any associated schedulers then
automatically start up.


Figure 7.15: Workload management role assignment options on a head node


**Workload Manager Client** Similarly, the workload manager client process can be enabled on a node
or head node by having the workload manager client role assigned to it. Some basic options can be set
for the client role right away.
Saving the role, and then running imageupdate (section 5.6.2), automatically starts up the client
process with the options chosen, and managed by CMDaemon.


**Workload Manager Role Assignment To A Category With Base View**
It is true that workload manager role assignment can be done as described in the preceding text for
individual non-head nodes. However it is usually more efficient to assign roles using categories or
configuration overlays, due to the large number of compute nodes in typical clusters.
For example, the case can be considered of all physical on-premises non-head nodes. By default these
are in the default category. This means that, by default, roles in the category are automatically assigned
to all those non-head nodes, unless, as an exception, an individual node configuration overrides the
category setting and uses a role setting instead at node level.


**7.4 Enabling, Disabling, And Monitoring Workload Managers** **349**


Viewing the possible workload manager roles for the category default is done by using the navigation path:
Grouping - Categories[default] - Edit - Settings - Roles - Add
Once the role is selected, its options can be edited and saved.
For compute nodes, the role assigned is usually a workload manager client. If the assigned role
is that of a workload manager client, then the node with that role can have queues, GPUs, and other
parameters specified for it.
For example, queues can then be assigned via the navigation path:
HPC - WLM Management Clusters[cluster instance] - Job Queues
while GPUs, if using Slurm as the workload manager with default settings, can then be specified via the
navigation path:
Configuration Overlays - slurm-client-gpu - roles - slurmclient - edit - Generic Resources 
gpu


The workload manager server role can also be assigned to a non-head node. For example, a Slurm
server role can be taken on by a non-head node. This is the equivalent to the --server-nodes option of
cm-wlm-setup .
Saving the roles with their options and then running imageupdate (section 5.6.2) automatically starts
up the newly-configured workload manager.


**Workload Manager Role Options With Base View**
Each compute node role (workload manager client role) has options that can be set for GPUs, Queues,
and Slots . Generally, the value that is set for Slots is the number of jobs expected to run on a node
simultaneously. This number can, for example, be set to the number of threads. Threads (virtual cores)
in the x86_64 architecture are provided by Intel’s hyper-threading (HT), or by AMD’s simultaneous
multithreading (SMT).
The physical CPU, the cores on the CPU, and the threads of a core (HT, SMT) should not be confused
with each other, they are distinct concepts, and can all have different values.


 - Slots, in a workload manager, corresponds in BCM to:


**–** the CPUs setting (a NodeName parameter) in Slurm’s slurm.conf


**–** the nproc setting in PBS,


In LSF setting the number of slots for the client role to 0 means that the client node does not run
jobs on itself, but becomes a submit host, which means it is able to forward jobs to other client
nodes.


The default value for Slots is AUTO, which means that the value for Slots is auto-detected. The
parameter may be alternatively be set to a non-negative number. Each WLM has a different implementation on how this is done. For instance, for Slurm, BCM uses Slurm’s own auto-detection
implementation.


 - Queues with a specified name are available in their associated role after they are created. The
creation of queues is described in sections 7.6.2 (using Base View) and 7.7.2 (using cmsh ).


All server roles also provide the option to enable or disable the External Server setting. Enabling
that means that the server is no longer managed by BCM, but provided by an external device.
The cmsh equivalent of enabling an external server is described on page 354.


**7.4.2** **Enabling And Disabling A Workload Manager With** cmsh
A particular workload manager package may be set up, but not enabled. This can happen, for example,
if no WLM server or WLM client role has been assigned.


**350** **Workload Management**


If a WLM instance exists, then the WLM client, server, or submit roles can be enabled from cmsh by
assigning it from within the roles submode. Within the assigned role, the properties of the WLM may
be further configured by setting options.


**Workload Manager Role Assignment To A Configuration Overlay With** cmsh
In cmsh, workload manager role assignment to a configuration overlay (section 2.1.5) can be done using
configurationoverlay mode. By default cm-wlm-setup run as a TUI session creates some configuration
overlays with suggestive names, and assigns roles to the configuration overlays according to what the
names suggest. Thus, for example, with the cm-wlm-setup TUI session used to carry out an express
setup for Slurm, the configuration overlays that get created are the following:


**Example**


[basecm11->configurationoverlay]% list
Name (key) Priority All head nodes Nodes Categories Roles

-------------------- ---------- -------------- ---------------- ---------------- ---------------
slurm-accounting 500 yes slurmaccounting

slurm-client 500 no default slurmclient

slurm-server 500 yes slurmserver

slurm-submit 500 no default slurmsubmit

wlm-headnode-submit 600 yes slurmsubmit


Nodes in the default category can take on the slurmclient or slurmsubmit role by setting the nodes
for the role using the associated configuration overlays slurm-client or slurm-submit .
The wlm-headnode-submit configuration overlay is a special overlay. It is applied only to the head
node, and is shared among all installed workload managers. Setting this overlay means that the head
node, by default, has a submit role for a given workload manager.


**Example**


[basecm11->configurationoverlay]% use slurm-client

[basecm11->configurationoverlay[slurm-client]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Name slurm-client

Revision

All head nodes no

Priority 500

Nodes

Categories default

Roles slurmclient

Customizations <0 in submode>

[basecm11->configurationoverlay[slurm-client]]% set nodes

node001 node002 node003 basecm11

[basecm11->configurationoverlay[slurm-client]]% set nodes node001..node002

[basecm11->configurationoverlay*[slurm-client*]]% commit

[basecm11->configurationoverlay[slurm-client]]% list
Name (key) Priority All head nodes Nodes Categories Roles

-------------------- ---------- -------------- ---------------- ---------------- ---------------
slurm-accounting 500 yes slurmaccounting

slurm-client 500 no node001,node002 default slurmclient

slurm-server 500 yes slurmserver

slurm-submit 500 no default slurmsubmit

wlm-headnode-submit 600 yes slurmsubmit

[basecm11->configurationoverlay[slurm-client]]%


**7.4 Enabling, Disabling, And Monitoring Workload Managers** **351**


All the head nodes can also be made to take on the configuration overlay role by setting its All head
nodes value to yes . The union set of All head nodes with Nodes is the set of nodes to which the role is
applied for that configuration overlay.
Values for the parameters in a role, such as the slurmclient role, can be set within the configuration
overlay:


**Example**


[basecm11->configurationoverlay[slurm-client]]% roles

[basecm11->configurationoverlay[slurm-client]->roles]% use slurmclient

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Name slurmclient

Revision

Type SlurmClientRole

Add services yes

WLM cluster slurm

Slots 0

All Queues no

Queues defq

Provisioning associations <0 internally used>

Power Saving Allowed no

Features

Sockets 0

Cores Per Socket 0

ThreadsPerCore 0

Boards 0

SocketsPerBoard 0

RealMemory 0B

NodeAddr

Weight 0

Port 0

TmpDisk 0

Reason

CPU Spec List

Core Spec Count 0

Mem Spec Limit 0B

Node Customizations <0 in submode>

Generic Resources <0 in submode>

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]%


After the workload manager roles are assigned or unassigned, and after running imageupdate (section 5.6.2) for non-head nodes, the associated workload manager services automatically start up or stop
as appropriate.
The configuration overlay role values are inherited by categories and nodes, unless the categories
and nodes have their own values set. Thus, for role properties, a value set at node level overrides values
set at category level, and a value set at configuration overlay level overrides a value set at category level.
This is typical of how properties of objects are inherited in BCM levels.


**Workload Manager Role Assignment To A Category With** cmsh
In cmsh, workload manager role assignment to a node category can be done using category mode, using
the category name, assigning a role from the roles submode, setting the WLM instance for that role,
and committing the modified role:


**Example**


**352** **Workload Management**


[root@basecm11 ~]# cmsh

[basecm11]% category

[basecm11->category]% use default

[basecm11->category[default]]% roles

[basecm11->category[default]->roles]% assign slurmclient

[basecm11->category[default]->roles*[slurmclient*]]% wlm list
Type Name (key) Server nodes Submit nodes Client nodes

------- --------------------- ------------ ---------------- ---------------
slurm slurm1 basecm11 basecm11,node001 node001,node002

[basecm11->category[default]->roles*[slurmclient*]]% set wlmcluster slurm1

[basecm11->category[default]->roles*[slurmclient*]]% commit


Settings that are assigned in the slurmclient role of the category overrule the slurmclient role
configuration overlay settings.
The role assignment at category level requires the value for a WLM instance to be specified for
wlmcluster before the commit command is successful.


**Workload Manager Role Assignment To An Individual Node With** cmsh
In cmsh, assigning a workload manager role to a head node can be done in device mode. This can be
done by using the head node name as the device, assigning the workload manager role to the device,
setting the WLM instance value to the role within the role submode, and committing the modified role.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% use basecm11

[basecm11->device[basecm11]]% roles

[basecm11->device[basecm11]->roles]% assign slurmserver

[basecm11->category[default]->roles*[slurmserver*]]% wlm list
Type Name (key) Server nodes Submit nodes Client nodes

------- --------------------- ------------ ---------------- ---------------
slurm slurm1 basecm11 basecm11,node001 node001,node002

[basecm11->category[default]->roles*[slurmserver*]]% set wlmcluster slurm1

[basecm11->device*[basecm11*]->roles*[slurmserver*]]% commit

[basecm11->device[basecm11]->roles[slurmserver]]%


For regular nodes, role assignment is done via device mode, using the node name. Th node name is
assigned the workload manager role, the WLM instance value is set for that role in the role submode,
and the modified role is committed.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% use node001

[basecm11->device[node001]]% roles

[basecm11->device[node001]->roles]% assign slurmclient

[basecm11->device[node001]->roles*[slurmclient*]]% wlm list

Type Name (key) Server nodes Submit nodes Client nodes

------- --------------------- ------------ ---------------- ---------------
slurm slurm1 basecm11 basecm11,node001 node001,node002

[basecm11->device[node001]->roles*[slurmclient*]]% set wlmcluster slurm1

[basecm11->device[node001]->roles*[slurmclient*]]% commit

[basecm11->device[node001]->roles[slurmclient]]%


**7.4 Enabling, Disabling, And Monitoring Workload Managers** **353**


The role assignment at node level requires the value for a WLM instance to be specified for wlmcluster
before the commit command is successful.

Role assignment values set in device mode have precedence over any role assignment values set in
category mode for that node. This means, for example, that if a node is originally in a node category
with a slurmclient role and queues set, then when the node is assigned a slurmclient role from device
mode, its queue properties are empty by default.


**Setting Options For Workload Manager Settings With** cmsh
In the preceding text, it is explained how the workload manager client or server is assigned a role (such
as slurmclient or slurmserver ) within the roles submode. It is done from within a main mode of
cmsh . The main modes from which role assignment can be done are: configurationoverlay, category

or device .


**Options for workload managers in general:** Whatever main mode is used, the workload manager
options for a role can then be set with the usual object commands introduced in section 2.5.3.


 - **WLM client options:** For example, the configuration options of a WLM client, such as the PBS
Professional client, can be seen by using the show command on the role. Here it can be seen at a
category level, for the default category default :


**Example**


[basecm11->category[default]->roles[pbsproclient]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Add services yes

All Queues no

GPUs 0

Name pbsproclient

Properties

Provisioning associations <0 internally used>

Queues

Revision

Slots 1

Type PbsProClientRole

WLM cluster

Mom Settings <submode>

Comm Settings <submode>

Node Customizations <0 in submode>


The Slots option can be set in the role


**Example**


[basecm11->category[default]->roles[pbsproclient]]% set slots 2

[basecm11->category*[default*]->roles*[pbsproclient*]]% commit

[basecm11->category[default]->roles[pbsproclient]]%


 - **WLM server options:** Similarly, WLM server options can be managed from an assigned server
role. For PBS, the pbsproserver role for a device shows:


**Example**


**354** **Workload Management**


[basecm11->device[basecm11]->roles]% use pbsproserver

[basecm11->device[basecm11]->roles[pbsproserver]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Name pbsproserver

Revision

Type PbsProServerRole

Add services yes

WLM cluster

Provisioning associations <0 internally used>

External Server no

Comm Settings <submode>


**Option to set an external workload manager:** A workload manager can be set to run as an external
server from within a device mode role:


**Example**


[basecm11->device[basecm11]->roles[pbsproserver]]% set externalserver on

[basecm11->device[basecm11]->roles[pbsproserver*]]% commit


For convenience, setting it on the head node is recommended.
The Base View equivalent of configuring externalserver is described on page 349.


**7.4.3** **Monitoring The Workload Manager Services**
By default, the workload manager services are monitored. BCM attempts to restart the services using
the service tools (section 3.14), unless the role for that workload manager service is disabled, or the
service has been stopped.
Workload manager roles and corresponding services can be disabled using cm-wlm-setup (section
7.3), Base View role configuration (section 7.4.1), or cmsh role configuration (section 7.4.2).
The daemon service states can be viewed for each node via the shell, cmsh, or Base View (section 3.14).
Queue submission and scheduling daemons normally run on the head node. From Base View their
states are viewable via the navigation path to the services running on the node. For example, on a head
node (figure 7.16), via:


Devices > Head Nodes > [basecm11] > Settings > JUMP TO > Services


Figure 7.16: Services seen on head node in Base View


For a regular node, a similar navigation path for node001, for example, is:
Devices > Nodes > node001 > Settings > JUMP TO > Services


**7.4 Enabling, Disabling, And Monitoring Workload Managers** **355**


and leads to a view of services on the regular nodes (figure 7.17):


Figure 7.17: Services seen on regular node in Base View


Considering only the WLMs: in figure 7.16 the pbsserver is seen running on the head node, while
in figure 7.17 the pbsmom server is seen running on the compute node.
The navigation path:
Devices > Head Nodes > basecm11 > Settings > JUMP TO > Roles
shows the roles that result in the servers running on the head node (figure 7.18):


Figure 7.18: Roles seen on head node in Base View


Similarly, the navigation path:
Devices > Nodes > node001 > Settings > JUMP TO > Roles
shows the roles on a regular node such as node001 (figure 7.19):


**356** **Workload Management**


Figure 7.19: Roles seen on regular node in Base View


The roles seen in these figures are from the defaults that cm-wlm-setup provides in an express setup.
For regular nodes, the inheritance of roles from category level or configuration overlay level is indicated by the values in the INHERITED column. Thus, in figure 7.19, the pbsprosubmit and pbsproclient
roles are decided by the default setting from the category level.
The assignment of roles can be varied to taste for WLMs. This allows WLM services to run on the
head node or on the regular nodes.
From cmsh the services states are viewable from within device mode, using the services command.
One-liners from the shell to illustrate this are (output elided):


**Example**


[root@basecm11 ~]# cmsh -c "device services node001; status"

Service Status

------------ ----------
nslcd [ UP ]

pbsmom [ UP ]

[root@basecm11 ~]# cmsh -c "device services basecm11; status"


Service Status

------------ ----------
...

pbsserver [ UP ]


Roles can be viewed from within the main modes of configurationoverlay, category, or device .
One-liners to view these are:


**Example**


[root@basecm11 ~]# cmsh -c "configurationoverlay; list"
Name (key) Priority All head nodes Nodes Categories Roles

-------------------- ---------- -------------- ---------------- ---------------- ---------------
openpbs-client 500 no default pbsproclient

openpbs-server 500 yes pbsproserver

openpbs-submit 500 no default pbsprosubmit

wlm-headnode-submit 600 yes pbsprosubmit


[root@basecm11 ~]# cmsh -c "category; use default; roles; list -p"
Name (key)

---------------------------

**7.5 Configuring And Running Individual Workload Managers** **357**


[overlay:openpbs-client:500] pbsproclient

[overlay:openpbs-submit:500] pbsprosubmit


[root@basecm11 ~]# cmsh -c "device use node001; roles; list -p"
Name (key)

---------------------------------------
[overlay:openpbs-client:500] pbsproclient

[overlay:openpbs-submit:500] pbsprosubmit


[root@basecm11 ~]# cmsh -c "device use basecm11; roles; list -p"
Name (key)

---------------------------------------
[750] backup

[750] boot

[750] firewall

[750] headnode

[750] monitoring

[750] provisioning

[750] storage

[overlay:openpbs-server:500] pbsproserver

[overlay:openpbs-submit:500] pbsprosubmit


The -p|--priority option displays of the list command the priority setting for the roles.


**7.5** **Configuring And Running Individual Workload Managers**


BCM deals with the various choices of workload managers in as generic a way as possible. This means
that not all features of a particular workload manager can be controlled, so that fine-tuning must be
done through the workload manager configuration files. Workload manager configuration files that are
controlled by BCM should normally not be changed directly because BCM overwrites them. However,
overwriting by CMDaemon is prevented on setting the directive:


FreezeChangesTo< _workload manager_ >Config = <true|false>


in cmd.conf (Appendix C), where < _workload manager_ - takes the value of Slurm, LSF, or PBSPro, as appropriate. The value of the directive defaults to false .
A list of configuration files that are changed by CMDaemon, the items changed, and the events
causing such a change are listed in Appendix H.
A very short guide to some specific workload manager commands that can be used outside of the
NVIDIA Base Command Manager 11 system is given in Appendix F.


**7.5.1** **Configuring And Running Slurm**

**Slurm Packages**
At the time of writing (April 2025), BCM is integrated with Slurm packages for Slurm versions 24.05,
24.11 and 25.05. Slurm version 24.11 is installed by default.
For Slurm version 24.05, the following packages are available from the BCM repositories for Ubuntu
24.04:


 - slurm24.05 : Simple Linux Utility for Resource Management, Slurm Workload Management.


 - slurm24.05-contribs : Perl tool to print Slurm job state information.


 - slurm24.05-devel : Development package for SLURM. Includes the header files and static libraries for the SLURM API.


**358** **Workload Management**


 - slurm24.05-libpmi : Slurm’s implementation of the pmi libraries.


 - slurm24.05-openlava : openlava/LSF wrappers for transition from OpenLava/LSF to Slurm.


 - slurm24.05-pam : PAM module for restricting access to compute nodes via Slurm.


 - slurm24.05-perlapi : Perl API to Slurm.


 - slurm24.05-prs : Slurm PRS plugin.


 - slurm24.05-sackd : Slurm authentication daemon. Used on login nodes that are not running
slurmd daemons to allow authentication to the cluster.


 - slurm24.05-slurmctld : Slurm control daemon.


 - slurm24.05-slurmd : Slurm compute node daemon.


 - slurm24.05-slurmdbd : Slurm database daemon.


 - slurm24.05-slurmrestd : Slurm REST API translator.


 - slurm24.05-torque : Torque/PBS wrappers for transition from Torque/PBS to Slurm.


For Slurm version 24.11, the value of 24.05 is simply replaced by 24.11 in the preceding list of packages. Similarly, for Slurm version 25.05, the value of 24.05 is simply replaced by 25.05 in the preceding
list of packages.
The distribution version of Slurm (package: slurm ) is not integrated with BCM and conflicts with
the preceding packages. It should not be used.
Important updates from upstream are patched into the BCM repositories. If updating Slurm packages, all the Slurm packages should be updated to the same version, on the compute nodes as well as
on the scheduling node.


**Updating From Earlier Slurm Versions To** slurm24.11
Upgrading between major versions of Slurm is generally possible. It is a good idea to upgrade one
version at a time, rather than jumping 2 or more versions ahead, which requires a full wipe of the Slurm
configuration.
If Slurm is using Pyxis (section 7.3.3), then upgrading the Slurm version means that Pyxis needs to be
reinstalled using cm-wlm-setup . The reinstallation run for Pyxis compiles Pyxis and recreates a plugin
directory for the new Slurm version under /cm/local/apps/slurm/ .
An upgrade from one major version of Slurm to another can be carried out according to the following example, which is for an update from major version 22.05 to version 24.11, and avoids total
reconfiguration of the Slurm configuration:


  - It is recommended that no jobs are running. Draining nodes (section 7.7.3) is one way to arrange
this over time. No new jobs run on a drained node, but old ones are allowed to finish.


  - When all running jobs are finished, then Slurm server services— slurmctld and slurmdbd —should
be stopped using cmsh or Base View (section 3.14.2):


**Example**


[basecm11->device[basecm11]->services]% stop slurmctld

[basecm11->device[basecm11]->services]% stop slurmdbd


  - The old Slurm packages should then be removed. There can be only one version of Slurm at a
time, so there will be a package installation conflict if a new version is installed while an old one
is still there.


Removal can be carried out on RHEL-based systems with, for example:


**7.5 Configuring And Running Individual Workload Managers** **359**


[root@basecm11 ~]# yum remove slurm22.05*


The old packages must also be removed from each software image that uses it:


[root@basecm11 ~]# cm-chroot-sw-img /cm/images/< _software image_   
...

[root@< _software image_   - /]# yum remove slurm22.05*
... _removal takes place_ ...

[root@< _software image_   - /]# exit


The cm-chroot-sw-img wrapper utility is discussed in section 9.4.1.


  - The new packages can then be installed. For installation onto the RHEL head node, the installation
might be carried out as follows:


[root@basecm11 ~]# yum install slurm24.11 slurm24.11-slurmd slurm24.11-contribs _\_
slurm24.11-perlapi slurm24.11-devel slurm24.11-pam slurm24.11-slurmdbd _\_

slurm24.11-slurmrestd


The client package can be installed in each software image with, for example:


[root@basecm11 ~]# cm-chroot-sw-img /cm/images/< _software image_   
...

[root@< _software image_   - /]# yum install slurm24.11-slurmd
... _installation takes place_

[root@< _software image_   - /]# exit


Other Slurm packages from the repository may also be installed on the head node and within the
software images, as needed.


  - The new Slurm version is then set in cmsh or Base View, in the Slurm WLM cluster configuration:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% wlm use slurm

[basecm11->wlm[slurm]]% set version 24.11; commit


  - Slurm server services slurmctld and slurmdbd should then be started again using cmsh or Base
View:


**Example**


[basecm11->device[basecm11]->services]% start slurmdbd

[basecm11->device[basecm11]->services]% start slurmctld


  - The nodes can then have their new image placed on them, and the new Slurm configuration can
then be taken up. This can be done in the following two ways:


1. The regular nodes can then be restarted to supply the live nodes with the new image and get
the new Slurm configuration running.


**360** **Workload Management**


2. Alternatively, the imageupdate command (section 5.6.2) can be run on the live nodes to supply them with the image.

Running the imageupdate command in dry mode (the default) first is recommended. The
synclog command can then be run to check there are no unexpected changes that will take
place due to the update. If all is well, then imageupdate ’s wet mode flag -w can be used in
order to really carry out the task.

For example, the change can be checked, and then actually carried out, for the image on
node001 with:


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[basecm11->device[node001]]% imageupdate
Performing dry run (use synclog command to review result, then pass -w to perform real update)...

... _some messages_ ...
imageupdate [ COMPLETED ]

[basecm11->device[node001]]% synclog
... _rsync dry run output_ ...

[basecm11->device[node001]]% imageupdate -w
... _same messages as before, but this time it really happens_ ...

[basecm11->device[node001]]% commit


The last commit command triggers the reconfiguration of the file /etc/systemd/system/
slurmd.service.d/99-cmd.conf on the node. After a short time—around 30 seconds—the
file is regenerated. The slurmd service on the node can then be restarted with:


[root@basecm11 ~]# ssh node001 "systemctl daemon-reload"

cmsh -c "device services node001; use slurmd; restart"


**IMEX**

NVIDIA IMEX (Internode Memory Exchange Service) is a secure service that facilitates the mapping of
GPU memory over NVLink between the GPUs in an NVLIink domain.
BCM can enable the IMEX daemon either globally, or per job for Slurm.


**Enabling the IMEX daemon globally for Slurm:** If IMEX is set globally, it means that it is set to run
on all nodes.

The advantage of this configuration is that it is easy to set up, and easy to test to see if it is all working.
A disadvantage is that a user running a job on one node can read memory from a job run by another
user on another node. It requires overcoming difficult hurdles to carry out, but it is not impossible. The
administrator should therefore weigh up if this seems a significant issue for the cluster being administered

The IMEX global service can be run by setting the values for the service for the compute nodes. For
example, nodes in a dgx-gb200 category can have the service added and set to:


[basecm11->category[dgx-gb200]->services[nvidia-imex]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Revision

Service nvidia-imex

Run if always

Monitored yes

Autostart yes

Managed yes


**7.5 Configuring And Running Individual Workload Managers** **361**


**Enabling and disabling the IMEX daemon per job for Slurm:** Configuring per job means that IMEX
runs just before the job starts, and that the service runs on only a node that need it.
A disadvantage is that verifying that it actually works requires a job run.
Running the IMEX daemon per job has the advantage that one user running a job cannot read the
memory of a job run by another user on another node.
To run IMEX per job, any global IMEX setting must first be cleared away. This can be done by first:


  - removing the nvidia-imex service configuration entirely from CMDaemon


**Example**


[basecm11->category[dgx-gb200]->services[nvidia-imex]]% remove nvidia-imex; commit


  - stopping the service on the compute nodes, for example with pdssh or pdexec, or simply carrying
out a reboot


The value of imex in the slurmclient role can then be set:


[root@basecm11 ~]# cmsh

[basecm11]% configurationoverlay roles slurm-client-gpu

[basecm11->configurationoverlay[slurm-client-gpu]->roles]% use slurmclient

[basecm11->configurationoverlay[slurm-client-gpu]->roles[slurmclient]]% set imex yes

[basecm11->configurationoverlay*[slurm-client-gpu*]->roles*[slurmclient*]]% commit

[basecm11->configurationoverlay[slurm-client-gpu]->roles[slurmclient]]%


Committing that imex setting configures Slurm prolog and epilog scripts in the backend as follows:


  - the prolog script configures the IMEX daemon with the nodes allocated to the GPU job and starts
the IMEX daemon on the node


  - the epilog cleans up the configuration and stops the IMEX daemon on the node


**Workload Power Profile Settings (WPPS)**
NVIDIA Blackwell GPUs support workload power profiles. Each GPU in a job can have a specific
workload power profile set for it; the profile can vary per GPU. For these power profles to work as
expected, a node that has a job allocated to it must have the job allocated exclusively to it.
BCM allows the user who is running a Slurm job to change its power profiles in two ways:


1. Statically: the job prolog script switches the power profiles for all GPUs allocated to the job just
before the job starts


2. Dynamically: the job process sets power profiles for each allocated GPU during job execution


In both cases, when the job is finished, the epilog script resets the GPU power profiles back to the default.
Workload power profiles settings are a part of the slurmclient role, located within the Power profiles
submode:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% configurationoverlay roles slurm-client-gpu

[basecm11->configurationoverlay[slurm-client-gpu]->roles]% use slurmclient

[basecm11->configurationoverlay[slurm-client-gpu]->roles[slurmclient]]% powerprofiles

[basecm11->configurationoverlay[slurm-client-gpu]->roles[slurmclient]->powerprofiles]% show

Parameter Value

-------------------------------- -----------------------------------------------

**362** **Workload Management**


Disabled yes

Fail on error no

Job keyword wpps
Jobs profiles directory /var/run/nvidia/workload-power-profiles

Debug no
Debug log directory /var/spool/cmd/wlm/wpps

[basecm11->configurationoverlay[slurm-client-gpu]->roles[slurmclient]->powerprofiles]% set disabled no

[basecm11->configurationoverlay*[slurm-client-gpu*]->roles*[slurmclient*]->powerprofiles*]% commit

[basecm11->configurationoverlay[slurm-client-gpu]->roles[slurmclient]]%


The Power profiles parameters are:


1. Disabled : forbids a job from changing workload power profiles (yes by default)


2. Fail on error : allows prolog and epilog to fail if a workload power profiles change fails for any

reason


3. Job keyword : a keyword in the JSON object, used by the WLM job, to specify a workload power
profiles setting in the comment field


4. Jobs profiles directory : a top directory which includes job ID directories, and used by the job
to change the workload power profiles


5. Debug : setting it to yes enables prolog and epilog debug messages The prolog and epilog then
write debug logs to the location set by the Debug log directory parameter,


6. Debug log directory : directory where prolog and epilog create debug log files per job. This is
/var/spool/cmd/wlm/wpps/<JOBID>.log by default. The log files are not cleaned up automatically.


If WPPS is enabled, then special BCM prolog and epilog scripts are enabled in Slurm on compute
nodes. The scripts parse the SLURM_JOB_COMMENT environment variable that is passed by Slurm. The
scripts search for a JSON object that includes the key wpps . The key used can be changed using the Job
keyword parameter. The expected format of the JSON object is:


{"wpps": {"profiles": PROFILES}}


Here, PROFILES is either


  - a JSON list of strings (workload profile names or their numbers) or


  - a single string (one workload profile name) or


  - a workload profile number.


The values that PROFILES can take are:


 - max_p


 - max_q


 - llm_training


 - llm_inference


On matching, the specified profiles are set for all the GPUs on the node that are allocated for the job
when the job starts.
For example, the following job submission command instructs the prolog script to set the workload
profiles to max_p and compute :


**7.5 Configuring And Running Individual Workload Managers** **363**


$ sbatch --gres=gpu:b100:8 --comment='{"wpps": {"profiles": ["max_p", "compute"]}}' job.sh


All allocated GPUs on the node get the specified workload profiles, which means that job allocation
must be configured to run on that node as a job that excludes other jobs running on it. If the cluster
administrator has set oversubscribe for Slurm, then that takes precedence over exclusivity, and must
therefore be taken into account.

If a job requires dynamic profiles management, then the job process can notify BCM to update the
power profiles of specific GPUs during job execution. The prolog creates a directory of the form /var/
run/nvidia/workload-power-profiles/<JOB_ID>/ per job. The following files are created within the
directory:


1. username : read-only (for users) file that includes the current job user name. Used by BCM.


2. uuids : read-only (for users) file that includes a list of GPU UUIDs (one per line) allocated for this
job.


3. profiles : file that can be used by the job process to set new profiles. The file is empty by default.
An empty file means that BCM does not modify the profiles. If the job process writes two lines:


max_p

compute


then BCM reads this file almost immediately, and applies these two workload profiles to the GPUs
whose UUIDs are specified in uuids file.


What users are running in each workload power profile can be viewed with a PromQL query, as
explained on page 367.


**Management of node workload profiles by regular users:** The user, for example John, can be given
access to checking and managing GPU power profiles by running the allowgpuworkloadpowerprofiles
command.


**Example**


[basecm11->user[john]]% set allowgpuworkloadpowerprofiles yes


The gpuworkloadpowerprofiles command can then be run to check the current node profiles:


**Example**


[basecm11->device]% gpuworkloadpowerprofiles show -n node001

Node GPU Profiles

------------ -------- -----------
node001 0 COMPUTE(2)

node001 1 MAX_P(0)

node001 2 MAX_P(0)

node001 3 MAX_P(0)

node001 4 MAX_P(0)

node001 5 MAX_P(0)

node001 6 MAX_P(0)

node001 7 MAX_P(0)

[basecm11->device]%


This may be useful for debug purposes.
The BCM script cm-gpu-workload-power-profiles can then be used to change the profiles as follows:


**364** **Workload Management**


  - The user first gets the GPU UUIDs:


**Example**


root@dgx-gb200-n07-c2:~# nvidia-smi --query-gpu=uuid --format=csv,noheader --id=0,1,2,3

GPU-1e72bc8d-b967-6031-24bd-c5a08ad090e1

GPU-3a6ac832-3423-68cc-ed1f-64f2b46d248d

GPU-f40fabb7-eb9b-0253-4bd5-08b4a12916ea


  - The user can then use the script to change the profile. For example, just for the GPUs 1 and 2:


**Example**


root@dgx-gb200-n07-c2:~# /cm/local/apps/cmd/sbin/cm-gpu-workload-power-profiles -p compute -u john _\_

3a6ac832-3423-68cc-ed1f-64f2b46d248d f40fabb7-eb9b-0253-4bd5-08b4a12916ea


The script carries the profile change out with the help of CMDaemon in the back end.


Slurm’s prolog and epilog actually work with the script in BCM when carrying out dynamic profiles management, so that the user does not need to use the script manually.


**Management of external users to allow them to use profiles:** External users, that is users managed
by an external LDAP and not managed by the BCM LDAP, can use the workload power profile settings
if their user name or UID is added to the file:


/cm/local/apps/cmd/etc/allow-users-wpps.conf


The file must be created on the head node, or on both head nodes if the cluster has HA. The file
should have its mode set to 0600 . The user name or UID should be added on its own line in the file.


**Advanced Slurm Job Accounting**
PromQL queries can be run and then filtered by Slurm job labels with BCM. The labels are taken either
from a job comment or from an account name used by the job. After the labels for the job are extracted, the labeled entity is stored in the monitoring data. The administrator can then run PromQL
queries, and filter results by label. Examples of such PromQL queries are the job_gpu_wasted or
job_gpu_utilization queries (section 12.4.1).
Extract accounting info must be set to yes to enable labels to be extracted from job comments or

account names:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% wlm use slurm

[basecm11->wlm[slurm]]% accounting

[basecm11->wlm[slurm]->show]% accounting

Parameter Value

-------------------------------- -----------------------------------------------
Managed hierarchy

Separator _

Job comment labels

Extract accounting info no

[basecm11->wlm[slurm]->accounting]% set extractaccountinginfo yes

[basecm11->wlm*[slurm*]->accounting*]% commit


In addition, the administrator must configure the job comment label format and the format of Slurm
account names, if they exist. Without that configuration, BCM cannot parse the labels.


**7.5 Configuring And Running Individual Workload Managers** **365**


**Job comment labels:** A user running the job can specify the label for the job comment in a special
format. Such a label could be, for example, a tag to indicate the artificial neural network model, where
different groups of jobs use different models. The administrator (after having enabled accounting information extraction) can set a regex for the tag in a Job comment field parameter in accounting submode:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% wlm use slurm

[basecm11->wlm[slurm]]% accounting

[basecm11->wlm[slurm]->accounting]% set jobcommentlabels model

[basecm11->wlm*[slurm*]->accounting*]% commit


In the preceding example, the label model is set in the monitoring data when the job comment includes a JSON object with model as a key. The value must be a string that will be a value for the label
model . For example "model": "llm123" . The JSON object may contain other information that will be
ignored by BCM when it reads the labels from the comment.


**Account name labels:** Several labels can be assigned by BCM to a job parsed from an associated account name. The labels can be used to represent a hierarchy of organizational entities, such as department, project, team, and so on. The following configuration options allow this representation:


1. Managed hierarchy: representation of the account name as a list of organizational entity labels.


2. Separator: a separator for the labels in the account names. By default this is the underscore character, _. The last entity is separated with double separator. This means that the last entity (and
only the last entity) can have a single separator in the name itself.


For instance, if Slurm account names use the following format:


DEPARTMENT_PROJECT_TEAM


then Managed hierarchy values can be set as follows:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% wlm use slurm

[basecm11->wlm[slurm]]% accounting

[basecm11->wlm[slurm]->accounting]% set managedhierarchy department project team

[basecm11->wlm*[slurm*]->accounting*]% commit


It is up to the administrator to create the accounting hierarchy in Slurm, and set names as described
by the Managed hierarchy parameter.


**Example**


[root@basecm11 ~]# module load slurm

[root@basecm11 ~]# sacctmgr add account NVIDIA Description="NVIDIA account" Organization=NVIDIA parent=root -i

[root@basecm11 ~]# sacctmgr add account Department1 Organization=NVIDIA parent=NVIDIA -i

[root@basecm11 ~]# sacctmgr add account Department1_Project1 Organization=NVIDIA parent=Department1 -i

[root@basecm11 ~]# sacctmgr add account Department1_Project1__Team_1 Organization=NVIDIA parent=Department1 -i

[root@basecm11 ~]# sacctmgr add account Department1__Team_2 Organization=NVIDIA parent=Department1 -i


In the preceding example two teams have been made. Team 1 is defined according to the full entities
hierarchy (department, project, team), while Team 2 is defined only under a department. BCM correctly
recognizes such "clipped" hierarchy locations for a team in the account names.
Similar to the Slurm command sshare, an administrator can display the Slurm account hierarchy
with the fairshare command in cmsh :


**366** **Workload Management**


**Example**


[basecm11->wlm[slurm]]% fairshare -t

Account fairshare raw_shares raw_usage norm_shares norm_usage parent

----------------------------- ------------ ---------- ---------- ----------- ---------- ------------------
root (top account) 0.0 0 0 0.0 0.0
nvidia 0.0 1 0 0.5 0.0 root (top account)

department1 0.0 1 0 1.0 0.0 nvidia

department1__team_2 0.0 1 0 0.333333 0.0 department1

department1_project1 0.0 1 0 0.333333 0.0 department1

department1_project1__team_1 0.0 1 0 0.333333 0.0 department1
root 1.0 1 0 0.5 0.0 root (top account)

[basecm11->wlm[slurm]]% fairshare -f ""

root


~~n~~ vidia


~~d~~ epartment1


~~d~~ epartment1__team_2

~~d~~ epartment1_project1

~~d~~ epartment1_project1__team_1

~~r~~ oot


The following command options can be used:


1. -t|--table : print accounts fairshare parameters as a table


2. -a|--account <name> : print information for specific account


3. -f|--fields <PARAMETERS> : display only specified fairshare account parameters (comma-delimited)
Format:


<FIELD>[%<MIN>[-<MAX>]][,<FIELD>[%<MIN>[-<MAX>]],...] ;


where MIN and MAX are minimum and maximum value lengths. The parameter can be combined
with others.


The following example uses labels from both job comment and account names:


**Example**


[root@basecm11 ~]# su - alice

[alice@basecm11 ~]$ module load slurm

[alice@basecm11 ~]$ sbatch -A department1_project1__team_1 --comment='{"model": "llm123"}' --wrap="hostname"

Submitted batch job 1

[alice@basecm11 ~]$


PromQL queries with these labels are run later on.
In cmsh the administrator can validate how BCM parses the job labels from both job comment and
from the Slurm account name:


[basecm11->wlm[slurm]->jobs]% info 1 | grep "accounting info" -i
Accounting info {"department":"department1","model":"llm123","project":"project1","team":"team_1"}

[basecm11->wlm[slurm]->jobs]%


Jobs information can also be displayed by filtering using the labels (some output elided for clarity):


**7.5 Configuring And Running Individual Workload Managers** **367**


[basecm11->wlm[slurm]->jobs]% filter -i team="team_1"

Job ID Job name User Queue Submit time Start time End time Nodes Exit code

------- ---------- ------ ------- ------------ ----------- --------- --------- ---------
1 wrap alice 13:28:46 13:28:46 13:28:46 1

2 wrap alice defq 13:28:59 13:28:59 13:30:00 node001 0

3 wrap alice defq 13:30:39 13:30:39 13:31:40 node001 0

[basecm11->wlm[slurm]->jobs]%


The following query filters the team:


[basecm11->monitoring->labeledentity]% instantquery "job_gpu_wasted{team= _\_ "team_1 _\_ "}[1h]"

Name category department group hostname job_id job_name project queue team user wlm ...

--------------- -------- ------------ ------ -------- ------- -------- --------- ------ ------- ------ ----- ...

job_gpu_wasted default department1 alice node001 1 wrap project1 defq team_1 alice slurm ...

job_gpu_wasted default department1 alice node002 2 wrap project1 defq team_1 alice slurm ...


The following query filters the model name:


[basecm11->monitoring->labeledentity]% instantquery "job_gpu_wasted{model= _\_ "llm123 _\_ "}[1h]"

Name category group hostname job_id job_name model queue user wlm ...

--------------- -------- ------ -------- -------- -------- -------- -------- ------ ----- ...

job_gpu_wasted default alice node001 1 wrap foo defq alice slurm ...

job_gpu_wasted default alice node002 2 wrap foo defq alice slurm ...


The following query show what users are running in each WPPS profile:


[-head-01->monitoring->labeledentity]% instantquery -q job_gpu_workload_power_profile_for_user

Name gpu_workload_power_profile user Timestamp ... Value

---------------------------------------- -------------------------- ---------- -----------... ----
job_gpu_workload_power_profile_for_user COMPUTE avolkov Mon Jun 2 ... 2

job_gpu_workload_power_profile_for_user LLM_INFERENCE avolkov Mon Jun 2 ... 2133

job_gpu_workload_power_profile_for_user LLM_INFERENCE root Mon Jun 2 ... 23

job_gpu_workload_power_profile_for_user LLM_INFERENCE shoreline Mon Jun 2 ... 336

job_gpu_workload_power_profile_for_user LLM_INFERENCE wglantz Mon Jun 2 ... 12

job_gpu_workload_power_profile_for_user LLM_TRAINING root Mon Jun 2 ... 7

job_gpu_workload_power_profile_for_user LLM_TRAINING shoreline Mon Jun 2 ... 331

job_gpu_workload_power_profile_for_user MAX_P avolkov Mon Jun 2 ... 2134

job_gpu_workload_power_profile_for_user MAX_P root Mon Jun 2 ... 60

job_gpu_workload_power_profile_for_user MAX_P shoreline Mon Jun 2 ... 379

job_gpu_workload_power_profile_for_user MAX_P wglantz Mon Jun 2 ... 12

job_gpu_workload_power_profile_for_user MAX_Q root Mon Jun 2 ... 8

job_gpu_workload_power_profile_for_user MAX_Q shoreline Mon Jun 2 ... 320


**Slurm NVIDIA Sharp Plugin**
NVIDIA’s Sharp packages are packages that offload some operations from CPUs and GPUs to the network. Sharp is the abbreviation used for the Scalable Hierarchical Aggregation and Reduction Protocol.
The protocol refers to the reduction in the amount of data traversing the network and the reduction in
the time for collective operations. Using Sharp frees up more CPUs and GPU resources for computation.
The Sharp binaries are available in various packages.
Slurm versions 24.05 and 24.11 have a special version that includes an NVIDIA Sharp plugin. To use
it, the existing Slurm packages must be substituted by packages with the -sharp suffix. This allows the
plugin and associated extra options to be used.


**Example**


The following session on an Ubuntu system illustrates the existing Slurm version 24.05 packages, and
then carrying out a replacement of these with the corresponding Sharp versions:


**368** **Workload Management**


basecm11:~# dpkg --get-selections | grep slurm | cut -f1 | tr " _\_ n" " " ; echo

slurm24.05 slurm24.05-client slurm24.05-contribs slurm24.05-devel slurm24.05-perlapi slurm24.05-slurmdbd
basecm11:~# apt install slurm24.05-sharp slurm24.05-sharp-client slurm24.05-sharp-contribs _\_

slurm24.05-sharp-devel slurm24.05-sharp-perlapi slurm24.05-sharp-slurmdbd


The change should be treated like the upgrade procedure on page 358, and should likewise end with
the cluster administrator selecting the -sharp Slurm version parameter in cmsh and committing it.


**Example**


root@basecm11:~# cmsh -c "wlm use slurm; get version"

24.05-sharp


This plugin is only useful for a network that has the necessary hardware and services configured.
Further information about Sharp can be found at [https://docs.nvidia.com/networking/display/](https://docs.nvidia.com/networking/display/sharpv300)
[sharpv300](https://docs.nvidia.com/networking/display/sharpv300) .


**Configuring Slurm**
After Slurm setup is configured and installed with cm-wlm-setup (section 7.3), the Slurm software components are installed in a symlinked directory /cm/local/apps/slurm/current . The same set of Slurm
packages should be installed on the head nodes and in each software image where any of the Slurm
services run.

Slurm clients and servers can be configured to some extent via role assignment (sections 7.4.1
and 7.4.2).
Using cmsh, advanced option parameters can be set under the slurmclient and slurmserver
roles. The settings for the roles can be done at configuration overlay, category, or node level (sections 2.1.5, 2.1.6).
By default, the cm-wlm-setup utility configures Slurm using configuration overlays.


**Example**


[basecm11->configurationoverlay]% list
Name (key) Priority All head nodes Nodes Categories Roles

-------------------- ---------- -------------- ---------------- ---------------- ---------------
slurm-accounting 500 yes slurmaccounting

slurm-client 500 no default slurmclient

slurm-server 500 yes slurmserver

slurm-submit 500 no default slurmsubmit

wlm-headnode-submit 600 yes slurmsubmit


The settings within the roles can be viewed and modified. For example, the slurmclient role of the
slurm-client configuration overlay can be viewed:


**Example**


[basecm11->configurationoverlay]% roles slurm-client

[basecm11->configurationoverlay[slurm-client]->roles]% show slurmclient

Parameter Value

-------------------------------- -----------------------------------------------
Name slurmclient

Revision

Type SlurmClientRole

Add services yes

WLM cluster slurm

Slots 0


**7.5 Configuring And Running Individual Workload Managers** **369**


All Queues no

Queues defq

Features

Sockets 0

Cores Per Socket 0

ThreadsPerCore 0

Boards 0

SocketsPerBoard 0

RealMemory 0B

NodeAddr

Weight 0

Port 0

TmpDisk 0

Reason

CPU Spec List

Core Spec Count 0

Mem Spec Limit 0B

GPU auto detect BCM

Node Customizations <0 in submode>

Generic Resources <0 in submode>

Cpu Bindings None

Slurm hardware probe autodetect yes
Memory autodetection slack 0.0%

IMEX no


**Assigning nodes to Slurm queues:** Slurm can configure _nodesets_ ( [man slurm.conf.5](https://slurm.schedmd.com/slurm.conf.html) ). Nodesets are a
way to conveniently group nodes under a unique arbitary name, so that features can be assigned to a
group of nodes.
Starting with BCM version 11, BCM can be used to configure Slurm nodesets using the Nodesets
and Nodeset features options within the slurmclient role options:


 - Nodesets : An arbitrary name can be set for the Nodesets parameter. Names that are set are automatically added to slurm.conf . Nodes with the slurmclient role are then associated with this
arbitrary nodeset name in slurm.conf . For example, if the nodesets parameter is set to ns1 and
the role is assigned only to node node001, then BCM translates this configuration after a short time
into a slurm.conf line that looks like:


NodeSet=ns1 Nodes=node001


In an express Slurm setup by cm-wlm-setup (page 333), the slurmclient role is set by default for
all nodes via the configuration overlay. This means that setting the nodesets parameter in the
slurmclient role there sets it for all nodes. After a short while, the NodeSet line in slurm.conf
changes to match the parameter change:


**Example**


[basecm11->configurationoverlay[slurm-client]->roles[slurmclient] get nodesets

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient] set nodesets ns1; commit

then, after a minute or so:

[basecm11->...->roles[slurmclient] !grep -i nodeset /cm/shared/apps/slurm/etc/slurm/slurm.conf

[basecm11->...->roles[slurmclient] NodeSet=ns1 Nodes=node[001-003] _for a 3-node cluster_


 - Nodeset features : All values of the Nodeset features parameter are added to nodes that have
the slurmclient role. They are added as Slurm node features, which means that there is no need


**370** **Workload Management**


to duplicate them in the Features parameter of the slurmclient role. The values that are set are
a list of strings.


The Slurm nodesets are added to slurm.conf with the same name as these features. This is useful

when the administrator needs to assign sets of nodes to queues based on the node features.


For example, if the parameter has a value bigmem, and the slurmclient role is assigned to node
node001, then BCM adds lines with:


NodeName=node001 Features=bigmem ...
and

NodeSet=bigmem Feature=bigmem


to slurm.conf .


For the 3-node case specified by the configuration overlay of earlier, the change is illustrated by
the following:


**Example**


[basecm11->...->roles[slurmclient]]% get nodesetfeatures

[basecm11->...]->roles[slurmclient]]% !grep -i ^Node /cm/shared/apps/slurm/etc/slurm/slurm.conf

NodeName=node[001-003] ... Features=location=local

NodeSet=ns1 Nodes=node[001..003]

[basecm11->...->roles[slurmclient]]% set nodesetfeatures bigmem
... _wait a little for the change to happen_ ...

[basecm11->...->roles[slurmclient]]% !grep -i ^Node /cm/shared/apps/slurm/etc/slurm/slurm.conf
NodeName=node[001-003] ... Features=location=local,bigmem

NodeSet=ns1 Nodes=node[001-003]

NodeSet=bigmem Feature=bigmem


The Nodeset features parameter does not automatically add the nodesets to any queues. The
administrator must add the nodesets to the queues separately.


**Specifying nodesets for Slurm via** wlm **mode with** jobqueues **, vs specifying nodes using the**
slurmclient **role’s** queues **parameter:**
Specifying which nodes go into Slurm job queues can be specified using either nodesets or nodes.


  - The administrator can specify which nodesets are included in Slurm job queues by setting the
nodesets parameter for a job queue, within a jobqueue submode.


For example, the nodeset ns1 defined in the slurmclient role earlier can be included in defq with:


**Example**


root@basecm11:~# cmsh

[basecm11]% wlm jobqueue

[basecm11->wlm[slurm]->jobqueue]% use defq

[basecm11->wlm[slurm]->jobqueue[defq]]% set nodesets ns1; commit


If the nodesets parameter is set for a queue, then BCM does not add any nodes that are specified
by the Compute nodes parameter, but only adds the nodes in the nodesets specification to a line
with the format:


PartitionName=... Nodes=< _nodesets_   - ...


in slurm.conf . As a reminder, a queue in Slurm terminology is a partition.


**7.5 Configuring And Running Individual Workload Managers** **371**


  - The administrator can specify the nodes that are associated with a job queue.


**–** Prior to BCM version 11, job queues were specified for nodes only by using the queues parameter of the slurmclient role at the device, category, or configurationoverlay mode
level.


For example, for the configuration overlay slurm-client that defines the Slurm client configuration by default, the nodes for the Slurm client role are the nodes in the default category
default . Within the configuration overlay, within the slurmclient role, the default queue to
be used is set to defq by default:


**Example**


root@basecm11:~# cmsh

[basecm11]% configurationoverlay use slurm-client

[basecm11->configurationoverlay[slurm-client]]% get categories

default

[basecm11->configurationoverlay[slurm-client]]% roles

[basecm11->configurationoverlay[slurm-client]->roles]% use slurmclient

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]% get queues

defq


**–**
Starting with BCM version 11, the administrator can also add nodes to queues directly from
within wlm mode for a particular WLM, within the jobqueue mode for a particular queue, by
setting nodes for particular node grouping parameters. For example, for Slurm the following
queue parameters are available:


**Example**


[basecm11->wlm[slurm]->jobqueue[defq]]% show | egrep -i '(overlay|nodegroups|compute|catego|nodeset)'

Nodesets

Overlays

Categories

Nodegroups

Compute nodes


Thus defq is used by nodes that have been specified in the following groupings:


        - [Nodesets] [: nodes in these nodesets]


        - [Overlays] [: nodes in these configuration overlays (including nodes of categories that are]
in this overlay)

        - [Categories] [: nodes in these categories]


        - [Nodegroups] [: nodes in these node groups]


        - [Compute nodes] [: nodes listed in this parameter]


**Slurm Hardware Autodetection (non-GPU):** The setting Slurm hardware probe autodetect in the
Slurm role enables automated hardware detection for Slurm for non-GPU hardware. (Specifically for
GPUs is the related Slurm GPU auto detect setting (page 373)).
Slurm hardware probe autodetect enables detection for the following Slurm parameters:


 - corespersocket


 - threadspercore


 - boards


 - socketsperboard


**372** **Workload Management**


 - sockets


 - realmemory


The autodetected parameters are placed in the NodeName line in slurm.conf .
The Slurm client role parameters can be modified. For example Core Spec Count :


**Example**


[basecm11->configurationoverlay[slurm-client]->roles]% set slurmclient corespeccount 2

[basecm11->configurationoverlay*[slurm-client*]->roles*]% commit


As usual, values set at node level override the values set at categories and configuration overlays
level.

For example, to set corespeccount to 4, only for node001 but not for other nodes, the session might
run further as:


**Example**


[basecm11->configurationoverlay[slurm-client]->roles]% device use node001

[basecm11->device[node001]]% roles

[basecm11->device[node001]->roles]% assign slurmclient

[basecm11->device*[node001*]->roles*[slurmclient*]]% set corespeccount 4

[basecm11->device*[node001*]->roles*[slurmclient*]]% commit

Field Message

------------------------ ---------------------------------------------------------------
wlmCluster Error: The WLM cluster should be set

[basecm11->device*[node001*]->roles*[slurmclient*]]% wlm list

Type Name (key) Server nodes Submit nodes Client nodes

------ ------------------------ ------------ ---------------- ---------------
Slurm slurm basecm11 basecm11,node001 node001,node001

[basecm11->device*[node001*]->roles*[slurmclient*]]% set wlmcluster slurm

[basecm11->device*[node001*]->roles*[slurmclient*]]% commit


In the preceding session, the role needs to be assigned at node level with assign slurmclient because it does not initially exist at node level. If it already existed, then use slurmclient could have
been used to descend into that role.

Also in the preceding session, one of the values that the Slurm client needs to know is wlmcluster,
which decides which WLM it is to work with on the cluster. The value is selected from the list of WLM

instance names in wlm mode.

The level of the active role can be seen with the list command. For example, the Slurm client role
assignment at node level is seen here:


**Example**


[basecm11->device[node001]->roles[slurmclient]]% list

Name (key)

----------------------------------
[overlay:slurm-submit] slurmsubmit

slurmclient


Removing the assignment has the list command display the configuration overlay Slurm client role
assignment:


**Example**


**7.5 Configuring And Running Individual Workload Managers** **373**


[basecm11->device[node001]->roles[slurmclient]]% unassign slurmclient; commit

[basecm11->device[node001]->roles[slurmclient]]% list

Name (key)

----------------------------------
[overlay:slurm-submit] slurmsubmit

[overlay:slurm-client] slurmclient


**Slurm Hardware Autodetection For GPUs:** The Slurm GPU auto detect setting is a setting seen in
the session output of page 368. It manages Slurm GRES configuration ( [https://slurm.schedmd.com/](https://slurm.schedmd.com/gres.conf.html)
[gres.conf.html](https://slurm.schedmd.com/gres.conf.html) ) automatically, and can be set:


  - globally, for all Slurm compute nodes in a Slurm instance, from within the wlm mode of cmsh


  - for a particular role, such as in a device role, a category role, and a configuration overlay role for a
Slurm client


**Example**


[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]% set gpuautodetect _<TAB><TAB>_

bcm none nrt nvml off oneapi rsmi


If GPU auto detect is assigned a value, then a corresponding value is assigned to the autodetect parameter in Slurm’s gres.conf file. One out of 7 values can be assigned to GPU auto detect :


1. bcm : to use BCM values, which are the values that CMDaemon automatically puts in for the vendor
(NVIDIA, Intel, AWS, AMD) and for the number of GPUs.


2. none : to not have the autodetect parameter exist in gres.conf . In this case, there is actually no
corresponding value that can be assigned to the autodetect of gres.conf .


3. nrt : to detect AWS Trainium/Inferentia devices. <— not yet, in October 2024, trunk, or bcm10.24.09


4. nvml : to detect NVIDIA GPUs.


5. off : to turn Slurm GPU autodetection off.


6. oneapi : to detect Intel GPUs.


7. rsmi : to detect AMD GPUs


Slurm GPU autodetection is described further on page 390.


**Slurm accounting database configuration in** cmsh **:** After package setup is carried out with
cm-wlm-setup (section 7.3), cmsh can be used to modify the settings for the Slurm accounting database.
Changes can be carried out in the slurm-accounting configuration overlay:


[basecm11->configurationoverlay[slurm-accounting]]% show

Parameter Value

-------------------------------- --------------------------
Name slurm-accounting

Revision

All head nodes no

Priority 500

Nodes node001,node002

Categories

Roles slurmaccounting

Customizations <0 in submode>


**374** **Workload Management**


In the preceding overlay, slurmdbd runs on the accounting node(s). It is possible to run slurmdbd on
both head nodes or on one or two compute nodes, as set in the configuration overlay. It is not possible
to mix up head nodes and compute nodes for this configuration, and it is not possible to run slurmdbd
on more than two nodes.

Further Slurm accounting changes can be carried out within the slurmaccounting role:


[basecm11->configurationoverlay[slurm-accounting]->roles[slurmaccounting]]% show

Parameter Value

-------------------------------- -------------------------
Name slurmaccounting

Revision

Type SlurmAccountingRole

Add services yes

High availability yes

Primary accounting server node001

DbdPort 6819

StorageHost node001

StoragePort 3306

StorageLoc slurm_acct_db

StorageUser slurm


The primaryaccountingserver parameter defines which node is primary, that is, which one is
AccountingStorageHost in slurm.conf . The other node setting in the configuration overlay is the
AccountingStorageBackupHost .
StorageHost, StoragePort, StorageLoc and StorageUser are settings for connecting to the MySQL
database, If these are for an external host, then they must be configured manually so that they are
reachable by the nodes running slurmdbd .
The highavailability parameter sets the high availability mode for slurmdbd . If set to yes, then
the service runs on both nodes at the same time.


**Generic resources (gres) configuration in Slurm:** In order to configure generic resources, the
genericresources mode can be used to set a list of objects. Each object then represents one generic
resource available on nodes.

Each value of name in genericresources must already be defined in the list of GresTypes . The list
of GresTypes is defined in the wlm role for the instance.


**Example**


[basecm11->wlm[slurm]]% get grestypes

gpu


Several generic resources entries can have the same value for name (for example gpu ), but must have
a unique alias. The alias is a string that is used to manage the resource entry in cmsh or in Base View.
The string is enclosed in square brackets in cmsh, and is used instead of the name for the object. The alias
does not affect Slurm configuration.
For example, to add two GPUs for all the nodes in the default category which are of type k20xm, and
to assign them to different CPU cores, the following cmsh commands can be run:


**Example**


[basecm11]% configurationoverlay use slurm-client

[basecm11->configurationoverlay[slurm-client]]% roles

[basecm11->configurationoverlay[slurm-client]->roles*]% use slurmclient

[...[slurmclient]]% genericresources

[...[slurmclient]->genericresources]% add gpu0


**7.5 Configuring And Running Individual Workload Managers** **375**


[...[slurmclient*]->genericresources*[gpu0*]]% set name gpu

[...[slurmclient*]->genericresources*[gpu0*]]% set file /dev/nvidia0

[...[slurmclient*]->genericresources*[gpu0*]]% set cores 0-7

[...[slurmclient*]->genericresources*[gpu0*]]% set type k20xm

[...[slurmclient*]->genericresources*[gpu0*]]% add gpu1

[...[slurmclient*]->genericresources*[gpu1*]]% set name gpu

[...[slurmclient*]->genericresources*[gpu1*]]% set file /dev/nvidia1

[...[slurmclient*]->genericresources*[gpu1*]]% set cores 8-15

[...[slurmclient*]->genericresources*[gpu1*]]% set type k20xm

[...[slurmclient*]->genericresources*[gpu1*]]% commit

[...[slurmclient]->genericresources[gpu1]]% list
Alias (key) Name Type Count File

----------- -------- -------- -------- ---------------
gpu0 gpu k20xm /dev/nvidia0
gpu1 gpu k20xm /dev/nvidia1

[...[slurmclient]->genericresources[gpu1]]%


Typically this configuration is done automatically during the GPU configuration process as outlined
in the GPU Configuration Screens section on page 334, where by default the configuration overlay is
given the name slurm-client-gpu .
In Base View, the navigation path:


Configuration Overlays  - slurm-client-gpu  - Edit  - Roles  - slurmclient  - Edit  - Generic

Resources - ADD


provides the equivalent (figure 7.20):


Figure 7.20: Base View access to NVIDIA GPU configuration options


After the generic resources are committed, BCM updates the gres.conf file.
Since NVIDIA Base Command Manager version 8.2 and higher, a single gres.conf configuration
file, located at /cm/shared/apps/slurm/etc/slurm/gres.conf is used.
If the category consists of node001 and node002, then the entries to the gres.conf file in this case


**376** **Workload Management**


would look like:


**Example**