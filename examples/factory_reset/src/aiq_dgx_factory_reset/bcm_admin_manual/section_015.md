# Start : 1552400295 / Tue Mar 12 14:18:15 2019

# End : 1552400595 / Tue Mar 12 14:23:15 2019

Timestamp Value Info

-------------------------- ------------ ---------
2019/03/12 14:18:15 201.942 B/s

2019/03/12 14:20:15 217.883 B/s

2019/03/12 14:22:15 233.058 B/s

2019/03/12 14:23:15 235.831 B/s


In the preceding example, the first 3 samples are raw samples, the last sample is an interpolated
value, over a time period evaluated as being from 14:18:15 to 14:23:15 . The epoch times for this
period, and corresponding human-readable values are shown in the heading to the output table.


**Displaying according to status:** The -s|--status option selects only for nodes with the specified
state. A state is one of the values output by the cmsh command ds or device status . It is also one of
the values returned by the enummetric DeviceStatus (section 10.2.2).


**Example**


[basecm11->device]% dumpmonitoringdata -2m now loadone -s up

Entity Timestamp Value Info

------------ -------------------------- ---------- ---------
basecm11 2017/07/21 15:00:00 0.35

basecm11 2017/07/21 15:02:00 0.53

node001 2017/07/21 14:12:00 0.04

node001 2017/07/21 15:02:00 0.04

node002 2017/07/21 15:00:00 0.22

node002 2017/07/21 15:02:00 0.21

[basecm11->device]%


The argument to -s|--status can be specified with simple regexes, which are case insensitive. For example, inst.* covers the states installing, installer_failed, installer_rebooting
installer_callinginit, installer_unreachable, installer_burning .


**Displaying deltas:** The --delta option lists the difference between successive monitoring data values.
It subtracts the previous data value from the current data value, and divides the result by the time
interval between the two values.


**Example**


[basecm11->device[node001]]% dumpmonitoringdata --delta -6m now pageout

Timestamp Value Delta Info

-------------------------- ------------ ---------------- ---------
2018/09/10 17:49:28 1015.46 B/s nan

2018/09/10 17:51:28 1.35 KiB/s 2.7 B/s/s

2018/09/10 17:53:28 1.34 KiB/s -0.083 B/s/s


**606** **Monitoring: Monitoring Cluster Devices**


Deltas are useful for seeing patterns in rates of change. For example, to check an experimental
version of CMDaemon for a memory leak, an administrator may run:


**Example**


[basecm11->device[basecm11]]% dumpmonitoringdata -2h now memoryused:cmd -n node001 --delta

Timestamp Value Delta Info

-------------------------- ---------- -------------- ---------
2018/08/15 10:00:00.812 68.4 MiB nan

2018/08/15 10:02:00.812 68.4 MiB 0.0341333 B/s

2018/08/15 12:10:00.812 68.4 MiB 0 B/s


The roughly 0B/s increase over 2 hours in the preceding output is a good sign.


**Displaying union and intersection sets:** The --union option displays the union of a set of specified
devices. The devices can be specified by the device grouping options (the options that are used to group
_<lists>_, such as -c, -r and so on).
For example:
if the overlay galeranodes has the node mon001
and

the overlay openstackhypervisors has the nodes node001, and node002
then an example of a union of the set of these two overlays is:


**Example**


[basecm11->device]% dumpmonitoringdata --union -3m now pageout -e galeranodes,openstackhypervisors

Entity Timestamp Value Info

------------ -------------------------- ----------- ---------
mon001 2018/09/11 11:31:56.198 192 KiB/s

mon001 2018/09/11 11:33:56.198 17.8 KiB/s

node001 2018/09/11 11:31:28.996 1.37 KiB/s

node001 2018/09/11 11:33:28.996 1.22 KiB/s

node002 2018/09/11 11:32:04.509 1.54 KiB/s

node002 2018/09/11 11:34:04.509 1.30 KiB/s

[basecm11->device]%


A union of sets in the same grouping option can be carried out using comma-separation for the list
of sets. In the preceding example, the same grouping option is -e|--overlay .
For a union of different grouping options however, the syntax is different. For example, for a union
of the galeranodes overlay, and a node001 node, a similar example is:


**Example**


[basecm11->device]% dumpmonitoringdata --union -3m now pageout -u -e galeranodes -n node001

Entity Timestamp Value Info

------------ -------------------------- ------------ ---------
mon001 1536659036.198 17.3 KiB/s

mon001 1536659156.198 116 KiB/s

node001 1536659008.997 1023.99 B/s

node001 1536659128.996 1.26 KiB/s

[basecm11->device]%


For an intersection of sets, the only syntax allowed is one that uses different grouping options:


**Example**


[basecm11->device]% dumpmonitoringdata --intersection -3m now pageout -e galeranodes -n node001

No remaining entities


For intersection, comma-separation within one grouping option is pointless, and is not supported.


**10.6 Obtaining Monitoring Data Values** **607**


