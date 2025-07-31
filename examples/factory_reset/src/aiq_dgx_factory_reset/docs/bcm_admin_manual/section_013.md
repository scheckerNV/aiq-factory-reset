# **10**

### **Monitoring: Monitoring Cluster** **Devices**

BCM monitoring allows a cluster administrator to monitor anything that can be monitored in the cluster.
Much of the monitoring consists of pre-defined sampling configurations. If there is anything that is not
configured, but the data on which it is based can be sampled, then monitoring can be configured for it
too, by the administrator.
The monitoring data can be viewed historically, as well as on demand. The historical monitoring
data can be stored raw, and optionally also as consolidated data—a way of summarizing data.
The data can be handled raw and processed externally, or it can be visualized within Base View in the
form of customizable charts. Visualization helps the administrator spot trends and abnormal behavior,
and is helpful in providing summary reports for managers.
Monitoring can be configured to set off alerts based on triggers, and pre-defined or custom actions
can be carried out automatically, depending on triggers. The triggers can be customized according to
user-defined conditional expressions.
Carrying out such actions automatically after having set up triggers for them means that the monitoring system can free the administrator from having to carry out these chores.
In this chapter, the monitoring system is explained with the following approach:


1. A basic example is first presented in which processes are run on a node. These processes are
monitored, and trigger an action when a threshold is exceeded.


2. With this easy-to-understand example as a basic model, the various features and associated functionality of the BCM monitoring system are then described and discussed in further depth. These
include visualization of data, concepts, configuration, monitoring customization and cmsh use.


**10.1** **A Basic Monitoring Example And Action**


**10.1.1** **Synopsis Of Basic Monitoring Example**
In section 10.1, after an overview (section 10.1.1), a minimal basic example of monitoring a process is
set up (section 10.1.2) and used (section 10.1.3). The example is contrived, with the aim being to present
a basic example that covers a part of what the monitoring system is capable of handling. The basic
example gives the reader a structure to keep in mind, around which further details are fitted and filled
in during the coverage in the rest of this chapter.
In the basic example, a user runs a large number of pointless CPU-intensive processes on a head
node which is normally very lightly loaded. An administrator who is monitoring user mode CPU load
usage throughout the cluster, notices this usage spike. After getting the user to stop wasting CPU cycles,
the administrator may decide that putting a stop to such processes automatically is a good idea. The
administrator can set that up with an action that is triggered when a high load is detected. The action
that is taken after triggering, is to stop the processes (figure 10.1).


**536** **Monitoring: Monitoring Cluster Devices**







Figure 10.1: Monitoring Basic Example: CPU-intensive Processes Started, Detected And Stopped


The basic example thus illustrates how BCM monitoring can be used to detect something on the
cluster and how an action can be set up and triggered based on that detection.


**10.1.2** **Before Using The Basic Monitoring Example—Setting Up The Pieces**

**Running A Large Number Of Pointless CPU-Intensive Processes**
One way to simulate a user running pointless CPU-intensive processes is to run several instances of the
standard unix utility, yes . The yes command sends out an endless number of lines of “ y ” texts. It is
typically used in scripts to answer dialog prompts for confirmation.
The administrator can run 8 subshell processes in the background from the command line on the
head node, with yes output sent to /dev/null, as follows:


for i in {1..8}; do ( yes > /dev/null &); done


Running “ mpstat 2 ” shows usage statistics for each processor, updating every 2 seconds. It shows that
%usr, which is user mode CPU usage percentage, is close to 90% on an 8-core or less head node when
the 8 subshell processes are running.


**Setting Up The Kill Action**
To stop the pointless CPU-intensive yes processes, the command killall yes can be used. The administrator can make it a part of a script killallyes :


#!/bin/bash

killall yes


and make the script executable with a chmod 700 killallyes . For convenience, it may be placed in the
/cm/local/apps/cmd/scripts/actions directory where some other action scripts also reside.


**10.1 A Basic Monitoring Example And Action** **537**


**10.1.3** **Using The Basic Monitoring Example**
Now that the pieces are in place, the administrator can use Base View to add the killallyesaction
action to its action list, and then set up a trigger for the action:


**Adding The Action To The Actions List**

In Base View:


  - The navigation path


Monitoring   - Actions   - Monitoring Actions   - killprocess   - Clone x 1


is used to clone the structure of an existing action. The killprocess action is convenient because
it is expected to function in a similar way, so its options should not have to be modified much.
However, any action could be cloned and the clone modified in appropriate places.


  - The name of the cloned action is changed. That is, the administrator sets Name to
killallyesaction . This is just a sensible label—the name can be arbitrary.


 - Script is set to the path /cm/local/apps/cmd/scripts/actions/killallyes, which is where the
script was placed earlier (page 536).


After saving, the killallyesaction action becomes part of the list of monitoring actions (figure 10.2).


Figure 10.2: Base View Monitoring Configuration: Adding An Action


**Setting Up A Trigger Using CPUUser On The Head Node(s)**
The navigation path


Monitoring - Triggers - Failing health checks - Clone x 1


can be used to configure a monitoring trigger, by cloning an existing trigger. A trigger is a condition
that is set on the state of sample, which runs an action when that condition is met. In this case, the


**538** **Monitoring: Monitoring Cluster Devices**


sample state condition may be that the metric (section 10.2.3) CPUUser must not exceed 50. If it does,
then an action ( killallyesaction ) is run, which should kill the yes processes.


 - CPUUser is a measure of the time spent in user mode CPU usage per second, and is measured in
jiffy intervals per second.


  - A jiffy interval is a somewhat arbitrary time interval that is predefined for kernel developers per
platform. It is the minimum amount of time that a process has access to the CPU before the kernel
can switch to another task.


The jiffy interval per second of CPUUser is a quantity rather than a percentage. It should not be
confused with the closely related measurable CPUUsage, which is a percentage. CPUUsage is used
for %user monitoring, where %user is the user time as defined and measured for the top command.


To configure triggering for CPUUser, the trigger attributes can be modified as follows (figure 10.3):


Figure 10.3: Base View Monitoring Configuration: Setting A Trigger


  - A name is set for the trigger. The name can be arbitrary, and killallyestrigger is used in this
example.


  - The trigger is enabled.


  - The Enter actions field is filled with the killallyesaction, which is the action defined earlier.


  - The trigger is saved by clicking on the SAVE button.


  - the trigger can be set to run an action script if the sample state crosses over into a state that meets
the trigger condition. That is, Enter actions is configured for a particular condition.


**10.1 A Basic Monitoring Example And Action** **539**


The condition under which the Enter actions action script is run in the example, can simply be
when CPUUser on the head node is above 50. Such a condition can be set by setting an expression in
a subwindow. The subwindow to do this is the JUMP TO   - Expression button. The button is found
in the screen of figure 10.3 by scrolling to the top. Clicking the button brings up the Monitoring
Expression subwindow (figure 10.4):


Figure 10.4: Base View Monitoring Configuration: Setting An Expression


Within the expression subwindow:


**–** A name is set for the expression. The name can be arbitrary, and killallyesexp is used for
Name in this example.


**–**
An entity is set. In this case, the entity being monitored is the head node. If the head node
is called basecm11 in this example, then basecm11 is the value set for Entities . An entity is
often simply a device, but it can be any object that CMDaemon stores.


**–** A measurable is set. In this case, Measurables is set to CPUUser .


**–** An operator and threshold value are set. In this case    -, which is the greater than operator,
and 50 which is a significant amount of CPUUser time in jiffies/s, are set for Operator and

Value .


After saving the configuration, the killallyesexp expression evaluates the data being sampled for the killallyestrigger trigger. If the expression is TRUE, then the trigger launches the
killallyesaction action.


**540** **Monitoring: Monitoring Cluster Devices**


**The Result**

In the preceding section, an action was added, and a trigger was set up with a monitoring expression.
With a default installation on a newly installed cluster, the measurement of CPUUser is done every
120s (the period can be modified in the Data Producer window of Base View, as seen in figure 10.10).
The basic example configured with the defaults thus monitors if CPUUser on the head node has crossed
the bound of 50 jiffies/s every 120s.
If CPUUser is found to have entered—that is: crossed over from below the value and gone into the
zone beyond 50 jiffies/s—then the killallyesexp expression notices that. Then, the trigger it is configured for, killallyestrigger trigger, runs the killallyesaction action, which runs the killallyes
script. The killallyes script kills all the running yes processes. Assuming the system is trivially loaded
apart from these yes processes, the CPUUser metric value then drops to below 50 jiffies/s.
To clarify what “found to have entered” means in the previous paragraph:
After an Enter trigger condition has been met for a sample, the first sample immediately after that
does not ever meet the Enter trigger condition, because an Enter threshold crossing condition requires
the previous sample to be below the threshold.
The second sample can only launch an action if the Enter trigger condition is met and if the preceding
sample is below the threshold.
Other non- yes CPU-intensive processes running on the head node can also trigger the killallyes
script. Since the script only kills yes processes, leaving any non- yes processes alone, it would in such
a case run unnecessarily. This is a deficiency due to the contrived and simple nature of the basic example which is being illustrated here. In a production case the action script is expected to have a more
sophisticated design.
At this point, having gone through section 10.1, the reader is expected to have a rough idea of how
monitoring, triggers, trigger conditional expressions, and actions work. The following sections in this
chapter cover the concepts and features for BCM monitoring in greater detail.


**10.2** **Monitoring Concepts And Definitions**


A discussion of the concepts of monitoring, along with definitions of terms used, is appropriate at this
point. The features of the monitoring system in BCM covered later on in this chapter will then be
understood more clearly.


**10.2.1** **Measurables**

Measurables are measurements (sample values) that are obtained via data producers (section 10.2.10) in
CMDaemon’s monitoring system. The measurements can be made for nodes, head nodes, other devices,
or other _entities_ .


**Types Of Measurables**

Measurables can be:


 - _enummetrics_ : measurements with a small number of states. The states can be pre-defined, or userdefined. Further details on enummetrics are given in section 10.2.2.


 - _metrics_ : measurements with number values, and no data, as possible values. For example, values
such as: -13113143234.5, 24, 9234131299 . Further details on metrics are given in section 10.2.3.


 - _health checks_ : measurements with the states PASS, FAIL, and UNKNOWN as possible states, and no
data as another possible state, when none of the other states are set. Further details on health
checks are given in section 10.2.4.


no data **And Measurables**

