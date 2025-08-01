# external-user-cert readonly spongebob --home=/home


If the home directory of spongebob is /home/spongebob, then the key files that are generated are
/home/spongebob/.cm/cert.key and /home/spongebob/.cm/cert.pem .
Assuming no other keys are used by cmsh, a cmsh session that runs as user spongebob with readonly
privileges can now be launched:


$ module load cmsh

$ cmsh


If other keys do exist, then they may be used according to the logic explained in item 2 on page 319.


**6.4.4** **Logging The Actions Of CMDaemon Users**
The following directives allow control over the logging of CMDaemon user actions.


 - CMDaemonAudit : Enables logging


 - CMDaemonAuditorFile : Sets log location


 - DisableAuditorForProfiles : Disables logging for particular profiles


Details on these directives are given in Appendix C.


**6.4 Tokens And Profiles** **321**


**6.4.5** **Creation Of Certificates For Nodes With** cm-component-certificate
The cm-component-certificate utility can be used to generate or update SSL certificates for components of services. The cluster administrator is not expected to use this utility because the cluster manager
manages the certificates without bothering the administrator about it during normal operations. If the
utilty is to be used, then it should be used with caution, to avoid failure in the components that use these
certificates.
One of the SSL client components for which this utility works is LDAP.
Options include setting a new CA and creating a new certificate or key for nodes.
Some examples of how it can be used are:


**LDAP PEM And Key Creation For A Standalone Node**
A standalone node (page 907) is a node that is not provisioned from the head node, but is configured to
boot from its own drive. A standalone node < _mynode_ - may have a PEM and key certificate created on
the head node with:


**Example**


[root@basecm11 ~]# cm-component-certificate --generate=< _mynode_ Certificate saved to ./ldap.{pem,key}

Done.


The certificates are saved to the working directory. They should be copied over manually to the
location of the LDAP certificates on _mynode_ . The nslcd daemon on mynode for RHEL8 (or the sssd
daemon for RHEL9) should then be restarted.


**LDAP PEM And Key Creation For A Regular Node**
If a node node001 that is provisioned has a lost or corrupted LDAP key or certificate, then replacements
for these can be made with:


**Example**


[root@basecm11 ~]# cm-component-certificate -n node001

Sending request to recreate certificates for 1 node to cmd on basecm11

[(38654705666, 1)] 1 0 0

1 certificates were successfully recreated

Done.


The ldap.{pem,key} files are automatically placed on node001, by default at the location specified
by the CMDaemon LDAPCertificate and LDAPPrivateKey directives (page 848).
The files /cm/node-installer/certificates/<node001-mac>/ldap.{pem,key} should be removed
on the head node.

The nslcd, sssd, and LDAP daemons should be restarted on node001, or more simply it can be
rebooted if it is not in use. The reboot replaces the ldap.{pem,key} files on the head node with the
newly-generated ones.


**LDAP CA Certificate Creation**
If a new LDAP CA certificate is needed, then a replacement can be made with:


[root@basecm11 ~]# cm-component-certificate --ca

Sending request to recreate the CA to cmd on basecm11

Done.


The following steps must be done manually:


  - If there is another head node, then the CA files, by default ca.pem and ca.key under /cm/local/
apps/openldap/etc/certs/, should be copied over the other head node.


**322** **User Management**


  - The key/PEM certificate files on all the nodes should be recreated using:
cm-component-certificate --allnodes


  - The old component PEM/key files for each regular node, ldap.pem and ldap.key, under the
node-installer directory of the head node(s), should be removed. These certificates are kept
under a directory named for the MAC address of the regular node, and follow the pattern:
/cm/node-installer/certificates/< _MAC address_ >/< _LDAP.{pem,key}_   

  - The node CA files, by default ca.pem and ca.key under /cm/local/apps/openldap/etc/certs/
should be copied to the nodes:


**Example**


[root@basecm11 ~]# export ldapcertdir="/cm/local/apps/openldap/etc/certs/"

for i in {01..12}

do

scp $ldapcertdir/ca.pem node0$i:/$ldapcertdir
scp $ldapcertdir/ca.key node0$i:/$ldapcertdir

done


  - The nslcd, sssd and LDAP daemons should be restarted on all nodes


  - CMDaemon should be restarted on the active head node


# **7**

### **Workload Management**

For clusters that have many users and a significant load, a workload manager (WLM) system allows a
more efficient use of resources to be enforced for all users than if there were no such system in place. This
is because without resource management, there is a tendency for each individual user to over-exploit

common resources.

When a WLM is used, the end user can submit a job to it. This can be done interactively, but it is
typically done as a non-interactive batch job.
The WLM assigns resources to the job, and checks the current availability as well as checking its
estimates of the future availability of the cluster resources that the job is asking for. The WLM then
schedules and executes the job based on the assignment criteria that the administrator has set for the
WLM system. After the job has finished executing, the job output is delivered back to the user.
Among the hardware resources that can be used for a job are GPUs. Installing CUDA software to
enable the use of GPUs is described in section 9 of the _Installation Manual_ . Configuring GPU settings
for BCM is described in section 3.16.2 of the _Administration Manual_ . Configuring GPU settings for an
individual WLM is described in the section on getting that particular WLM up and running.
The details of job submission from a user’s perspective are covered in the _User Manual_ .
Sections 7.1–7.5 cover the installation procedure to get a WLM up and running.
Sections 7.6 –7.7 describe how Base View and cmsh are used to view and handle jobs, queues and
node drainage.
Section 7.8 shows examples of WLM assignments handled by BCM.
Section 7.9 describes the power saving features of WLMs.
Section 7.10 describes cgroups, a resources limiter, mostly in the context of WLMs.
Section 7.11 describes WLM customizations for settings other than the common settings covered by
BCM.


**7.1** **Workload Managers Choices**


Some WLM packages are installed by default, others require registration from the distributor before
installation.

During cluster installation, a WLM can be chosen (figure 3.9 of the _Installation Manual_ ) for setting up.
The choices are:


 - **PBS** : An HPC job scheduler, originally developed at NASA, now developed by Altair. This is
integrated with BCM in these variants:


1. **PBS Professional** : A commercial variant, with commercial support from Altair. Available as:


**– PBS Professional version 2022**


2. **OpenPBS** : A community-supported variant. The variant was known as PBS Pro CE before
version 20. OpenPBS is available as:


**324** **Workload Management**


**– OpenPBS version 22.05**


**– OpenPBS version 23.06**


 - **Slurm** : Available as version 24.05, 24.11, or 25.05. Slurm is a free (GPL) job scheduler, with commercial support.


 - **LSF v10.1** : IBM Spectrum LSF (Load Sharing Facility) version 10.1, is a further development of
what used to be IBM Platform LSF.


 - **None** : For clusters that need no HPC job-scheduling.


The WLMs in the preceding list can also be chosen and set up later using the cm-wlm-setup tool
(section 7.3).
After installation, if there are no major changes in the WLM for updated versions of the workload
managers, then


  - WLMs that are packaged with BCM (Slurm, PBS) can have their packages updated using standard
package update commands ( yum update and similar). The installation and configuration of the
WLM from the updated packages is carried out as described later on in this chapter.


  - WLMs such as LSF that are installed by picking up software from the vendor can be updated by
following vendor guidelines.


**7.2** **Forcing Jobs To Run In A Workload Management System**


Another preliminary step is to consider forcing users to run jobs only within the WLM system. Having
jobs run via a WLM is normally a best practice.
For convenience, BCM defaults to allowing users to log in via ssh to a node, using the authorized
keys files stored in each users directory in /home (section 2.3.2). This allows users to run their processes
without restriction, that is, outside the WLM system. For clusters with a significant load this policy
results in a sub-optimal use of resources, since such unplanned-for jobs disturb any already-running
jobs.
Disallowing user logins to nodes, so that users have to run their jobs through the WLM system,
means that jobs are then distributed to the nodes only according to the planning of the WLM. If planning
is based on sensible assignment criteria, then resources use is optimized—which is the entire aim of a
WLM in the first place.


**7.2.1** **Disallowing User Logins To Regular Nodes Via** cmsh
The usernodelogin setting of cmsh restricts direct user logins from outside the WLM, and is thus one
way of preventing the user from using node resources in an unaccountable manner. The usernodelogin
setting is applicable to node categories only, rather than to individual nodes.
In cmsh the attribute of usernodelogin is set from within category mode:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% category use default

[basecm11->category[default]]% set usernodelogin onlywhenjob

[basecm11->category*[default*]]% commit


The attributes for usernodelogin are:


 - always (the default): This allows all users to ssh directly into a node at any time.


 - never : This allows no user other than root to directly ssh into the node.


**7.2 Forcing** **Jobs To Run In A Workload Management System** **325**


 - onlywhenjob : This allows the user to ssh directly into the node when a job is running on it. It
typically also prevents other users from doing a direct ssh into the same node during the job run,
since typically the WLM is set up so that only one job runs per node. However, an ssh session that
is already running is not automatically terminated after the job is done.


**–**
Some cluster administrators may wish to allow some special user accounts to override the
onlywhenjob setting, for example for diagnostic purposes. Before giving the details of how
to override the setting, some background explanation is probably useful:

The onlywhenjob setting works with the PAM system, and adds the following line to /etc/
pam.d/sshd on the regular nodes:


account required pam_bright.so


Nodes with the onlywhenjob restriction can be configured to allow a particular set of users
to access them, despite the restriction, by allowing them with the PAM system, as follows:
Within the software image < _node image_      - used by the node, that is under /cm/images/< _node_
_image_      -, the administrator can add the set of user accounts to the file etc/security/pam_
bright.d/pam_allow.conf . This file is installed in the software image with a chroot installation (section 9.4) of the cm-libpam package.

Groups of users can be allowed using the file etc/security/pam_bright.d/pam_allow_
group.conf .


Other adjustments to PAM configuration, such as the number of attempted logins and the
associated wait time per login, can be carried by editing the /etc/security/pam_bright.d/
cm-check-alloc.conf file.

The image can then be updated to allow the users, by running the imageupdate command in
cmsh (section 5.6.2), or by clicking the Update node option in Base View (section 5.6.3).


**7.2.2** **Disallowing User Logins To Regular Nodes Via Base View**
In Base View, user node login access is set via a category setting, for example for the default category
via the navigation path in figure 7.1:
Grouping - Categories[default] - Edit - Settings - User node login


Figure 7.1: Disallowing user logins to nodes via Base View


**326** **Workload Management**


**7.2.3** **Disallowing Other User Processes Outside Of Workload Manager User Processes**
Besides disabling user logins, administrators may choose to disable interactive jobs in the WLM as an
additional measure to prevent users from starting jobs on other nodes.
Administrators may also choose to set up scripts that run after job execution. Such scripts can terminate user processes outside the WLM, as part of a policy, or for general administrative hygiene. These
are Epilog scripts and are part of the WLM.
The WLM documentation has more on configuring these options.


**7.2.4** **High Availability By Workload Managers**
NVIDIA Base Command Manager uses the existing built-in high availability (HA) functionalities of
workload managers as much as possible. A double server HA configuration with the existing builtin HA functionality can be carried out using the cm-wlm-setup utility (section 7.3), or using the Base
View HA wizard (section 7.4.1). The built-in functionality makes use of the primary WLM server and
secondary WLM server, which are placed on separate nodes.
The HA configuration aspect (section 15.1.3) in this case means that a WLM server role is assigned
to both the WLM primary and the WLM secondary nodes. These primary WLM and secondary WLM
servers can then:


  - both be on head nodes,


  - both be on regular (compute) nodes


It is not possible to configure a mixed setup—that is with one head node and one regular node—for the
WLM servers on an HA setup.
In a non-HA cluster, the WLM primaryserver value is set to the head node by default.


**Example**


[head->wlm[slurm]]% get primaryserver

head


This is because NVIDIA Base Command Manager always configures the primary WLM server on the
primary cluster head node.
If both the head nodes are configured with the WLM server roles, then the WLM primaryserver
value is set to the primary cluster head node. This is because NVIDIA Base Command Manager always
configures the primary WLM server on the primary cluster head node, and the backup WLM server on
the secondary head node.


**Example**


[head1->wlm[slurm]]% get primaryserver

head1

[head1->wlm[slurm]]% exit

root@head1:~# ssh head2 "cmha makeactive"

...

...[ _logging into the newly active head node, and checking where the primary server is:_ ]...

[head2->wlm[slurm]]% get primaryserver

head1


If the parameter primaryserver is unset in wlm mode, and the Slurm server role is assigned to the
head nodes, then the slurmctld service is always started on both head nodes. During a failover, the
Slurm configuration is regenerated and both slurmctld services are restarted. The primary slurmctld
is always on the active head node.
If two regular nodes are configured with the WLM server roles instead, then in the cluster entity
configuration the primaryserver parameter is set to one of the compute nodes.


**7.2 Forcing** **Jobs To Run In A Workload Management System** **327**


The cluster primary head node and the WLM primary server should not be confused. In particular,
the active cluster head node and active workload manager server are not necessarily the same for the
case of the Slurm, PBS Professional, or LSF workload managers. For these, if the passive cluster head
node becomes an active cluster head node without a crash, then this does not trigger a passive WLM
server on the newly active head node to also become an active WLM server. Thus, the WLM server can
be active on a passive head node, and vice versa, because the WLM primary server is independent of
the cluster primary head node.


**Slurm High Availability,** scontrol takeover **And** slurmstartpolicy
This section considers some Slurm high availability issues on running scontrol takeover with BCM
integration.


**Logical steps during the Slurm takeover between head nodes:** Slurm high availability normally waits
a short while with moving its control activity over to a passive head node that has just been made active.
After a short delay, the Slurm failover algorithm is followed so that the Slurm controller ( slurmctld )
takes over operations on the newly active head node.
Slurm can speed up takeover by running scontrol takeover from the Bash shell on the node with
the secondary slurmctld . Running scontrol takeover stops the primary slurmctld and triggers the
Slurm failover algorithm.
This can be useful if the administrator wants to carry out maintenance on the usually active head
node. Carrying out the takeover lets the Slurm service remain available, and stops the Slurm primary
controller following the newly active head node.
The logic on how this works in BCM is:


1. The production state starts with


    - an active primary


    - a passive secondary


    - the primary head node set up as the primary Slurm controller


2. the administrator runs cmha makeactive on the secondary passive. This causes the following to
happen:


   - scontrol takeover is run by CMDaemon on the secondary passive


    - CMDaemon goes into the passive state on the primary node, and slurmctld on the primary
node stops


    - CMDaemon goes into the active state on the secondary node, and slurmctld on the secondary node starts


3. there is no interruption in Slurm services, because with scontrol takeover CMDaemon has
forced the backup slurmctld to take over


4. the administrator can now carry out maintenance on the primary (now passive) head node


5. once maintenance has been completed, the administrator can optionally reboot the primary (passive) head node, and then make it active again with cmha makeactive to get back to the original
production state


The problem with the preceding logic is that by default BCM automatically restarts a stopped
slurmctld that it notices. This means that the results of scontrol takeover in steps 2 and 3 are unknown if carried out manually. That is, it is not practical to run the scontrol takeover command directly from Bash because it is possible to unintentionally configure the primary and backup slurmctld
with an incorrect status.

To deal with this problem cleanly, CMDaemon provides the slurmctldstartpolicy parameter, described next.


**328** **Workload Management**


**The** slurmctldstartpolicy **parameter and Slurm takeover behavior:** The slurmctldstartpolicy
parameter can take the following values to decide the slurmctld behavior during scontrol takeover :


 - TAKEOVER : The default value on an HA cluster.


 - ALWAYS : The default value on a non-HA cluster.


 - ACTIVEONLY : Useful only if /cm/shared is not mounted on both head nodes at the same time. For
example, as in DAS (Direct Attached Storage), which should never be used anyway for shared
storage in a production system.


1. If within NVIDIA Base Command Manager, in the SlurmServerRole, the slurmctldstartpolicy
parameter is set to TAKEOVER, then disabling the automatic restart of the slurmctld service is un
necessary:


[root@basecm11 ~]# cmsh

[basecm11-]% configurationoverlay

[basecm11-]>configurationoverlay]% use slurm-server

[basecm11->configurationoverlay[slurm-server]]% roles

[basecm11->configurationoverlay[slurm-server]->roles]% use slurmserver

[basecm11->configurationoverlay[slurm-server]->roles[slurmserver]]% set slurmctldstartpolicy TAKEOVER

[basecm11->configurationoverlay*[slurm-server*]->roles*[slurmserver*]]% commit


The setting value can be cleared with:


[basecm11->configurationoverlay[slurm-server]->roles[slurmserver]]% set slurmctldstartpolicy ALWAYS

[basecm11->configurationoverlay*[slurm-server*]->roles*[slurmserver*]]% commit


2. If cm-wlm-setup installs Slurm on an HA cluster, then the slurmctldstartpolicy parameter can
be set in one of the TUI screens during the session. Before HA is configured, the parameter has
a default value of ALWAYS . After HA is configured it has a default value of TAKEOVER . The default
value of TAKEOVER causes prefailoverscript in the failover submode (section 15.4.6) to take the
value /cm/local/apps/cmd/scripts/slurm.takeover.sh


3. If cm-wlm-setup installs Slurm on a non-HA cluster, then the prefailoverscript parameter must
be set within the failover submode of partition mode:


[basecm11->partition[base]->failover]% set prefailoverscript /cm/local/apps/cmd/scripts/slurm.takeover.sh

[basecm11->partition*[base*]->failover*]% commit


This ensures that the active head node is taken over by Slurm during a change of the active head
node.


The takeover is temporary. If the head node which has the Slurm primary slurmctld on it is
restarted, or if the service itself is restarted manually, then the primary slurmctld takes back its role, as
per Slurm documentation.
For a Slurm cluster with a single slurmctld, where the Slurm server role is assigned to a single compute node or the BCM cluster has only one head node, the parameter slurmctldstartpolicy should be
set to ALWAYS, which is the default.


Table 7.2.4 shows what slurmctld does when the slurmctldstartpolicy parameter is set to
TAKEOVER and when in SlurmWlmCluster the parameter primaryserver is set. The detailed behavior
per head node depends on whether the head nodes are active or primary:


**7.3 Installation Of Workload Managers** **329**


**Node** **Is** slurmctldstartpolicy **Active node?** **Slurm primary** slurmctld
**pair** **TAKEOVER?** **node?** **starts?**


Head001 no   -   - yes
Head002 no   -   - yes


Head001 yes yes yes yes
Head002 yes no no yes


Head001 yes yes no yes
Head002 yes no yes no


Head001 yes no yes no
Head002 yes yes no yes


Head001 yes no no yes
Head002 yes yes yes yes


   - any value of yes or no

Table 7.2.4 slurmctldstartpolicy parameter and slurmctld


**7.3** **Installation Of Workload Managers**


Normally the administrator selects a WLM to be used during BCM installation (figure 3.9 of the _Installa-_
_tion Manual_ ). A WLM may however also be added and configured after BCM has been installed, using
cm-wlm-setup, or the Base View WLM wizard.
With most other objects, BCM front ends— cmsh and Base View—can be used to create a new object
from scratch, or can clone a new object from another existing object. However, the front ends cannot
do this for a WLM object. An attempt to create or clone a new WLM object via cmsh or Base View is
prohibited by the front ends, because there are many pitfalls possible in configuration.
A new WLM object, and WLM instance, can therefore only be installed via cm-wlm-setup, the Base
View WLM wizard, or by selecting a WLM during the initial BCM installation.


**7.3.1** **Running** cm-wlm-setup **In CLI Mode**
The recommended way to run the cm-wlm-setup utility is without options or arguments, in which case
a TUI dialog starts up. A TUI session run with cm-wlm-setup is covered in section 7.3.2.
However, the cm-wlm-setup utility can alternatively be used in a non-GUI, command-line, mode,
with options and arguments. The utility has the following usage:


[root@basecm11 ~]# cm-wlm-setup -h
usage: Workload manager setup cm-wlm-setup [-c <config_file>]

[--setup | --disable]

[--wlm <name>]

[--server-nodes SERVER_NODES]

[--server-primary SERVER_PRIMARY]

[--server-overlay-name SERVER_OVERLAY_NAME]

[--server-overlay-priority SERVER_OVERLAY_PRIORITY]

[--client-categories CLIENT_CATEGORIES]

[--client-nodes CLIENT_NODES]

[--client-overlay-name CLIENT_OVERLAY_NAME]

[--client-overlay-priority CLIENT_OVERLAY_PRIORITY]

[--client-slots <slots>]

[--submit-categories SUBMIT_CATEGORIES]

[--submit-nodes SUBMIT_NODES]

[--submit-overlay-name SUBMIT_OVERLAY_NAME]

[--submit-overlay-priority SUBMIT_OVERLAY_PRIORITY]


**330** **Workload Management**


[--wlm-cluster-name WLM_CLUSTER_NAME]

[--reboot] [--reset-cgroups]

[--yes-i-really-mean-it]

[--archives-location <path>]

[--license <license>] [--purge]

[--accounting-overlay-name ACCOUNTING_OVERLAY_NAME]

[--accounting-overlay-priority ACCOUNTING_OVERLAY_PRIORITY]

[--with-pyxis]

[--add-pyxis]

[--reinstall-pyxis]

[--remove-pyxis]

[--pyxis-data-directory <path>]

[--nvidia-gpus NVIDIA_GPUS] [-v]

[--no-distro-checks] [--json]

[--output-remote-execution-runner]

[--on-error-action {debug,remotedebug,undo,abort}]

[--skip-packages]

[--min-reboot-timeout <reboot_timeout_seconds>]

[--allow-running-from-secondary]

[--dev] [-h]


The help output from running cm-wlm-setup -h continues on beyond the preceding text output,
and presents more options.
These options can be grouped as follows:


**Optional Arguments**

 - --setup : Helps set up a server, enable roles, and create the default queues/partitions


 - --disable : Disable WLM services


 - -h, --help : Displays the help screen


**Common Arguments**

 - -c < _YAML configuration file_  - : Loads a runtime configuration for plugins, from a YAML configuration file.


**Options For Installing Or Managing A WLM**

 - --wlm < _WLM name_  - : Specifies which WLM is to be set up. Choices for < _WLM name_  - are:


**–**
openpbs


**–**
pbspro


**–** slurm


**–** lsf


 - --wlm-cluster-name < _WLM cluster name_  - : Specifies the name for the new WLM cluster that is to be
set up.


 - --reboot : Reboot after install


**Server Role Settings**

 - --server-nodes < _server nodes_  - : Sets the server roles of the WLM to the value set for < _server nodes_  -,
which is a comma-separated list of nodes. Default value: HEAD, which is a reserved name for the
head node.


 - --server-primary < _primary server_  - : Sets the hostname used for the primary server to < _primary_
_server_    - . Default name: HEAD .


**7.3 Installation Of Workload Managers** **331**


 - --server-overlay-name < _server overlay name_  - : Sets the server role configuration overlay name to
< _server overlay name_   - . Default name: < _WLM name_ >-server, where < _WLM name_   - is the name specified in the --wlm option.


 - --server-overlay-priority < _server overlay priority_  - : Sets the server role configuration overlay priority to < _server overlay priority_    - . Default value: 500 .


**Client Role Settings**

 - --client-categories < _client categories_  - : Sets the client roles of the WLM to the value set for < _client_
_categories nodes_    -, which is a comma-separated list of node categories. Default value: default .


 - --client-nodes < _client nodes_  - : Sets the client roles of the WLM to the value set for < _client nodes_  -,
which is a comma-separated list of nodes. No value set by default.


 - --client-overlay-name < _client overlay name_  - : Sets the client role configuration overlay name to
< _client overlay name_   - . Default name: < _WLM name_ >-client, where < _WLM name_   - is the name specified in the --wlm option.


 - --client-overlay-priority < _client overlay priority_  - : Sets the client role configuration overlay priority to < _client overlay priority_    - . Default value: 500 .


 - --client-slots < _slots_  - : Sets the number of slots on the client to < _slots_  - .


**Submit Role Settings**

 - --submit-categories < _submit categories_  - : Sets the submit roles of the WLM to the value set for
< _submit categories nodes_   -, which is a comma-separated list of node categories that are submit nodes.
Default value: default .


 - --submit-nodes < _submit nodes_  - : Sets the submit roles of the WLM to the value set for < _submit_

_nodes_   -, which is a comma-separated list of submit nodes. No value set by default.


 - --submit-overlay-name < _submit overlay name_  - : Sets the submit role configuration overlay name to
< _submit overlay name_   - . Default name: < _WLM name_ >-submit, where < _WLM name_   - is the name
specified in the --wlm option.


 - --submit-overlay-priority < _submit overlay priority_  - : Sets the submit role configuration overlay priority to < _submit overlay priority_    - . Default value: 500 .


**Disable Options**

 - --reset-cgroups : Disable joining cgroup controllers with systemd setting JoinControllers


 - --yes-i-really-mean-it : Required for additional safety


**Workload Manager Specific Options**

 - --archives-location < _path_  - : Set the directory path for the archive files, only for LSF. This parameter is mandatory for LSF installation.


 - --license < _path_  - : Set the path to the PBSPro, or LSF license.


 - --purge : Remove the directories on disable, for LSF.


**Slurm Accounting Role Settings**

 - --accounting-overlay-name < _accounting overlay name_  - : Sets the accounting role configuration overlay


 - --accounting-overlay-priority < _accounting overlay priority_  - : Sets the accounting role configuration overlay priority to < _accounting overlay priority_    - . Default value: 500 .


**332** **Workload Management**


**Slurm Pyxis Settings**

 - --add-pyxis : Add Pyxis to an existing cluster


 - --reinstall-pyxis : Reinstall or upgrade Pyxis on all the clusters using it


 - --remove-pyxis : Remove Pyxis from an existing cluster


 - --with-pyxis : Enable Pyxis


 - --pyxis-data-directory < _path_  - : Sets directory where images will be stored


**Slurm GPU Settings**

 - --nvidia-gpus < _NVIDIA GPUs specification_  - : Sets the NVIDIA GPUs that will be used in the configuration, specifying type and number of GPUs. For example: --nvidia-gpus=A100:4


 - --gpu-client-nodes < _NVIDIA GPU client nodes_  - : Sets a comma-separated list of nodes assigned to
the GPU overlay.


 - --gpu-client-categories < _NVIDIA GPU client categories_  - : Sets a comma-separated list of node categories assigned to the GPU overlay.


**Advanced Options**

 - -v, --verbose : This displays a more verbose output. It can be helpful in troubleshooting.


 - --no-distro-checks : Disables distribution checks based on ds.json.


 - --json : Use json formatting for logs printed to STDOUT.


 - --output-remote-execution-runner : Format output for CMDaemon.


 - --on-error-action {debug,remotedebug,undo,abort} : Upon encountering a critical error, instead
of asking the user for choice, the setup will do the selected action.


 - --skip-packages : Skip the stages which install packages. Requires packages to be already installed.


 - --min-reboot-timeout < _timeout_  - : How long to wait for nodes to finish reboot, in seconds. Minimum value: 300 . Default value: 300 .


 - --allow-running-from-secondary : Allow the wizard to be run from the secondary when it is the
active head node.


 - --dev : Enables additional command line arguments for developers.


**7.3.2** **Running** cm-wlm-setup **As A TUI**
Running cm-wlm-setup with no options and with no arguments brings up a TUI screen (figure 7.2).


Figure 7.2: cm-wlm-setup TUI initial screen


**7.3 Installation Of Workload Managers** **333**


**Express Installation**
The Setup (Express) menu option allows the administrator to select the workload manager in the next
screen (figure 7.3), and to install it with a minimal number of configuration steps. If it has already been
installed, but disabled via cm-wlm-setup, then it can also be re-enabled, instead of installed from scratch.


Figure 7.3: cm-wlm-setup TUI WLM selection screen


**Step-by-step Installation**
If the Setup (Step By Step) menu option is chosen instead of the express option, then this also allows
the administrator to select the workload manager in figure 7.3. But after selection, there are a number
of extra configuration steps that can be carried out which are not available in the express configuration.
Guidance is given for these extra steps, and sensible default values are already filled in for many options.
One part of the step-by-step session involves assigning the WLM client role to the compute nodes of
the cluster. Only the non-GPU compute nodes should be assigned the (standard, non-GPU) WLM client
role. The GPU compute nodes are assigned a _GPU_ WLM client role in the section of the TUI wizard that
deals with GPU configuration.
The WLM client role is assigned to the entire category—the default category— of non-head nodes
by default (figure 7.4):


Figure 7.4: Slurm with cm-wlm-setup : WLM Client role category configuration screen


The WLM client role can be assigned to selected nodes only by setting the default category checkbox
to blank, and then selecting the non-GPU nodes in the following screen. For example, as illustrated in
figure 7.4, where the standard, non-GPU nodes are node002 and node003 :


**334** **Workload Management**


Figure 7.5: Slurm with cm-wlm-setup : WLM client role node configuration screen


**GPU Configuration Screens**
The GPU configuration screens are extra steps available during a Setup (Step By Step) session. The
GPU configuration steps are discussed summarily in the quickstart section for GPUs, on page 13 of the
_Installation Manual_ .

The GPU configuration steps are covered in this section in more detail:
After configuring the WLM server, WLM submission and WLM client roles for the nodes of the
cluster, a screen that asks if GPU resources should be configured is displayed (figure 7.6):


Figure 7.6: Slurm With cm-wlm-setup : GPU Configuration Entry Screen


Choosing yes means that some extra GPU configuration screens are presented. These are screens
that allow:


  - the configuration overlay (section 2.1.6) name to be set for the GPU WLM clients. By default the
name is set to slurm-client-gpu .


  - a GPU WLM client role to be assigned to a category, if, for example, all the GPU nodes have been
given their own category.


  - the GPU WLM client role to be assigned to individual nodes instead of to a category.


  - a configuration overlay priority to be set for a GPU WLM client role. By default, this has a value
of 450 .


  - automatic GPU detection, with the following options:


**–**
Automatic NVIDIA GPU configuration


**–**
Automatic AMD GPU configuration


**–**
Manual GPU configuration


**–**
Skip


**Slurm Accounting Database Configuration**
In the step-by-step configuration for the Slurm WLM, after the server and client parameters have been
set, the Slurm accounting database configuration can be set.
This requires setting:


  - one or two accounting nodes


  - a primary accounting node


**7.3 Installation Of Workload Managers** **335**


All nodes must be reachable from slurmctld .

The accounting nodes can be set with the Select accounting nodes screen (figure 7.7):


Figure 7.7: cm-wlm-setup selection of accounting nodes


Head nodes and compute nodes cannot be mixed for the accounting nodes. If two accounting nodes
are set, then the slurmdbd high availability configuration is automatically set up.
The primary accounting node—that is, the node that is AccountingStorageHost in slurm.conf —can
then be set in the Select the primary accounting server node screen (figure 7.8):


Figure 7.8: cm-wlm-setup selection of primary accounting node


The other accounting node is automatically set to be AccountingStorageBackupHost .
The type of node on which the slurmdbd database runs can then be set (figure 7.9):


Figure 7.9: cm-wlm-setup selection of the type of node on which the Slurm accounting database runs


  - If Use accounting node is selected, then the database is stored on the primary accounting node


  - If Select cluster node is selected, then the next screen allows the selection of the BCM node on
which the database is to be installed (figure 7.10)


Figure 7.10: cm-wlm-setup Selection of host where the Slurm accounting database used by slurmdbd is
stored


  - If Select external node is selected, then a non-BCM hostname is asked for, and the cluster ad

**336** **Workload Management**


ministrator is responsible for the installation and configuration of the DBMS


Modifying the settings after installation is discussed on page 373.


**Disabling An Installation**
The Disable option in figure 7.2 allows the administrator to disable an existing instance.


**Summary Screen**
The screen that appears after the configuration steps are completed, is the Summary screen (figure 7.11).
This screen allows the configuration to be viewed, saved, or saved and deployed.


Figure 7.11: cm-wlm-setup TUI summary screen


If deployment is carried out, then several screens of output are displayed. After the deployment is
completed, the log file can be viewed at /var/log/cm-wlm-setup.log .


**7.3.3** **Installation And Configuration Of Enroot And Pyxis With Slurm To Run Containerized**
**Jobs**

**What Is Enroot?**

[As the README file for Enroot says, Enroot is an open source tool to turn container images into un-](https://github.com/NVIDIA/enroot/blob/master/README.md)
privileged sandboxes. Enroot can be thought of as an enhanced unprivileged chroot. It uses user and
mount namespaces, as well as other modern kernel features, in order to create such sandboxes. It
uses the same underlying technologies as containers, but removes much of the isolation that they inherently provide, while preserving filesystem separation. Further details on Enroot can be found at
[https://github.com/NVIDIA/enroot](https://github.com/NVIDIA/enroot) .
Enroot can be used with different workload managers, but for now only Slurm has been tightly
integrated.


**What Is Pyxis?**
Pyxis ( [https://github.com/NVIDIA/pyxis](https://github.com/NVIDIA/pyxis) ) is a SPANK plugin for Slurm. SPANK (Slurm Plug-in architecture for Node and job (K)control, man spank.8 ) is a generic interface for job launch code control in
Slurm. The Pyxis plugin requires the Enroot utility, and allows the user’s jobs to be executed seamlessly
over Enroot in unprivileged containers. The plugin enables the Slurm submission utilities to provide
container-related command line options.


**Enroot And Pyxis Packages**
BCM provides two Enroot package flavors: _standard_ and _hardened_ . The standard binaries are compiled
as follows:


  - Open file descriptors are inherited


  - Spectre variant 2 (IBPB/STIBP) mitigations are disabled


**7.3 Installation Of Workload Managers** **337**


  - Spectre variant 4 (SSBD) mitigations are disabled


[As a rule of thumb: the hardened flavor is slightly more secure but suffers a larger overhead.](https://github.com/NVIDIA/enroot/blob/master/doc/installation.md)


  - The standard packages that are installed by default on new clusters are:


**–** enroot : provides the main utility and helper files.


**–** enroot+caps : a nearly empty package which runs a post-installation script to grant extra
capabilities to unprivileged users. This allows them to import and convert container images.


**–**
pyxis-sources : installs a tarball with the Pyxis plugin source files. The tarball is used by
cm-wlm-setup to compile the Pyxis plugin on a cluster. The version of the package (section 9.1), found using yum info pyxis-sources or apt-cache show pyxis-sources, implies the
Pyxis source version that is provided. For example: pyxis-sources-0.20.0-[...].rpm provides the Pyxis source for version 0.20.0.


  - The hardened packages that can be installed from the BCM repositories to replace the standard
enroot and enroot+caps are:


**–** enroot-hardened : provides hardened main utility and helper files.


**–**
enroot-hardened+caps : Provides extra capabilities to unprivileged users so that they can
import and convert containers themselves.


The package pyxis-sources installs the tarball at /cm/local/apps/slurm/var/pyxis/
pyxis-sources.tar.gz . If the administrator needs a version of Pyxis other than the one provided by
the package, then the archive can be replaced with a source tarball of the same name.


**How Are Enroot And Pyxis Set Up In BCM?**
Pyxis and Enroot can be set up by the administrator by choosing the appropriate options when Slurm
is set up. In order to choose the appropriate options, cm-wlm-setup can be run in step-by-step mode
(page 333). Alternatively, Pyxis-related command line options can be specified for the cm-wlm-setup
arguments --add-pyxis and --reinstall-pyxis .
The step-by-step mode eventually presents a screen where the Pyxis setup can be enabled via a
plugin:


Figure 7.12: cm-wlm-setup Pyxis setup screen


The Pyxis screen is available for RHEL8-based systems and Ubuntu 20 and beyond. Older systems
are not supported.
If the plugin is enabled in the Pyxis setup screen, then cm-wlm-setup installs the enroot and
enroot+caps packages from [https://github.com/NVIDIA/enroot/releases](https://github.com/NVIDIA/enroot/releases) into the software images
where the Slurm client role is to be assigned. The cm-wlm-setup uitility also installs them directly on
the head node if the head node was selected to run jobs. Pyxis sources are downloaded from GitHub,
compiled with the installed Slurm, and installed in the appropriate Slurm directory.
If the administrator enables the Pyxis plugin, then a new screen with Enroot settings is shown:


**338** **Workload Management**


Figure 7.13: cm-wlm-setup Enroot settings screen


The Enroot settings have reasonable default values. The administrator can change these:


 - Share raw images among users and nodes : If enabled, then the raw container image is shared
among users and nodes, and the administrator must ensure that the cache directory is shared
among all the compute nodes. Enabling the option disables the creation of a UID subdirectory by
the Enroot prolog script.


The following points about implementing Enroot cache sharing should be considered by the administrator:


**–**
Enabling the checkbox for the option normally changes the default value of the Enroot cache
directory, as defined in the TUI in the Cache directory field, to ${XDG_CACHE_HOME}/enroot .
This field is normally evaluated by the Enroot installation to the home directory of the user:


~/.cache/enroot

when a job is executed.
The default value can also be changed in the TUI to any shared directory. If the specified
directory does not exist, then cm-wlm-setup creates it with Unix directory permissions set to
chmod 00777 [, which allows all users to share container images in the cache with each other](https://www.gnu.org/software/coreutils/manual/html_node/Directory-Setuid-and-Setgid.html)
on all the nodes. The extra 0 [prefix is a non-POSIX-compliant GNU/Linux extension that](https://www.gnu.org/software/coreutils/manual/html_node/Directory-Setuid-and-Setgid.html)
[clears the SUID and SGID bits so that users do not get elevated privileges simply through](https://www.gnu.org/software/coreutils/manual/html_node/Directory-Setuid-and-Setgid.html)
[sharing the images.](https://www.gnu.org/software/coreutils/manual/html_node/Directory-Setuid-and-Setgid.html)


**–**
Restrictions can be placed on the ability of regular users to share images and to create files
in the cache, by setting more restrictive permissions for the directory manually, after the
cm-wlm-setup run.

For example, the permissions can be set to 00770, while the ownership group of the directory
is changed to a group with all the Pyxis users in it. In this case, only the users within the
Pyxis users group can create the image layers in the cache.


**–**
An alternative to cache sharing of images among users and nodes is to save Squashfs images
in a shared directory, outside the cache. Then the users can specify a full path to a shared
Squashfs image on the cluster in the srun/sbatch command line. In this case there is no need
to share the cache among the nodes, as the Squashfs images are not copied over to cache
before execution.


Only the administrator should have access to updating the image.


 - Share unpacked container images among nodes : Enables sharing of unpacked container images (image filesystems) among nodes. A user job can modify the filesystem, so it is not recommended to share this directory among users.


Enabling the option disables removal of the Enroot data directory, if the container name is specified. This allows a user to keep the container filesystem between jobs run by the user. It is up to
the user or the administrator to clean up the data directory if the option is enabled.


**7.3 Installation Of Workload Managers** **339**


If the data directory is shared among nodes, then it is up to a user to ensure that the container
filesystem is unpacked at least once before real jobs start. Otherwise, a race condition is possible
when the images are extracted simultaneously on several nodes.


 - Cache directory : Path to the cache directory where raw container image layers are stored.


If the directory is not shared, then the Slurm prolog script creates a subdirectory with a name that
is the job user ID, while epilog cleans up that subdirectory. If the directory is shared, then neither
prolog nor epilog touches the directory.


 - Data directory : Directory where the container filesystems (unpackaged images) are stored. If
the directory is shared, then the epilog script checks if the container name is specified for the job,
and skips removal of the container subdirectory.


 - Runtime directory : A working directory with temporary files created by Enroot.


When Pyxis is set up, cm-wlm-setup also prepares the following configuration files for the compute
nodes:


 - /etc/enroot/enroot.conf : This is a symlink to /cm/shared/apps/slurm/etc/enroot.conf . The
configuration file provides reasonable default settings that allows Enroot to be used by many users.
Important settings in the file are:


**–** ENROOT_RUNTIME_PATH : working directory for enroot, created per user. Default value: /run/
enroot/runtime/ $(id -u)


**–** ENROOT_CACHE_PATH : directory where container layers are stored. Default value: /run/enroot/
cache/ $(id -u)


**–**
ENROOT_DATA_PATH : directory where the filesystems of running containers are stored. Default
value: /run/enroot/data/ $(id -u)


**–**
ENROOT_SQUASH_OPTIONS : options passed to mksquashfs to produce container images. Default value: -noI -noD -noF -noX -no-duplicates


**–** ENROOT_MOUNT_HOME : mount the current user’s home directory by default. Default value: yes .


The administrator can change the symlink, or replace the file with a customized enroot.conf, if
other values are preferred.


 - /etc/sysctl.d/80-enroot.conf : symlink to /cm/shared/apps/slurm/etc/enroot-sysctl.conf .
The file tunes sysctl parameters for Enroot.


 - /cm/local/apps/slurm/var/prologs/50-prolog-enroot.sh : symlink to /cm/shared/apps/
slurm/prologs/prolog-enroot.sh . This is the slurmd prolog that creates appropriate directories, with appropriate user permissions, that are used by Enroot.


 - /cm/local/apps/slurm/var/epilogs/50-epilog-enroot.sh : symlink to /cm/shared/apps/
slurm/epilogs/epilog-enroot.sh . Cleans the user directories used by Enroot.


When cm-wlm-setup finishes its Pyxis configuration run, then there is no need for the nodes to be
rebooted. The plugin works immediately.
The new Slurm submission command option names start with either --container or --no-container .
The full list of options can be displayed with the --help option. For example:


**Example**


**340** **Workload Management**


[user@basecm11 ~]$ srun --help | grep container

--container Path to OCI container bundle

--container-image=[USER@][REGISTRY#]IMAGE[:TAG]|PATH

[pyxis] the image to use for the container
--container-mounts=SRC:DST[:FLAGS][,SRC:DST...]

[pyxis] bind mount[s] inside the container. Mount

--container-workdir=PATH

[pyxis] working directory inside the container
--container-name=NAME [pyxis] name to use for saving and loading the

container on the host. Unnamed containers are

containers are not. If a container with this name

already exists, the existing container is used and
--container-save=PATH [pyxis] Save the container state to a squashfs
--container-mount-home [pyxis] bind mount the user's home directory.

--no-container-mount-home

--container-remap-root [pyxis] ask to be remapped to root inside the

container. Does not grant elevated system

--no-container-remap-root

[pyxis] do not remap to root inside the container
--container-entrypoint [pyxis] execute the entrypoint from the container

--no-container-entrypoint

container image
--container-writable [pyxis] make the container filesystem writable
--container-readonly [pyxis] make the container filesystem read-only


**Simple installation validation:** The simplest way to validate the Pyxis/Enroot setup after Slurm setup
is to try out an srun command:


**Example**


[user@basecm11 ~]$ module load slurm

[user@basecm11 ~]$ srun --container-image=ubuntu grep PRETTY /etc/os-release

pyxis: importing docker image: ubuntu

PRETTY_NAME="Ubuntu 24.04.2 LTS"


**A more thorough installation validation:** In order to perform a more thorough test of Pyxis/Enroot,
an NCCL-based test can be used. NCCL is the NVIDIA Collective Communications Library ( [https:](https://docs.nvidia.com/deeplearning/nccl)
[//docs.nvidia.com/deeplearning/nccl](https://docs.nvidia.com/deeplearning/nccl) ), which is a library of multi-GPU collective communication
primitives. The test can be found at [https://github.com/NVIDIA/nccl-tests](https://github.com/NVIDIA/nccl-tests) . A prebuilt container
image, with the NCCL test already installed, can be started as shown in the example that follows.
It should be noted that running a multi-tenant cluster with all the export flags enabled as in the
example may compromise security. It is therefore not recommended as a standard configuration.


**Example**


[user@basecm11 ~]$ module load slurm

[user@basecm11 ~]$ srun --export="NCCL_DEBUG=INFO,NCCL_IB_DISABLE=1,PMIX_MCA_gds=hash" -N 2 _\_
--ntasks-per-node=1 --gpus-per-task=1 --mpi=pmix --container-image=deepops/mpi-nccl-test _\_
/nccl_tests/build/all_reduce_perf -b 1M -e 4G -f 2 -g 1


pyxis: imported docker image: deepops/mpi-nccl-test
pyxis: imported docker image: deepops/mpi-nccl-test
# nThread 1 nGpus 1 minBytes 1048576 maxBytes 4294967296 step: 2(factor) warmup iters: 5 iters: 20 validation: 1

#


**7.3 Installation Of Workload Managers** **341**


# Using devices

# Rank 0 Pid 175945 on node001 device 0 [0x00] Tesla V100-SXM3-32GB