# **E**

### Example initialize And finalize Scripts

The node-installer executes any initialize and finalize scripts at particular stages of its 13-step run
during node-provisioning (section 5.4). They are sometimes useful for troubleshooting or workarounds
during those stages. The scripts are stored in the CMDaemon database, rather than in the filesystem
as plain text files, because they run before the node’s init process takes over and establishes the final
filesystem.
Default iniitialize and finalize scripts are provided with the default category:


[basecm11->category[default]]% show | grep ize

Initialize script <1.46KiB>

Finalize script <3.4KiB>


**E.1** **When Are They Used?**


The iniitialize and finalize scripts are sometimes used as an alternative configuration option out of
a choice of other possible options (section 3.19.1). As a solution it can be a bit of a hack, but sometimes
there is no reasonable alternative other than using an initialize or finalize script.


**An** initialize **script:** is used well before the init process starts, to execute custom commands before
partitions and mounting devices are checked. Typically, initialize script commands are related to
partitioning, mounting, or initializing special storage hardware. Often an initialize script is needed
because the commands in it cannot be stored persistently anywhere else.


**A** finalize **script:** (also run before init, but shortly before init starts) is used to set a file configuration or to initialize special hardware, sometimes after a hardware check. It is run in order to make
software or hardware work before, or during the later init stage of boot. Thus, often a finalize script
is needed because its commands must be executed before init, and the commands cannot be stored
persistently anywhere else, or it is needed because a choice between (otherwise non-persistent) configuration files must be made based on the hardware before init starts.


**E.2** **Accessing From Base View And** cmsh


The initialize and finalize scripts are accessible for viewing and editing:


  - In Base View, via the Node Categories or Nodes window, under the Settings window. The navigation paths for these are:


**–** Grouping    - Node categories[default]    - Edit    - Settings


**914** **Example** initialize **And** finalize **Scripts**


**–** Devices    - Nodes[node001]    - Edit    - Settings


  - In cmsh, using the category or device modes. The get command is used for viewing the script,
and the set command to start up the default text editor to edit the script. Output is truncated in
the two following examples at the point where the editor starts up:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% category use default

[basecm11->category[default]]% show | grep script

Parameter Value

------------------------------ -----------------------------------------------
Finalize script <1367 bytes>

Initialize script <0 bytes>

[basecm11->category[default]]% set initializescript


**Example**


[basecm11]% device use node001

[basecm11->device[node001]]%

[basecm11->device[node001]]% set finalizescript


**E.3** **Environment Variables Available To** initialize **And** finalize **Scripts**


When CMDaemon is fully up, the environment variables available to CMDaemon scripts are fully available and can be listed by the CMDaemon front-ends (page 72).
That full range of environment variables is not available for initialize and finalize scripts, since
only a subset of the full environment is defined during the stages associated with the scripts.
For the initialize and finalize scripts, node-specific customizations can still be made from a
script using the environment variables that are available. For initialize scripts, this is discussed
briefly in section E.5.1.
For finalize scripts, the available environment variables can be listed using the following script as a
finalizescript :


**Example**


[basecm11->device[node001]]% get finalizescript

#!/bin/bash

#

# All cluster manager environment variables are prefixed with CMD_
# The root / of the running node is always mounted on /localdisk

#


set | grep CMD_ > /localdisk/var/log/node-installer-finalize.env


After the node comes up, the contents of the saved file on that node are the available variables:


**Example**


[root@node001 ~]# cat /var/log/node-installer-finalize.env

CMD_ACTIVE_MASTER_IP=10.141.255.254

CMD_CATEGORY=default

CMD_CHASSIS=

CMD_CHASSIS_IP=0.0.0.0


**E.3 Environment Variables Available To** initialize **And** finalize **Scripts** **915**


CMD_CHASSIS_PASSWORD=

CMD_CHASSIS_SLOT=

CMD_CHASSIS_USERNAME=

...


The following table shows the available variables with some example values:


_Table E: Environment Variables For The_ initialize _And_ Finalize _Scripts_


**Variable** **Example Value**


CMD_ACTIVE_MASTER_IP 10.141.255.254


CMD_CATEGORY default


CMD_CHASSIS chassis01


CMD_CHASSIS_IP 10.141.1.1


CMD_CHASSIS_PASSWORD ADMIN


CMD_CHASSIS_SLOT 1


CMD_CHASSIS_USERNAME ADMIN


CMD_CLUSTERNAME BCM HEAD Cluster


CMD_DEVICE_HEIGHT 1


CMD_DEVICE_POSITION 10


CMD_DEVICE_TYPE SlaveNode


CMD_ETHERNETSWITCH switch01:1


CMD_FSEXPORT__SLASH_cm_SLASH_node-installer_ALLOWWRITE no


CMD_FSEXPORT__SLASH_cm_SLASH_node-installer_HOSTS 10.141.0.0/16


CMD_FSEXPORT__SLASH_cm_SLASH_node-installer_PATH /cm/node-installer


CMD_FSEXPORTS _SLASH_cm_SLASH_node-installer


CMD_FSMOUNT__SLASH_cm_SLASH_shared_DEVICE master:/cm/shared


CMD_FSMOUNT__SLASH_cm_SLASH_shared_FILESYSTEM nfs


CMD_FSMOUNT__SLASH_cm_SLASH_shared_MOUNTPOINT /cm/shared


CMD_FSMOUNT__SLASH_cm_SLASH_shared_OPTIONS rsize=32768,wsize=32768, _\_


hard,intr,async


CMD_FSMOUNT__SLASH_dev_SLASH_pts_DEVICE none


CMD_FSMOUNT__SLASH_dev_SLASH_pts_FILESYSTEM devpts


CMD_FSMOUNT__SLASH_dev_SLASH_pts_MOUNTPOINT /dev/pts


CMD_FSMOUNT__SLASH_dev_SLASH_pts_OPTIONS gid=5,mode=620


CMD_FSMOUNT__SLASH_dev_SLASH_shm_DEVICE none


CMD_FSMOUNT__SLASH_dev_SLASH_shm_FILESYSTEM tmpfs


CMD_FSMOUNT__SLASH_dev_SLASH_shm_MOUNTPOINT /dev/shm


CMD_FSMOUNT__SLASH_dev_SLASH_shm_OPTIONS defaults


CMD_FSMOUNT__SLASH_home_DEVICE master:/home


CMD_FSMOUNT__SLASH_home_FILESYSTEM nfs


_...continues_


**916** **Example** initialize **And** finalize **Scripts**


_Table E: Environment Variables For The_ initialize _And_ Finalize _Scripts...continued_


**Variable** **Example Value**


CMD_FSMOUNT__SLASH_home_MOUNTPOINT home


CMD_FSMOUNT__SLASH_home_OPTIONS rsize=32768,wsize=32768, _\_


hard,intr,async


CMD_FSMOUNT__SLASH_proc_DEVICE none


CMD_FSMOUNT__SLASH_proc_FILESYSTEM proc


CMD_FSMOUNT__SLASH_proc_MOUNTPOINT /proc


CMD_FSMOUNT__SLASH_proc_OPTIONS defaults,nosuid


CMD_FSMOUNT__SLASH_sys_DEVICE none


CMD_FSMOUNT__SLASH_sys_FILESYSTEM sysfs


CMD_FSMOUNT__SLASH_sys_MOUNTPOINT /sys


CMD_FSMOUNT__SLASH_sys_OPTIONS defaults


CMD_FSMOUNTS _[∗]_ _SLASH_dev_SLASH_pts

_SLASH_proc _SLASH_sys

_SLASH_dev_SLASH_shm

_SLASH_cm_SLASH_shared

_SLASH_home


CMD_GATEWAY 10.141.255.254


CMD_HOSTNAME node001


CMD_INSTALLMODE AUTO


CMD_INTERFACE_eth0_IP _[∗∗]_ 10.141.0.1


CMD_INTERFACE_eth0_MTU _[∗∗]_ 1500


CMD_INTERFACE_eth0_NETMASK _[∗∗]_ 255.255.0.0


CMD_INTERFACE_eth0_TYPE _[∗∗]_ physical


CMD_INTERFACES _[∗]_ eth0 eth1 eth2 ipmi0


CMD_IP 10.141.0.1


CMD_MAC 00:00:00:00:00:01


CMD_PARTITION base


CMD_PASSIVE_MASTER_IP 10.141.255.253


CMD_PDUS


CMD_POWER_CONTROL custom


CMD_RACK rack01


CMD_RACK_HEIGHT 42


CMD_RACK_ROOM serverroom


CMD_ROLES sgeclient storage


CMD_SHARED_MASTER_IP 10.141.255.252


CMD_SOFTWAREIMAGE_PATH /cm/images/default-image


CMD_SOFTWAREIMAGE default-image


CMD_TAG 00000000a000


CMD_USERDEFINED1 var1


CMD_USERDEFINED2 var2


_...continues_


**E.4 Using Environment Variables Stored In Multiple Variables** **917**


_Table E: Environment Variables For The_ initialize _And_ Finalize _Scripts...continued_


**Variable** **Example Value**


 - The value for this variable is a string with spaces, not an array. Eg:


CMD_FSMOUNTS="_SLASH_dev_SLASH_pts _SLASH_proc _SLASH_sys _SLASH_dev_SLASH_shm ..."


** The name of this variable varies according to the interfaces available. So,


eth0 can be replaced by eth1, eth2, ipmi0, and so on.


**E.4** **Using Environment Variables Stored In Multiple Variables**


Some data values, such as those related to interfaces ( CMD_INTERFACES_* ), mount points
( CMD_FSMOUNT__SLASH_* ) and exports ( CMD_FSEXPORT__SLASH_cm__SLASH_node-installer_* ) are
stored in multiple variables. The following finalize script set for node001 shows how they can be used:


**Example**


[head->device*[node001*]]% get finalizescript

#!/bin/bash

echo "These are the interfaces:" >> /localdisk/env

CMD_ENV=`env`

function parser {

for s in TYPE IP NETMASK; do

echo $((grep CMD_INTERFACE_${1/:/-}_${s} | grep -Po "[\w.]+$") <<< "${CMD_ENV[@]}")

done

}

for interface in $CMD_INTERFACES

do

read -r type ip mask <<< $(parser $interface)


echo $interface type=$type >> /localdisk/env
echo $interface ip=$ip >> /localdisk/env

echo $interface netmask=$mask >> /localdisk/env

done


The technique of storage of values in a file under the path within the node of /localdisk/ is described later on in section E.5.2. When the node boots up and runs the finalize script, then files stored
under /localdisk/, end up under the path of / after the node is fully up.
The detailed workings of the parser function in the preceding bash script are not easy, but the result is that the parser function returns output so that the interface type, IP address, and netmask are
listed for each interface. The parser works for physical interfaces, VLAN interfaces, and alias interfaces.
For example, if there are two interfaces, eth0 and eth0:1, then the file env might be seen to have the
following data:


**Example**


[root@head ~]# ssh node001 cat /env

These are the interfaces:

eth0 type=physical

eth0 ip=10.141.0.1

eth0 netmask=255.255.0.0

eth0:1 type=alias

eth0:1 ip=10.141.0.2

eth0:1 netmask=255.255.0.0


**918** **Example** initialize **And** finalize **Scripts**


For remotely mounted devices, the name of the environment variables for mount entries have the
following naming convention:


**Description** **Naming Convention**


volume CMD_FSMOUNT_<x>_DEVICE


mount point CMD_FSMOUNT_<x>_MOUNTPOINT


filesystem type CMD_FSMOUNT_<x>_FILESYSTEM


mount point options CMD_FSMOUNT_<x>_OPTIONS


For the names, the entries _<x>_ are substituted with the local mount point path, such as
“ /cm/shared ”, but with the “ / ” character replaced with the text “ _SLASH_ ”. So, for a local
mount point path “ /cm/shared ”, the name of the associated volume environment variable becomes

CMD_FSMOUNT__SLASH_cm_SLASH_shared_DEVICE .
A similar naming convention is applicable to the names of the environment variables for the export
entries:


**Description** **Naming Convention**


exported system writable? CMD_FSEXPORT_<y>_ALLOWWRITE


allowed hosts or networks CMD_FSEXPORT_<y>_HOSTS


path on exporter CMD_FSMOUNT_<y>_PATH


Here, the entry _<y>_ is replaced by the file path to the exported filesystem on the exporting node. This
is actually the same as the value of “ CMD_FSMOUNT_<y>_PATH ”, but with the “ / ” character replaced with
the text “ _SLASH_ ”.
The entries for the local mount values and the export values in the table in section E.3 are the default
values for a newly installed cluster. If the administrator wishes to add more devices and mount entries,
this is done by configuring fsexports on the head node, and fsmounts on the regular nodes, using Base
View or cmsh (section 3.13).


**E.5** **Storing A Configuration To A Filesystem**


**E.5.1** **Storing With Initialize Scripts**
The initialize script (section 5.4.5) runs after the install-mode type and execution have been determined (section 5.4.4), but before unloading specific drivers and before partitions are checked and filesystems mounted (section 5.4.6). Data output cannot therefore be written to a local drive. It can however be
written by the script to the tmpfs, but data placed there is lost quite soon, namely during the pivot_root
process that runs when the node-installer hands over control to the init process running from the local
drive. However, if needed, the data can be placed on the local drive later by using the finalize script
to copy it over from the tmpfs.
Due to this, and other reasons, a finalize script is easier to use for an administrator than an
initialize script, and the use of the finalize script is therefore preferred.


**E.5.2** **Ways Of Writing A Finalize Script To Configure The Destination Nodes**

**Basic Example—Copying A File To The Image**
For a finalize script (section 5.4.11), which runs just before switching from using the ramdrive to using
the local hard drive, the local hard drive is mounted under /localdisk . Data can therefore be written to
the local hard drive if needed, but is only persistent until a reboot, when it gets rewritten. For example,
predetermined configuration files can be written from the NFS drive for a particular node, or they can
be written from an image prepared earlier and now running on the node at this stage, overwriting a


**E.5 Storing A Configuration To A Filesystem** **919**


node-installer configuration:


**Example**


#!/bin/bash

cp /etc/myapp.conf.overwrite /localdisk/etc/myapp.conf


This technique is used in a finalize script example in section 3.19.4, except that an append operation
is used instead of a copy operation, to overcome a network issue by modifying a network configuration
file slightly.
There are three important considerations for most finalize scripts:


1. **Running A Finalize Script Without** exit 0 **Considered Harmful**


**Failed Finalize Script Logic Flow:** For a default configuration without a finalize script, if PXE
boot fails from the network during node provisioning, the node then goes on to attempt booting
from the local drive via iPXE (section 5.1.2).


However, if the configuration has a finalize script, such as in the preceding example, and if the
finalize script fails, then the failure is passed to the node-installer.


**Avoiding Remote Node Hang During A Finalize Script:** exit 0 **Recommended:** If the nodeinstaller fails, then no attempt is made to continue booting, and the node remains hung at that
stage. This is usually undesirable, and can also make remote debugging of a finalize script annoying.


Adding an exit 0 to the end of the finalize script is therefore recommended, and means that an
error in the script will still allow the node-installer to continue with an attempt to boot from the
local drive.


**Debugging Tips When A Node Hangs During A Finalize Script:** If there is a need to understand
the failure, then if the node-installer hangs, the administrator can ssh into the node into the nodeinstaller environment, and run the finalize script manually to debug it. Once the bug has been
understood, the script can be copied over to the appropriate location in the head node, for nodes
or categories.


Additional aid in understanding a failure may be available by looking through the nodeinstaller logs. The debug mode for the node-installer can be enabled by setting debug=true instead of debug=false in the file /cm/node-installer/scripts/node-installer.conf (for multiarch/multidistro configurations the path takes the form: /cm/node-installer- _<distribution>-_
_<architecture>_ /scripts/node-installer.conf ).


Another way to help debug a failure could be by setting custom event messages in the script, as
explained on page 627.


2. **Protecting A Configuration File Change From Provisioning Erasure With** excludelistupdate


In the preceding example, the finalize script saves a file /etc/myapp.conf to the destination nodes.


