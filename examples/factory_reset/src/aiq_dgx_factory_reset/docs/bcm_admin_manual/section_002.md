# **1**

### **Introduction**

**1.1** **NVIDIA Base Command Manager Functions And Aims**


NVIDIA Base Command Manager (often shortened to BCM) contains tools and applications to facilitate
the installation, administration, and monitoring of a cluster. In addition, BCM aims to provide users
with an optimal environment for developing and running applications that require extensive computational resources.


**1.2** **The Scope Of The Administrator Manual (This Manual)**


The _Administrator Manual_ covers installation, configuration, management, and monitoring of BCM,
along with relevant background information to help understand the topics covered.


**1.2.1** **Installation**

Installation can generally be divided into parts as follows, with some parts covered by the _Administrator_
_Manual_, some by the _Installation Manual_, and some by other manuals:


 - **Initial installation of BCM:** This is covered in the _Installation Manual_, which gives a short introduction to the concept of a cluster along with details on installing BCM onto the head node. The
_Installation Manual_ is therefore the first manual an administrator should usually turn to when getting to work with BCM for the first time. The _Administrator Manual_ can be referred to as the main
reference resource once the head node has had BCM installed on it.


 - **Provisioning installation:** This is covered in the _Administrator Manual_ . After the head node has
had BCM installed on it, the other, regular, nodes can (network) boot off it and provision themselves from it with a default image, without requiring a Linux distribution DVD themselves. The
network boot and provisioning process for the regular nodes is described in detail in Chapter 5.


In brief, provisioning installs an operating system and files on a node. This kind of installation
to a regular node differs from a normal Linux installation in several ways. An important difference is that content that is put on the filesystem of the regular node is normally overwritten by
provisioning when the regular node reboots.


 - **Post-installation software installation:** The installation of software to a cluster that is already
configured and running BCM is described in detail in Chapter 9 of this manual.


 - **Third-party software installation:** The installation of software that is not developed as part of
BCM, but is supported as a part of BCM. This is described in detail in the _Installation Manual_ .


 - **Cloudbursting, and Edge** : these are integrated as part of BCM in various ways. These have their
own deployment procedures and have separate manuals.


**22** **Introduction**


**1.2.2** **Configuration, Management, And Monitoring Via BCM Tools And Applications**
The administrator normally deals with the cluster software configuration via a front end to BCM. This
can be GUI-based (Base View, section 2.4) or shell-based ( cmsh, section 2.5). Other tasks can be handled
via special tools provided with BCM, or the usual Linux tools. The use of BCM tools is usually recommended over standard Linux tools because cluster administration often has special issues, including
that of scale.

The following topics are among those covered in this manual:


**Chapter** **Title** **Description**



2 Cluster Management With
NVIDIA Base Command

Manager



Introduction to main concepts and tools of BCM. Lays
down groundwork for the remaining chapters



3 Configuring The Cluster Further configuration and set up of the cluster after software installation of BCM on the head node.


4 Power Management How power management within the cluster works


5 Node Provisioning Node provisioning in detail


6 User Management Account management for users and groups


7 Workload Management Workload management implementation and use


8 The cm-scale Service A BCM service to dynamically scale the cluster according to need


9 Post-Installation Software Managing, updating, modifying BCM software and imManagement ages


10 Monitoring: Monitoring Clus- Device monitoring and conditional action triggers
ter Devices


11 Monitoring: Job Monitoring Jobs resource consumption monitoring by the jobs


12 Monitoring: Job Accounting Jobs resource consumption monitoring aggregated by
user or similar groupings


13 Monitoring: Job Chargeback Resource request monitoring, so that groups of users can
be charged for their use


14 Day-To-Day Administration Miscellaneous administration


15 High Availability Background details and setup instructions to build a
cluster with redundant head nodes


16 The Jupyter Notebook Envi- Installing and using the Jupyter notebook environment
ronment Integration


The appendices to this manual generally give supplementary details to the main text.
The following topics are also logically a part of BCM administration, but they have their own separate manuals. This is because they have, or are eventually expected to have, many features or cover a
special set of topics:


  - Cloudbursting ( _Cloudbursting Manual_ )


  - Edge deployment ( _Edge Manual_ )


  - Developer topics ( _Developer Manual_ )


  - Containerization topics ( _Containerization Manual_ )


  - NVIDIA Mission Control topics ( _NVIDIA Mission Control Manual_ )


**1.3 Outside The Direct Scope Of The Administrator Manual** **23**


**1.3** **Outside The Direct Scope Of The Administrator Manual**


The following supplementary resources can deal with issues related to this manual, but are outside its
direct scope:


 - **Use by the end user:** This is covered very peripherally in this manual. The user normally interacts