**Displaying percentages of a particular value across a time interval (the** --timegroup **option):** The
--timegroup option for a measurable displays the percentage of appearances of each sampled value of
the measurable during the interval. The percentage is displayed in the row alongside the start time of
the interval. The end time of the interval is displayed in the row that follows:
An example with devicestatus showing the percentages of times in the various provisioning states
(section 5.5.3:


**Example**


[basecm11->device[node001]]% dumpmonitoringdata -8h now devicestatus --timegroup
# Start - Mon May 13 07:43:13 2024 (1715578993)
# End - Mon May 13 15:43:13 2024 (1715607793)

# DeviceStatus - The device status

Timestamp Value Info

-------------------------- ----------------------- ---------
2024/05/13 07:43:13 up 72.8%
2024/05/13 15:43:13 up

2024/05/13 07:43:13 down 24.1%

2024/05/13 15:43:13 down

2024/05/13 07:43:13 installing 1.46%
2024/05/13 15:43:13 installing
2024/05/13 07:43:13 installer_calling_init 0.31%
2024/05/13 15:43:13 installer_calling_init
2024/05/13 07:43:13 going_down 0.57%
2024/05/13 15:43:13 going_down
2024/05/13 07:43:13 booting 0.73%
2024/05/13 15:43:13 booting


Another example is with wlm_slurm_state, an enum that shows the state of nodes that can be allocated
to the Slurm workload manager:


[basecm11->device[node001]]% dumpmonitoringdata -8h now wlm_slurm_state --timegroup
# Start - Mon May 13 07:42:34 2024 (1715578954)
# End - Mon May 13 15:42:34 2024 (1715607754)

# wlm_slurm_state - The state of the nodes

Timestamp Value Info

-------------------------- ---------- ---------
2024/05/13 07:42:34 allocated 4.27%

2024/05/13 15:42:34 allocated

2024/05/13 07:42:34 drain 0.50%

2024/05/13 15:42:34 drain

2024/05/13 07:42:34 idle 90.9%

2024/05/13 15:42:34 idle

2024/05/13 07:42:34 maint 1.76%

2024/05/13 15:42:34 maint

2024/05/13 07:42:34 mixed 2.55%

2024/05/13 15:42:34 mixed


The percentage total is 100% in the output. The --timegroup option tends to be useful and meaningful for health checks and enummetrics, rather than for metrics.


**Some non-interpolating RLE quirks:** When a sample measurement is carried out, if the sample has
the same value as the two preceding it in the records, then the “middle” sample is discarded from
storage.
Thus, when viewing the sequence of output of non-interpolated samples, identical values do not
exceed two entries one after the other. This is a common compression technique known as Run Length
Encoding (RLE). It can have some implications in the output of the dumpmonitoringdata command.


**608** **Monitoring: Monitoring Cluster Devices**


**Example**


[basecm11->device[node001]]% dumpmonitoringdata -10m now threadsused:cmd

Timestamp Value Info

-------------------------- ---------- ---------
2017/07/21 11:16:00 42

2017/07/21 11:20:00 42

2017/07/21 11:22:00 41

2017/07/21 11:24:00 42

2017/07/21 11:26:00 42


In the preceding example, data values for the number of threads used by CMDaemon are dumped
for the last 10 minutes.

Because of RLE, the value entry around 11:18:00 in the preceding example is skipped. It also means
that at most only 2 of the same values are seen sequentially in the Value column. This means that 42 is
not the answer to everything.
For a non-interpolated value, the nearest value in the past, relative to the time of sampling, is used
as the sample value for the time of sampling. This means that for non-interpolated values, some care
may need to be taken due to another aspect of the RLE behavior: The time over which the samples
are presented may not be what a naive administrator may expect when specifying the time range. For
example, if the administrator specifies a 10 minute time range as follows:


**Example**


[basecm11->softwareimage]% dumpmonitoringdata -10m now nodesup default-image

Timestamp Value Info

-------------------------- ---------- ---------
2017/07/13 16:43:00 2

2017/07/20 17:37:00 2

[basecm11->softwareimage]%


then here, because the dump is for non-interpolated values, it means that the nearest value in the
past, relative to the time of sampling, is used as the sample value. For values that are unlikely to change
much, it means that rather than 10 minutes as the time period within which the samples are taken, the
time period can be much longer. Here it turns out to be about 7 days because the nodes happened to be
booted then.


**10.6.5** **Monitoring Data Health Overview–The** healthoverview **Command**
In figure 10.20, section 10.4.6, the Base View navigation path


Monitoring  - Health Status


showed an overview of the health status of all nodes.

The cmsh equivalent is the healthoverview command, which is run from within device mode. If
run without using a device, then it provides a summary of the alert levels for all nodes.
The help text in cmsh explains the options for the healthoverview command. The command can be
run with options to restrict the display to specified nodes, and also to display according to the sort order
of the alert level values.


**Example**


[basecm11->device]% healthoverview -n node00[1-3]

Device Sum Maximum Count Age Info

------------ ------------ ------------ ------------ ------------ ------------
node001 30 15 2 50.7s hot, fan high

node002 30 15 2 50.7s hot, fan high

node003 15 15 1 50.7s hot


**10.6 Obtaining Monitoring Data Values** **609**


**10.6.6** **Monitoring Data About The Monitoring System—The** monitoringinfo **Command**
The monitoringinfo command provides information for specified head nodes or regular nodes about
the monitoring subsystem. The help text shows the options for the command. Besides options to specify
the nodes, there are options to specify what monitoring information aspect is shown, such as storage,
cache, or services.


**Example**


[basecm11->device]% monitoringinfo -n node001

Service Queued Handled Cache miss Stopped Suspended Last operation

--------------------------- ------ -------- ---------- ------- --------- ------------------
Mon::CacheGather 0 0 0 yes no 
Mon::DataProcessor 0 0 0 yes no 
Mon::DataTranslator 0 932,257 0 no no Mon Jul 24 11:34:00

Mon::EntityMeasurableCache 0 0 0 no no Thu Jul 13 16:39:52

Mon::MeasurableBroker 0 0 0 no no 
Mon::Replicate::Collector 0 0 0 yes yes 
Mon::Replicate::Combiner 0 0 0 yes yes 
Mon::RepositoryAllocator 0 0 0 yes no 
Mon::RepositoryTrim 0 0 0 yes no 
Mon::TaskInitializer 0 30 0 no no Thu Jul 13 16:39:52

Mon::TaskSampler 30 233,039 0 no no Mon Jul 24 11:34:00

Mon::Trigger::Actuator 0 0 0 yes no 
Mon::Trigger::Dispatcher 0 0 0 yes no 

Cache Size Updates Requests

----------------------- ------------ ------------ -----------
ConsolidatorCache 0 17 0

EntityCache 10 17 935,280

GlobalLastRawDataCache 87 17 0

LastRawDataCache 142 17 427,301

MeasurableCache 231 17 935,230


Cache Up Down Closed

----------------- ------------ ------------ -----------
DeviceStateCache 3 0 0


Replicator First Last Requests Samples Sources

------------------------ ------------ ------------ ------------ ------------ -----------
ReplicateRequestHandler - - 0 0


Cache Queued Delivered Handled Pickup

------------ ------------ ------------ ------------ -----------
Cache 0 120 932,257 7,766


Plotter First Last Count Samples Sources Requests

------------------ ---------- ---------- -------- -------- -------- -------
RequestDispatcher - - 0 0 0 
RequestHandler - - 0 0 0 

Storage Elements Disk size Usage Free disk

--------------------------- ---------- ------------ -------- -----------
Mon::Storage::Engine 0 0 B 0.0% Mon::Storage::Message 0 0 B 0.0% Mon::Storage::RepositoryId 0 0 B 0.0% 

**610** **Monitoring: Monitoring Cluster Devices**


**10.6.7** **Dropping Monitoring Data With The** monitoringdrop **Command**
Monitoring data gathering can be restricted to certain nodes using node execution filtering and execution multiplexers. Entire data producers can also be disabled with the disable option in monitoring
mode. However, restricting or disabling leaves historical samples in storage—the existing monitoring
data values do not automatically get removed. So, in cmsh and Base View the latest known monitoring
data values then still show up, with a forever-increasing age.
If a data producer is removed, then the associated data values for its measurable or measurables are
removed.

Alternatively, if adding execution filters to a monitoring data producer is intended to be a permanent
change, then all previously collected data can be dropped for filtered nodes.
For example, if the ssh connectivity to only cloud nodes is to be checked:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% monitoring setup use ssh2node

[...->monitoring->setup[ssh2node]]% executionmultiplexers

[...->executionmultiplexers]% show

Type None

[...->executionmultiplexers]% use all nodes

[...->executionmultiplexers[All nodes]]% get types

Node

[...->executionmultiplexers[All nodes]]% set types CloudNode

[...->executionmultiplexers*[All nodes*]]% commit


After this is set, the monitoring data values for a non-cloud node can be checked. The ssh2node
health check data values are then seen to be getting older, without any more updates being added.
These health check data values can then be dropped using the monitoringdrop command from within
the device mode of cmsh command.

It is wise to run a dry-run operation first, in order to make sure that no data values are unintentionally
removed:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device use node001

[...->device[node001]]% latestmonitoringdata | grep ssh2node

ssh2node Network PASS 43m 38s filtered

[...->device[node001]]% monitoringdrop --dry-run --filtered

Entity Measurable

------------ -----------
node001 ssh2node

[...->device[node001]]% monitoringdrop --filtered

Removed 1 entity, measurable pairs

[...->device[node001]]% latestmonitoringdata | grep ssh2node

[...->device[node001]]%


The --force option can be used to remove non-filtered old data, such as data from a disabled measurable. This is also useful when correcting a bad metric script. After fixing the script, the old (incorrect)
data can be dropped.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[...->device]% monitoringdrop --category default my-metric --force

Removed 32 entity, measurable pairs


**10.6 Obtaining Monitoring Data Values** **611**


A reboot or CMDaemon restart is required for the node to start collecting data again on a non-filtered
metric which has been dropped with the --force option.


**10.6.8** **Monitoring Suspension And Resumption—The** monitoringsuspend **And**
monitoringresume **Commands**
The monitoringsuspend command suspends monitoring. The monitoringresume command resumes
monitoring.
When suspension is applied to a head node, the regular nodes simply continue sampling data up to
a maximum of 1 million samples per node. The available backlog is fetched upon resumption.
Suspension can be used during benchmarking to measure the results of benchmarking runs without
having monitoring get in the way.
Suspension can also be used as a quick sanity check during regular cluster operation, as a way for
an administrator to see if it is monitoring that is consuming excessive resources, in comparison with the
other processes on the system. For example, running it on a head node (some output omitted or elided):


**Example**


[root@head1 ~]# sar -b 1

Linux 3.10.0-957.1.3.el7.x86_64 (head1) 10/14/2019 _x86_64_ (28 CPU)


04:41:00 PM tps rtps wtps bread/s bwrtn/s

04:41:02 PM 1481.82 0.00 1481.82 0.00 24355.56

04:41:03 PM 849.49 0.00 849.49 0.00 10367.68

04:41:04 PM 509.00 0.00 509.00 0.00 4440.00

04:41:05 PM 709.90 0.00 709.90 0.00 5853.47

04:41:06 PM 1209.00 0.00 1209.00 0.00 18168.00

^C

[root@head1 ~]# cmsh

[head1]% device use master

[head1->device[head1]]% monitoringsuspend

suspend 14 on head1

[head1->device[head1]]% monitoringinfo

Service Queued Handled Cache miss Stopped Suspended

--------------------------- ---------- ---------- ---------- ---------- ---------
Mon::CacheGather 425 39,857 0 no yes

Mon::DataConverter 0 0 0 no yes

Mon::DataProcessor 0 6,609,369 0 no yes

Mon::DataTranslator 0 311,658 0 no yes

Mon::EntityMeasurableCache 0 0 0 no yes

Mon::MeasurableBroker 0 0 0 no yes

Mon::PerpetualTaskManager 0 0 0 no yes

Mon::Replicate::Collector 0 0 0 yes yes

Mon::Replicate::Combiner 0 0 0 yes yes

...

[head1->device[head1]]% quit

[root@head1 ~]# sar -b 1

Linux 3.10.0-957.1.3.el7.x86_64 (head1) 10/14/2019 _x86_64_ (28 CPU)


04:41:58 PM tps rtps wtps bread/s bwrtn/s

04:41:59 PM 4.04 0.00 4.04 0.00 96.97

04:42:00 PM 3.00 0.00 3.00 0.00 96.00

04:42:01 PM 4.04 0.00 4.04 0.00 96.97

04:42:02 PM 0.00 0.00 0.00 0.00 0.00

04:42:03 PM 0.00 0.00 0.00 0.00 0.00

04:42:04 PM 43.00 0.00 43.00 0.00 528.00


**612** **Monitoring: Monitoring Cluster Devices**


04:42:05 PM 0.00 0.00 0.00 0.00 0.00

04:42:06 PM 3.06 0.00 3.06 0.00 130.61

04:42:07 PM 0.00 0.00 0.00 0.00 0.00


In the preceding example monitoring is seen to be consuming significant resources.
After running monitoringsuspend, resuming monitoring should not be forgotten, and it should be
done soon enough after suspension. If that is not done, then backlogged samples that exceed the limit
of 1 million samples per node on the regular nodes would be lost. Resumption is carried out with:


**Example**


[root@head1 ~]# cmsh

[head1]% device use master

[head1->device[head1]]% monitoringresume

resume 14 on head1


**CMDaemon Directive Settings To Reduce Monitoring Resource Consumption**
The following CMDaemon directive changes may reduce the resource consumption due to monitoring:


**Increasing** **the** **job** **account** **collection** **interval:** by increasing the value of the
JobsSamplingMetricsInterval directive (page 867).


**Disabling** **job** **information** **collection** **completely:** by setting the value of the
JobInformationDisabled directive to 0 (page 870).


**For the Slurm workload manager only, disabling job accounting:** by setting the value of the
SlurmDisableAccountingParsing directive to 0 (page 866).


**Reducing** **the** **duration** **for** **which** **job** **data** **is** **stored:** by reducing the value of the
JobInformationKeepDuration (page 871).


**10.6.9** **Monitoring Pickup Intervals**
All nodes cache their monitoring data. This cached data gets picked up by the active head node at a
regular pickup interval.
It is possible to alter the pickup interval using the monitoringpickup command covered in this
section. The command is run from device mode.

The current pickup intervals can be listed with:


**Example**


[basecm11]% device

[basecm11->device]% monitoringpickup

Hostname Interval Times Priority

------------- ---------- -------- ---------
basecm11 2m - 0

node001 2m - 0

node002 2m - 0


An interval can be set for one or more nodes. For example, a 1-minute pickup interval can be set as
follows:


**Example**


**10.6 Obtaining Monitoring Data Values** **613**


[basecm11]% device use node001

[basecm11->device[node001]]% monitoringpickup --interval 1m

Changed 1 pickup intervals

[basecm11->device[node001]]% monitoringpickup

Hostname Interval Times Priority

------------- ----------- -------- --------
node001 1m 1 100


The pickup interval is carried out only once by default, unless otherwise specified.
The --times option allows the number of times to be specified:


**Example**


[basecm11]% device use node001

[basecm11->device[node001]]% monitoringpickup --interval 1m --times 10

Changed 1 pickup intervals

[basecm11->device[node001]]% monitoringpickup

Hostname Interval Times Priority

------------- ----------- -------- --------
node001 1m 10 100


The --forever option lets the pickup be carried out “forever” [3] .


**Example**


[basecm11->device[node001]]% monitoringpickup --interval 30s --forever

Changed 1 pickup intervals

[basecm11->device[node001]]% monitoringpickup

Hostname Interval Times Priority

------------- ----------- -------- --------
node001 30s - 100


The --priority option applies the priority to equal or lower priority settings:


**Example**


[basecm11]% device

[basecm11->device]% monitoringpickup -n node00[1-2]

Hostname Interval Times Priority

------------- ----------- -------- --------
node001 1m 12 80

node002 1m 17 20

[basecm11->device]% monitoringpickup -n node00[1-2] --interval 5s --priority 50

Changed 1 pickup intervals

[basecm11->device]% monitoringpickup -n node00[1-2]

Hostname Interval Times Priority

------------- ----------- -------- --------
node001 1m 12 80

node002 5s 1 50


In the preceding example, parameters for node002 only were changed, as the priority setting for
node001 was higher than the applied priority option that was requested. Thus, the Interval value
became 5s, as specified, the Times value defaulted to 1, and the specified Priority value of 50 was
applied to node002 only.
The further behavior of the pickup from node002 is as follows:
After picking up data once from node002, five seconds from the change, the interval becomes the
default of 2 minutes once again:


3 Strictly speaking, “forever” means ( 2 64 _−_ 1 ) times on the 64-bit architecture that BCM runs on. For comparison, ( 2 64 _−_ 1 )
seconds is about 585 billion years.


**614** **Monitoring: Monitoring Cluster Devices**


[basecm11->device]% monitoringpickup -n node00[1-2]

Hostname Interval Times Priority

------------- ----------- -------- --------
node001 1m 12 80

node002 2m 0 0


The yet further behavior of the pickup, during the next pickup event, is then as follows:
The Times value of 0 becomes unset. The unset value is represented by  -, and is equivalent to

--forever .

In other words, if a monitoring interval is changed, and the change is not specified as “forever”, then
after the Times value has decremented to zero, the monitoring interval reverts to the default value of
2 minutes. The Times value then becomes a value of -, which implies forever, when the next pickup

occurs.

The job metric sampler can also automatically modify the pickup interval for nodes. Every time a
new job is started, all the nodes that are used by the job are assigned a modified pickup interval. The
new values for the pickup can be managed in the jobmetricsettings mode of cmsh .


[basecm11->...->jobmetricsettings]% show

Parameter Value

-------------------- -----
...

Pickup interval 5s

Pickup priority 50

Pickup times 12


**10.7** **Offloaded Monitoring**


_Offloaded monitoring_ is a feature introduced in NVIDIA Base Command Manager version 9.1.
Traditional BCM monitoring uses a single (active) head node to manage monitoring. That is, to carry
out sampling and to store results for measurables. Traditional monitoring can be used for clusters of
thousands of nodes, assuming the default number measurables are running.
Offloaded monitoring in BCM is designed to share the more resource-intensive parts of monitoring
across nodes so that the head node is not overloaded by monitoring. In practice, offloaded monitoring
needs only to be considered for a clusters that are greater than about 1000 nodes in size, assuming the
clusters have the default number of measurables running.
There are some mandatory requirements, and some recommended settings, which are discussed
later on in section 10.7.3.


**10.7.1** **Why Offloaded Monitoring?**
Traditional monitoring is highly optimized, and with some care is typically able to deal with clusters
of around 10,000 nodes with the default metrics. While it has the virtue of simplicity, it also has the
following possible issues:


  - there is a single point of failure, since monitoring runs on the active head node


  - the head node performance as the number of nodes increases may not be sufficient. To get around
this, monitoring may rely on increasingly expensive hardware, or on reducing the sampling that
is carried out. With the default monitoring in place, with typical server hardware available at the
time of writing of this section (2020), a limit is reached at around 20000 nodes.


These issues may not be acceptable, in which case it makes sense to consider offloaded monitoring.
The advantages of offloaded monitoring are:


  - no single point of failure


  - the ability to scale with the size of the cluster


**10.7 Offloaded Monitoring** **615**


A disadvantage is that offloaded monitoring is more complicated than single head monitoring. However, BCM simply implements it as a role that is assigned to nodes. The BCM backend then manages
the details of offloaded monitoring.


**10.7.2** **Implementing Offloaded Monitoring**
In cmsh offloaded monitoring is implemented via role assignment. The assignment can be carried out at
the level of device, category, or configuration overlay:


**Example**


[basecm11->device]% use node001

[basecm11->device[node001]]% roles

[basecm11->device[node001]->roles]% assign monitoring

[basecm11->device*[node001*]->roles*[monitoring*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Name monitoring

Revision

Type MonitoringRole

Add services yes

Provisioning associations <0 internally used>

Number of backups 2

Backup ring automatic

[basecm11->device*[node001*]->roles*[monitoring*]]%


If offloaded monitoring is to run in a highly available way, so that a failure of one monitoring node
does not halt the monitoring system, then offloaded monitoring must be assigned to two or more nodes.


**10.7.3** **Background Details**
A description of how offloaded monitoring works in the backend follows, because it should help the
cluster administrator in understanding how and when to implement it.
Offloaded monitoring uses nodes that are assigned a monitoring role.
If there are N regular (non-head) nodes in a cluster that are being monitored, and if there are M
monitoring nodes, then the idea of offloading is that each monitoring node covers N/M of the total
monitoring storage, and N/M of the sampling scripts.
In other words, the cluster manager aims to evenly spread the total storage and sampling needed for
all the regular nodes, over the nodes with a monitoring role.
BCM in the default state with no high availability does not run offloaded monitoring.


**High Availability And Offloaded Monitoring With Just The Head Nodes Running As Monitoring Nodes**
The simplest offloaded monitoring configuration is when high availability is configured. That is, when
BCM is configured with two head nodes as described in Chapter 15. By default, a monitoring role is
then assigned to both the head nodes.
This has the effect of doubling the monitoring capacity of the head node pair in NVIDIA Base Command Manager 9.1, in comparison with a head node pair in NVIDIA Base Command Manager version
9.0 and earlier.

The head nodes then carry out storage and sampling for the regular nodes as well as for themselves.


**Offloaded Monitoring With Regular Compute Nodes Running As Monitoring Nodes**
It is possible to run a compute node with a monitoring role assigned to them. This means that the
compute node carries out storage and sampling as part of its monitoring role.
During a SYNC install—the default node provisioning for a healthy node—monitoring data persists.
Monitoring data would be wiped out during a FULL install (section 5.4.4). To provide a check on
this, the node can be set up with the datanode setting (page 261), which requires a confirmation from


**616** **Monitoring: Monitoring Cluster Devices**


the cluster administrator before carrying out a FULL install. However, if the monitoring data values are
that important, then the cluster administrator should consider backup solutions for it anyway.


**Offloaded Monitoring With Dedicated Nodes Running As Monitoring Nodes**
For large clusters of around 10,000 or more nodes, a recommended practice is to have dedicated monitoring nodes. These are then regular nodes that are typically set up with the datanode setting, and are
not used for other purposes such as HPC use. The dedicated monitoring nodes then carry out monitoring sampling and monitoring data storage for the regular nodes. Each of the M dedicated monitoring
nodes takes on N/M of the regular nodes for itself, and records monitoring data from those N/M nodes.
This is illustrated by the following schematic, with arrows indicating the monitoring sampling flow
for the head nodes (H1, H2), dedicated monitoring nodes (M1 to M3), and regular nodes (N1 to N6):


Figure 10.27: Monitoring Sampling Flow For Offloaded Monitoring With Dedicated Monitoring Nodes


A monitoring node in this configuration also copies backups of its monitoring data to other monitoring nodes. Number of backups for the monitoring role (section 10.7.2) is used to configure the number
of backups. In the following schematic, two neighboring monitoring nodes are used as backup:


N1 N2 N3 N4 N5 N6


Figure 10.28: A Simple Backup Flow For Offloaded Monitoring With Dedicated Monitoring Nodes


The backups need not be on the same local network. For example, edge directors can be backed up
to the head node.

If a monitoring node fails, then its monitoring data can be extracted from its backup nodes, and a
new distribution of nodes to be monitored is allocated to the remaining monitoring nodes.
A backup is carried out using what the BCM developers call a _provisioning grab_ . This is similar to
grabimage (section 5.6), but this time designed for grabbing monitoring data. Like grabimage, provisioning grab also works on the basis of an rsync. This means that the first copy can take a while, but that
subsequent copies are much faster.
Provisioning grabs are staggered to reduce bandwidth consumption and to reduce the likely amount


**10.7 Offloaded Monitoring** **617**


of monitoring data that goes out of date during an outage.
Dedicated monitoring nodes can cope with short outages of monitoring nodes, such as are caused by
a CMDaemon restart on that monitoring node, or by a reboot of that monitoring node. These outages are
not expected to take longer than a few minutes, and the monitoring nodes just continue on as normal,
with some missing data samples. However, if an outage is greater than about 15 minutes, such as may
happen if a monitoring node crashes, then a fully automated rebalancing of the loads on the monitoring
nodes can only take place with the aid of backups.
The head nodes in this configuration are configured as HA, and without the monitoring role, and
thus do not carry out monitoring data storage for the regular nodes. They do however still sample and
store data for themselves, and carry out backups to each other.


**Backup nodes:** In addition, for larger clusters, another recommended practice is to have backup nodes
(B1, B2 in the following schematic) for the dedicated monitoring nodes:


N1 N2 N3 N4 N5 N6


Figure 10.29: A More Sophisticated Backup Flow For Offloaded Monitoring With Dedicated Monitoring
Nodes And Dedicated Backup Nodes


Backup nodes for the monitoring nodes take away the monitoring data backup task from the monitoring nodes. This frees up the monitoring nodes so that they can take on even more monitoring.


**Provisioning role on monitoring nodes:** If there is enough capacity on the dedicated monitoring
nodes, and the cluster spends most of its time in a relatively steady state where its nodes do not reboot
frequently, then adding a provisioning role to the monitoring nodes can be an efficient use of resources.
In this case the monitoring nodes are obviously not so dedicated, but the advantage is that rebooting the
entire cluster is then faster, at the cost of perhaps some extra load on the monitoring nodes during such
a reboot.


**Offloaded Monitoring Sampling And Backup Flows For Edge Computing**
For a cluster with edge configured, the edge director flows in the edge network are analogous to head
node flows in the local network. Thus, monitoring is carried out by the directors on the edge nodes, and
the directors also sample themselves.
Thus, edge directors, not in a high-availablity configuration, have the monitoring sampling data flow
shown by the following schematic (figure 10.30):


**618** **Monitoring: Monitoring Cluster Devices**













Figure 10.30: Sampling Flow For Offloaded Monitoring With Non-HA Edge Director Nodes


For edge directors that have been set up in an HA configuration (section 2.1.1 of the _Edge Manual_ ) the
monitoring sampling data flow in the edge network is split up between directors, so that each director
takes half of the edge nodes. This is analogous to how head nodes in an HA configuration take half of
the regular nodes each (figure 10.31):













Figure 10.31: Sampling Flow For Offloaded Monitoring With HA Edge Director Nodes


The backup data flow for a non-HA configuration would then be as follows for an edge director
(figure 10.32):



N1 N2 N3





Figure 10.32: Backup Flow For Offloaded Monitoring With Non-HA Edge Director Nodes


Backing up to the head node is possible for an edge director. But it is usually unwise because one of
the usual reasons to have a segregation of local and edge networks is to reduce data flow between the
local and edge network.


**10.8 The User Portal** **619**


With edge directors in an HA configuration, a big advantage is that backing up to the other edge
director is possible and configured by default, rather than backing up to the head node (figure 10.33):


H1



N1 N2 N3



E1 E2 E3 E4 E5 E6



Figure 10.33: Backup Flow For Offloaded Monitoring With HA Edge Director Nodes


**Default Backups Configurations**
The default backup configurations for monitoring data are:


  - Head node HA : head nodes back up each other


  - Edge node HA : directors back up each other


  - edge directors: directors back up to (both) head nodes


  - cloud directors: directors back up to (both) head nodes


**10.7.4** **Examining Offloaded Monitoring With** monitoringoffloadinformation
The monitoringoffloadinformation displays the monitoring relations between nodes. In a small HA
cluster with a default configuration, with only two HA head nodes basecm11-ha-a and basecm11-ha-b
in a monitoring role, the output of the command for node001 is:


[basecm11-ha-a->device[node001]]% monitoringoffloadinformation

Node Selected Monitoring node Viable Monitoring nodes

-------- -------------------------- ---------------------------
node001 basecm11-ha-b basecm11-ha-a,basecm11-ha-b


Here, node001 is seen as having its monitoring data going to one selected head node.
Viable in this context means a node that is capable of being used for monitoring, even if it may not
be available now, for example due to a temporary outage such as a reboot. Both head nodes are thus
capable of doing monitoring.
For one of the head nodes in the cluster, the output is:


[basecm11-ha-a->device[basecm11-ha-a]]% monitoringoffloadinformation

Node Selected Monitoring node Viable Monitoring nodes

------------- -------------------------- -------------------------
basecm11-ha-a basecm11-ha-a basecm11-ha-a


**10.8** **The User Portal**


The user portal is a restricted version of Base View that allows non-root users to view some cluster
manager data.
With a browser:


  - If the head node landing page (figure 2.1) shows a greytoned user portal block with a _⊕_ within it,
then it means that the user portal is not installed.


**620** **Monitoring: Monitoring Cluster Devices**


  - If the head node landing page shows a colored user portal block with a chain link icon within it,
then the user portal can be accessed via the icon.


The user portal can be added or removed from the cluster manager by adding or removing the
cm-webportal package.


**Example**


[root@basecm11 ~]# yum install cm-webportal

...

Is this ok [y/N]: y

Downloading Packages:

...

Complete!


**10.8.1** **Accessing The User Portal**
The user portal is compatible with most browsers using reasonable settings, and is supported for the
same browsers that Base View supports (section 2.4).
The user portal is located by default on the head node, and can then be accessed in two ways:


  - From the aforementioned link icon within the colored user portal block of the head node landing

page.


  - More directly using a URL of the form:


https://< _host name or IP address_ >:8081/userportal


Both of these access routes lead to a user login page. The state of the cluster can then be viewed by
the users via an interactive interface.

The first time a browser is used to log in to the portal, a prominent warning about the site certificate
being untrusted appears.
The certificate is a self-signed certificate (the X509v3 certificate of Chapter 4 of the _Installation Man-_
_ual_ ), generated and signed by Bright Computing, and the attributes of the cluster owner are part of the
certificate. However, Bright Computing is not a recognized Certificate Authority (CA) like the CAs that
are recognized by a browser, which is why the warning appears.
For a portal that is not accessible from the outside world, such as the internet, the warning about
Bright Computing not being a recognized Certificate Authority is not an issue, and the user can simply accept the “untrusted” certificate, and the browser used then no longer displays such a prominent
warning about the issue.
For a portal that is accessible via the internet, some administrators may regard it as more secure to
ask users to trust the self-signed certificate rather than external certificate authorities. Alternatively the
[administrator can replace the self-signed certificate with one obtained by a trusted recognized CA, for](https://letsencrypt.org)
example the one at [https://letsencrypt.org](https://letsencrypt.org), if that is preferred.
The user portal certificate discussed here is a webserver certificate, similar to that of the landing
page, but served by CMDaemon rather than Apache.


**10.8.2** **Setting A Common Username/Password For The User Portal**
By default, each user has their own username/password login to the portal. Removing the login is not
possible, because the portal is provided by CMDaemon, and users must connect to CMDaemon.
A shared (common) username/password for all users can be set in the configuration file,
common-credentials.json . The default username/password settings are blank, which means that common access is not enabled:


**Example**


**10.8 The User Portal** **621**


[root@basecm11 ~]# cat /cm/local/apps/cmd/etc/htdocs/userportal/assets/config/common-credentials.json

{

"username": "",

"password": ""

}


To enable common access:


  - the common username and password must be added via cmsh or Base View


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% user

[basecm11->user]% add forrestgump

[basecm11->user[forrestgump]]% set password

enter new password:

retype new password:

[basecm11->user*[forrestgump*]]% commit

[basecm11->user[forrestgump]]% quit


  - the common username and password should be set in the appropriate place in the configuration
file, common-credentials.json :


**Example**


[root@basecm11 ~]# cat /cm/local/apps/cmd/etc/htdocs/userportal/assets/config/common-credentials.json

{

"username": "forrestgump",

"password": "1forrest1"

}


A minor stumbling block for the unwary administrator is:
If using Base View, then if the password for the username has already been saved in the browser’s
password manager before changing it in the configuration file, then the password saved in the browser’s
password manager may need to be changed to the new one explicitly.


**10.8.3** **User Portal Access**

By default, the user profile (section 6.4) is set to readonly, which allows viewing of the information
presented in the user portal, without allowing it to be altered.


**10.8.4** **User Portal Home Page**

**User Portal Overview Page**
The default user portal home page is the Overview page. This allows a quick glance to convey the most
important cluster-related information for users (figure 10.34):


**622** **Monitoring: Monitoring Cluster Devices**


Figure 10.34: User Portal: Overview Page


The following items are displayed on the overview page:


  - a Message Of The Day. This can be edited in /cm/local/apps/cmd/etc/htdocs/userportal/
assets/config/message-of-the-day.html


  - links to the documentation for the cluster


  - an overview of the cluster state, displaying some cluster parameters. By default, it is refreshed
every 10s.


The user portal is designed to serve files only, and will not run executables such as PHP or similar
CGI scripts.


**User Portal Job Accounting Page**
Job accounting charts can be viewed on clicking upon the associated icon,, at the top right corner
of the user portal page. The user portal’s Accounting and reporting page for Base View is then displayed.
The accounting and reporting page allows job accounting to be viewed in an accounting panel in a
very similar manner to how it is done in section 12.5.


**10.9** **Cloud Job Tagging**


_Cloud job tagging_ is about the ability for cloud job instances to have their associated cloud resources
_tagged_ . This is only possible for AWS at the time of writing (February 2020). Enabling cloud job tagging
via NVIDIA Base Command Manager was introduced in version 9.0.
Tags are key=value pairs for AWS resources, and can be _applied_ to resources. Typically, tags that are
applied are set by the user via the Tag Editor of the Amazon Management Console, and up to 50 tags
can be applied per resource.


**10.10 Event Viewer** **623**


Cloud job tagging should not be confused with the tagging of job metrics for job accounting (section 12.2). AWS cloud resource tagging is only active and handled within AWS.
Cloud job tags allow the time span between tag creation and removal to be associated with a particular workload on the node.

In cmsh, for a cloud node, cloud job tagging can be enabled within cloud mode by setting the
cloudjobtagging parameter for the EC2Provider entity to yes


**Example**


cmsh -c 'cloud; use amazon; set cloudjobtagging yes; commit'


If it is set to yes, then every job running on a cloud node using that specific provider is tagged
according to the applied tags.
A subset of the tags for cloud jobs are _cost allocation tags_ . Cloud job cost allocation tags allow AWS
costs to be tracked for jobs. A cost allocation tag can be:


  - an AWS generated tag: defined, created, and applied by AWS


  - a user-defined tag: defined, created, and applied by the user


By default, BCM provides the following tag names when the cloud job tagging feature is enabled:


 - BCM_JOB_ID


 - BCM_JOB_ACCOUNT


 - BCM_JOB_USER


 - BCM_JOB_NAME


When CMDaemon sees that a job has started, the resources of that job are then tagged with the job ID,
the job account, the job user, and the job name. When CMDaemon detects that the job has stopped, it
removes the tags.
The AWS Cost Explorer can be used to view the AWS costs for a billing period according to tags.
Further information on tagging can be found at:
[https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html) .
Further information on using the Cost Explorer with cost allocation tags can be found at:
[https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)


**10.10** **Event Viewer**


Monitoring in BCM is normally taken by developers to mean how sampling with data producers is
handled. However, cluster administrators using this manual typically consider watching and handling
events in BCM to also be a part of a more general concept of monitoring. This manual is aimed at cluster
administrators, and therefore this section on event viewing and handling is also placed in the current
monitoring chapter.
BCM events can be handled and viewed in several ways. Event logging is enabled by default by the
EventLogger directive (page 853).


**10.10.1** **Viewing Events In Base View**
In Base View, events can be viewed by clicking on the Events icon of figure 10.5. This opens up a
window with a sortable set of columns listing the events in the events log, and with by default with the
most recent events showing up first.


**624** **Monitoring: Monitoring Cluster Devices**


**10.10.2** **Viewing Events In** cmsh
The events command is a global cmsh command. It allows events to be viewed at several severity levels
(section 10.2.7), and allows old events to be displayed. The usage and synopsis of the events command
is:


Usage: events
events on [broadcast|private]
events off [broadcast|private]

events level <level>

events clear

events details <id> [<id>]

events <number> [level]

events follow


Arguments:


level info,notice,warning,error,alert


Running the command without any option shows event settings, and displays any event messages
that have not been displayed yet in the session:


**Example**


[basecm11->device]% events

Private events: off

Broadcast events: on

Level: notice

custom ......................[ RESET ] node001


Running the command with options allows the viewing and setting of events as follows:


 - on [broadcast|private] : event messages are displayed as they happen in a session, with cmsh
prompts showing in between messages:


**–** If only on is set, then all event messages are displayed as they happen:


       - [either to all open] [ cmsh] [ sessions, and also in Base View event viewer panes, if the event or]
its trigger has the “broadcast” property.

       - [or only in the] [ cmsh] [ session that is running the command, if the event or its trigger has the]
“private” property.


**–** If the further option broadcast is set, then the event message is displayed as it happens in all
open cmsh sessions, and also in all Base View event viewer panes, if the event or its trigger
has the “broadcast” property.


**–**
If the further option private is set, then the event message is displayed as it happens only in
the cmsh session that ran the command, if the event or its trigger has the “private” property.


 - off [broadcast|private] : disallows viewing of event messages as they happen in a session.
Event messages that have not been displayed due to being forbidden with these options, are displayed when the events command is run without any options in the same session.


**–** If only off is set, then no event message is displayed as it happens in the session. This is
regardless of the “broadcast” or “private” property of the event or its trigger.


**–** If the further option broadcast is set, then the event message is not displayed as it happens,
if the event or its trigger has the “broadcast” property.


**–**
If the further option private is set, then the event message is not displayed as it happens, if
the event or its trigger has the “private” property.


**10.10 Event Viewer** **625**


 - level <info|notice|warning|error|alert> : sets a level. Messages are then displayed for this
and higher levels.


 - clear : clears the local cmsh event message cache. The cache indexes some of the events.


 - details < _id_  - : shows details for a specific event with the index value of < _id_  -, which is a number
that refers to an event.


 - < _number_  - [info|notice|warning|error|alert] : shows a specified < _number_  - of past lines of
events. If an optional level ( info, notice,...) is also specified, then only that level and higher
(more urgent) levels are displayed.


 - follow : follows event messages in a cmsh session, similar to tail -f /var/log/messages . This
is useful, for example, in tracking a series of events in a session without having the cmsh prompt
showing. The output can also be filtered with the standard unix text utilities, for example: events
follow | grep node001


A common example of events that send private messages as they happen are events triggered by the
updateprovisioners command, which has the “private” property. The following example illustrates
how setting the event viewing option to private controls what is sent to the cmsh session. Some of the
output has been elided or truncated for clarity:


**Example**


[basecm11->softwareimage]% events on private

Private events: on

[basecm11->softwareimage]% updateprovisioners

Provisioning nodes will be updated in the background.

[basecm11->softwareimage]%
Tue Apr 29 01:19:12 2014 [notice] basecm11: Provisioning started: sendi...

[basecm11->softwareimage]%
Tue Apr 29 01:19:52 2014 [notice] basecm11: Provisioning completed: sen...
updateprovisioners [ COMPLETED ]

[basecm11->softwareimage]% !#events were indeed seen in cmsh session

[basecm11->softwareimage]% !#now block the events and rerun update:

[basecm11->softwareimage]% events off private

Private events: off

[basecm11->softwareimage]% updateprovisioners

Provisioning nodes will be updated in the background.

[basecm11->softwareimage]% !#let this 2nd update run for a while

[basecm11->softwareimage]% !#(time passes)

[basecm11->softwareimage]% !#nothing seen in cmsh session.

[basecm11->softwareimage]% !#show a 2nd update did happen:

[basecm11->softwareimage]% events 4 | grep -i provisioning
Tue Apr 29 01:19:12 2014 [notice] basecm11: Provisioning started: sendi...
Tue Apr 29 01:19:52 2014 [notice] basecm11: Provisioning completed: sen...
Tue Apr 29 01:25:37 2014 [notice] basecm11: Provisioning started: sendi...
Tue Apr 29 01:26:01 2014 [notice] basecm11: Provisioning completed: sen...


**10.10.3** **Using The Event Bucket From The Shell For Events And For Tagging Device States**

**Event Bucket Default Behavior**

The BCM _event bucket_ accepts input piped to it, somewhat like the traditional unix “bit bucket”,
/dev/null . However, while the bit bucket simply accepts any input and discards it, the event bucket
accepts a line of text and makes an event of it. Since the event bucket is essentially an event processing
tool, the volumes that are processed by it are obviously less than that which /dev/null can handle.
By default, the location of the event bucket is at /var/spool/cmd/eventbucket, and a message can
be written to the event pane like this:


**626** **Monitoring: Monitoring Cluster Devices**


**Example**


[root@basecm11 ~]# echo "Some text" > /var/spool/cmd/eventbucket


This adds an event with, by default, the info severity level, to the event pane, with the _InfoMessage_
“Some text”.


**10.10.4** **InfoMessages**
InfoMessages are optional messages that inform the administrator of the reason for the status change of
a measurable, or an event in the cluster.
Measurable scripts can use file descriptor 3 within their scripts to write an InfoMessage:


**Example**


echo "Drive speed unknown: Reverse polarity" >&3


**Event Bucket Severity Levels**
To write events at specific severity levels (section 10.2.7), and not just at the info level, the appropriate
text can be prepended from the following to the text that is to be displayed:


EVENT_SEVERITY_DEBUG:

EVENT_SEVERITY_INFO:

EVENT_SEVERITY_NOTICE:

EVENT_SEVERITY_WARNING:

EVENT_SEVERITY_ERROR:

EVENT_SEVERITY_ALERT:


**Example**


echo "EVENT_SEVERITY_ERROR:An error line" > /var/spool/cmd/eventbucket


The preceding example displays an output notification in the Base View event viewer as shown in figure 10.35:


Figure 10.35: Base View Monitoring: Event Bucket Message Example


**Event Bucket Filter**

Regex expressions can be used to conveniently filter out the user-defined messages that are about to go
into the event bucket from the shell. The filters used are placed in the event bucket filter, located by
default at /cm/local/apps/cmd/etc/eventbucket.filter .


**Event Bucket CMDaemon Directives**

The name and location of the event bucket file and the event bucket filter file can be set using the
EventBucket and EventBucketFilter directives from the CMDaemon configuration file directives (Appendix C).


**10.10 Event Viewer** **627**


**Adding A User-Defined Message To A Device State With The Event Bucket**
While the event bucket is normally used to send a message to the event viewer, it can instead be used to
add a message to the state of a device. The line passed to the echo command then has the message and
device specified in the following format:
STATE.USERMESSAGE[.device]:[message] .
The device can be anything with a status property, such as, for example, a node, a switch, or a chassis.


**Example**


echo "STATE.USERMESSAGE.node001:just right" > /var/spool/cmd/eventbucket


The state then shows as:


cmsh -c "device ; status node001"

node001 .................. (just right) [ UP ]


If the device is not specified, then the current host of the shell that is executing the echo command is
used. For example, running these commands from the head node, basecm11, as follows:


**Example**


echo "STATE.USERMESSAGE:too hot" > /var/spool/cmd/eventbucket
ssh node001 'echo "STATE.USERMESSAGE:too cold" > /var/spool/cmd/eventbucket'


yields these states:


cmsh -c "device ; status basecm11"

basecm11 .................. (too hot) [ UP ]

cmsh -c "device ; status node001"

node001 .................. (too cold) [ UP ]


The added text can be cleared with echoing a blank message to that device. For example, for node001
that could be:


echo "STATE.USERMESSAGE.node001:" > /var/spool/cmd/eventbucket


**Reloading CMDaemon Logging Configuration With Event Bucket**
CMDemon logging configuration is reloaded when CMDaemon is restarted ( systemctl restart cmd ).
The logging configuration can also be reloaded without restarting CMDaemon by triggering the event
bucket:


**Example**


[root@basecm11 etc]# echo LOGGING.RELOAD.CONFIG > /var/spool/cmd/eventbucket


**Using An Event Bucket During The Node-installer Stage**
The node-installer runs before systemd is up on the node that is being provisioned. This means that CMDaemon is also not yet running on that node, so that the regular event bucket features are not available
during that time. However, a simplified event bucket—the node-installer event bucket—is available
during this stage.
The node-installer event bucket can be particularly useful if debugging larger initialize and finalize
scripts (Appendix E).
To use it, text is echoed to /tmp/eventbucket within the node or category scripts. The text will show
up (if permitted) within the sessions of cmsh, and within the events viewer of Base View.
There are two different modes for the node-installer event bucket:


1. Device status info-message updater mode:


**628** **Monitoring: Monitoring Cluster Devices**


**Example**


echo "info-message: this text will be shown in the device status" > /tmp/eventbucket


2. Warning event mode:


**Example**


echo "Some text that will become an event" > /tmp/eventbucket


**An Alternative To InfoMessages With The REST API**
A cleaner alternative to InfoMessages for status messages is the Status REST API call (section 4.2.1 of
the _Developer Manual_ ).


**10.11** **Monitoring Location With GNSS**


GNSS (Global Navigation Satellite System) is the term given to GPS and similar systems. GNSS can be
used to allow devices with the appropriate GNSS hardware to work out their location. The hardware is
commonly implemented as a PCI-X card. A use case for this is to allow an engoineer to walk to a node
with a mobile phone, or to determine a sensible provisioning host.
The hardware requires the ability to receive satellite signals via an antenna. From the signals, the
time of receipt and location can be worked out. BCM makes the results available in the locations
submode of the base partition of cmsh :


**Example**


[basecm11->partition[base]]% locations

Type Entity Age Latitude Longitude Height Message

---------------- ----------------------- -------- ----------- ----------- -------- ---------------
EdgeSite Amsterdam West 2d 17h 52.1904 4.939 0 Amsterdam-South

EdgeSite Fort-Collins 6d 7h 40.5538 -105.0849 0 Fort-Collins

HeadNode rima 57m 3s 52.3927 4.8361 0 Amsterdam

PhysicalNode bright-office-director 2d 16h 52.1903 4.9163 0 Amsterdam-South

PhysicalNode bright-office-node001 2d 17h 52.1904 4.9617 0 Amsterdam-South

PhysicalNode fort-collins-director 6d 7h 40.5538 -105.0849 0 Fort-Collins

[basecm11->partition[base]]%


In practice, due to environmental interference, a minimum resolution of 5m is common for longitude
and lattitude. The height determination is typically 1.5x more inaccurate. Vendor specifications should
be referred to for details on obtaining greater accuracy, since there are technology enhancements that
can improve the accuracy.
The location is determined at start up and on demand.


**10.12** **Monitoring Report Queries**


**10.12.1** **Monitoring Report Queries In** cmsh
There are usually several hundred sources of data in BCM, and they are often of different types. An administrator would sometimes like to see the output of the data sources grouped by particular nodes. The
variety of types means that examining the data output according to grouping choices would normally
be awkward.

The data output can be viewed in BCM with the help of a simple query language from within the
monitoring report submode. The query language can be used to filter by grouping choices and data
values.


**10.12 Monitoring Report Queries** **629**


**Data Sources For Monitoring Reports**
The sources of data can be listed in report mode with the fields command:


**Example**


[basecm11->monitoring->report]% fields | head -30

Name Type Values

--------------------------------- ------------ --------------
AlertLevel METRIC

BIOS Date SYSINFO 04/01/2014

BIOS Vendor SYSINFO SeaBIOS

BIOS Version SYSINFO SeaBIOS

BlockedProcesses METRIC

BufferMemory METRIC

BytesRecv COUNTER

BytesSent COUNTER

...


**Filtering And Grouping For Monitoring Reports**
A filter can be executed using the execute command on a specified field, and applying a filter grouping
to it using an operator.
For example, in report mode, the already-existing "Dual cpu" object by default has the query property:


**Example**


[basecm11->monitoring->report]% get dual cpu query

filter processors == 2 group_by cores "processor vendor"


With this, the operator == checks for dual CPU cores using a filter grouping on the field cores . An
existing query can be executed with the execute -q option:


**Example**


[basecm11->monitoring->report]% execute -q dualcpu

cores processor vendor Hostnames

-------- ---------------- ---------------------------------------------
2 GenuineIntel nas,basecm11-a,basecm11-b


Similarly, the field ssh2node can have the filter grouping category applied to it using the operator

==
for all nodes that are up. This could then be executed.
If the ssh2node field output is a PASS for nodes that are in a category gpu, and ssh2node is also a PASS
for node001 and node002, but is a FAIL for node003 and node004, then the report from the query for this,
showing the non-empty groupings of hostnames, would be as indicated by the following session:


**Example**


[basecm11->monitoring->report]% execute filter status == up group_by ssh2node category

ssh2node category Hostnames

-------- -------- ----------------------
PASS default node001,node002

FAIL default node003,node004

PASS gpu gpu01..gpu20

[basecm11->monitoring->report]%


Alternatively, the query can be saved and run as follows:


**630** **Monitoring: Monitoring Cluster Devices**


**Example**


[basecm11->monitoring->report]% add ssh2node-category

[basecm11->monitoring->report*[ssh2node-category*]% set query


_the editor opens up and the line_
execute filter status == up group_by ssh2node category
_is entered_


[basecm11->monitoring->report*[ssh2node-category*]% commit

[basecm11->monitoring->report*[ssh2node-category]% execute

ssh2node category Hostnames

-------- -------- ----------------------
PASS default node001,node002

FAIL default node003,node004

PASS gpu gpu01..gpu20

[basecm11->monitoring->report*[ssh2node-category]%


**Saving the list of nodes that the filter is applied to:** The --save option takes a file base name as its
argument, and saves the list of nodes that the filter applies to. Suffixes appended to the file base name
are taken from the filter that is used and from the grouping values.


**Example**


[basecm11->monitoring->report]% execute filter status == up group_by ssh2node category --save /tmp/test

[basecm11->monitoring->report]% !cat /tmp/test-default-up.lst

node001

node002


The file name thus takes the form: < _basename_ >-< _grouping value_ >-< _filter value_  - .lst
The file can be read within cmsh by using the operator ˆ


**Example**


[basecm11->monitoring->report]% device power status -n ^/tmp/PASS-default.lst

custom ................... [ ON ] node001

custom ................... [ ON ] node002


**10.13** **Monitoring With** nvsm


The nvsm command in the device mode of cmsh is a BCM wrapper for the NVIDIA System Management
(NVSM) software stack.


  - The NVSM stack provides a CLI and API for the end user to monitor NVIDIA DGX hardware.
These are documented in detail at [https://docs.nvidia.com/datacenter/nvsm/latest/pdf/](https://docs.nvidia.com/datacenter/nvsm/latest/pdf/nvsm-user-guide.pdf)

[nvsm-user-guide.pdf](https://docs.nvidia.com/datacenter/nvsm/latest/pdf/nvsm-user-guide.pdf) .


  - The nvsm wrapper command of cmsh is a front-end to some parts of the NVSM stack.


The nvsm CLI can be run directly on a node with an NVSM software stack. That CLI should not be
confused with the nvsm wrapper command that is run from within the device mode of cmsh, and which
is what is described in the rest of this section (section 10.13).
Running nvsm without any arguments displays the nvsm help text:


**10.13 Monitoring With** nvsm **631**


[basecm11->device]% nvsm

Name:

nvsm - NVSM management


Usage:

nvsm [OPTIONS] versions

nvsm [OPTIONS] list


Options:

-n, --nodes <node>

List of nodes, e.g. node001..node015,node020..node028,node030 or ^/some/file/containing/hostnames


... many options skipped...


Examples:

nvsm versions Show versions reported by NVSM for this or all nodes

nvsm versions -c dgx-h100 Show versions reported by NVSM for the specified category of nodes

nvsm info List the most recent health dumps information

nvsm alerts List the alerts for this or all nodes

nvsm health -n dgx-[001-002] Run the NVSM dump on the specified nodes
nvsm status -n dgx-[001-002] Get the NVSM dump status on the specified nodes

nvsm stop -n dgx-001 Stop the NVSM dump status on the specified nodes


Tab-completion prompts to nvsm suggest nvsm -specific options:


**Example**


[basecm11->device[node001]]% nvsm _<TAB><TAB>_

alerts health info status stop versions


The nvsm -specific parts for this command are indicated by the following cmsh tree:


nvsm


alerts


--start <start>

--limit <limit>

health


--quick

--tags <tags>

info


--history

status

stop

versions


--details


The preceding tree is discussed further next:


 - alerts : Presents a list of the alerts that NVSM detects.


**Example**


[basecm11->device[node001]]% nvsm alerts

Node component_id description event_time message message_details ...

-------- ------------ ---------------------- ----------- ---------------------- ---------------------...

node001 0 NVLink-C2C is reporti+ 1737722655 System entered degrad+ Unexpected Link Count...

node001 1 NVLink-C2C is reporti+ 1737722655 System entered degrad+ Unexpected Link Count...


**632** **Monitoring: Monitoring Cluster Devices**


node001 GPU0 GPU is reporting an e+ 1737722589 GPU0 is reporting NV GPU 0's NvLink link 0...

node001 GPU1 GPU is reporting an e+ 1737722589 GPU1 is reporting NV GPU 1's NvLink link 0...

node001 NVME0 PCI sub-system is rep+ 1737722589 System entered degrad Device is missing on ...
node001 StorageSub+ Storage Drive configu+ 1737722595 Unsupported drive con+ Drive(s) missing or D...


It has the options:


**–** --start <start> : Sets the first index of the alert to list.


**Example**


[basecm11->device[node001]]% nvsm alerts --start 5


This skips the first 4 alerts received, and displays the rest. The alerts are not necessarily
received in same order as displayed by the nvsm alerts command.


**–** --limit <limit> : Sets a limit of <limit> alerts to be displayed.


 - health : carries out a dump to a .tar.xz file for the specified node. The dump for a node named
node001 is stored in /cm/shared/nvsm/node001 by default. It can take about 15 minutes to complete.


**–**
--quick : does a quick dump. This completes faster, but uses more memory and CPU.


**–** --tags <tags> : a comma-separated list of tags for the dump.


 - info : Lists the most recent health dump information.


**Example**


[basecm11->device[node001]]% nvsm info

Node Filename Size

-------- --------------------------------------------------- -------
node001 /cm/shared/nvsm/node001_2025-01-24-04-51-31.tar.xz 417MiB


The file name for a node named node001 takes a timestamped format of:


node001 _YYYY-MM-DD-HH-MM-SS .tar.xz


**–**
--history : Lists historical dumps.


**Example**


[basecm11->device]% nvsm info --history

Node Filename Size

-------- --------------------------------------------------- -------
node001 /cm/shared/nvsm/node001_2025-01-24-04-51-31.tar.xz 417MiB

node001 /cm/shared/nvsm/node001_2025-02-14-00-25-24.tar.xz 5.9MiB


 - status : Shows the dump status of the node.


**Example**


[basecm11->device[node001]]% nvsm status

Node duration log status success Result Error

------- --------- --------------------------------------------------- -------- --------- ------- -----
node001 748 Jan 25 02:53:16 node001 systemd[1]: Stopping cm-nv+ active yes good


 - stop : Aborts the dump creation for the specified nodes. With stop, the dump that has been created
until then remains available as a directory rather than a .tar.xz file


**10.13 Monitoring With** nvsm **633**


 - versions : Lists the versions of various components used by NVSM.


**–** --details : May provide some more details on the component.


**Example**


[basecm11->device[node001]]% nvsm versions

Component Version Nodes

------------------------------------- -------------------------------- ----------
FW_BMC_0 Version Unavailable node001

FW_CPLD_0 Version Unavailable node001


_...many entries skipped..._


cuda-driver 12.8 node001

datacenter-gpu-manager 1:4.0.0~10338 node001

datacenter-gpu-manager-fabricmanager 570.59-1 node001

dgx-release 7.0.0 node001

kernel 6.8.0-31-generic-64k node001

nvidia-driver 570.59 node001

nvsm 24.09.05 node001

os-release Ubuntu 24.04 LTS (Noble Numbat) node001

platform PG548 node001

sbios 02.03.13 node001

vBIOS 0 97.00.6c.00.03 node001

vBIOS 1 97.00.6c.00.03 node001

vBIOS 2 97.00.6c.00.03 node001

vBIOS 3 97.00.6c.00.03 node001


The nvsm alert command can inform the cluster administrator about hardware issues more conve
niently than diving into the NVSM CLI. Viewing the output of the alert may be enough to get on with
solving the issue.
If that is not enough, then examining the dump file produced by nvsm health allows for further
troubleshooting by experienced administrators and developers.
The dump file can be extracted with:


**Example**


root@basecm11:/cm/shared/nvsm # tar xvJf node001_2025-01-24-04-51-31.tar.xz


The extracted directories and files have the following layout if viewed at a two-level depth with tree

-L2 :


boot


System.map-6.8.0-31-generic-64k

System.map-6.8.0-51-generic-64k

etc


apt

cm-release

debian_version

dgx-release

environment

issue

lsb-release

network

nvsm


**634** **Monitoring: Monitoring Cluster Devices**


os-release

nvsmhealth_commands


bash_-c_ulimit_-a_

bash_--version

cat_sys_devices_virtual_dmi_id_bios_version

cat_sys_devices_virtual_dmi_id_product_name


_... hundreds of health commands skipped ..._


top_-b_-n_5

uname_-a

uptime_-p

_usr_bin_nv-disk-encrypt_info

virsh_list_--all

xl_info

xrandr_--verbose

xset_-q

nvsm_resources.json

nvsm_show_health.json

proc


cmdline

cpuinfo

driver

fs

interrupts

iomem

loadavg

mdstat

meminfo

modules

version

result.json

usr


share

var


crash

log