If no measurements are carried out, but a sample value needs to be saved, then the sample value is set
to no data for a measurable. This is a defined value, not a null data value. metrics and enummetrics
can therefore also take the no data value.


**10.2 Monitoring Concepts And Definitions** **541**


**Entities And Measurables**

An entity is a concept introduced in BCM version 8.0.
Normally, a device, or a category or some similar grouping is a convenient idea to keep in mind as
an entity, for concreteness.
The default entities in a new installation of BCM are the following:
device category partition[base] softwareimages
However, more generally, an entity can be an object from the following modes of cmsh :
category cloud configurationoverlay device edgesite etcd fspart group jobqueue jobs

kubernetes network nodegroup partition profile rack softwareimage user
For example, a software image object that is to be provisioned to a node is an entity, with some of
the possible attributes of the entity being the name, kernelversion, creationtime, or locked attributes
of the image:


[root@basecm11 ~]# cmsh -c "softwareimage use default-image; show"

Parameter Value

-------------------------------- ----------------------------------------------
Creation time Thu, 08 Jun 2017 18:15:13 CEST

Enable SOL no

Kernel modules <44 in submode>

Kernel parameters

Kernel version 3.10.0-327.3.1.el7.x86_64

Locked no

Name default-image

...


Because measurements can be carried out on such a variety of entities, it means that the monitoring
and conditional actions that can be carried out on a BCM cluster can be very diverse. This makes entities
a powerful and versatile concept in BCM’s monitoring system for managing clusters.


**Listing Measurables Used By An Entity**
In cmsh, for an entity, such as a device within device mode, a list of the measurables used by that device
can be viewed with the measurables command.


**Example**


[basecm11->device]% measurables node001

Type Name Parameter Class Producer

------------ ------------------- ---------- --------- --------------
Enum DeviceStatus Internal DeviceState

HealthCheck ManagedServicesOk Internal CMDaemonState

HealthCheck defaultgateway Network defaultgateway

HealthCheck diskspace Disk diskspace

HealthCheck dmesg OS dmesg

...

...


The subsets of these measurables—enummetrics, metrics, and health checks—can be listed with the
enummetrics (section 10.2.2), metrics (section 10.2.3), or healthchecks (section 10.2.4) command.
In Base View, all the entities that are using health checks can be viewed via the navigation path:


Monitoring  - All Health Checks (figure 10.22 section 10.4.7)


**542** **Monitoring: Monitoring Cluster Devices**


**Listing Entities That Use A Measurable**
The entities using a specific measurable can be listed with the usage command:


**Example**


[basecm11->monitoring->measurable]% usage nfs_v3_server_total

Measurable Count Entities

-------------------- ------ -------------
nfs_v3_server_total 1 basecm11


If the number of measurables is too large to view on the screen:


**Example**


[basecm11->monitoring->measurable]% usage devicestatus

Measurable Count Entities

------------- ------ -------------------------------------------------------------------------------
DeviceStatus 21 node001,node002,node003,node004,node005,node006,node007,node008,node009,node010+


then the -v option can be used to list the entities over multiple lines:


**Example**


basecm11->monitoring->measurable]% usage -v devicestatus

Measurable Count Entities

------------- ------ -------------------------------------------------------------------------------
DeviceStatus 21 node001,node002,node003,node004,node005,node006,node007,node008,node009,node010,

node011,node012,node013,node014,node015,node016,node017,node018,node019,node020,

basecm11


**Listing Measurables From** monitoring **Mode**
Similarly, under monitoring mode, within the measurable submode, the list of measurable objects that
can be used can be viewed with a list command:


**Example**


[basecm11->monitoring]% measurable list
Type Name (key) Parameter Class Producer

------------ ------------------- ---------- ---------------------------- -----------------
Enum DeviceStatus Internal DeviceState

HealthCheck ManagedServicesOk Internal CMDaemonState
HealthCheck Mon::Storage Internal/Monitoring/Storage MonitoringSystem

HealthCheck chrootprocess OS chrootprocess

HealthCheck cmsh Internal cmsh

...

...


The subsets of these measurables—enummetrics, metrics, and health checks—can be listed with:
list enum (section 10.2.2), list metric (section 10.2.3), or list healthcheck (section 10.2.4).
In Base View, the equivalent to listing the measurables can be carried out via the navigation path:


Monitoring  - Measurables (figure 10.11, section 10.4.2)


**10.2 Monitoring Concepts And Definitions** **543**


**Viewing Parameters For A Particular Measurable From** monitoring **Mode**
Within the measurable submode, parameters for a particular measurable can be viewed with the show
command for that particular measurable:


**Example**


[basecm11->monitoring->measurable]% use devicestatus

[basecm11->monitoring->measurable[DeviceStatus]]% show

Parameter Value

-------------------------------- ---------------------
Class Internal

Consolidator none

Description The device status

Disabled no (DeviceState)

Maximal age 0s (DeviceState)
Maximal samples 4,096 (DeviceState)

Name DeviceStatus

Parameter

Producer DeviceState

Revision

Type Enum


**10.2.2** **Enummetrics**

An _enummetric_ is a measurable for an entity that can only take a limited set of values. At the time
of writing of this section (August 2024), DeviceStatus and wlm_slurm_state are the only enummetrics.
This may change in future versions of BCM.
The full list of possible values for the enummetric DeviceStatus is:
up, down, closed, installing, installer_failed, installer_rebooting, installer_callinginit,
installer_unreachable, installer_burning, burning, unknown, opening, going_down, pending, and

no data .

The full list of possible values for the enummetric wlm_slurm_state is:
allocated, completing, down, drain, draining, fail, failing, idle, maint, and mixed .
The enummetrics available for use can be listed from within the measurable submode of the

monitoring mode:


**Example**


[basecm11->monitoring->measurable]% list enum
Type Name (key) Parameter Class Producer

------ ------------------------ ------------------- --------- -------------------
Enum DeviceStatus Internal DeviceState

Enum wlm_slurm_state Workload slurm-state-count

[basecm11->monitoring->measurable]%


The list of enummetrics that is configured to be used by an entity, such as a device, can be viewed
with the enummetrics command for that entity:


**Example**


[basecm11->device]% enummetrics node001

Type Name Parameter Class Producer

------ ------------------------ ------------------- --------- ------------------
Enum DeviceStatus Internal DeviceState

[basecm11->device]%


**544** **Monitoring: Monitoring Cluster Devices**


The states that the entity has been through can be viewed with a dumpmonitoringdata command
(section 10.6.4):


**Example**


[basecm11->device]% dumpmonitoringdata -99d now devicestatus node001

Timestamp Value Info

-------------------------- ----------- ---------
2017/07/03 16:07:00.001 down

2017/07/03 16:09:00.001 installing

2017/07/03 16:09:29.655 no data

2017/07/03 16:11:00 up
2017/07/12 16:05:00 up


The parameters of an enummetric such as devicestatus can be viewed and set from monitoring
mode, from within the measurable submode (page 543).


**10.2.3** **Metrics**

A _metric_ for an entity is typically a numeric value for an entity. The value can have units associated with
it.

In the basic example of section 10.1, the metric value considered was CPUUser, measured at the
default regular time intervals of 120s.
The value can also be defined as no data . no data is substituted for a null value when there is no
response for a sample. no data is not a null value once it has been set. This means that there are no null
values stored for monitored data.

Other examples for metrics are:


 - LoadOne (value is a number, for example: 1.23)


 - WriteTime (value in ms/s, for example: 5 ms/s)


 - MemoryFree (value in readable units, for example: 930 MiB, or 10.0 GiB)


A metric can be a built-in, which means it comes with BCM as integrated code within CMDaemon. This
is based on c++ and is therefore much faster than the alternative. The alternative is that a metric can be

a standalone script, which means that it typically can be modified more easily by an administrator with
scripting skills.
The word metric is often used to mean the script or object associated with a metric as well as a metric
value. The context makes it clear which is meant.

A list of metrics in use can be viewed in cmsh using the list command from monitoring mode:


**Example**


[basecm11->monitoring]% measurable list metric
Type Name (key) Parameter Class Producer

------- ------------------------ -------------- ------------------ ------------
Metric AlertLevel count Internal AlertLevel

Metric AlertLevel maximum Internal AlertLevel

...


In Base View, the metrics can be viewed with the navigation path:


Monitoring  - Measurables (figure 10.11, section 10.4.2)


A list of metrics in use by an entity can be viewed in cmsh using the metrics command for that entity.
For example, for the entity node001 in mode devices :


**10.2 Monitoring Concepts And Definitions** **545**


**Example**


[basecm11->devices]% metrics node001

Type Name Parameter Class Producer

------- ------------------------ -------------- --------- -------------
Metric AlertLevel count Internal AlertLevel

Metric AlertLevel maximum Internal AlertLevel

...


The parameters of a metric such as AlertLevel:count can be viewed and set from monitoring mode,
from within the measurable submode, just as for the other measurables:


**Example**


[basecm11->monitoring->measurable]% use alertlevel:count

[basecm11->monitoring->measurable[AlertLevel:count]]% show

Parameter Value

-------------------------------- ---------------------
Class Internal

Consolidator default

Cumulative no

Description Number of active triggers

Disabled no

Maximal age 0s

Maximal samples 0

Maximum 0

Minimum 0

Name AlertLevel

Parameter count

Producer AlertLevel

Revision

Type Metric


The equivalent Base View navigation path to edit the parameters is:


Monitoring  - Measurables  - Edit


**10.2.4** **Health Check**

A _health check_ value is a response to a check carried out on an entity. The response indicates the health
of the entity for the check that is being carried out.
For example, the ssh2node health check, which runs on the head node to check if the SSH port 22
passwordless access to regular nodes is reachable.
A health check is run at a regular time interval, and can have the following possible values:


 - PASS : The health check succeeded. For example, if ssh2node is successful, which suggests that an
ssh connection to the node is fine.


 - FAIL : The health check failed. For example, if ssh2node was rejected. This suggests that the ssh
connection to the node is failing.


 - UNKNOWN : The health check did not succeed, did not fail, but had an unknown response. For example, if ssh2node has a timeout, for example due to routing or other issues. It means that it is
unknown whether the connection is fine or failing, because the response that came in is unknown.
Typically the administrator should investigate this further.


**546** **Monitoring: Monitoring Cluster Devices**


 - no data : The health check did not run, so no data was obtained. For example, if ssh2node is
disabled for some time, then no data values were obtained during this time. Since the health check
is disabled, it means that no data cannot be recorded during this time by ssh2node . However,
because having a no data value in the monitoring data for this situation is a good idea—explicitly
knowing about having no data is helpful for various reasons—then no data values can be set, by
CMDaemon, for samples that have no data.


Other examples of health checks are:


 - diskspace : check if the hard drive still has enough space left on it


 - mounts : check mounts are accessible


 - mysql : check status and configuration of MySQL is correct


 - hpraid : check RAID and health status for certain HP RAID hardware


These and others can be seen in the directory: /cm/local/apps/cmd/scripts/healthchecks .


**Health Checks**

In Base View, the health checks that can be configured for all entities can be seen with the navigation
path:


Monitoring  - Measurables (figure 10.11, section 10.4.2)


Options can be set for each health check by clicking through via the Edit button.


**All Configured Health Checks**
In Base View, health checks that have been configured for all entities can be seen with the navigation
path:


Monitoring  - All Health Checks (section 10.4.7)


The view can be filtered per column.


**Configured Health Checks For An Entity**
An overview can be seen for a particular entity < _entity_ - via the navigation path:


Monitoring  - Health status  - < _entity_  -  - Show


**Severity Levels For Health Checks, And Overriding Them**
A health check has a settable severity (section 10.2.7) associated with its response defined in the trigger
options.
For standalone healthchecks, the severity level defined by the script overrides the value in the trigger. For example, FAIL 40 or UNKNOWN 10, as is set in the hpraid health check ( /cm/local/apps/cmd/
scripts/healthchecks/hpraid ).
Severity values are processed for the AlertLevel metric (section 10.2.8) when the health check runs.


**Default Templates For Health Checks And Triggers**
A health check can also launch an action based on any of the response values.
Monitoring triggers have the following default templates:


 - Failing health checks : With a default severity of 15


 - Passing health checks : With a default severity of 0


**10.2 Monitoring Concepts And Definitions** **547**


 - Unknown health checks : With a default severity of 10


The severity level is one of the default parameters for the corresponding health checks. These defaults
can also be modified to allow an action to be launched when the trigger runs, for example, sending an
e-mail notification whenever any health check fails.
With the default templates, the actions are by default set for all health checks. However, specific
actions that are launched for a particular measurable instead of for all health checks can be configured.
To do this, one of the templates can be cloned, the trigger can be renamed, and an action can be set to
launch from a trigger. The reader should be able to recognize that in the basic example of section 10.1 this
is how, when the metric measurable CPUUser crosses 50 jiffies/s, the killallyestrigger is activated,
and the killallyes action script is run.


**10.2.5** **Trigger**
A _trigger_ is a threshold condition set for a sampled measurable. When a sample crosses the threshold
condition, it enters or leaves a zone that is demarcated by the threshold.
A trigger zone also has a settable severity (section 10.2.7) associated with it. This value is processed
for the AlertLevel metric (section 10.2.8) when an action is triggered by a threshold event.
Triggers are discussed further in section 10.4.5.


**10.2.6** **Action**

In the basic example of section 10.1, the action script is the script added to the monitoring system to kill
all yes processes. The script runs when the condition is met that CPUUser crosses 50 jiffies/s.
An _action_ is a standalone script or a built-in command that is executed when a condition is met, and
has exit code 0 on success. The condition that is met can be:


 - A FAIL, PASS, UNKNOWN, or no data from a health check


  - A trigger condition. This can be a FAIL or PASS for conditional expressions.


  - State flapping (section 10.2.9).


The actions that can be run are listed from within the action submode of the monitoring mode.


**Example**


[basecm11->monitoring->action]% list
Type Name (key) Run on Action

----------- ---------------- ---------------------------------------------------------
Drain Drain Active Drain node from all WLM

Email Send e-mail Active Send e-mail

Event Event Active Send an event to users with connected client

ImageUpdate ImageUpdate Active Update the image on the node

PowerOff PowerOff Active Power off a device

PowerOn PowerOn Active Power on a device

PowerReset PowerReset Active Power reset a device

Reboot Reboot Node Reboot a node

Script killallyesaction Node /cm/local/apps/cmd/scripts/actions/killallyes
Script killprocess Node /cm/local/apps/cmd/scripts/actions/killprocess.pl
Script remount Node /cm/local/apps/cmd/scripts/actions/remount
Script testaction Node /cm/local/apps/cmd/scripts/actions/testaction

Shutdown Shutdown Node Shutdown a node

Undrain Undrain Active Undrain node from all WLM


The Base View equivalent is accessible via the navigation path:


**548** **Monitoring: Monitoring Cluster Devices**


Monitoring - Actions (figure 10.17, section 10.4.4)


Configuration of monitoring actions is discussed further in section 10.4.4.


**10.2.7** **Severity**
_Severity_ is a positive integer value that the administrator assigns for a trigger. It takes one of these 6
suggested values:


**Value** **Name** **Icon** **Description**


0 debug debug message


0 info informational message


10 notice normal, but significant, condition


20 warning warning conditions


30 error error conditions


40 alert action must be taken immediately


Severity levels are used in the AlertLevel metric (section 10.2.8). They can also be set by the administrator in the return values of health check scripts (section 10.2.4).
By default the severity value is 15 for a health check FAIL response, 10 for a health check UNKNOWN
response, and 0 for a health check PASS response (section 10.2.4).


**10.2.8** **AlertLevel**

_AlertLevel_ is a special metric. It is sampled and re-calculated when an event with an associated Severity
(section 10.2.7) occurs. There are three types of AlertLevel metrics:


1. AlertLevel (count) : the _number_ of events that are at notice level and higher . The aim of this
metric is to alert the administrator to the _number_ of issues.


2. AlertLevel (max) : simply the maximum severity of the latest value of all the events. The aim of
this metric is to alert the administrator to the severity of the _most important_ issue.


3. AlertLevel (sum) : the _sum_ of the latest severity values of all the events. The aim of this metric is
to alert the administrator to the _overall severity_ of issues.


**10.2.9** **Flapping**
_Flapping_, or _State Flapping_, is when a measurable trigger is detecting changes (section 10.4.5) that are too
frequent. That is, the measurable goes in and out of the zone too many times over a number of samples.
In the basic example of section 10.1, if the CPUUser metric crossed the threshold zone 5 times within
5 minutes (the default values for flap detection), then it would by default be detected as flapping. A
flapping alert would then be recorded in the event viewer, and a flapping action could also be launched
if configured to do so.


**10.2.10** **Data Producer**

A data producer produces measurables. Sometimes it can be a group of measurables, as in the measurables provided by a data producer that is being used:


**Example**


[basecm11->monitoring->measurable]% list -f name:25,producer:15 | grep ProcStat

BlockedProcesses ProcStat

CPUGuest ProcStat

CPUIdle ProcStat


**10.2 Monitoring Concepts And Definitions** **549**


CPUIrq ProcStat

CPUNice ProcStat

CPUSoftIrq ProcStat

CPUSteal ProcStat

CPUSystem ProcStat

CPUUser ProcStat

CPUWait ProcStat

CtxtSwitches ProcStat

Forks ProcStat

Interrupts ProcStat

RunningProcesses ProcStat


Sometimes it may just be one measurable, as provided by a used data producer:


**Example**


[basecm11->monitoring->measurable]% list -f name:25,producer:15 | grep ssh2node

ssh2node ssh2node


It can even have no measurables, and just be an empty container for measurables that are not in use
yet.
In cmsh all possible data producers (used and unused) can be listed as follows:


**Example**


[basecm11->monitoring->setup]% list


The equivalent in Base View is via the navigation path:


Monitoring - Data Producers


The data producers configured for an entity, such as a head node basecm11, can be listed with the
monitoringproducers command:


**Example**


[basecm11->device[basecm11]]% monitoringproducers

Type Name Arguments Measurables Node execution filters

------------------ ----------------- ------------ ------------ ---------------------
AlertLevel AlertLevel 3 / 231 <0 in submode>

CMDaemonState CMDaemonState 1 / 231 <0 in submode>

ClusterTotal ClusterTotal 18 / 231 <1 in submode>

Collection NFS 32 / 231 <0 in submode>

Collection sdt 0 / 231 <0 in submode>

DeviceState DeviceState 1 / 231 <1 in submode>

HealthCheckScript chrootprocess 1 / 231 <1 in submode>
HealthCheckScript cmsh 1 / 231 <1 in submode>
HealthCheckScript defaultgateway 1 / 231 <0 in submode>
HealthCheckScript diskspace 1 / 231 <0 in submode>
HealthCheckScript dmesg 1 / 231 <0 in submode>
HealthCheckScript exports 1 / 231 <0 in submode>
HealthCheckScript failedprejob 1 / 231 <1 in submode>
HealthCheckScript hardware-profile 0 / 231 <1 in submode>
HealthCheckScript ib 1 / 231 <0 in submode>
HealthCheckScript interfaces 1 / 231 <0 in submode>
HealthCheckScript ldap 1 / 231 <0 in submode>


**550** **Monitoring: Monitoring Cluster Devices**


HealthCheckScript lustre 1 / 231 <0 in submode>
HealthCheckScript mounts 1 / 231 <0 in submode>
HealthCheckScript mysql 1 / 231 <1 in submode>
HealthCheckScript ntp 1 / 231 <0 in submode>
HealthCheckScript oomkiller 1 / 231 <0 in submode>
HealthCheckScript opalinkhealth 1 / 231 <0 in submode>
HealthCheckScript rogueprocess 1 / 231 <1 in submode>
HealthCheckScript schedulers 1 / 231 <0 in submode>
HealthCheckScript smart 1 / 231 <0 in submode>
HealthCheckScript ssh2node 1 / 231 <1 in submode>
Job JobSampler 0 / 231 <1 in submode>
JobQueue JobQueueSampler 7 / 231 <1 in submode>
MonitoringSystem MonitoringSystem 36 / 231 <1 in submode>

ProcMemInfo ProcMemInfo 10 / 231 <0 in submode>

ProcMount ProcMounts 2 / 231 <0 in submode>

ProcNetDev ProcNetDev 18 / 231 <0 in submode>

ProcNetSnmp ProcNetSnmp 21 / 231 <0 in submode>

ProcPidStat ProcPidStat 5 / 231 <0 in submode>

ProcStat ProcStat 14 / 231 <0 in submode>

ProcVMStat ProcVMStat 6 / 231 <0 in submode>

Smart SmartDisk 0 / 231 <0 in submode>

SysBlockStat SysBlockStat 20 / 231 <0 in submode>
SysInfo SysInfo 5 / 231 <0 in submode>

UserCount UserCount 3 / 231 <1 in submode>


The displayed data producers are the ones configured for the entity, even if there are no measurables
used by the entity.
Data producer configuration in Base View is discussed further in section 10.4.1.


**Access Control For Monitoring Data**
**Access control to data producers:** An access control setting for a data producer determines who can
plot (via the measurables monitoring interface used by Base View and the User Portal), or view data
(using the text-based interface of cmsh or pythoncm ) from the measurables generated by a data producer.
Thus, for example, the charts in the user portal (section 10.8) can be restricted according to the data
producer that generates them.
There are three possible settings for access control for data producers. If the data producer is set to:


1. Public : then it means any user can, by default, plot/view data derived from that data producer.
This is because by default a user has the token PLOT_TOKEN in their profile.


2. Private : then it means that a non-root user cannot, by default, plot/view data derived
from that data producer. This is because, by default, non-root users do not have the token
PRIVATE_MONITORING_TOKEN in their profile. If that token is in the profile, then the user has an elevated privilege, and can plot/view data, just like root.


3. Individual : then it means that a non-root user, by default, can plot/view the data only if the job
associated with that data was run by that same non-root user. More verbosely, with the default
user settings: the user who ran a job for which job measurables are produced by a data producer,
must be the same as the user that who wants to plot/view the data, or else the data cannot be plotted/viewed. [1] The exception to this is, as already suggested, if the user that wants to plot/view


1 Even more verbosely: Individual access control is meant for job-based measurables, and works like this:
All monitoring data is stored per (entity, measurable) pair.
If the measurable has an access control value of individual, then a user check is performed. If the login name is the same as
the user that owns the entity, then data can be plotted/viewed. If the user check does not match, then no data is returned.
Jobs—which are entities—are owned by the user that ran the job. Similarly Prometheus (entities) can have a ’user="Alice"’ label
set, to define ownership. No other entity managed by BCM is owned by a user.
For all unowned entities, individual access is equivalent to private access.


**10.2 Monitoring Concepts And Definitions** **551**


the data is root, or has a user profile with the token PRIVATE_MONITORING_TOKEN . In that case the data
can be plotted/viewed.


On a regular BCM cluster, only a few low level data producers are set to private . An administrator
can decide to set a data producer access control value to one of the three possible values, by using the
setup submode of monitoring mode:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% monitoring setup

[basecm11->monitoring->setup]% use mounts

[basecm11->...[mounts]]% set access private

[basecm11->...*[mounts*]]% commit


If a data producer is newly added, then by default its access control value is set to public . Changing
this to private at a later time means that access to past and future data values from that data producer
are affected by the private setting. If access is changed once more back to public, then it means that
access to past and future data values are once again viewable and plottable by all users.
The current settings for access control for the data producers can be seen with:


**Example**


[root@basecm11 ~]# cmsh -c "monitoring setup; list -f name:40,access"
name (key) access

---------------------------------------- -------------------
AggregateNode Public

AlertLevel Public

BigDataTools Public

CMDaemonState Public

Cassandra Public

ClusterTotal Public

...


**Access control to measurables:** Measurables can also have access controls.

Access control for measurables is by default inherited from the data producer that generates it. It
can be overwritten:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% monitoring measurable

[basecm11->monitoring->measurable]% use loadone

[basecm11->...[LoadOne]]% get access
Public (SysInfo)

[basecm11->...[LoadOne]]% set access private

[basecm11->...*[LoadOne*]]% commit


A measurable can thus take an access control value of Public, Private, or Individual . It can also
explicitly be set to a value of inherit, which sets it to the value of its data producer. The inheritance
is indicated in cmsh by enclosing the parent data producer in parentheses, as shown in the preceding
example.
The current settings for access control for the measurables can be seen with:


**Example**


**552** **Monitoring: Monitoring Cluster Devices**


[root@basecm11 ~]# cmsh -c "monitoring measurable; list -f name:40,access"
name (key) access

---------------------------------------- -------------------
AlertLevel Public

AlertLevel Public

AlertLevel Public

AvgJobDuration Public

BlockedProcesses Public

...


**10.2.11** **Conceptual Overview: The Main Monitoring Interfaces Of Base View**
Base View, besides having the default settings mode, has some other display modes and logging view
modes that can be selected via the 11 icons in the top right corner of the Base View standard display
(figure 10.5):



Chargeback
(Chapter 13)



**6**


Toggle
dark theme



**6**


Search box



Settings
(section 10.4)



**6**



**6**


Monitoring
(section 10.3)



**6**



**6**



**6**



**6**


Action

results



**6**



**6**


Unsaved
entities



**6**


Account



Accounting
(Chapter 12)



Events



Background tasks



Figure 10.5: Base View: Top Right Corner Icons


The 11 icons are described from left to right next:


1. Toggle dark theme option allows the display of Base View to be toggled to a darker theme.


2. Search box allows resource to be searched for, with predictive text suggestions.


3. Settings mode is active when Base View first starts up.


The Settings mode has a navigation panel to the left of it, showing the resources of the cluster
as expandable items. One of the resources is Monitoring . This resource should not be confused
with the Base View Monitoring mode, which is launched by the next icon in figure 10.5. The
Monitoring resource is about configuring how items are monitored and how their data values are
collected, and is discussed further in section 10.4.


4. The Monitoring mode allows visualization of the data values collected according to the specifications of the Base View Monitoring resource. The visualization allows graphs to be configured,
and is discussed further in section 10.3.


5. The Accounting mode typically allows visualization of job resources used by users, although it
can be used to visualize job resources used by other entities that are used as a classifier. This is
helpful tracking resources consumed by users. Job accounting is discussed further in Chapter 12.


6. The Chargeback mode allows the monitoring of resources requested over a period for jobs run by
selected groups (Chapter 13).


7. The Events icon allows logs of events (section 10.10) to be viewed.


8. The Action results icon allows the logs of the results of actions to be viewed.


9. The Background tasks icon allows background tasks to be viewed.


**10.3 Monitoring Visualization With Base View** **553**


10. The Unsaved entities icon allows entities that have not yet been saved to be viewed.


11. The Account handling icon allows account settings to be managed for the Base View user.


The monitoring aspects of the first two icons are discussed in greater detail in the sections indicated.


**10.3** **Monitoring Visualization With Base View**


The Monitoring icon in the menu bar of Base View (item 4 in figure 10.5) launches an intuitive visualization tool that is the main GUI tool for getting a feel of the system’s behavior over periods of time. With
this tool the measurements and states of the system can be viewed as resizable and overlayable graphs.
The graphs can be zoomed in and out on over a particular time period, the graphs can be laid out on top
of each other or the graphs can be laid out as a giant grid. The graph scale settings can also be adjusted,
stored and recalled for use the next time a session is started.

An alternative to Base View’s visualization tool is the command-line cmsh . This has the same func
tionality in the sense that data values can be selected and studied according to configurable parameters
with it (section 10.6). The data values can even be plotted and displayed on graphs with cmsh with the
help of unix pipes and graphing utilities. However, the strengths of monitoring with cmsh lie elsewhere:
cmsh is more useful for scripting or for examining pre-decided metrics and health checks rather than a
quick visual check over the system. This is because cmsh needs more familiarity with options, and is designed for text output instead of interactive graphs. Monitoring with cmsh is discussed in sections 10.5
and 10.6.

Visualization of monitoring graphs with Base View is now described.


**10.3.1** **The Monitoring Window**
If the Monitoring icon is clicked on from the menu bar of Base View (figure 10.5), then a monitoring
window for visualizing data opens up. By default, this displays a dashboard called Critical Services
which has two plots panels. The plot panels are graph axes with a time scale going back some time on
the _x_ -axis, and with a _y_ -axis that allows measurable data values plotted against time (figure 10.6).
By default, the data values that are plotted are for the ManagedServicesOK health check. The first
panel displays the plots for the head node, the second panel displays the plots for all the regular nodes
in the default category..


Figure 10.6: Base View Monitoring Window: Default Plot Panels


**554** **Monitoring: Monitoring Cluster Devices**


**Finding And Selecting The Measurable To Be Plotted**
To plot measurables, the entity which it belongs to should be selected from the navigation menu on
the left-hand side. Once that has been selected, a class for that measurable can be chosen, and then
the measurable itself can be selected. For example, to plot the measurable CPUUser for a head node
basecm11, it can be selected from the navigation navigation path:
_Menu bar_  - _Monitoring icon_  - Device  - basecm11  - CPU  - CPUUser
Sometimes, finding a measurable is easier if the Expand all widget is used, together with the Search
box. Typing in CPUUser in the search box then shows all the measurables with that text (figure 10.7). The
search is case-insensitive.


Figure 10.7: Base View Monitoring Window: Search Box In Navigation


The search box can handle some simple regexes too, with .* and | taking their usual meaning:


**Example**


 - node001.*cpuuser : select a measurable with a data path that starts with node001 and ends with
cpuuser, with 0 or more characters of any kind in between.


 - (node001|node002).*cpuuser : as for preceding example, but including node002 as an alternative

to node001 .


The / (forward slash) allows filtering according to the data path. It corresponds to the navigation
depth in the tree hierarchy:


**Example**


 - node001/cpu/cpuuser : search for a measurable with a data path that matches node001/cpu/

cpuuser


**Plotting The Measurable**
Once the measurable is selected, it can be drag-and-dropped into a plot panel. This causes the data
values to be plotted.


**10.4 Monitoring Configuration With Base View** **555**


When a measurable is plotted into a panel, two graph plots are displayed. The smaller, bottom
plot, represents the polled value as a bar chart. The larger, upper plot, represents an interpolated line
graph. Different kinds of interpolations can be set. To get a quick idea of the effect of different kinds
of interpolations, [https://bl.ocks.org/mbostock/4342190](https://bl.ocks.org/mbostock/4342190) is an interactive overview that shows how
they work on a small set of values.
The time axes can be expanded or shrunk using the mouse wheel in the graphing area of the plot
panel. The resizing is carried out centered around the position of the mouse pointer.


**10.4** **Monitoring Configuration With Base View**


This section is about the configuration of monitoring for measurables, and about setting up trigger
actions.

If Base View is running in the standard Settings mode, which is the gear icon in figure 10.5,
page 552, then selecting Monitoring from the navigation menu resources makes the following menu
items available for managing or viewing:


 - Data Producers (section 10.4.1)


 - Measurables (section 10.4.2)


 - Consolidators (section 10.4.3)


 - Actions (section 10.4.4)


 - Triggers (section 10.4.5)


 - Health status (section 10.4.6)


 - All Health checks (section 10.4.7)


 - Standalone Monitored Entities (section 10.4.8)


 - PromQL Queries (section 10.4.9)


 - Resources (section 10.4.10)


 - Types (section 10.4.11)


**556** **Monitoring: Monitoring Cluster Devices**


Figure 10.8: Base View Monitoring Configuration Settings


These settings (figure 10.8) are now discussed in detail.


**10.4.1** **Monitoring Configuration: Data Producers**
The navigation path:
Monitoring - Dataproducers
opens up the Monitoring Data Producer list screen, which lists all the data producers (figure 10.9).


Figure 10.9: Base View Monitoring Configuration Data Producers


**10.4 Monitoring Configuration With Base View** **557**


Data producers are introduced in section 10.2.10.
Each data producer can have its settings edited within a subwindow. For example, the ProcStat
data producer, which produces data for several measurables, including CPUUser, has the settings shown
in figure 10.10:


Figure 10.10: Base View Monitoring Configuration Data Producer: ProcStat


When the data producer takes samples to produce data, run length encoding (RLE) is used to compress the number of samples that are stored as data. Consolidation is carried out on the RLE samples.
Consolidation in BCM means gathering several data values, and making one value from them over
time periods. Consolidation is done as data values are gathered. The point at which data values are
discarded, if ever, is thus not dependent on consolidation.
The data producer settings that are seen in the subwindow of figure 10.10 include the following:


 - Maximal samples : the maximum number of RLE samples that are kept. If set to 0, then the number
of samples is not considered.


 - Maximal Age : the maximum age of RLE samples that are kept. If Maximal Age is set to 0 then the
sample age is not considered.


With Maximal samples and Maximal Age, the first of the rules that is reached is the one that causes
the exceeding RLE samples to be dropped.


Samples are kept forever if Maximal samples and Maximal Age are both set to 0 . This is discouraged due to the risk of exceeding the available data storage space.


 - Interval : the interval between sampling, in seconds.


 - Offset : A time offset from start of sampling. Some sampling depends on other sampling to be
carried out first. This is used, for example, by data producers that rely on sampling from other
data producers. For example, the AggregateNode data producer, which has measurables such as
TotalCPUIdle and TotalMemoryFree . The samples for AggregateNode depend upon the ProcStat


**558** **Monitoring: Monitoring Cluster Devices**


data producer, which produces the CPUIdle measurable; and the ProcMemInfo data producer,
which produces the MemoryFree measurable.


 - Fuzzy offset : a multiplier in the range from 0 to 1. It is multiplied against the sampling time
interval to fix a maximum value for the time offset for when the sampling takes place. The actual
offset used per node is spread out reasonably evenly within the range up to that maximum time
offset.


For example, for a sampling time interval of 120s:


If the offset is 0, then there is no offset, and the sampling is attempted for all nodes at time instant
when the interval restarts. This can lead to an overload at the time of sampling.


If, on the other hand, the offset is 0.25, then the sampling is done within a range offset from the
time of sampling by a maximum of 0.25 _×_ 120 `s` = 30 `s` . So, each node is sampled at a time that is
offset by up to 30s from when the 120s interval restarts. From the time the change in value of the
fuzzy offset starts working, the offset is set for each node. The instant at which sampling is carried
out on a node then differs from the other nodes, even though each node still has an interval of 120s
between sampling. An algorithm is used that tends to even out the spread of the instants at which
sampling is carried out within the 30s range. The spreading of sampling has the effect of reducing
the chance of overload at the time of sampling.


 - Consolidator : By default, set to the default group. The default group consolidates (summarizes) the RLE samples over periods of an hour, a day, and a week. Consolidators are explained
further in section 10.4.3.


 - Node execution filters : A way to filter execution (restrict execution) of the data producer. It
tells BCM where the data producer runs. If not set, then the data producer runs on all nodes
managed by CMDaemon. Filters can be for nodes, types, overlays, resources, and categories.


 - Execution multiplexer : A way to multiplex execution (have execution work elsewhere) for a
data producer. It tells BCM about the entities that the data producer is sampling for. A data producer gathers data at the nodes defined by the node execution filter, and with multiplex execution
the data producer gathers samples from other entities. These entities can be nodes, types, overlays, and resources. The entities from which it can sample are defined into groups called execution
multiplexers. Execution multiplexers can thus be node multiplexers, type multiplexers, overlay
multiplexers, or resource multiplexers.


 - When : This has 4 possible values:


1. Timed : Data producer is run at a periodic Interval . This is the default.


2. On demand : Data producer is only run on demand, and not at a periodic Interval .


3. Out of band : Data producer is only run on out of band connections.


4. On start : Data producer is only run on start and not at a periodic Interval .


 - Only when idle : By default a data producer runs regardless of how busy the nodes are. However,
if the Only when idle setting is enabled, then the data producer runs only when the node is idle.
Idle is a condition that is defined by the metric condition LoadOne>1 (page 930).


**10.4.2** **Monitoring Configuration: Measurables**
The Measurables window lists the available measurables (figure 10.11):


**10.4 Monitoring Configuration With Base View** **559**


Figure 10.11: Base View Monitoring Configuration Measurables


There are many measurables, so using the search box in the menu bar (item 2 in list describing
figure 10.5) can be handy.
From the measurables window, a subwindow can be opened with the Edit button for a measurable.
This accesses the options for a particular measurable (figure 10.12):


**560** **Monitoring: Monitoring Cluster Devices**


Figure 10.12: Base View Monitoring Configuration Measurables Options Subwindow


The options shown include the sampling options: Maximal age, Maximal samples, and
Consolidator . The sampling options work as described for data producers (section 10.4.1).
Other options for a metric are setting the Maximum and Minimum values, the Unit used, and whether
the metric is Cumulative .

If a metric is cumulative, then it is monotonic. Monotonic means that the metric only increments (is
cumulative), as time passes. In other words, if the metric is plotted as a graph against time, with time on
the _x_ -axis, then the metric never descends. Normally the increments are from the time of boot onward,
and the metric resets at boot. For example, the number of bytes received at an interface is cumulative,
and resets at boot time.

Usually the cluster administrator is only interested in the differential value of the metric per sample
interval. That is, the change in the value of the current sample, from its value in the preceding sample.
For example, bytes/second, rather than total number of bytes up to that time from boot.


**10.4.3** **Monitoring Configuration: Consolidators**

**Introduction To Consolidators**

The concept of consolidators is explained using simple ascii graphics in Appendix K, while the cmsh
interface to the consolidators submode is discussed in section 10.5.2.

In this current section, the Base View interface to consolidators is discussed.
In Base View, the Monitoring Consolidator list window lists all consolidator groups (fig

**10.4 Monitoring Configuration With Base View** **561**


ure 10.13). There are two pre-existing consolidator groups: default and none .


Figure 10.13: Base View Monitoring Consolidator list


Subwindows allow the consolidator components (consolidator items) to be created or modified (figure 10.14).


Figure 10.14: Base View Monitoring Configuration Consolidator Items


**The** none **Consolidator Group**
The none consolidator group has no consolidators. Using a consolidator group of none for a measurable
or data producer means that samples are not consolidated. This can be dangerous if the cluster is more
likely to run out of space due to unrestrained sampling. Unrestrained sampling can occur, for example,
if Maximal Age and Maximal samples (section 10.4.1) for data producers are both set to 0 .


**The** default **Consolidator Group**
The default consolidator group consists of the consolidators hour, day, and week . These are, unsurprisingly, defined to consolidate the samples in intervals of an hour, day, or week.
A consolidated value is generated on-the-fly. So, for example, during the hour that samples of a
measurable come in, the hour consolidator uses the samples to readjust the consolidated value for that
hour. When the hour is over, the consolidated value is stored for that hour as the data value for that
hour, and a new consolidation for the next hour begins.
Consolidator values are kept, as for sample values, until the Maximal Age and Maximal sample settings prevent data values being kept.


**562** **Monitoring: Monitoring Cluster Devices**


**Other Consolidator Group Possibilities**
Other sets of custom intervals can also be defined. For example, instead of the default consolidator group, consisting of consolidators of an hour, a day, and a week ; a similar group called the
decimalminutes consolidator group, consisting of consolidators of 1min, 10min, 100min, 1000min,
10000min, could be created with the appropriate intervals (figure 10.15):


Figure 10.15: Base View Monitoring Configuration Consolidators: decimalminutes Consolidator Group


**Consolidator Item Settings**
Consolidator items (consolidator components) are the component members of the consolidator groups.
The items have settings as properties, which can be managed (figure 10.16).


**10.4 Monitoring Configuration With Base View** **563**


Figure 10.16: Base View Monitoring Configuration Consolidators: Consolidator Item Settings


The consolidator item hour, which is within the default consolidators group, can have its properties
edited using the navigation path:


Monitoring - Consolidators[default] - Edit - Consolidator[hour] - Edit


The properties that can be set for a consolidator item are:


 - Name : The name of the consolidator item. By default, for the consolidator group default, the
consolidator items with names of Day, Hour, and Month are already set up, with appropriate values
for their corresponding fields.


 - Maximal samples : The maximum number of samples that are stored for that consolidator item.
This should not be confused with the Maximal samples of the measurable being consolidated.


 - Interval : The time period (in seconds) covered by the consolidator sample. For example, the
consolidator with the name Hour has a value of 3600. The property should not be confused with
the time period between samples of the measurable being consolidated.


 - Offset : The time offset from the default consolidation time, explained in more detail shortly.


 - Kind : The kind of consolidation that is done on the raw data samples. The value of kind is set
to average by default. The output result for a processed set of raw data—the consolidated data
point—is an average, a maximum or a minimum of the input raw data values. Kind can thus have
the value Average, Maximum, or Minimum . The value of kind is set to average by default.


**564** **Monitoring: Monitoring Cluster Devices**


For a given consolidator, when one Kind is changed to another, the historically processed data
values become inconsistent with the newer data values being consolidated. Previous consolidated
data values for that consolidator are therefore discarded during such a change.


To understand what Offset means, the Maximal samples of the measurable being consolidated can
be considered. This is the maximum number of raw data points that the measurable stores. When this
maximum is reached, the oldest data point is removed from the measurable data when a new data point
is added. Each removed data point is gathered and used for data consolidation purposes.
For a measurable that adds a new data point every Interval seconds, the time `t` `raw gone`, which is
how many seconds into the past the raw data point is removed, is given by:
`t` `raw gone` = ( `Maximal samples` ) `measurable` _×_ ( `Interval` ) `measurable`
This value is also the default consolidation time, because the consolidated data values are normally
presented from `t` `raw gone` seconds ago, to further into the past. The default consolidation time occurs
when the Offset has its default, zero value.
If however the Offset period is non-zero, then the consolidation time is offset, because the time into
the past from which consolidation is presented to the user, `t` `consolidation`, is then given by:
`t` `consolidation` = `t` `raw gone` + `Offset`
The monitoring visualization graphs then show consolidated data from `t` `consolidation` seconds into
the past, to further into the past [2] .


**10.4.4** **Monitoring Configuration: Actions**
Actions are introduced in section 10.2.6. The Actions window (figure 10.17) displays actions that BCM
provides by default, and also displays any custom actions that have been created:


2 For completeness: the time `t` `consolidation gone`, which is how many seconds into the past the consolidated data goes and is
viewable, is given by an analogous equation to that of the equation defining `t` `raw gone` :
`t` `consolidation gone` = ( `Maximalsamples` ) `consolidation` _×_ ( `Interval` ) `consolidation`


**10.4 Monitoring Configuration With Base View** **565**


Figure 10.17: Base View Monitoring Configuration: Actions


The killallyes script from the basic example of section 10.1 would show up here if it has been
implemented.
Actions are triggered, by triggers (section 10.4.5).
By default, the following actions exist:


 - PowerOn : Powers on the node


 - PowerOff : Powers off the node


 - PowerReset : Hard resets the node


 - Drain : Drains the node (does not allow new jobs on that node)


 - Undrain : Undrains the node (allows new jobs on that node)


 - Reboot : Reboots node via the operating system


 - Shutdown : Shuts the node down via the operating system


 - ImageUpdate : Updates the node from the software image


 - Event : Sends an event to users connected with cmsh or Base View


 - killprocess : A script to kill a process


 - remount : A script to remount all devices


 - testaction : A test script


**566** **Monitoring: Monitoring Cluster Devices**


 - Send e-mail to administrators : Sends an e-mail out


The preceding actions show their options when the associated Edit button is clicked. A subwindow
with options opens up. The following options are among those then displayed:


 - Run on : What nodes the action should run on. Choices are:


**–** Active head node : the action runs on the active node only


**–** Node : the action runs on the triggering node


**–**
Monitoring node : the action runs on the monitoring node


 - Allowed time : The time interval in the 24 hour clock cycle that the action is allowed to start
running. The interval can be restricted further to run within certain days of the week, months of
the year, or dates of the month. Days and months must be specified in lower case.


The Base View interface for setting the time can be used to set the allowed times.


The allowed times have a format that is also used in cmsh . Rather than defining a formal syntax,
some cmsh examples are given of possible formats, with explanations:


**–** november-march : November to March. The months April to October are forbidden.


**–**
november-march{monday-saturday} : As in the preceding, but all Sundays are also forbidden.


**–**
november-march{monday-saturday{13:00-17:00}} : Restricted to the period defined in the
preceding example, and with the additional restriction that the action can start running only
during the time 13:00-17:00.


**–** 09:00-17:00 : All year long, but during 09:00-17:00 only.


**–**
monday-friday{9:00-17:00} : All year long, but during 9:00-17:00 only, and not on Saturdays
or Sundays.


**–**
november-march{monday-saturday{13:00-17:00}} : Not in April to October. In the other
months, only on Mondays to Saturdays, from 13:00-17:00.


**–**
may-september{monday-friday{09:00-18:00};saturday-sunday{13:00-17:00}} : May to
September, with: Monday to Friday 09:00-18:00, and Saturday to Sunday 13:00-17:00.


**–**
may{1-31} : All of May.


**–**
may,september{1-15} : All of May, and only September 1-15.


**–**
may,september{1-15{monday-friday}} : All of May. And only September 1-15 Monday to
Friday.


A BNF grammar for allowed times is given in section 3.2.1 of the _Developer Manual_ .


The following action scripts have some additional options:


 - Send e-mail to administrators : Additional options here are:


**–** Info : body of text inserted into the default e-mail message text, before the line beginning
“ Please take action ”. The default text can be managed in the file /cm/local/apps/cmd/
scripts/actions/sendemail.py


**–**
Recipients : a list of recipients


**–** All administrators : uses the list of users in the Administrator e-mail setting in partition[base]
mode


 - killprocess, and testaction : Additional options for these are:


**–**
Arguments : text that can be used by the script.


**–**
Script : The location of the script on the file system.


**10.4 Monitoring Configuration With Base View** **567**


**10.4.5** **Monitoring Configuration: Triggers**
Triggers are introduced in section 10.2.5. The Triggers window (figure 10.18) allows actions (section 10.2.6) to be triggered based on conditions defined by the cluster administrator.


Figure 10.18: Base View Monitoring Configuration: Triggers


**Change Detection For Triggers**
Triggers launch actions by detecting changes in the data of configured measurables. The detection of
these changes can happen:


  - When a threshold is crossed. That is: the latest sample value means that either the value has
entered a zone when it was not in the zone in the preceding sample, or the latest sample means
that the value has left a zone when it was in the zone in the preceding sample


  - When the zone remains crossed. That is: the latest sample as well as the preceding sample are both
within the zone of a crossed threshold.


  - When state flapping is detected. This is when the threshold is crossed repeatedly (5 times by
default) within a certain time period (5 minutes by default).


The monitoring configuration dialog triggers have four possible action launch configuration options
to cover these cases:


1. Enter actions : if the sample has entered into the zone and the previous sample was not in the
zone. This is a threshold-crossing change.


2. Leave actions : if the sample has left the zone and the previous sample was in the zone. This is
also a threshold-crossing change.


3. During actions : if the sample is in the zone, and the previous sample was also in the zone.


4. State flapping actions : if the sample is entering and leaving the zone within a particular
period ( State flapping period, 5 minutes by default) a set number of times ( State flapping
count, 5 by default).


**Pre-defined Triggers: Passing, Failing, And Unknown Health Checks**
By default, the only triggers that are pre-defined are the following three health check triggers, which use
the Enter actions launch configuration option, and which have the following default behavior:


 - Failing health checks : If a health check fails, then on entering the state of the health check
failing, an event is triggered as the action, and a severity of 15 is set for that health check.


 - Passing health checks : If a health check passes, then on entering the state of the health check
passing, an event is triggered as the action, and a severity of 0 is set for that health check.


**568** **Monitoring: Monitoring Cluster Devices**


 - Unknown health checks : If a health check has an unknown response, then on entering the state of
the health check returning an unknown response, an event is triggered as the action, and a severity
of 10 is set for that health check.


**Example: carry out a triggered action:** cmsh or Base View can be used for the configuration of carrying
out an e-mail alert action (that is: sending out an e-mail) that is triggered by failing health checks.


 - A cmsh way to configure it is:


The e-mail action ( send\ e-mail\ to\ administrators ) is first configured so that the right recipients
get a useful e-mail.


[root@basecm11 ~]# cmsh

[basecm11]% monitoring action

[basecm11->monitoring->action]% use send\ e-mail\ to\ administrators

[basecm11->...[send e-mail to administrators]]% append recipients user1@example.com

[basecm11->...*[send e-mail to administrators*]]% commit


Here, email alerts would go to user1@example.com, as well as to anyone already configured in
administratore-mail . Additional text can be set in the body of the e-mail by setting a value for

info .


The trigger can be configured to run the action when the health check enters a state where its value
is true :


[basecm11->monitoring->action[use send e-mail to administrators]]% monitoring trigger

[basecm11->monitoring->trigger]% use failing\ health\ checks

[basecm11->monitoring->trigger[Failing health checks]]% append enteractions send\ e-mail\ to\ administrators

[basecm11->monitoring->trigger*[Failing health checks*]]% commit


The settings can be viewed with the show command. TAB-completion prompting can be used to
suggest possible values for the settings.


  - A Base View way to carry out the configuration is using the navigation path:


Monitoring   - Actions   - Send e-mail to administrators   - Edit


This can be used to set the recipients and other items, and the configuration can then be saved.


The email action can then be configured in Base View via the navigation path:


Monitoring   - Triggers   - Failing Health Checks   - Edit   - Enter Actions   - Send E-mail to

Administrators


The checkbox for the " Send E-mail to Administrators " action should be ticked and the configuration saved.


**Carrying Out Post-Drain Actions**
A special, and hidden, setting for a triggered drain is post-drain-actions . This allows one or more
actions to be triggered after a node has reached a fully-drained state after a drain action.


**Example**


[basecm11->monitoring]% trigger

[basecm11->monitoring->trigger]% add mydrain

[basecm11->...->trigger*[mydrain*]]% set enteractions drain

[basecm11->...->trigger*[mydrain*]]% set -e -v post-drain-actions send\ e-mail\ to\ administrators poweroff

[basecm11->...->trigger*[mydrain*]]% commit


In the preceding example, nodes that enter a drained state, after they are fully-drained, send an
e-mail to the administrator and are powered off (page 566 and section G.4.1).
The syntax of the post-drain action is:
set -e -v post-drain-actions < _action name_   - [< _action name_   - ...]


**10.4 Monitoring Configuration With Base View** **569**


**Adding Custom Triggers: Any Measurable, Any Action**
More triggers can be added. The killallyestrigger example from the basic example of section 10.1,
seen in figures 10.3 and 10.4, is one such example.
The idea is that actions are launched from triggers, and the action for the trigger can be set to a
predefined action, or to a custom action.


**The Expression Subwindow For A Trigger**
One of the options presented when editing a trigger listed in figure 10.18 is the Expression button.
Clicking on it opens up the expression subwindow. The expression for the trigger can then be configured
by setting the entity, measurable, parameters, (comparison) operator, and measurable value, as shown
in figure 10.19:


Figure 10.19: Base View Monitoring Configuration: Triggers Expression


The trigger launch is carried out when, during sampling, CMDaemon evaluates the expression as
being true.
An example cmsh session to set up an expression for a custom trigger might be as follows, where the


**570** **Monitoring: Monitoring Cluster Devices**


administrator is setting up the configuration so that an e-mail is sent by the monitoring system when a
node is detected as having gone down:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% monitoring trigger add nodedown

[basecm11->monitoring->trigger*[nodedown*]]% expression

[basecm11->monitoring->trigger*[nodedown*]->expression[compare]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Name compare

Revision

Type MonitoringCompareExpression

Entities

Measurables

Parameters

Operator ==

Value FAIL

Use raw no

[basecm11->monitoring->trigger*[nodedown*]->expression*[compare*]]% set value down

[basecm11->monitoring->trigger*[nodedown*]->expression*[compare*]]% set operator eq

[basecm11->monitoring->trigger*[nodedown*]->expression*[compare*]]% set measurables devicestate


To add a touch of realism, a deliberate mistake is set here—the use of devicestate (the data producer) instead of devicestatus (the measurable). The validate command (page 58) gives a helpful
warning here, so that the cluster administrator can fix the setting:


[basecm11->monitoring->trigger*[nodedown*]->expression*[compare*]]% validate

Field Message

---------------- -----------------------------------------------------------------------------
actions Warning: No actions were set
measurables/ Warning: No known measurable matches the specified regexes ('devicestate', '')

parameters

[basecm11->monitoring->trigger*[nodedown*]->expression*[compare*]]% set measurables devicestatus

[basecm11->monitoring->trigger*[nodedown*]->expression*[compare*]]% ..;..

[basecm11->monitoring->trigger*[nodedown*]]% set enteractions send e-mail to administrators

[basecm11->monitoring->trigger*[nodedown*]]% commit


**10.4.6** **Monitoring Configuration: Health status**
The Health status window (figure 10.20) displays all the nodes, and summarizes the results of all the
health checks that have been run against them over time, by presenting a table of the associated severity
levels (section 10.2.7):


Figure 10.20: Base View Monitoring Configuration: Health Status


In the example shown in figure 10.20 the last entity shows a severity issue, while the other devices
are fine. Details of the individual health checks per entity can be viewed in a subwindow using the


**10.4 Monitoring Configuration With Base View** **571**


Show button for that entity. Clicking on the show button for the last entity in this example opens up a
subwindow (figure 10.21). For this example the issue turns out to be due to a FAIL status in the ssh2node
measurable.


Figure 10.21: Base View Monitoring Configuration: Health Status For An Entity


**10.4.7** **Monitoring Configuration: All Health Checks**


Figure 10.22: Base View Monitoring Configuration: All Health Checks For All Entities


The All Health checks window shows all the running health checks for all entities. The Group by
Entity option at the top of the ENTITY column can be used to show the results for per entity only. The
results for one entityare then similar to what the Show button for the entity produces in section 10.4.6,
figure 10.21.


**572** **Monitoring: Monitoring Cluster Devices**


**10.4.8** **Monitoring Configuration: Standalone Monitored Entities**
The Standalone Monitored Entities window allows the cluster administrator to define a standalone
entity. A standalone entity is one that is not managed by BCM—which means that no CMDaemon is
running on it to gather data and for managing it—but the entity can still be monitored. For example, a
workstation that is running the Base View browser could be the standalone entity. This could have its
connectivity monitored by pinging it from the head node with a custom script.


**10.4.9** **Monitoring Configuration: PromQL Queries**
The Prometheus Query list window displays the list of PromQL job-related queries, and allows query
properties to be edited. Drilldowns can also be viewed.


Figure 10.23: Base View Monitoring Configuration: PrompQL Queries


PromQL job queries are discussed further in section 12.3.


**10.4.10** **Monitoring Configuration: Resources**
The Monitoring Resource list window displays a view-only list of resources.


**10.4 Monitoring Configuration With Base View** **573**


Figure 10.24: Base View Monitoring Configuration: Resources


**10.4.11** **Monitoring Configuration: Types**
The Monitoring Types list window displays a view-only list of types.


**574** **Monitoring: Monitoring Cluster Devices**


Figure 10.25: Base View Monitoring Configuration: Types


**10.5** **The** monitoring **Mode Of** cmsh


This section covers how to use cmsh to configure monitoring. The monitoring mode in cmsh corresponds
generally to the Monitoring resource of Base View in section 10.4. Similarly to how monitoring subwindows are accessed in Base View, the monitoring mode of cmsh is itself is not used directly, except as a
way to access the monitoring configuration submodes of cmsh .
For this section some familiarity is assumed with handling of objects as described in the introduction
to working with objects (section 2.5.3). When using cmsh ’s monitoring mode, the properties of objects in
the submodes are how monitoring settings are carried out.
The monitoring mode of cmsh gives access to 9 modes under it:


**Example**


[root@myheadnode ~]# cmsh

[myheadnode]% monitoring help | tail -11

============================== Monitoring ===============================

action ........................ Enter action mode

consolidator .................. Enter consolidator mode

labeledentity ................. Enter labeled entity mode

measurable .................... Enter measurable mode

query.......................... Enter monitoring query mode

report......................... Enter report mode

setup ......................... Enter monitoring configuration setup mode

standalone .................... Enter standalone entity mode

trigger ....................... Enter trigger mode


For convenience, a tree of modes for monitoring submodes is shown in figure 10.26.


(page 589)

















(section 10.5.6) (page 590)


Figure 10.26: Submodes Under monitoring Mode


Sections 10.5.1–10.5.6 give examples of how objects are handled under these monitoring modes. To
avoid repeating similar descriptions, section 10.5.1 is relatively detailed, and is often referred to by the


The action submode under the monitoring mode of cmsh allows monitoring actions to be configured.
This mode in cmsh corresponds to the Base View navigation path:


Monitoring  - Actions


described earlier in section 10.4.4:


The action mode handles action objects in the way described in the introduction to working with
objects (section 2.5.3). A typical reason to handle action objects—the properties associated with an action
script or action built-in—might be to view the actions available, or to add a custom action for use by, for
example, a metric or health check.
Some examples of how the action mode is used are now give.


**The** action **Submode:** list **,** show **, And** get
The list command by default lists the names and properties of actions available from action mode in
a table:


**Example**


[myheadnode]% monitoring action

[myheadnode->monitoring->action]% list
Type Name (key) Run on Action

----------- ---------------- -------- ----------------------------------------------------

**576** **Monitoring: Monitoring Cluster Devices**


Drain Drain Active Drain node from all WLM

Email Send e-mail to Active Send e-mail

administrators

Event Event Active Send an event to users with connected client

ImageUpdate ImageUpdate Active Update the image on the node

PowerOff PowerOff Active Power off a device

PowerOn PowerOn Active Power on a device

PowerReset PowerReset Active Power reset a device

Reboot Reboot Node Reboot a node

Script killprocess Node /cm/local/apps/cmd/scripts/actions/killprocess.pl
Script remount Node /cm/local/apps/cmd/scripts/actions/remount
Script testaction Node /cm/local/apps/cmd/scripts/actions/testaction

Shutdown Shutdown Node Shutdown a node

Undrain Undrain Active Undrain node from all WLM (node accepts new WLM jobs)


The preceding shows the actions available on a newly installed system.
The show command of cmsh displays the individual parameters and values of a specified action:


**Example**


[myheadnode->monitoring->action]% show poweroff

Parameter Value

-------------------------------- ---------------------------
Action Power off a device

Allowed time

Disable no

Name PowerOff

Revision

Run on Active

Type PowerOff


Instead of using list, a convenient way to view the possible actions is to use the show command
with tab-completion suggestions:


**Example**


[myheadnode->monitoring->action]% show _<TAB><TAB>_
drain killprocess powerreset send _\_ e-mail _\_ to _\_ administrators undrain

event poweroff reboot shutdown

imageupdate poweron remount testaction


The get command returns the value of an individual parameter of the action object:


**Example**


[myheadnode->monitoring->action]% get poweroff runon

active


**The** action **Submode:** add **,** use **,** remove **,** commit **,** refresh **,** modified **,** set **,** clear **, And** validate
In the basic example of section 10.1, in section 10.1.2, the killallyes action was cloned from a similar
script using a clone option in Base View.
The equivalent can be done with a clone command in cmsh . However, using the add command
instead, while it requires more steps, makes it clearer what is going on. This section therefore covers
adding the killallyes script of section 10.1.2 using the add command.
When add is used: an object is added, the object is made the current object, and the name of the object
is set, all at the same time. After that, set can be used to set values for the parameters within the object,
such as a path for the value of the parameter command .


**10.5 The** monitoring **Mode Of** cmsh **577**


Adding an action requires that the type of action be defined. Just as tab-completion with show comes
up with action suggestions, in the same way, using tab-completion with add comes up with type suggestions.
Running the command help add in the action mode also lists the possible types. These types are
drain, e-mail, event, imageupdate, poweroff, poweron, powerreset, reboot, script, servicerestart,

servicestart, servicestop, shutdown, undrain .
The syntax for the add command takes the form:


add < _type_ - < _action_ 

If there is no killallyes action already, then the name is added in the action mode with the
add command, and the script type, as follows:


**Example**


[myheadnode->monitoring->action]% add script killallyes

[myheadnode->monitoring->action*[killallyes*]]%


Using the add command drops the administrator into the killallyes object level, where its properties can be set. A successful commit means that the action is stored in CMDaemon.

The converse to the add command is the remove command, which removes an action that has had
the commit command successfully run on it.
The refresh command can be run from outside the object level, and it removes the action if it has
not yet been committed.
The use command is the usual way of "using" an object, where "using" means that the object being
used is referred to by default by any command run. So if the killallyes object already exists, then use
killallyes drops into the context of an already existing object (i.e. it “uses” the object).
The set command sets the value of each individual parameter displayed by a show command for
that action. The individual parameter script can thus be set to the path of the killallyes script:


**Example**


[...oring->action*[killallyes*]]% set script /cm/local/apps/cmd/scripts/actions/killallyes


The clear command can be used to clear the value that has been set for script .
The validate command checks if the object has all required values set to sensible values. So, for
example, commit only succeeds if the killallyes object passes validation.
Validation does not check if the script itself exists. It only does a sanity check on the values of the
parameters of the object, which is another matter. If the killallyes script does not yet exist in the
location given by the parameter, it can be created as suggested in the basic example of section 10.1, in
section 10.1.2. In the basic example used in this chapter, the script is run only on the head node. If it
were to run on regular nodes, then the script should be copied into the disk image.
The modified command lists changes that have not yet been committed.


**10.5.2** **The** consolidator **Submode**

Consolidators are introduced in section 10.4.3. Consolidators can be managed in cmsh via the
consolidator mode, which is the equivalent of the consolidators window (section 10.4.3) in Base View.
The consolidator mode deals with groups of consolidators . One such pre-defined group is
default, while the other is none, as discussed earlier in section 10.4.3:


[basecm11->monitoring->consolidator]% list
Name (key) Consolidators

------------------------ -----------------------
default hour, day, week

none <0 in submode>


**578** **Monitoring: Monitoring Cluster Devices**


Each consolidators entry can have its parameters accessed and adjusted.
For example, the parameters can be viewed with:


**Example**


[basecm11->monitoring->consolidator]% use default

[basecm11->monitoring->consolidator[default]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Consolidators hour, day, week

Name default

Revision

[basecm11->monitoring->consolidator[default]]% consolidators

[basecm11->monitoring->consolidator[default]->consolidators]% list
Name (key) Interval

------------------------ -----------------------
day 1d

hour 1h

week 1w

[basecm11->monitoring->consolidator[default]->consolidators]% use day

[basecm11->monitoring->consolidator[default]->consolidators[day]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Interval 1d

Kind AVERAGE

Maximal age 0s

Maximal samples 4096

Name day

Offset 0s

Revision

[basecm11->monitoring->consolidator[default]->consolidators[day]]%


For the day consolidator shown in the preceding example, the number of samples saved per day can be
doubled with:


**Example**


[basecm11->monitoring->consolidator[default]->consolidators[day]]% set maximalsamples 8192

[basecm11->monitoring->consolidator*[default*]->consolidators*[day*]]% commit


Previously consolidated data is discarded with this type of change, if the number of samples is reduced. Changing parameters should therefore be done with some care.
A new consolidators group can be created if needed.
A Base View way, where a decimalminutes group is created, is discussed in the example in section 10.4.3, page 562.
A cmsh way, where a max-per-day group is created, is discussed in the following section:


**Creation Of A Consolidator In** cmsh

A new consolidator group, max-per-day, can be added to the default consolidator groups of default
and none, with:


**Example**


[basecm11]% monitoring consolidator

[basecm11->monitoring->consolidator]% add max-per-day

[...[max-per-day*]]%


**10.5 The** monitoring **Mode Of** cmsh **579**


Within this new group, a new consolidator item, max-per-day can also be defined. The item can be
defined so that it only calculates the maximum value per day, using the kind setting. Another setting is
interval, which defines the interval with which the old data is compressed:


**Example**


[...[max-per-day*]]% consolidators

[...[max-per-day*]->consolidators]% add max-per-day

[...[max-per-day*]]% set interval 1d

[...[max-per-day*]]% set kind maximum

[...[max-per-day*]]% show

Parameter Value

------------------- ----------
Interval 1d

Kind maximum

Maximal age 0s

Maximal samples 4096

Name max-per-day

Offset 0s

Revision

[...[max-per-day*]]% commit


**10.5.3** **The** measurable **Submode**

The measurable submode under the monitoring mode of cmsh handles measurable objects, that is:
metrics, health checks, and enummetrics. This mode corresponds to the Base View navigation path:


Monitoring  - Measurables


covered earlier in section 10.4.2.

Measurable objects represent the configuration of scripts or built-ins. The properties of the objects
are handled in cmsh in the way described in the introduction to working with objects (section 2.5.3).
A typical reason to handle measurable objects might be to view the measurables already available,
or to remove a measurable that is in use by an entity.
Measurables cannot be added from this mode. To add a measurable, its associated data producer
must be added from monitoring setup mode (section 10.5.4).
This section goes through a cmsh session giving some examples of how this mode is used.


**The** measurable **Submode:** list **,** show **, And** get
In measurable mode, the list command by default lists the names of all measurable objects along with
parameters, their class, and data producer.


**Example**


[basecm11->monitoring->measurable]% list
type name (key) parameter class producer

------------- -------------------- ---------- ----------------------------- ----------------
Enum DeviceStatus Internal DeviceState

HealthCheck ManagedServicesOk Internal CMDaemonState
HealthCheck Mon::Storage Internal/Monitoring/Storage MonitoringSystem

Metric nfs_v3_server_total Disk NFS

Metric nfs_v3_server_write Disk NFS

...


The above example illustrates a list with some of the measurables that can be set for sampling on a
newly installed system. A full list typically contains over two hundred items.
The list command in measurable submode can be run as:


**580** **Monitoring: Monitoring Cluster Devices**


 - list metric : to display only metrics


 - list healthcheck : to display only health checks


 - list enum : to display only enummetrics


The show command of the measurable submode of monitoring mode displays the parameters and
values of a specified measurable, such as, for example CPUUser, devicestatus, or diskspace :


**Example**


**Example**


[myheadnode->monitoring->measurable]% show cpuuser

Parameter Value

-------------------- ---------------------------
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

[myheadnode->monitoring->measurable]% show devicestatus

Parameter Value

-------------------- ---------------------------
Class Internal

Consolidator none

Description The device status

Disabled no (DeviceState)

Gap 0 (DeviceState)
Maximal age 0s (DeviceState)
Maximal samples 4,096 (DeviceState)

Name DeviceStatus

Parameter

Producer DeviceState

Revision

Type Enum

[myheadnode->monitoring->measurable]% show diskspace

Parameter Value

-------------------- ---------------------------
Class Disk

Consolidator - (diskspace)

Description checks free disk space
Disabled no (diskspace)
Gap 0 (diskspace)
Maximal age 0s (diskspace)
Maximal samples 4,096 (diskspace)


**10.5 The** monitoring **Mode Of** cmsh **581**


Name diskspace

Parameter

Producer diskspace

Revision

Type HealthCheck


The Gap setting here is a number. It sets how many samples are allowed to be missed before a value
of NaN is set for the value of the metric.

As detailed in section 10.5.1, tab-completion suggestions for the show command suggest the names
of objects that can be used, with the use command in this mode. For show in measurable mode, tabcompletion suggestions suggests over 200 possible objects:


**Example**


[basecm11->monitoring->measurable]% show
Display all 221 possibilities? (y or n)

alertlevel:count iotime:vda mon::storage::engine::elements oomkiller

alertlevel:maximum iotime:vdb mon::storage::engine::size opalinkhealth

alertlevel:sum ipforwdatagrams mon::storage::engine::usage packetsrecv:eth0

blockedprocesses ipfragcreates mon::storage::message::elements packetsrecv:eth1

buffermemory ipfragfails mon::storage::message::size packetssent:eth0

bytesrecv:eth0 ipfragoks mon::storage::message::usage packetssent:eth1

...


The single colon (“ : ”) indicates an extra parameter for that measurable.
Because there are a large number of metrics, it means that grepping a metrics list is sometimes handy.
When listing and grepping, it is usually a good idea to allow for case, and be aware of the existence of
the parameter column. For example, the AlertLevel metric shown in the first lines of the tab-completion
suggestions of the show command of the previous example, shows up as alertlevel . However the list
command displays it as AlertLevel . There are also several parameters associated with the AlertLevel
command. So using the case-insensitive -i option of grep, and using the head command to display the
headers is handy:


**Example**


[basecm11->monitoring->measurable]% list | head -2 ; list metric | grep -i alertlevel
type name (key) parameter class producer

------------- -------------------- ---------- ------------------- --------------
Metric AlertLevel count Internal AlertLevel

Metric AlertLevel maximum Internal AlertLevel

Metric AlertLevel sum Internal AlertLevel


The get command returns the value of an individual parameter of a particular health check object:


**Example**


[myheadnode->monitoring->measurable]% get oomkiller description

Checks whether oomkiller has come into action (then this check returns FAIL)

[myheadnode->monitoring->measurable]%


**The** measurable **Submode: The** has **Command**

The has command is used with a measurable to list the entities that use the measurable. Typically these
are nodes, but it can also be other entities, such as the base partition.


**Example**


**582** **Monitoring: Monitoring Cluster Devices**


[basecm11->monitoring->measurable]% has alertlevel:sum

basecm11

node001

node002

[basecm11->monitoring->measurable]% use devicesup

[basecm11->monitoring->measurable[DevicesUp]]% has

base


The remaining commands in measurable mode, such as use, remove, commit, refresh, modified,
set, clear, and validate ; all work as outlined in the introduction to working with objects (section 2.5.3).
More detailed usage examples of these commands within a monitoring mode are given in the earlier
section covering the action submode (section 10.5.1).


**The** measurable **Submode: An Example Session On Viewing And Configuring A Measurable**
A typical reason to look at metrics and health check objects—the properties associated with the script or
built-in—might be, for example, to view the operating sampling configuration for an entity.
This section goes through a cmsh example session under monitoring mode, where the setup submode (page 583) is used to set up a health check. The healthcheck can then be viewed from the
measurable submode.

In the basic example of section 10.1, a trigger was set up from Base View to check if the CPUUser
metric was above 50 jiffies/s, and if so, to launch an action.
A functionally equivalent task can be set up by creating and configuring a health check, because
metrics and health checks are so similar in concept. This is done here to illustrate how cmsh can be used
to do something similar to what was done with Base View in the basic example. A start is made on
the task by creating a health check data producer, and configuring its measurable properties. using the
setup mode under the monitoring mode of cmsh . The task is completed in the section on the setup
mode in section 10.5.4.

To start the task, cmsh ’s add command is used, and the type is specified, to create the new object:


**Example**


[root@myheadnode ~]# cmsh

[myheadnode]% monitoring setup

[myheadnode->monitoring->setup]% add healthcheck cpucheck

[myheadnode->monitoring->setup*[cpucheck*]]%


The show command shows the parameters.
The values for description, runinbash, script, and class should be set:


**Example**


[...->setup*[cpucheck*]]% set script /cm/local/apps/cmd/scripts/healthchecks/cpucheck

[...->setup*[cpucheck*]]% set description "CPUuser under 50%?"

[...->setup*[cpucheck*]]% set runinbash yes

[...->setup*[cpucheck*]]% set class OS

[...->setup*[cpucheck*]]% commit

[myheadnode->monitoring->setup[cpucheck]]%


On running commit, the data producer cpucheck is created:


**Example**


[myheadnode->monitoring->setup[cpucheck]]% exit; exit

[myheadnode->monitoring]% setup list | grep -i cpucheck
HealthCheckScript cpucheck 1 / 222 <0 in submode>


**10.5 The** monitoring **Mode Of** cmsh **583**


The measurable submode shows that a measurable cpucheck is also created:


**Example**


[myheadnode->monitoring]% measurable list | grep -i cpucheck

HealthCheck cpucheck OS cpucheck


Since the cpucheck script does not yet exist in the location given by the parameter script, it needs
to be created. One ugly bash script that can do a health check is:


#!/bin/bash