To protect such a configuration file from erasure, its file path must be covered in the second sublist
in the excludelistupdate list (section 5.6.1).


3. **Finalize scripts cannot modify** /proc **,** /sys **, and** /dev **filesystems of end result on node directly.**


The /proc, /sys, and /dev filesystems are unmounted after the finalize script is run before pivoting
into the root filesystem under the /localdisk directory, which means any changes made to them


**920** **Example** initialize **And** finalize **Scripts**


are simply discarded. To change values under these filesystems on the node, an rc.local file
inside the software image can be used.


For example, if swappiness is to be set to 20 via the /proc filesystem, one way to do it is to set it in
the rc.local file:


**Example**


# cat /cm/images/< _image-name_ >/etc/rc.local | grep -v �# | grep .
echo 20 > /proc/sys/vm/swappiness

exit 0

# chmod 755 /cm/images/< _image-name_ >/etc/rc.d/rc.local # must be made executable


The preceding way of using rc.local set to run a command to modify the image just for illustration. A better way to get the same result in this case would be to not involve rc.local, but to add
a line within the /cm/images/< _image-name_ >/etc/sysctl.conf file:


vm.swappiness = 20


**Copying A File To The Image—Decision Based On Detection**
Detection within a basic finalize script is useful extra technique. The finalize script example of
section 3.19.4 does detection too, to decide if a configuration change is to be done on the node or not.
A further variation on a finalize script with detection is a script selecting from a choice of possible
configurations. A symlink is set to one of the possible configurations based on hardware detection or
detection of an environment variable. The environment variable can be a node parameter or similar,
from the table in section E.3. If it is necessary to overwrite different nodes with different configurations,
then the previous finalize script example might become something like:


**Example**


#!/bin/bash

if [[ $CMD_HOSTNAME = node00[1-7] ]]

then ln -s /etc/myapp.conf.first /localdisk/etc/myapp.conf

fi

if [[ $CMD_HOSTNAME = node01[5-8] ]]

then ln -s /etc/myapp.conf.second /localdisk/etc/myapp.conf

fi

if [[ $CMD_HOSTNAME = node02[3-6] ]]

then ln -s /etc/myapp.conf.third /localdisk/etc/myapp.conf

fi


In the preceding example, the configuration file in the image has several versions:
/etc/myapp.conf.<first|second|third> . Nodes node001 to node007 are configured with the
first version, nodes node015 to node018 with the second version, and nodes node023 to node026 with
the third version. It is convenient to add more versions to the structure of this decision mechanism.


**Copying A File To The Image—With Environment Variables Evaluated In The File**
Sometimes there can be a need to use the CMDaemon environment variables within a finalize script to
specify a configuration change that depends on the environment.
For example a special service may need a configuration file, test, that requires the hostname myhost,
as a parameter=value pair:


**Example**


**E.5 Storing A Configuration To A Filesystem** **921**


SPECIALSERVICEPARAMETER=myhost


Ideally the placeholder value myhost would be the hostname of the node rather than the fixed value
myhost . Conveniently, the CMDaemon environment variable CMD_HOSTNAME has the name of the host as
its value.

So, inside the configuration file, after the administrator changes the host name from its placeholder
name to the environment variable:


SPECIALSERVICE=${CMD_HOSTNAME}


then when the node-installer runs the finalize script, the file could be modified in-place by the finalize
script, and ${CMD_HOSTNAME} be substituted by the actual hostname.
A suitable finalize Bash script, which runs an in-line Perl substitution, is the following:


#!/bin/bash

perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' /localdisk/some/directory/file


Here, /some/directory/file means that, if for example the final configuration file path for the node
is to be /var/spool/test then the file name should be set to /localdisk/var/spool/test inside the
finalize script.
The finalize script replaces all lines within the file that have environment variable names of the form:


PARAMETER=${< _environment variable name_ >}


with the value of that environment variable. Thus, if < _environment variable name_  - is CMD_HOSTNAME,
then that variable is replaced by the name of the host.


**E.5.3** **Restricting The Script To Nodes Or Node Categories**
As mentioned in section 2.1.3, node settings can be adjusted within a category. So the configuration
changes to ifcfg-eth0 is best implemented per node by accessing and adjusting the finalize script
per node if only a few nodes in the category are to be set up like this. If all the nodes in a category are to
be set up like this, then the changes are best implemented in a finalize script accessed and adjusted at
the category level. Accessing the scripts at the node and category levels is covered in section E.2.
People used to normal object inheritance behavior should be aware of the following when considering category level and node level finalize scripts:
With objects, a node item value overrules a category level value. On the other hand, finalize scripts,
while treated in an analogous way to objects, cannot always inherit properties from each other in the
precise way that true objects can. Thus, it is possible that a finalize script run at the node level may not
have anything to do with what is changed by running it at the category level. However, to allow it to
resemble the inheritance behavior of object properties a bit, the node-level finalize script, if it exists, is
always run after the category-level script. This gives it the ability to “overrule” the category level.


# **F**

### **Workload Managers Quick** **Reference**

**F.1** **Slurm**


Slurm is a GPL-licensed workload management system and developed largely at Lawrence Livermore
National Laboratory. The name was originally an acronym for Simple Linux Utility for Resource Management, but the acronym is deprecated because it no longer does justice to the advanced capabilities of
Slurm.

The Slurm service and outputs are normally handled using the Base View or cmsh front end tools for
CMDaemon (section 7.4).
From the command line, direct Slurm commands that may sometimes come in useful include the
following:


 - sacct : used to report job or job step accounting information about active or completed jobs.


**Example**


# sacct -j 43 -o jobid,AllocCPUs,NCPUS,NNodes,NTasks,ReqCPUs

JobID AllocCPUS NCPUS NNodes NTasks ReqCPUS

------------ ---------- ---------- -------- -------- -------
43 1 1 1 1


 - salloc : used to allocate resources for a job in real time. Typically this is used to allocate resources
and spawn a shell. The shell is then used to execute srun commands to launch parallel tasks.


 - sattach used to attach standard input, output, and error plus signal capabilities to a currently
running job or job step. One can attach to and detach from jobs multiple times.


 - sbatch : used to submit a job script for later execution. The script typically contains one or more
srun commands to launch parallel tasks.


 - sbcast : used to transfer a file from local disk to local disk on the nodes allocated to a job. This can
be used to effectively use diskless compute nodes or provide improved performance relative to a
shared filesystem.


 - scancel : used to cancel a pending or running job or job step. It can also be used to send an
arbitrary signal to all processes associated with a running job or job step.


 - scontrol : the administrative tool used to view and/or modify Slurm state. Note that many scontrol commands can only be executed as user root.


**Example**


**924** **Workload Managers Quick Reference**


[fred@basecm11 ~]$ scontrol show nodes

NodeName=basecm11 Arch=x86_64 CoresPerSocket=1

CPUAlloc=0 CPUErr=0 CPUTot=1 CPULoad=0.05 Features=(null)

...


If a node, for example node001, is stuck in a CG state (“completing”), and rebooting it is not feasible,
then the following may clear it in some cases:


**Example**


[fred@basecm11 ~]$ scontrol update nodename=node001 state=down reason=hung

[fred@basecm11 ~]$ scontrol update nodename=node001 state=resume


 - sinfo : reports the state of partitions and nodes managed by Slurm. It has a wide variety of filtering, sorting, and formatting options.


**Example**


basecm11:~ # sinfo -o "%9P %.5a %.10l %.6D %.6t %C %N"

PARTITION AVAIL TIMELIMIT NODES STATE CPUS(A/I/O/T) NODELIST

defq* up infinite 1 alloc 1/0/0/1 basecm11


 - smap : reports state information for jobs, partitions, and nodes managed by Slurm, but graphically
displays the information to reflect network topology.


 - squeue : reports the state of jobs or job steps. It has a wide variety of filtering, sorting, and formatting options. By default, it reports the running jobs in priority order and then the pending jobs in
priority order.


**Example**


basecm11:~ # squeue -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %C %R"

JOBID PARTITION NAME USER ST TIME NODES CPUS NODELIST(REASON)

43 defq bash fred R 16:22 1 1 basecm11

...


 - srun : used to submit a job for execution or initiate job steps in real time. srun has a wide variety of
options to specify resource requirements, including: minimum and maximum node count, processor count, specific nodes to use or not use, and specific node characteristics (so much memory, disk
space, certain required features, etc.). A job can contain multiple job steps executing sequentially
or in parallel on independent or shared nodes within the job’s node allocation.


**Auto Scaler dynamic node issues with** srun **:** A concern about srun ( [https://bugs.schedmd.](https://bugs.schedmd.com/show_bug.cgi?id=1333)
[com/show_bug.cgi?id=1333](https://bugs.schedmd.com/show_bug.cgi?id=1333) ) at the time of writing (January 2023) is the following: After an srun
job has been queued, and a new node is added, the slurm.conf file is not read again. This means
that the new node resource is not seen by jobs using srun . Thus, with srun jobs, nodes launched
dynamically by Auto Scaler remain unused, and can fail. Workarounds are to use salloc or
sbatch instead of srun .


 - smap : reports state information for jobs, partitions, and nodes managed by Slurm, but graphically
displays the information to reflect network topology.


 - strigger : used to set, get or view event triggers. Event triggers include things such as nodes
going down or jobs approaching their time limit.


**F.2 PBS Professional** **925**


 - sview : a graphical user interface to get and update state information for jobs, partitions, and nodes
managed by Slurm.


There are man pages for these commands. Full documentation on Slurm is available online at: [http:](http://slurm.schedmd.com/documentation.html)
[//slurm.schedmd.com/documentation.html](http://slurm.schedmd.com/documentation.html) .


**F.2** **PBS Professional**


The following commands can be used in PBS Professional to view queues, jobs, and server status:


qstat query queue status

qstat -a show only queued or running jobs for a destination, or all states for a job ID

qstat -r show only running or suspended jobs for a destination, or all states for a job ID

qstat -q show queue status for destinations
qstat -rn only running or suspended jobs, with list of allocated nodes (exec_host string)

qstat -i information on queued, held, waiting jobs is given for specified destination. Inform
ation about the job is given if a job ID is specified, regardless of the job status

qstat -B display server status for the specified servers

qstat -u < _username_ - show jobs for a user for the specified destination. Status

information for the job is displayed for a specified job ID.


Other useful commands are:


tracejob < _job id_ - show what happened today to < _job id_ tracejob -n < _number_ - < _job id_ - search last < _number_ - days for < _job id_ 

qmgr administrator interface to batch system ( man qmgr.8B for more details)


qterm terminates PBS server (but BCM starts pbs_server again)


pbsnodes < _node_ - query status of compute node

pbsnodes -a query status of all compute nodes


The commands of PBS Professional are documented in the man pages, and also in the extensive documentation available via [https://community.altair.com/community?id=altair_product_](https://community.altair.com/community?id=altair_product_documentation)

[documentation](https://community.altair.com/community?id=altair_product_documentation) .


# **G**

### **Metrics, Health Checks,** **Enummetrics, And Actions**

This appendix describes the metrics (section G.1), health checks (section G.2), enummetrics (section 10.2.2), and actions (section G.4), along with their parameters, in a newly-installed cluster. Metrics, health checks, enummetrics, and actions can each be standalone scripts, or they can be built-ins.
Standalone scripts can be those supplied with the system, or they can be custom scripts built by the
administrator. Scripts often require environment variables (as described in section 3.3.1 of the _Developer_
_Manual_ . On success scripts must exit with a status of 0, as is the normal practice.


**G.1** **Metrics And Their Parameters**


A list of metric names can be viewed, for example, for the head node, using cmsh as follows (section 10.5.3):


[basecm11 ~]# cmsh -c "monitoring measurable; list metric"


The metrics listed in this section are classed into 10 kinds:


1. regular metrics (section G.1.1)


2. NFS metrics (section G.1.2)


3. InfiniBand metrics (section G.1.3)


4. monitoring system metrics (section G.1.4)


5. GPU metrics (section G.1.6)


6. Job metrics (section G.1.8)


7. IPMI metrics (section G.1.9)


8. Redfish metrics (section G.1.10)


9. SMART metrics (section G.1.11)


10. Prometheus metrics (section G.1.12)


**928** **Metrics, Health Checks, Enummetrics, And Actions**


**G.1.1** **Regular Metrics**


_Table G.1.1: List Of Metrics_


**Metric** **Description**


AlertLevel Indicates the healthiness of a device based on severity of events
(section 10.2.8). The lower it is, the better. There are 3 parameters
it can take:


                - count : the number of active triggers


                - maximum : the maximum alert level of all active triggers


                - sum : the summed alert level of all active triggers


BlockedProcesses Blocked processes waiting for I/O


BufferMemory System memory used for buffering

BytesRecv _[∗]_ [,‡] Bytes/s received

BytesSent _[∗]_ [,‡] Bytes/s sent


CPUGuest _[∗]_ CPU time spent in guest mode (Jiffies/s)


CPUIdle _[∗]_ CPU time spent in idle mode (Jiffies/s)


CPUIrq _[∗]_ CPU time spent in servicing IRQ (Jiffies/s)


CPUNice _[∗]_ CPU time spent in nice mode (Jiffies/s)


CPUSoftIrq _[∗]_ CPU time spent in servicing soft IRQ (Jiffies/s)


CPUSteal _[∗]_ CPU time spent in steal mode (Jiffies/s)


CPUSystem _[∗]_ CPU time spent in system mode (Jiffies/s)


CPUUser _[∗]_ CPU time spent in user mode (Jiffies/s)


CPUUsage _[∗]_ Percent of time not spent in idle mode (sum of non-idling percentages) (%/s)


CPUWait _[∗]_ CPU time spent in I/O wait mode (Jiffies/s).


CacheMemory System memory used for caching.


Cores Number of cores for a node


CoresDown Number of cores for all nodes marked as DOWN


CoresTotal Total number of known cores for all nodes


CoresUp Number of cores for all nodes marked as UP


CtxtSwitches _[∗]_ Context switches/s


DPUNodesClosed Number of DPUs not marked as UP or DOWN


DPUNodesDown Number of DPUs marked as DOWN


DPUNodesTotal Total number of DPUs


DPUNodesUp Number of DPUs not marked as UP or DOWN


DevicesClosed Number of devices not marked as UP or DOWN


DevicesDown Number of devices marked as DOWN


DevicesTotal Total number of devices


_...continues_


**G.1 Metrics And Their Parameters** **929**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


DevicesUp Number of devices in status UP. A node (head, regular, virtual,
cloud) or GPU Unit is not classed as a device. A device can be an
item such as a switch, PDU, chassis, or rack, if the item is enabled
and configured for management.

DropRecv _[∗]_ [,‡] Packets/s received and dropped

DropSent _[∗]_ [,‡] Packets/s sent and dropped


EC2SpotPrice Amazon EC2 price for spot instances


EccDBitGPU _[∗∗]_ Total number of double bit ECC errors/s (file: sample_gpu )


EccSBitGPU _[∗∗]_ Total number of single bit ECC errors/s (file: sample_gpu )

ErrorsRecv _[∗]_ [,‡] Packets/s received with error


ErrorsSent _[∗]_ [,‡] Packets/s sent with error


FPGAsDown Number of FPGAs for all nodes marked as DOWN


FPGAsTotal Total number of known FPGAs for all nodes


FPGAsUp Number of FPGAs for all nodes marked as UP


FabricTopologies Number of fabric topologies


FabricTopologyHostUsage Average usage of all topology hosts


FabricTopologyResourceBoxUsage Average usage of all topology resource boxes


Forks _[∗]_ Forked processes/s

FrameErrors _[∗]_ [,‡] Packet framing errors/s

FreeFiles [§] Free file inodes on the specified mount point

FreeSpace [§] Free space for non-root user. Takes mount point as a parameter


GPUUnitsClosed Number of GPU units not marked as UP or DOWN


GPUUnitsDown Number of GPU units marked as DOWN


GPUUnitsTotal Total number of GPU Units


GPUUnitsUp Number of GPU units marked as UP


GPUsTotal Total number of known GPUs for all nodes


GPUsUp Number of GPUs for all nodes marked as UP


GPUsDown Number of GPUs for all nodes marked as DOWN


HardwareCorruptedMemory Hardware corrupted memory detected by ECC

IOInProgress [†] I/O operations in progress

IOTime _[∗]_ [,†] I/O operations time in milliseconds/s


InterfaceState Interface operation state


IpForwDatagrams _[∗]_ Input IP datagrams/s to be forwarded/s


IpFragCreates _[∗]_ IP datagram fragments/s generated/s


IpFragFails _[∗]_ IP datagrams/s which needed to be fragmented but could not


IpFragOKs _[∗]_ IP datagrams/s successfully fragmented


IpInAddrErrors _[∗]_ Input datagrams/s discarded because the IP address in their
header was not a valid address


IpInDelivers _[∗]_ Input IP datagrams/s successfully delivered


IpInDiscards _[∗]_ Input IP datagrams/s discarded


_...continues_


**930** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


IpInHdrErrors _[∗]_ Input IP datagrams/s discarded due to errors in their IP headers


IpInReceives _[∗]_ Input IP datagrams/s, including ones with errors, received from
all interfaces


IpInUnknownProtos _[∗]_ Input IP datagrams/s received but discarded due to an unknown
or unsupported protocol


IpOutDiscards _[∗]_ Output IP datagrams/s discarded


IpOutNoRoutes _[∗]_ Output IP datagrams/s discarded because no route could be
found


IpOutRequests _[∗]_ Output IP datagrams/s supplied to IP in requests for transmission


IpReasmOKs _[∗]_ IP datagrams/s successfully re-assembled


IpReasmReqds _[∗]_ IP fragments/s received needing re-assembly


JobsRunning Jobs running on the node


LiteNodesClosed Number of lite nodes not marked as UP or DOWN


LiteNodesDown Number of lite nodes marked as DOWN


LiteNodesTotal Total number of lite nodes


LiteNodesUp Number of lite nodes marked as UP


LoadFifteen Load average on 15 minutes


LoadFive Load average on 5 minutes


LoadOne Load average on 1 minute


MajorPageFaults _[∗]_ Page faults/s that require I/O


ManagedServicesOk This metric uses the ManagedServicesOk health check (page 971)
for a grouping of nodes, such as the nodes in a category, or the
nodes in a cluster. A parameter is specified for the metric, and a
value is returned, as follows:


                - fail : Total number of health checks in a FAIL state


                - good : Percentage that are in the PASS state


                - pass : Total number that are in the PASS state


                - total : Total number of the ManagedServicesOk metrics
being sampled, regardless of state


                - unknown : Total number that are in the UNKNOWN state


_...continues_


**G.1 Metrics And Their Parameters** **931**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


ManagedSwitchesClosed Number of managed switches not marked as UP or DOWN


ManagedSwitchesDown Number of managed switches marked as DOWN


ManagedSwitchesTotal Number of managed switches not marked as UP or DOWN


ManagedSwitchesUp Total number of managed switches


MemoryAvailable Available system memory


MemoryFree Free system memory


MemoryTotal Total system memory

MemoryUsed [¶] Used system memory for a process specified as a parameter. Processes can be anything that is always running:


**Example**


                - cm-lite-daemon


                - cm-mqtt


                - cmd


                - mysqld


                - promtail


                - slurmctld


                - slurmd


MemoryUtilization Memory utilization

MergedReads _[∗]_ [,†] Merged reads/s

MergedWrites _[∗]_ [,†] Merged writes/s


NodesClosed Number of nodes not marked as UP or DOWN


NodesDown Number of nodes marked as DOWN


NodesTotal Total number of nodes


NodesUp Number of nodes in status UP


Cluster occupation rate—a normalized cluster load percentage.
OccupationRate
100% means all cores on all nodes are fully loaded.


The calculation is done as follows: LoadOne on each node is

mapped to a value, calibrated so that LoadOne =1 corresponds to
100% per node. The maximum allowed for a node in the mapping is 100%. The average of these mappings taken over all nodes
is the OccupationRate .


A high value can indicate the cluster is being used optimally.
However, a value that is 100% most of the time suggests the cluster may need to be expanded.


OOM kill Number of processes killed by OOM killer since boot

PacketsRecv _[∗]_ [,‡] Packets/s received


PacketsSent _[∗]_ [,‡] Packets/s sent


PageFaults _[∗]_ Page faults/s


_...continues_


**932** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


PageIn _[∗]_ Number of bytes the system has paged in from disk/s


PageOut _[∗]_ Number of bytes the system has paged out to disk/s


PageSwapIn _[∗]_ Number of bytes the system has swapped in from disk/s


PageSwapOut _[∗]_ Number of bytes the system has swapped out to disk/s


PDUBankLoad Total PDU bank load, in amps


PDULoad Total PDU phase load, in amps


PDUUptime _[∗]_ PDU uptime per second. I.e. ideally=1, but in practice has jitter
effects.


PhaseLoad Sum of PDULoad over all power distribution units


ProcessCount [Total number of all processes in the OS. These are run-](https://linux.die.net/lkmpg/x1052.html)
ning processes ( [RunningProcesses](https://linux.die.net/lkmpg/x1052.html) ) and blocked processes( [BlockedProcesses](https://linux.die.net/lkmpg/x1052.html) ).

ReadOnly [§] Indicates if the specified mount point was mounted as read-only

ReadTime _[∗]_ [,†] Read time in milliseconds/s

Reads _[∗]_ [,†] Reads/s completed successfully


RunningProcesses Running processes


ReportedSpeed Speed reported by the port of the switch. The parameter name
used is the hardware port name, as specified by the output of
the switchoverview command. For example, for the Cumulus
switch these can be swp0, swp1 ...

SectorsRead _[∗]_ [,†] Sectors/s read successfully/s

SectorsWritten _[∗]_ [,†] Sectors/s written successfully


SwapCached Cached swap memory


SwapFree Free swap memory


SwapTotal Total swap memory


SwapUsed Used swap memory


SwapUtilization Swap memory utilization

SystemTime [¶] System time used by process specified by a parameter, for example: cmd


SwitchBroadcastPackets _[∗]_ Total number of good packets received and directed to the broadcast address/s


SwitchCollisions _[∗]_ Collisions/s on this network segment


SwitchCPUUsage Switch CPU utilization estimation (%)


SwitchDelayDiscardFrames _[∗]_ Frames discarded/s due to excessive transit delay through the
bridge


SwitchFilterDiscardFrames _[∗]_ Valid frames received/s but discarded by the forwarding process


SwitchMTUDiscardFrames _[∗]_ Number of frames discarded/s due to an excessive size


SwitchMulticastPackets _[∗]_ Total number of good packets/s received and directed to a multicast address


SwitchOverSizedPackets _[∗]_ Well-received packets/s longer than 1518 octets


SwitchUnderSizedPackets _[∗]_ Packets/s received which are less than 64 octets long


_...continues_


**G.1 Metrics And Their Parameters** **933**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


SwitchUptime _[∗]_ Switch uptime per second. Ie, ideally=1, but in practice has jitter
effects


TcpCurrEstab TCP connections that are either ESTABLISHED or CLOSE-WAIT


TcpInErrs _[∗]_ Input IP segments/s received in error


TcpRetransSegs _[∗]_ Total number of IP segments/s re-transmitted

ThreadsUsed [¶] Threads used by process. For example: cmd


TotalBytesRecv Total bytes received on swp interfaces over all managed switches


TotalBytesSent Total bytes sent on swp interfaces over all managed switches


TotalCPUIdle Cluster-wide core usage in idle tasks (sum of all CPUIdle metric
percentages)


TotalCPUPowerUsage Total CPU power usage over all nodes


TotalCPUSystem Cluster-wide core usage in system mode (sum of all CPUSystem
metric percentages)


TotalCPUTemperature Average CPU temperature over all nodes


TotalCPUUser Cluster-wide core usage in user mode (sum of all CPUUser metric percentages)


TotalCPUUtilization Sum of CPUUsage over all nodes


TotalGPUMemoryUtilization Average of GPU memory utilization percentage
gpu_mem_utilization:average (table G.1.6) over all nodes


TotalGPUNvlinkBandwidth Total GPU Nvlink bandwidth using
gpu_nvlink_total_bandwidth:total (table G.1.6) over all
nodes


TotalGPUPowerUsage Total GPU power usage, using gpu_power_usage:total (table G.1.6) over all nodes


TotalGPUTemperature Average of average GPU temperature using
gpu_temperature:average (table G.1.6) over all nodes


TotalGPUUtilization Average of GPU utilization using gpu_utilization:average (table G.1.6) over all nodes


TotalMemory Sum of MemoryTotal over all nodes


TotalMemoryFree Cluster-wide total of memory free


TotalMemoryUsed Cluster-wide total of memory used


TotalMemoryUtilization Sum of MemoryUtilization over all nodes


TotalNodePowerUsage Total power usage over all nodes


TotalSwap Sum of SwapTotal over all nodes


TotalSwapFree Cluster-wide total swap free


TotalSwapUsed Cluster-wide total swap used


TotalUser Total number of known users


TotalUserLogin Total number of logged in users


UdpInDatagrams _[∗]_ Input UDP datagrams/s delivered to UDP users


UdpInErrors _[∗]_ Input UDP datagrams/s received that could not be delivered/s
for other reasons (no port excl.)


_...continues_


**934** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


UdpNoPorts _[∗]_ Received UDP datagrams/s for which there was no application
at the destination port


UniqueUserLogin Number of unique users logged in


UnmanagedNodesClosed Number of unmanaged nodes not marked as UP or DOWN


UnmanagedNodesDown Number of unmanaged nodes marked as DOWN


UnmanagedNodesTotal Total number of unmanaged nodes


UnmanagedNodesUp Number of unmanaged nodes marked as UP


Uptime _[∗]_ System uptime per second. Ie, ideally=1, but in practice has jitter
effects


UsedFiles [§] Used file inodes on the specified parameter as mount point

UsedSpace [§] Used space on the specified parameter as mount point

UserTime [¶] User time used by specified process. For example: cmd

Utilization [¶] Utilization by specified process. For example; cmd

VirtualMemoryUsed [¶] Virtual memory used by specified process. For example cmd


WlmSlotsFree The number of WLM slots free


WlmSlotsTotal The total number of WLM slots


WlmSlotsUsed The number of WLM slots in use


WlmSlotsUtilization The percentage of WLM slots in use


wlm_slurm_state_count Number of nodes in the state for a parameter. The possible pa
rameters are:


                - allocated


                - completing


                - down


                - drain


                - draining


                - fail


                - failing


                - idle


                - maint


                - mixed


_...continues_


**G.1 Metrics And Their Parameters** **935**


_Table G.1.1: List Of Metrics...continued_


**Metric** **Description**


WriteTime _[∗]_ [,†] Write time in milliseconds/s (this is a per mille), for the parameter as device


Writes _[∗]_ [,†] Writes/s completed successfully for the parameter as device


isilon_node_disk_access_latency Isilon access latency for node disk


isilon_node_disk_iosched_queue Isilon iosched queue for node disk


isilon_node_disk_xfer_size_in Transfer size in for node disk


isilon_node_disk_xfer_size_out Transfer size out for node disk


isilon_node_ip IP address of isilon node


isilon_in_rate Bytes written to NFS client from Isilon


isilon_out_rate Bytes read from Isilon to NFS client


isilon_op_rate I/O rate for NFS client to/from Isilon


node_network_carrier_changes_ Samples total network carrier changes

total


nvidia_licensed_compute_ Total licensed compute resources

resources


nvidia_used_compute_resources Used compute resources, (maximum of nodes used and GPUs
used, but value can only be up to the total licensed compute resources)


nvidia_used_gpu_resources Used GPU resources


nvidia_used_node_resources Used node resources


nvidia_used_node_resources Used node resources


 - Cumulative metric. I.e. the metric is derived from cumulative raw measurements taken at two different times, according to:
_metric_ _time_ 2 = _[measurement]_ _time_ [2] 2 _[−]_ _−_ _[measurement]_ _time_ 1 [1]


The metric is a “per second” measurement.
** Standalone scripts, not built-ins.
If sampling from a head node, the script is in directory: /cm/local/apps/cmd/scripts/metrics/
For regular nodes, the script is in directory: /cm/images/default-image/cm/local/apps/cmd/scripts/metrics/

 - Takes block device name ( sda, sdc, nvme0n1 and so on) as parameter

 - Takes interface device name ( eth0, eth1, en01, docker0, ib0 and so on) as parameter

§ Takes mount point (for example: /, or /var ) as parameter

 - Takes a process, eg: cmd as a parameter


**G.1.2** **NFS Metrics**

The NFS metrics are all cumulative. They correspond to nfsstat output, and are shown in table G.1.2.


_Table G.1.2: NFS Metrics_


**NFS Metric** **Description**


nfs_client_packet_packets NFS client packets statistics: packets


nfs_client_packet_tcp NFS client package statistics: TCP/IP packets


nfs_client_packet_tcpconn NFS client package statistics: TCP/IP connections


_...continues_


**936** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.2: NFS Metrics_


**NFS Metric** **Description**


nfs_client_packet_udp NFS client package statistics: UDP packets


nfs_client_rpc_authrefrsh NFS Client RPC statistics: authenticated refreshes to RPC

server


nfs_client_rpc_calls NFS Client RPC statistics: calls


nfs_client_rpc_retrans NFS Client RPC statistics: re-transmissions


nfs_server_file_anon NFS Server file statistics: anonymous access


nfs_server_file_lookup NFS Server file statistics: look-ups


nfs_server_file_ncachedir NFS Server file statistics: ncachedir


nfs_server_file_stale NFS Server file statistics: stale files


nfs_server_packet_packets NFS Server packet statistics: packets


nfs_server_packet_tcp NFS Server packet statistics: TCP/IP packets


nfs_server_packet_tcpconn NFS Server packet statistics: TCP/IP connections


nfs_server_packet_udp NFS Server packet statistics: UDP packets


nfs_server_reply_hits NFS Server reply statistics: hits


nfs_server_reply_misses NFS Server reply statistics: misses


nfs_server_reply_nocache NFS Server reply statistics: no cache


nfs_server_rpc_badauth NFS Server RPC statistics: bad authentication


nfs_server_rpc_badcalls NFS Server RPC statistics:bad RPC requests


nfs_server_rpc_badclnt NFS Server RPC statistics: badclnt


nfs_server_rpc_calls NFS Server RPC statistics: all calls to NFS and NLM


nfs_v3_client_access NFSv3 client statistics: access


nfs_v3_client_create NFSv3 client statistics: create


nfs_v3_client_fsinfo NFSv3 client statistics: static file system information


nfs_v3_client_fsstat NFSv3 client statistics: dynamic file system status


nfs_v3_client_getattr NFSv3 client statistics: file system attributes


nfs_v3_client_lookup NFSv3 client statistics: lookup


nfs_v3_client_pathconf NFSv3 client statistics: configuration path


nfs_v3_client_read NFSv3 client statistics: reads


nfs_v3_client_read_readdirplus NFSv3 client statistics: readdirplus


nfs_v3_client_remove NFSv3 client statistics: removes


nfs_v3_client_settattr NFSv3 client statistics: setattr


nfs_v3_client_total NFSv3 client statistics: total


nfs_v3_client_write NFSv3 client statistics: writes


nfs_v3_server_access NFSv3 server statistics: access


nfs_v3_server_create NFSv3 server statistics: create


nfs_v3_server_fsinfo NFSv3 server statistics: static file system information


nfs_v3_server_fsstat NFSv3 server statistics: dynamic file system information


nfs_v3_server_getattr NFSv3 server statistics: file system attributes gets


nfs_v3_server_lookup NFSv3 server statistics: file name look-ups


_...continues_


**G.1 Metrics And Their Parameters** **937**


_Table G.1.2: NFS Metrics_


**NFS Metric** **Description**


nfs_v3_server_mkdir NFSv3 server statistics: directory creation


nfs_v3_server_null NFSv3 server statistics: null operations


nfs_v3_server_pathconf NFSv3 server statistics: retrieve POSIX information


nfs_v3_server_read NFSv3 server statistics: reads


nfs_v3_server_readdirplus NFSv3 server statistics: READDIRPLUS procedures


nfs_v3_server_readlink NFSv3 server statistics: Symbolic link reads


nfs_v3_server_setattr NFSv3 server statistics: file system attribute sets


nfs_v3_server_total NFSv3 server statistics: total


nfs_v3_server_write NFSv3 server statistics: writes


nfs_v4_server_compound NFSv4 server statistics: compound operations


nfs_v4_server_null NFSv4 server statistics: null operations


nfs_v4_server_total NFSv4 server statistics: total


nfs_v4_servop_access NFSv4 server statistics: access


nfs_v4_servop_close NFSv4 server statistics: close


nfs_v4_servop_create NFSv4 server statistics: create


nfs_v4_servop_getattr NFSv4 server statistics: file system attributes gets


nfs_v4_servop_getfh NFSv4 server statistics: filehandle gets


nfs_v4_servop_lookup NFSv4 server statistics: file name look-ups


nfs_v4_servop_open NFSv4 server statistics: opens


nfs_v4_servop_putfh NFSv4 server statistics: filehandle puts


nfs_v4_servop_putrootfh NFSv4 server statistics: filehandle puts to root


nfs_v4_servop_read NFSv4 server statistics: reads


nfs_v4_servop_readdirplus NFSv4 server statistics: READDIRPLUS procedures


nfs_v4_servop_readlink NFSv4 server statistics: Symbolic link reads


nfs_v4_servop_rename NFSv4 server statistics: renames


nfs_v4_servop_savefh NFSv4 server statistics: filehandle saves


nfs_v4_servop_setattr NFSv4 server statistics: file system attribute sets


nfs_v4_servop_total NFSv4 server statistics: total


nfs_v4_servop_write NFSv4 server statistics: writes


**G.1.3** **InfiniBand Metrics**
The available InfiniBand metrics are displayed in table G.1.3.


_Table G.1.3: InfiniBand Metrics_


**InfiniBand Metric** **Description**


_...continues_


**938** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.3: InfiniBand Metrics...continued_


**IB Metric** **Description**


SymbolErrorCount Total number of minor link errors detected on
one or more physical lanes.


LinkErrorRecoveryCount Total number of times the Port Training state machine has successfully completed the link error

recovery process.


LinkDownedCounter Total number of times the Port Training state machine has failed the link error recovery process
and downed the link.


PortRcvErrors Total number of packets containing an error that
were received on the port.


PortRcvRemotePhysicalErrors Total number of packets marked with the EBP
delimiter received on the port.


PortRcvSwitchRelayErrors Total number of packets received on the port that
were discarded because they could not be forwarded by the switch relay.


PortXmitDiscards Total number of outbound packets discarded by
the port because the port is down or congested.


PortXmitConstrainErrors Total number of packets not transmitted from
the switch physical port.


PortRcvConstraintErrors Total number of packets received on the switch
physical port that are discarded.


LocalLinkIntegrityErrors The number of times that the count of local physical errors exceeded the threshold specified by
LocalPhyErrors.


ExcessiveBufferOverrunError The number of times that OverrunErrors consec
utive flow control update periods occurred, each
having at least one overrun error


QP1Dropped Drops on the lower priority QP1 interconnect


VL15Dropped Drops in the highest priority virtual lane 15


PortXmitData Total number of data octets, divided by 4 (lanes),
transmitted on all VLs. This is a 64-bit counter.


PortRcvData Total number of data octets, divided by 4 (lanes),
received on all VLs. This is a 64-bit counter.


PortXmitPkts Total number of packets transmitted on all VLs
from this port, including packets with errors,
and excluding link packets.


PortRcvPkts Total number of packets, including packets containing errors, and excluding link packets, received from all VLs on this port. This is a 64-bit

counter.


PortXmitWait The number of ticks during which the port had
data to transmit but no data was sent during the
entire tick (either because of insufficient credits
or because of lack of arbitration).


**G.1 Metrics And Their Parameters** **939**


**G.1.4** **Monitoring System Metrics**
Internal metrics for the monitoring system itself are produced by the MonitoringSystem data producer.
The data producer does not run by default on any node, as is seen by running the nodes command
(page 585) for it:


[basecm11->monitoring->setup[MonitoringSystem]]% nodes

Not used


However, for convenience, some monitoring system metrics values are displayed on demand in an
organized way, by running the monitoringinfo command for a device:


**Example**


[basecm11->device[basecm11]]% monitoringinfo

Service Queued Handled Cache miss Stopped Suspended Last operation

----------------------------- -------- ---------- ---------- --------- ---------- --------------
Mon::CacheGather 4 910 4 no no Fri Oct 4 ...

Mon::DataConverter 0 0 0 no no 
Mon::DataProcessorEngine 0 155,470 0 no no Fri Oct 4 ...

Mon::DataProcessorKeepLatest 0 155,470 0 no no Fri Oct 4 ...

Mon::DataProcessorKeepRecent 0 0 0 no no 
...


The internal monitoring system metrics can be activated so that their data values are saved. This is
not recommended, except temporarily for debugging purposes. To save the values, the Introspect flag
for the monitoring system data producer should be set to yes :


**Example**


[basecm11->monitoring->setup[MonitoringSystem]]% set --extra Introspect yes

[basecm11->monitoring->setup*[MonitoringSystem*]]% commit

[basecm11->monitoring->setup[MonitoringSystem]]% nodes

basecm11

[basecm11->monitoring->setup[MonitoringSystem]]% get interval

900


After a time defined by interval, the metrics can be viewed:


**Example**


[basecm11->device[basecm11]]% latestmetricdata | grep Mon::Storage
Mon::Storage::Engine::elements Internal/Monitoring/Storage 999,549 44.3s
Mon::Storage::Engine::size Internal/Monitoring/Storage 1.00 GiB 44.3s
Mon::Storage::Engine::usage Internal/Monitoring/Storage 9.63% 44.3s
Mon::Storage::Message::elements Internal/Monitoring/Storage 28 44.3s

...


The monitoring system metrics that are saved are shown in table G.1.4.


**940** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.4: Monitoring System Metrics_


**Monitoring System Metric** **Description**


Mon::CacheGather::handled Cache gathers handled/s


Mon::CacheGather::miss Cache gathers missed/s


Mon::DataProcessor::handled Data processors handled/s


Mon::DataProcessor::miss Data processors missed /s


Mon::DataTranslator::handled Data translators handled/s


Mon::DataTranslator::miss Data translators missed/s


Mon::EntityMeasurableCache::handled Measurable cache handled/s


Mon::EntityMeasurableCache::miss Measurable cache missed/s


Mon::MeasurableBroker::handled Measurable broker handled/s


Mon::MeasurableBroker::miss Measurable broker missed/s


Mon::OOB::TaskService::handled Out-of-band task service handled/s


Mon::OOB::TaskService::miss Out-of-band task service missed/s


Mon::Replicate::Collector::handled Replication collection handled/s


Mon::Replicate::Collector::miss Replication collection missed/s


Mon::Replicate::Combiner::handled Replication combiner handled/s


Mon::Replicate::Combiner::miss Replication combiner missed/s


Mon::RepositoryAllocator::handled Repository allocator handled/s


Mon::RepositoryAllocator::miss Repository allocator missed/s


Mon::RepositoryTrim::handled Repository trim handled/s


Mon::RepositoryTrim::miss Repository trim missed/s


Mon::Storage::Engine::elements Storage engine data elements, in total


Mon::Storage::Engine::size Storage engine size, in bytes


Mon::Storage::Engine::usage Storage engine usage


Mon::Storage::Message::elements Storage message data elements, in total


Mon::Storage::Message::size Storage message size in bytes


Mon::Storage::Message::usage Storage message usage


Mon::Storage::RepositoryId::elements Storage repository ID data elements, in total


Mon::Storage::RepositoryId::size Storage repository ID, size, in bytes


Mon::Storage::RepositoryId::usage Repository ID usage


Mon::TaskInitializer::handled Task initializer handled/s


Mon::TaskInitializer::miss Task initializer missed/s


Mon::TaskSampler::handled Task sampler handled/s


Mon::TaskSampler::miss Task sampler missed/s


Mon::Trigger::Actuator::handled Trigger actuators handled/s


Mon::Trigger::Actuator::miss Trigger actuators missed/s


Mon::Trigger::Dispatcher::handled Trigger dispatchers handled/s


_...continues_


**G.1 Metrics And Their Parameters** **941**


_Table G.1.4: Monitoring System Metrics...continued_


**Monitoring System Metric** **Description**


Mon::Trigger::Dispatcher::miss Trigger dispatchers missed/s


Prometheus::DataTranslator::handled DataTranslator queries handled. The DataTranslator is a translation layer between PromQL format and BCM format sampling.


Prometheus::DataTranslator::miss DataTranslator misses


**G.1.5** **CPU Metrics Sampled By The CPUSampler And GPUSampler**
Some CPU metrics are sampled by the data producers CPUSampler and GPUSampler (table G.1.5):


_Table G.1.5: CPU Metrics Sampled By The CPUSampler And GPUSampler_


**CPU Metric** **Parameter** **Description**


cpu_core_clock_speed _[∗]_ cpu_core0 CPU0 core clock speed


cpu_power_cap_enabled _[∗]_ cpu0 CPU0 power capping enabled


cpu_power_cap_long_term_max_limit _[∗]_ cpu0 Long term CPU0 power constraint


cpu_power_cap_long_term_time_window _[∗]_ cpu0 Long term CPU0 power constraint time
window


cpu_power_cap_short_term_max_limit _[∗]_ cpu0 Short term CPU0 power constraint


cpu_power_cap_short_term_time_window _[∗]_ cpu0 Short term CPU0 power constraint time
window


cpu_power_limit _[∗]_ cpu0 CPU0 power limit


cpu_power_usage _[∗]_ cpu0 CPU0 power usage


cpu_power_usage total Total CPU power usage


cpu_temperature average Average CPU temperature


cpu_temperature _[∗]_ cpu0 CPU0 temperature


cpu_utilization average Average CPU utilization


 - The number 0 in the parameter column can be replaced by the number associated with the core used. Thus:
cpu_core0 can be replaced by cpu_core1, cup_core2 ...


and


cpu0 can be replaced by cpu1, cpu2 ...


**G.1.6** **GPU Metrics**

The data producer (section 10.2.10) for the GPU metrics of this section is GPUSampler .
There were GPU metrics described earlier on in table G.1.1. These were cluster overview metrics

about GPUs, and were provided by the ClusterTotal data producer.
However, the NVIDIA GPU metrics of this section, as the GPUSampler data producer name suggests,
is about gathering the sampled GPU data from the devices themselves.
There is also a separate section about job GPU metrics (section G.1.8, page 950), which uses the
JobSampler data producer, and is about gathering the sampled job data from the GPU devices themselves.

The device parameter for the GPU metrics in this section, unless otherwise noted, specifies the device
slot number that the GPU uses. The parameter takes the form gpu0, gpu1, and so on. It is appended to the
metric with a colon character. For example, the gpu_ecc_dbe_agg metric, if used with gpu1, is specified

as:


**942** **Metrics, Health Checks, Enummetrics, And Actions**


**Example**


gpu_ecc_dbe_agg:gpu1


Available GPU metrics for V100 and A100 GPUs are listed in table G.1.6. The available GPU health

checks for V100 and A100 GPUs are listed in table G.2.2.

If the cluster has been configured with AMD GPUs (section 7.4 of the _Installation Manual_ ) then AMD
GPU metrics become available. Metrics in the table that are also valid AMD GPU metrics are noted.

Some metrics have been added and noted that are only valid for AMD GPUs.
Extra GPU measurables for the GB200 GPUs are listed in section 6.6 of the _NVIDIA Mission Control_

_Manual_ .

_Table G.1.6: GPU Metrics_


**GPU Metric** **Description**


gpu_dec_utilization _[∗]_ GPU decoding usage


gpu_ecc_dbe_agg Total double bit aggregate ECC errors


gpu_ecc_dbe_vol Total double bit volatile ECC errors


gpu_ecc_sbe_agg Total single bit aggregate ECC errors


gpu_ecc_sbe_vol Total single bit volatile ECC errors


gpu_enc_utilization _[∗]_ GPU encoding usage


gpu_enforced_power_limit GPU-enforced power limit


gpu_mem_clock GPU memory clock (also for AMD GPU)


gpu_mem_copy_utilization _[∗]_ Percentage of GPU memory copy used


gpu_mem_free Amount of GPU free memory


gpu_mem_total _[∗∗]_ GPU framebuffer size (also for AMD GPU)


gpu_mem_used _[∗∗]_ Amount of GPU memory used (also for AMD GPU)


gpu_mem_utilization _[∗]_ GPU memory used percentage


gpu_memory_temp _[∗]_ GPU memory temperature (Celsius)


gpu_nvlink_total_bandwidth _[∗∗]_ Total NVLink bandwidth used


gpu_power_management_limit GPU power management limit


gpu_power_usage _[∗∗]_ GPU power usage (also for AMD GPU)


gpu_power_violation _[∗∗]_ Throttling duration due to power constraints


gpu_shutdown_temp GPU shutdown temperature (Celsius)


gpu_slowdown_temp GPU slowdown temperature (Celsius)


gpu_sm_clock GPU shader multiprocessor clock (also for AMD GPU)


_...continues_


**G.1 Metrics And Their Parameters** **943**


_Table G.1.6: GPU Metrics...continued_


**GPU Metric** **Description**


gpu_temperature _[∗]_ GPU temperature (Celsius)


gpu_thermal_violation _[∗∗]_ Throttling duration due to thermal constraints


gpu_utilization _∗_ Average GPU utilization percentage


gpu_xid_error The value is the specific XID error


 - Specified as average, or specified for a GPU.
For example, for the gpu_dec_utilization metric:

gpu_dec_utilization:average or gpu_dec_utilization:GPU0


** Specified as a total, or specified for a GPU.
For example, for the gpu_mem_total metric:

gpu_mem_total:total or gpu_mem_total:GPU0


**G.1.7** **GPU Profiling Metrics**
The data producer (section 10.2.10) for the GPU profiling metrics of this section is GPUSampler .
The device parameter for the GPU profiling metrics in this section, unless otherwise noted, specifies
the device slot number that the GPU uses. The parameter takes the form gpu0, gpu1, and so on. It is
appended to the metric with a colon character. For example, the gpu_profiling_fp64_active metric, if
used with gpu1, is specified as:


**Example**


gpu_profiling_fp64_active:gpu1


Available GPU profiling metrics for V100 and A100 GPUs are listed in table G.1.7.


_Table G.1.6: GPU Profiling Metrics_


**GPU Profiling Metric** **Description**


gpu_profiling_dram_active The ratio of cycles the device memory interface is active
sending or receiving data


gpu_profiling_fp16_active Ratio of cycles the fp16 pipe is active


gpu_profiling_fp32_active Ratio of cycles the fp32 pipe is active


gpu_profiling_fp64_active Ratio of cycles the fp64 pipe is active


gpu_profiling_graphics_engine_active Ratio of time the graphics engine is active. The graphics
engine is active if a graphics/compute context is bound
and the graphics pipe or compute pipe is busy


gpu_profiling_nvlink_read The number of bytes of active NvLink rx (read) data
including both header and payload


_...continues_


**944** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.7: GPU Profiling Metrics...continued_


**GPU Profiling Metric** **Description**


gpu_profiling_nvlink_transmit The number of bytes of active NvLink tx (transmit)
data including both header and payload


gpu_profiling_pcie_read The number of bytes of active PCIe rx (read) data including both header and payload


gpu_profiling_pcie_transmit The number of bytes of active PCIe tx (transmit) data
including both header and payload


gpu_profiling_pipe_tensor_active The ratio of cycles the tensor (HMMA) pipe is active


gpu_profiling_sm_active The ratio of cycles an SM has at least 1 warp assigned


gpu_profiling_sm_occupancy The ratio of cycles the tensor (HMMA) pipe is active


**G.1.8** **Job Metrics**

Job metrics are introduced in section 11.1.


**Basic Job Metrics**

The following table lists some of the most useful job metrics that BCM can monitor and visualize. In the
table, the text < _device_ - denotes a block device name, such as sda .
On virtual machines, block device metrics may be unavailable because of virtualization.


**G.1 Metrics And Their Parameters** **945**


_Table G.1.8.1: Basic Job Metrics_


**Job Metric** **Description** **Cgroup Source File**


blkio.time: < _device_ - Time job had I/O access to de- blkio.time_recursive
vice


blkio.sectors: < _device_ - Sectors transferred to or from blkio.sectors_recursive
specific devices by a cgroup


blkio.io_service_read: < _device_ - Bytes read blkio.io_service_bytes_recursive


blkio.io_service_write: < _device_ - Bytes written blkio.io_service_bytes_recursive


blkio.io_service_sync: < _device_ - Bytes transferred synchronously blkio.io_service_bytes_recursive


blkio.io_service_async: < _device_ - Bytes transferred asyn- blkio.io_service_bytes_recursive
chronously



blkio.io_wait_time_read: < _device_ - Total time spent waiting for service in the scheduler queues for
I/O read operations


blkio.io_wait_time_write: < _device_ - Total time spent waiting for service in the scheduler queues for
I/O write operations


blkio.io_wait_time_sync: < _device_ - Total time spent waiting for service in the scheduler queues for
I/O synchronous operations


blkio.io_wait_time_async: < _device_ - Total time spent waiting for service in the scheduler queues for
I/O asynchronous operations



blkio.io_wait_time_recursive


blkio.io_wait_time_recursive


blkio.io_wait_time_recursive


blkio.io_wait_time_recursive



cpuacct.usage Total CPU time consumed by all cpuacct.usage
job processes


cpuacct.stat.user User CPU time consumed by all cpuacct.stat
job processes


_...continues_


**946** **Metrics, Health Checks, Enummetrics, And Actions**


_...continued_


**Job Metric** **Description** **Cgroup Source File**


cpuacct.stat.system System CPU time consumed by cpuacct.stat
all job processes


memory.usage Total current memory usage memory.usage_in_bytes


memory.memsw.usage Sum of current memory plus memory.memsw.usage_in_bytes

swap space usage


memory.memsw.max_usage Maximum amount of memory memory.memsw.max_usage_in_bytes
and swap space used



memory.failcnt How often the memory limit
has reached the value set in

memory.limit_in_bytes


memory.memsw.failcnt How often the memory
plus swap space limit has
reached the value set in

memory.memsw.limit_in_bytes



memory.failcnt


memory.memsw.failcnt



memory.swap Total swap usage memory


memory.cache Total page cache, including memory
tmpfs (shmem)



memory.mapped_file Size of memory-mapped
mapped files, including tmpfs
(shmem)



memory



memory.unevictable Memory that cannot be re- memory
claimed


The third column in the table shows the precise source file name that is used when the value is
retrieved. These files are all virtual files, and are created as the cgroup controllers are mounted to
the cgroup directory. In this case several controllers are mounted to the same directory, which means
that all the virtual files will show up in that directory, and in its associated subdirectories—job cgroup
directories—when the job runs.


**Advanced Job Metrics**

The metrics in the preceding table are enabled by default. There are also over 40 other advanced metrics
that can be enabled via the Enable Advanced Metrics property of the jobmetricsettings object:


[basecm11->monitoring->setup[JobSampler]->jobmetricsettings]% show

Parameter Value

-------------------------------- -----------------------------------------------
Enable Advanced Metrics no

Exclude Devices loop,sr

Exclude Metrics

Include Devices

Include Metrics

Revision

Sampling Type Both

[basecm11->monitoring->setup[JobSampler]->jobmetricsettings]% set enableadvancedmetrics yes

[basecm11->monitoring->setup*[JobSampler*]->jobmetricsettings*]% commit


**G.1 Metrics And Their Parameters** **947**


The advanced job metrics are:


**948** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.8.2: Advanced Job Metrics_


**Advanced Job Metric** **Description** **Cgroup Source File**



blkio.io_service_time_read: < _device_ - Total time between request
dispatch and request completion according to CFQ
scheduler for I/O read operations


blkio.io_service_time_write: < _device_ - Total time between request
dispatch and request completion according to CFQ
scheduler for I/O write operations


blkio.io_service_time_sync: < _device_ - Total time between request dispatch and request
completion according to
CFQ scheduler for I/O
synchronous operations


blkio.io_service_time_async: < _device_ - Total time between request
dispatch and request completion according to CFQ
scheduler for I/O asynchronous operations



blkio.io_service_time_recursive


blkio.io_service_time_recursive


blkio.io_service_time_recursive


blkio.io_service_time_recursive



blkio.io_serviced_read: < _device_ - Read I/O operations blkio.io_serviced_recursive


blkio.io_serviced_write: < _device_ - Write I/O operations blkio.io_serviced_recursive


blkio.io_serviced_sync: < _device_ - Synchronous I/O opera- blkio.io_serviced_recursive
tions


blkio.io_serviced_async: < _device_ - Asynchronous I/O opera- blkio.io_serviced_recursive
tions



blkio.io_merged_read: < _device_ - Number of block I/Os
(requests) merged into
requests for I/O read
operations


blkio.io_merged_write: < _device_ - Number of block I/Os
(requests) merged into
requests for I/O write
operations


blkio.io_merged_sync: < _device_ - Number of block I/Os
(requests) merged into requests for I/O synchronous
operations


blkio.io_merged_async: < _device_ - Number of block I/Os
(requests) merged into
requests for I/O asynchronous operations


_...continues_



blkio.io_merged_recursive


blkio.io_merged_recursive


blkio.io_merged_recursive


blkio.io_merged_recursive


**G.1 Metrics And Their Parameters** **949**


_...continued_


**Advanced Job Metric** **Description** **Cgroup Source File**


blkio.io_queued_read: < _device_ - Number of requests queued blkio.io_queued_recursive
for I/O read operations


blkio.io_queued_write: < _device_ - Number of requests queued blkio.io_queued_recursive
for I/O write operations



blkio.io_queued_sync: < _device_ - Number of requests queued
for I/O synchronous operations


blkio.io_queued_async: < _device_ - Number of requests queued
for I/O asynchronous operations


memory.rss Anonymous and swap
cache, not including tmpfs
(shmem)



blkio.io_queued_recursive


blkio.io_queued_recursive


memory



memory.pgpgin Number of pages paged memory
into memory


memory.pgpgout Number of pages paged out memory
of memory



memory.active_anon Anonymous and swap
cache on active least
recently-used (LRU) list,
including tmpfs (shmem)


memory.inactive_anon Anonymous and swap
cache on inactive LRU list,
including tmpfs (shmem)



memory


memory



memory.active_file File-backed memory on ac- memory
tive LRU list


memory.inactive_file File-backed memory on in- memory
active LRU list


memory.hierarchical _\_ Memory limit for the memory
_memory_limit Hierarchy that contains the
memory cgroup of job


memory.hierarchical _\_ Memory plus swap limit for memory
_memsw_limit Hierarchy that contains the
memory cgroup of job


**Job Queue Metrics**

Job queue metrics become available after workload manager jobs are run. They are produced by the
JobQueueSampler data producer.


**950** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.1: List Of Job Queue Metrics_


**Metric** **Description**


AvgJobDuration Average job duration of current jobs


AvgJobStartDelay Average job start delay of current jobs


CompletedJobs Successfully completed jobs


CoresInQueue Cores in queue


CoresUPInQueue Active cores in queue


EstimatedDelay Estimated delay time to execute jobs


FailedJobs Failed completed jobs


GPUsInQueue GPUs in queue


GPUsUPInQueue Active GPUs in queue


JobThroughput Average number of Jobs finished


NodesInQueue Number of nodes in the queue


NodesUPInQueue Active nodes in queue


QueuedJobs Queued jobs


RunningJobs Running jobs


RunningJobsMax Maximal running jobs


RunningJobsUtilization Running jobs utilization


**Job GPU Metrics**

The GPU metrics of section G.1.6 have a GPUSampler data producer (section 10.2.10). As the name
suggests, those metrics are about gathering the sampled GPU data from the devices themselves.
The job GPU metrics of this section have a JobSampler data producer. As the name suggests, these
metrics are about gathering the sampled job data from the GPU devices themselves.
In other words, the job GPU metrics are essentially the same metrics as in the GPU metrics section,
but are valid only for the job. This is reflected in their names, which are identical, except for the job_
prefix. Other differences of job GPU metrics in comparison with GPU metrics are that


  - they are sampled only on the node that hosts the GPUs on which the job ran, and do not take
specific GPUs as a parameter.


  - the metrics are listed in the monitoring measurable mode of cmsh only after jobs have run on the
GPUs.


Available job GPU metrics for V100 and A100 GPUs are listed in table G.1.8.
If the cluster has been configured with AMD GPUs (section 7.4 of the _Installation Manual_ ) then AMD
job GPU metrics become available. Metrics in the table that are also valid AMD job GPU metrics are
noted. Some metrics have been added and noted that are only valid for AMD GPUs.


_Table G.1.8: Job GPU Metrics For Node_


**Job GPU Metric** **Description For Job On Node**


job_gpu_dec_utilization GPU decoding usage


_...continues_


**G.1 Metrics And Their Parameters** **951**


_Table G.1.8: Job GPU Metrics For Node...continued_


**Job GPU Metric** **Description For Job On Node**


job_gpu_ecc_dbe_agg Total double bit aggregate ECC errors


job_gpu_ecc_dbe_vol Total double bit volatile ECC errors


job_gpu_ecc_sbe_agg Total single bit aggregate ECC errors


job_gpu_ecc_sbe_vol Total single bit volatile ECC errors


job_gpu_enc_utilization GPU encoding usage


job_gpu_enforced_power_limit GPU-enforced power limit


job_gpu_mem_clock GPU memory clock (also for AMD GPU)


job_gpu_mem_copy_utilization Percentage of GPU memory copy used


job_gpu_mem_free Amount of GPU free memory


job_gpu_mem_total GPU framebuffer size (also for AMD GPU)


job_gpu_mem_used Amount of GPU memory used (also for AMD GPU)


job_gpu_mem_utilization GPU memory used percentage


job_gpu_memory_temp GPU memory temperature


job_gpu_nvlink_total_bandwidth Total NVLink bandwidth used


job_gpu_power_management_limit GPU power management limit


job_gpu_power_usage GPU power usage (also for AMD GPU)


job_gpu_power_violation Throttling duration due to power constraints


job_gpu_shutdown_temp GPU shutdown temperature


job_gpu_slowdown_temp GPU slowdown temperature


job_gpu_sm_clock GPU shader multiprocessor clock (also for AMD GPU)


job_gpu_temperature GPU temperature


job_gpu_thermal_violation Throttling duration due to thermal constraints


job_gpu_utilization GPU utilization (section 12.4.1)


job_gpu_wasted GPU wasted (section 12.4.1)


job_gpu_xid_error The value is the specific XID error


**G.1.9** **IPMI Metrics**

The IPMI metrics correspond to metrics provided by the BMC devices. The metrics available depend on
the manufacturer, and are detected by BCM. The metrics listed in the following table are a limited list of
what may be detected on a system.
The data producer (section 10.2.10) for the IPMI metrics is the ipmi data producer.


_Table G.1.9: IPMI Metrics_


**IPMI Metric** **Description**


Current_< _number_ - _[∗∗]_ Current seen by BMC sensor < _number_ >, in amps
(file: sample_ipmi )


_...continues_


**952** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.9: IPMI Metrics...continued_


**IPMI Metric** **Description**


Exhaust_Temp Exhaust temperature, in Celsius


FETDRV_PG PowerEdge voltage sensor on IPMI board


Fan< _number_ >_RPM RPM of Fan< _number_ - as seen by BMC (file:
sample_ipmi )


Fan_Redundancy [fan redundancy status](https://www.dell.com/support/manuals/nl-nl/dell-opnmang-sw-v8.0.1/eemi_13g-v1/rdu-event-messages?guid=guid-0a608eff-2318-4c32-9395-499fa2b6a15e&lang=en-us)


Inlet_Temp _[∗∗]_ Inlet Temperature, in Celsius (file: sample_ipmi )


M01_VDDQ_PG PowerEdge CPU voltage sensor
M01_VDDQ_PG


M01_VTT_PG PowerEdge CPU voltage sensor


M23_VDDQ_PG PowerEdge CPU voltage sensor


M23_VTT_PG PowerEdge CPU voltage sensor


NDC_PG PowerEdge system board voltage sensor


PFault_Fail_Safe PowerEdge sensor


PLL_PG PowerEdge sensor


PS1_PG_Fail PowerEdge sensor


PS2_PG_Fail PowerEdge sensor


Pwr_Consumption Power consumed by BMC, in watts (file:
sample_ipmi )


Temp Temperature, in Celsius


VSA_PG PowerEdge voltage sensor


VTT_PG PowerEdge voltage sensor


Voltage_< _number_ - _[∗∗]_ Voltage seen by BMC sensor _number_, in Volts
(file: sample_ipmi )


** Standalone scripts, not built-ins.
If sampling from a head node, the script is in directory: /cm/local/apps/cmd/scripts/metrics/
For regular nodes, the script is in directory: /cm/images/default-image/cm/local/apps/cmd/scripts/metrics/


**G.1.10** **Redfish Metrics**
By default Redfish metrics are sampled only when the BMC interface (section 3.7) starts with rf (e.g.
rf0, rf1 etc). The Redfish metric sampler is enabled by setting userdefinedresources as follows:


**Example**


[basecm11->device[node001]]% set userdefinedresources redfish

[basecm11->device[node001]]% commit


**Redfish Standalone Script Metrics**
An example script that samples Redfish metrics is the standalone script /cm/images/default-image/
cm/local/apps/cmd/scripts/metrics/sample_redfish :


**G.1 Metrics And Their Parameters** **953**


_Table G.1.10: Redfish Standalone Script Metrics_


**Redfish Standalone Script Metrics** **Description**


fan_speed Speed of fan (RPM)


psu_power The average power supply unit power (W)


sensor_reading Temperature sensor reading (C)


**Redfish Metrics From CMDaemon Built-in Sampling**
CMDaemon built-in sampling also samples Redfish metrics from the hardware:


**Example**


[basecm11->device[node001]]% latestmetricdata | head -2; latestmetricdata | grep ^RF

Measurable Parameter Type Value ...

------------------------------------------------ --------- --------------------------------------- --------
RF_Baseboard_0_PCB_0_Temp_0 reading Environmental/Redfish/Sensor reading 34 C
RF_Baseboard_0_PCB_1_Temp_0 reading Environmental/Redfish/Sensor reading 33.5 C
RF_Baseboard_0_PCB_2_Temp_0 reading Environmental/Redfish/Sensor reading 33 C
RF_Baseboard_0_StandbyHSC_0_Power_0 reading Environmental/Redfish/Sensor reading 34.746 W
RF_Baseboard_0_StandbyHSC_0_Temp_0 reading Environmental/Redfish/Sensor reading 33.4375 C
RF_C2C_0_Resource_MaxSpeed Environmental/Redfish/Port 0 B/s
RF_DIMM_Slot_AllowedSpeeds Environmental/Redfish/Memory no data
RF_DIMM_Slot_Capacity Environmental/Redfish/Memory 0 B
RF_DIMM_Slot_CapacityMiB Environmental/Redfish/Memory 0 B
RF_DIMM_Slot_Nvidia_RowRemappingFailed Environmental/Redfish/Memory 0
RF_GPU_0_DRAM_0_Memory_Metrics_Bandwidth Environmental/Redfish/Memorymetrics 0.0%
RF_GPU_0_DRAM_0_Memory_Metrics_CapacityUtilizat+ Environmental/Redfish/Memorymetrics 0.0%

RF_GPU_0_Processor_Metrics_Bandwidth Environmental/Redfish/Processormetrics 0.0%

RF_GPU_0_Processor_Metrics_LifeTime_Correctable+ Environmental/Redfish/Processormetrics 0

RF_GPU_0_Processor_Metrics_LifeTime_Uncorrectab+ Environmental/Redfish/Processormetrics 0

RF_GPU_0_Processor_Metrics_Nvidia_AccumulatedGP+ Environmental/Redfish/Processormetrics no data

RF_GPU_0_Processor_Metrics_Nvidia_AccumulatedSM+ Environmental/Redfish/Processormetrics no data

RF_GPU_0_Processor_Metrics_Nvidia_DMMAUtilizatio Environmental/Redfish/Processormetrics 0.0%

RF_GPU_0_Processor_Metrics_Nvidia_FP16Activity Environmental/Redfish/Processormetrics 0.0%


The preceding list is a truncated excerpt from an NVIDIA DGX system. The Redfish metrics that are
available depend on the vendor and hardware.


**G.1.11** **SMART Metrics**

The SMART metrics correspond to metrics provided by SMART hard drive implementation. The metrics
available depend on the manufacturer, and are detected by BCM. The metrics listed in the following
table are a limited list of what may be detected on a system.
A SMART metric takes a block device name ( sda, sdc, nvme0n1 and so on) as a parameter. Some
reported values, such as “spin up time” and “start/stop count” are not relevant on non-rotational (solidstate) drives.
The data producer (section 10.2.10) for SMART metrics is the smart data producer.


**954** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.11: SMART Metrics_


**SMART Metric** **Description**


Command_Timeout Command timeout


Current_Pending_Sector Current pending sectors


Hardware_ECC_Recovered Hardware ECC recovered


Offline_Uncorrectable Uncorrectable sectors


Raw_Read_Error_Rate Raw read error rate


Reallocated_Sector_Ct Reallocated sectors count


Reported_Uncorrect Reported uncorrectable errors


UDMA_CRC_Error_Count UDMA CRC errors


**G.1.12** **Prometheus Metrics**

Prometheus metrics are introduced in section 12.2.

The data producers for Prometheus metrics are JobSampler, JobMetadataSampler, and some others.


_Table G.1.12: Prometheus Metrics_


**Prometheus Metric** **Description (for a job, unless asterisked)**


job_blkio_io_merged Number of block I/Os (requests) merged into requests for I/O operations by a cgroup


job_blkio_io_queued Number of requests queued for I/O operations
by a cgroup


job_blkio_io_service_bytes Reports the number of bytes transferred to or
from specific devices by a cgroup as seen by the
CFQ scheduler


job_blkio_io_service_bytes_total Reports the number of bytes transferred to or
from specific devices by a cgroup as seen by the
CFQ scheduler (for all jobs) _[∗]_


job_blkio_io_service_time_seconds Reports the total time in seconds between request dispatch and request completion for I/O
operations on specific devices by a cgroup as
seen by the CFQ scheduler


job_blkio_io_serviced Reports the number of I/O operations performed on specific devices by a cgroup as seen
by the CFQ scheduler


job_blkio_io_wait_time_seconds Reports the total time I/O operations on specific
devices by a cgroup spent waiting for service in
the scheduler queues


_...continues_


**G.1 Metrics And Their Parameters** **955**


_Table G.1.12: Prometheus Metrics...continued_


**Prometheus Metric** **Description (for a job, unless asterisked)**


job_blkio_sectors Reports the number of sectors transferred to or
from specific devices by a cgroup


job_blkio_time_seconds Reports the time that a cgroup had I/O access to
specific devices


job_cpuacct_stat_system System CPU time consumed by processes


job_cpuacct_stat_user User CPU time consumed by processes


job_cpuacct_usage_seconds CPU usage time consumed


job_memory_active_anon_bytes Anonymous and swap cache on active leastrecently-used (LRU) list, including tmpfs
(shmem), in bytes


job_memory_active_file_bytes File-backed memory on active LRU list, in bytes


job_memory_cache_bytes Page cache, including tmpfs (shmem), in bytes


job_memory_failcnt Reports the number of times that the memory limit has reached the value set in memory.limit_in_bytes


job_memory_hierarchical_memory_limit_bytes Memory limit for the hierarchy that contains the
memory cgroup, in bytes


job_memory_hierarchical_memsw_limit_bytes Memory plus swap limit for the hierarchy that
contains the memory cgroup, in bytes


job_memory_inactive_anon_bytes Anonymous and swap cache on inactive LRU
list, including tmpfs (shmem), in bytes


job_memory_inactive_file_bytes File-backed memory on inactive LRU list, in
bytes


job_memory_mapped_file_bytes Size of memory-mapped mapped files, including tmpfs (shmem), in bytes


job_memory_memsw_failcnt Reports the number of times that the memory
plus swap space limit has reached the value set
in memory.memsw.limit_in_bytes


job_memory_memsw_max_usage_bytes Reports the maximum amount of memory and
swap space used by processes in the cgroup, in
bytes


job_memory_memsw_usage_bytes Reports the sum of current memory usage plus
swap space used by processes in the cgroup, in
bytes


job_memory_pgpgin_bytes Number of pages paged into memory


job_memory_pgpgout_bytes Number of pages paged out of memory


_...continues_


**956** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.12: Prometheus Metrics...continued_


**Prometheus Metric** **Description (for a job, unless asterisked)**


job_memory_rss_bytes Anonymous and swap cache, not including
tmpfs (shmem), in bytes


job_memory_swap_bytes Swap usage, in bytes


job_memory_unevictable_bytes Memory that cannot be reclaimed, in bytes,


job_memory_usage_bytes Reports the total current memory usage by processes in the cgroup, in bytes


job_memory_usage_bytes_total Reports the total current memory usage by processes in the cgroup, in bytes (for all jobs) _[∗]_


job_metadata_allocated_cpu_cores CPU cores used by a job by the user


job_metadata_allocated_gpus GPUs used by a job by the user


job_metadata_is_running Returns 1 if the job metadata sampler is running
a job


job_metadata_is_waiting Returns 1 if the job metadata sampler is waiting


job_metadata_num_cpus Number of CPUs that the job runs on


job_metadata_num_nodes Number of nodes that the job runs on


job_metadata_pending_jobs Number of pending jobs for the user


job_metadata_running_jobs Number of running jobs for the user


job_metadata_running_seconds Time the job has run


job_metadata_waiting_seconds Time the job has been waiting to run


users_job_effective_cpu_seconds:1w CPU seconds used by users over the past week _[∗]_


users_job_running_count:1w Number of jobs run by users over the past week _[∗]_


users_job_waiting_seconds:1w Time users have been waiting for jobs to run over
the past week _[∗]_


users_job_wall_clock_seconds:1w Time the jobs runs for users according to wall
time over the past week _[∗]_


users_job_wasted_cpu_seconds:1w CPU time wasted during users jobs over the past
week _[∗]_


_∗_ total in the past 7x24x60x60 seconds, as measured at the time of sampling


**G.1.13** **NetQ Metrics**

NetQ metrics (table G.1.13) are metrics sourced from NetQ. Configuring NetQ with BCM is described
in section 3.11.

The data producer (section 10.2.10) for NetQ metrics is the netq data producer.


_Table G.1.13: NetQ Metrics_


**NetQ Metric** **Description**


NetQ_node_fan_speed Fan speed (RPM)


_...continues_


**G.1 Metrics And Their Parameters** **957**


_Table G.1.13: NetQ Metrics...continued_


**NetQ Metric** **Description**


NetQ_node_nvlink_rx_all_flits NVLink packets received, control and data
[(FLITs/s)](https://handwiki.org/wiki/FLITs)


NetQ_node_nvlink_rx_data_flits NVLink packets received, data (FLITs/s)


NetQ_node_nvlink_tx_all_flits NVLink packets sent, control and data (FLITs/s)


NetQ_node_nvlink_tx_data_flits NVLink packets sent, data (FLITs/s)


NetQ_node_PSU_power_input Power supply power input (W)


NetQ_node_PSU_power_output Power supply power output (W)


NetQ_node_PSU_voltage_input Power supply voltage input (V)


NetQ_node_PSU_voltage_output Power supply voltage output (V)


NetQ_node_Temp_sensor Temperature sensor value (C)


NetQ health checks are covered in section G.2.4.


**G.1.14** **Kubernetes Metrics**

Configuring Kubernetes with BCM is described in Chapter 4 of the _Containerization Manual_ .
There were cluster Kubernetes metrics described earlier on in table G.1.1. Those were overview

metrics about Kubernetes.

The Kubernetes metrics in the following table G.1.14 are state metrics sourced from Kubernetes itself.
The data producer (section 10.2.10) for the Kubernetes metrics of this section is kubestatemetrics .
The metrics that are not tagged as [STABLE] are experimental, and may change in behavior during
Kubernetes updates.


_Table G.1.6: Kubernetes Metrics_


**Kubernetes Metric** **Description**


kube_configmap_annotations Kubernetes annotations converted to
Prometheus labels.


kube_configmap_created [STABLE] Unix creation timestamp


kube_configmap_info [STABLE] Information about configmap.


kube_configmap_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


kube_configmap_metadata_resource_version Resource version representing a specific version
of the configmap.


kube_cronjob_annotations Kubernetes annotations converted to
Prometheus labels.


kube_cronjob_created [STABLE] Unix creation timestamp


kube_cronjob_info [STABLE] Info about cronjob.


_...continues_


**958** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_cronjob_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


kube_cronjob_metadata_resource_version [STABLE] Resource version representing a specific version of the cronjob.


kube_cronjob_next_schedule_time [STABLE] Next time the cronjob should be
scheduled. The time after lastScheduleTime, or
after the cron job’s creation time if it’s never been
scheduled. Use this to determine if the job is delayed.


kube_cronjob_spec_failed_job_history_limit Failed job history limit tells the controller how
many failed jobs should be preserved.


kube_cronjob_spec_successful_job_history_ Successful job history limit tells the controller
limit how many completed jobs should be preserved.


kube_cronjob_spec_suspend [STABLE] Suspend flag tells the controller to suspend subsequent executions.


kube_cronjob_status_active [STABLE] Active holds pointers to currently running jobs.


kube_cronjob_status_last_schedule_time [STABLE] LastScheduleTime keeps information
of when was the last time the job was successfully scheduled.


kube_cronjob_status_last_successful_time LastSuccessfulTime keeps information of when
was the last time the job was completed successfully.


kube_daemonset_annotations Kubernetes annotations converted to

Prometheus labels.


kube_daemonset_created [STABLE] Unix creation timestamp


kube_daemonset_labels [STABLE] Kubernetes labels converted to

Prometheus labels.


kube_daemonset_metadata_generation [STABLE] Sequence number representing a specific generation of the desired state.


kube_daemonset_status_current_number_ [STABLE] The number of nodes running at least
scheduled one daemon pod and are supposed to.


kube_daemonset_status_desired_number_ [STABLE] The number of nodes that should be
scheduled running the daemon pod.


kube_daemonset_status_number_available [STABLE] The number of nodes that should be
running the daemon pod and have one or more
of the daemon pod running and available


_...continues_


**G.1 Metrics And Their Parameters** **959**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_daemonset_status_number_misscheduled [STABLE] The number of nodes running a daemon pod but are not supposed to.


kube_daemonset_status_number_ready [STABLE] The number of nodes that should be
running the daemon pod and have one or more
of the daemon pod running and ready.


kube_daemonset_status_number_unavailable [STABLE] The number of nodes that should be
running the daemon pod and have none of the
daemon pod running and available


kube_daemonset_status_observed_generation [STABLE] The most recent generation observed
by the daemon set controller.


kube_daemonset_status_updated_number_ [STABLE] The total number of nodes that are
scheduled running updated daemon pod


kube_deployment_annotations Kubernetes annotations converted to
Prometheus labels.


kube_deployment_created [STABLE] Unix creation timestamp


kube_deployment_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


kube_deployment_metadata_generation [STABLE] Sequence number representing a specific generation of the desired state.


kube_deployment_spec_paused [STABLE] Whether the deployment is paused
and will not be processed by the deployment
controller.


kube_deployment_spec_replicas [STABLE] Number of desired pods for a deploy
ment.


kube_deployment_spec_strategy_ [STABLE] Maximum number of replicas that can
rollingupdate_max_surge be scheduled above the desired number of replicas during a rolling update of a deployment.


kube_deployment_spec_strategy_ [STABLE] Maximum number of unavailable
rollingupdate_max_unavailable replicas during a rolling update of a deployment.


kube_deployment_status_condition [STABLE] The current status conditions of a deployment.


kube_deployment_status_observed_generation [STABLE] The generation observed by the deployment controller.


kube_deployment_status_replicas [STABLE] The number of replicas per deploy
ment.


kube_deployment_status_replicas_available [STABLE] The number of available replicas per
deployment.


_...continues_


**960** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_deployment_status_replicas_ready [STABLE] The number of ready replicas per deployment.


kube_deployment_status_replicas_unavailable [STABLE] The number of unavailable replicas
per deployment.


kube_deployment_status_replicas_updated [STABLE] The number of updated replicas per
deployment.


kube_endpoint_address [STABLE] Information about Endpoint available
and non available addresses.


kube_endpoint_address_available (Deprecated since v2.6.0) Number of addresses
available in endpoint.


kube_endpoint_address_not_ready (Deprecated since v2.6.0) Number of addresses
not ready in endpoint.


kube_endpoint_annotations Kubernetes annotations converted to
Prometheus labels.


kube_endpoint_created [STABLE] Unix creation timestamp


kube_endpoint_info [STABLE] Information about endpoint.


kube_endpoint_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


kube_endpoint_ports [STABLE] Information about the Endpoint ports.


kube_ingress_annotations Kubernetes annotations converted to
Prometheus labels.


kube_ingress_created [STABLE] Unix creation timestamp


kube_ingress_info [STABLE] Information about ingress.


kube_ingress_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


kube_ingress_metadata_resource_version Resource version representing a specific version
of ingress.


kube_ingress_path [STABLE] Ingress host, paths and backend service information.


kube_job_annotations Kubernetes annotations converted to
Prometheus labels.


kube_job_complete [STABLE] The job has completed its execution.


kube_job_created [STABLE] Unix creation timestamp


kube_job_info [STABLE] Information about job.


kube_job_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


_...continues_


**G.1 Metrics And Their Parameters** **961**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_job_owner [STABLE] Information about the Job’s owner.


kube_job_spec_completions [STABLE] The desired number of successfully
finished pods the job should be run with.


kube_job_spec_parallelism [STABLE] The maximum desired number of
pods the job should run at any given time.


[STABLE] The number of actively running pods.
kube_job_status_active


kube_job_status_completion_time [STABLE] CompletionTime represents time
when the job was completed.


kube_job_status_failed [STABLE] The number of pods which reached
Phase Failed and the reason for failure.


kube_job_status_start_time [STABLE] StartTime represents time when the
job was acknowledged by the Job Manager.


kube_job_status_succeeded [STABLE] The number of pods which reached
Phase Succeeded.


kube_lease_owner Information about the Lease’s owner.


kube_lease_renew_time Kube lease renew time.


kube_mutatingwebhookconfiguration_created Unix creation timestamp.


kube_mutatingwebhookconfiguration_info Information about the MutatingWebhookConfiguration.


kube_mutatingwebhookconfiguration_ Resource version representing a specific version
metadata_resource_version of the MutatingWebhookConfiguration.


kube_mutatingwebhookconfiguration_ Service used by the apiserver to connect to a muwebhook_clientconfig_service tating webhook.


kube_namespace_annotations Kubernetes annotations converted to
Prometheus labels.


kube_namespace_created [STABLE] Unix creation timestamp


kube_namespace_labels [STABLE] Kubernetes labels converted to
Prometheus labels.


kube_namespace_status_condition The condition of a namespace.


kube_namespace_status_phase [STABLE] kubernetes namespace status phase.


kube_node_annotations Kubernetes annotations converted to

Prometheus labels.


kube_node_created [STABLE] Unix creation timestamp


kube_node_info [STABLE] Information about a cluster node.


kube_node_labels [STABLE] Kubernetes labels converted to

Prometheus labels.


_...continues_


**962** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_node_role The role of a cluster node.


kube_node_spec_taint [STABLE] The taint of a cluster node.


kube_node_spec_unschedulable [STABLE] Whether a node can schedule new
pods.


kube_node_status_allocatable [STABLE] The allocatable for different resources
of a node that are available for scheduling.


kube_node_status_capacity [STABLE] The capacity for different resources of
a node.


kube_node_status_condition [STABLE] The condition of a cluster node.


kube_pod_completion_time [STABLE] Completion time in unix timestamp
for a pod.


kube_pod_container_info [STABLE] Information about a container in a
pod.


kube_pod_container_resource_limits The number of requested limit resource by
a container. It is recommended to use the

kube_pod_resource_limits metric exposed by
kube-scheduler instead, as it is more precise.


kube_pod_container_resource_requests The number of requested request resource by
a container. It is recommended to use the

kube_pod_resource_requests metric exposed by
kube-scheduler instead, as it is more precise.


kube_pod_container_state_started [STABLE] Start time in unix timestamp for a pod
container.


kube_pod_container_status_last_terminated_ Describes the exit code for the last container in
exitcode terminated state.


kube_pod_container_status_last_terminated_ Describes the last reason the container was in terreason minated state.


kube_pod_container_status_ready [STABLE] Describes whether the containers
readiness check succeeded.


kube_pod_container_status_restarts_total [STABLE] The number of container restarts per
container.


kube_pod_container_status_running [STABLE] Describes whether the container is
currently in running state.


kube_pod_container_status_terminated [STABLE] Describes whether the container is
currently in terminated state.


kube_pod_container_status_terminated_ Describes the reason the container is currently in
reason terminated state.


_...continues_


**G.1 Metrics And Their Parameters** **963**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_pod_container_status_waiting [STABLE] Describes whether the container is
currently in waiting state.


kube_pod_container_status_waiting_ [STABLE] Describes the reason the container is
reason currently in waiting state.


kube_pod_created [STABLE] Unix creation timestamp


kube_pod_deletion_timestamp Unix deletion timestamp


kube_pod_info [STABLE] Information about pod.


kube_pod_init_container_info [STABLE] Information about an init container in
a pod.


kube_pod_init_container_resource_limits The number of requested limit resource by an
init container.


kube_pod_init_container_resource_requests The number of requested request resource by an
init container.


kube_pod_init_container_status_last_ Describes the last reason the init container was
terminated_reason in terminated state.


kube_pod_init_container_status_ready [STABLE] Describes whether the init containers
readiness check succeeded.


kube_pod_init_container_status_restarts_ [STABLE] The number of restarts for the init con
total tainer.


kube_pod_init_container_status_running [STABLE] Describes whether the init container is
currently in running state.


kube_pod_init_container_status_terminated [STABLE] Describes whether the init container is
currently in terminated state.


kube_pod_init_container_status_terminated_ Describes the reason the init container is curreason rently in terminated state.


kube_pod_init_container_status_waiting [STABLE] Describes whether the init container is
currently in waiting state.


kube_pod_init_container_status_waiting_ Describes the reason the init container is curreason rently in waiting state.


kube_pod_ips Pod IP addresses


kube_pod_owner [STABLE] Information about the Pod’s owner.


kube_pod_restart_policy [STABLE] Describes the restart policy in use by
this pod.


kube_pod_service_account The service account for a pod.


kube_pod_start_time [STABLE] Start time in unix timestamp for a pod.


kube_pod_status_container_ready_time Readiness achieved time in unix timestamp for a
pod containers.


_...continues_


**964** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_pod_status_initialized_time Initialized time in unix timestamp for a pod.


kube_pod_status_phase [STABLE] The pods current phase.


kube_pod_status_qos_class The pods current qosClass.


kube_pod_status_ready [STABLE] Describes whether the pod is ready to
serve requests.


kube_pod_status_ready_time Readiness achieved time in unix timestamp for a
pod.


kube_pod_status_reason The pod status reasons


kube_pod_status_scheduled [STABLE] Describes the status of the scheduling
process for the pod.


kube_pod_status_scheduled_time [STABLE] Unix timestamp when pod moved
into scheduled status


kube_pod_tolerations Information about the pod tolerations


kube_poddisruptionbudget_annotations Kubernetes annotations converted to
Prometheus labels.


kube_poddisruptionbudget_created [STABLE] Unix creation timestamp


kube_poddisruptionbudget_labels Kubernetes labels converted to Prometheus labels.


kube_poddisruptionbudget_status_current_ [STABLE] Current number of healthy pods
healthy


kube_poddisruptionbudget_status_desired_ [STABLE] Minimum desired number of healthy
healthy pods


kube_poddisruptionbudget_status_expected_ [STABLE] Total number of pods counted by this
pods disruption budget


kube_poddisruptionbudget_status_observed_ [STABLE] Most recent generation observed
generation when updating this PDB status


kube_poddisruptionbudget_status_pod_ [STABLE] Number of pod disruptions that are
disruptions_allowed currently allowed


kube_replicaset_created [STABLE] Unix creation timestamp


kube_replicaset_metadata_generation [STABLE] Sequence number representing a specific generation of the desired state.


kube_replicaset_owner [STABLE] Information about the ReplicaSet’s

owner.


kube_replicaset_spec_replicas [STABLE] Number of desired pods for a ReplicaSet.


_...continues_


**G.1 Metrics And Their Parameters** **965**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_replicaset_status_fully_labeled_ [STABLE] The number of fully labeled replicas
replicas per ReplicaSet.


kube_replicaset_status_observed_generation [STABLE] The generation observed by the ReplicaSet controller.


kube_replicaset_status_ready_replicas [STABLE] The number of ready replicas per
ReplicaSet.


kube_replicaset_status_replicas [STABLE] The number of replicas per ReplicaSet.


kube_replicationcontroller_created [STABLE] Unix creation timestamp


kube_replicationcontroller_metadata_ [STABLE] Sequence number representing a spegeneration cific generation of the desired state.


kube_replicationcontroller_owner Information about the ReplicationController’s

owner.


kube_replicationcontroller_spec_replicas [STABLE] Number of desired pods for a ReplicationController.


kube_replicationcontroller_status_ [STABLE] The number of available replicas per
available_replicas ReplicationController.


kube_replicationcontroller_status_fully_ [STABLE] The number of fully labeled replicas
labeled_replicas per ReplicationController.


kube_replicationcontroller_status_ [STABLE] The generation observed by the Repliobserved_generation cationController controller.


kube_replicationcontroller_status_ready_ [STABLE] The number of ready replicas per
replicas ReplicationController.


kube_replicationcontroller_status_replicas [STABLE] The number of replicas per ReplicationController.


kube_resourcequota [STABLE] Information about resource quota.


kube_resourcequota_created [STABLE] Unix creation timestamp


kube_secret_created [STABLE] Unix creation timestamp


kube_secret_info [STABLE] Information about secret.


kube_secret_metadata_resource_version Resource version representing a specific version
of secret.


kube_secret_type [STABLE] Type about secret.


kube_service_created [STABLE] Unix creation timestamp


kube_service_info [STABLE] Information about service.


kube_service_spec_type [STABLE] Type about service.


kube_statefulset_created [STABLE] Unix creation timestamp


_...continues_


**966** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.1.6: Kubernetes Metrics...continued_


**Kubernetes Metric** **Description**


kube_statefulset_metadata_generation [STABLE] Sequence number representing a specific generation of the desired state for the StatefulSet.


kube_statefulset_persistentvolumeclaim_ Count of retention policy for StatefulSet temretention_policy plate PVCs


kube_statefulset_replicas [STABLE] Number of desired pods for a StatefulSet.


kube_statefulset_status_current_revision [STABLE] Indicates the version of the StatefulSet
used to generate Pods in the sequence [0,currentReplicas).


kube_statefulset_status_observed_ [STABLE] The generation observed by the Stategeneration fulSet controller.


kube_statefulset_status_replicas [STABLE] The number of replicas per StatefulSet.


kube_statefulset_status_replicas_available The number of available replicas per StatefulSet.


kube_statefulset_status_replicas_current [STABLE] The number of current replicas per
StatefulSet.


kube_statefulset_status_replicas_ready [STABLE] The number of ready replicas per
StatefulSet.


kube_statefulset_status_replicas_updated [STABLE] The number of updated replicas per
StatefulSet.


kube_statefulset_status_update_revision [STABLE] Indicates the version of the StatefulSet
used to generate Pods in the sequence [replicasupdatedReplicas,replicas)


kube_storageclass_created [STABLE] Unix creation timestamp


kube_storageclass_info [STABLE] Information about storageclass.


kube_validatingwebhookconfiguration_created Unix creation timestamp.


kube_validatingwebhookconfiguration_info Information about the ValidatingWebhookConfiguration.


kube_validatingwebhookconfiguration_ Resource version representing a specific version
metadata_resource_version of the ValidatingWebhookConfiguration.


kube_validatingwebhookconfiguration_ Service used by the apiserver to connect to a valwebhook_clientconfig_service idating webhook.


**G.1 Metrics And Their Parameters** **967**


**G.1.15** **Parameters For Metrics**

Metrics have the parameters indicated by the left column in the following example:


**Example**


[basecm11->monitoring->measurable[CPUUser]]% show

Parameter Value

----------------------- ---------------------------
Class CPU

Consolidator default (ProcStat)

Cumulative yes

Description CPU time spent in user mode

Disabled no (ProcStat)

Gap 0 (ProcStat)
Maximal age 0s (ProcStat)
Maximal samples 4,096 (ProcStat)

Maximum 0

Minimum 0

Name CPUUser

Parameter

Producer ProcStat

Revision

Type Metric

Unit Jiffies/s


If the value is inherited from the producer, then it is shown in parentheses next to the value. An
inherited value can be overwritten by setting it directly for the parameter of a measurable.
The meanings of the parameters are:


Class : A choice assigned to a metric. It can be an internal type, or it can be a standalone class type. A
slash ( / ) is used to separate class levels. A partial list of the class values is:


   - CPU : CPU-related


   - Disk : Disk-related


   - Disk/Smart : SMART Disk-related


   - Fabric : Fabric-related


   - GPU : GPU-related


   - Internal : An internal metric


   - Job : Job metric


   - License : License-related


   - Memory : Memory-related


   - Network : Network-related


   - OS : Operating-system-related


   - Process : Process-related


   - Prometheus : Prometheus-related


   - Total : Total cluster-wide-related


   - Workload : Workload-related


   - Environmental : Environmental-related


Consolidator : This is described in detail in sections 10.4.3 and 10.5.2


**968** **Metrics, Health Checks, Enummetrics, And Actions**


Cumulative : If set to no, then the raw value is treated as not cumulative (for example, CoresUp ), and
the raw value is presented as the metric value.


If set to yes, then the metric is treated as being cumulative, which means that a rate (per second)
value is presented.


More explicitly: When set to yes, it means that the raw sample used to calculate the metric is
expected to be cumulative, like, for example, the bytes-received counter for an Ethernet interface.
This in turn means that the metric is calculated from the raw value by taking the difference in raw
sample measurement values, and dividing it by the time period over which the raw values are
sampled. Thus, for example:


    - The bytes-received raw measurements, which accumulate as the packets are received, and are
in bytes, and have Cumulative set to yes, and then have a corresponding metric, BytesRecv,
with a value in bytes/second.


    - The system uptime raw measurements, which accumulate at the rate of 1 second per second,
and are in seconds, have Cumulative set to yes, and have a corresponding metric, Uptime,
with a value that uses no units. Ideally, the metric has a value of 1, but in practice the measured value varies a little due to jitter.


Description : Description of the raw measurement used by the metric. Empty by default.


Disabled : If set to no (default) then the metric runs.


Gap : The number of samples that are allowed to be missed before a value of NaN is set for the value of
the metric.


Maximal age : the maximum age of RLE samples that are kept. If Maximal age is set to 0 then the
sample age is not considered. Units can be w, d, h, m, s (weeks, days, hours, minutes, seconds),
with s as the default.


Maximal samples : the maximum number of RLE samples that are kept. If Maximal samples is set to 0
then the number of sample age is not considered.


Maximum : the value that the y-axis maximum takes in graphs plotted in Base View by default. If the
maximum of the y-values is more than the default y-axis maximum value, then the maximum of
the y-values becomes the y-axis maximum. [1]


Minimum : the value that the y-axis minimum takes in graphs plotted in Base View by default. If the
minimum of the y-values is less than the default y-axis minimum value, then the minimum of the
y-values becomes the y-axis minimum. [1]


Name : The name given to the metric.


Parameter : Parameter used for this metric. For example, eth0 with the metric BytesRecv


Producer : The data producer that produces the metric


Revision : User-definable revision number for the object


Type : This can be one of metric, healthcheck, or enummetric


1 To clarify the concept, a case can be considered where minimum =0, maximum =3 are set. If a data point with a y-value of 2 is
plotted on a graph, then the y-axis spans the range from 0 to 3 by default.
However


  - if the data point has a y-value of 4 instead, then it means the y-axis maximum of 3 is re-sized from its default of 3 to the
value of 4, so that the y-axis now spans from 0 to 4.


  - if the data point has a y-value of -1 instead, then it means the y-axis minimum of 0 is re-sized from its default of 0 to the
value of -1, so that the y-axis now spans from -1 to 3.


**G.1 Metrics And Their Parameters** **969**


Unit : A unit for the metric. For example: B/s (bytes/second) for BytesRecv metric, or unit-less for the
Uptime metric. A percent is indicated with %


**970** **Metrics, Health Checks, Enummetrics, And Actions**


**G.2** **Health Checks And Their Parameters**


A list of health checks can be viewed, for example, for the head node, using cmsh as follows (section 10.5.3):


[basecm11 ~]# cmsh -c "monitoring measurable; list healthcheck"


The health checks listed in this section are classed into 4 kinds:


1. Regular health checks (section 10.2.4) are listed and described in section G.2.1.


2. GPU health checks (section G.2.2)


3. Redfish health checks (section G.2.3)


4. NetQ health checks (section G.2.4)


**G.2 Health Checks And Their Parameters** **971**


**G.2.1** **Regular Health Checks**


_Table G.2.1: List Of Health Checks_


**Name** **Query** (script response is PASS / FAIL )


ManagedServicesOk _[∗]_ Are CMDaemon-monitored services all OK?
If the response is FAIL, then at least one of the services
being monitored is failing. The latesthealtdata -v command (section 10.6.3) should show which one(s). After correcting the problem with the service, a reset of the service
is normally carried out (section 3.14, page 170).
There is also a related ManagedServicesOk metric on
page 930.


Mon::Storage Is space available for the monitoring system metrics (section G.1.4)?


chrootprocess Are there daemon processes running using chroot in software images? Here: yes = FAIL . On failure, kill cron daemon processes running in the software images.


cm-chroot-sw-img Are there dangling mounts left behind of images created
by cm-chroot-sw-img? Here: yes = FAIL . The cluster administrator is expected to inspect and unmount the dangling mounts.


cmha-status Are both head nodes up and running?


cmsh _[∗]_ Is cmsh available?


cuda-dcgm Is cuda-dcgm available?


defaultgateway Is there a default gateway available?


dellnss If running, is the Dell NFS Storage Solution healthy?


diskspace Is there less local disk space available to non-root users
than any of the space parameters specified?
_The space parameters can be specified as MB, GB, TB, or as per-_
_centages with %. The default severity of notices from this check_
_is 10, when one space parameter is used. For more than one_
_space parameter, the severity decreases by 10 for each space pa-_
_rameter, sequentially, down to 10 for the last space parameter._
_By default a space parameter of 10% is assumed. Another, also_
_optional, non-space parameter, the filesystem mount point pa-_
_rameter, can be specified after the last space parameter to track_
_filesystem space, instead of disk space. A metric-based alterna-_
_tive to tracking filesystem space changes is to use the built-in_
_metric_ freespace _(page 929) instead._


_...continued_


**972** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.2.1: List Of Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


Examples:


                 - diskspace 10%


less than 10% space = FAIL, severity 10


                 - diskspace 10% 20% 30%


less than 30% space = FAIL, with severity levels as
indicated:


**space left** **severity**


10% 30


20% 20


30% 10


                 - diskspace 10GB 20GB


less than 20GB space = FAIL, severity 10


less than 10GB space = FAIL, severity 20


                 - diskspace 10% 20% /var


For the filesystem /var :


less than 20% space = FAIL, severity 10


less than 10% space = FAIL, severity 20


_...continued_


**G.2 Health Checks And Their Parameters** **973**


_Table G.2.1: List Of Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


dmesg Is dmesg output OK?
_Regexes to parse the output can be constructed in the_
_configuration_ _file_ _at_ /cm/ local/ apps/ cmd/ scripts/
healthchecks/ configfiles/ dmesg. py


docker Is Docker running OK? Checks for Docker server availability and corruption, dead containers, proper endpoints


dockerregistry Is the Docker registry running OK? Checks registry endpoint and registry availability


exports Are all filesystems as defined by the cluster management
system exported?


etcd Are the core etcd processes of Kubernetes running OK?
Checks endpoints and interfaces


failedprejob Are there failed prejob health checks (section 7.8.2)? Here:
yes = FAIL.
By default, the job ID is saved under /cm/local/
apps/ < _scheduler_                   - /var/ :


                     - On FAIL, in failedprejobs .


                     - On PASS, in allprejobs


The maximum number of IDs stored is 1000 by default.
The maximum period for which the IDs are stored is 30
days by default. Both these maxima can be set with the
failedprejob health check script.


failover Is the failover status OK?


hpraid Are the HP Smart Array controllers OK?


ib Is the InfiniBand Host Channel Adapter working properly?
_A_ _configuration_ _file_ _for_ _this_ _health_ _check_ _is_ _at_
/cm/ local/ apps/ cmd/ scripts/ healthchecks/
configfiles/ ib. py


_...continued_


**974** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.2.1: List Of Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


interfaces Are the interfaces up and running at full speed?


ipmihealth Is the BMC (IPMI or iLO) health OK? Uses the script
sample_ipmi .


kubernetescertsexpiration Are Kubernetes certificates valid for at least the next 30
days?


kuberneteschildnode Are all Kubernetes child nodes up?


kubernetescomponentsstatus Are all expected agents and services up and running for
active nodes?


kubernetesnodesstatus Is the status for all Kubernetes nodes OK?


kubernetespodsstatus Is the status for all pods OK?


ldap Can the ID of the user be looked up with LDAP?


lustre Is the Lustre filesystem running OK?


megaraid Are the MegaRAID controllers OK?
_Either the proprietary MegaCLI software, or its successor, the_
_proprietary StorCLI software is needed for this health check. The_
_MegaCLI software was originally provided by LSI Logic, but LSI_
_is now part of Broadcom._
_Both the MegaCLI software and the StorCLI software are now_
_available from the Broadcom website (_ [http://www.broadcom.](http://www.broadcom.com)
[com](http://www.broadcom.com) _)._
_For BCM 10 and onwards, the healthcheck first checks for Stor-_
_CLI, and then for MegaCLI, and uses the first binary that is_
_detected. For BCM versions prior to version 10, the healthcheck_
_first checks for MegaCLI, and then StorCLI, and uses the first_
_binary that is detected._


_...continued_


**G.2 Health Checks And Their Parameters** **975**


_Table G.2.1: List Of Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


mounts Are all mounts defined in the fstab OK?


mysql Is the status and configuration of MySQL correct?


node-hardware-profile Is the specified node’s hardware configuration during
health check use unchanged?


_The options to this script are described using the “-h” help_
_option._ _Before this script is used for health checks, the_
_specified hardware profile is usually first saved with the_ -s
_option._ _Eg:_ _“_ node-hardware-profile -n node001 -s
hardwarenode001 _”_


ntp _[∗]_ Is NTP synchronization happening?


oomkiller Has the oomkiller process run? Yes=FAIL. The oomkiller
health check checks if the oomkiller process has run.
The configuration file /cm/local/apps/cmd/scripts/
healthchecks/configfiles/oomkiller.conf for the
oomkiller health check can be configured to reset the response to PASS after one FAIL is logged,
until the next oomkiller process runs. The processes killed by the oomkiller process are logged in
/var/spool/cmd/save-oomkilleraction .
_A consideration of the causes and consequences of the killed pro-_
_cesses is strongly recommended. A reset of the node is generally_
_recommended._


opalinkhealth Are the quality and the integrity of the Intel OPA HFI link
OK?


Overall_Health:< _sda_ - Overall disk health status (SMART response) for specified
device, in this case < _sda_                        - .


SMART_Health:< _sda_ - Overall SMART health as reported by the exit code, for a
specified device, in this case < _sda_                        - .


rogueprocess Are the processes that are running legitimate (ie, not
’rogue’)? Besides the FAIL / PASS / UNKNOWN response to
CMDaemon, also returns a list of rogue process IDs to file
descriptor 3 (InfoMessages), which the killprocess action (page 982) can then go ahead and kill.
Illegitimate processes are processes that should not be running on the node. An illegitimate process is at least one of
the following, by default:


                       - not part of the workload manager service or its jobs


                      - not a root- or system-owned process


                        - in the state Z, T, W, or X. States are described in the
ps man pages in the section on “PROCESS STATE
CODES”


_...continued_


**976** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.2.1: List Of Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


Rogue process criteria can be configured in the
file /cm/local/apps/cmd/scripts/healthchecks/
configfiles/rogueprocess.py within the software
image. To implement a changed criteria configuration,
the software image used by systems on which the health
check is run should be updated (section 5.6). For example,
using: cmsh -c "device; imageupdate -c default -w"
for the default category of nodes.


schedulers Are the queue instances of all schedulers on a node healthy
?


smart Is the SMART response healthy? The severities can
be configured in the file /cm/local/apps/cmd/scripts/
healthchecks/configfiles/smart.conf .
By default, if a drive does not support the SMART commands and results in a "Smart command failed" info mes
sage for that drive, then the healthcheck is configured to
give a PASS response. This is because the mere fact that
the drive is a non-SMART drive should not be a reason to

conclude that the drive is unhealthy.
The info messages can be suppressed by setting an allowed list of the disks to be checked within /cm/local/

apps/cmd/scripts/healthchecks/smart .


ssh2node Is passwordless ssh root login, from head to a node that is
up, working?
Some details of its behavior are:


                      - The health check fails on the head node if root ssh

login to the head node has been disabled.


                        - The health check fails if ssh certificate-based access,
to a non-head node that is in the UP state, fails, even if
login (key-based) access is still available. The UP state
is determined by whether CMDaemon is running on
that node.


                       - If the regular node is in a DOWN state—which could
be due to CMDaemon being down, or the node having been powered off gracefully, or the node suffering a sudden power failure—then the health check
responds with a PASS . The idea here is to check key
or certificate access, and decouple it from the node

state.


_...continued_


**G.2 Health Checks And Their Parameters** **977**


_Table G.2.1: List Of Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


swraid Are the software RAID arrays healthy?


testhealthcheck _A health check script example for creating scripts, or setting a_
_mix of PASS/FAIL/UNKNOWN responses. The source includes_
_examples of environment variables that can be used, as well as_
_configuration suggestions._


 - built-ins, not standalone scripts.
If sampling from a head node, a standalone script is in directory:
/cm/local/apps/cmd/scripts/healthchecks/
If sampling from a regular node, a standalone script is in directory:
/cm/images/default-image/cm/local/apps/cmd/scripts/healthchecks/


**G.2.2** **GPU Health Checks**

The data producer (section 10.2.10) for the GPU health checks of this section is GPUSampler .
The NVIDIA GPU health checks of this section, as the GPUSampler data producer name suggests, is
about gathering the sampled GPU data from the devices themselves.
The device parameter for the GPU health checks in this section, unless otherwise noted, requires as
a parameter the device slot number that the GPU uses. The parameter takes the form gpu0, gpu1, and
so on. It is appended to the metric with a colon character. For example, the gpu_health_inforom health
check, if used with gpu1, is specified as:


**Example**


gpu_health_inforom:gpu1


Available GPU health checks for V100 and A100 GPUs are listed in table G.2.2. The available GPU

metrics are displayed in table G.1.6.


_Table G.2.2: List Of GPU Health Checks_


**Name** **Query** (script response is PASS / FAIL )


gpu_health_driver Is the driver-related subsystem OK?


gpu_health_hostengine _[∗]_ Is the host engine status, for all GPU devices on that node,
OK?


gpu_health_inforom Is the Inforom OK?


gpu_health_mcu Is the microcontroller unit OK?


gpu_health_mem Is the memory subsystem OK?


gpu_health_nvlink Is the NVLINK system OK?


gpu_health_nvswitch_fatal Is the NVSwitch showing no fatal errors?


_...continued_


**978** **Metrics, Health Checks, Enummetrics, And Actions**


_Table G.2.2: List Of GPU Health Checks...continued_


**Name** **Query** (response is PASS / FAIL )


gpu_health_nvswitch_non_fatal Is the NVSwitch showing no non-fatal errors?


gpu_health_overall _[∗∗]_ Is the overall GPU health OK?


gpu_health_pcie Is the PCIe system OK?


gpu_health_pmu Is the power management unit OK?


gpu_health_power Is the power OK?


gpu_health_sm Is the streaming multiprocessor OK?


gpu_health_thermal Is the temperature OK?


 - Specified without a GPU because the check is a check for all GPUs.
** If specified without a GPU, then the check is a check for all GPUs.
For example, for the gpu_health_overall health check:
gpu_health_overall is for all the GPUs


gpu_health_overall:gpu0 is just for GPU0


**G.2.3** **Redfish Health Checks**
The available Redfish health checks are displayed in table G.2.3.


_Table G.2.3: Redfish health checks_


**Redfish Health Check** **Description**


chassis_health Health status of chassis


cpu_health Health status of processor


memory_health Health status of memory


storage_health Health status of storage


device_health Health status of storage device


drive_health Health status of storage drive


volume_health Health status of storage volume


psu_health Health status of power supply


fan_health Health status of a fan


sensor_health Health status of a sensor


pcie_health Health status of PCIe device


manager_health Health status of manager (e.g.: HPE iLO)


**G.2.4** **NetQ Health Checks**

NetQ health checks (table G.1.13) are healtcheck measurables sourced from NetQ. Configuring NetQ
with BCM is described in section 3.11.

The data producer (section 10.2.10) for NetQ measurables is the netq data producer.


**G.2 Health Checks And Their Parameters** **979**


_Table G.1.13: NetQ Health Checks_


**NetQ Health Check** **Query** (Response is PASS / FAIL )


NetQ_node_fan_status Is the fan working?


NetQ_node_NVLink_status Is NVLink up?


NetQ_node_PSU_status Is the power supply unit working?


NetQ_node_Temp_status Is the temperature sensor working?


**G.2.5** **Parameters For Health Checks**

Health checks have the parameters indicated by the left column in the example below:


**Example**


[myheadnode->monitoring->measurable]% show cmsh

Parameter Value

-------------------------------- ---------------------------------------------
Class Internal

Consolidator - (cmsh)

Description Checks whether cmsh is available, i.e. can we

use cmsh for the default cluster?

Disabled no (cmsh)

Gap 0 (cmsh)
Maximal age 0s (cmsh)
Maximal samples 4,096 (cmsh)

Name cmsh

Parameter

Producer cmsh

Revision

Type HealthCheck


If the value is inherited from the producer, then it is shown in parentheses next to the value. An inherited
value can be overwritten by setting it directly for the parameter of a measurable.
The parameters are a subset of the parameters for metrics described in section G.1.15.


**980** **Metrics, Health Checks, Enummetrics, And Actions**


**G.3** **Enummetrics**


_Table G.3: List Of Enummetrics_


**Name** **Query**


DeviceStatus What is the status of the device? Possible values are:


            - up


            - down


            - closed


            - installing


            - installer_failed


            - installer_rebooting,


            - installer_callinginit


            - installer_unreachable


            - installer_burning


            - burning


            - unknown


            - opening


            - going_down


            - pending


            - no data


_...continued_


**G.3 Enummetrics** **981**


_Table G.3: List Of Enummetrics...continued_


**Name** **Query**


wlm_slurm_state What is the status of the device allocated to Slurm? Possible values are:


            - allocated


            - completing


            - down


            - drain


            - draining


            - fail


            - failing


            - idle


            - maint


            - mixed


**982** **Metrics, Health Checks, Enummetrics, And Actions**


**G.4** **Actions And Their Parameters**


**G.4.1** **Actions**


_Table G.4.1: List Of Actions_


**Name** **Description**


Drain Allows no new processes on a compute node from the workload manager.
This means that already running jobs are permitted to complete. Usage
Tip: Plan for undrain from another node becoming active


Send e-mail to Sends mail using the mailserver that was set up during server configuraadministrators tion. Default destination is root@localhost . The e-mail address that it is

otherwise sent to is specified by the recipient parameter for this action.


Event Send an event to users with a connected client


ImageUpdate Update the image on the node


PowerOff Powers off, hard


PowerOn Powers on, hard


PowerReset Power reset, hard


Reboot Reboot via the system, trying to shut everything down cleanly, and then
start up again


killprocess _[∗]_ Kills processes seen by CMDaemon with the KILL (-9) signal. The PIDs
are passed via the CMD_INFO_MESSAGE environmental variable. Syntax:
killprocess < _PID1_ [,< _PID2_ >,...]>
This action is designed to work with rogueprocess (page 975)


remount _[∗]_ remounts all defined mounts


testaction _[∗]_ An action script example for users who would like to create their own
scripts. The source has helpful remarks about the environment variables
that can be used as well as tips on configuring it generally


Shutdown Power off via system, trying to shut everything down cleanly


Undrain node Allow processes to run on the node from the workload manager


 - standalone scripts, not built-ins.
If running from a head node, the script is in directory: /cm/local/apps/cmd/scripts/actions/
If running from a regular node, the script is in directory: /cm/images/default-image/cm/local/apps/
cmd/scripts/actions/


**G.4.2** **Parameters For A Monitoring Action**
The default monitoring actions are listed in section 10.4.4.
All actions have in common the parameters shown by the left column, illustrated by the example
below for the drain action:


**Example**


[myheadnode->monitoring->action]% show drain

Parameter Value

------------------ ----------------------
Action Drain node from all WLM

Allowed time

Disable no

Name Drain

Revision

Run on Active

Type DrainAction


**G.4 Actions And Their Parameters** **983**


Out of the full list of default actions, the actions with only the common parameter settings are:


 - Poweron : Powers off the node


 - PowerOff : Powers off the node


 - PowerReset : Hard resets the node


 - Drain : Drains the node (does not allow new jobs on that node)


 - Undrain : Undrains the node (allows new jobs on that node)


 - Reboot : Reboots node via the operating system.


 - Shutdown : Shuts the node down via the operating system.


 - ImageUpdate : Updates the node from the software image


 - Event : Sends an event to users connected with cmsh or Base View


**Extra Parameters For Some Actions**

The following actions have extra parameters:


**Action of the type** ScriptAction **:**


 - killprocess : A script that kills a specified process


 - testaction : A test script


 - remount : A script to remount all devices


The extra parameters for an action of type ScriptAction are:


**–**
Arguments : List of arguments that are taken by the script


**–** Node environment : Does the script run in the node environment?


**–**
Script : The script path


**–** timeout : Time within which the script must run before giving up


**Action of the type** EmailAction **:**


 - Send e-mail to administrators : Sends an e-mail out, by default to the administrators


The extra parameters for an action of type EmailAction are:


**–** All administrators : sends the e-mail to the list of users in the Administrator e-mail set
ting in partition[base] mode


**–** Info : the body of the e-mail message


**–**
Recipients : a list of recipients