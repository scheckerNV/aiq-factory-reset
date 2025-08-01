# **13**

### **Monitoring: Job Chargeback**

**13.1** **Introduction**


**13.1.1** **The Word “Chargeback”**
In a non-IT context, the term chargeback is commonly used with credit cards, in a situation where a
cardholder disputes a payment that was made to a merchant. When the credit card company pays back
the disputed payment to the card holder, that is called a chargeback.
In an IT context, the term chargeback still has to do with money, and the idea of getting money back.
However, in practice the intention ideally is not about disputing costs, but rather about measuring what
the costs are of the IT resources that have been requested. Measurement of requested resources means
that there is a potential to charge back the users or groups of users who requested these resources.
So, for example, an IT department for an organization may be allocated a budget to run a cluster,
meant for the benefit of the organization. The IT department may make the cluster available to many
other departments. These other departments request cluster resources. The IT department measures the
requested resources and charges back the associated costs.
If a cluster is used by several different departments in the organization, then a simple way to pay
for resource requests is to spread the entire cost as a general overhead expense over all departments
equally. That may make matters easy for the cluster administrator, but can be harmful to the organization, because without a fair resource request management, there is a tendency for resource request
abuse.

If however the resource requests per department are measured, it means that department managers
can be kept aware of how resource requests are being divided up. Being able to measure requested resources per department, and thus being able to charge back the department for the requested resources,
means that the organization using the cluster can plan and manage resource request budgets efficiently
and fairly.


**13.1.2** **Comparison Of Job Chargeback Monitoring Measurement With Other Monitoring**
**Measurements**

Monitoring measurements in BCM in general can be considered to be:


  - Monitoring of devices (Chapter 10), which is about monitoring devices in a cluster.


  - Job monitoring (Chapter 11), which is about using monitoring to measure the resources used by
jobs that actually run.


  - Job accounting (Chapter 12), which is about using monitoring to measure the resources used by a
user, a group, or other classifier entity.


  - Job chargeback (this chapter), which is about using monitoring to measure the resources requested
for a job, whether the resources are used or not. This allows the requester to be charged the costs
of requesting those resources.


**674** **Monitoring: Job Chargeback**


The difference between actual resource use and requested resource use can be illustrated by a thought
experiment:
First, a job is run that runs the CPU at 100% for 10 minutes. After that job is completed, a second job
is run that runs a sleep command that lasts 10 minutes.
If these two jobs are considered from the point of view of CPU resource usage, then according to the
workload manager:
The first job actually uses the CPU for 10 minutes, and the administrator can work out from the job
monitoring system what user that ran that job, and charge the user for CPU usage.
For the second job, the administrator cannot use the job monitoring system to charge the user for the
CPU usage because there was no significant usage measured. However, resources were used up during
this time, because the request for the job blocked the availability of that CPU during this period for
other users. The administrator would like to charge the user for preventing others from accessing the
resources during that period. To do that requires measuring the resources requested during that period,
rather than resources that were really used.
Thus, the aim of job chargeback monitoring is to provide a way to track resource requests, which
typically differs a little from resource usage.


**13.2** **Job Chargeback Measurement**


**13.2.1** **Predefined Job Chargebacks**
Some predefined chargebacks can be listed and configured under the chargeback submode of the wlm
mode.

The predefined list is short:


[basecm11->wlm[slurm]]% chargeback

[basecm11->wlm[slurm]->chargeback]% list
Name (key) Group by user Group by account Price per CPU second

------------------------------------------ ------------- ---------------- -------------------
Jobs completed last month grouped by user yes no 8.64$/d
Jobs completed this month grouped by user yes no 8.64$/d
Jobs completed this year grouped by user yes no 8.64$/d


**Setting A Price For Resource Requests**
The pricing can be set per resource requests over a specified time period. In the preceding list, the period
is a month or a year. The resource and associated resource request consumption can be the following
pairs:


**Resource And Resource Request Consumption Pairs**


**Resource** **Resource Request Consumption**


CPU CPU second


GPU GPU second


CPU core CPU core second


slot slot second


memory bytes byte-second


Different workload managers use different resources for resource measurement, which is why there
is a variety in the resources that can be used for pricing.


**13.2 Job Chargeback Measurement** **675**


**13.2.2** **Setting A Custom Job Chargeback**
In addition to the predefined job chargebacks, more chargebacks can be added. For example, the number
of jobs completed so far today can be set up as follows:


**Example**


[basecm11->wlm[slurm]->chargeback]% add "Jobs completed this day grouped by user"

[basecm11->...ck*[Jobs completed this day grouped by user*]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Name Jobs completed this day grouped by user

Revision

Notes <0B>

Group by user no

Group by group no

Group by account no

Group by job name no

Group by job ID no

Group by parent ID no

Users

Groups

Accounts

Job names

Job IDs

Parent IDs

Price per CPU second 0.00$/s
Price per CPU core second 0.00$/s
Price per GPU second 0.00$/s
Price per memory byte-second 0$/B*s
Price per slot second 0$/slot*s
Currency $

Start time

End time

UTC no

Include running no

Calculate prediction no


[basecm11->...ck*[Jobs completed this day grouped by user*]]% set pricepercpusecond 0.0001$/s

[basecm11->...ck*[Jobs completed this day grouped by user*]]% set groupbyuser yes

[basecm11->...ck*[Jobs completed this day grouped by user*]]% set starttime now/d

[basecm11->...ck*[Jobs completed this day grouped by user*]]% set endtime now/d

[basecm11->...ck*[Jobs completed this day grouped by user*]]% commit


**Chargeback Groupings**
The grouping for the new chargeback Jobs completed this day grouped by user is set to be Group
by user . Grouping by user is a common grouping, because finding resource use by an individual user
is typically the most useful case. Grouping is possible by:


  - user


  - group


  - account


  - job name


  - job ID


**676** **Monitoring: Job Chargeback**


  - parent ID


After setting up chargebacks to suit the needs of the cluster administrator, queries can be made and
reports can be generated using chargebacks. The report and request commands (section 13.2.3) are
used for this.


**13.2.3** **The** report **And** request **Commands**
Continuing on with the chargeback jobs completed this day grouped by user created in section 13.2.2, the report and request commands can be used after CPU request data values have been
gathered on the jobs being run.


**The** report **Command And Its Options**
The report command displays a table of the number of jobs that were run per grouping for a chargeback,
alongside the resource use and cost for each grouping.
Thus, some time after running jobs in Slurm, the report output for the chargeback created earlier,
jobs completed this day grouped by user, might look as follows (some columns elided for clarity):


**Example**


[basecm11->wlm[slurm]->chargeback[jobs completed this day grouped by user]]% report
# Start - Tue Sep 8 00:00:00 2020 CEST (1599516000)
# End - Tue Sep 8 23:59:59 2020 CEST (1599602399)

User Jobs Runtime (s) CPU (s) CPU ($) ... Price ($)

------------ ------------ ------------ ------------ ---------- ... ---------
alice 17 7,806 7,806 0.78 ... 0.78

bob 20 8,775 8,775 0.88 ... 0.88

charlie 19 7,007 7,007 0.7 ... 0.7

david 10 5,122 5,122 0.51 ... 0.51

edgar 25 10,502 10,502 1.05 ... 1.05

frank 21 8,289 8,289 0.83 ... 0.83


The help text for report command lists formatting options:


[basecm11->wlm[slurm]->chargeback]% help report

Name:

report - Create charge back report


Usage:
report [options] <name>


Options:

-d, --delimiter

Set default row separator


-v, --verbose

Be more verbose: multiline table


--start

Pagination start offset


--limit

Pagination result limit


**The** request **Command And Its Options**
The request command lists the chargeback resources requested for a workload manager.
The request command can be run without options. In that case the output shows the resource
request consumption for the chargeback, for the jobs over the period associated with that chargeback:


**13.2 Job Chargeback Measurement** **677**


**Example**


[basecm11->wlm[slurm]->chargeback[jobs completed this day grouped by user]]% request
# Start - Sun Sep 13 00:00:00 2020 CEST (1599948000)
# End - Sun Sep 13 23:59:59 2020 CEST (1600034399)
Jobs Runtime (s) CPU (s) Core (s) GPU (s) Slots (s) Memory (B*s)

------------ ------------ ------------ ------------ ------------ ------------ -----------
5 1,765 1,765 0 0 0 0


The help text for request lists formatting, grouping, pricing, and filtering options:


[basecm11->wlm[slurm]->chargeback]% help request

Name:

request - Chargeback report for workload


Usage:


request [options]


Options:

-u, --group-by-user

group by username


--filter-user <user>[,<user>,...]

filter on specified users


-g, --group-by-group

group by group name


--filter-group <group>[,<group>,...]

filter on specified groups


-a, --group-by-account

group by account


--filter-account <account>[,<account>,...]

filter on specified accounts


-j, --group-by-job-name

group by job name


--filter-job-name <job-name>[,<job-name>,...]

filter on specified job names


-i, --group-by-job-id

group by job id


--filter-job-id <job-id>[,<job-id>,...]

filter on specified job ids


-p, --group-by-parentid

group by parent id


--filter-parent-id <parent-id>[,<parent-id>,...]

filter on specified parent-ids


--price-per-cpu-second


**678** **Monitoring: Job Chargeback**


Price per CPU second


--price-per-cpu-core-second

Price per CPU core second


--price-per-gpu-second

Price per GPU second


--price-per-gpu-second

Price per GPU second


--price-per-memory-byte-second

Price per memory byte * second


--price-per-slot-second

Price per slot second


--currency
Change the currency in which the price is displayed (default $)


--include-running
include running jobs in charge back report (prices will not be final)


--calculate-prediction

calculate a prediction for an incomplete time frame


-d, --delimiter

Set default row separator


--sort <field1>[,<field2>,...]

Override default sort order


--start-time, -s <time>

Start time in Prometheus format


--end-time, -e <time>

End time in Prometheus format, falls back to start-time if not specified


--utc

Use UTC instead of local time


--start

Pagination start offset


--limit

Pagination result limit


-v, --verbose

Be more verbose


Examples:

request Chargeback report for workload for the current WLM

request default Chargeback report for workload for default


For example, using epoch times to specify the start and end times, and grouping by user:


**13.2 Job Chargeback Measurement** **679**


**Example**


[basecm11->wlm[slurm]->chargeback[jobs completed this day grouped by user]]% request -s _\_

1599948000 -e 1600034399 -u

# Start - Sun Sep 13 00:00:00 2020 CEST (1599948000)
# End - Sun Sep 13 23:59:59 2020 CEST (1600034399)
User Jobs Runtime (s) CPU (s) Core (s) GPU (s) Slots (s) Memory (B*s)

--------- ----- ------------ ------------ --------- ---------- ------------ -----------
alice 1 398 398 0 0 0 0

david 2 1,041 1,041 0 0 0 0

edgar 1 325 325 0 0 0 0

frank 1 1 1 0 0 0 0


Another way of duplicating the output of request without options, is to explicitly specify the default values. For the chargeback jobs completed this day grouped by user, which was set up in
section 13.2.2. it corresponds to a start time of now/d and an end time of now/d :


**Example**


[basecm11->...eback[jobs completed this day grouped by user]]% request
# Start - Tue Sep 15 00:00:00 2020 CEST (1600120800)
# End - Tue Sep 15 23:59:59 2020 CEST (1600207199)
Jobs Runtime (s) CPU (s) Core (s) GPU (s) Slots (s) Memory (B*s)

------------ ------------ ------------ ------------ ------------ ------------ -----------
56 72,374 72,374 0 0 0 0

[basecm11->...eback[jobs completed this day grouped by user]]% request -s now/d -e now/d
# Start - Tue Sep 15 00:00:00 2020 CEST (1600120800)
# End - Tue Sep 15 23:59:59 2020 CEST (1600207199)
Jobs Runtime (s) CPU (s) Core (s) GPU (s) Slots (s) Memory (B*s)

------------ ------------ ------------ ------------ ------------ ------------ -----------
56 72,374 72,374 0 0 0 0


Users can be added to the table with the -u option (some output is truncated here for clarity in the
examples that follow):


**Example**


[basecm11->...eback[jobs completed this day grouped by user]]% request -u
# Start - Tue Sep 15 00:00:00 2020 CEST (1600120800)
# End - Tue Sep 15 23:59:59 2020 CEST (1600207199)

User Jobs Runtime (s) CPU (s) Core (s) GPU (s)

------------ ------------ ------------ ------------ ------------ -----------
alice 16 19,538 19,538 0 0

bob 7 15,158 15,158 0 0

charlie 6 6,056 6,056 0 0

david 3 1,636 1,636 0 0

edgar 15 16,475 16,475 0 0

frank 9 13,511 13,511 0 0


A jobs drilldown can be carried out with -j .


**Example**


[basecm11->wlm[slurm]->chargeback[jobs completed this day grouped by user]]% request -j
# Start - Tue Sep 15 00:00:00 2020 CEST (1600120800)
# End - Tue Sep 15 23:59:59 2020 CEST (1600207199)

Job name Jobs Runtime (s) CPU (s) Core (s) GPU (s)


**680** **Monitoring: Job Chargeback**


-------------- ------------ ------------ ------------ ------------ -----------
data-transfer 15 49,248 49,248 0 0

iozone 19 9,918 9,918 0 0

sleep 22 13,208 13,208 0 0


The jobs drilldown can be carried out for a particular user, alice, using the filter option:


**Example**


[basecm11->...grouped by user]]% request -j --filter-user alice
# Start - Tue Sep 15 00:00:00 2020 CEST (1600120800)
# End - Tue Sep 15 23:59:59 2020 CEST (1600207199)

Job name Jobs Runtime (s) CPU (s) Core (s) GPU (s)

-------------- ------------ ------------ ------------ ------------ -----------
data-transfer 5 13,404 13,404 0 0

iozone 6 3,132 3,132 0 0

sleep 5 3,002 3,002 0 0


This can have the user fields added for the case when several users are specified, as follows:


**Example**


[basecm11->...grouped by user]]% request -s now/d -e now/d -u -j --filter-user alice,bob,charlie
# Start - Tue Sep 15 00:00:00 2020 CEST (1600120800)
# End - Tue Sep 15 23:59:59 2020 CEST (1600207199)

User Job name Jobs Runtime (s) CPU (s) Core (s) GPU (s)

------------ -------------- ------------ ------------ ------------ ------------ -----------
alice data-transfer 5 13,404 13,404 0 0

alice iozone 6 3,132 3,132 0 0

alice sleep 5 3,002 3,002 0 0

bob data-transfer 3 12,842 12,842 0 0

bob iozone 1 516 516 0 0

bob sleep 3 1,800 1,800 0 0

charlie data-transfer 1 3,212 3,212 0 0

charlie iozone 2 1,044 1,044 0 0

charlie sleep 3 1,800 1,800 0 0

[basecm11->wlm[slurm]->chargeback[jobs completed this day grouped by user]]%


As the help text for request suggests, there are many more combinations possible.


**13.3** **Job Chargeback Background Information**


Because users can run large numbers of jobs per day, the storage requirement for chargeback records
can be very large indeed. For this reason, a cache is kept in memory, and flushed to storage in a MySQL
database.

CMDaemon AdvancedConfig directives for configuring the MySQL storage for chargebacks are:


 - JobInformationChargeBackKeepDuration (page 871)


 - JobInformationChargeBackKeepCount (page 871)


 - JobInformationChargeBackRemoveInterval (page 872)


# **14**

### **Day-to-day Administration**

Just as for regular Linux system administration, it is a best practice for cluster administration procedures
to be documented as they are carried out.
Updating software packages for bug fixes or for security fixes is a substantial and important part of
the tasks carried out in daily cluster administration. It has its own chapter (Chapter 9).
This chapter discusses other tasks that may come up in day-to-day cluster administration with
NVIDIA Base Command Manager.
Section 14.1 discusses running shell commands in parallel over the cluster.
Section 14.2 discusses how a cluster administrator can ask the help of the BCM support team for
guidance with an issue in an optimum manner.
Section 14.3 discusses how backups can be implemented for BCM.
Section 14.4 discusses revision control for images.
Section 14.5 discusses BIOS configuration with BCM.
Section 14.6 discusses checking hardware matching across the nodes of the cluster.
Section 14.7 discusses Serial Over LAN console access.

Section 14.8 discusses administrative aspects of handling the large amounts of raw monitoring data.
Section 14.9 discusses node replacement.
Section 14.10 discusses using Ansible to configure the cluster via Ansible collections and playbooks.


**14.1** **Parallel Shells:** pdsh **And** pexec


**What** pdsh **And** pexec **Do**
The cluster management tools include two parallel shell execution commands:


 - pdsh (parallel distributed shell, section 14.1.1), runs from within the OS shell. That is, pdsh executes its commands from within bash by default.


 - pexec (parallel execute, section 14.1.2, runs from within CMDaemon. That is, pexec executes its
commands from within the cmsh front end.


A one-time execution of pdsh or pexec can run one or more shell commands on a group of nodes in
parallel.


**A Warning About Power Surge Risks With** pdsh **And** pexec
Some care is needed when running pdsh or pexec with commands that affect power consumption. For
example, running commands that power-cycle devices in parallel over a large number of nodes can be
risky because it can put unacceptable surge demands on the power supplies.
Within cmsh, executing a power reset command from device mode to power cycle a large group of
nodes is much safer than running a parallel command to do a reset using pdsh or pexec . This is because
the CMDaemon power reset powers up nodes after a deliberate delay between nodes (section 4.2).


**682** **Day-to-day Administration**


**Which Command To Use Out Of** pdsh **And** pexec
The choice of using pdsh or pexec commands is mostly up to the administrator. The only time that running pdsh from bash is currently required instead of running pexec from within cmsh, is when stopping
and restarting CMDaemon on a large number of regular nodes (section 2.6.1). This is because a command to stop CMDaemon on a regular node, that itself relies on being run from a running CMDaemon
on a regular node, can obviously give unexpected results.


**14.1.1** pdsh **In The OS Shell**

**Packages Required For** pdsh
By default, the following packages must be installed from the BCM repositories to the head node for
pdsh to function fully:


 - pdsh


 - genders


 - pdsh-mod-cmupdown


 - pdsh-mod-genders


 - pdsh-rcmd-exec


 - pdsh-ssh


The pdsh utility is modular, that is, it gets extra functionality through the addition of modules.
The genders package is used to generate a default /etc/genders configuration file. The file is used to
decide what and how nodes are to be used or excluded by default, when used with pdsh . Configuration
details can be found in man pdsh(1) . The configuration can probably best be understood by viewing
the file itself and noting that BCM in the default configuration associates the following _genders_ with a
list of nodes:


 - all : all the nodes in the cluster, head and regular nodes.


 - category=default : the nodes that are in the default category


 - computenode : regular nodes


 - headnode : node or nodes that are head nodes.


In a newly-installed cluster using default settings, the genders category=default and computenode
have the same list of nodes to begin with.
The default /etc/genders file has a section that is generated and maintained by CMDaemon, but
the file can be altered by the administrator outside the CMDaemon-maintained section. However, it is
not recommended to change the file manually frequently. For example, tracking node states with this
file is not recommended. Instead, the package pdsh-mod-cmupdown provides the -v option for node state
tracking functionality, and how to use this and other pdsh options is described in the next section.


pdsh **Options**
In the OS shell, running pdsh -h displays the following help text:


Usage: pdsh [-options] command ...

-S return largest of remote command return values

-h output usage menu and quit

-V output version information and quit

-q list the option settings and quit

-b disable ^C status feature (batch mode)

-d enable extra debug information from ^C status


**14.1 Parallel Shells:** pdsh **And** pexec **683**


-l user execute remote commands as user

-t seconds set connect timeout (default is 10 sec)

-u seconds set command timeout (no default)

-f n use fanout of n nodes

-w host,host,... set target node list on command line

-x host,host,... set node exclusion list on command line

-R name set rcmd module to name

-M name,... select one or more misc modules to initialize first

-N disable hostname: labels on output lines

-L list info on all loaded modules and exit

-v exclude targets if they are down

-g query,... target nodes using genders query

-X query,... exclude nodes using genders query

-F file use alternate genders file `file'

-i request alternate or canonical hostnames if applicable

-a target all nodes except those with "pdsh_all_skip" attribute

-A target all nodes listed in genders database
available rcmd modules: ssh,exec (default: ssh)


Further options and details are given in man pdsh(1) .


**Examples Of** pdsh **Use**
For the examples in this section, a cluster can be considered that is set up with two nodes, with the state
of node001 being UP and that of node002 being DOWN :


[root@basecm11 ~]# cmsh -c "device status"

node001 .................. [ UP ]

node002 .................. [ DOWN ]

basecm11 ................. [ UP ]


In the examples, the outputs for pdsh could be as follows for the pdsh options considered:


**-A:** With this pdsh option an attempt is made to run the command on all nodes, regardless of the node

state:


**Example**


[root@basecm11 ~]# pdsh -A hostname

node001: node001

node002: ssh: connect to host node002 port 22: No route to host

pdsh@basecm11: node002: ssh exited with exit code 255

basecm11: basecm11


**-v:** With this option an attempt is made to run the command only on nodes nodes that are in the state

UP :


**Example**


[root@basecm11 ~]# pdsh -A -v hostname

node001: node001

basecm11: basecm11


**-g:** With this option, and using, for example, computenode as the genders query, only nodes within
computenode in the /etc/genders file are considered for the command. The -v option then further
ensures that the command runs only on a node in computenode that is up. In a newly-installed cluster,
regular nodes are assigned to computenode by default, so the command runs on all regular nodes that
are up in a newly-installed cluster:


**684** **Day-to-day Administration**


**Example**


[root@basecm11 ~]# pdsh -v -g computenode hostname

node001: node001


**-w:** This option allows a node list ( man pdsh(1) ) to be specified on the command line itself:


**Example**


[root@basecm11 ~]# pdsh -w node00[1-2] hostname

node001: node001

node002: ssh: connect to host node002 port 22: No route to host

pdsh@basecm11: node002: ssh exited with exit code 255


**-x:** This option is the converse of -w, and excludes a node list that is specified on the command line
itself:


**Example**


[root@basecm11 ~]# pdsh -x node002 -w node00[1-2] hostname

node001: node001


**The** dshbak **Command**

The dshbak (distributed shell backend formatting filter) command is a filter that reformats pdsh output.
It comes with the pdsh package.
Running dshbak with the -h option displays:


[root@basecm11 ~]# dshbak -h

Usage: dshbak [OPTION]...

-h Display this help message

-c Coalesce identical output from hosts

-d DIR Send output to files in DIR, one file per host

-f With -d, force creation of DIR


Further details can be found in man dshbak(1) .
For the examples in this section, it is assumed that all the nodes in the cluster are now up. That is,
node002 used in the examples of the preceding section is now also up. Some examples to illustrate how
dshbak works are then the following:


**Without** dshbak **:**


**Example**


[root@basecm11 ~]# pdsh -A ls /etc/services /etc/yp.conf

basecm11: /etc/services

basecm11: /etc/yp.conf

node001: /etc/services

node001: ls: cannot access /etc/yp.conf: No such file or directory

pdsh@basecm11: node001: ssh exited with exit code 2

node002: /etc/services

node002: /etc/yp.conf


**14.1 Parallel Shells:** pdsh **And** pexec **685**


**With** dshbak **, with no** dshbak **options:**


**Example**


[root@basecm11 ~]# pdsh -A ls /etc/services /etc/yp.conf | dshbak
node001: ls: cannot access /etc/yp.conf: No such file or directory

pdsh@basecm11: node001: ssh exited with exit code 2

---------------
basecm11

---------------
/etc/services

/etc/yp.conf

---------------
node001

---------------
/etc/services

---------------
node002

---------------
/etc/services

/etc/yp.conf

[root@basecm11 ~]#


**With** dshbak **, with the** -c **(coalesce) option:**


**Example**


[root@basecm11 ~]# pdsh -A ls /etc/services /etc/yp.conf | dshbak -c
node001: ls: cannot access /etc/yp.conf: No such file or directory

pdsh@basecm11: node001: ssh exited with exit code 2

---------------
node002,basecm11

---------------
/etc/services

/etc/yp.conf

---------------
node001

---------------
/etc/services

[root@basecm11 ~]#


The dshbak utility is useful for creating human-friendly output in clusters with larger numbers of
nodes.


**14.1.2** pexec **In** cmsh
In cmsh, the pexec command is run from device mode:


**Example**


[basecm11->device]% pexec -n node001,node002 "cd ; ls"


[node001] :

anaconda-ks.cfg

install.log

install.log.syslog


**686** **Day-to-day Administration**


[node002] :

anaconda-ks.cfg

install.log

install.log.syslog


**14.1.3** pexec **In Base View**
In Base View, pexec is hidden, but executed in a GUI wrapper, using the navigation path Cluster - Run

command .

For large numbers of nodes, rendering the output into the node subpanes (little boxes) can take a
long time. To improve the Base View experience, selecting the Single text view icon instead of the
Grouped view icon speeds up the rendering significantly, but at the cost of removing the borders of the
subpanes.
Ticking the Join output checkbox places output that is the same for particular nodes, into the same
subpane.
Running parallel shell commands from cmsh instead of in Base View is faster in most cases, due to
less graphics rendering overhead.


**14.1.4** **Using The** -j|--join **Option Of** pexec **In** cmsh
The output of the pexec command by default can come out in a sequence depending on node response
time. To make it more useful for an administrator, order can be imposed on the output. Checking
consistency across nodes is then easier.
For example, in a cluster with 2 nodes, the /etc/resolv.conf files for each node could be displayed

as:


**Example**


[basecm11->device]% pexec -c default "cat /etc/resolv.conf"


[node001] :

# This file was generated by the Node Installer.

search cm.cluster eth.cluster brightcomputing.com

nameserver 10.141.255.254


[node002] :

# This file was generated by the Node Installer.

search cm.cluster eth.cluster brightcomputing.com

nameserver 10.141.255.254


More order can be imposed on the preceding output by using the -j|--join option. This joins
identical fields together in a way similar to the standard unix text utility, join, which makes the result
easier to view:


**Example**


[basecm11->device]% pexec -j -c default "cat /etc/resolv.conf"

[node001,node002]

# This file was generated by the Node Installer.

search cm.cluster eth.cluster brightcomputing.com

nameserver 10.141.255.254


In the following example, a cluster with 10 nodes is inspected. In the cluster, node002 is down, and
the idea is to see if the remaining nodes have the same mounts:


**Example**


**14.2 Getting Support With BCM Issues, And Notifications For Release Updates** **687**


[basecm11->device]% pexec -j -c default "mount|sort"

Nodes down: node002

[node002]

Node down


[node001,node003..node010]

/dev/hda1 on / type ext3 (rw,noatime,nodiratime)
/dev/hda2 on /var type ext3 (rw,noatime,nodiratime)
/dev/hda3 on /tmp type ext3 (rw,nosuid,nodev,noatime,nodiratime)
/dev/hda6 on /local type ext3 (rw,noatime,nodiratime)
master:/cm/shared on /cm/shared type nfs
(rw,rsize=32768,wsize=32768,hard,intr,addr=10.141.255.254)

master:/home on /home type nfs
(rw,rsize=32768,wsize=32768,hard,intr,addr=10.141.255.254)

none on /dev/pts type devpts (rw,gid=5,mode=620)
none on /dev/shm type tmpfs (rw)
none on /proc/sys/fs/binfmt_misc type binfmt_misc (rw)
none on /proc type proc (rw,nosuid)
none on /sys type sysfs (rw)


Here, even more order is imposed by sorting the output of each mount command within bash before
the -j option operates from cmsh . The -c option executes the command on the default category of
nodes.


**14.1.5** **Other Parallel Commands**

Besides pexec, CMDaemon has several other parallel commands:


**pkill** : parallel kill
Synopsis:
pkill [OPTIONS] < _tracker_ - [< _tracker_ - ... ]


**plist** : List the parallel commands that are currently running, with their tracker ID
Synopsis:

plist


**pping** : ping nodes in parallel
Synopsis:
pping [OPTIONS]


**pwait** : wait for parallel commands that are running to complete
Synopsis:
pwait [OPTIONS] < _tracker_ - [< _tracker_ - ... ]


Details on these parallel commands, including examples, can be seen by executing the help command within the device mode of cmsh for a parallel command, < _pcommand_ -, as follows:


[basecm11->device]%help < _pcommand_  

**14.2** **Getting Support With BCM Issues, And Notifications For Release**
**Updates**


The scope of BCM technical support is described in Appendix D of the _Installation Manual_ .


**688** **Day-to-day Administration**


**14.2.1** **The Support Portal For BCM**
Support requests can be sent in via the support portal at
[https://enterprise-support.nvidia.com/s/create-case](https://enterprise-support.nvidia.com/s/create-case)


Figure 14.1: Customer support portal: submitting a support request


When creating a BCM support case at that URL:


  - the Product Type that must be selected is Software .


  - the Product Category that must be selected is:


**–**
Bright Cluster Manager for issues related to versions of BCM prior to BCM version 10.


**–**
Base Command Manager for issues related to BCM version 10 and beyond.


  - Registered users are advised to log in to the support portal. It makes the user experience better
because cluster-related data values are already filled in for a logged-in user.


  - Unregistered users can also create a case via the same URL, to deal with registration issues.


**14.2 Getting Support With BCM Issues, And Notifications For Release Updates** **689**


The Enterprise Support Portal User Guide at


[https://enterprise-support.nvidia.com/s/article/NVIDIA-Enterprise-Support-Guide-for-New-Users](https://enterprise-support.nvidia.com/s/article/NVIDIA-Enterprise-Support-Guide-for-New-Users)


has further details on how users can submit support requests.


BCM support as implemented via the support portal is carried out primarily via e-mail. As a supplement to that, the cm-diagnose (section 14.2.2) and the request-remote-assistance (section 14.2.3)
utilities are provided to help resolve issues. These are discussed next.


**14.2.2** **Reporting Cluster Manager Diagnostics With** cm-diagnose
The diagnostic utility cm-diagnose is run from the head node. It gathers data on the cluster that may
help diagnose issues. Running it as
cm-diagnose --help
displays its options, capabilities, and defaults.
For particular issues it may be helpful to change some of the default values to gather data in a more
targeted way. For example, for larger clusters, the log file limit and the timeout values can both be
increased to avoid logs being cropped and commands being killed during the gathering of diagnostic
data:


**Example**


[root@basecm11 ~]# cm-diagnose --limit 100 --timeout 240


The preceding command increases the log limit from its default of 50 MB to 100 MB, and the timeout
value from its default of 60 s to 240 s.

When carrying out a run to pick up diagnostic data, cm-diagnose runs interactively by default.
The administrator can send the resultant diagnostics file to BCM support directly. The output of a
cm-diagnose session looks something like the following (the output has been made less verbose for
easy viewing):


**Example**


[root@basecm11 ~]# cm-diagnose

To be able to contact you about the issue, please provide
your e-mail address (or support ticket number, if applicable):

franknfurter@example.com


Please enter the related Support Request (SR) or NVIDIA Enterprise Support number and any other

related additional information: [SR-XXXXX] or [XXXXXXXX]

End input with ctrl-d

This has to do with SR-999999 that I submitted just now. In short:

I tried X, Y, and Z on the S2464 motherboard. When that didn't work, I

tried A, B, and C, but the florbish is grommicking.

Thank you.


Support Request number: SR-999999

Thank you.

If issues are suspected in the cmdaemon process, a gdb trace of that process

is useful. In general such trace is only needed if Bright Support asks for this.
Do you want to create a gdb trace of the running CMDaemon? [y/N]


Proceed to collect information? [Y/n]


Processing master


**690** **Day-to-day Administration**


Processing commands

/bin/uname -a

/usr/bin/top -b -n 1
/sbin/ifconfig -a

...

Processing file contents

...

Processing large files and log files

...

Collecting process information for CMDaemon

gdb -p 1334

Executing CMSH commands

...

Finished executing CMSH commands


Processing default-image

Processing commands

...

Processing file contents

...

Creating log file: /root/SR-999999-basecm11__1234.tar.gz


Cleaning up


Automatically submit diagnostics file to http://support.brightcomputing.com/cm-diagnose/ ? [Y/n]


Uploaded file: SR-999999-basecm11__1234.tar.gz
Remove log file (/root/SR-999999-basecm11__1234.tar.gz)? [y/N] y

[root@basecm11 ~]#


**14.2.3** **Requesting Remote Support With** request-remote-assistance
The life-cycle of solving a ticket begins with opening a ticket via the support portal (section 14.2.1), and
then establishing that both the cluster administrator and the support engineer have a basic grasp of the
issue at hand. This is best done via an e-mail exchange.
From this stage onward there are many possible paths. The support engineer may offer a solution,
or ask for more details, or may ask for some tests to be run. Most of the time, e-mail remains the most
efficient way to troubleshoot an issue.
However at times it may be more appropriate for the cluster administrator to allow remote support
from the BCM support engineer in order to resolve the issue. The support engineer may in that case
suggest that the request-remote-assistance utility be run.
The request-remote-assistance utility allows a BCM engineer to securely tunnel into the cluster,
often without a change in firewall or ssh settings of the cluster.
With request-remote-assistance :


  - It must be allowed to access the www and ssh ports of the internet servers used by BCM support.


  - For some problems, the engineer may wish to power cycle a node. In that case, indicating what
node the engineer can power cycle should be added to the option for entering additional information.


  - Administrators familiar with screen may wish to run it within a screen session and detach it so
that they can resume the session from another machine. A very short reminder of the basics of
how to run a screen session is:


**–** run the screen command to open the screen session


**14.2 Getting Support With BCM Issues, And Notifications For Release Updates** **691**


**–** run the request-remote-assistance command within the screen session


**–** ctrl-a d to detach the session (session remains open)


**–** screen -r to resume the session


**–** exit to exit (closes the session)


The request-remote-assistance command itself is run as follows:


**Example**


[root@basecm11 ~]# request-remote-assistance


This tool helps securely set up a temporary ssh tunnel to

sandbox.brightcomputing.com.


Allow an NVIDIA engineer ssh access to the cluster? [Y/n]
This tool uses ICMP ping. Skip ping if your firewall does not allow it? [y/N]


Please enter the related Support Request (SR) or NVIDIA Enterprise Support number and any other related

additional information: [SR-XXXXX] or [XXXXXXXX]

End input with ctrl-d

SR-1234567 - the florbish is grommicking


Thank you.


Added temporary NVIDIA public key.


After the administrator has responded to the ...additional information... entry, and has typed
in the ctrl-d, the utility tries to establish the connection. The screen clears, and the secure tunnel opens
up, displaying the following notice:


REMOTE ASSISTANCE REQUEST

########################################################

A connection has been opened to Bright Computing Support.

Closing this window will terminate the remote assistance

session.

-------------------------------------------------------

Hostname: basecm11.NOFQDN

Connected on port: 7000


ctrl-c to terminate this session


BCM support automatically receives an e-mail alert that an engineer can now securely tunnel into the
cluster. The session activity is not explicitly visible to the administrator. Whether an engineer is logged
in can be viewed with the w command, which shows a user running the ssh tunnel, and—if the engineer is logged in—another user session, along with whatever other sessions the administrator may be
running:


**Example**


[root@basecm11 ~]# w

13:35:00 up 97 days, 17 min, 2 users, load average: 0.28, 0.50, 0.52

USER TTY FROM LOGIN@ IDLE JCPU PCPU WHAT

root pts/0 10.2.37.101 12:24 1:10m 0.14s 0.05s ssh -q -R :7013:127.0.0.1:22 _\_

remote@sandbox.brightcomputing.com basecm11
root pts/1 localhost.locald 12:54 4.00s 0.03s 0.03s -bash


**692** **Day-to-day Administration**


When the engineer has ended the session, the administrator may remove the secure tunnel with a
ctrl-c, and the display then shows:


Tunnel to sandbox.brightcomputing.com terminated.

Removed temporary NVIDIA public key.

[root@basecm11 ~]#


The BCM engineer is then no longer able to access the cluster.
The preceding tunnel termination output may also show up automatically, without a ctrl-c from
the administrator, within seconds after the connection session starts. In that case, it typically means that
a firewall is blocking access to SSH and WWW to BCM’s internet servers.


**14.2.4** **Getting Notified About Updates**
Updates for the various NVIDIA Base Command Manager releases continue for some time after the
initial release is made public. The updates typically have bugfixes and improvements, and an administrator may wish to install an update when it becomes publicly available.
The release notes for BCM can be found online at:

[https://docs.nvidia.com/base-command-manager/#release-notes](https://docs.nvidia.com/base-command-manager/#release-notes)


**14.3** **Backups**


**14.3.1** **Cluster Installation Backup**
BCM does not include facilities to create backups of a cluster installation. The cluster administrator is
responsible for deciding on the best way to back up the cluster, out of the many possible choices.
A backup method is strongly recommended, and checking that restoration from backup actually
works is also strongly recommended.
One option that may be appropriate for some cases is simply cloning the head node. A clone can be
created by PXE booting the new head node, and following the procedure in section 15.4.8.
When setting up a backup mechanism, it is recommended that the full filesystem of the head node
(i.e. including all software images) is backed up. Unless the regular node hard drives are used to store
important data, it is not necessary to back them up.
If no backup infrastructure is already in place at the cluster site, the following open source (GPL)
software packages may be used to maintain regular backups:


 - **Bacula** : Bacula is a mature network based backup program that can be used to backup to a remote
storage location. If desired, it is also possible to use Bacula on nodes to back up relevant data that
is stored on the local hard drives. More information is available at [http://www.bacula.org](http://www.bacula.org)


Bacula requires ports 9101-9103 to be accessible on the head node. Including the following lines
in the Shorewall rules file for the head node allows access via those ports from an IP address of
93.184.216.34 on the external network:


**Example**


ACCEPT net:93.184.216.34 fw tcp 9101

ACCEPT net:93.184.216.34 fw tcp 9102

ACCEPT net:93.184.216.34 fw tcp 9103


The Shorewall service should then be restarted to enforce the added rules.


 - **rsnapshot** : rsnapshot allows periodic incremental filesystem snapshots to be written to a local
or remote filesystem. Despite its simplicity, it can be a very effective tool to maintain frequent
backups of a system. More information is available at [http://www.rsnapshot.org](http://www.rsnapshot.org) .


Rsnapshot requires access to port 22 on the head node.


**14.3 Backups** **693**


**14.3.2** **Local Database And Data Backups And Restoration**
The CMDaemon database is stored in the MySQL cmdaemon database, and contains most of the stored
settings of the cluster.
Monitoring data values are stored as binaries in the filesystem, under /var/spool/cmd/monitoring .
The administrator is expected to run a regular backup mechanism for the cluster to allow restores of
all files from a recent snapshot. As an additional, separate, convenience:


  - For the CMDaemon database:


**–**
the entire database is, by default, also backed up nightly on the cluster filesystem itself (“local
rotating backup”) for the last 7 days:


**Example**


[root@basecm11 ~]# ls -1t /var/spool/cmd/backup/

backup-Wed.sql.gz

backup-Tue.sql.gz

backup-Mon.sql.gz

backup-Sun.sql.gz

backup-Sat.sql.gz

backup-Fri.sql.gz

backup-Thu.sql.gz


**–** the CMDaemon database can also be manually backed up with the cmdaemon-backup command. This can be useful if the administrator would like to carry out an extensive change
on the cluster and would like the reassuring possibility of getting back the old configuration.
If no argument is supplied to cmdaemon-backup, then any existing default backup of the day
is overwritten. If a string is supplied, then the default backup- prefix is replaced. The replacement becomes the supplied string concatenated with a timestamp. This is most easily
illustrated with an example:


**Example**


[root@basecm11 ~]# cmdaemon-backup manual

[root@basecm11 ~]# ls /var/spool/cmd/backup/manual*

manual-24-08-28_13-19-59_Wed.sql.gz


The time stamp in the preceding example is of the form:

-< _two-digit year_ >-< _month_ >-< _date_ >_< _hour_ >-< _minute_ >-< _seconds_ >_


  - For the monitoring data, the raw data records are not backed up locally, since these can get very
large. However, the configuration of the monitoring data, which is stored in the CMDaemon
database, is backed up for the last 7 days too.


**Database Corruption Messages**
A corrupted MySQL database is commonly caused by an improper shutdown of the node. To deal with
this, when starting up, MySQL checks itself for corrupted tables, and tries to repair itself.


  - If MySQL cannot start, then CMDaemon on the head node cannot start.


  - If MySQL can start, but corruption is detected in the database later on, then it keeps running
in read-only mode. The mysql health check on the head node fails, and an info message (section 10.10.4) with an indication of the issue is seen. More details can be found in /var/log/
cmdaemon and using service status mysql.service or journalctl -xeu mysql.service .


The journalctl output might show something similar to the following output extract, if corruption is detected in the data (some output ellipsized):


**694** **Day-to-day Administration**


**Example**


[root@basecm11 ~]# journalctl -xeu mysql.service

...

mysqld[179281]:..546 [ERROR] [MY-012224] [InnoDB] Checksum mismatch in datafile: ./cmdaemon/....
mysqld[179281]:..546 [ERROR] [MY-012592] [InnoDB] Operating system error number 22 in a file....
mysqld[179281]:..546 [ERROR] [MY-012596] [InnoDB] Error number 22 means 'Invalid argument' ...
mysqld[179281]:..546 [ERROR] [MY-012131] [InnoDB] Could not find a valid tablespace file for....
mysqld[179281]:..546 [Warning] [MY-012049] [InnoDB] Cannot calculate statistics for table `c....
mysqld[179281]:..1192 [Warning] [MY-012049] [InnoDB] Cannot calculate statistics for table `....
mysqld[179281]:..1838 [ERROR] [MY-012224] [InnoDB] Checksum mismatch in datafile: ./cmdaemon....
mysqld[179281]:..1838 [ERROR] [MY-012592] [InnoDB] Operating system error number 22 in a fil....
mysqld[179281]:..1838 [ERROR] [MY-012596] [InnoDB] Error number 22 means 'Invalid argument' ...
mysqld[179281]:..1838 [ERROR] [MY-012131] [InnoDB] Could not find a valid tablespace file fo....
mysqld[179281]:..1838 [Warning] [MY-012049] [InnoDB] Cannot calculate statistics for table `....
mysqld[179281]:..2485 [Warning] [MY-012049] [InnoDB] Cannot calculate statistics for table `....
mysqld[179281]:..3131 [Warning] [MY-012049] [InnoDB] Cannot calculate statistics for table `....
mysqld[179281]:..3778 [ERROR] [MY-012224] [InnoDB] Checksum mismatch in datafile: ./cmdaemon....
mysqld[179281]:..3778 [ERROR] [MY-012592] [InnoDB] Operating system error number 22 in a fil....


A corrupt database can continue to run for a while, as write attempts pile up in cache. However,
eventually the database crashes and then BCM and other systems that rely on the database cannot carry
on. Preventing a database crash is therefore important, which is why automatic checks and repairs are
carried out when a database starts up.
To fix a corrupted database, a restoration from backup can be carried out, as explained in the next
section.


**Restoring From The Local Backup**
If the MySQL InnoDB repair tools do not automatically fix the problem, then the issue can normally be
resolved with some manual intervention for a failover or non-failover configuration.
If the head node is a part of a failover configuration, the dbreclone option (section 15.4.2) should
normally provide a CMDaemon and Slurm database that is current. The dbreclone option does not
clone the monitoring data.


**Cloning extra databases:** The file /cm/local/apps/cluster-tools/ha/conf/extradbclone.xml.
template can be used as a template to create a file extradbclone.xml in the same directory. The
extradbclone.xml file can then be used to define additional databases to be cloned. Running the
/cm/local/apps/cmd/scripts/cm-update-mycnf script then updates /etc/my.cnf . The database can
then be cloned with this new MySQL configuration by running
cmha dbreclone < _passive_  where < _passive_ - is the hostname of the passive head node.


If the head node is not part of a failover configuration, then a restoration from local backup can be
done. The local backup directory is /var/spool/cmd/backup, with contents that look like (some text
elided):


**Example**


[root@solaris ~]# cd /var/spool/cmd/backup/

[root@solaris backup]# ls -l

total 280

...

-rw------- 1 root root 33804 Oct 10 04:02 backup-Mon.sql.gz

-rw------- 1 root root 33805 Oct 9 04:02 backup-Sun.sql.gz


**14.4 Revision Control For Images** **695**


-rw------- 1 root root 33805 Oct 11 04:02 backup-Tue.sql.gz

...


The CMDaemon database snapshots are stored as backup-<day of week>.sql.gz In the example,
the latest backup available in the listing for CMDaemon turns out to be backup-Tue.sql.gz
The latest backup can then be ungzipped and piped into the MySQL database for the user cmdaemon .
The password, _<password>_, can be retrieved from /cm/local/apps/cmd/etc/cmd.conf, where it is configured in the DBPass directive (Appendix C).


**Example**


gunzip backup-Tue.sql.gz
systemctl stop cmd #(just to make sure)

mysql -ucmdaemon -p<password> cmdaemon < backup-Tue.sql


Running “ systemctl start cmd ” should have CMDaemon running again, this time with a restored
database from the time the snapshot was taken. That means, that any changes that were done to BCM
after the time the snapshot was taken are no longer implemented.
Monitoring data values are not kept in a database, but in files (section 14.8).


**14.4** **Revision Control For Images**


BCM version 7 introduced support for the implementations of Btrfs provided by the distributions. Btrfs
makes it possible to carry out revision control for images efficiently.


**14.4.1** **Btrfs: The Concept And Why It Works Well In Revision Control For Images**
Btrfs, often pronounced “butter FS”, is a Linux implementation of a copy-on-write (COW) filesystem.
A COW design for a filesystem follows the principle that, when blocks of old data are to be modified, then the new data blocks are written in a new location (the COW action), leaving the old, now
superseded, copy of the data blocks still in place. Metadata is written to keep track of the event so that,
for example, the new data blocks can be used seamlessly with the contiguous old data blocks that have
not been superseded.
This is in contrast to the simple overwriting of old data that a non-COW filesystem such as Ext3fs
carries out.

A result of the COW design means that the old data can still be accessed with the right tools, and
that rollback and modification become a natural possible feature.
“Cheap” _revision control_ is thus possible.
Revision control for the filesystem is the idea that changes in the file system are tracked and can
be rolled back as needed. “Cheap” here means that COW makes tracking changes convenient, take up
very little space, and quick. For an administrator of BCM, cheap revision control is interesting for the
purpose of managing software images.
This is because for a non-COW filesystem such as Ext3fs, image variations take a large amount of
space, even if the variation in the filesystem inside the image is very little. On the other hand, image
variations in a COW filesystem such as Btrfs take up near-minimum space.
Thus, for example, the technique of using initialize and finalize scripts to generate such image variations on the fly (section 3.19.4) in order to save space, can be avoided by using a Btrfs partition to save
the full image variations instead.
“Expensive” revision control on non-COW filesystems is also possible. It is merely not recommended, since each disk image takes up completely new blocks, and hence uses up more space. The
administrator will then have to consider that the filesystem may become full much earlier. The degree
of restraint on revision control caused by this, as well as the extra consumption of resources, means


**696** **Day-to-day Administration**


that revision control on non-COW filesystems is best implemented on test clusters only, rather than on
production clusters.


**14.4.2** **Btrfs Availability And Distribution Support**
Btrfs has been part of the Linux kernel since kernel 2.6.29-rc1. Depending on which Linux distribution
is being used on a cluster, it may or may not be a good idea to use Btrfs in a production environment, as
in the worst case it could lead to data loss.

Btrfs has been officially removed from RHEL distributions since RHEL8.
Btrfs features are supported in SLES15, as described at [https://www.suse.com/releasenotes/x86_](https://www.suse.com/releasenotes/x86_64/SUSE-SLES/15-SP1/index.html#TechInfo.Filesystems)
[64/SUSE-SLES/15-SP1/index.html#TechInfo.Filesystems](https://www.suse.com/releasenotes/x86_64/SUSE-SLES/15-SP1/index.html#TechInfo.Filesystems) .
While no problems have been noticed with storing software images on Btrfs using BCM, it is highly
advisable to keep backups of important software images on a non-Btrfs filesystem when Btrfs is used.
An issue with using cm-clone-install with Btrfs is described on page 766.


**14.4.3** **Installing Btrfs To Work With Revision Control Of Images In BCM**

**Installation Of** btrfs-progs
To install a Btrfs filesystem, the btrfs-progs packages must be installed from the distribution repository
first (some lines elided):


**Example**


[root@basecm11 ~]# yum install btrfs-progs

...

Resolving Dependencies

--> Running transaction check

---> Package btrfs-progs.x86_64 0:4.9.1-1.el7 will be installed

...

Total download size: 678 k

Installed size: 4.0 M

...

Complete!


**Creating A Btrfs Filesystem**
The original images directory can be moved aside first, and a new images directory created to serve as
a future mount point for Btrfs:


**Example**


[root@basecm11 ~]# cd /cm/

[root@basecm11 cm]# mv images images2

[root@basecm11 cm]# mkdir images


A block device can be formatted as a Btrfs filesystem in the usual way by using the mkfs.btrfs
command on a partition, and then mounted to the new images directory:


**Example**


[root@basecm11 cm]# mkfs.btrfs /dev/sdc1

[root@basecm11 cm]# mount /dev/sdc1 /cm/images


If there is no spare block device, then, alternatively, a file with zeroed data can be created, formatted
as a Btrfs filesystem, and mounted as a loop device like this:


**Example**


**14.4 Revision Control For Images** **697**


[root@basecm11 cm]# dd if=/dev/zero of=butter.img bs=1G count=20

20+0 records in

20+0 records out

21474836480 bytes (21 GB) copied, 916.415 s, 23.4 MB/s

[root@basecm11 cm]# mkfs.btrfs butter.img


WARNING! - Btrfs Btrfs v0.20-rc1 IS EXPERIMENTAL

WARNING! - see http://btrfs.wiki.kernel.org before using


fs created label (null) on butter.img

nodesize 4096 leafsize 4096 sectorsize 4096 size 20.00GB

Btrfs Btrfs v0.20-rc1

[root@basecm11 cm]# mount -t btrfs butter.img images -o loop

[root@basecm11 cm]# mount

...

/cm/butter.img on /cm/images type btrfs (rw,loop=/dev/loop0)


**Migrating Images With** cm-migrate-images
The entries inside the /cm/images/ directory are the software images (file trees) used to provision nodes.
Revision tracking of images in a Btrfs filesystem can be done by making the directory of a specific
image a _subvolume_ . Subvolumes in Btrfs are an extension of standard unix directories with versioning.
The files in a subvolume are tracked with special internal Btrfs markers.
To have this kind of version tracking of images work, image migration cannot simply be done with a
cp -a or a mv command. That is, moving images from the images2 directory in the traditional filesystem,
over to images in the images directory in the Btrfs filesystem command with the standard cp or mv
command is not appropriate. This is because the images are to be tracked once they are in the Btrfs
system, and are therefore not standard files any more, but instead extended, and made into subvolumes.
The migration for BCM software images can be carried out with the utility cm-migrate-image, which
has the usage:


cm-migrate-image <path to old image> <path to new image>


where the old image is a traditional directory, and the new image is a subvolume.


**Example**


[root@basecm11 cm]# cm-migrate-image /cm/images2/default-image /cm/images/default-image


The default-image directory, or more exactly, subvolume, must not exist in the Btrfs filesystem
before the migration. The subvolume is created only for the image basename that is migrated, which is
default-image in the preceding example.
In the OS, the btrfs utility is used to manage Btrfs. Details on what it can do can be seen in the
btrfs(8) man page. The state of the loop filesystem can be seen, for example, with:


**Example**


[root@basecm11 cm]# btrfs filesystem show /dev/loop0

Label: none uuid: 6f94de75-2e8d-45d2-886b-f87326b73474

Total devices 1 FS bytes used 3.42GB
devid 1 size 20.00GB used 6.04GB path /dev/loop0


Btrfs Btrfs v0.20-rc1

[root@basecm11 cm]# btrfs subvolume list /cm/images

ID 257 gen 482 top level 5 path default-image


The filesystem can be modified as well as merely viewed with btrfs . However, instead of using the
utility to modify image revisions directly, it is recommended that the administrator use BCM to manage
image version tracking, since the necessary functionality has been integrated into cmsh and Base View.


**698** **Day-to-day Administration**


**14.4.4** **Using** cmsh **For Revision Control Of Images**

**Revision Control Of Images Within** softwareimage **Mode**
The following commands and extensions can be used for revision control in the softwareimage mode
of cmsh :


 - newrevision < _parent software image name_  - " _textual description_ "
Creates a new revision of a specified software image. For that new revision, a revision number is
automatically generated and saved along with time and date. The new revision receives a name
of the form:


< _parent software image name_ >@< _revision number_      

A new Btrfs subvolume:


/cm/images/< _parent software image name_ >-< _revision number_      

is created automatically for the revision. From now on, this revision is a self-contained software
image and can be used as such.


 - revisions [-a|--all] < _parent software image name_  Lists all revisions of specified parent software image in the order they ware created, and associates
the revision with the revision number under the header ID . The option -a|--all also lists revisions
that have been removed.


 - list [-r|--revisions]
The option -r|--revisions has been added to the list command. It lists all revisions with their
name, path, and kernel version. A parent image is the one at the head of the list of revisions, and
does not have @< _revision number_   - in its name.


 - setparent [ _parent software image name_ ] < _revision name_  Sets a revision as a new parent. The action first saves the image directory of the current, possibly
altered, parent directory or subvolume, and then attempts to copy or snapshot the directory or
subvolume of the revision into the directory or subvolume of the parent. If the attempt fails, then
it tries to revert all the changes in order to get the directory or subvolume of the parent back to the
state it was in before the attempt.


 - remove [-a|--all] [-d|--data] < _parent software image name_  Runnning remove without options removes the parent software image. The option -a|--all removes the parent and all its revisions. The option -d|--data removes the actual data. To run the
remove command, any images being removed should not be in use.


**Revision Control Of Images Within** category **Mode**
The category mode of cmsh also supports revision control.
Revision control can function in 3 kinds of ways when set for the softwareimage property at category
level.

To explain the settings, an example can be prepared as follows: It assumes a newly-installed cluster
with Btrfs configured and /cm/images migrated as explained in section 14.4.3. The cluster has a default
software image default-image, and two revisions of the parent image are made from it. These are
automatically given the paths default-image@1 and default-image@2 . A category called storage is
then created:


**Example**


[basecm11->softwareimage]% newrevision default-image "some changes"

[basecm11->softwareimage]% newrevision default-image "more changes"

[basecm11->softwareimage]% revisions default-image


**14.4 Revision Control For Images** **699**


ID Date Description

----- ------------------------------ -----------------------------
1 Fri, 04 Oct 2019 11:19:33 CEST some changes

2 Fri, 04 Oct 2019 11:19:52 CEST more changes

[basecm11->softwareimage]% list -r
Name (key) Path Kernel version

---------------- -------------------------- -------------------------
default-image /cm/images/default-image 3.10.0-957.1.3.el7.x86_64
default-image@1 /cm/images/default-image-1 3.10.0-957.1.3.el7.x86_64
default-image@2 /cm/images/default-image-2 3.10.0-957.1.3.el7.x86_64

[basecm11->softwareimage]% category add storage; commit


With the cluster set up like that, the 3 kinds of revision control functionalities in category mode can
be explained as follows:


1. **Category revision control functionality is defined as unset**
If the administrator sets the softwareimage property for the category to an image without any
revision tags:


**Example**


[basecm11->category]% set storage softwareimage default-image


then nodes in the storage category take no notice of the revision setting for the image set at
category level.


2. **Category revision control sets a specified revision as default**


If the administrator sets the softwareimage property for the category to a specific image, with a
revision tag, such as default-image@1 :


**Example**


[basecm11->category]% set storage softwareimage default-image@1


then nodes in the storage category use the image default-image@1 as their image if nothing is
set at node level.


3. **Category revision control sets the latest available revision by default**
If the administrator sets the softwareimage property for the category to a parent image, but tagged
with the reserved keyword tag latest :


**Example**


[basecm11->category]% set storage softwareimage default-image@latest


then nodes in the storage category use the image default-image@2 if nothing is set at node level.
If a new revision of default-image is created later on, with a later tag ( @3, @4, @5 ...) then the
property takes the new value for the revision, so that nodes in the category will use the new
revision as their image.


**700** **Day-to-day Administration**


**Revision Control For Images—An Example Session**
This section uses a session to illustrate how image revision control is commonly used, with commentary
along the way. It assumes a newly installed cluster with Btrfs configured and /cm/images migrated as
explained in section 14.4.3.
First, a revision of the image is made to save its initial state:


[basecm11->softwareimage]% newrevision default-image "Initial state"


A new image default-image@1 is automatically created with a path /cm/images/default-image-1 .
The path is also a subvolume, since it is on a Btrfs partition.
The administrator then makes some modifications to the parent image /cm/images/default-image,
which can be regarded as a “trunk” revision, for those familiar with SVN or similar revision control
systems. For example, the administrator could install some new packages, edit some configuration files,
and so on. When finished, a new revision is created by the administrator:


[basecm11->softwareimage]% newrevision default-image "Some modifications"


This image is then automatically called default-image@2 and has the path
/cm/images/default-image-2 . If the administrator then wants to test the latest revision on nodes in
the default category, then this new image can be set at category level, without having to specify it for
every node in that category individually:


[basecm11->category]% set default softwareimage default-image@2


At this point, the content of default-image is identical to default-image@2 . But changes done in
default-image will not affect what is stored in revision default-image@2 .
After continuing on with the parent image based on the revision default-image@2, the administrator
might conclude that the modifications tried are incorrect or not wanted. In that case, the administrator
can roll back the state of the parent image default-image back to the state that was previously saved as
the revision default-image@1 :


[basecm11->softwareimage]% setparent default-image default-image@1


The administrator can thus continue experimenting, making new revisions, and trying them
out by setting the softwareimage property of a category accordingly. Previously created revisions
default-image@1 and default-image@2 will not be affected by these changes. If the administrator
would like to completely purge a specific unused revision, such as default-image@2 for example, then
it can be done with the -d|--data option:


[basecm11->softwareimage]% remove -d default-image@2


The -d does a forced recursive removal of the default-image-2 directory, while a plain remove
without the -d option would simply remove the object from CMDaemon, but leave default-image-2
alone. This CMDaemon behavior is not unique for Btrfs—it is true for traditional filesystems too. It is
however usually very wasteful of storage to do this with non-COW systems.


**14.5** **BIOS And Firmware Management**


**14.5.1** **Introduction**

The main PC BIOS firmware is nowadays a subset of the more general firmware of a system. In older versions of BCM, BIOS and firmware management relied on proprietary vendor implementations. While
such legacy implementations are still in use at the time of writing of this section (December 2023), the
modern way of managing BIOS and firmware is with the Redfish standard.
The Redfish standard is an industry API standard intended for RESTful management of large numbers of nodes. It is supported by Dell, HPE, Intel, and others.


**14.5 BIOS And Firmware Management** **701**


Redfish uses a pluggable framework architecture with JSON. This makes adding new properties
easier, and also makes isolating, debugging, and fixing issues easier.
The CMDeamon front ends of cmsh and Base View provide a front end for BIOS and firmware management via Redfish.


**14.5.2** **BIOS Management With BCM JSON Configuration Templates In Redfish**
For BIOS management via Redfish, the JSON configuration is specified per vendor. In BCM the files are
kept under:


/cm/local/apps/cm-bios-tools/templates/


By default, BCM ships with the following configuration file templates:


 - dell_14g.json


 - dell_15g-amd.json


 - dell_15g-intel.json


 - dell_r730.json


 - hpe_dl110.json


 - hpe_dl380g10.json


**Example**


[root@basecm11 ~]# ls -al /cm/local/apps/cm-bios-tools/templates/

total 280

drwxr-xr-x 2 root root 148 Nov 15 08:24 .

drwxr-xr-x 6 root root 64 Nov 15 08:24 ..

-rw-r--r-- 1 root root 5008 Oct 25 19:24 dell_14g.json

-rw-r--r-- 1 root root 6411 Oct 25 19:24 dell_15g-amd.json

-rw-r--r-- 1 root root 20493 Oct 25 19:24 dell_15g-intel.json

-rw-r--r-- 1 root root 7052 Oct 25 19:24 dell_r730.json

-rw-r--r-- 1 root root 211366 Oct 25 19:24 hpe_dl110.json

-rw-r--r-- 1 root root 24448 Oct 25 19:24 hpe_dl380g10.json

[root@basecm11 templates]# cat dell_r730.json


{

"displayName": "Dell Inc. - PowerEdge R730",

"description": "Dell Inc. - PowerEdge R730 - BIOS settings template - v1.0.0",
"properties": [

{

"name": "BootMode",

"displayName": "Boot Mode",
"description": "This field determines the boot mode of the system.\n\nSelecting 'UEFI' enables\
booting to Unified Extensible Firmware Interface (UEFI) capable operating systems.\n\nSelecting\
'BIOS' (the default) ensures compatibility with operating systems that do not support UEFI.",

"type": "Enumeration",
"options": [

{

"displayName": "BIOS",

"value": "Bios"

},

{

"displayName": "UEFI",


**702** **Day-to-day Administration**


"value": "Uefi"

}

],

"pos": {

"g": 0,

"r": 0,

"o": 0,

"w": 6

}

},

{

"name": "NodeInterleave",

"displayName": "Node Interleaving",
"description": "When set to Enabled, memory interleaving is supported if a symmetric memory\
configuration is installed. When set to Disabled, the system supports Non-Uniform Memory Access\
(NUMA) (asymmetric) memory configurations.\n\nOperating Systems that are NUMA-aware understand the\
distribution of memory in a particular system and can intelligently allocate memory in an optimal\
manner. Operating Systems that are not NUMA aware could allocate memory to a processor that is not\
local resulting in a loss of performance. Node Interleaving should only be enabled for Operating\
Systems that are not NUMA aware.\n\nDefault: Disabled",

"type": "Enumeration",
"options": [

{

"displayName": "Enabled",

"value": "Enabled"

},

{

"displayName": "Disabled",

"value": "Disabled"

}

],

"pos": {

"g": 0,

"r": 0,

"o": 1,

"w": 6

}

},

{

"name": "SnoopMode",

"displayName": "Snoop Mode",
"description": "Allows tuning of memory performances under different memory bandwidths. The optimal\
Snoop Mode setting is highly dependent on workload type.\n\nEarly Snoop is best used for latency sensitive\
workloads. This setting offers the best balance between workload effects.\n\nHome Snoop is best used for\
NUMA workloads that need maximum local and remote memory bandwidth.\n\nCluster on Die is best used for\
highly NUMA optimized workloads. This setting offers the best case local memory latency, but worst case\
remote latency.\n\nCluster On Die is only available when Node Interleaving is Disabled.\n\nOpportunistic\
Snoop Broadcast, available on select processor models, works well for workloads of mixed NUMA optimization.\
It offers a good balance of latency and bandwidth.\n\nDefault: Early Snoop",

"type": "Enumeration",
"options": [

{

"displayName": "Early Snoop",

"value": "EarlySnoop"
},


**14.5 BIOS And Firmware Management** **703**


...


**BCM BIOS Configuration States And Operations Overview**
In BCM, a BIOS configuration of a node or category can be thought of as being in one of 4 possible
states, with 3 possible operations that apply the changes to the states. This is shown by the following
schematic:


cmsh or **commit** **bios apply** **reboot**
BCM --------------> CMDaemon database -----------> BIOS (pending) -----------> BIOS (live)

View


For example, the cluster administrator might adjust the BIOS configuration for the node or category
in cmsh . The state set within cmsh then becomes a state stored within the CMDaemon database after the

commit operation of cmsh is carried out.
The cluster administrator can then apply the BIOS configuration that is stored in the CMDaemon
database by running the bios apply operation from within cmsh . The BIOS configuration is then taken
up as the “BIOS (pending)”state stored in the BIOS firmware of the node (or category).
Finally, the cluster administrator can implement the BIOS, so that it runs on the live node (or category). This happens when carrying out a reboot operation for that node (or category). The BIOS
configuration that was a pending BIOS setting then becomes a live BIOS setting.
The details of how these changes can be carried out are explained in the following sections.


**Example BIOS Configuration Session In** cmsh
In cmsh, the BIOS settings can be viewed, compared, and applied at the device mode level or category
mode level.

The BIOS settings for the various states can alternatively be managed using the cm-bios-manage
utility (page 706). However the cmsh or Base View front ends to cm-bios-manage are easier to use.


**Model:** The model must be set for the BIOS settings before other BIOS settings can be managed. If it
is not set, then the status command in biossettings displays an error, as indicated by the following
cmsh session:


**Example**


[basecm11->device[node002]->biossettings]% status

Parameter Configured Pending Live

-------------------------------- ---------- ------- ---
Pending errors:

No model defined


It can be set with the help of tab-completion:


**Example**


[basecm11->device[node002]->biossettings]% set model< _tab_ >< _tab_ 
dell_r730 hpe_dl380

[basecm11->device[node002]->biossettings]% set model hpe_dl380

[basecm11->device*[node002*]->biossettings*]% commit


**704** **Day-to-day Administration**


**Viewing BIOS Parameters:** Each BIOS parameter can now have its value listed and compared by state.
The status command shows a list of the parameters, and their values are displayed for each state.
So, the state columns show:


1. the BIOS parameter as stored in the CMDaemon database (the Configured column),


2. the BIOS parameter as stored on the node itself (the Pending column),


3. the BIOS parameter as implemented on the node itself (the Live column)


**Example**


[basecm11->device[node002]]% biossettings

[basecm11->device[node002]->biossettings]% status

Parameter Configured Pending Live

----------------------------------------------- -------------- ------- ----------------------------
High Precision Event Timer (HPET) ACPI Support < default > - Enabled

Adjacent Sector Prefetch < default > - Enabled

Boot Mode < default > - UEFI Mode

Boot Order Policy < default > - Retry Boot Order Indefinitely

Channel Interleaving < default > - Enabled

Collaborative Power Control < default > - Enabled

Consistent Device Naming < default > - CDN Support for LOMs and Slots

Custom POST Message < default > 
LLC Prefetch < default > - Disabled

Local/Remote Threshold < default > - Auto

Maximum Memory Bus Frequency < default > - Auto

Maximum PCI Express Speed < default > - Per Port Control

Memory Mirroring Mode < default > - Full Mirror

Memory Patrol Scrubbing < default > - Enabled

Memory Refresh Rate < default > - 1x Refresh
Minimum Processor Idle Power Package C-State < default > - Package C6 (retention) State

Minimum Processor Idle Power Core C-State < default > - C6 State

Mixed Power Supply Reporting < default > - Enabled

Network Boot Retry Support < default > - Enabled

Node Interleaving < default > - Disabled

NUMA Group Size Optimization < default > - Flat

Embedded NVM Express Option ROM < default > - Enabled

NVMe PCIe Resource Padding < default > - Normal

Persistent Memory Address Range Scrub < default > - Enabled

POST Verbose Boot Progress < default > - Disabled

Power-On Delay < default > - No Delay

Server Asset Tag < default > 
Network Boot Retry Count < default > - 20


In the preceding example, each parameter of the configured column has a setting of < default > .
This means that the value for the configured setting is a null value, as achieved by running the clear
command for that setting. A BIOS setting configured with < default > as a value does nothing based
on that configuration setting when doing BIOS management operations. Thus, for example, the setting
for Boot Mode in the Configured column can only be made to cause a change in the Pending or Live
columns if it takes a value that is not default .


**Changing And Checking Changes For BIOS Parameters:** Thus, if the states for a node are as follows
for the Boot Mode parameter:


**Example**


**14.5 BIOS And Firmware Management** **705**


[basecm11->device[node002]->biossettings]% status |head -2 ; status |grep "Boot Mode"

Parameter Configured Pending Live

----------------------------------------------- ---------------- --------------- ---------------
Boot Mode < default > - UEFI Mode


then have the Live state value change from UEFI Mode to Legacy BIOS Mode :


1. the first step is to change the Configured state:


**Example**


[basecm11->device[node002]->biossettings]% set boot mode< _tab_ >< _tab_   
legacy bios mode uefi mode

[basecm11->device[node002]->biossettings]% set boot mode legacy bios mode

[basecm11->device*[node002]->biossettings*]% commit

[basecm11->device[node002]->biossettings]% status |head -2 ; status |grep "Boot Mode"

Parameter Configured Pending Live

----------------------------------------------- ---------------- --------------- ---------------
Boot Mode Legacy BIOS Mode - UEFI Mode


    - Beside using the status command within the biossettings submode, the existing BIOS
states that are configured (in CMDaemon) and detected (on the live node) can also be checked
with the bios check command at node or category level:


**Example**


[basecm11->device[node002]->biossettings]% ..

[basecm11->device[node002]]% bios check

Result Parameter Configured Detected

---------- -------------------------------- -------------------------------- ---------
different BootMode LegacyBios Uefi


The bios check command shows a result if there is a difference between the configured (CMDaemon) and detected (live) configuration.


2. The next step is to apply the configuration change to the Pending BIOS state:


**Example**


[basecm11->device[node002]]% bios apply

Node Result Output Error

---------------- -------- -------------------------------- -------------------------------
node002 good

[basecm11->device[node002]]% biossettings

[basecm11->device[node002]->biossettings]% status |head -2 ; status |grep "Boot Mode"

Parameter Configured Pending Live

----------------------------------------------- ---------------- ---------------- --------------
Boot Mode Legacy BIOS Mode Legacy BIOS Mode UEFI Mode


3. Finally, a reboot causes the Pending value to be made live:


**Example**


[basecm11->device[node002]->biossettings]% ..

[basecm11->device[node002]]% reboot

_[cluster administrator waits for the node to finish rebooting]_


**706** **Day-to-day Administration**


The BIOS change to the Live state is then complete. The Pending and Configured state values are
cleared automatically too, so that the states for the Boot Mode parameter now show:


**Example**


[basecm11->device[node002]->biossettings]% status |head -2 ; status |grep "Boot Mode"

Parameter Configured Pending Live

----------------------------------------------- ---------------- --------------- ---------------
Boot Mode < default > - Legacy BIOS Mode


**BIOS Configuration Via** cm-bios-manage
This section can usually be skipped because the administrator is not expected to use the cm-bios-manage
utility directly.
This is because it is relatively low-level, and because the easiest way for a cluster administrator to
manage the BIOS of a cluster via Redfish is usually via the cmsh (page 703) or Base View front ends.
The cm-bios-manage help text is:


[root@basecm11 ~]# /cm/local/apps/cm-bios-tools/bin/cm-bios-manage -h
usage: cm-bios-manage [-h]

[-a | -c | -f VENDOR_MODEL | -p VENDOR_MODEL | -P VENDOR_MODEL PROFILE | -t |

-T VENDOR_MODEL] [-l] [-d]


Script used by cmd to manage BIOS settings.


optional arguments:

-h, --help show this help message and exit

-a, --apply apply settings.

-c, --check check defined settings.

-f VENDOR_MODEL, --fetch VENDOR_MODEL

fetch settings based on JSON template of specified model.

-p VENDOR_MODEL, --profiles VENDOR_MODEL

list all profiles for the specified model.

-P VENDOR_MODEL PROFILE, --profile VENDOR_MODEL PROFILE

display profile for the specified model and specified profile.

-t, -m, --vendor-types, --models

list all supported HW models.

-T VENDOR_MODEL, --template VENDOR_MODEL

display JSON template of specified HW model.

-l, --live fetch live settings, instead of pending settings.

used with --fetch and --check options.

-d, --debug enable debug messages.


A session with options might run as follows:


**Example**


[root@basecm11 ~]# /cm/local/apps/cm-bios-tools/python/cm-bios-manage -t

[

"dell_r730",

"hpe_dl380"

]

[root@basecm11 ~]# /cm/local/apps/cm-bios-tools/python/cm-bios-manage -p hpe_dl380

[

"test"

]

[root@basecm11 ~]# /cm/local/apps/cm-bios-tools/python/cm-bios-manage -P hpe_dl380 test


**14.5 BIOS And Firmware Management** **707**


{

"test": "xyz"

}

[root@basecm11 ~]# /cm/local/apps/cm-bios-tools/python/cm-bios-manage -T hpe_dl380

[

{

"displayName": "High Precision Event Timer (HPET) ACPI Support",

"name": "AcpiHpet",
"pos": {

"w": 12,

"r": 0,

"o": 0,

"g": 0
},

...


**14.5.3** **Updating BIOS And Firmware Versions**
There are two ways that the firmware can be updated. A legacy way based on DOS tools (page 707),
and a more recent way, based on CMDaemon and Redfish (page 708).


**Updating A BIOS Via DOS Tools**
The legacy way of upgrading a BIOS to a new version involves using the DOS tools that were supplied
with the BIOS to flash a new BIOS. The flash tool and the BIOS image must be copied to a DOS image.
The file autoexec.bat should be altered to invoke the flash utility with the correct parameters. In case
of doubt, it can be useful to boot the DOS image and invoke the BIOS flash tool manually. Once the
correct parameters have been determined, they can be added to the autoexec.bat .
After a BIOS upgrade, the contents of the NVRAM may no longer represent a valid BIOS configuration because different BIOS versions may store a configuration in different formats. It is therefore
recommended to also write updated NVRAM settings immediately after flashing a BIOS image.
The next section describes how to boot the DOS image.


**Booting the DOS image:** To boot the DOS image over the network, it first needs to be copied to software image’s /boot directory, and must be world-readable.


**Example**


cp flash.img /cm/images/default-image/boot/bios/flash.img
chmod 644 /cm/images/default-image/boot/bios/flash.img


An entry is added to the PXE boot menu to allow the DOS image to be selected. This can easily
be achieved by modifying the contents of /cm/images/default-image/boot/bios/menu.conf, which
is by default included automatically in the PXE menu. By default, one entry Example is included in the
PXE menu, which is however invisible as a result of the MENU HIDE option. Removing the MENU HIDE
line will make the BIOS flash option selectable. Optionally the LABEL and MENU LABEL may be set to an
appropriate description.
The option MENU DEFAULT may be added to make the BIOS flash image the default boot option. This
is convenient when flashing the BIOS of many nodes.


**Example**


LABEL FLASHBIOS

KERNEL memdisk

APPEND initrd=bios/flash.img

MENU LABEL ^Flash BIOS