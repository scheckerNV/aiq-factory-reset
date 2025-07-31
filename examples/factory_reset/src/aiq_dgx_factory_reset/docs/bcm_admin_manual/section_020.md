# Only listen for connections from the local machine.

Listen localhost:631

...

# Show shared printers on the local network.

...

BrowseLocalProtocols


...

<Location />

# Restrict access to the server...

Order allow,deny


</Location>

...


Corresponding lines in a modified cupsd.conf file that accepts printing from hosts on the internal
network could be modified and end up looking like:


# Allow remote access

Port 631

...

# Enable printer sharing and shared printers.

...

BrowseAddress @LOCAL

BrowseLocalProtocols CUPS dnssd

...

<Location />


**15.5 HA For Regular Nodes And Edge Director Nodes** **771**


# Allow shared printing...

Order allow,deny

Allow from 10.141.0.0/16

</Location>

...


The operating system that ends up on the failover group nodes should have the relevant service
modifications running on those nodes after these nodes are up. In general, the required service modifications could be done:


  - with an initialize or finalize script, as suggested for minor modifications in section 3.19.4


  - by saving and using a new image with the modifications, as suggested for greater modifications
in section 3.19.2, page 202.


**Testing Regular Node HA**
To test that the regular node HA works, the active node can have a simulated crash carried out on it like
in section 15.2.4.


**Example**


ssh node001

echo c > /proc/sysrq-trigger

~.


A passive node then takes over.


**15.5.4** **The Sequence Of Events When Making Another HA Regular Node Active**
The active head node tries to initiate the actions in the following sequence, after the makeactive command is run (page 769):


**Sequence Of Events In Making Another HA Regular Node Active**


All Run pre-failover script


Active Stop service


Run umount script (stop and show exit>0 on error)


Stop active IP address


Start passive IP address


Start services on passive.


Active is now passive


Passive Stop service


Run mount script


Stop passive IP address.


Start active IP address.


Start service.


Passive is now active.


All Post-failover script


The actions are logged by CMDaemon.
The following conditions hold for the sequence of actions:


**772** **High Availability**


  - The remaining actions are skipped if the active umount script fails.


  - The sequence of events on the initial active node is aborted if a STONITH instruction powers it off.


  - The actions for All nodes is done for that particular failover group, for all nodes in that group.


**15.6** **HA And Workload Manager Jobs**


Workload manager jobs continue to run through a failover handover if conditions allow it.
The 3 conditions that must be satisfied are:


1. The workload manager setup must have been carried out


(a) during initial installation


or


(b) during a run of cm-wlm-setup


2. The HA storage setup must support the possibility of job continuity for that workload manager.
This support is possible for NAS for Slurm, PBS Professional, and LSF.


3. Jobs must also not fail due to the shared filesystem being inaccessible during the short period that
it is unavailable during failover. This usually depends on the code in the job itself, rather than
the workload manager, since workload manager clients by default have timeouts longer than the
dead time during failover.


Already-submitted jobs that are not yet running continue as they are, and run when the resources
become available after the failover handover is complete, unless they fail as part of the BCM prejob
health check configuration.


# **16**

### **The Jupyter Notebook** **Environment Integration**

**16.1** **Introduction**


This chapter covers the installation and usage of the Jupyter environment in BCM.
An updated list of the supported Linux distributions and Jupyter functionalities can be found in
the feature matrix at [https://support.brightcomputing.com/feature-matrix/](https://support.brightcomputing.com/feature-matrix/), under the Feature
column, in the section for Jupyter features.
An overview of the concepts and terminology follows.


**What Is Jupyter Notebook?**
_Jupyter Notebook_ ( [https://jupyter-notebook.readthedocs.io/](https://jupyter-notebook.readthedocs.io/) ), or Jupyter, is a client-server opensource application that provides a convenient way for a cluster user to write and execute _notebook docu-_
_ments_ in an interactive environment.

In Jupyter, a notebook document, or notebook, is content that can be managed by the application.
Notebooks are organized in units called _cells_ and can contain both executable code, as well as items that
are not meant for execution.

Items not meant for execution can be, for example: explanatory text, figures, formulas, or tables.
Notebooks can also store the inputs and outputs of an interactive session.
Notebooks can thus serve as a complete record of a user session, interleaving code with rich representations of resulting objects.
These documents are encoded as JSON files and saved with the .ipynb extension. Since JSON is a
plain text format, notebooks can be version-controlled, shared with other users and exported to other
formats, such as HTML, L [A] TEX, PDF, and slide shows.


**What Is A Notebook Kernel?**

A _notebook kernel_ (often shortened to _kernel_ ) is a computational engine that handles the various types of
requests in a notebook (e.g. code execution, code completions, inspection) and provides replies to the
user ( [https://jupyter.readthedocs.io/en/latest/projects/kernels.html](https://jupyter.readthedocs.io/en/latest/projects/kernels.html) ). Usually kernels only
allow execution of a single language. There are kernels available for many languages, of varying quality
and features.


**What Is JupyterHub?**
Jupyter on its own provides a single user service. _JupyterHub_ ( [https://jupyterhub.readthedocs.io/](https://jupyterhub.readthedocs.io/) )
allows Jupyter to provide a multi-user service, and is therefore commonly installed with it. JupyterHub
is an open-source project that supports a number of authentication protocols, and can be configured in
order to provide access to a subset of users.


**774** **The Jupyter Notebook Environment Integration**


**What Is JupyterLab?**
_JupyterLab_ ( [https://jupyterlab.readthedocs.io/](https://jupyterlab.readthedocs.io/) ) is a modern and powerful interface for Jupyter. It
enables users to work with notebooks and other applications, such as terminals or file browsers. It is
open-source, flexible, integrated, and extensible.
JupyterLab works out of the box with JupyterHub. It can be used to arrange the user interface to
support a wide range of workflows in data science, scientific computing, and machine learning.
JupyterLab is extensible with plugins that can customize or enhance any part of the interface. Plugins
exist for themes, file editors, keyboard shortcuts, as well as for other components.


**What Is A Jupyter Extension?**
Several components of the Jupyter environment can be customized in different ways with extensions.
Some types of extensions are:


  - IPython extensions ( [https://ipython.readthedocs.io/en/stable/config/extensions/](https://ipython.readthedocs.io/en/stable/config/extensions/#ipython-extensions)
[#ipython-extensions](https://ipython.readthedocs.io/en/stable/config/extensions/#ipython-extensions) )


  - Jupyter Notebook server extensions ( [https://jupyter-notebook.readthedocs.io/en/stable/](https://jupyter-notebook.readthedocs.io/en/stable/extending/index.html)
[extending/index.html](https://jupyter-notebook.readthedocs.io/en/stable/extending/index.html) )


  - JupyterLab extensions ( [https://jupyterlab.readthedocs.io/en/stable/user/extensions.](https://jupyterlab.readthedocs.io/en/stable/user/extensions.html)
[html](https://jupyterlab.readthedocs.io/en/stable/user/extensions.html) )


Extensions are usually developed, bundled, released, installed, and enabled in different ways.
Each extension provides a new functionality for a specific component. For example, JupyterLab
extensions can customize or enhance any part of the JupyterLab user interface. Extensions can provide
new themes, file viewers, editors and renderers for rich output in notebooks. They can also add settings,
add keyboard shortcuts, or add items to the menu or command palette.


**What Is Jupyter Kernel Provisionning?**
By default, Jupyter runs kernels locally, which can exhaust server resources. A resource manager, such
as a workload manager (Slurm, PBS, LSF) or Kubernetes, can be used to deal with this issue.
_Jupyter Kernel Provisioning_ ( [https://jupyter-client.readthedocs.io/en/latest/provisioning.](https://jupyter-client.readthedocs.io/en/latest/provisioning.html#kernel-provisioning)
[html#kernel-provisioning](https://jupyter-client.readthedocs.io/en/latest/provisioning.html#kernel-provisioning) ) provides a pluggable interface to distribute kernels across the compute
cluster, and uses local underlying resource managers.
The Jupyter Kernel Provisioning framework provides scalability, an improved multi-user support,
and a more granular security for Jupyter, in comparison with Jupyter Enterprise Gateway.


In BCM, all the technologies mentioned in these sections are combined to provide a powerful, customizable and user-friendly JupyterLab web interface running on a lightweight, multi-tenant, multilanguage, scalable and secure environment, ready for a wide range of enterprise scenarios.
For convenience, in the following sections, _Jupyter_ is generally used to collectively refer to Jupyter
Notebook, JupyterHub and JupyterLab


**16.2** **Jupyter Environment Installation**


BCM distributes Jupyter via two packages: cm-jupyter and cm-jupyter-local . They are typically installed via the cm-jupyter-setup script (section 16.2.1). Additional packages installed
by cm-jupyter-setup are cm-jupyter-eg-kernel-wlm-py312 (used with WLMs), and the optional
cm-jupyter-vnc-local metapackage (installs distribution-specific VNC packages).
cm-jupyter is installed in the /cm/shared directory, which is by default exported over NFS. As a
result, Jupyter kernels can run on all the compute nodes, without a separate installation to those nodes.
cm-jupyter provides JupyterHub, JupyterLab, and some extensions.
cm-jupyter-local provides the JupyterHub system service ( cm-jupyterhub.service ), and is therefore designed to be installed only on the node exposing users to the web login page for Jupyter. For


**16.2 Jupyter Environment Installation** **775**


convenience, this node is called the _login node_ . A login node is typically the head node, but any cluster
node can be used.

Since compute nodes are not reachable via a web interface by default, it is the responsibility of the
cluster administrator to configure access to these nodes if they are configured to be login nodes while
Jupyter runs. That is, login nodes that are compute nodes must have their access configured by assigning
IP addresses, configuring the firewall, opening Jupyter ports, and so on. However, if the Jupyter login
node is the head node, then BCM takes care of configuring the firewall to open the required ports and
of ensuring that the resulting environment is working out of the box.


**BCM Jupyter Extensions**
For a default deployment of Jupyter, BCM installs and enables the following extensions to the Jupyter
environment:


  - Jupyter Addons: A Jupyter Notebook server extension that performs API calls to CMDaemon and
manages other server extensions;


  - Jupyter Kernel Provisioning modules: A set of modules created to handle Jupyter kernels’ lifecycles in different possible BCM configurations. The modules available are: Slurm, PBS, LSF,
Kubernetes.


  - Jupyter Kernel Creator (section 16.5): A Jupyter Notebook server extension that provides a new
interactive and user-friendly way to create kernels;


  - Jupyter VNC (section 16.7): A Jupyter Notebook server extension that enables remote desktops
with VNC from notebooks;


  - JupyterLab Tools: A JupyterLab extension that exposes BCM server extensions functionalities to
the users and shows the Cluster View section;


  - Jupyter WLM Magic (section 16.8): An IPython extension that simplifies scheduling of workload
manager jobs from the notebook;


  - Jupyter Kubernetes Operators Manager (section 16.9): An extension that integrates with Kubernetes clusters, and for which it provides basic overview and management features.


**16.2.1** **Jupyter Setup**
The cm-jupyter-setup script can be run on the head node of the cluster to deploy a working Jupyter environment with minimal effort. The script comes with BCM’s cm-setup package. It has no prerequisites,
and can be run before or after configuring any resource manager, such as Kubernetes or Slurm.
By default, the Jupyter environment initially contains only Jupyter’s default Python 3 kernel, which
runs on the login node.
During setup, an administrator can deploy the Jupyter login interface on multiple nodes to evenly
distribute the load across them. In this case the administrator must configure a load balancer to route
users’ requests across those nodes.
These login nodes become members of the same configurationoverlay, and therefore share the
same Jupyter configuration, such as port numbers, authenticator, and so on.
By default, the Jupyter configuration file points to local SSL certificates. This means that if there are
multiple Jupyter login interfaces, then each node uses its own SSL certificate.


**16.2.2** **Jupyter Architecture**
The default Jupyter architecture deployed by cm-jupyter-setup is shown in figure 16.1.


**776** **The Jupyter Notebook Environment Integration**





Figure 16.1: Jupyter architecture


In this architecture, the cm-jupyterhub.service provided by cm-jupyter-local starts JupyterHub
on the port specified by c.JupyterHub.hub_port (default: 8901) on a login node (typically the head
node).
JupyterHub then automatically spawns a dynamic proxy to route HTTP requests via BCM’s
cm-npm-configurable-http-proxy package.
The proxy is the only process that listens for clients’ requests on Jupyter’s public interface, as specified by c.JupyterHub.port (default: 8000).
JupyterHub instructs the proxy on how requests should be dispatched by using its REST API. This
is exposed at the port specified by c.ConfigurableHTTPProxy.port (default: 8902), typically defined
within c.ConfigurableHTTPProxy.api_url .
At this stage, users accessing Jupyter with their browsers are either redirected to the shared Hub (e.g.
for authentication), or to their dedicated single-user servers to run notebooks.
By default, single-user servers are accessed at /user/< _username_  -, while JupyterHub is accessed at
/hub ( [https://jupyterhub.readthedocs.io/en/stable/reference/technical-overview.html](https://jupyterhub.readthedocs.io/en/stable/reference/technical-overview.html) ).
The cm-jupyter-setup script automatically installs JupyterLab and sets /lab as the default URL
( c.Spawner.default_url ) to redirect users to the new interface.
Finally, JupyterHub is integrated to spawn the JupyterLab interface on a login node
by configuring jupyterhub.spawner.LocalProcessSpawner as the default spawning mechanism
( c.JupyterHub.spawner_class ), and jupyterhub-singleuser-gw as the default spawning command
( c.Spawner.cmd ).
When a new notebook is started, a Jupyter kernel provisioner scans for an available port, and spawns
a kernel chosen by the user on an appropriate cluster node. This process is then connected to JupyterLab.
JupyterHub and its HTTP proxy are run as two root processes, while JupyterLab and the in-built
kernel provisioning run as user processes.


**16.2 Jupyter Environment Installation** **777**


The privileges of the kernels spawned by Jupyter Kernel Provisioning can be configured by cluster
administrators, and depend on the underlying computational engine (for example, Kubernetes). By
default, all the kernels configurable by BCM are run as user processes, and no privilege escalation is
possible.
Communication between users’ browsers, JupyterHub, its HTTP proxy, and JupyterLab, is secured
by default by JupyterHub. On the other hand, communication between JupyterLab and the kernels on
the nodes, is secured by BCM.
Administrators can customize their Jupyter integration by setting some of the aforementioned options when the cm-jupyter-setup script runs. New values are automatically handled by BCM and
written to Jupyter configuration files.
Other configuration options can be found in /cm/local/apps/jupyter/current/conf/jupyterhub_
config.py .


**16.2.3** **Verifying Jupyter Installation**
The cm-jupyter-setup script automatically starts the cm-jupyterhub service.
Any user (not necessarily root) can then verify the installation is working as expected. Here an
ordinary user, jupyterhubuser runs the checks.
It can take some time until the service is fully up and running, even if a status check with systemctl
shows that the service is active:


**Example**


[jupyterhubuser@basecm11 ~]$ systemctl status cm-jupyterhub -l

cm-jupyterhub.service - JupyterHub
Loaded: loaded (/lib/systemd/system/cm-jupyterhub.service; static)
Active: active (running) since Mon 2025-01-06 14:47:28 CET; 4h 25min ago

Main PID: 4367 (run.sh)

Tasks: 11 (limit: 19051)

Memory: 190.2M

CPU: 1min 46.193s

CGroup: /system.slice/cm-jupyterhub.service
|-4367 /bin/bash /cm/shared/apps/jupyter/16.0.0/bin/run.sh
|-4428 /cm/local/apps/python312/bin/python3 /cm/shared/apps/jupyter/16.0.0/bin/jupyterhub ...
|-4429 tee -a /var/log/jupyterhub.log
'-5431 node /cm/shared/apps/jupyter/16.0.0/bin/configurable-http-proxy --ip "" --port 8000 ...


A check can then be done to see that the Jupyter extensions provided by BCM are installed and
enabled:


**Example**


[jupyterhubuser@basecm11 ~]$ module load jupyter
Loading jupyter/16.0.0

Loading requirement: python312

[jupyterhubuser@basecm11 ~]$ jupyter labextension list

JupyterLab v4.3.3
/cm/shared/apps/jupyter/current/share/jupyter/labextensions
jupyterlab_pygments v0.3.0 enabled OK (python, jupyterlab_pygments)
@brightcomputing/jupyterlab-tools v0.2.7 enabled OK (python, brightcomputing_jupyterlab_tools)
@jupyter-widgets/jupyterlab-manager v5.0.13 enabled OK (python, jupyterlab_widgets)
@jupyterhub/jupyter-server-proxy v4.4.0 enabled OK


**16.2.4** **Login Configuration**

**User Access To JupyterHub With The Default Configuration**
Once JupyterHub is functioning, its web login interface is accessible with a browser using the HTTPS
protocol on the specified port (figure 16.2):


**778** **The Jupyter Notebook Environment Integration**


Figure 16.2: JupyterHub login screen


Running as root under JupyterHub is not recommended, so logging in to JupyterHub as root is not
allowed by default.
Any other PAM user can log in to JupyterHub.
If needed, a test user jupyterhubuser with password jupyterhubuser can be created with, for example:


**Example**


[root@basecm11 ~]# cmsh -c "user; add jupyterhubuser; set password jupyterhubuser; commit"


**Restricting User Access To JupyterHub**
JupyterHub logins can be limited to members of particular groups.
For example, alice could be made a member of the group jupyterusers :


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% group

[basecm11->group]% add jupyterusers

[basecm11->group]*[jupyterusers*]% append members alice

[basecm11->group]*[jupyterusers*]% commit


The group jupyterusers could then be set to be allowed to authenticate to JupyterHub with an
authentication policy:


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% configurationoverlay

[basecm11->configurationoverlay]% use jupyterhub

[basecm11->configurationoverlay[jupyterhub]]% roles

[basecm11->configurationoverlay[jupyterhub]->roles]% use jupyterhub

[basecm11->configurationoverlay[jupyterhub]->roles[jupyterhub]]% configs

[basecm11->...roles[jupyterhub]->configs]% add c.BrightAuthenticator.groups_allow

[basecm11->...roles*[jupyterhub*]->configs*[c.BrightAuthenticator.groups_allow*]]% set value [\"jupyterusers\"]

[basecm11->...roles*[jupyterhub*]->configs*[c.BrightAuthenticator.groups_allow*]]% commit


**16.2 Jupyter Environment Installation** **779**


Similarly, restricting authentication to JupyterHub to a specific group of users can be done by configuring c.BrightAuthenticator.groups_deny .
Another way to restrict user access is based on the CMDaemon profile set for the user. In that
case the JupyterHub configuration settings are c.BrightAuthenticator.cmd_profiles_allow and
c.BrightAuthenticator.cmd_profiles_deny .
In the following example, users with a readonly profile are not allowed to authenticate for JupyterHub.


**Example**


[basecm11->...roles[jupyterhub]->configs[c.BrightAuthenticator.groups_allow]]% ..

[basecm11->...roles[jupyterhub]->configs]% add c.BrightAuthenticator.cmd_profiles_deny]]%

[basecm11->...roles*[jupyterhub*]->configs*[c.BrightAuthenticator.cmd_profiles_deny*]]% set value [\"readonly\"]

[basecm11->...roles*[jupyterhub*]->configs*[c.BrightAuthenticator.cmd_profiles_deny*]]% commit


A table summarizing the authentication policies is:


**Key** **Value**


c.BrightAuthenticator.groups_allow users in the specified groups can authenticate


c.BrightAuthenticator.groups_deny users in the specified groups cannot authenticate


c.BrightAuthenticator.cmd_profiles_allow users with the specified profiles can authenticate


c.BrightAuthenticator.cmd_profiles_deny users with the specified profiles cannot authenticate


**16.2.5** **JupyterHub Screen After Login**
After the first login, a new single-user server is spawned (figure 16.3):


Figure 16.3: JupyterHub starting single-user server


Users are redirected to the JupyterLab interface and have access to Jupyter’s default Python 3 kernel
(figure 16.4):


**780** **The Jupyter Notebook Environment Integration**


Figure 16.4: JupyterLab Launcher


If using Kubernetes under Jupyter, then a user registered under the Linux-PAM system must be
added separately via Kubernetes with cm-kubernetes-setup . (section 4.11 of the _Containerization Man-_
_ual_ ).


**16.3** **Jupyter Notebook Examples**


The cm-jupyter package (section 16.2.1) provides a number of machine learning notebook examples
that can be executed with Jupyter.
The notebooks include some applications developed with TensorFlow, PyTorch, MXNet, and other
frameworks. The applications can be found in the /cm/shared/examples/jupyter/notebooks/ directory:


[jupyterhubuser@basecm11 ~]$ ls /cm/shared/examples/jupyter/notebooks/

Keras+TensorFlow2-addition.ipynb psql-example.ipynb Spark+XGBoost-mortgage.ipynb

llm-bcm-manuals-rag Pytorch-cartpole.ipynb TensorFlow-minigo.ipynb

llm-codellama-local R-iris.ipynb

MXNet-superresolution.ipynb Spark-pipeline.ipynb


The datasets needed to execute these notebooks can be found in the /cm/shared/examples/jupyter/
datasets/ directory:


[jupyterhubuser@basecm11 ~]$ ls /cm/shared/examples/jupyter/datasets/

880f8b8a6fd-mortgage-small.tar.gz kaggle-iris.csv


Users can copy these examples to their home directories, create or choose appropriate kernels to
execute them, and interactively run them from Jupyter. In order to edit notebooks, the write permissions
must be kept during the copy.


**16.4 Jupyter Kernels** **781**


The distributed examples typically only require the packages provided by BCM with the Data Science Add-on, such as TensorFlow, PyTorch, and MXNet.
It is the responsibility of users to make sure that the required modules are loaded by their Jupyter
kernels. The list of frameworks and libraries required to run an example is usually available at the
beginning of each notebook.


**16.4** **Jupyter Kernels**


In Jupyter, kernels are defined as JSON files.
Any user that the cluster administrator has registered in the Linux-PAM system can list the available
Jupyter kernels via the command line. The following example is run in the initial Jupyter environment:


**Example**


[jupyterhubuser@basecm11 ~]$ module load jupyter

[jupyterhubuser@basecm11 ~]$ jupyter kernelspec list

Available kernels:

python3 /cm/shared/apps/jupyter/current/share/jupyter/kernels/python3


Each kernel directory contains a kernel.json file describing how Jupyter spawns that kernel:


**Example**


[jupyterhubuser@basecm11 ~]$ ls /cm/shared/apps/jupyter/current/share/jupyter/kernels/*/kernel.json
/cm/shared/apps/jupyter/current/share/jupyter/kernels/python3/kernel.json


In addition to specifications for shared kernels, each user can define new personal ones in the home
directory. By default, the Jupyter data directory for a user is located at $HOME/.local/share/jupyter .
This path can be verified with Jupyter by using the --paths option:


**Example**


[jupyterhubuser@basecm11 ~]$ jupyter --paths

config:
/home/jupyterhubuser/.jupyter
/home/jupyterhubuser/.local/etc/jupyter
/cm/local/apps/jupyter/conf
/cm/shared/apps/jupyter/current/etc/jupyter

data:

/home/jupyterhubuser/.local/share/jupyter
/cm/shared/apps/jupyter/current/share/jupyter

runtime:

/home/jupyterhubuser/.local/share/jupyter/runtime


The simplest definition for a Python3 kernel designed to run on the login node is:


{

"argv": ["python",

"-m",

"ipykernel_launcher",

"-f",

"{connection_file}"

],

"display_name": "Python 3",

"language": "python"

}


**782** **The Jupyter Notebook Environment Integration**


In the preceding kernel definition:


 - argv : is the command to be executed to locally spawn the kernel


 - "display_name ": is the name to be displayed in the JupyterLab interface


 - "language" : is the supported programming language ( "language" )


 - "{connection_file}" ( [https://jupyter-client.readthedocs.io/en/stable/kernels.html#](https://jupyter-client.readthedocs.io/en/stable/kernels.html#connection-files)
[connection-files](https://jupyter-client.readthedocs.io/en/stable/kernels.html#connection-files) ) is a placeholder, and is replaced by Jupyter with the actual path to the connection file before starting the kernel.


The following kernel is Jupyter’s default Python 3 kernel distributed by BCM in the initial environ
ment:


**Example**


[jupyterhubuser@basecm11 ~]$ cat /cm/shared/apps/jupyter/current/share/jupyter/kernels/python3/kernel.json


{

"argv": [
"/cm/local/apps/python312/bin/python3.12",

"-m",

"ipykernel_launcher",

"--InteractiveShellApp.extra_extensions=cm_jupyter_wlm_magic",

"--TerminalIPythonApp.extra_extensions=cm_jupyter_wlm_magic",

"-f",

"{connection_file}"

],

"display_name": "Python 3",

"language": "python",

"env": {

"PYTHONPATH": "/cm/shared/apps/jupyter/current/lib64/python3.12/site-packages:/cm/shared/apps/jupyter/
current/lib/python3.12/site-packages"

}

}


The two kernels are not very different. They differ from each other in the Python 3 binary path, the
IPython extension (Jupyter WLM Magic), and the exported PYTHONPATH environment variable ( "env" ).


**16.4.1** **Jupyter Kernel Provisioning Kernels**
Jupyter is designed to run both the kernel processes, as well as the user interface (JupyterLab or
Jupyter Notebook) on the same host. The kernel {connection_file} is therefore stored in the
~/.local/share/jupyter/runtime directory, or in the /run directory.
JupyterLab can delegate the task of spawning kernels to another component, Jupyter Kernel Provisioning, as defined in the kernel’s JSON file for kernel_provisioner . Jupyter Kernel Provisioning allows
the complete life-cycle of several Jupyter kernels to be managed at the same time—their start, status
monitoring, and termination, but the particular Jupyter kernels that run are otherwise independent of
Jupyter Kernel Provisioning, and can be managed by third parties.
Jupyter Kernel Provisioning requires an extended kernel.json definition to describe a particular
process-proxy module to handle the kernel.
A simple definition for a Python3 kernel designed to be scheduled via JEG is:


**16.4 Jupyter Kernels** **783**


{

"display_name": "Python 3.12 via SLURM 250102185019",

"language": "python",

"metadata": {

"kernel_provisioner": {

"provisioner_name": "slurm-provisioner",
"config": {

"timeout": 60,

"response_manager": {

"version": 2

},

"submit_cmd": {

"path": "templates/submit_cmd.sh.j2",

"vars": {

"modules": "shared slurm jupyter-eg-kernel-wlm-py312"

}

},

"query_cmd": {
"path": "templates/query_cmd.sh.j2",

"vars": {

"modules": "shared slurm jupyter-eg-kernel-wlm-py312"

}

},

"info_cmd": {

"path": "templates/info_cmd.sh.j2",

"vars": {

"modules": "shared slurm jupyter-eg-kernel-wlm-py312"

}

},

"cancel_cmd": {

"path": "templates/cancel_cmd.sh.j2",

"vars": {

"modules": "shared slurm jupyter-eg-kernel-wlm-py312"

}

},

"submit_script": {
"path": "templates/submit_script.sh.j2",

"vars": {

"job_prefix": "jupyter-kernel-slurm-py312",

"partition": "",

"ntasks": "1",

"gres": "",
"work_dir": "/home/alice",

"modules": "shared slurm jupyter-eg-kernel-wlm-py312",

"oversubscribe": false,

"pythonuserbase_loc": "temp"

}

}

}

}

},

"argv": []

}


In this example, the "metadata" entry has been added. It includes "kernel_provisioner" and
"provisioner_name", which define the exact provisioner being used to manage the life-cycle of the


**784** **The Jupyter Notebook Environment Integration**


kernel. The provisioner is defined via Python’s entry points specification.
It also contains paths to several script templates used to spawn the job within the context
that the kernel process runs, and sets the corresponding environment variables and other variables for the templates. The "argv": [] is empty because it is replaced by a script defined in
templates/submit_script.sh.j2
BCM is equipped with several types of provisioners to interact with a wide range of resource managers, such as Kubernetes or Slurm. This allows kernels to be scheduled across compute nodes.
BCM recommends that kernels using the Jupyter Kernel Provisioning mechanism are created and
used with the Jupyter Kernel Creator (section 16.5) extension.


**16.4.2** **Tunables For Kernel Provisioners**

BCM provides defaults for all the templates. The aim is to have the kernels that are created just work
on a typical cluster. However a better fit to the running environment may be possible with some further
fine-tuning.
Configuration parameters for modifying the kernel templates can be added with cmsh . These parameters are put into the Jupyter configuration file at /cm/local/apps/jupyter/conf/jupyterhub_
config.py, and become accessible when JupyterLab starts. Templates or already-created kernels can
be edited—which might be a preferred approach to test a parameter before simply adding it via cmsh .
Parameters that are set in the kernel specification (the kernel.json file) have precedence over the ones
set in jupyterhub_config.py
The following example shows a session that adds the c.KernelResponseManager.public_ip configuration parameters within cmsh :


**Example**


[root@basecm11 ~]# cmsh

[basecm11]% configurationoverlay

[basecm11->configurationoverlay]% use jupyterhub

[basecm11->configurationoverlay[jupyterhub]]% roles

[basecm11->configurationoverlay[jupyterhub]->roles]% use jupyterhub

[basecm11->configurationoverlay[jupyterhub]->roles[jupyterhub]]% configs

[basecm11->...]->roles[jupyterhub]->configs]% add c.KernelResponseManager.public_ip

[basecm11->...]->roles*[jupyterhub*]->configs*[c.KernelResponseManager.public_ip*]]% set value "'10.10.1.1'"

[basecm11->...]->roles*[jupyterhub*]->configs*[c.KernelResponseManager.public_ip*]]% commit


On commit, the cm-jupyter service is restarted, which means that all user sessions are dropped. To
avoid this, editing the templates directly in the /cm/shared/apps/jupyter/current/share/jupyter/
kerneltemplates directory can be considered.


_Table 16.4.2: Jupyter Kernel Tunables_


**Path in kernel.json**



**Configuration parameter**



(metadata.kernel_ **Default** **Description**


provisioner.config)



c.CMKernelProvisionerBase. .timeout 5 Timeout starting kernel

timeout


_...continues_


**16.4 Jupyter Kernels** **785**


_...continued_


**Path in kernel.json**



**Configuration parameter**



(metadata.kernel_ **Default** **Description**


provisioner.config)



c.CMKernelProvisionerBase. .include_regex_env ^(.+_API_(KEY|TOKEN| Regex for environment
include_regex_env HOST|TYPE|ORG_ID| variable names to be
ENDPOINT)|HF_.+)$ inherited from JupyterLab
process running on login
node


c.CMKernelProvisionerBase. .exclude_regex_env ^(JPY_API_TOKEN| Regex for environment
exclude_regex_env JUPYTERHUB_.+|PYTHON.+| variable names not to be
JUPYTERLAB_.+|PATH| passed to running
LD_LIBRARY_PATH.*)$ kernels


c.CMJKProvisioner. .poll_interval 5 Polling interval and
poll_interval interval between retries for
k8s operations


c.CMJKProvisioner. .operation_timeout 5 Timeout for running
operation_timeout commands interacting with
k8s


c.KernelResponseManager. .response_manager. Detected The IP address on the login
public_ip public_ip automatically node that jupyter-kernelstarter will use for call
backs when the kernel is

started on the compute node


c.KernelResponseManager. .response_manager. Detected The network on the login
public_network public_network automatically node that jupyter-kernelstarter will use for call
backs when the kernel is

started on the compute node


c.KernelResponseManager. .response_manager. Detected External hostname of the
public_hostname public_hostname automatically login node can be specified,
and the public IP address
will be detected by resolving


c.KernelResponseManager .response_manager. Detected The IP address used by the
bind_ip bind_ip automatically the response manager to
bind the socket that lis
tens for callbacks from

jupyter-kernel-starter


c.KernelResponseManager. .response_manager. Detected The IP address used by
bind_network bind_network automatically the response manager to
bind the socket that lis
tens for callbacks from

jupyter-kernel-starter


_...continues_


**786** **The Jupyter Notebook Environment Integration**


_...continued_


**Path in kernel.json**



**Configuration parameter**



(metadata.kernel_ **Default** **Description**


provisioner.config)



c.KernelResponseManager. .response_manager. 1025 The start of the port range
bind_port_range_start bind_port_range_start within which the response
manager tries to obtain a
port, for listening to callbacks from the kernel


c.KernelResponseManager. .response_manager. 65535 The end of the port range
bind_port_range_end bind_port_range_end within which the response
manager tries to obtain a
port, for listening to callbacks from the kernel


c.KernelResponseManager. .response_manager. 16 How many times the
bind_port_retries bind_port_retries response manager tries to
find a free port


c.KernelResponseManager. .response_manager. 5 How many incoming
max_in_requests max_in_requests messages to the kernel
starter can be buffered


c.KernelResponseManager. .response_manager. 5 How many outgoing
max_out_requests max_out_requests 5 messages to the kernel
starter can be buffered


The _response manager_ in the preceding table is a part of WLM kernel provisioners. It is dedicated to
getting callbacks and managing signal communications with the running kernel. It acts as a proxy for
system signals and informs the kernel provisioner about the kernel being started and which ports it is
listening to. The response manager works in tandem with jupyter-kernel-starter .


**16.5** **Jupyter Kernel Creator Extension**


Creating or editing kernels can be cumbersome and error-prone for users, depending on the features of
the execution context desired for their notebooks.

To provide a more user-friendly experience, BCM includes the _Jupyter Kernel Creator_ extension in
JupyterLab. This extension is accessed from the navigation pane in the JupyterLab interface, by clicking
on the BCM icon.

Jupyter Kernel Creator allows users to create kernels using the JupyterLab interface, without the
need to directly edit JSON files. With this interface users can create kernels by customizing an available
_template_ according to their needs.
A template can be considered to be the skeleton of a kernel, with several preconfigured options, and
others options that are yet to be specified. Common customizations for templates include environment
modules to be loaded, workload manager queues to be used, number and type of GPUs to acquire, and

so on.

Templates are usually defined by administrators according to cluster capabilities, programming lan

**16.5 Jupyter Kernel Creator Extension** **787**


guages and user requirements. Each template can provide different options for customizations.
Administrators often create different templates to take advantage of different workload managers,
programming languages and hardware resources. For example, an administrator may define a template
for scheduling Python kernels via Kubernetes, another one for R kernels via Slurm, and yet another one
for Bash kernels via Platform LSF.


**16.5.1** **BCM Predefined Kernel Templates**
To simplify Jupyter configuration for administrators, BCM distributes a number of pre-defined templates with Jupyter Kernel Creator. These templates can be used for default configurations of BCM
workload managers, and can be customized and extended for more advanced use. Kernel templates defined by BCM can be found in the Jupyter installation directory, under the kerneltemplates directory:


[jupyterhubuser@basecm11 ~]$ ls /cm/shared/apps/jupyter/current/share/jupyter/kerneltemplates/

filter.yaml k8s-cmjkop-py lsf-py312 pbspro-bash slurm-py312 slurm-pyxis-r

k8s-cmjkop-julia k8s-cmjkop-py-spark openpbs-bash pbspro-py312 slurm-py-conda

k8s-cmjkop-ngc-py lsf-bash openpbs-py312 slurm-bash slurm-pyxis-py


**BCM Predefined Kernel Templates Seen By Users**
Users can view the available predefined kernel templates in the Jupyter web browser interface, within
the KERNEL TEMPLATES section of the dedicated BCM extensions panel (figure 16.5):


Figure 16.5: JupyterLab BCM extensions section with kernel templates


However, the templates provided by BCM are listed in the panel only if they can be used on the
cluster. This means that the templates are listed only after the associated workload manager instance,
or associated Kubernetes configuration (such as a Kubernetes operator), have been deployed by cluster
manager utilities. For example:


**788** **The Jupyter Notebook Environment Integration**


  - After running the cm-wlm-setup cluster manager utility to deploy an OpenPBS workload manager,
the openpbs-bash and openpbs-py312 templates become available. The templates are listed as:


**–**
Bash via OpenPBS


**–**
Python 3.12 via OpenPBS


and accessed via the navigation path: _menu_    - _dedicated BCM extension panel_    - _kernel templates section_ .


  - After running the cm-kubernetes-setup cluster manager utility to deploy a Kubernetes cluster,
the Kubernetes cluster instance is displayed (navigation path: _menu_    - _dedicated BCM extension_
_panel_    - _Kubernetes clusters section_ )


Then, after running the cm-jupyter-kernel-operator cluster manager utility to deploy a Jupyter
kernel operator package, and configuring a user (section 6.3 of the _Containerization Manual_ ), the
templates k8s-cmjkop-julia, k8s-cmjkop-py, and k8s-cmjkop-py-spark become available.


The templates are listed as:


**–**
Julia on Kubernetes Operator


**–**
Python on Kubernete Operator


**–**
Python+Spark on Kubernetes Operator


and accessed via the navigation path: _menu_    - _dedicated BCM extension panel_    - _kernel templates section_ .


Users can instantiate a kernel template to create an actual kernel from the dedicated BCM extensions
section using the + button of the template. A dialog is dynamically generated for the template being
instantiated, and users are asked to fill a number of customization options defined by administrators
(figure 16.6):


**16.5 Jupyter Kernel Creator Extension** **789**


Figure 16.6: Jupyter kernel template customization screen


Once the template is completely customized, the kernel can be created. It automatically appears
in the JupyterLab Launcher screen (figure 16.7) and can be used to run notebooks or a console session
(figure 16.7):


**790** **The Jupyter Notebook Environment Integration**


Figure 16.7: JupyterLab Launcher screen with new custom kernel


A user who lists available Jupyter kernels via the command line now sees the newly-created kernel:


[jupyterhubuser@basecm11 ~]$ module load jupyter

[jupyterhubuser@basecm11 ~]$ jupyter kernelspec list

Available kernels:

k8s-cmjkop-py-1gii7nm01 /home/alice/.local/share/jupyter/kernels/k8s-cmjkop-py-1gii7nm01
python3 /cm/shared/apps/jupyter/current/share/jupyter/kernels/python3


The new kernel directory will contain the JSON definition generated by the Jupyter Kernel Creator:


[jupyterhubuser@basecm11 ~]$ cat .local/share/jupyter/kernels/k8s-cmjkop-py-1gii7nm01/kernel.json


{

"language": "python",

"display_name": "Datascience Notebook Kernel",

"metadata": {

"kernel_provisioner": {

"provisioner_name": "cmjk-provisioner",
"config": {

"timeout": 280,

"template": {
"path": "templates/cmjk.yaml.j2",

"env_module": "kubernetes",

"vars": {

"image": "quay.io/jupyter/datascience-notebook",

"namespace": "alice-restricted",

"image_pull_policy": "IfNotPresent",

"gpu_limit": 0,


**16.5 Jupyter Kernel Creator Extension** **791**


"pythonuserbase_loc": "temp"

}

}

}

}

},

"argv": []

}


Jupyter kernel names need not be unique. Users should therefore choose meaningful and distinguishable display names for their kernels. Doing so makes the JupyterLab Launcher screen easier to

use.

For convenience, a summary of the available kernel templates and their requirements is shown in
table 16.1:


_**Table 16.1:**_ _Available Jupyter kernel templates for BCM and their requirements_


**Template name** **Requirement** **Description**


k8s-cmjkop-julia Kubernetes Jupyter official image via Jupyter Kernel Operator (using Julia)


k8s-cmjkop-ngc-py Kubernetes NGC images via Jupyter Kernel Oper
ator


k8s-cmjkop-py Kubernetes Jupyter official image via Jupyter Kernel Operator (Python)

k8s-cmjkop-py-spark Kubernetes [1] Python + Spark via Jupyter Kernel Operator (using Python and Spark


lsf-bash Platform LSF Bash via Platform LSF


lsf-py312 Platform LSF Python 3.12 via Platform LSF


openpbs-bash Open PBS Bash via Open PBS


openpbs-py312 Open PBS Python 3.12 via Open PBS


pbspro-bash PBS Professional Bash via PBS Professional


pbspro-py312 PBS Professional Python 3.12 via PBS Professional


slurm-bash Slurm Bash via Slurm


slurm-py312 Slurm Python 3.12 via Slurm

slurm-py-conda Slurm + Conda [2] Python 3.12 and Conda via Slurm


slurm-pyxis-py Slurm + Enroot Python running inside imported
Pyxis+Enroot image in Slurm


_...continues_


**792** **The Jupyter Notebook Environment Integration**


_Table 16.1: Available Jupyter kernel templates...continued_


**Template name** **Requirement** **Description**


slurm-pyxis-r Slurm + Enroot R running inside imported
Pyxis+Enroot image in Slurm

1 Docker image: _docker.io/brightcomputing/jupyter-kernel-sample:k8s-spark-3.5.3-py38-cuda12.6-rapids24.08-2_
2 Conda needs to be installed for the user, and the Conda environment needs to be configured in the user’s Bash
shell as described in section 11.4.2 of the _User Manual_ .

DockerHub kernels page: [https://hub.docker.com/r/brightcomputing/jupyter-kernel-sample/tags](https://hub.docker.com/r/brightcomputing/jupyter-kernel-sample/tags)


**16.5.2** **Jupyter Kernel Starter**
Jupyter Kernel Starter, implemented as the software jupyter-kernel-starter, runs alongside the
Jupyter kernel. It acts as a starter and sidecar to manage the life-cycle of the kernel on the node within
the WLM job context. It informs the kernel provisioner, via the response manager, about the kernel status, and which ports are being used by Jupyter Kernel Manager (the kernel provisioner layer manager).
It also performs basic heartbeat and watchdog operations to make sure that the running kernel does not
drain cluster resources if the connection to the kernel provisioner is lost.


[jupyterhubuser@basecm11 ~]$ module load jupyter-eg-kernel-wlm-py312

[jupyterhubuser@basecm11 ~]$ jupyter-kernel-starter --help
usage: jupyter-kernel-starter [-h] [--log-level <log_level>] [--kernel-id <kernel_id>]

[--response-address <ip>:<port>] [--bind-ip <x.x.x.x>]

[--bind-network <x.x.x.x/y>] [--port-range <begin>..<end>]

[--port-bind-attempts <n>] [--wait-ports-timeout <sec>]

[--shutdown-timeout <sec>] [--response-server-socket-timeout <sec>]

[--watchdog-interval <sec>] [--kernel-script <cmd>]

[--kernel-script-base64 <cmd_base64>] [--connection-file-dir <path>]

[--encryption-key <pem_key>]


options:

-h, --help show this help message and exit

--log-level <log_level>
Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Can be specified as the

JKS_LOG_LEVEL environment variable.

--kernel-id <kernel_id>

ID of the Jupyter kernel

--response-address <ip>:<port>

Address of the server to return kernel connection info. Can be specified as the

JKS_RESPONSE_ADDRESS environment variable.

--bind-ip <x.x.x.x> IP address to bind. Can be specified as the JKS_BIND_IP environment variable.
--bind-network <x.x.x.x/y>

Alternatively IP network to bind. Can be specified as the JKS_BIND_NETWORK environment

variable.

--port-range <begin>..<end>

Range of the ports to use for kernel. Can be specified as the JKS_PORT_RANGE environment

variable.

--port-bind-attempts <n>

How many times to try to find unoccupied ports to use. Can be specified as the

JKS_PORT_BIND_ATTEMPTS environment variable.

--wait-ports-timeout <sec>

How many seconds the kernel waits for ports to open before sending connection information

to the server. Can be specified as the JKS_WAIT_PORTS_TIMEOUT environment variable.

--shutdown-timeout <sec>

Timeout to shutdown kernel if connection to server is lost. Can be specified as the


**16.5 Jupyter Kernel Creator Extension** **793**


JKS_SHUTDOWN_TIMEOUT environment variable.

--response-server-socket-timeout <sec>

Socket timeout value for connecting to response server. Can be specified as the

JKS_RESPONSE_SERVER_SOCKET_TIMEOUT environment variable.

--watchdog-interval <sec>

How often watchdog with check liveness of kernel and connection to server. Can be

specified as the JKS_WATCHDOG_INTERVAL environment variable.

--kernel-script <cmd>

Script to run; '__connection_file__' placeholder will be substituted. Can be

specified as the JKS_KERNEL_SCRIPT environment variable.

--kernel-script-base64 <cmd_base64>

Alternatively cmd can be in base64 format to avoid issues with templating. Can be

specified as the JKS_KERNEL_SCRIPT_BASE64 environment variable.

--connection-file-dir <path>

Directory to store connection file json

--encryption-key <pem_key>

Public key to encrypt data; must be in string in PEM format or path to .pem file.

Can be specified as the JKS_ENCRYPTION_KEY environment variable


To establish communication with the response manager, the cryptographic key stored in
JKS_ENCRYPTION_KEY is required. This is a public key generated by response manager, used to secure
communication between the response manager and jupyter-kernel-starter .
A typical starting command is:


jupyter-kernel-starter _\_
--kernel-id 2a8bf66d-1577-4876-b908-a219fd4f8944 _\_
--response-address 10.141.255.254:23949 _\_
--shutdown-timeout 15 _\_

--kernel-script 'python -m ipykernel_launcher -f __connection_file__'


In the preceding command __connection_file__ is a placeholder for jupyter-kernel-starter .
It becomes a real path to the file for ipykernel_launcher to start. Data from the connection file is
created by jupyter-kernel-starter, and is then transferred to the response manager, so that Jupyter Kernel
Manager knows how to connect to the running kernel. This way --kernel-script can start the kernel
for any language supported by Jupyter.
Useful arguments that are often needed for more sophisticated cluster configuration are:


 - --bind-network : used to make sure that jupyter-kernel-starter selects the right interface on
the compute node that is connected to the login node


 - --port-range : limits the ports that are probed to establish a connection to the response manager—
this can be useful for strict network and firewall rules.


Various timeouts ( jupyter-kernel-starter help | grep timeout ) can also be tuned.
The command options can be set in kernel templates ( templates/submit_script.sh.j2 ) or directly
in the created kernel.


**16.5.3** **Running Jupyter Kernels With Two Factor Authentication**
If PAM and CMDaemon are configured with two-factor authentication (2FA), then JupyterHub needs to
be instructed to support it. This can be done using cmsh as follows:


[root@basecm11 ~]# cmsh

[basecm11]% configurationoverlay

[basecm11->configurationoverlay]% use jupyterhub


**794** **The Jupyter Notebook Environment Integration**


[basecm11->configurationoverlay[jupyterhub]]% roles

[basecm11->configurationoverlay[jupyterhub]->roles]% use jupyterhub

[basecm11->configurationoverlay[jupyterhub]->roles[jupyterhub]]% configs

[basecm11->...]->roles[jupyterhub]->configs]% add c.BrightAuthenticator.twofa

[basecm11->...]->roles*[jupyterhub*]->configs*[c.BrightAuthenticator.twofa*]]% set value True

[basecm11->...]->roles*[jupyterhub*]->configs*[c.BrightAuthenticator.twofa*]]% commit


**16.5.4** **Running Jupyter Kernels With Kubernetes**
The Jupyter Kernel Operator (section 6.3 of the _Containerization Manual_ ) is the recommended way to run
kernels in Kubernetes in BCM. It allows users to run unmodified images; it takes care of communication
with Jupyter Kernel Provisioning as it manages the Jupyter kernel life-cycle, including cleaning up dead
or orphaned kernels.
After installation and configuration by cm-kubernetes-setup, Jupyter Kernel Operator kernels
( k8s-cmjkop-* ) appear in the JuputerLab interface in the template section.
The following BCM templates allow users to create and run Jupyter kernels on compute nodes via
Kubernetes:


_**Table 16.2:**_ _BCM templates for creating and running Jupyter kernel provisioner kernels on cluster nodes via Kubernetes_


**Template** **Description**


k8s-cmjkop-ngc-py NGC images via Jupyter Kernel Operator


k8s-cmjkop-py Jupyter official image via Jupyter Kernel Operator
(Python)


k8s-cmjkop-julia Jupyter official image via Jupyter Kernel Operator
(Julia)


k8s-cmjkop-py-spark Python + Spark via Jupyter Kernel Operator


The administrator has to make sure that Kubernetes is correctly configured on the cluster Kyverno is
enabled and Kubernetes Permissions Manager is installed (section 4.10.2 of the _Containerization Manual_ ).
Details on Kubernetes installation are provided in Chapter 4 of the _Containerization Manual_ .
The default configuration proposed by cm-kubernetes-setup is usually sufficient to run Kubernetes
kernels created from BCM’s templates. However, it is the responsibility of the administrator to add
users registered in the Linux-PAM system to Kubernetes.
For example, a test user jupyterhubuser can be added to Kubernetes with:


**Example**


[root@basecm11 ~]# cm-kubernetes-setup --add-user jupyterhubuser --operators cm-jupyter-kernel-operator


For every new user added, cm-kubernetes-setup automatically generates a dedicated namespace
with a name in the form < _user_ >-restricted. For instance, the command in the example above, creates the
namespace: jupyterhubuser-restricted .
Cluster administrators are strongly recommended to review the security policies for Kyverno, RBAC,
and the dedicated namespaces.
In order to speed up kernel creation for the first user logging into JupyterLab when using BCM, it is
recommended that all the relevant Kubernetes images are pre-loaded on the compute nodes that Jupyter
Kernel Provisioning can contact.


**16.5.5** **Running Jupyter Kernels Based On NGC Containers**
Jupyter NGC templates are available in the list of templates if:


  - Kubernetes is set up


**16.5 Jupyter Kernel Creator Extension** **795**


  - NVIDIA GPUs are available on the Kubernetes cluster


  - Jupyter Kernel Operator (section 6.3 of the _Containerization Manual_ ) is installed


Figure 16.8: Jupyter Kernel Operator selection with cm-kubernetes-setup


It is also strongly advised to enable Kyverno on the Kubernetes cluster.


Figure 16.9: Kyverno policy engine selection in cm-kubernetes-setup


The user needs to be given permission to access to the Jupyter Kernel Operator. This can be done via
the cm-kubernetes-setup TUI, by adding a user, and then setting the permissions in the permissions
screen that shows up (figure 16.10):


Figure 16.10: User permissions in cm-kubernetes-setup


The permissions can also be configured using the CLI: