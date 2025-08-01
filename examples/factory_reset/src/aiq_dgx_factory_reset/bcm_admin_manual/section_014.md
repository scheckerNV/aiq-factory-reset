## echo PASS if CPUUser < 50

## cpu is a %, ie: between 0 and 100


cpu=`mpstat 1 1 | tail -1 | awk '{print $3}'`
comparisonstring="$cpu"" < 50"


if (( $(bc <<< "$comparisonstring") )); then

echo PASS

else

echo FAIL

fi


The script should be placed in the location suggested by the object, /cm/local/apps/cmd/scripts/
healthchecks/cpucheck, and made executable with a chmod 700 .
The cpucheck object is handled further within the cmsh monitoring setup mode in section 10.5.4 to
produce a fully configured health check.


**10.5.4** **The** setup **Submode**

**The** setup **Submode: Introduction**
The setup submode under the monitoring mode of cmsh allows access to all the data producers. This
mode in cmsh corresponds to the Base View navigation path:


Monitoring  - Data Producers


covered earlier in section 10.4.1.


**The** setup **Submode: Data Producers And Their Associated Measurables**
The list of data producers in setup mode should not be confused with the list of measurables in
measurable mode. Data producers are not the same as measurables. Data producers produce measurables, although it is true that the measurables are often named the same as, or similar to, their data
producer.
In cmsh, data producers are in the Name (key) column when the list command is run from the
setup submode:


**Example**


[basecm11->monitoring->setup]% list
Type Name (key) Arguments Measurables Node execution filters

-------------- --------------- ----------- ------------ ----------------------
AggregateNode AggregateNode 8 / 222 <1 in submode>

AlertLevel AlertLevel 3 / 222 <1 in submode>

CMDaemonState CMDaemonState 1 / 222 <0 in submode>

ClusterTotal ClusterTotal 18 / 222 <1 in submode>

Collection BigDataTools 0 / 222 <2 in submode>


**584** **Monitoring: Monitoring Cluster Devices**


Collection Cassandra 0 / 222 <1 in submode>

...


In the preceding example, the AlertLevel data producer has 3 / 222 as the value for measurables.
This means that this AlertLevel data producer provides 3 measurables out of the 222 configured measurables. They may be enabled or disabled, depending on whether the data producer is enabled or
disabled, but they are provided in any case.
To clarify this point: if the list command is run from setup mode to list producers, then the producers that have configured measurables are the ones that have 1 or more as the numerator value in the
Measurables column. Conversely, the data producers with 0 in the numerator of the Measurables column have no configured measurables, whether enabled or disabled, and are effectively just placeholders
until the software for the data producers is installed.
So, comparing the list of producers in setup mode with the measurables in measurable mode:


**Example**


In measurable mode, the three AlertLevel measurables (the 3 out of 222) produced by the AlertLevel
producer can be seen with:


[basecm11->monitoring->measurable]% list | head -2; list | grep AlertLevel
Type Name (key) Parameter Class Producer

-------- ------------ --------- --------- ------------
Metric AlertLevel count Internal AlertLevel

Metric AlertLevel maximum Internal AlertLevel

Metric AlertLevel sum Internal AlertLevel


On the other hand, in measurable mode, there are no measurables seen for BigDataTools (the 0 out
of 222) produced by the BigDataTools producer, when running, for example: list | head -2; list
| grep BigDataTools .


**The** setup **Submode: Listing Nodes That Use A Data Producer**
The nodes command can be used to list the nodes on which a data producer < _data producer_ - runs. It is
run in the setup submode level of the monitoring mode as:


nodes < _data producer_  

**Example**


[basecm11->monitoring->setup]% list | head -2; list | grep mount
Type Name (key) Arguments Measurables Node execution filters

---------------------- -------------- ------------ ------------ ---------------------
HealthCheckScript mounts 1 / 229 <0 in submode>

[basecm11->monitoring->setup]% nodes mounts

node001..node003,basecm11


**The** setup **Submode: Data Producers Properties**
Any data producer from the full list in setup mode can, if suitable, be used to provide a measurable for
any entity.
An example is the data producer AlertLevel . Its properties can be seen using the show command:


**Example**


[basecm11->monitoring->setup]% show alertlevel

Parameter Value

-------------------------------- -------------------------------------------------
Automatic reinitialize yes


**10.5 The** monitoring **Mode Of** cmsh **585**


Consolidator default

Description Alert level as function of all trigger severities

Disabled no

Execution multiplexer <1 in submode>

Fuzzy offset 0

Gap 0

Interval 2m

Maximal age 0s

Maximal samples 4096

Measurables 3 / 222

Name AlertLevel

Node execution filters <1 in submode>

Notes <0 bytes>

Offset 1m

Only when idle no

Revision

Type AlertLevel

When Timed


These properties are described in section 10.4.1. Most of these properties are inherited by the
meaurables associated with the data producer, which in the AlertLevel data producer case are
alertlevel:count, alertlevel:maximum, and alertlevel:sum .


**The** setup **Submode: Deeper Submodes**
One level under the setup submode of monitoring mode are 3 further submodes (modes deeper than
submodes are normally also just called submodes for convenience, rather than sub-submodes):


 - nodeexecutionfilters


 - executionmultiplexers


 - jobmetricsettings


**Node execution filters:** A way to filter execution (restrict execution) of the data producer.
If no node execution filter is set for that data producer, then the data producer runs on all nodes of
the cluster. Filters are of type node, category, overlay, resource, and lua . The type is set when the
filter is created.


 - **The** nodes **command for listing the execution nodes**


Running the nodes command for a data producer lists which nodes the execution of the data
producer is run on.


**Example**


[myhost->monitoring->setup]% nodes procmeminfo

mon001..mon003,myhost,osd001,osd002,node001,node002

[myhost->monitoring->setup]% nodes ssh2node

myhost

[myhost->monitoring->setup]% nodes devicestate

myhost

[myhost->monitoring->setup]% foreach * ( get name; nodes) | paste - - | sort

AggregateCDU myhost

AggregateNode myhost

AggregatePDU myhost
...[so far the data producers run only on the head node, but eventually see other nodes]...


**586** **Monitoring: Monitoring Cluster Devices**


CMDaemonState node001..node006,myhost

cmha-status Not used

cmsh myhost

CPUSampler node001..node006,myhost

cuda-dcgm node001..node006,myhost

...


Most of the default data producers that are used by the cluster run on an active head node, and
often on the regular nodes.


 - nodexecutionfilters **to restrict data producer execution**


The rogueprocess (page 975) data producer is one of the few that by default runs on a regular
node. Restricting a data producer to run on a particular list of nodes can be carried out as follows
on a cluster that is originally in its default state:


**Example**


[basecm11->monitoring->setup[rogueprocess]]% nodeexecutionfilters

[basecm11->monitoring->setup[rogueprocess]->nodeexecutionfilters]% add _<TAB><TAB>_

category lua node overlay resource type

[...tup[rogueprocess]->nodeexecutionfilters]% add node justthese

[...tup*[rogueprocess*]->nodeexecutionfilters*[justthese*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Filter operation Include

Name justhese

Nodes

Revision

Type Node

[...tup*[rogueprocess*]->nodeexecutionfilters*[justthese*]]% set nodes node001,node002

[...tup*[rogueprocess*]->nodeexecutionfilters*[justthese*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Filter operation Include

Name justhese

Nodes node001,node002

Revision

Type Node

[...tup*[rogueprocess*]->nodeexecutionfilters*[justthese*]]% commit


This way, the rogueprocess health check runs on just those nodes ( node001, node002 ), and none
of the others.


 - **Restricting a data producer execution to the head node—monitoring a process on the head node**


Another example of data producer restriction is as follows: an administrator may wish to monitor
the slapd process on the head nodes. In cmsh, a session to achieve this could be:


**Example**


[basecm11->monitoring->setup]% add procpidstat slapd

[basecm11->monitoring->setup*[slapd*]]% set process slapd

[basecm11->monitoring->setup*[slapd*]]% set consolidator none

[basecm11->monitoring->setup*[slapd*]]% nodeexecutionfilters


**10.5 The** monitoring **Mode Of** cmsh **587**


[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters]% add type headnodes

[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters*[headnodes*]]% set headnode yes

[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters*[headnodes*]]% commit


An equivalent to the preceding, starting from the nodeexecutionfilters mode, but using a different name for the type, is:


[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters]% add type headnode

[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters*[headnode*]]% commit


The value for headnode attribute within the headnode object is automatically matched to its name,
and so its value is automatically set to yes just as in the earlier session.


The preceding sessions set the filter to work on all head nodes. To have it work on only the active
head node, the active command can be used instead, at nodeexecutionfilter mode level:


[basecm11->monitoring->setup*[slapd*]]% nodeexecutionfilters

[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters]% active

[basecm11->monitoring->setup*[slapd*]->nodeexecutionfilters*]% commit


The newly-defined slapd metric can now have its output displayed or plotted just like any other
metric:


[basecm11->device[basecm11]]% latestmetricdata | grep slapd

MemoryUsed slapd Process 739 MiB 28.6s

SystemTime slapd Process 2m 35s 28.6s

ThreadsUsed slapd Process 50 28.6s

UserTime slapd Process 1h 36m 28.6s

VirtualMemoryUsed slapd Process 4.77 GiB 28.6s


 - **Filtering a data producer by resource**


A data producer can also be set up so that it is run on a particular list of nodes filtered
by resource. The resources that are available to a node can be viewed using the command
monitoringresources for that device:


**Example**


[basecm11->device[basecm11]]% monitoringresources

Active

Docker::Host

Ethernet

Kubernetes::ApiServer

Kubernetes::ApiServerProxy

Kubernetes::Controller

kubelet

kubernetes-control-plane

overlay:kube-default-etcd

overlay:kube-default-master

RDO

boot

...


An example of where running a node execution filter by resource is useful, is for data producers
that are intended to run on the active head node. Most data producers that are used by the cluster
run on an active head node (besides often running on the regular nodes too).


Thus, for example, the cpucheck health check from page 582 can be set to run on the active head
node, by creating an arbitrary resource called myactive :


**588** **Monitoring: Monitoring Cluster Devices**


**Example**


[basecm11->monitoring->setup[cpucheck]]% nodeexecutionfilters

[...tup[cpucheck]->nodeexecutionfilters]% add resource "myactive"

[...tup*[cpucheck*]->nodeexecutionfilters*[myactive*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Filter Include

Name myactive

Operator OR

Resources

Revision

Type Resource


and then setting the Resources parameter to Active :


[...tup*[cpucheck*]->nodeexecutionfilters*[myactive*]]% set resources Active

[...tup*[cpucheck*]->nodeexecutionfilters*[myactive*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Filter Include

Name myactive

Operator OR

Resources Active

Revision

Type Resource

[...tup*[cpucheck*]->nodeexecutionfilters*[myactive*]]% commit


The cpucheck health check then runs on the active head node, whichever head node it is.


When node execution filtering is carried out, the filtered data is not dropped by default. Filtered
data can be dropped for a measurable or an entity with the monitoringdrop command (section 10.6.7).


**Execution multiplexer:** A way to multiplex execution (have execution work elsewhere) for a data producer. It tells BCM about the entities that the data producer is sampling for. A data producer runs and
gathers data at the entity (node, category, lua, overlay, resource type) defined by the node execution
filter, and with multiplex execution the data producer gathers samples from other entities. These entities can be nodes, categories, lua scripts, overlays, resources, and types. The entities from which it
can sample are defined into groups called execution multiplexers. Execution multiplexers can thus be
node multiplexers, category multiplexers, lua multiplexers, type multiplexers, overlay multiplexers,
or resource multiplexers.
The executionmultiplexers mode can be entered for a data producer dmesg with:


**Example**


root@basecm11 ~]# cmsh

[basecm11]% monitoring setup executionmultiplexers dmesg


Running the commands: help add, or help set, can be used to show the valid syntax in this submode.
Most data producers run on a head node, but sample from the regular nodes. So, for example, the
dmesg health check from Appendix G.2.1 can be set to sample from the regular nodes by setting it to
carry out execution multiplexing to specified node entities using a node multiplexer with the arbitrary
name of nodes as follows:


**Example**


**10.5 The** monitoring **Mode Of** cmsh **589**


[basecm11->monitoring->setup[dmesg]->executionmultiplexers]% add _<TAB><TAB>_

category lua node overlay resource type

[basecm11->monitoring->setup[dmesg]->executionmultiplexers]% add node nodes

[basecm11->...*[dmesg*]->executionmultiplexers*[nodes*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Filter operation Include

Name nodes

Nodes

Revision

Type Node


[basecm11->...*[dmesg*]->executionmultiplexers*[nodes*]]% set nodes node001,node002

[basecm11->...*[dmesg*]->executionmultiplexers*[nodes*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Filter operation Include

Name nodes

Nodes node001,node002

Revision

Type Node


The concepts and expected behavior of node execution filters and execution multiplexers is covered
in more explicit detail in Appendix L.


**Job Metrics Settings:** Job metrics settings are a submode for setting job metric collection options for
the JobSampler data producer (section 11.4).


**10.5.5** **The** standalone **Submode**

The standalone submode under the monitoring mode of cmsh allows entities that are not managed by
BCM to be configured for monitoring. This mode in cmsh corresponds to the Base View navigation path:


Monitoring  - Standalone Monitored Entities


covered earlier in section 10.4.8.

The monitoring for such entities has to avoid relying on a CMDaemon that is running on the entity.
An example might be a chassis that is monitored via a ping script running on the BCM head node.


**10.5.6** **The** trigger **Submode**
The trigger submode under the monitoring mode of cmsh allows actions to be configured according
to the result of a measurable.

This mode in cmsh corresponds to the Base View navigation path:


Monitoring  - Triggers


covered earlier in section 10.4.5.

By default, there are 3 triggers:


**Example**


[basecm11->monitoring->trigger]% list
Name (key) Expression Enter actions During actions Leave actions

------------------------ ------------------------ ------------- -------------- ------------
Failing health checks (*, *, *) == FAIL Event


**590** **Monitoring: Monitoring Cluster Devices**


Passing health checks (*, *, *) == PASS Event
Unknown health checks (*, *, *) == UNKNOWN Event


Thus, for a passing, failing, or unknown health check, an event action takes place if entering a state
change. The default severity level of a passing health check does not affect the AlertLevel value. However, if the failing or unknown health checks are triggered on entering a state change, then these will
affect the AlertLevel value.


**The** trigger **Submode: Setting An Expression**
In the basic example of section 10.1, a trigger to run the killallyes script was configured using Base
View.

The expression that was set for the killallyes script in the basic example using Base View can also
be set in cmsh . For example:


**Example**


[basecm11->monitoring->trigger]% add killallyestrigger

[basecm11->monitoring->trigger*[killallyestrigger*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Disabled no

During actions

Enter actions

Leave actions

Mark entity as failed yes

Mark entity as unknown no

Name killallyestrigger

Revision

Severity 10

State flapping actions

State flapping count 5

State flapping period 5m
expression (*, *, *) == FAIL

[basecm11->monitoring->trigger*[killallyestrigger*]]% expression

[basecm11->monitoring->trigger*[killallyestrigger*]->expression[]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Entities

Measurables

Name

Operator EQ

Parameters

Revision

Type MonitoringCompareExpression

Use raw no

Value FAIL

[basecm11->monitoring->trigger*[killallyestrigger*]->expression[]]% set entities basecm11

[basecm11->monitoring->trigger*[killallyestrigger*]->expression*[*]]% set measurables CPUUser

[basecm11->monitoring->trigger*[killallyestrigger*]->expression*[*]]% set operator GT

[basecm11->monitoring->trigger*[killallyestrigger*]->expression*[*]]% set value 50

[basecm11->monitoring->trigger*[killallyestrigger*]->expression*[*]]% commit

[basecm11->monitoring->trigger*[killallyestrigger*]->expression*[*]]% set name killallyesexp

Field Message

------------------------ ------------------------------------------------------
actions Warning: No actions were set

============================== killallyestrigger ===============================


**10.5 The** monitoring **Mode Of** cmsh **591**


[basecm11->monitoring->trigger[killallyestrigger]->expression[killallyesexp]]% exit

[basecm11->monitoring->trigger[killallyestrigger]->expression]% exit

[basecm11->monitoring->trigger[killallyestrigger]]% set enteractions killallyesname

[basecm11->monitoring->trigger*[killallyestrigger*]]% commit

[basecm11->monitoring->trigger[killallyestrigger]]%


The expression format is shown in cmsh as:


(< _entity_ >, < _measurable_ >, < _parameter_ >) < _comparison operator_     - < _value_     

Here:


  - an entity, as described in section 10.2.1, can be, for example, a node, category, device, or software
image. To include more than one entity for the comparison, the alternation (pipe, |) symbol can
be used, with double quotes to enclose the expression.


**Example**


...[killallyestrigger*]->expression[]]% set entities "basecm11|node001|compute|gpuimage"


In the preceding example, the entity compute could be a category, and the entity gpuimage could
be a software image.


  - a measurable (section 10.2.1) can be a health check, a metric, or an enummetric. For example:
CPUUsage . Alternation works for < _measurable_   - in a similar way to that for < _entity_   - .


  - a parameter is a further option to a measurable. For example, the FreeSpace metric can take a
mount point as a parameter. Alternation works for < _parameter_    - in a similar way to that for < _entity_    - .


  - the comparison operator can be:


EQ : equivalent to, displayed as ==


NE : not equivalent to, displayed as !=


GT : greater than, displayed as     

LT : less than, displayed as <


If the user uses an arithmetic symbol such as    - in cmsh as an unescaped entry, then the entry may
unintentionally be interpreted by the shell. That is why the two-letter entries are recommended
instead for entry, even though when displayed they display like the arithmetic symbols for easier
recognition.


  - the value can be a string, or a number.


The regex evaluates to TRUE or FALSE . The trigger runs its associated action in the case of TRUE .
The wildcard  - implies any entity, measurable, or parameter when used with the appropriate position according to the syntax of the expression format.
Using .* is also possible to match zero or more of any characters.
Some further expression matching examples:


**Example**


True for any failing health check:


(*, *, *) == FAIL


**Example**


**592** **Monitoring: Monitoring Cluster Devices**


True for any nearly full local disk (less than 10MB left):


(*, FreeSpace, sd[a-z]) < 10MB


**Example**


True for any cloud node that is too expensive (price more than more than 10$):


(.*cnode.*, Price, *) > 10$


**Example**


Excluding node agw001 :


(^(?!.*agw001).*$, *, *) == FAIL


**Example**


True for any node in the data, gpu, or hpc categories, that has a nearly full local disk (less than 10MB
left):


(!resource=category:data|category:gpu|category:hpc, FreeSpace, sd[a-z]) < 10MB


The unusual syntax in the preceding example is liable to change in future versions.


At the end of section 10.5.3 a script called cpucheck was built. This script was part of a task to use
health checks instead of metrics to set up the functional equivalent of the behavior of the basic example
of section 10.1. In this section the task is continued and completed as follows:


[basecm11->monitoring->trigger]% expression killallyestrigger

[...trigger[killallyestrigger]->expression[killallyesexp]]% get measurables

CPUUser

[...trigger[killallyestrigger]->expression[killallyesexp]]% set measurables cpucheck

[...trigger*[killallyestrigger*]->expression*[killallyesexp*]]% commit


**10.6** **Obtaining Monitoring Data Values**


The monitoring data values that are logged by devices can be used to generate graphs using the methods
in section 10.3. However, sometimes an administrator would like to have the data values that generate
the graphs instead, perhaps to import them into a spreadsheet for further direct manipulation, or to pipe
them into a utility such as gnuplot .


**10.6.1** **Getting The List Of Measurables For An Entity: The** measurables **,** metrics **,**
healthchecks **And** enummetrics **Commands**

The measurables for a specified entity can be seen with the measurables command, and the measurable
subtypes can be seen with the corresponding measurable subset commands: metrics, healthchecks
and enummetrics . The results look quite similar to the results of the measurable submode of the
monitoring mode (section 10.5.3). However, for entities, the measurables are a sublist of the full number
of measurables listed in the measurable submode, which in turn are only the list of measurables for the
data producers that have been enabled.
For example, within device mode where the entities are typically the head node and regular nodes,
running metrics with a specified entity shows only the metrics that are configured for that entity. Thus
if the entity is a head node, then only head node metrics are shown; and if the entity is a regular node,
only regular node metrics are shown:


**Example**


**10.6 Obtaining Monitoring Data Values** **593**


[basecm11->device]% enummetrics node001

Type Name Parameter Class Producer

------------ ------------------ ---------- ---------------------------- ---------------
Enum DeviceStatus Internal DeviceState

[basecm11->device]% use basecm11

[basecm11->device[basecm11]]% measurables

Type Name Parameter Class Producer

------------ ------------------ ---------- ---------------------------- ---------------
Enum DeviceStatus Internal DeviceState

HealthCheck ManagedServicesOk Internal CMDaemonState
HealthCheck Mon::Storage Internal/Monitoring/Storage MonitoringSystem

...

[basecm11->device[basecm11]]% exit

[basecm11->device]% metrics node001

Type Name Parameter Class Producer

------------ ------------------ ---------- ---------------------------- ---------------
Metric AlertLevel count Internal AlertLevel

Metric AlertLevel maximum Internal AlertLevel

Metric AlertLevel sum Internal AlertLevel

Metric BlockedProcesses OS ProcStat

...


Typically the number of metrics listed on the head node will differ from those listed on a regular
node. Whatever each number is, it cannot be more than the number of metrics seen in the number of

metrics listed in the measurable submode of section 10.5.3.

The preceding example shows the measurables listing commands being carried out on head nodes
and regular nodes. These commands can be used on other entities too. For example, the base partition
in partition mode, where the measurables can be listed with:


**Example**


[basecm11->device]% partition use base

[basecm11->partition[base]]% measurables

Type Name Parameter Class Producer

------------ ------------------ ---------- ---------------------------- ---------------
Metric CoresTotal Total ClusterTotal

Metric CoresUp Total ClusterTotal

Metric DevicesClosed Total ClusterTotal

Metric DevicesDown Total ClusterTotal

...


The values for metric samples and health checks can be obtained from within device mode in various
ways, and are explained next.


**10.6.2** **On-Demand Metric Sampling And Health Checks**

**The** samplenow **Command For On-Demand Measurable Samples**
An administrator can do live sampling, or sampling on-demand, for specified entities by using the
samplenow command. The command has the following syntax:


samplenow [ _OPTIONS_ ] [< _entity_ >] [< _measurable_ - ...]


The command can be run without options when an entity object, such as a node is used (output
truncated):


**Example**


**594** **Monitoring: Monitoring Cluster Devices**


[basecm11->device]% use basecm11

[basecm11->device[basecm11]]% samplenow

Measurable Parameter Type Value Age Info

------------------ --------- --------- ------------ ------- ----
AlertLevel count Internal 0 2.01s

AlertLevel maximum Internal 0 2.01s

AlertLevel sum Internal 0 2.01s

BlockedProcesses OS 0 processes 2.01s

BufferMemory Memory 847 KiB 2.01s

...


The entity used can also be in other modes that have measurables, such as the base partition (output
truncated):


**Example**


[basecm11->device]% partition use base

[basecm11->partition[base]]% samplenow

Measurable Parameter Type Value Age Info

---------------- ------------ ------------ ---------- ---------- ---------
CoresTotal Total 24 0.001s

CoresUp Total 24 0.001s

DevicesClosed Total 0 0.001s

DevicesDown Total 0 0.001s

DevicesTotal Total 0 0.001s

DevicesUp Total 0 0.001s

...


**The** -n|--nodes **Option**
The -n option is used to sample specified nodes or node ranges:


**Example**


[basecm11->partition[base]]% device

[basecm11->device]% samplenow -n node001..node002 loadone

Entity Measurable Parameter Type Value Age Info

------------ ------------------ --------- --------- ------- ------- ----
node001 LoadOne OS 0.04 0.08s

node002 LoadOne OS 0 0.077s


**The** --metrics **And** --checks **Option**
For a particular entity:


  - All metrics can be sampled on demand with the --metrics option


  - All health checks can be sampled on demand with the --checks option


**Example**


[basecm11->device]% samplenow --metrics loadone loadfifteen --n node001,node002

Entity Measurable Parameter Type Value Age Info

------------ ------------------ --------- --------- ------- ------- ----
node001 LoadOne OS 0.04 0.08s

node002 LoadOne OS 0 0.077s

[basecm11->device]% samplenow --checks -n node001..node002

Entity Measurable Parameter Type Value Age Info

------------ ------------------ --------- --------- ------- ------- ----
node001 ManagedServicesOk Internal PASS 0.177s


**10.6 Obtaining Monitoring Data Values** **595**


node001 defaultgateway Network PASS 0.145s

node001 diskspace Disk PASS 0.16s

node001 dmesg OS PASS 0.177s

[basecm11->device]% samplenow --checks diskspace -n node001..node002

Entity Measurable Parameter Type Value Age Info

------------ ------------------ --------- --------- ------- ------- ----
node001 diskspace Disk PASS 0.095s

node002 diskspace Disk PASS 0.097s

[basecm11->device]%


**The** --debug **Option**
The --debug option passes CMD_DEBUG=1 to the script environment. This can be used to provide extra
information on what is happening during sampling.


**Example**


[basecm11->device[node001]]% samplenow ntp

Measurable Type Value Age Info

------------ ------------ ---------- ---------- ---------
ntp Internal PASS 0.51s

[basecm11->device[node001]]% samplenow --debug ntp

Measurable Type Value Age Info

------------ ------------ ---------- ---------- -----------------
ntp Internal PASS 0.524s command: "ps -e"+

[basecm11->device[node001]]% samplenow --debug -v ntp

Measurable Type Value Age Info

------------ ------------ ---------- ---------- ------------------------------------------
ntp Internal PASS 0.543s command: "ps -e"

ntpd process found, pid: 11226
command: "/sbin/ntpq -pn"

found time syspeer: 10.141.255.254

send time request to 10.141.255.254

received a reply from 10.141.255.254

time from 10.141.255.254 : 1586171027.783

time on node : 1586171027.771

time difference : 0.012

execution time 0.06


[basecm11->device[node001]]% !systemctl stop ntpd

[basecm11->device[node001]] samplenow --debug -v ntp

measurable Type Value Age Info

------------ ------------ ---------- ---------- --------------------
ntp Internal UNKNOWN 10s timed out after: 10s


Many scripts under /cm/local/apps/cmd/scripts/ can have their debug output inspected with
samplenow --debug .
A recursive grep on the head node, similar to the following, should show which scripts have a
settable debug environment:


grep -r CMD_DEBUG /cm/local/apps/cmd/scripts/


**The** -s|--status **Option**
Nodes in device mode which have a status of UP, as seen by the status command, can be sampled with
the -s|--status option:


**Example**


**596** **Monitoring: Monitoring Cluster Devices**


[basecm11->device]% samplenow -s UP

Entity Measurable Parameter Type Value Age Info

------------ ------------------ --------- --------- ----------- ------ ----
basecm11 AlertLevel count Internal 0 4.67s

basecm11 AlertLevel maximum Internal 0 4.67s

basecm11 AlertLevel sum Internal 0 4.67s

basecm11 BlockedProcesses OS 0 processes 4.67s

basecm11 BufferMemory Memory 847 KiB 4.67s

basecm11 BytesRecv eth0 Network 357 MiB 4.67s

basecm11 BytesRecv eth1 Network 78.7 MiB 4.67s

...


The preceding example is truncated because it is quite lengthy. However, on the screen, for the
device mode, it shows all the sample values for the measurables for all the entities—head node and
regular nodes—that are up.
To restrict the results to node001 only, it can be run as:


**Example**


[basecm11->device]% samplenow -s UP -n node001

Measurable Parameter Type Value Age Info

------------------ --------- --------- ----------- ------ ----
AlertLevel count Internal 0 0.081s

AlertLevel maximum Internal 0 0.081s

AlertLevel sum Internal 0 0.081s

...


Sampling according to a device status value other than UP is also possible.
The help text for the samplenow command gives further details on its possible options.
The latestmetricdata and latesthealthdata commands (section 10.6.3) display the results from
the latest metric and health samples that have been gathered by the cluster, rather than sampling on
demand.

The dumpmonitoringdata command (section 10.6.4) displays monitoring data gathered over a period
of time in a variety of formats.


**10.6.3** **The Latest Data And Counter Values—The** latest*data **And** latestmetriccounters

**Commands**

Within device mode, the values obtained by the latest measurable sampling run can be displayed for
a specified entity with the latestmonitoringdata, latestmetricdata and latesthealthdata commands:


 - latestmetricdata : The latestmetricdata command for a specified entity displays the most recent metric value that has been obtained by the monitoring system for each metric used by the
entity. For displaying metrics on-demand in cmsh, the samplenow --metrics command (page 594)
can be used for a specified entity.


 - latesthealthdata : The latesthealthdata command for a specified entity displays the most recent value that has been obtained by the monitoring system for each health check used by the
entity. For displaying health check responses on demand in cmsh, the samplenow --checks command (page 594) can be used for a specified entity.


 - latestmonitoringdata : The latestmonitoringdata command for a specified entity combines
the output of the latesthealthdata and latestmetricdata commands, i.e. it displays the latest
samples of the measurables for that entity. For displaying measurables on-demand in cmsh, the
samplenow command (page 593) can be run without options, for a specified entity.


**10.6 Obtaining Monitoring Data Values** **597**


The latestmetriccounters command, on the other hand, displays the latest cumulative counter
values of the cumulative metrics in use by the entity.


**Using The** latest ***** data **Commands**
When using the latest - data commands, the entity must be specified (some output elided):


**Example**


[basecm11->device]% use node001

[basecm11->device[node001]]% latestmetricdata

Measurable Parameter Type Value Age Info

----------------- ---------- ------------ ------------------------ --------------
AlertLevel count Internal 0 1m 12s FAIL schedulers

AlertLevel maximum Internal 0 1m 12s FAIL schedulers

AlertLevel sum Internal 0 1m 12s

BlockedProcesses OS 0 processes 1m 12s

BufferMemory Memory 847 KiB 1m 12s
BytesRecv eth0 Network 311.611 B/s 1m 12s
BytesRecv eth1 Network 0 B/s 1m 12s
BytesSent eth0 Network 349.953 B/s 1m 12s
BytesSent eth1 Network 0 B/s 1m 12s

CPUGuest CPU 0 Jiffies/s 1m 12s

...


Valid entity grouping options and other options can be seen in the help text for the
latestmetricdata and latesthealthdata commands.


**Example**


[basecm11->device]% help latestmetricdata

Name: Latestmetricdata - Display the latest metric data


Usage: latestmetricdata [OPTIONS] [<entity>]


Options:

-v, --verbose

Be more verbose


-n, --nodes <node>

List of nodes, e.g. node001..node015,node020..node028,node030
or ^/some/file/containing/hostnames


-g, --group <group>

Include all nodes that belong to the node group, e.g. testnodes

or test01,test03

...


The commands are mode-sensitive. That means, for example for a nodegroup consisting of, for
example, node001 and node002, that there is a difference in the entities that are displayed from device
mode:


**Example**


[basecm11->device]% latestmetricdata -g mynodegroup

Entity Measurable Parameter Type Value Age State Info

---------- ------------------- ---------- ----------- -------------- ------- ------ -----
node001 AlertLevel count Internal 0 15.4s


**598** **Monitoring: Monitoring Cluster Devices**


node001 AlertLevel maximum Internal 0 15.4s

node001 AlertLevel sum Internal 0 15.4s

node001 BlockedProcesses OS 0 processes 1m 41s

node001 BufferMemory Memory 27.3 KiB 41s
node001 BytesRecv ens3 Network 622.722 B/s 56s
node001 BytesSent ens3 Network 580.088 B/s 56s

...

node002 AlertLevel count Internal 0 15.4s

node002 AlertLevel maximum Internal 0 15.4s

node002 AlertLevel sum Internal 0 15.4s

node002 BlockedProcesses OS 0 processes 1m 20s

node002 BufferMemory Memory 39 KiB 2m 20s
node002 BytesRecv ens3 Network 696.364 B/s 35.6s
node002 BytesSent ens3 Network 574.08 B/s 35.6s

...


and the entities that are displayed, for example, in nodegroup mode:


**Example**


[basecm11->nodegroup]% latestmetricdata mynodegroup

Measurable Parameter Type Value Age State Info

------------ ------------ ------------ ---------- ---------- ------- ----
CoresTotal Total 4 31.8s

CoresUp Total 4 31.8s

FPGAsTotal Total 0 31.8s

FPGAsUp Total 0 31.8s

GPUsTotal Total 0 31.8s

GPUsUp Total 0 31.8s

NodesClosed Total 0 31.8s

NodesDown Total 0 31.8s

NodesTotal Total 2 31.8s

NodesUp Total 2 31.8s


The metrics displayed in device mode are individual device metrics, while the metrics displayed in
nodegroup mode are totalling metrics.
By default the data values are shown with human-friendly units. The --raw option displays the data
values as raw units.


**Using The** latestmetriccounter **Command**
The latestmetriccounter is quite similar to the latestmetricdata command, except that it
displays only cumulative metrics, and displays their accumulated counts since boot. The
latestmonitoringcounter command is an alias for this command.


**Example**


[basecm11->device]% latestmonitoringcounters node001

Measurable Parameter Type Value Age Info

---------------- ------------ ------------ ----------------------- ---------- ----
BytesRecv eth0 Network 286 MiB 11.7s

BytesRecv eth1 Network 0 B 11.7s

BytesSent eth0 Network 217 MiB 11.7s

BytesSent eth1 Network 0 B 11.7s

CPUGuest CPU 0 Jiffies/s 11.7s

CPUIdle CPU 60.1 Jiffies/s 11.7s

CPUIrq CPU 0 Jiffies/s 11.7s

CPUNice CPU 66 Jiffies/s 11.7s

...


**10.6 Obtaining Monitoring Data Values** **599**


The reader can compare the preceding example output against the example output of the
latestmetricdata command (page 597) to become familiar with the meaning of cumulative output.


**10.6.4** **Data Values Over A Period—The** dumpmonitoringdata **Command**
The dumpmonitoringdata command displays monitoring data values over a specified period. This is for
an entity, such as:


  - a node in device mode


  - the base partition in partition mode


  - an image in softwareimage mode


  - a job in the jobs submode. The jobs submode is under the path cmsh  - wlm[< _workload man-_
_ager_ >]    - jobs, and using dumpmonitoringdata with it is covered on page 641.


**Using The** dumpmonitoringdata **Command**
A concise overview of the dumpmonitoringdata command can be displayed by typing in “ help
dumpmonitoringdata ” in a cmsh mode that has entities.
The usage of the dumpmonitoringdata command consists of the following options and mandatory
arguments:
dumpmonitoringdata [ _OPTIONS_ ] < _start-time_ - < _end-time_ - < _measurable_ - [ _entity_ ]


**The mandatory arguments:** The mandatory arguments for the times, the measurables being dumped,
and the entities being sampled, have values that are specified as follows:


  - The measurable < _measurable_  - for which the data values are being gathered must always be given.
Measurables currently in use can conveniently be listed by running the measurables command
(section 10.6.1).


  - If [ _entity_ ] is not specified when running the dumpmonitoringdata command, then it must be set
by specifying the entity object from its parent mode of cmsh (for example, with use node001 in
device mode). If the mode is device mode, then the entity can also be specified via the options as
a list, a group, an overlay, or a category of nodes.


  - The time pair < _start-time_  - or < _end-time_  - can be specified as follows:


**–**
_Fixed time format_ : The format for the times that make up the time pair can be:


       - [[YY/MM/DD] HH:MM[:SS]]
(If YY/MM/DD is used, then each time must be enclosed in double quotes)


       - [The unix epoch time (seconds since 00:00:00 1 January 1970)]


**–** now : For the < _end-time_    -, a value of now can be set. The time at which the dumpmonitoringdata
command is run is then used.


**–**
_Relative time format_ : One item in the time pair can be set to a fixed time format. The other item
in the time pair can then have its time set relative to the fixed time item. The format for the
non-fixed time item (the relative time item) can then be specified as follows:


       - [For the] [ <] _[start-time]_ [>] [, a number prefixed with “-” is used. It indicates a time that much]
earlier than the fixed end time.

       - [For the] [ <] _[end-time]_ [>] [, a number prefixed with “+” is used. It indicates a time that much later]
than the fixed start time.

       - [The number values also have suffix values indicating the units of time, as seconds (] [s] [),]
minutes ( m ), hours ( h ), or days ( d ).


**600** **Monitoring: Monitoring Cluster Devices**


The relative time format is summarized in the following table:


**Unit** < _start-time_      - < _end-time_      

seconds: -< _number_ >s +< _number_ >s


minutes: -< _number_ >m +< _number_ >m


hours: -< _number_ >h +< _number_ >h


days: -< _number_ >d +< _number_ >d


**–** Both < _start-time_    - and < _end-time_    - can have their values prefixed with a “-”. In this case, the
range over which the monitored values are seen is in the past, relative to the current time.
If the end time for the range is specified as further in the past than the starting time, then
the time values are swapped over so that the end time becomes more recent than the starting
time.


**The options:** The options applied to the samples are specified as follows:


**10.6 Obtaining Monitoring Data Values** **601**


**Option** **Argument(s)** **Description**


-v, --verbose show the rest of the line on a new line instead of cutting it off


-d, --delimiter " _<string>_ " set the delimiter to a character


-i, --intervals _<number>_ number of samples to show


-i|--intervals _<number>_ is mandatory if using one of the following four options:


--sum sum over specified entities


--max maximum over specified entities


--min minimum over specified entities


--avg average over specified entities


-u, --unix-epoch use a unix timestamp instead of using the default date format


--raw show the raw value, without units


--human show the human-friendly value, with appropriate units (default)


--consolidationinterval retrieve data from the consolidator with specified interval


--consolidationoffset retrieve data from the consolidator with specified (interval,
offset)


--timeaverage calculate the average for the entire interval for specified devices


--timesum calculate the sum for the entire interval for specified devices


--timecount calculate the number of data points for the entire interval for
specified devices


--timemaximum calculate the maximum for the entire interval for specified devices


--timeminimum calculate the minimum for the entire interval for specified devices


--timegroup group data points for the entire interval for specified devices,
intended for health checks and enummetrics


--delta display change relative to previous value


--clip clip data samples to the requested interval


--uncompress uncompress data samples to the current sampling interval
(shows intermediate values that are the same as the preceding value (“un-RLE” operation))


**The following options are valid only for** device **mode:**


-n, --nodes _<list>_ for list of nodes


-g, --groups _<list>_ for list of groups


-c, --categories _<list>_ for list of categories


-r, --racks _<list>_ for list of racks


-h, --chassis _<list>_ for list of chassis


-e, --overlay _<list>_ Include all nodes in list of overlays


--union calculate the union of specified devices


_...continues_


**602** **Monitoring: Monitoring Cluster Devices**


_...continued_


**Option** **Argument(s)** **Description**


--intersection calculate the intersection of the specified devices


-l, --role _<role>_ Filter all nodes in role


-s, --status _<state>_ for nodes in state UP, OPENING, DOWN, and so on


**Notes And Examples Of** dumpmonitoringdata **Command Use**
Notes and examples of how the dumpmonitoringdata command can be used now follow:


**Fixed time formats:** Time pairs can be specified for fixed times:


**Example**


[basecm11->device[node001]]% dumpmonitoringdata 18:00:00 18:02:00 loadone

Timestamp Value Info

-------------------------- ---------- ---------
2017/08/30 17:58:00 0.02

2017/08/30 18:00:00 0.01

2017/08/30 18:02:00 0.02


Double quotes are needed for times with a YY/MM/DD specification:


**Example**


[basecm11->device[node001]]% dumpmonitoringdata "17/08/30 18:00" "17/08/30 18:02" loadone

Timestamp Value Info

-------------------------- ---------- ---------
2017/08/30 17:58:00 0.02

2017/08/30 18:00:00 0.01

2017/08/30 18:02:00 0.02


Unix epoch time can also be set:


**Example**


[basecm11->device[node001]]% !date -d "Aug 30 18:00:00 2017" +%s

1504108800

[basecm11->device[node001]]% dumpmonitoringdata 1504108800 1504108920 loadone

Timestamp Value Info

-------------------------- ---------- ---------
2017/08/30 17:58:00 0.02

2017/08/30 18:00:00 0.01

2017/08/30 18:02:00 0.02


**Intervals and interpolation:** The -i|--intervals option interpolates the data values that are to be
displayed. The option needs < _number_ - samples to be specified. This then becomes the number of interpolated samples across the given time range. Using “ -i 0 ” outputs only the non-interpolated stored
samples—the raw data—and is the default.


**Example**


**10.6 Obtaining Monitoring Data Values** **603**


[basecm11->device]% dumpmonitoringdata -i 0 -10m now loadone node001

Timestamp Value Info

-------------------------- ---------- ---------
2017/07/21 14:56:00 0.01

2017/07/21 14:58:00 0.14

2017/07/21 15:00:00 0.04

2017/07/21 15:02:00 0.04

2017/07/21 15:04:00 0.08

2017/07/21 15:06:00 0.08


If the number of intervals is set to a non-zero value, then the last value is always no data, since it
cannot be interpolated.


**Example**


[basecm11->device]% dumpmonitoringdata -i 3 -10m now loadone node001

Timestamp Value Info

-------------------------- ---------- ---------
2017/07/21 21:49:36 0

2017/07/21 21:54:36 0.0419998

2017/07/21 21:59:36 no data


A set of nodes can be specified for the dump:


[basecm11->device]% dumpmonitoringdata -n node001..node002 -5m now cpuidle

Entity Timestamp Value Info

------------ -------------------------- ----------------- ---------
node001 2017/07/20 20:14:00 99.8258 Jiffies/s

node001 2017/07/20 20:16:00 99.8233 Jiffies/s

node001 2017/07/20 20:18:00 99.8192 Jiffies/s

node001 2017/07/20 20:20:00 99.8475 Jiffies/s

node002 2017/07/20 20:14:00 99.7917 Jiffies/s

node002 2017/07/20 20:16:00 99.8083 Jiffies/s

node002 2017/07/20 20:18:00 99.7992 Jiffies/s

node002 2017/07/20 20:20:00 99.815 Jiffies/s

[basecm11->device]%


**Summing values:** The --sum option sums a specified metric for specified devices, for a set of specified
times. For 2 nodes, over a period from 2 hours ago until now, with values interpolated over 3 time
intervals, the option can be used as follows:


**Example**


[basecm11->device]% dumpmonitoringdata -2h now -i 3 loadone -n node00[1-2] --sum

Timestamp Value Info

-------------------------- ---------- ---------
2017/07/20 18:30:27 0.0292462

2017/07/20 19:30:27 0

2017/07/20 20:30:27 no data


Each entry in the values column in the preceding table is the sum of loadone displayed by node001, and
by node002, at that time, as can be seen from the following corresponding table:


**Example**


**604** **Monitoring: Monitoring Cluster Devices**


[basecm11->device]% dumpmonitoringdata -2h now -i 3 loadone -n node00[1-2]

Entity Timestamp Value Info

------------ -------------------------- ---------- ---------
node001 2017/07/20 18:30:27 0

node001 2017/07/20 19:30:27 0

node001 2017/07/20 20:30:27 no data

node002 2017/07/20 18:30:27 0.0292462

node002 2017/07/20 19:30:27 0

node002 2017/07/20 20:30:27 no data


Each loadone value shown by a node at a time shown in the preceding table, is in turn an average
interpolated value, based on actual data values sampled for that node around that time.


**Maximum and minimum values:** The --max option takes the maximum of a specified metric for specified devices, for a set of specified times. For 2 nodes, over a period from 2 hours ago until now, with
values interpolated over 3 time intervals, the option can be run as follows:


**Example**


[basecm11->device]% dumpmonitoringdata -2h now -i 3 loadone -n node00[1-2] --max

# Start - Tue Nov 3 09:56:05 2020 (1604393765)

# End - Tue Nov 3 11:56:05 2020 (1604400965)

# LoadOne - Load average on 1 minute

Entity Timestamp Value Info

------------ -------------------------- ---------- ---------
2020/11/03 09:56:05 0.010954

2020/11/03 10:56:05 0.000000

2020/11/03 11:56:05 nan


Each entry in the values column in the preceding table is the maximum of loadone displayed by
node001, and by node002, at that time, as can be seen from the following corresponding table:


**Example**


[basecm11->device]% dumpmonitoringdata -2h now -i 3 loadone -n node00[1-2]

# Start - Tue Nov 3 09:56:05 2020 (1604393765)

# End - Tue Nov 3 11:56:05 2020 (1604400965)

# LoadOne - Load average on 1 minute

Entity Timestamp Value Info

------------ -------------------------- ---------- ---------
node001 2020/11/03 09:56:05 0.0109537

node001 2020/11/03 10:56:05 0

node001 2020/11/03 11:56:05 no data

node002 2020/11/03 09:56:05 0

node002 2020/11/03 10:56:05 0

node002 2020/11/03 11:56:05 no data


Similarly, for the preceding table, if the --min option is used instead, then the result would be:


**Example**


[basecm11->device]% dumpmonitoringdata -2h now -i 3 loadone -n node00[1-2] --min

# Start - Tue Nov 3 09:56:05 2020 (1604393765)

# End - Tue Nov 3 11:56:05 2020 (1604400965)

# LoadOne - Load average on 1 minute

Entity Timestamp Value Info

------------ -------------------------- ---------- ---------
2020/11/03 09:56:05 0.000000

2020/11/03 10:56:05 0.000000

2020/11/03 11:56:05 nan


**10.6 Obtaining Monitoring Data Values** **605**


**Displaying values during a specified time period, with** --clip **:** The --clip option is used with a
specified time period. If there are raw values within the period, these are displayed.
A value is displayed for the start of the period, either by selection of a raw value if it exists at the
exact starting time, or via interpolation if there is no raw value at the exact starting time. Similarly, at
the end of the period a raw value is shown if it exists, or an interpolated value is shown if it does not.


**Example**


[basecm11->device[node001]]% dumpmonitoringdata -5m now bytessent:eth0 --clip