with the cluster by logging into a custom Linux user environment to run jobs. Details on running
jobs from the perspective of the user are given in the _User Manual_ .


 - **The knowledge base** at [http://kb.brightcomputing.com](http://kb.brightcomputing.com) often supplements the _Administrator_
_Manual_ with discussion of the following:


**–**
Obscure, or complicated, configuration cases


**–**
Procedures that are not really within the scope of BCM itself, but that may come up as part of
related general Linux configuration.


 - **Further support options.** If the issue is not described adequately in the manuals, then section 14.2
describes how to get further support.


# **2**

### **Cluster Management With** **NVIDIA Base Command** **Manager**

This chapter introduces cluster management with NVIDIA Base Command Manager. A cluster running
BCM exports a cluster management interface to the outside world, which can be used by any application
designed to communicate with the cluster.
Section 2.1 introduces a number of concepts which are key to cluster management using BCM.
Section 2.2 gives a short introduction on how the modules environment can be used by administrators. The modules environment provides facilities to control aspects of a users’ interactive sessions and
also the environment used by compute jobs.
Section 2.3 introduces how authentication to the cluster management infrastructure works and how
it is used. Section 2.4 and section 2.5 introduce the cluster management GUI (Base View) and cluster
management shell ( cmsh ) respectively. These are the primary applications that interact with the cluster
management daemon.
Section 2.6 describes the basics of the cluster management daemon, CMDaemon, running on all
nodes of the cluster.


**2.1** **Concepts**


In this section some concepts central to cluster management with BCM are introduced.


**2.1.1** **Devices**

A _device_ in BCM infrastructure represents components of a cluster. A device can be any of the following
types:


 - Head Node


  - Physical Node


  - Virtual Node


  - Cloud Node


  - GPU Unit


  - Chassis


  - Switch (ethernet, InfiniBand, Myrinet)


  - Lite Node


**26** **Cluster Management With NVIDIA Base Command Manager**


  - Power Distribution Unit


  - Rack Sensor Kit


  - Generic Device


A device can have a number of properties (e.g. rack position, hostname, switch port) which can be
set in order to configure the device. Using BCM, operations (e.g. power on) may be performed on a
device. The property changes and operations that can be performed on a device depend on the type of
device. For example, it is possible to mount a new filesystem to a node, but not to an Ethernet switch.
Every device that is managed by BCM has a device state associated with it. The table below describes
the most important states for devices:


**device statuses** **device is** **monitored by BCM?** **state tracking?**


[ UP ] UP monitored tracked


[ DOWN ] DOWN monitored tracked


[ CLOSED ] (UP) UP mostly ignored tracked


[ CLOSED ] (DOWN) DOWN mostly ignored tracked


These, and other states are described in more detail in section 5.5.

[ DOWN ] and [ CLOSED ] (DOWN) states have an important difference. In the case of [ DOWN ],
the device is down, but is typically intended to be available, and thus typically indicates a failure. In
the case of [ CLOSED ] (DOWN), the device is down, but is intended to be unavailable, and typically
indicates that the administrator deliberately brought the device down, and would like the device to be
ignored.


**2.1.2** **Software Images**
A _software image_ is a blueprint for the contents of the local filesystems on a regular node. In practice, a
software image is a directory on the head node containing a full Linux filesystem.
The software image in a standard BCM installation is based on the same parent distribution that
the head node uses. A different distribution can also be chosen after installation, from the distributions
listed in section 2.1 of the _Installation Manual_ for the software image. That is, the head node and the
regular nodes can run different parent distributions. However, such a “mixed” cluster can be harder
to manage and it is easier for problems to arise in such mixtures. Such mixtures, while supported, are
therefore not recommended, and should only be administered by system administrators that understand
the differences between Linux distributions.

RHEL 8 and Rocky Linux 8 mixtures are completely compatible with each other on the head and
regular nodes. The same applies to RHEL9 and Rocky Linux 9. That is because Rocky Linux is designed
to be a binary-compatible derivative of its RHEL parents. On the other hand, SLES and Ubuntu need
quite some effort to work in a mixture.
When a regular node boots, the node provisioning system (Chapter 5) sets up the node with a copy
of the software image, which by default is called default-image .
Once the node is fully booted, it is possible to instruct the node to re-synchronize its local filesystems
with the software image. This procedure can be used to distribute changes to the software image without
rebooting nodes (section 5.6.2).
It is also possible to “lock” a software image so that no node is able to pick up the image until the
software image is unlocked. (section 5.4.7).
Software images can be changed using regular Linux tools and commands (such as rpm and chroot ).
More details on making changes to software images and doing image package management can be
found in Chapter 9.


**2.1 Concepts** **27**


**2.1.3** **Node Categories**

**Reasons For Categories**
The collection of settings in BCM that can apply to a node is called the configuration of the node. The
administrator usually configures nodes using the Base View (section 2.4) or cmsh (section 2.5) front end
tools, and the configurations are managed internally with a database.
A _node category_ is a group of regular nodes that share the same configuration. Node categories allow
efficiency, allowing an administrator to:


  - configure a large group of nodes at once. For example, to set up a group of nodes with a particular
disk layout.


  - operate on a large group of nodes at once. For example, to carry out a reboot on an entire category.


A regular node is in exactly one category at all times, which is default by default. The default
category can be changed by accessing the base object of partition mode (page 102), and setting the
value of defaultcategory to another, existing, category.
Nodes are typically divided into node categories based on the hardware specifications of a node or
based on the task that a node is to perform. Whether or not a number of nodes should be placed in a
separate category depends mainly on whether the configuration—for example: monitoring setup, disk
layout, role assignment—for these nodes differs from the rest of the nodes.


**Corresponding Category Values And Node Values**

  - For non-boolean values, a node inherits values from the category it is in. Each value is treated as
the default property value for a node, and can be overruled by specifying the node property value
for a particular node.


  - For boolean values, such as datanode (page 261) and installbootrecord (page 269), a node does
not inherit the value from the category it is in. Instead the category boolean value has the boolean
or operation applied to the node boolean value, and the result is the boolean value that is used for
the node. This is reasonably similar to the non-boolean values behavior.


**Category And Software Image Do Not Necessarily Map One-To-One**
One configuration property value of a node category is its software image (section 2.1.2). However,
there is no requirement for a one-to-one correspondence between node categories and software images.
Therefore multiple node categories may use the same software image, and conversely, one variable
image—it is variable because it can be changed by the node setting—may be used in the same node
category.
Software images can have their parameters overruled by the category settings. By default, however,
the category settings that can overrule the software image parameters are unset.
By default, all nodes are placed in the default category. Alternative categories can be created and
used at will, such as:


**Example**


**Node Category** **Description**


nodes-ib nodes with InfiniBand capabilities


nodes-highmem nodes with extra memory


login login nodes


storage storage nodes


**2.1.4** **Node Groups**
A _node group_ consists of nodes that have been grouped together for convenience. The group can consist
of any mix of all kinds of nodes, irrespective of whether they are head nodes or regular nodes, and


**28** **Cluster Management With NVIDIA Base Command Manager**


irrespective of what category they are in. A node may be in 0 or more node groups at one time. I.e.: a
node may belong to many node groups.
Node groups are used mainly for carrying out operations on an entire group of nodes at a time. Since
the nodes inside a node group do not necessarily share the same configuration, configuration changes
cannot be carried out using node groups.


**Example**


**Node Group** **Members**


brokenhardware node087, node783, node917


headnodes mycluster-m1, mycluster-m2


rack5 node212..node254


top node084, node126, node168, node210


One important use for node groups is in the nodegroups property of the provisioning role configuration (section 5.2.1), where a list of node groups that provisioning nodes provision is specified.


**2.1.5** **Roles**

A _role_ is a task that can be performed by a node. By assigning a certain role to a node, an administrator
activates the functionality that the role represents on this node. For example, a node can be turned into
provisioning node, or can be turned into a storage node, by assigning the corresponding roles to the
node.

Roles can be assigned to individual nodes or to node categories. When a role has been assigned to a
node category, it is implicitly assigned to all nodes inside the category.
A _configuration overlay_ (section 2.1.6) is a group of roles that can be assigned to designated groups
of nodes within a cluster. This allows configuration of a large number of configuration parameters in
various combinations of nodes.

Some roles allow parameters to be set that influence the behavior of the role. For example, the
Slurm Client Role (which turns a node into a Slurm client) uses parameters to control how the node
is configured within Slurm in terms of queues and the number of GPUs.
When a role has been assigned to a node category with a certain set of parameters, it is possible to
override the parameters for a node inside the category. This can be done by assigning the role again to
the individual node with a different set of parameters. Roles that have been assigned to nodes override
roles that have been assigned to a node category.
Roles have a priority setting associated with them. Roles assigned at category level have a fixed
priority of 250, while roles assigned at node level have a fixed priority of 750. The configuration overlay
priority is variable, but is set to 500 by default. Thus, for example, roles assigned at the node level override roles assigned at the category level. Roles assigned at the node level also override roles assigned by
the default configuration overlay.
A role can be imported from another entity, such as a role, a category, or a configuration overlay.
Examples of role assignment are given in sections 5.2.2 and 5.2.3.


**2.1.6** **Configuration Overlay**
A configuration overlay assigns roles (section 2.1.5) for groups of nodes. The number of roles can be
quite large, and priorities can be set for these.
Multiple configuration overlays can be set for a node. A priority can be set for each configuration
overlay, so that a configuration overlay with a higher priority is applied to its associated node instead of
a configuration overlay with a lower priority. The configuration overlay with the highest priority then
determines the actual assigned role.
A configuration overlay assigns a group of roles to an instance. This means that roles are assigned
to nodes according to the instance configuration, along with a priority. Whether the configuration over

**2.2 Modules Environment** **29**


lay assignment is used, or whether the original role assignment is used, depends upon the configured
priorities.
Configuration overlays can take on priorities in the range 0-1000, except for 250 and 750, which are
forbidden. Setting a priority of -1 means that the configuration overlay is ignored.
The priorities of 250, 500, and 750 are also special, as indicated by the following table:


**priority** **assigned to node from**


-1 _configuration overlay not assigned_


250 category


500 configuration overlay with default priority


750 node


**2.2** **Modules Environment**


The _modules environment_ is the shell environment that is set up by a third-party software (section 7.1 of
the _Installation Manual_ [) called Environment Modules. The software allows users to modify their shell](https://modules.readthedocs.io/en/latest/)
environment using pre-defined _modules_ . A module may, for example, configure the user’s shell to run a
certain version of an application.
Details of the modules environment from a user perspective are discussed in section 2.3 of the _User_
_Manual_ . However some aspects of it are relevant for administrators and are therefore discussed here.


**2.2.1** **Adding And Removing Modules**
Modules may be loaded and unloaded, and also be combined for greater flexibility.
Modules currently installed are listed with:


module list


The modules available for loading are listed with:


module avail


Loading and removing specific modules is done with module load and module remove, using this
format:


module load < _module name 1_ - [< _module name 2_ - ...]


For example, loading the shared module (section 2.2.2), the gcc compiler, the openmpi parallel library, and the openblas library, allows an MPI application myapp.c to be compiled with OpenBLAS
optimizations:


**Example**


module add shared

module add gcc/13.1.0
module add openmpi/gcc/64/4.1.5

module add openblas
module add openblas/dynamic/0.3.18

mpicc -o myapp myapp.c


The exact versions used can be selected using tab-completion. In most cases, specifying version
numbers explicitly is typically only necessary when multiple versions of an application are installed
and available. When there is no ambiguity, module names without a further path specification may be
used.


**30** **Cluster Management With NVIDIA Base Command Manager**


**2.2.2** **Using Local And Shared Modules**
Applications and their associated modules are divided into _local_ and _shared_ groups. Local applications
are installed on the local filesystem, whereas shared applications reside on a shared (i.e. imported)
filesystem.
It is recommended that the shared module be loaded by default for ordinary users. Loading it gives
access to the modules belonging to shared applications, and allows the module avail command to show
these extra modules.

Loading the shared module automatically for root is not recommended on a cluster where shared
storage is not on the head node itself. This is because root logins could be obstructed if this storage is
not available, and if the root user relies on files in the shared storage.
On clusters without external shared storage, root can safely load the shared module automatically
at login. This can be done by running the following command as root :


module initadd shared


Other modules can also be set to load automatically by the user at login by using “ module initadd ”
with the full path specification. With the initadd option, individual users can customize their own
default modules environment.

Modules can be combined in _meta-modules_ . By default, the default-environment meta-module exists, which allows the loading of several modules at once by a user. Cluster administrators are encouraged to customize the default-environment meta-module to set up a recommended environment for
their users. The default-environment meta-module is empty by default.
The administrator and users have the flexibility of deciding the modules that should be loaded in
undecided cases via module _dependencies_ . Dependencies can be defined using the prereq and conflict
commands. The man page for modulefile gives details on configuring the loading of modules with
these commands.


**2.2.3** **Setting Up A Default Environment For All Users**
How users can set up particular modules to load automatically for their own use with the module
initadd command is discussed in section 2.2.2.

How the administrator can set up particular modules to load automatically for all users by default
is discussed in this section (section 2.2.3). In this example it is assumed that all users have just the
following modules as a default:


**Example**


[fred@basecm11 ~]$ module list

Currently Loaded Modulefiles:

1) shared


The slurm and gdb modules can then be set up by the administrator as a default for all users in the
following 2 ways:


1. Creating and defining part of a .profile to be executed for login shells. For example, a file
userdefaultmodules.sh created by the administrator:


[root@basecm11 ~]# cat /etc/profile.d/userdefaultmodules.sh

module load shared

module load slurm

module load gdb


Whenever users now carry out a bash login, these modules are loaded.


2. Instead of placing the modules directly in a script under profile.d like in the preceding
item, a slightly more sophisticated way is to set the modules in the meta-module /cm/shared/
modulefiles/default-environment . For example:


**2.2 Modules Environment** **31**


[root@basecm11 ~]# cat /cm/shared/modulefiles/default-environment

#%Module1.0######################################################

## default modulefile

##

proc ModulesHelp { } {
puts stderr " _\_ tLoads default environment modules for this cluster"
}

module-whatis "adds default environment modules"


# Add any modules here that should be added by when a user loads the 'default-enviro _\_

nment' module

module add shared slurm gdb


The script userdefaultmodules.sh script under profile.d then only needs to have the
default-environment module loaded in it:


[root@basecm11 ~]# cat /etc/profile.d/userdefaultmodules.sh

module load -s default-environment


The -s option is used to load it silently, because otherwise a message is displayed on the terminal
informing the person logging in that the default-environment module has been loaded.


Now, whenever the administrator changes the default-environment module, users get these
changes too during login.


The lexicographical order of the scripts in the /etc/profile directory is important. For example,
naming the file defaultusermodules.sh instead of userdefaultmodules.sh means that the modules.sh
script is run after the file is run, instead of before, which would cause an error.


**2.2.4** **Creating A Modules Environment Module**
All module files are located in the /cm/local/modulefiles and /cm/shared/modulefiles directories.
A module file is a Tcl or Lua script in which special commands are used to define functionality. The
modulefile(1) man page has more on this.
Cluster administrators can use the existing modules files as a guide to creating and installing their
own modules for module environments, and can copy and modify a file for their own software if there
is no environment provided for it already by BCM.


**2.2.5** **Lua Modules Environment (LMod)**
By default, BCM uses traditional Tcl scripts for its module files, or _TMod_ . Lua modules, or _LMod_, provide
an alternative modules environment, where the files are typically written in Lua. LMod can be used as
a replacement for TMod.
Conceptually LMod works in the same way as TMod, but provides some extra features and commands.

For LMod, the module files are typically written in Lua, but LMod is also capable of reading Tcl module files. It is therefore not necessary to convert all existing Tcl modules manually to the Lua language.
On a BCM cluster, both LMod and TMod are installed by default. However only one of them is
active, depending on which one is enabled. Switching between LMod and TMod for a node can be done
by setting an environment variable, $ENABLE_LMOD in the cm-lmod-init.sh shell script.


**Switching For The Head Node**
For example, for the head node:


**Example**


**32** **Cluster Management With NVIDIA Base Command Manager**


[root@basecm11 ~]# cat /etc/sysconfig/modules/lmod/cm-lmod-init.sh

export ENABLE_LMOD=1


In the preceding example, LMod is enabled, and TMod is disabled because $ENABLE_LMOD is set to 1 .


**Example**


[root@basecm11 ~]# cat /etc/sysconfig/modules/lmod/cm-lmod-init.sh

export ENABLE_LMOD=0


In the preceding example, LMod is disabled, and TMod is enabled because $ENABLE_LMOD is set to 0 .
A change in the file on the node is effective after having logged out, then logged into the shell again.


**Switching For The Regular Nodes**
A _node_ _image_ is a directory and contents of that directory. It is used as the template for a regular node when the node is provisioned (Chapter 5). For a node image with the name < _image name_ -, the cm-lmod-init.sh file is located at /cm/images/ _<image_
_name>_ /etc/sysconfig/modules/lmod/cm-lmod-init.sh . For switching between LMod and TMod on
a regular node, the file is changed on the image, and the file on the image is then updated to the node.
The update from the image to the node is typically carried out with the imageupdate command in cmsh
(section 5.6.2) or the Update node command in Base View (section 5.6.3).


**2.3** **Authentication**


**2.3.1** **Changing Administrative Passwords On The Cluster**
How to set up or change regular user passwords is not discussed here, but in Chapter 6 on user management.
Amongst the administrative passwords associated with the cluster are:


1. **The root password of the head node:** This allows a root login to the head node.


2. **The root passwords of the software images:** These allow a root login to a regular node running
with that image, and is stored in the image file.


3. **The root password of the node-installer:** This allows a root login to the node when the nodeinstaller, a stripped-down operating system, is running. The node-installer stage prepares the
node for the final operating system when the node is booting up. Section 5.4 discusses the nodeinstaller in more detail.


4. **The root password of MySQL:** This allows a root login to the MySQL server.


To avoid having to remember the disparate ways in which to change these 4 kinds of passwords,
the cm-change-passwd command runs a dialog prompting the administrator on which of them, if any,
should be changed, as in the following example:


[root@basecm11 ~]# cm-change-passwd

With this utility you can easily change the following passwords:

 - root password of head node

 - root password of slave images

 - root password of node-installer

 - root password of mysql


Note: if this cluster has a high-availability setup with 2 head

nodes, be sure to run this script on both head nodes.


**2.3 Authentication** **33**


Change password for root on head node? [y/N]: y

Changing password for root on head node.

Changing password for user root.

New password:

Retype new password:

passwd: all authentication tokens updated successfully.


Change password for root in default-image [y/N]: y

Changing password for root in default-image.

Changing password for user root.

New password:

Retype new password:

passwd: all authentication tokens updated successfully.


Change password for root in node-installer? [y/N]: y

Changing password for root in node-installer.

Changing password for user root.

New password:

Retype new password:

passwd: all authentication tokens updated successfully.


Change password for MYSQL root user? [y/N]: y

Changing password for MYSQL root user.

Old password:

New password:

Re-enter new password:


For a high-availability—also called a failover—configuration, the passwords are copied over automatically to the other head node when a change is made in the software image root password (case 2 on
page 32).
For the remaining password cases (head root password, MySQL root password, and node-installer
root password), the passwords are best “copied” over to the other head node by simply rerunning the
script on the other head node.
Also, in the case of the password for software images used by the regular nodes: the new password
that is set for a regular node only works on the node after the image on the node itself has been updated,
with, for example, the imageupdate command (section 5.6.2). Alternatively, the new password can be
made to work on the node by simply rebooting the node to pick up the new image.
The LDAP root password is a random string set during installation. Changing this is not done using
cm-change-password . It can be changed as explained in Appendix I.
If the administrator has stored the password to the cluster in the Base View front-end, then the
password should be modified there too (figure 2.2).


**2.3.2** **Logins Using** ssh
The standard system login root password of the head node, the software image, and the node-installer,
can be set using the cm-change-passwd command (section 2.3.1).
In contrast, ssh logins from the head node to the regular nodes are set by default to be passwordless:


  - For non-root users, an ssh passwordless login works if the /home directory that contains the authorized keys for these users is mounted. The /home directory is mounted by default on the head
node as well as on the regular node, so that by default a passwordless login works from the head
node to the regular nodes, as well as from the regular nodes to the head node.


**34** **Cluster Management With NVIDIA Base Command Manager**


  - For the root user, an ssh passwordless login should always work from the head node to the regular
nodes since the authorized keys are stored in /root . Logins from the regular node to the head node
are configured by default to request a password, as a security consideration.


Users can be restricted from ssh logins


  - on regular nodes using the cmsh usernodelogin option (section 7.2.1) or the Base View User node
login (section 7.2.2) settings


  - on the head node by modifying the sshd configuration on the head node. For example, to allow
only root logins, the value of AllowUsers can be set in /etc/ssh/sshd_config to root . The man
page for sshd_config has details on this.


**2.3.3** **Certificates**

**PEM Certificates And CMDaemon Front-end Authentication**
While nodes in the cluster accept ordinary ssh -based logins, the cluster manager accepts public key
authentication using X509v3 certificates. Public key authentication using X509v3 certificates means in
practice that the person authenticating to the cluster manager must present their public certificate, and
in addition must have access to the private key that corresponds to the certificate.
BCM uses the PEM format for certificates. In this format, the certificate and private key are stored as
plain text in two separate PEM-encoded files, ending in .pem and .key .


**Using** cmsh **and authenticating to BCM:** By default, one administrator certificate is created for root for
the cmsh front end to interact with the cluster manager. The certificate and corresponding private key
are thus found on a newly-installed BCM cluster on the head node at:


/root/.cm/admin.pem
/root/.cm/admin.key


The cmsh front end, when accessing the certificate and key pair as user root, uses this pair by default, so
that prompting for authentication is then not a security requirement. The logic that is followed to access
the certificate and key by default is explained in detail in item 2 on page 319.


**Using Base View and authenticating to BCM:** When an administrator uses the Base View front end,
a login to the cluster is carried out with username password authentication (figure 2.2), unless the authentication has already been stored in the browser, or unless certificate-based authentication is used.


  - Certificate-based authentication can be carried out using a PKCS#12 certificate file. This can be
generated from the PEM format certificates. For example, for the root user, an openssl command
that can be used to generate the admin.pfx file is:


openssl pkcs12 -export -in ~/.cm/admin.pem -inkey ~/.cm/admin.key -out ~/.cm/admin.pfx


**–** In Chrome, the IMPORT wizard at [chrome://settings/certificates](chrome://settings/certificates) can be used to save the
file into the browser.


**–**
For Firefox, the equivalent navigation path is:


about:preferences#privacy     - Certificates     - View Certificates     - Your Certificates

    - Import


The browser can then access the Base View front end without a username/password combination.


**2.4 Base View GUI** **35**


If the administrator certificate and key are replaced, then any other certificates signed by the original
administrator certificate must be generated again using the replacement, because otherwise they will no
longer function.
Certificate generation in general, including the generation and use of non-administrator certificates,
is described in greater detail in section 6.4.


**Replacing A Temporary Or Evaluation License**
In the preceding section, if a license is replaced, then regular user certificates need to be generated again.
Similarly, if a temporary or evaluation license is replaced, regular user certificates need to be generated
again. This is because the old user certificates are signed by a key that is no longer valid. The generation
of non-administrator certificates and how they function is described in section 6.4.


**Checking Certificates Validity With** cm-check-certificates.sh
A BCM script that checks whether certificates are current or expired is /cm/local/apps/cmd/scripts/

cm-check-certificates.sh :


**Example**


root@basecm11:~# /cm/local/apps/cmd/scripts/cm-check-certificates.sh
/cm/local/apps/cmd/etc/cluster.pem: OK
/cm/local/apps/cmd/etc/cert.pem: OK


/cm/local/apps/cmd/etc/cluster.key : matches


All /cm/local/apps/cmd/etc/cluster.pem files are up to date (82070dedb489df6c19ffa3ace1bf354e)


/root/.cm/admin.pem: OK
_... output truncated ..._

root@basecm11:~#


**2.3.4** **Profiles**
Certificates that authenticate to CMDaemon contain a _profile_ .
A profile determines which cluster management operations the certificate holder may perform. The
administrator certificate is created with the admin profile, which is a built-in profile that allows all cluster
management operations to be performed. In this sense it is similar to the root account on unix systems.
Other certificates may be created with different profiles giving certificate owners access to a pre-defined
subset of the cluster management functionality (section 6.4).


**2.4** **Base View GUI**


This section introduces the basics of the cluster management GUI (Base View). Base View is the web
application front end to cluster management in BCM.
[Base View is supported to run on the last 2 versions of Firefox, Google Chrome, Edge, and Safari.](https://browserl.ist/?q=last+2+versions)
[“Last 2 versions” means the last two publicly released versions at the time of release of NVIDIA Base](https://browserl.ist/?q=last+2+versions)
[Command Manager. For example, at the time of writing of this section, June 2025, the last 2 versions](https://browserl.ist/?q=last+2+versions)

[were:](https://browserl.ist/?q=last+2+versions)


**Browser** **Versions**


Chrome 136, 137


Edge 136, 137


Firefox 138, 139


Safari 18.4, 18.5


**36** **Cluster Management With NVIDIA Base Command Manager**


Base View should run on more up-to-date versions of the browsers in the table without issues.
Base View should run on other recent browsers without issues too, but this is not supported. Browsers
that run on mobile devices are also not supported.


**2.4.1** **Installing The Cluster Management GUI Service**
In a default installation, accessing the head node hostname or IP address with a browser leads to the
landing page (figure 2.1).


Figure 2.1: Head node hostname or IP address landing page at https://< _host name or IP address_  

The landing page is served by the Apache web server from the distribution, and can be served over
the HTTP (unencrypted) or HTTPS (encrypted) protocols.
The certificates used to ensure an encrypted connection are set within:


 - /etc/httpd/conf.d/ssl.conf for the RHEL family of distributions. The PEM-encoded certificate
at /etc/pki/tls/certs/localhost.crt is set by default.


 - /etc/apache2/sites-available/default-ssl.conf for Ubuntu. The PEM-encoded certificate
at /etc/ssl/certs/ssl-cert-snakeoil.pem is set by default.


The system administrator may wish to consider the security aspects of using the default distribution
certificates, and may wish to replace them.
Within the landing page are several blocks, one of which is the Base View block. Base View is the
BCM GUI. Within the Base View block is a clickable link, which is a circle with a chain-link symbol
inside it.

Base View connects by default to the encrypted web service on port 8081. This is served from the
head node cluster manager, rather than from Apache, to the browser. The direct URL for this is of the
form:


https://< _host name or IP address_ >:8081/base-view


The BCM package that provides the service is base-view and it is installed by default with BCM. The
service can be disabled by removing the package with, for example, yum remove base-view .


**2.4 Base View GUI** **37**


**NVIDIA Base Command Manager Base View Login Window**
Figure 2.2 shows the login dialog window for Base View.


Figure 2.2: Base View Login via https://< _host name or IP address_ >:8081/base-view


**NVIDIA Base Command Manager** Base View **Default Display On Connection**
Clicking on the Login button logs the administrator into the Base View service on the cluster. By default
an overview window is displayed, corresponding to the navigation path Cluster - Partition base
(figure 2.3).


Figure 2.3: Cluster Overview


**38** **Cluster Management With NVIDIA Base Command Manager**


**2.4.2** **Navigating The Cluster With Base View**
Aspects of the cluster can be managed by administrators using Base View (figure 2.3).
The resource tree, displayed on the left side of the window, consists of available cluster usage concepts such as Provisioning, Grouping, HPC, Cloud, and Containers . It also has a cluster-centric approach to miscellaneous system concepts such as hardware devices Devices, non-hardware resources
such as Identity Management, and Networking .
Selecting a resource opens a window that allows parameters related to the resource to be viewed and
managed.
As an example, the Cluster resource can be selected. This opens up the so-called Partition base
window, which is essentially a representation of the cluster instance. [1]

The tabs within the Partition base window are mapped out in figure 2.4 and summarily described

next.


1 The name Partition base is literally a footnote in BCM history. It derives from the time that BCM clusters were planned to
run in separate partitions within the cluster hardware. The primary cluster was then to be the base cluster, running in the base
partition. The advent of BCM cloud computing options in the form of the Cluster-On-Demand option (Chapter 2 of the _Cloud-_
_bursting Manual_ ), and the Cluster Extension option (Chapter 3 of the _Cloudbursting Manual_ ) means developing cluster partitions is
no longer a priority.


**40** **Cluster Management With NVIDIA Base Command Manager**


**Overview**

The Overview tab (figure 2.3, page 37) shows the Occupation rate (page 931), memory used, CPU
cycles used, node statuses, and other helpful cluster overview details.


**Settings**
The Settings tab has a number of global cluster properties and property groups. These are loosely
grouped as follows:


  - Buttons for jumping to settings for: Failover, time zone, ArchOS, burn configuration, failover
groups, BMC settings, SNMP settings, DPU settings, ZTP settings, ZTP new switch settings,
SELinux settings, provisioning settings, access settings, NetQ settings, provisioning settings.


 - Cluster name, Administrator e-mail, partition name


 - Node basename, Node digits


 - Name servers, Time servers


 - Search domains, Relay Host


 Externally visible IP, Provisioning Node Auto Update Timeout


 - Default burn configuration


 - External network, Management network


 - Default category : Sets the default category


 - Sign installer certificates


 - Notes


**License info**

The License info tab shows information to do with cluster licensing. A slightly obscure property
within this window is Version, which refers to the version type of the license. The license for NVIDIA
Base Command Manager version 7.0 and above is of a type that is compatible with versions all the
way up to the current version. NVIDIA Base Command Manager license versions from before 7.0 are
not compatible. In practice it means that an upgrade from before 7.0, to 7.0 or beyond, requires a license
upgrade. The BCM support team must be contacted to arrange the license upgrade.


**System information**
The System information tab shows the main hardware specifications of the node (CPU, memory, BIOS),
along with the operating system version that it runs.


**Version info**

The Version info tab shows version information for important cluster software components, such as
the CMDaemon database version, and BCM version and builds.


**Run command**

The Run command tab allows a specified command to be run on a selected node of the cluster.


**Fabrics**

The Fabrics tab displays the topology and switches for the fabrics used.


**Rack View**

The Rack View tab displays a view of the rack as defined by node allocations made by the administrator
to racks and chassis.


**2.5 Cluster Management Shell** **41**


**2.5** **Cluster Management Shell**


This section introduces the basics of the cluster management shell, cmsh . This is the command-line
interface to cluster management in BCM. Since cmsh and Base View give access to the same cluster management functionality, an administrator need not become familiar with both interfaces. Administrators
intending to manage a cluster with only Base View may therefore safely skip this section.
The cmsh front end allows commands to be run with it, and can be used in batch mode. Although
cmsh commands often use constructs familiar to programmers, it is designed mainly for managing the
cluster efficiently rather than for trying to be a good or complete programming language. For programming cluster management, the use of Python bindings (Chapter 1 of the _Developer Manual_ ) is generally
recommended instead of using cmsh in batch mode.
Usually cmsh is invoked from an interactive session (e.g. through ssh ) on the head node, but it can
also be used to manage the cluster from outside.


**2.5.1** **Invoking** cmsh

From the head node, cmsh can be invoked as follows:


**Example**


[root@mycluster ~]# cmsh

[mycluster]%


By default it connects to the IP address of the local management network interface, using the default BCM port. If it fails to connect as in the preceding example, but a connection takes place using
cmsh localhost, then the management interface is most probably not up. In that case, bringing the
management interface up allows cmsh to connect to CMDaemon.
Running cmsh without arguments starts an interactive cluster management session. To go back to the
unix shell, a user enters quit or ctrl-d :


[mycluster]% quit

[root@mycluster ~]#


**Batch Mode And Piping In** cmsh
The -c flag allows cmsh to be used in batch mode. Commands may be separated using semi-colons:


[root@mycluster ~]# cmsh -c "main showprofile; device status apc01"

admin

apc01 ............... [ UP ]

[root@mycluster ~]#


Alternatively, commands can be piped to cmsh :


[root@mycluster ~]# echo device status | cmsh

device status

apc01 ............... [ UP ]
mycluster ........... [ UP ]

node001 ............. [ UP ]

node002 ............. [ UP ]

switch01 ............ [ UP ]

[root@mycluster ~]#


**Dotfiles And** /etc/cmshrc **File For** cmsh
In a similar way to unix shells, cmsh sources an rc file from the /etc directory, and also dotfiles, if
they exist. The sourcing is done upon start-up in both batch and interactive mode.
If /etc/cmshrc exists, then its settings are used, but the values can be overridden by user dotfiles.
This is standard Unix behavior, analogous to how bash works with /etc/bashrc and .bashrc files.
In the following list of cmsh dotfiles, a setting in the file that is in the shorter path overrides a setting
in the file with the longer path (i.e.: “shortest path overrides”):


**42** **Cluster Management With NVIDIA Base Command Manager**


 - _∼_ /.cm/cmsh/.cmshrc


 - _∼_ /.cm/.cmshrc


 - _∼_ /.cmshrc


**Defining Command Aliases In** cmsh
Sourcing settings is convenient when defining command aliases. Command aliases can be used to abbreviate longer commands. For example, putting the following in .cmshrc would allow lv to be used
as an alias for device list virtualnode :


**Example**


alias lv device list virtualnode


Besides defining aliases in dotfiles, aliases in cmsh can also be created with the alias command. The
preceding example can be run within cmsh to create the lv alias. Running the alias command within
cmsh lists the existing aliases.
Aliases can be exported from within cmsh together with other cmsh dot settings with the help of the
export command:


**Example**


[mycluster]% export > /root/mydotsettings


The dot settings can be taken into cmsh by running the run command from within cmsh :


**Example**


[mycluster]% run /root/mydotsettings


**Built-in Aliases In** cmsh

The following aliases are built-ins, and are not defined in any .cmshrc or cmshrc files:


[basecm11]% alias

alias - goto 
alias .. exit

alias / home

alias ? help

alias ds device status

alias ls list


The meanings are:


 - goto - : go to previous directory level of cmsh


 - exit : go up a directory level, or leave cmsh if already at top level.


 - home : go to the top level directory


 - help : show help text for current level


 - device status : show status of devices that can be accessed in device mode


**2.5 Cluster Management Shell** **43**


**Automatic Aliases In** cmsh

A cmsh script is a file that has a sequence of cmsh commands that run within a cmsh session.
The directory .cm/cmsh/ can have placed in it a cmsh script with a .cmsh suffix and an arbitrary
prefix. The prefix then automatically becomes an alias in cmsh .
In the following example


  - the file tablelist.cmsh provides the alias tablelist, to list devices using the | symbol as a delimiter, and


  - the file dfh.cmsh provides the alias dfh to carry out the Linux shell command df -h


**Example**


[root@mycluster ~]# cat /root/.cm/cmsh/tablelist.cmsh

list -d "|"

[root@mycluster ~]# cat /root/.cm/cmsh/dfh.cmsh

!df -h

[root@mycluster ~]# cmsh

[mycluster]% device

[mycluster->device]% alias | egrep '(tablelist|dfh)'

alias dfh run /root/.cm/cmsh/dfh.cmsh

alias tablelist run /root/.cm/cmsh/tablelist.cmsh

[mycluster->device]% list
Type Hostname (key) MAC Category Ip

---------------------- ---------------- ------------------ ---------------- --------------
HeadNode mycluster FA:16:3E:B4:39:DB 10.141.255.254

PhysicalNode node001 FA:16:3E:D5:87:71 default 10.141.0.1

PhysicalNode node002 FA:16:3E:BE:05:FE default 10.141.0.2

[mycluster->device]% tablelist
Type |Hostname (key) |MAC |Category |Ip

----------------------|----------------|------------------|----------------|--------------
HeadNode |mycluster |FA:16:3E:B4:39:DB | |10.141.255.254
PhysicalNode |node001 |FA:16:3E:D5:87:71 |default |10.141.0.1
PhysicalNode |node002 |FA:16:3E:BE:05:FE |default |10.141.0.2

[mycluster->device]% dfh
Filesystem Size Used Avail Use% Mounted on
devtmpfs 1.8G 0 1.8G 0% /dev
tmpfs 1.9G 0 1.9G 0% /dev/shm
tmpfs 1.9G 33M 1.8G 2% /run
tmpfs 1.9G 0 1.9G 0% /sys/fs/cgroup

/dev/vdb1 25G 17G 8.7G 66% /

tmpfs 374M 0 374M 0% /run/user/0


The cmsh session in NVIDIA Base Command Manager does not need restarting for the alias to become active.


**Default Arguments In** cmsh **Scripts**
In a cmsh script, the parameters $1, $2 and so on can be used to pass arguments. If the argument being
passed is blank, then the values the parameters take also remain blank. However, if the parameter
format has a suffix of the form -< _value_ -, then < _value_ - is the default value that the parameter takes if the
argument being passed is blank.


**Example**


[root@mycluster ~]# cat .cm/cmsh/encrypt-node-disk.cmsh

home


**44** **Cluster Management With NVIDIA Base Command Manager**


device use ${1-node001}

set disksetup /root/my-encrypted-node-disk.xml

set revision ${2-test}

commit


The script can be run without an argument (a blank value for the argument), in which case it takes
on the default value of node001 for the parameter:


[root@mycluster ~]# cmsh

[mycluster]% encrypt-node-disk

[mycluster->device[node001]]%


The script can be run with an argument ( node002 here), in which case it takes on the passed value of
node002 for the parameter:


[root@mycluster ~]# cmsh

[mycluster]% encrypt-node-disk node002

[mycluster->device[node002]]%


**Options Usage For** cmsh
The options usage information for cmsh is obtainable with cmsh -h :


Usage:
cmsh [options] [hostname[:port]]
cmsh [options] -c <command>
cmsh [options] -f <filename>


Options:


--help|-h

Display this help


--noconnect|-u

Start unconnected


--controlflag|-z

ETX in non-interactive mode


--color <yes/no>

Define usage of colors


--spool <directory>
Alternative /var/spool/cmd


--tty|-t

Pretend a TTY is available


--noredirect|-r

Do not follow redirects


--norc|-n

Do not load cmshrc file on start-up


--noquitconfirmation|-Q

Do not ask for quit confirmation


--echo|-x


**2.5 Cluster Management Shell** **45**


Echo all commands


--quit|-q

Exit immediately after error


--disablemultiline|-m

Disable multiline support


--hide-events

Hide all events by default


--disable-events

Disable all events by default


--certificate|-i

Specify alternative certificate


--key|-k

Specify alternative private key


Arguments:

hostname

The hostname or IP to connect to


command

A list of cmsh commands to execute


filename

A file which contains a list of cmsh commands to execute


Examples:

cmsh run in interactive mode

cmsh -c 'device status' run the device status command and exit

cmsh --hide-events -c 'device status' run the device status command and exit, without

showing any events that arrive during this time

cmsh -f some.file -q -x run and echo the commands from some.file, exit


**Man Page For** cmsh
There is also a man page for cmsh(8), which is a bit more extensive than the help text. It does not
however cover the modes and interactive behavior.


**2.5.2** **Levels, Modes, Help, And Commands Syntax In** cmsh
The _top-level_ of cmsh is the level that cmsh is in when entered without any options.
To avoid overloading a user with commands, cluster management functionality has been grouped
and placed in separate cmsh _mode_ levels. Mode levels and associated _objects_ for a level make up a hierarchy available below the top-level.
There is an object-oriented terminology associated with managing via this hierarchy. To perform
cluster management functions, the administrator descends via cmsh into the appropriate mode and object, and carries out actions relevant to the mode or object.
For example, within user mode, an object representing a user instance, fred, might be added or
removed. Within the object fred, the administrator can manage its properties. The properties can be
data such as a password fred123, or a home directory /home/fred .
Figure 2.5 shows the top-level commands available in cmsh . These commands are displayed when
help is typed in at the top-level of cmsh :


**46** **Cluster Management With NVIDIA Base Command Manager**


alias ......................... Set aliases

category ...................... Enter category mode

cert .......................... Enter cert mode

cloud ......................... Enter cloud mode

color ......................... Manage console text color settings

configurationoverlay .......... Enter configurationoverlay mode

connect ....................... Connect to cluster

delimiter ..................... Display/set delimiter

device ........................ Enter device mode

disconnect .................... Disconnect from cluster

edgesite....................... Enter edgesite mode

etcd .......................... Enter etcd mode

events ........................ Manage events

exit .......................... Exit from current object or mode

export ........................ Display list of aliases current list formats

fspart ....................... Enter fspart mode

group ......................... Enter group mode

groupingsyntax ................ Manage the default grouping syntax

help .......................... Display this help

hierarchy ..................... Enter hierarchy mode

history ....................... Display command history

kubernetes..................... Enter kubernetes mode

list .......................... List state for all modes

main .......................... Enter main mode

modified ...................... List modified objects

monitoring .................... Enter monitoring mode

network ....................... Enter network mode

nodegroup ..................... Enter nodegroup mode

partition ..................... Enter partition mode

powercircuit .................. Enter powercircuit mode

process ....................... Enter process mode

profile ....................... Enter profile mode

quit .......................... Quit shell

quitconfirmation .............. Manage the status of quit confirmation

rack .......................... Enter rack mode

refresh ....................... Refresh all modes

run ........................... Execute cmsh commands from specified file

session ....................... Enter session mode

softwareimage ................. Enter softwareimage mode

task .......................... Enter task mode

time .......................... Measure time of executing command

unalias ....................... Unset aliases

user .......................... Enter user mode

watch ......................... Execute a command periodically, showing output

wlm ........................... Enter wlm mode


Figure 2.5: Top level commands in cmsh


All levels inside cmsh provide these top-level commands.
Passing a command as an argument to help gets details for it:


**Example**


[myheadnode]% help run
Name: run - Execute all commands in the given file(s)


**2.5 Cluster Management Shell** **47**


Usage: run [OPTIONS] <filename> [<filename2> ...]


Options: -x, --echo

Echo all commands


-q, --quit

Exit immediately after error


[myheadnode]%


In the general case, invoking help at any mode level or within an object, without an argument,
provides two lists:


  - Firstly, under the title of Top : a list of top-level commands.


  - Secondly, under the title of the level it was invoked at: a list of commands that may be used at that
level.


For example, entering session mode and then typing in help displays, firstly, output with a title of Top,
and secondly, output with a title of session (some output ellipsized):


**Example**


[myheadnode]% session

[myheadnode->session]% help

============================ Top =============================

alias ......................... Set aliases

category ...................... Enter category mode

cert .......................... Enter cert mode

cloud ......................... Enter cloud mode

...

========================== session ===========================

id ....................... Display current session id

killsession .............. Kill a session

list ..................... Provide overview of active sessions

[myheadnode->session]%


**Navigation Through Modes And Objects In** cmsh
The major modes tree is shown in Appendix M.1.
The following notes can help the cluster administrator in navigating the cmsh shell:


  - To enter a mode, a user enters the mode name at the cmsh prompt. The prompt changes to indicate
that cmsh is in the requested mode, and commands for that mode can then be run.


  - To use an object within a mode, the use command is used with the object name. In other words,
a mode is entered, and an object within that mode is used. When an object is used, the prompt
changes to indicate that that object within the mode is now being used, and that commands are
applied for that particular object.


  - To leave a mode, and go back up a level, the exit command is used. Similarly, if an object is in
use, the exit command exits the object. At the top level, exit has the same effect as the quit
command, that is, the user leaves cmsh and returns to the unix shell. The string .. is an alias for

exit .


  - The home command, which is aliased to /, takes the user from any mode depth to the top level.


**48** **Cluster Management With NVIDIA Base Command Manager**


  - The path command at any mode depth displays a string that can be used as a path to the current
mode and object, in a form that is convenient for copying and pasting into cmsh . The string can be
used in various ways. For example, it can be useful to define an alias in .cmshrc (page 42).


In the following example, the path command is used to print out a string. This string makes it
easy to construct a bash shell command to run a list from the correct place within cmsh :


**Example**


[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]% list
Name (key)

---------------------------
slurmclient

[basecm11->configurationoverlay[slurm-client]->roles[slurmclient]]% path

home;configurationoverlay;use "slurm-client";roles;use slurmclient;


Pasting the string into a bash shell, using the cmsh command with the -c option, and appending
the list command to the string, replicates the session output of the list command:


[basecm11 ~]# cmsh -c 'configurationoverlay;use "slurm-client";roles;use slurmclient; list'
Name (key)

---------------------------
slurmclient


The following example shows the path command can also be used inside the cmsh session itself
for convenience:


**Example**


[basecm11]% device

[basecm11->device]% list

Type Hostname (key) MAC Category Ip Network Status

---------------- --------------- ------------------ --------- -------------- ----------- -----
EthernetSwitch switch01 00:00:00:00:00:00 10.141.0.50 internalnet [ UP ]

HeadNode basecm11 00:0C:29:5D:55:46 10.141.255.254 internalnet [ UP ]

PhysicalNode node001 00:0C:29:7A:41:78 default 10.141.0.1 internalnet [ UP ]
PhysicalNode node002 00:0C:29:CC:4F:79 default 10.141.0.2 internalnet [ UP ]

[basecm11->device]% exit

[basecm11]% device

[basecm11->device]% use node001

[basecm11->device[node001]]% path

home;device;use node001;

[basecm11->device[node001]]% home

[basecm11]% home;device;use node001 #copy-pasted from path output earlier

[basecm11->device[node001]]%


A command can also be executed in a mode without staying within that mode. This is done by
specifying the mode before the command that is to be executed within that node. Most commands also
accept arguments after the command. Multiple commands can be executed in one line by separating
commands with semi-colons.

A cmsh input line has the following syntax:


**2.5 Cluster Management Shell** **49**


_<mode> <cmd> <arg> ...<arg>; ...; <mode> <cmd> <arg> ...<arg>_


where _<_ _mode_ _>_ and _<_ _arg_ _>_ are optional. [2]


**Example**


[basecm11->network]% device status basecm11; list

basecm11 ............ [ UP ]

Name (key) Type Netmask bits Base address Domain name Ipv6

------------- --------- ------------- ------------- -------------------- ---
externalnet External 16 192.168.1.0 brightcomputing.com no

globalnet Global 0 0.0.0.0 cm.cluster

internalnet Internal 16 10.141.0.0 eth.cluster

[basecm11->network]%


In the preceding example, while in network mode, the status command is executed in device mode
on the host name of the head node, making it display the status of the head node. The list command
on the same line after the semi-colon still runs in network mode, as expected, and not in device mode,
and so displays a list of networks.
Inserting a semi-colon makes a difference, in that the mode is actually entered, so that the list displays
a list of nodes (some output truncated here for convenience):


**Example**


[basecm11->network]% device; status basecm11; list

basecm11 ................ [ UP ]

Type Hostname (key) MAC Category Ip Network Status

------------- --------------- ------------------ --------- -------------- ----------- -----
HeadNode basecm11 FA:16:3E:C8:06:D1 10.141.255.254 internalnet [ UP ]

PhysicalNode node001 FA:16:3E:A2:9C:87 default 10.141.0.1 internalnet [ UP ]

[basecm11->device]%


**2.5.3** **Working With Objects**
Modes in cmsh work with associated groupings of data called _objects_ . For instance, device mode works
with device objects, and network mode works with network objects.
The commands used to deal with objects have similar behavior in all modes. Not all of the commands
exist in every mode, and not all of the commands function with an explicit object:


**Command** **Description**


use Use the specified object. I.e.: Make the specified object the _current object_


add Create the object and use it


assign Assign a new object


unassign Unassign an object


clear Clear the values of the object


clone Clone the object and use it


remove Remove the object


commit Commit local changes, done to an object, to CMDaemon


_...continues_


2 A more precise synopsis is:

[<mode>] <cmd> [<arg> ... ] [; ... ; [<mode>] <cmd> [<arg> ... ]]


**50** **Cluster Management With NVIDIA Base Command Manager**


_...continued_


**Command** **Description**


refresh Undo local changes done to the object


list List all objects at current level


sort Sort the order of display for the list command


format Set formatting preferences for list output


foreach Execute a set of commands on several objects


show Display all properties of the object


swap Swap (exchange) the names of two objects


get Display specified property of the object


set Set a specified property of the object


clear Set default value for a specified property of the object.


append Append a value to a property of the object, for a multi-valued property


removefrom Remove a value from a specific property of the object, for a multi-valued property


modified List objects with uncommitted local changes


usedby List objects that depend on the object


validate Do a validation check on the properties of the object


exit Exit from the current object or mode level


Working with objects with these commands is demonstrated with several examples in this section.


**Working With Objects:** use **,** exit
**Example**


[mycluster->device]% use node001

[mycluster->device[node001]]% status

node001 ............. [ UP ]

[mycluster->device[node001]]% exit

[mycluster->device]%


In the preceding example, use node001 issued from within device mode makes node001 the _cur-_
_rent object_ . The prompt changes accordingly. The status command, without an argument, then returns
status information just for node001, because making an object the current object makes subsequent commands within that mode level apply only to that object. Finally, the exit command exits the current
object level.


**Working With Objects:** add **,** commit **,** remove
The commands introduced in this section have many implicit concepts associated with them. So an
illustrative session is first presented as an example. What happens in the session is then explained in
order to familiarize the reader with the commands and associated concepts.


**Example**


[mycluster->device]% add physicalnode node100 10.141.0.100

[mycluster->device*[node100*]]% commit

[mycluster->device[node100]]% category add test-category

[mycluster->category*[test-category*]]% commit

[mycluster->category[test-category]]% remove test-category

[mycluster->category*]% commit

Successfully removed 1 Categories

Successfully committed 0 Categories


**2.5 Cluster Management Shell** **51**


[mycluster->category]% device remove node100

[mycluster->category]% device

[mycluster->device*]% commit

Successfully removed 1 Devices

Successfully committed 0 Devices

[mycluster->device]%


add: The add command creates an object within its associated mode, and in cmsh the prompt drops
into the object level just created. Thus, at the start in the preceding example, within device mode, a new
object, named node100, is added. For this particular object properties can also be set, such as the type
( physicalnode ), and IP address ( 10.141.0.100 ). The node object level ( [node100*] ) is automatically
dropped into from device mode when the add command is executed. After execution, the state achieved
is that the object has been created with some properties. However, it is still in a temporary, modified
state, and not yet persistent.
_Asterisk tags_ in the prompt are a useful reminder of a modified state, with each asterisk indicating
a tagged object that has an unsaved, modified property. In this case, the unsaved properties are the IP
address setting, the node name, and the node type.


The add command—syntax notes:


In most modes the add command takes only one argument, namely the name of the object that is
to be created. However, in device mode an extra object-type, in this case physicalnode, is also
required as argument, and an optional extra IP argument may also be specified. The response to
“ help add ” while in device mode gives details:


[myheadnode->device]% help add

Name:

add - Create a new device of the given type with specified hostname


Usage:

add <type> <hostname>
add cloudnode <hostname> [provider]
add physicalnode <hostname> [ip] [interface]


Arguments:

type chassis, fabricresourcebox, fabricswitch, genericdevice, litenode,

cloudnode, dpu, physicalnode, headnode, powerdistributionunit,

racksensor, switch, unmanagednode


interface eg. ens3, bond0=ens3+ens4


commit: The commit command is a further step that actually saves any changes made after executing
a command. In this case, in the second line, it saves the node100 object with its properties. The asterisk
tag disappears for the prompt if settings for that mode level and below have been saved.
Conveniently, the top level modes, such as the category mode, can be accessed directly from within
this level if the mode is stated before the command. So, stating the mode category before running the
add command allows the specified category test-category to be added. Again, the test-category
object level within category mode is automatically dropped into when the add command is executed.


The -w|--wait option to commit :


The commit command by default does not wait for a state change to complete. This means that the
prompt becomes available right away. This means that it is not obvious that the change has taken
place, which could be awkward if scripting with cmsh for cloning (discussed shortly) a software


**52** **Cluster Management With NVIDIA Base Command Manager**


image (section 2.1.2). The -w|--wait option to the commit command works around this issue
by waiting for any associated background task, such as the cloning of a software image, to be
completed before making the prompt available.


remove **:** The remove command removes a specified object within its associated mode. On successful
execution, if the prompt is at the object level, then the prompt moves one level up. The removal is not
actually carried out fully yet; it is only a proposed removal. This is indicated by the asterisk tag, which
remains visible, until the commit command is executed, and the test-category removal is saved. The
remove command can also remove a object in a non-local mode, if the non-local mode is associated
with the command. This is illustrated in the example where, from within category mode, the device
mode is declared before running the remove command for node100 . The proposed removal is configured
without being made permanent, but in this case no asterisk tag shows up in the category mode, because
the change is in device mode. To drop into device mode, the mode command “ device ” is executed. An
asterisk tag then does appear, to remind the administrator that there is still an uncommitted change (the
node that is to be removed) for the mode. The commit command would remove the object whichever
mode it is in—the non-existence of the asterisk tag does not change the effectiveness of commit .


The -d|--data option to remove :


The remove command by default removes an object, and not the represented data. An example
is if, in softwareimage mode, a software image is removed with the remove (without options)
command. As far as the cluster manager is concerned, the image is removed after running commit .
However the data in the directory for that software image is not removed. The -d|--data option
to the remove command arranges removal of the data in the directory for the specified image, as
well as removal of its associated object.


The -a|--all option to remove :


The remove command by default does not remove software image revisions. The -a|--all option
to the remove command also removes all software image revisions.


**Working With Objects:** clone **,** modified **,** swap
Continuing on with the node object node100 that was created in the previous example, it can be cloned
to node101 as follows:


**Example**


[mycluster->device]% clone node100 node101

Warning: The Ethernet switch settings were not cloned, and have to be set manually

[mycluster->device*[node101*]]% exit

[mycluster->device*]% modified

State Type Name

------ ------------------------ ----------------------------------
+ Device node101

[mycluster->device*]% commit

[mycluster->device]%

[mycluster->device]% remove node100

[mycluster->device*]% commit

[mycluster->device]%


The modified command is used to check what objects have uncommitted changes, and the new
object node101 that is seen to be modified, is saved with a commit . The device node100 is then removed
by using the remove command. A commit executes the removal.
The modified command corresponds roughly to the functionality of the Unsaved entities icon in
figure 10.5.


**2.5 Cluster Management Shell** **53**


The “ + ” entry in the State column in the output of the modified command in the preceding example
indicates the object is a newly added one, but not yet committed. Similarly, a “ � ” entry indicates an object that is to be removed on committing, while a blank entry indicates that the object has been modified
without an addition or removal involved.

Cloning an object is a convenient method of duplicating a fully configured object. When duplicating
a device object, cmsh will attempt to automatically assign a new IP address using a number of heuristics.
In the preceding example, node101 is assigned IP address 10.141.0.101 .
The attempt is a best-effort, and does not guarantee a sensibly-configured object. The cluster administrator should therefore inspect the result.
Sometimes an object may have been misnamed, or physically swapped. For example, node001 exchanged physically with node002 in the rack, or the hardware device eth0 is misnamed by the kernel
and should be eth1 . In that case it can be convenient to simply swap their names via the cluster manager
front end rather than change the physical device or adjust kernel configurations. This is equivalent to
exchanging all the attributes from one name to the other.
For example, if the two interfaces on the head node need to have their names exchanged, it can be
done as follows:


[mycluster->device]% use mycluster

[mycluster->device[mycluster]]% interfaces

[mycluster->device[mycluster]->interfaces]% list

Type Network device name IP Network

------------ -------------------- ---------------- -------------
physical eth0 [dhcp] 10.150.4.46 externalnet
physical eth1 [prov] 10.141.255.254 internalnet

[basecm11->device[mycluster]->interfaces]% swap eth0 eth1; commit

[basecm11->device[mycluster]->interfaces]% list

Type Network device name IP Network

------------ -------------------- ---------------- -------------
physical eth0 [prov] 10.141.255.254 internalnet
physical eth1 [dhcp] 10.150.4.46 externalnet

[mycluster->device[mycluster]->interfaces]% exit; exit


**Working With Objects:** get **,** set **,** refresh
The get command is used to retrieve a specified property from an object, and set is used to set it:


**Example**


[mycluster->device]% use node101

[mycluster->device[node101]]% get category

test-category

[mycluster->device[node101]]% set category default

[mycluster->device*[node101*]]% get category

default

[mycluster->device*[node101*]]% modified

State Type Name

------ ------------------------ ------------------------------
Device node101

[mycluster->device*[node101*]]% refresh

[mycluster->device[node101]]% modified

No modified objects of type device

[mycluster->device[node101]]% get category

test-category

[mycluster->device[node101]]%


Here, the category property of the node101 object is retrieved by using the get command. The


**54** **Cluster Management With NVIDIA Base Command Manager**


property is then changed using the set command. Using get confirms that the value of the property
has changed, and the modified command reconfirms that node101 has local uncommitted changes.
The refresh command undoes the changes made, and corresponds roughly to the Revert button in
Base View when viewing Unsaved entities (figure 10.5). The modified command then confirms that
no local changes exist. Finally the get command reconfirms that no local change took place.
Among the possible values a property can take on are strings and booleans:


  - A string can be set as a revision label for any object:


**Example**


[mycluster->device[node101]]% set revision "changed on 10th May"

[mycluster->device*[node101*]]% get revision

[mycluster->device*[node101*]]% changed on 10th May 2011


This can be useful when using shell scripts with an input text to label and track revisions when
sending commands to cmsh . How to send commands from the shell to cmsh is introduced in
section 2.5.1.


  - For booleans, the values “ yes ”, “ 1 ”, “ on ” and “ true ” are equivalent to each other, as are their
opposites “ no ”, “ 0 ”, “ off ” and “ false ”. These values are case-insensitive.


**Working With Objects:** clear
**Example**


[mycluster->device]% set node101 mac 00:11:22:33:44:55

[mycluster->device*]% get node101 mac

00:11:22:33:44:55

[mycluster->device*]% clear node101 mac

[mycluster->device*]% get node101 mac

00:00:00:00:00:00

[mycluster->device*]%


The get and set commands are used to view and set the MAC address of node101 without running
the use command to make node101 the _current object_ . The clear command then unsets the value of the
property. The result of clear depends on the type of the property it acts on. In the case of string properties, the empty string is assigned, whereas for MAC addresses the special value 00:00:00:00:00:00
is assigned.


**Working With Objects:** list **,** format **,** sort
The list command is used to list objects in a mode. The command has many options. The ones that are
valid for the current mode can be viewed by running help list . The -f|--format option is available
in all modes, and takes a format string as argument. The string specifies what properties are printed for
each object, and how many characters are used to display each property in the output line. In following
example a list of objects is requested for device mode, displaying the hostname, switchports and ip
properties for each device object.


**Example**


[basecm11->device]% list -f hostname:14,switchports:15,ip
hostname (key) switchports ip

-------------- --------------- -------------------
apc01 10.142.254.1

basecm11 switch01:46 10.142.255.254

node001 switch01:47 10.142.0.1

node002 switch01:45 10.142.0.2

switch01 10.142.253.1

[basecm11->device]%


**2.5 Cluster Management Shell** **55**


Running the list command with no argument uses the current format string for the mode.
Running the format command without arguments displays the current format string, and also displays all available properties including a description of each property. For example (output truncated):


**Example**


[basecm11->device]% format

Current list printing format:

----------------------------
type:22, hostname:[16-32], mac:18, category:[16-32], ip:15, network:[14-32], status:[16-32]


Valid fields:

------------
activation : Date on which node was defined

additionalhostnames : List of additional hostnames that should resolve to the interfaces IP address

allownetworkingrestart : Allow node to update ifcfg files and restart networking

banks : Number of banks

...


The print specification of the format command uses the delimiter “ : ” to separate the parameter and
the value for the width of the parameter column. For example, a width of 10 can be set with:


**Example**


[basecm11->device]% format hostname:10

[basecm11->device]% list

hostname (

---------
apc01

basecm11

node001

node002

switch01


A range of widths can be set, from a minimum to a maximum, using square brackets. A single
minimum width possible is chosen from the range that fits all the characters of the column. If the
number of characters in the column exceeds the maximum, then the maximum value is chosen. For
example:


**Example**


[basecm11->device]% format hostname:[10-14]

[basecm11->device]% list

hostname (key)

-------------
apc01

basecm11

node001

node002

switch01


The parameters to be viewed can be chosen from a list of valid fields by running the format command
without any options, as shown earlier.
The format command can take as an argument a string that is made up of multiple parameters in a
comma-separated list. Each parameter takes a colon-delimited width specification.


**Example**


**56** **Cluster Management With NVIDIA Base Command Manager**


[basecm11->device]% format hostname:[10-14],switchports:14,ip:20

[basecm11->device]% list

hostname (key) switchports ip

-------------- -------------- -------------------
apc01 10.142.254.1

basecm11 switch01:46 10.142.255.254

node001 switch01:47 10.142.0.1

node002 switch01:45 10.142.0.2

switch01 10.142.253.1


The output of the format command without arguments shows the current list printing format string,
with spaces. This can be used with enclosing quotes ( " ).
In general, the string used in the format command can be set with enclosing quotes ( " ), or alternatively, with the spaces removed:


**Example**


[basecm11->device]% format "hostname:[16-32], network:[14-32], status:[16-32]"


_or_


[basecm11->device]% format hostname:[16-32],network:[14-32],status:[16-32]


The default parameter settings can be restored with the -r|--reset option:


**Example**


[basecm11->device]% format -r

[basecm11->device]% format | head -3

Current list printing format:

----------------------------
type:22, hostname:[16-32], mac:18, category:[16-32], ip:15, network:[14-32], status:[16-32]

[basecm11->device]%


The sort command sorts output in alphabetical order for specified parameters when the list command is run. The sort is done according to the precedence of the parameters passed to the sort command:


**Example**


[basecm11->device]% sort type mac

[basecm11->device]% list -f type:15,hostname:15,mac
type hostname (key) mac

--------------- --------------- -------------------
HeadNode basecm11 08:0A:27:BA:B9:43

PhysicalNode node002 00:00:00:00:00:00

PhysicalNode log001 52:54:00:DE:E3:6B

[basecm11->device]% sort type hostname

[basecm11->device]% list -f type:15,hostname:15,mac
type hostname (key) mac

--------------- --------------- -------------------
HeadNode basecm11 08:0A:27:BA:B9:43

PhysicalNode log001 52:54:00:DE:E3:6B

PhysicalNode node002 00:00:00:00:00:00


[basecm11->device]% sort mac hostname

[basecm11->device]% list -f type:15,hostname:15,mac


**2.5 Cluster Management Shell** **57**


type hostname (key) mac

--------------- --------------- -------------------
PhysicalNode node002 00:00:00:00:00:00

HeadNode basecm11 08:0A:27:BA:B9:43

PhysicalNode log001 52:54:00:DE:E3:6B


The preceding sort commands can alternatively be specified with the -s|--sort option to the list
command:


[basecm11->device]% list -f type:15,hostname:15,mac --sort type,mac

[basecm11->device]% list -f type:15,hostname:15,mac --sort type,hostname

[basecm11->device]% list -f type:15,hostname:15,mac --sort mac,hostname


**Working With Objects:** append **,** removefrom
When dealing with a property of an object that can take more than one value at a time—a list of values—
the append and removefrom commands can be used to respectively append to and remove elements from
the list. If more than one element is appended, they should be space-separated. The set command may
also be used to assign a new list at once, overwriting the existing list. In the following example values are
appended and removed from the powerdistributionunits properties of device node001 . The powerdistributionunits properties represent the list of ports on power distribution units that a particular
device is connected to. This information is relevant when power operations are performed on a node.
Chapter 4 has more information on power settings and operations.


**Example**


[mycluster->device]% use node001

[mycluster->device[node001]]% get powerdistributionunits

apc01:1

[...device[node001]]% append powerdistributionunits apc01:5

[...device*[node001*]]% get powerdistributionunits

apc01:1 apc01:5

[...device*[node001*]]% append powerdistributionunits apc01:6

[...device*[node001*]]% get powerdistributionunits

apc01:1 apc01:5 apc01:6

[...device*[node001*]]% removefrom powerdistributionunits apc01:5

[...device*[node001*]]% get powerdistributionunits

apc01:1 apc01:6

[...device*[node001*]]% set powerdistributionunits apc01:1 apc01:02

[...device*[node001*]]% get powerdistributionunits

apc01:1 apc01:2


**Working With Objects:** usedby
Removing a specific object is only possible if other objects do not have references to it. To help the administrator discover a list of objects that depend on (“use”) the specified object, the usedby command
may be used. In the following example, objects depending on device apc01 are requested. The usedby
property of powerdistributionunits indicates that device objects node001 and node002 contain references to (“use”) the object apc01 . In addition, the apc01 device is itself displayed as being in the up state,
indicating a dependency of apc01 on itself. If the device is to be removed, then the 2 references to it first
need to be removed, and the device also first has to be brought to the CLOSED state (page 274) by using
the close command.


**Example**


[mycluster->device]% usedby apc01

Device used by the following:

Type Name Parameter


**58** **Cluster Management With NVIDIA Base Command Manager**


---------------- ---------- ---------------------
Device apc01 Device is up

Device node001 powerDistributionUnits

Device node002 powerDistributionUnits

[mycluster->device]%


**Working With Objects:** validate
Whenever committing changes to an object, the cluster management infrastructure checks the object to
be committed for consistency. If one or more consistency requirements are not met, then cmsh reports
the violations that must be resolved before the changes are committed. The validate command allows
an object to be checked for consistency without committing local changes.


**Example**


[mycluster->device]% use node001

[mycluster->device[node001]]% clear category

[mycluster->device*[node001*]]% commit

Code Field Message

----- ------------------------ --------------------------
1 category The category should be set

[mycluster->device*[node001*]]% set category default

[mycluster->device*[node001*]]% validate

All good

[mycluster->device*[node001*]]% commit

[mycluster->device[node001]]%


**Working With Objects:** show
The show command is used to show the parameters and values of a specific object. For example for the
object node001, the attributes displayed are (some output ellipsized):


[mycluster->device[node001]]% show

Parameter Value

--------------------------------------- -----------------------------------
Activation Thu, 03 Aug 2017 15:57:42 CEST

BMC Settings <submode>

Block devices cleared on next boot

Category default

...

Data node no

Default gateway 10.141.255.254 (network: internalnet)

...

Software image default-image

Static routes <0 in submode>

...


**Working With Objects:** assign **,** unassign
The assign and unassign commands are analogous to add and remove . The difference between assign
and add from the system administrator point of view is that assign sets an object with settable properties
from a choice of existing names, whereas add sets an object with settable properties that include the name
that is to be given. This makes assign suited for cases where multiple versions of a specific object choice
cannot be used.

For example,


  - If a node is to be configured to be run with particular Slurm settings, then the node can be assigned
an slurmclient role (section 2.1.5) with the assign command. The node cannot be assigned another slurmclient role with other Slurm settings at the same time. Only the settings within the
assigned Slurm client role can be changed.


**2.5 Cluster Management Shell** **59**


  - If a node is to be configured to run with added interfaces eth3 and eth4, then the node can have
both physical interfaces added to it with the add command.


The only place where the assign command is currently used within cmsh is within the roles submode, available under category mode, configurationoverlay mode, or device mode. Within roles,
assign is used for assigning roles objects to give properties associated with that role to the category,
configuration overlay, or device.


**Working With Objects:** import **For Roles**
The import command is an advanced command that works within a role. It is used to clone roles
between entities.

A node inherits all roles from the category and configuration overlay it is a part of.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device roles node001

[basecm11->device[node001]->roles]% list

Name (key)

------------------------------
[category:default] cgroupsupervisor

[category:default] slurmclient


If there is a small change to the default roles to be made, only for node001, in slurmclient, then the
role can be imported from a category or overlay. Importing the role duplicates the object and assigns the
duplicated value to node001 .
This differs from simply assigning a slurmclient role to node001, because importing provides the
values from the category or overlay, whereas assigning provides unset values.
After running import, just as for assign, changes to the role made at node001 level stay at that node
level, and changes made to the category-level or overlay-level slurmclient role are not automatically
inherited by the node001 slurmclient role.


**Example**


[basecm11->device[node001]->roles]% import _<TAB><TAB>_

backup etcd::host pbsproclient

boot failover pbsproserver

...

... _and other available roles including_ slurmclient...

[basecm11->device[node001]->roles]% import --overlay slurm-client slurmclient

[basecm11->device*[node001*]->roles*]% list

Name (key)

------------------------------
[category:default] cgroupsupervisor

slurmclient

[basecm11->device*[node001*]->roles*]% set slurmclient queues node1q

[basecm11->device*[node001*]->roles*]% commit


The preceding shows that a list of possible roles is prompted for via tab-completion after having
typed import, and that the settings from the configuration overlay level are brought into node001 for
the slurmclient role. The slurmclient values at node level then override any of the overlay level or
category level settings, as suggested by the new list output. The Slurm client settings are then the same
for node001 as the settings at the overlay level. The only change made is that a special queue, node1q, is
configured just for node001 .
The import command in roles mode can duplicate any role between any two entities. Options can
be used to import from a category ( -c|--category ), or a node ( -n|--node ), or an overlay ( -o|--overlay ),
as indicated by its help text ( help import ).


**60** **Cluster Management With NVIDIA Base Command Manager**


**2.5.4** **Accessing Cluster Settings**
The management infrastructure of BCM is designed to allow cluster partitioning in the future. A cluster
partition can be viewed as a virtual cluster inside a real cluster. The cluster partition behaves as a
separate cluster while making use of the resources of the real cluster in which it is contained. Although
cluster partitioning is not yet possible in the current version of BCM, its design implications do decide
how some global cluster properties are accessed through cmsh .
In cmsh there is a partition mode which will, in a future version, allow an administrator to create
and configure cluster partitions. Currently, there is only one fixed partition, called base . The base
partition represents the physical cluster as a whole and cannot be removed. A number of properties
global to the cluster exist inside the base partition. These properties are referenced and explained in
remaining parts of this manual.


**Example**


[root@myheadnode ~]# cmsh

[myheadnode]% partition use base

[myheadnode->partition[base]]% show

Parameter Value

-------------------------------- -----------------------------------------------
Cluster name mycluster

Revision

Cluster reference architecture

Administrator e-mail gandalf@example.com

Name base

Headnode myheadnode

Node basename node

Node digits 3

Name servers

Name servers from dhcp 10.3.100.100

Time servers 0.pool.ntp.org,1.pool.ntp.org,2.pool.ntp.org

Search domains example.com

Relay Host

Externally visible IP 0.0.0.0
Time zone Europe/Amsterdam

BMC Settings <submode>

SNMP Settings <submode>

DPU Settings <submode>

SELinux Settings <submode>

Access Settings <submode>

Provisioning Settings <submode>

ZTP settings <submode>

ZTP new switch settings <submode>

NetQ settings <submode>

Default burn configuration default-destructive

External network externalnet

Management network internalnet

No zero conf no

Default category default

ArchOS <0 in submode>

Fabrics <0 in submode>

Sign installer certificates AUTO

Failover not defined

Failover groups <0 in submode>

Burn configs <3 in submode>

Notes <0B>


**2.5 Cluster Management Shell** **61**


**2.5.5** **Advanced** cmsh **Features**

This section describes some advanced features of cmsh and may be skipped on first reading.


**Command Line Editing**
Command line editing and history features from the readline library are available. [http://tiswww.](http://tiswww.case.edu/php/chet/readline/rluserman.html)
[case.edu/php/chet/readline/rluserman.html](http://tiswww.case.edu/php/chet/readline/rluserman.html) provides a full list of key-bindings.
For users who are reasonably familiar with the bash shell running with readline, probably the most
useful and familiar features provided by readline within cmsh are:


  - tab-completion of commands and arguments


  - being able to select earlier commands from the command history using <ctrl>-r, or using the upand down-arrow keys


**History And Timestamps**
The history command within cmsh explicitly displays the cmsh command history as a list.
The --timestamps|-t option to the history command displays the command history with timestamps.


**Example**


[basecm11->device[node001]]% history | tail -3

162 use node001

163 history
164 history | tail -3

[basecm11->device[node001]]% history -t | tail -3

163 Thu Dec 3 15:15:18 2015 history
164 Thu Dec 3 15:15:43 2015 history | tail -3
165 Thu Dec 3 15:15:49 2015 history -t | tail -3


This history is saved in the file .cm/.cmshhistory in the cmsh user’s directory. The timestamps in
the file are in unix epoch time format, and can be converted to human-friendly format with the standard
date utility.


**Example**


[root@mycluster ~]# tail -2 .cm/.cmshhistory

1615412046

device list

[root@mycluster ~]# date -d @1615412046

Wed Mar 10 22:34:06 CET 2021


**Mixing** cmsh **And Unix Shell Commands**
It is often useful for an administrator to be able to execute unix shell commands while carrying out
cluster management tasks. The cluster manager shell, cmsh, therefore allows users to execute commands
in a subshell if the command is prefixed with a “ ! ” character:


**Example**


[mycluster]% !hostname -f

mycluster.cm.cluster

[mycluster]%


Executing the ! command by itself will start an interactive login sub-shell. By exiting the sub-shell,
the user will return to the cmsh prompt.
Besides simply executing commands from within cmsh, the output of operating system shell commands can also be used within cmsh . This is done by using the legacy-style “backtick syntax” available
in most unix shells.


**62** **Cluster Management With NVIDIA Base Command Manager**


**Example**


[mycluster]% device use `hostname`

[mycluster->device[mycluster]]% status
mycluster ................ [ UP ]

[mycluster->device[mycluster]]%


**Output Redirection**
Similar to unix shells, cmsh also supports output redirection to the shell through common operators such
as -, >>, and | .


**Example**


[mycluster]% device list > devices

[mycluster]% device status >> devices

[mycluster]% device list | grep node001
Type Hostname (key) MAC (key) Category

-------------- -------------- ------------------- ---------
PhysicalNode node001 00:E0:81:2E:F7:96 default


**Input Redirection**
Input redirection with cmsh is possible. As is usual, the input can be a string or a file. For example, for a
file runthis with some commands stored in it:


**Example**


[root@mycluster ~]# cat runthis

device

get node001 ip


the commands can be run with the redirection operator as:


**Example**


[root@mycluster ~]# cmsh < runthis

device

get node001 ip

10.141.0.1


Running the file with the -f option avoids echoing the commands


**Example**


[root@mycluster ~]# cmsh -f runthis

10.141.0.1


**The** ssh **Command**

The ssh command is run from within the device mode of cmsh . If an ssh session is launched from within

cmsh, then it clears the screen and is connected to the specified node. Exiting from the ssh session returns
the user back to the cmsh launch point.


**Example**


[basecm11]% device ssh node001

< _screen is cleared_ 
< _some MOTD text and login information is displayed_ 
[root@node001 ~]# exit

Connection to node001 closed.


**2.5 Cluster Management Shell** **63**


[basecm11]% device use basecm11

[basecm11->device[basecm11]]% #now let us connect to the head node from the head node object

[basecm11->device[basecm11]]% ssh

< _screen is cleared_ 
< _some MOTD text and login information is displayed_ 
[root@basecm11 ~]# exit

logout

Connection to basecm11 closed.

[basecm11->device[basecm11]]%


An alternative to running ssh within cmsh is to launch it in a subshell anywhere from within cmsh,
by using !ssh .


**The** time **Command**

The time command within cmsh is a simplified version of the standard unix time command.
The time command takes as its argument a second command that is to be executed within cmsh .
On execution of the time command, the second command is executed. After execution of the time
command is complete, the time the second command took to execute is displayed.


**Example**


[basecm11->device]% time ds node001

node001 .................. [ UP ]

time: 0.108s


**The** watch **Command**

The watch command within cmsh is a simplified version of the standard unix watch command.
The watch command takes as its argument a second command that is to be executed within cmsh .
On execution of the watch command, the second command is executed every 2 seconds by default, and
the output of that second command is displayed.
The repeat interval of the watch command can be set with the --interval|-n option. A running
watch command can be interrupted with a <Ctrl>-c .


**Example**


[basecm11->device]% watch newnodes

_screen clears_

Every 2.0s: newnodes Thu Dec 3 13:01:45 2015

No new nodes currently available.


**Example**


[basecm11->device]% watch -n 3 status -n node001,node002

_screen clears_

Every 3.0s: status -n node001,node002 Thu Jun 30 17:53:21 2016

node001 ...............[ UP ]

node002 ...............[ UP ]


**Looping Over Objects With** foreach
It is frequently convenient to be able to execute a cmsh command on several objects at once. The foreach
command is available in a number of cmsh modes for this purpose. A foreach command takes a list of
space-separated object names (the keys of the object) and a list of commands that must be enclosed by
parentheses, i.e.: “(” and “)”. The foreach command will then iterate through the objects, executing the
list of commands on the iterated object each iteration.


**64** **Cluster Management With NVIDIA Base Command Manager**


**Basic syntax for the** foreach **command:** The basic foreach syntax is:


foreach _<_ _object_ 1 _> <_ _object_ 2 _> · · ·_ ( _<_ _command_ 1 _>_ ; _<_ _command_ 2 _> · · ·_ )


**Example**


[mycluster->device]% foreach node001 node002 (get hostname; status)

node001

node001 ............. [ UP ]

node002

node002 ............. [ UP ]

[mycluster->device]%


With the foreach command it is possible to perform set commands on groups of objects simultaneously, or to perform an operation on a group of objects. The range command (page 68) provides an
alternative to it in many cases.


**Advanced options for the** foreach **command:** The foreach command advanced options can be viewed
from the help page:


[root@basecm11 ~]# cmsh -c "device help foreach"


The options can be classed as: grouping options (list, type), adding options, conditional options, and
looping options.


 - **Grouping options:**


**–** -n|--nodes, -g|--group, -c|--category, -r|--rack, -h|--chassis, -e|--overlay,
-l|--role, -m|--image, -u|--union, -i|--intersection


**–**
-t|--type chassis|fabricresourcebox|fabricswitch|genericdevice|litenode|cloudnode|
dpu|physicalnode|headnode|powerdistributionunit|racksensor|switch|unmanagednode


There are two forms of grouping options shown in the preceding text. The first form uses a list
of the objects being grouped, while the second form uses the type of the objects being grouped.
These options become available according to the cmsh mode used.


In the device mode of cmsh, for example, the foreach command has many grouping options
available. If objects are specifed with a grouping option, then the specified objects can be looped

over.


For example, with the list form, the --category ( -c ) option takes a node category argument (or
several categories), while the --node ( -n ) option takes a node-list argument. Node-lists (specification on page 67) can also use the following, more elaborate, syntax:
_<_ _node_ _>_, . . ., _<_ _node_ _>_, _<_ _node_ _>_ .. _<_ _node_ _>_


**Example**


[demo->device]% foreach -c default (status)

node001 ............. [ DOWN ]

node002 ............. [ DOWN ]

[demo->device]% foreach -g rack8 (status)

...

[demo->device]% foreach -n node001,node008..node016,node032 (status)

...

[demo->device]%


**2.5 Cluster Management Shell** **65**


With the type form, using the -t|--type option, the literal value to this option must be one of
node, cloudnode, virtualnode, and so on.


If multiple grouping options are used, then the union operation takes place by default.


Both grouping option forms are often used in commands other than foreach for node selection.


 - **Adding options:** -o|--clone **,** -a|--add
**The** --clone **(** -o **) option** allows the cloning (section 2.5.3) of objects in a loop. In the following
example, from device mode, node001 is used as the base object from which other nodes from
node022 up to node024 are cloned:


**Example**


[basecm11->device]% foreach --clone node001 -n node022..node024 ()

[basecm11->device*]% list | grep node
Type Hostname (key) Ip

------------ -------------- ----------
PhysicalNode node001 10.141.0.1

PhysicalNode node022 10.141.0.22

PhysicalNode node023 10.141.0.23

PhysicalNode node024 10.141.0.24

[basecm11->device*]% commit


To avoid possible confusion: the cloned objects are merely objects (placeholder schematics and
settings, with some different values for some of the settings, such as IP addresses, decided by
heuristics). So it is explicitly not the software disk image of node001 that is duplicated by object
cloning to the other nodes by this action at this time.


**– Overriding the default heuristics for IP address allocation:** The default heuristics for IP
address allocation choose the next free IP address if, among other conditions, the same base
name is used for the clone. Thus, if the base name used differs from the original, then by
default the next free IP address is not chosen. To override the heuristic, so that the next free
IP address is chosen anyway, the --next-ip option can be used.

For example, when creating nodes starting with node02 instead of the default node002 :


**Example**


[basecm11->device]% foreach -o node001 -n node[02-04] ()

Base name mismatch, IP settings will not be modified!

Base name mismatch, IP settings will not be modified!

Base name mismatch, IP settings will not be modified!

[basecm11->device*]% network ips internalnet

Hostname IP State

----------------- ---------------- ---------------
basecm11 10.141.255.254 ok

node001 10.141.0.1 duplicate

node02 10.141.0.1 duplicate

node03 10.141.0.1 duplicate

node04 10.141.0.1 ok


[basecm11->device]% foreach -o node001 -n node[02-04] --next-ip ()

[basecm11->device*]% network ips internalnet

Hostname IP State

----------------- ---------------- ---------------
basecm11 10.141.255.254 ok


**66** **Cluster Management With NVIDIA Base Command Manager**


node001 10.141.0.1 ok

node02 10.141.0.2 ok

node03 10.141.0.3 ok

node04 10.141.0.4 ok


Conversely, IP addresses can be incremented by a specific amount when using the
addinterface command (section 3.7.1), by using its --increment option.


**The** --add **(** -a **) option** creates the device for a specified device type, if it does not exist. Valid types
are shown in the help output, and include physicalnode, headnode, switch .


 - **Conditional options:** -s|--status **,** -q|--quitonunknown
**The** --status **(** -s **) option** allows nodes to be filtered by the device status (section 2.1.1).


**Example**


[basecm11->device]% foreach -n node001..node004 --status UP (get IP)

10.141.0.1

10.141.0.3


Since the --status option is also a grouping option, the union operation applies to it by default
too, when more than one grouping option is being run.


**The** --quitonunknown **(** -q **) option** allows the foreach loop to be exited when an unknown command is detected.


 - **Looping options:**  - **,** -v|--verbose
**The wildcard character**   - **with** foreach implies all the objects that the list command lists for that
mode. It is used without grouping options:


**Example**


[myheadnode->device]% foreach * (get ip; status)

10.141.253.1

switch01 ............ [ DOWN ]

10.141.255.254

myheadnode .......... [ UP ]

10.141.0.1

node001 ............. [ CLOSED ]

10.141.0.2

node002 ............. [ CLOSED ]

[myheadnode->device]%


Another example that lists all the nodes per category, by running the listnodes command within
category mode:


**Example**


[basecm11->category]% foreach * (get name; listnodes)

default

Type Hostname MAC Category Ip Network Status

------------- --------- ------------------ --------- ---------- ------------ -------
PhysicalNode node001 FA:16:3E:79:4B:77 default 10.141.0.1 internalnet [ UP ]
PhysicalNode node002 FA:16:3E:41:9E:A8 default 10.141.0.2 internalnet [ UP ]
PhysicalNode node003 FA:16:3E:C0:1F:E1 default 10.141.0.3 internalnet [ UP ]


bf The --verbose ( -v ) option displays the loop headers during a running loop with time stamps,
which can help in debugging.


**2.5 Cluster Management Shell** **67**


**Node List Syntax**
Node list specifications, as used in the foreach specification and elsewhere, can be of several types.
These types are best explained with node list specification examples:


 - **adhoc (with a comma, or a space):**
example: node001,node003,node005,node006


 - **sequential (with two dots or square brackets):**
example: node001..node004
or, equivalently: node00[1-4]
which is: node001,node002,node003,node004


 - **sequential extended expansion (only for square brackets):**
example: node[001-002]s[001-005]
which is:
node001s001,node001s002,node001s003,node001s004,node001s005, _\_

node002s001,node002s002,node002s003,node002s004,node002s005


 - **rack-based:**

This is intended to hint which rack a node is located in. Thus:


**–** example: r[1-2]n[01-03]
which is: r1n01,r1n02,r1n03,r2n01,r2n02,r2n03
This might hint at two racks, r1 and r2, with 3 nodes each.


**–** example: rack[1-2]node0[1-3]
which is: rack1node01,rack1node02,rack1node03,rack2node01,

rack2node02,rack2node03
Essentially the same as the previous one, but for nodes that were named more verbosely.


 - **sequential exclusion (negation):**
example: node001..node005,-node002..node003
which is: node001,node004,node005


 - **sequential stride (every <** _**stride**_ **> steps):**
example: node00[1..7:2]
which is: node001,node003,node005,node007


 - **mixed list:**

The square brackets and the two dots input specification cannot be used at the same time in one
argument. Other than this, specifications can be mixed:


**–**
example: r1n001..r1n003,r2n003
which is: r1n001,r1n002,r1n003,r2n003


**–**
example: r2n003,r[3-5]n0[01-03]
which is: r2n003,r3n001,r3n002,r3n003,r4n001,r4n002,r4n003,r5n001,r5n002,r5n003


**–**
example: node[001-100],-node[004-100:4]
which is: every node in the 100 nodes, except for every fourth node.


 - **path to file that contains a list of nodes:**
example: �/some/filepath/< _file with list of nodes_   The caret sign is a special character in cmsh for node list specifications. It indicates the string that
follows is a file path that is to be read.


Node list syntax is a customized subset of device list syntax. As such, when using devices other than
nodes, some of the syntax from node list syntax may not work as expected.


**68** **Cluster Management With NVIDIA Base Command Manager**


**Setting grouping syntax with the** groupingsyntax **command:** “Grouping syntax” here refers to usage
of dots and square brackets. In other words, it is syntax of how a grouping is marked so that it is accepted
as a list. The list that is specified in this manner can be for input or output purposes.
The groupingsyntax command sets the grouping syntax using the following options:


 - bracket : the square brackets specification.


 - dot : the two dots specification.


 - auto : the default. Setting auto means that:


**–** either the dot or the bracket specification are accepted as input,


**–** the dot specification is used for output.


The chosen groupingsyntax option can be made persistent by adding it to the .cmshrc dotfiles, or
to /etc/cmshrc (section 2.5.1).


**Example**


[root@basecm11 ~]# cat .cm/cmsh/.cmshrc

groupingsyntax auto


**The** range **Command**
The range command provides an interactive option to carry out basic foreach commands over a grouping of nodes. When the grouping option has been chosen, the cmsh prompt indicates the chosen range
within braces ( {} ).


**Example**


[basecm11->device]% range -n node0[01-24]

[basecm11->device{-n node001..024}]%


In the preceding example, commands applied at device level will be applied to the range of 24 node
objects.
Continuing the preceding session—if a category can be selected with the -c option. If the default
category just has three nodes, then output displayed could look like:


**Example**


[basecm11->device{-n node001..024}]% range -c default

[basecm11->device{-c default}]% ds

node001 .................. [ UP ] state flapping

node002 .................. [ UP ]

node003 .................. [ UP ]


Values can be set at device mode level for the selected grouping.


**Example**


[basecm11->device{-c default}]% get revision


[basecm11->device{-c default}]% set revision test

[basecm11->device{-c default}]% get revision

test

test

test


**2.5 Cluster Management Shell** **69**


Values can also be set within a submode. However, staying in the submode for a full interaction
is not possible. The settings must be done by entering the submode via a semi-colon (new command
statement continuation on same line) syntax, as follows:


**Example**


[basecm11->device{-c default}]% roles; assign pbsproclient; commit


The range command can be regarded as a modal way to carry out an implicit foreach on the grouping object. Many administrators should find it easier than a foreach :


**Example**


[basecm11->device{-c default}]% get ip

10.141.0.1

10.141.0.2

10.141.0.3

[basecm11->device{-c default}]% ..

[basecm11->device]% foreach -c default (get ip)

10.141.0.1

10.141.0.2

10.141.0.3


Commands can be run inside a range. However, running a pexec command inside a range is typically not the intention of the cluster administrator, even though it can be done:


**Example**


[basecm11->device]% range -n node[001-100]

[basecm11->device{-n node[001-100]}]% pexec -n node[001-100] hostname


The preceding starts 100 pexec commands, each running on each of the 100 nodes.
Further options to the range command can be seen with the help text for the command (output
truncated):


**Example**


[root@basecm11 ~]# cmsh -c "device help range"

Name: range - Set a range of several devices to execute future commands on


Usage: range [OPTIONS] * (command)
range [OPTIONS] <device> [<device> ...] (command)


Options: --show Show the current range

--clear Clear the range

-v, --verbose Show header before each element

...


**The** bookmark **And** goto **Commands**
**Bookmarks:** A _bookmark_ in cmsh is a location in the cmsh hierarchy.
A bookmark can be


  - set with the bookmark command


  - reached using the goto command


A bookmark is set with arguments to the bookmark command within cmsh as follows:


  - The user can set the current location as a bookmark:


**70** **Cluster Management With NVIDIA Base Command Manager**


**–**
by using no argument. This is the same as setting no name for it


**–**
by using an arbitrary argument. This is the same as setting an arbitrary name for it


  - Apart from any user-defined bookmark names, cmsh automatically sets the special name: “-”. This
is always the previous location in the cmsh hierarchy that the user has just come from.


All bookmarks that have been set can be listed with the -l|--list option.


**Reaching a bookmark:** A bookmark can be reached with the goto command. The goto command can
take the following as arguments: a blank (no argument), any arbitrary bookmark name, or “-”. The
bookmark corresponding to the chosen argument is then reached.
The “-” bookmark does not need to be preceded by a goto .


**Example**


[mycluster]% device use node001

[mycluster->device[node001]]% bookmark

[mycluster->device[node001]]% bookmark -l

Name Bookmark

---------------- -----------------------
home;device;use node001;

- home;

[mycluster->device[node001]]% home

[mycluster]% goto

[mycluster->device[node001]]% goto 
[mycluster]% goto

[mycluster->device[node001]]% bookmark dn1

[mycluster->device[node001]]% goto 
[mycluster]% goto dn1

[mycluster->device[node001]]%


**Saving bookmarks, and making them persistent:** Bookmarks can be saved to a file, such as mysaved,
with the -s|--save option, as follows:


**Example**


[mycluster]% bookmark -s mysaved


Bookmarks can be made persistent by setting (.)cmshrc files (page 41) to load a previously-saved
bookmarks file whenever a new cmsh session is started. The bookmark command loads a saved bookmark file using the -x|--load option.


**Example**


[root@basecm11 ~]# cat .cm/cmsh/.cmshrc

bookmark -x mysaved


**Renaming Nodes With The** rename **Command**
Nodes can be renamed globally from within partition mode, in the Node basename field associated
with the prefix of the node in Base View (section 3.1.1) or in cmsh (section 2.5.4, and also page 104).
However, a more fine-grained batch renaming is also possible with the rename command, and typically avoids having to resort to scripting mechanisms. Using rename is best illustrated by examples:
The examples begin with using the default basename of node and default node digits (padded suffix
number length) of 3 .
A simple rename that is a prefix change, can then be carried out as:


**2.5 Cluster Management Shell** **71**


**Example**


[basecm11->device]% rename node001..node003 test

Renamed: node001 to test1

Renamed: node002 to test2

Renamed: node003 to test3


The rename starts up its own numbering from 1, independent of the original numbering. The change
is committed using the commit command.
Zero-padding occurs if the number of nodes is sufficiently large to need it. For example, if 10 nodes
are renamed (some output elided):


**Example**


[basecm11->device]% rename node[001-010] test

Renamed: node001 to test01

Renamed: node002 to test02

...

Renamed: node009 to test09

Renamed: node010 to test10


then 2 digits are used for each number suffix, in order to match the size of the last number.
String formatting can be used to specify the number of digits in the padded number field:


**Example**


[basecm11->device]% rename node[001-003] test%04d

Renamed: node001 to test0001

Renamed: node002 to test0002

Renamed: node003 to test0003


The target names can conveniently be specified exactly. It requires an exact name mapping. That is,
it assumes the source list size and target list size match:


**Example**


[basecm11->device]% rename node[001-005] test0[1,2,5-7]

Renamed: node001 to test01

Renamed: node002 to test02

Renamed: node003 to test05

Renamed: node004 to test06

Renamed: node005 to test07


The hostnames are sorted alphabetically before they are applied, with some exceptions based on the
listing method used.
A --dry-run option can be used to show how the devices will be renamed. Alternatively, the
refresh command can clear a proposed set of changes before a commit command commits the change,
although the refresh would also remove other pending changes.
Exact name mapping could be used to allocate individual servers to several people:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% rename node[001-004] alice,bob,charlie,dave

Renamed: node001 to alice

Renamed: node002 to bob

Renamed: node003 to charlie

Renamed: node004 to dave

[basecm11->device]% commit


**72** **Cluster Management With NVIDIA Base Command Manager**


Skipping by a number of nodes is possible using a colon ( : ). An example might be to skip by two so
that twin servers can be segregated into left/right.


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% device

[basecm11->device]% rename node[001-100:2] left[001-050]

Renamed: node001 to left001

Renamed: node003 to left002

...

Renamed: node097 to left049

Renamed: node099 to left050

[basecm11->device]% rename node[002-100:2] right[001-050]

Renamed: node002 to right001

Renamed: node004 to right002

...

Renamed: node098 to right049

Renamed: node100 to right050

[basecm11->device]% commit


**Using CMDaemon Environment Variables In Scripts**
Within device mode, the environment command shows the CMDaemon environment variables (section 3.3.2 of the _Developer Manual_ ) that can be passed to scripts for particular device.


**Example**


[mycluster->device]% environment node001

Key Value

---------------------------------------------- ---------------------------------------------------------------
CMD_ACTIVE_MASTER_IP 10.141.255.254

CMD_CATEGORY default

CMD_CLUSTERNAME mycluster

CMD_DEVICE_TYPE ComputeNode

CMD_ENVIRONMENT_CACHE_EPOCH_MILLISECONDS 1615465821582

CMD_ENVIRONMENT_CACHE_UPDATES 4

...


The environment variables can be prepared for use in Bash scripts with the -e|--export option:


**Example**


[mycluster->device]% environment -e node001

export CMD_ENVIRONMENT_CACHE_UPDATES=4

export CMD_CATEGORY=default

export CMD_SOFTWAREIMAGE=default-image

export CMD_DEVICE_TYPE=ComputeNode

export CMD_ROLES=

export CMD_FSMOUNT__SLASH_home_FILESYSTEM=nfs

export CMD_NODEGROUPS=

...


**Creating JSON Format Output From A Table Format Output In** cmsh
A list of table entries can be converted to a JSON representation by using the delimiter specification
option: -d {}
By default, the indentation value used is 2. Other values can be set by putting the value inside the
braces.


**2.6 Cluster Management Daemon** **73**


**Example**


[basecm11->device]% list -f hostname,ip,mac,status
hostname (key) ip mac status

-------------------- -------------------- -------------------- -------------------
node001 10.141.0.1 FA:16:3E:95:80:9F [ UP ]

basecm11 10.141.255.254 FA:16:3E:D3:56:E0 [ UP ]


[basecm11->device]% color off; list -f hostname,ip,mac,status -d {}

[

{

"hostname (key)": "basecm11",

"ip": "10.141.255.254",

"mac": "FA:16:3E:D3:56:E0",

"status": "[ UP ]"

},

{

"hostname (key)": "node001",

"ip": "10.141.0.1",

"mac": "FA:16:3E:95:80:9F",

"status": "[ UP ]"

}

]

[basecm11->device]%


The color off setting is needed to remove the default console coloring. If the command is to run
from the bash shell, the same output can be achieved with:


**Example**


[root@basecm11 ~]# cmsh --color=no -c "device; list -f hostname,ip,mac,status -d {}"


**2.6** **Cluster Management Daemon**


The _cluster management daemon_ or _CMDaemon_ is a server process that runs on all nodes of the cluster
(including the head node). The cluster management daemons work together to make the cluster manageable. When applications such as cmsh and Base View communicate with the cluster, they are actually
interacting with the cluster management daemon running on the head node. Cluster management applications never communicate directly with cluster management daemons running on non-head nodes.
The CMDaemon application starts running on any node automatically when it boots, and the application continues running until the node shuts down. Should CMDaemon be stopped manually for
whatever reason, its cluster management functionality becomes unavailable, making it hard for administrators to manage the cluster. However, even with the daemon stopped, the cluster remains fully
usable for running computational jobs using a workload manager.
The only route of communication with the cluster management daemon is through TCP port 8081 .
The cluster management daemon accepts only SSL connections, thereby ensuring all communications
are encrypted. Authentication is also handled in the SSL layer using client-side X509v3 certificates (section 2.3).
On the head node, the cluster management daemon uses a MySQL database server to store all of its
internal data. Raw monitoring data, on the other hand, is stored as binary data outside of the MySQL
database (section 14.8).


**74** **Cluster Management With NVIDIA Base Command Manager**


**2.6.1** **Managing And Inspecting The Cluster Management Daemon**

**Using** systemctl **To Manage The Cluster Management Daemon**
It may be useful to shut down or restart the cluster management daemon. For instance, a restart may be
necessary to activate changes when the cluster management daemon configuration file is modified.
The cluster management daemon operation can be controlled through the systemctl unit command
options:


**Example**


[root@basecm11 etc]# systemctl stop cmd.service

[root@basecm11 etc]# systemctl is-enabled cmd.service

enabled

[root@basecm11 etc]# systemctl status cmd.service

- cmd.service - BCM daemon

Loaded: loaded (/usr/lib/systemd/system/cmd.service; enabled; preset: enabled)
Active: inactive (dead) since Tue 2025-04-08 15:44:00 CEST; 48s ago

...

[root@basecm11 etc]# systemctl start cmd.service

[root@basecm11 etc]# systemctl status cmd.service

- cmd.service - BCM daemon

Loaded: loaded (/usr/lib/systemd/system/cmd.service; enabled; preset: enabled)
Active: active (running) since Tue 2025-04-08 09:18:18 CEST; 6h ago

...


The cluster management daemon can be restarted on all regular nodes that are up:


**Example**


[root@mycluster ~]# pdsh -a "systemctl restart cmd; systemctl is-active cmd"

node001: active

node002: active

node003: active

[root@mycluster ~]#


This uses pdsh, the parallel shell command (section 14.1).


**Using** cmdaemonctl **To Inspect The Cluster Management Daemon**
The cmdaemonctl command is a way to run some CMDaemon-specific service-related commands:


**Example**


[root@basecm11 etc]# cmdaemonctl -h

cmdaemonctl [OPTIONS...] COMMAND ...


Query or send control commands to the cluster manager daemon.


-h --help Show this help


Commands:

debugon Turn on CMDaemon debug

debugoff Turn off CMDaemon debug

full-status Display CMDaemon status

upgrade Upgrade CMDaemon database

logconf Reload log configuration

[root@basecm11 etc]# cmdaemonctl full-status


**2.6 Cluster Management Daemon** **75**


CMDaemon version 3.0 is running (active)

Running locally

Debug logging is disabled


Current Time: Tue, 08 Apr 2025 16:15:41 CEST

Startup Time: Tue, 08 Apr 2025 15:55:39 CEST

Uptime: 20m 1s


CPU Usage: 5.55887u 1.93049s (0.6%)

Memory Usage: 176MB


Sessions Since Startup: 5

Active Sessions: 5


Number of occupied worker-threads: 1

Number of free worker-threads: 14


Connections handled: 323

Requests processed: 323

Total read: 93KB

Total written: 317KB


Average request rate: 16.1 requests/m
Average bandwidth usage: 264.35B/s


For performance reasons, CMDaemon should not normally be run in debug mode.


**2.6.2** **Configuring The Cluster Management Daemon**
Many cluster configuration changes can be done by modifying the cluster management daemon configuration file. For the head node, the file is located at:


/cm/local/apps/cmd/etc/cmd.conf


For regular nodes, it is located inside of the software image that the node uses.
Appendix C describes the supported configuration file directives and how they can be used. Normally there is no need to modify the default settings.
After modifying the configuration file, the cluster management daemon must be restarted to activate
the changes.


**2.6.3** **CMDaemon Versions**

**Updating CMDaemon**
CMDaemon can be updated on the head node with a package manager command such as:


yum update cmdaemon


and on a regular node image with a command such as:


yum update --installroot=/cm/images/< _software image_ - cmdaemon


Updating software on the cluster is covered in greater detail in Chapter9.


**CMDaemon Version Extraction**

For debugging an issue, knowing the version of CMDaemon that is in use on the cluster can be helpful.
The cmdaemonversions command runs within the device mode of cmsh . It lists the CMDaemon version

running on the nodes of the cluster


**76** **Cluster Management With NVIDIA Base Command Manager**


**Example**


[basecm11->device]% cmdaemonversions

Hostname Version index Version hash

---------------- ------------- -----------
basecm11 146,965 e6f593b676

node001 146,965 e6f593b676

node002 146,965 e6f593b676


A higher version index value indicates a more recent CMDaemon version.
The -join option is a formatting option which gathers together versions with the same option:


[basecm11->device]% cmdaemonversions --join

Version index Version hash Count Hostnames

------------- ------------ ------------ ------------------------
146,965 e6f593b676 3 basecm11,node001..node002


**2.6.4** **Configuring The Cluster Management Daemon Logging Facilities**
CMDaemon generates log messages in /var/log/cmdaemon from specific internal subsystems, such as
Workload Management, Service Management, Monitoring, Certs, and so on. By default, none of those
subsystems generate detailed (debug-level) messages, as that would make the log file grow rapidly.


**CMDaemon Logging Configuration Global Debug Mode**
A global debug mode can be enabled in CMDaemon using cmdaemonctl :


**Example**


[root@basecm11 ~]# cmdaemonctl -h

cmdaemonctl [OPTIONS...] COMMAND ...


Query or send control commands to the cluster manager daemon.


-h --help Show this help


Commands:

debugon Turn on CMDaemon debug

debugoff Turn off CMDaemon debug

...


[root@basecm11 ~]# cmdaemonctl debugon

CMDaemon debug level on


Stopping debug level logs from running for too long by executing cmdaemonctl debugoff is a good
idea, especially for production clusters. This is important in order to prevent swamping the cluster with
unfeasibly large logs.


**CMDaemon Subsystem Logging Configuration Debug Mode**
CMDaemon subsystems can generate debug logs separately per subsystem, including by severity level.
This can be done by modifying the logging configuration file at:


/cm/local/apps/cmd/etc/logging.cmd.conf


Within this file, a section with a title of #Available Subsystems lists the available subsystems that
can be monitored. These subsystems include MON (for monitoring), DB (for database), HA (for high availability), CERTS (for certificates), and so on.


**2.6 Cluster Management Daemon** **77**


**CMDaemon Subsystem Logging Configuration Severity Levels**
The debug setting is one of several severity levels. Other severity levels are info, warning, error, and

all .

Further details on setting subsystem options are given within the logging.cmd.conf file.
For example, to set CMDaemon log output for Monitoring, at a severity level of warning, the file
contents for the section severity might look like:


**Example**


Severity {

warning: MON

}


**CMDaemon Subsystem Logging Configuration Deployment**
The new logging configuration can be reloaded from the file by restarting CMDaemon:


**Example**


[root@basecm11 etc]# systemctl restart cmd


or by triggering it using the event bucket (page 627)


**Example**


[root@basecm11 etc]# echo LOGGING.RELOAD.CONFIG > /var/spool/cmd/eventbucket


**2.6.5** **Configuration File Modification, And The** FrozenFile **Directive**
As part of its tasks, the cluster management daemon modifies a number of system configuration files.
Some configuration files are completely replaced, while other configuration files only have some sections
modified. Appendix A lists all system configuration files that are modified.


  - A file that has been generated entirely by the cluster management daemon contains a header: