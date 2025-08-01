# cm-kubernetes-setup --add-user=alice --operators=cm-jupyter-kernel-operator


Once Jupyter kernel Operator is available, then kernel templates appear in the list:


**796** **The Jupyter Notebook Environment Integration**


Figure 16.11: Jupyter Kernel Operator templates


A kernel can be created from the template:


**16.5 Jupyter Kernel Creator Extension** **797**


Figure 16.12: Creating kernel from template


If authentication is required to access container images from the private registry, then the template
can be modified as described in section 6.3.8 of the _Containerization Manual_ .


**16.5.6** **Running Jupyter Kernels With Workload Managers**
BCM’s Jupyter Kernel Provisioning kernels can be created and run by users on compute nodes via
workload managers (WLMs). For convenience, Slurm is used as an example in this section. However,
the same instructions are valid for the other WLMs listed in table 16.1.

The templates used to create Slurm kernels are BCM’s


**798** **The Jupyter Notebook Environment Integration**


 - slurm-bash and


 slurm-py312,


which offer a Bash and a Python 3.12 environment respectively.
The administrator has to make sure that Slurm is correctly configured on the cluster. Slurm installation is described in section 7.3.

The default configuration that cm-wlm-setup suggests in Express mode is usually sufficient to run
Slurm kernels created from BCM’s templates. If Slurm is configured to automatically detect GPUs, they
will be listed as available resources while instantiating Slurm templates.
The Jupyter login node must be authorized to submit Slurm jobs. This is typically the case, since
the JupyterHub login node is by default the head node, and cm-wlm-setup by default assigns the
slurmsubmit role to the head node.

Finally, the administrator must make sure that relevant dependency packages are installed on the
software image used by Slurm clients. The image used is typically for the compute nodes. Missing
packages may cause kernels to fail at startup or at run time.
In particular, administrators need to install cm-python312 to use kernels based on the slurm-py312
template.


**16.6** **Jupyter Kernel Creator Extension Customization**


The Jupyter kernel templates described in section 16.5 are stored under the directory
/cm/shared/apps/jupyter/current/share/jupyter/kerneltemplates/ .
The template of a particular Jupyter kernel in BCM’s Jupyter Kernel Creator extension is a directory
containing at least two files: meta.yaml and kernel.json.j2 . The kernel template can also contain
other files placed in the same directory, such as icons. These files are copied to the target user kernels
directory upon kernel creation, after the template is instantiated.
The meta.yaml file includes all the parameters that can be substituted into kernel.json.j2 and is
defined with the YAML format ( [https://yaml.org/](https://yaml.org/) ).
The kernel.json.j2 file is a skeleton of the kernel.json file to be generated. It can contain some
placeholders, and is defined with the Jinja2 format ( [https://jinja.palletsprojects.com/](https://jinja.palletsprojects.com/) ).


**16.6.1** **Kernel Template Parameters Definition**
The kernel template meta.yaml file defines all the parameters that can be used in kernel.json.j2 .
It should contain three entries:


 - display_name : the name that will be displayed for the kernel in the JupyterLab Launcher;


 - features : a list of features that must be available on the cluster to show this kernel template to
JupyterLab users in the BCM extensions panel;


 - parameters : the variables for kernel.json.j2 .


The display_name entry is an arbitrary string:


[...]

display_name: "A simple kernel"

[...]


The features entry is a string that defines the condition under which the template becomes available
in the user interface. The features definitions are found within filter.yaml, which is in the same
directory as the kernel templates (section 16.5.1)
For example, a kernel template that only requires Kubernetes to work contains this line in its meta.yaml
file:


**16.6 Jupyter Kernel Creator Extension Customization** **799**


[...]

features: features: "k8s-jupyter-operator-enabled and k8s-nvidia-gpu-available"

[...]


and filter.yaml must have definitions of both conditions:


features:

[...]

k8s-jupyter-operator-enabled:

getter: shell

timeout: 5

exec:

   - "source /etc/profile.d/modules.sh"

   - "module load kubernetes"

   - "kubectl get cmjupyterkernels"

[...]

k8s-nvidia-gpu-available:

getter: shell

timeout: 5

exec:

   - "source /etc/profile.d/modules.sh"

   - "module load kubernetes"

   - "kubectl get nodes -o \\"

   - "jsonpath=\"{.items[*].status.capacity['nvidia\\.com/gpu']}\" \\"

   - "| egrep -q '.'"

[...]


The preceding means that a user can list cmjupyterkernels objects in Kubernetes, and that nodes
must have nvidia.com/gpu records available in their manifest
The scripts (the exec entries) in the preceding filters use typical values. For example, default values
for the Kubernetes environment module. These lines can be edited to be consistent with the actual

situation on the cluster.

The same principle and customizations should be considered for the other workload managers.
Finally, the parameters entry contains a dictionary of kernel parameters. The keys of the dictionary
are parameter names that are used in kernel.json.j2 . The values of the dictionary are options that
help users choose a correct value for the parameter. Parameter options are also dictionaries.
A kernel template meta.yaml is thus structured as:


[...]

parameters:

<parameter_name1>:

<option_key>: <option_value>

...

<option_key>: <option_value>

<parameter_name2>:

<option_key>: <option_value>

...

<option_key>: <option_value>

...

<parameter_nameN>:

<option_key>: <option_value>

...

<option_key>: <option_value>

[...]


Parameter names are arbitrary strings.
Option keys are strings. The only possible values for these strings are:


**800** **The Jupyter Notebook Environment Integration**


 - type


 - definition


 - limits


The option keys type and definition are mandatory. The option key limits is optional.
For example, a kernel template with two parameters foo and bar looks as follows:


**Example**


[...]

parameters:

foo:

type: <option_value>

definition: <option_value>

limits: <option_value>

bar:

type: <option_value>

definition: <option_value>

limits: <option_value>

[...]


**The** type **Option**
The type option key defines the type of the kernel parameter.
The type option key only accepts one of the following string values:


 - num : for numeric values (both float and integer are supported);


 - str : for arbitrary strings;


 - bool : for boolean values (a checkbox is presented in the user interface);


 - oneof : for picker to choose one value out out of several provided;


 - list : for lists of pre-defined or dynamically-generated settings;


 - uri : for interactive RESTful endpoints (only /kernelcreator/envmodules is currently supported).


**The** definition **Option**
The definition option key defines how the parameter value is retrieved and displayed.
The definition option key accepts dictionary-like values. Allowed string keys for the dictionary

are:


 - display_name : the name that is displayed for the parameter in the kernel customization dialog. It
accepts an arbitrary string as a value;


 - getter : how parameter values are retrieved. It only accepts as value one of the following strings:


**–** static : the values for the parameter are pre-defined;


**–** shell : the values for the parameter are the output of the shell script;


**–**
python : the values for the parameter are the output of a Python script;


 - values : possible values for the parameter that are displayed in the kernel customization dialog. It
accepts a list of arbitrary values;


 - default : default value for the parameter. It accepts a value from values ;


 - exec : the script to be executed to fill values when getter is shell or python . It accepts a
shell/Python script.


If type option value is list, then every line of getter with a setting of shell or python is treated as
an element of the list.


**16.6 Jupyter Kernel Creator Extension Customization** **801**


**The** limits **Option**
The limits option key offers a way to apply bounds on values provided by users. This usually reduces
the chances of making mistakes and helps users defining correct kernels before actually running them.
The limits option key accepts dictionary-like values according to the value chosen for the type
option key.
If num is the type, then limits can contain:


 - min : the minimum numeric value;


 - max : the maximum numeric value.


If str or list is the type, then limits can contain:


 - min_len : the minimum length of the string or the list;


 - max_len : the maximum length of the string or the list.


For example, if every node in the cluster has no more than 4 GPUs, then the upper limit on the
requested GPU number can be set to 4:


[...]

parameters:

gpus:

type: num

definition: <option_value>

limits:

min: 1

max: 4

[...]


These limits are not a security measure. They should be considered as convenient sanity checks
for values entered while instantiating a kernel template. This is because users are always able to later
directly edit the generated kernel.json, thereby ignoring such limits.


**16.6.2** **Kernel Template Parameters Usage**
During the creation of the kernel definition from the template, the kernel.json file is created from
kernel.json.j2, so all the Jinja2 variables are substituted based on the meta.yaml file and choices
provided by the user. When a kernel startup is initiated, Jupyter Kernel Provisioning uses kernel.json
and some internal variables to create WLM jobs or Kubernetes manifests from templates defined in the
kernel.json file.
Variables are available from a vars dictionary on kernel startup. These variables are defined within
a subsection of metadata.kernel_provisionersection . The subsection is config.< _subsection_ >.vars,
where < _subsection_ - depends on the chosen kernel provisioner.
Other dictionaries are internal and env .

The internal dictionary contains several variables defined at runtime:


 - uuid : Unique ID for every running kernel process. Does not persist across kernel restarts.


 - kernel_id : ID of the kernel. Persists across restarts.


 - kernel_spec_resource_dir : Full path to the kernel spec definition, normally: ~/.local/share/
jupyter/kernel-name .


 - username : PAM username of the user starting the kernel.


 - uid : PAM user’s UID.


 - gid : PAM user’s GID.


**802** **The Jupyter Notebook Environment Integration**


 - homedir : User’s home directory from the PAM database.


 - shell : User’s shell from the PAM database.


 - kernel_cmd : Command to run. For most kernels it is set to an empty string, as the actual command
is defined separately in WLM job or Kubernetes manifest templates.


The env variables pass some environment variables matching a regex in order to pass some variables
to be used in accessing API endpoints. Users thus do not need to hardcode API keys for notebooks.


**16.6.3** **Filtering Out Irrelevant Templates From The Interface For Users**
The list of kernel templates that are available for users of the Jupyter Kernel Creator can be modified as
follows:

In the parent directory of the templates, the file filter.yaml describes items called features . These
can be statically defined or they can represent scripts to be executed. The result of an executed script
can be true or false . If the script code exits with zero, then the result is true .
Every kernel template can have the feature field, which is a boolean expression that is calculated
when the JupyterLab extension is started.


**Example**


# cat filter.yaml

...

slurm:

getter: shell

timeout: 5

exec:

   - "source /etc/profile.d/modules.sh"

   - "module load slurm"

   - "sinfo"

...


# cat slurm-py312/meta.yaml

...

features: "slurm"

...


In the preceding example, the slurm-py312 template is shown in the JupyterLab interface if the script
in the exec: section is able to finish successfully.
It is also possible to define more complicated rules:


**Example**


# cat filter.yaml

features:

kubernetes:

getter: shell

timeout: 5

exec:

   - "source /etc/profile.d/modules.sh"

   - "module load kubernetes"

   - "kubectl get pods"

k8s-jupyter-operator-installed:

getter: shell

timeout: 5

exec:


**16.7 Jupyter VNC Extension** **803**


   - "source /etc/profile.d/modules.sh"

   - "module load kubernetes"

   - "(kubectl get cmjupyterkernels 2>&1 || true) \\"

   - "| egrep -q '^Error from server \\(Forbidden\\)'"

k8s-jupyter-operator-enabled:

getter: shell

timeout: 5

exec:

   - "source /etc/profile.d/modules.sh"

   - "module load kubernetes"

   - "kubectl get cmjupyterkernels"

...


# cat jupyter-eg-kernel-k8s-py/meta.yaml

--
display_name: "Python on Kubernetes"

features: "kubernetes and not k8s-jupyter-operator-installed and not k8s-jupyter-operator-enabled"

...


In the preceding example, jupyter-eg-kernel-k8s-py is shown when Kubernetes is installed, and
is hidden if Jupyter Kubernetes Operator is available for the user.
The filter.yaml file also supports statically defined features:


**Example**


features:

always-enabled:

getter: static

default: True

always-disabled:

getter: static

default: False

...


and supports Python code:


**Example**


python3-available:

getter: python

timeout: 5

exec:

   - "import sys"

   - "sys.exit(0) if sys.version_info.major == 3 else sys.exit(1)"

...


The Kubernetes Jupyter Kernel Operator is discussed in section 6.3 of the _Containerization Manual_ .


**16.7** **Jupyter VNC Extension**


**16.7.1** **What Is Jupyter VNC Extension About?**
VNC (Virtual Network Computing) is a screen sharing service that can work in a browser.
If VNC is allowed by the cluster administrator, then the Jupyter environment configured by BCM
can be used to start and control remote desktops via VNC with the _Jupyter VNC_ extension.
Several kernels created from BCM’s templates are capable of running VNC sessions so that users
can run GUI applications. In order to do so, the cluster nodes where kernels are executed must support
VNC.


**804** **The Jupyter Notebook Environment Integration**


During the cm-jupyter-setup run, the TUI prompts for installation of VNC servers on the nodes.
The cluster administrator can select the nodes on which it installs. On these nodes Jupyter kernels can
work with several types of VNC clients.


**16.7.2** **Enabling User Lingering**
User lingering is a systemd setting that sets a user manager for a user at boot and keeps it around after
logout. This allows that user to run long-running sessions despite not being logged in. Enabling user
lingering may be required for Jupyter VNC extension to run for a relatively complicated desktop such
as KDE or GNOME.

For each user on each machine where these environments are installed, the following command must
be run:


loginctl enable-linger < _username_ 

The command may also be carried out using prolog/epilog scripts in the chosen WLM.


**16.7.3** **Starting A VNC Session With The Jupyter VNC Extension**
Users can start a VNC session with the button added by Jupyter VNC (figure 16.13). Additional VNC
parameters can be optionally specified.


Figure 16.13: Starting Jupyter VNC session from kernel


If VNC is available and correctly configured on the node where the kernel is running, then a new
tab is automatically created by Jupyter VNC containing the new session (figure 16.14). A user can now
freely interact in JupyterLab both with the notebook and with the desktop environment.


**16.7 Jupyter VNC Extension** **805**


Figure 16.14: Running Jupyter VNC session from kernel


To provide a user-friendly experience, Jupyter VNC also allows the graphical viewport to be resized,
so that the desktop application can run full-screen (figure 16.15).


**806** **The Jupyter Notebook Environment Integration**


Figure 16.15: Running Jupyter VNC session from kernel (full-screen)


**16.7.4** **Running Examples And Applications In The VNC Session With The Jupyter VNC**
**Extension**

Once the VNC session is correctly started and the new JupyterLab tab has been created, Jupyter VNC
automatically exports the DISPLAY environment variable to the running notebook (figure 16.16). Doing
so means that any application or library running in the notebook can make use of the freshly created
desktop environment. An example of such a library is OpenAI Gym, a toolkit for developing and comparing reinforcement learning algorithms, that is distributed by BCM.
Among the examples distributed by BCM (section 16.3), a notebook running PyTorch in the OpenAI
Gym CartPole environment can be found. If executed after a VNC session has been started, a user can
then observe the model being trained in real time in the graphical environment.


Figure 16.16: Automatic configuration of DISPLAY environment variable


**16.8 Jupyter WLM Magic Extension** **807**


**16.8** **Jupyter WLM Magic Extension**


In the Jupyter environment configured by BCM, the _Jupyter WLM Magic_ extension can be used to schedule workload manager jobs from notebooks.
The Jupyter WLM Magic extension is an IPython extension. It is designed to improve the capabilities
of Jupyter’s default Python 3 kernel, which runs on the login node.
The Jupyter WLM Magic extension should therefore not be used from kernels running on compute
nodes, such as those typically created with BCM’s Jupyter Kernel Creator extension (section 16.5), and
submitted via Jupyter Kernel Provisioning. Indeed, compute nodes running these kernels are often
incapable of starting workload manager jobs in many default WLM configurations.
Jupyter WLM Magic extension makes it possible for users to programmatically submit WLM jobs,
and then interact with their results. This can be done while using the Python programming language
and its libraries, which are available in the notebook.
Users submit jobs and check their progress from the login node. The actual computation is distributed by the underlying workload manager across compute nodes, which means that server resources
are spared.
Jupyter WLM Magic commands are available in the IPython kernel as _magic functions_ ( [https://](https://ipython.readthedocs.io/en/stable/interactive/tutorial.html#magic-functions)
[ipython.readthedocs.io/en/stable/interactive/tutorial.html#magic-functions](https://ipython.readthedocs.io/en/stable/interactive/tutorial.html#magic-functions) ). A new line
magic ( % ) and a new cell magic ( %% ) are now added in the kernel, according to the workload manager:


  - Platform LSF: %lsf_job and %%lsf_job


  - PBS Professional: %pbspro_job and %%pbspro_job


  - Slurm: %slurm_job and %%slurm_job


A user can list the magic functions in the kernel to see if they are available, with Jupyter’s
builtin command %lsmagic ( [https://ipython.readthedocs.io/en/stable/interactive/magics.](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-lsmagic)
[html#magic-lsmagic](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-lsmagic) ):


**Example**


In []: %lsmagic

Out []: root:

line:

automagic:"AutoMagics"

autocall:"AutoMagics"

[...]

slurm_job:"SLURMMagic"

pbspro_job:"PBSProMagic"

lsf_job:"LSFMagic"

cell:

js:"DisplayMagics"

javascript:"DisplayMagics"

[...]

slurm_job:"SLURMMagic"

pbspro_job:"PBSProMagic"

lsf_job:"LSFMagic"


The magic functions introduced by this BCM extension share a similar syntax. For convenience,
Slurm is used as an example in this section. However, the same instructions are valid for the other
WLMs.

Users can check which options are available for a WLM function with the line magic helper:


**Example**


**808** **The Jupyter Notebook Environment Integration**


In []: %slurm_job --help
Out []: usage: %slurm_job [-h] [--module MODULE] [--module-load-cmd MODULE_LOAD_CMD]

[--shell SHELL] [--submit-command SUBMIT_COMMAND]

[--cancel-command CANCEL_COMMAND]

[--control-command CONTROL_COMMAND]

[--stdout-file STDOUT_FILE] [--stderr-file STDERR_FILE]

[--preamble PREAMBLE] [--timeout TIMEOUT]

[--check-condition-var CHECK_CONDITION_VAR]

[--job-id-var JOB_ID_VAR]

[--stdout-file-var STDOUT_FILE_VAR]

[--stderr-file-var STDERR_FILE_VAR] [--dont-wait]

[--write-updates WRITE_UPDATES]

[--check-status-every CHECK_STATUS_EVERY]


optional arguments:

-h, --help show this help message and exit

[...]


Line magic functions are typically used to set options with a global scope in the notebook. By doing
so, a user will not need to specify the same option every time a job will be submitted via cell magic. For
example, if two Slurm instances are deployed on the cluster and their associated environment modules
are slurm-primary and slurm-secondary, a user could run the following line magic once to configure
the Jupyter WLM Magic extension to always use the second deployment:


**Example**


In []: %slurm_job --module slurm-secondary

Out []:


Now, jobs will always be submitted to slurm-secondary . This is more convenient than repeatedly
defining the same module option for every cell magic upon scheduling a job:


**Example**


In []: %%slurm_job --module slurm-secondary

<WLM JOB DEFINITION>

Out []: <WLM JOB OUTPUT>

In []: %%slurm_job --module slurm-secondary

<WLM JOB DEFINITION>

Out []: <WLM JOB OUTPUT>


It should be noted that line magic functions cannot be used to submit WLM jobs. Cell magic functions have to be used instead.

A well-defined cell contains the WLM cell magic function provided by the extension, followed by
the traditional job definition. For example, a simple MPI job running on two nodes can be submitted to
Slurm by defining and running this cell:


**Example**


In []: %%slurm_job

#SBATCH -J mpi-job-example

#SBATCH -N 2

module load openmpi

mpirun hostname

Out []: COMPLETED

STDOUT file content: /home/demo/.jupyter/wlm_magic/slurm-1.out


**16.9 Jupyter Kubernetes Operators Manager** **809**


node001

node001

node002

node002


Users can take advantage of the Jupyter WLM Magic extension to store some information into Python
variables about the job being submitted. The information could be the ID or the output file name, for
example. Users can then later programmatically interact with them in Python. This feature is convenient when a user wants to, for example, programmatically carry out new actions depending on the job
output:


**Example**


In []: %%slurm_job --job-id-var my_job_id --stdout-file-var my_job_out

#SBATCH -J mpi-job-example

#SBATCH -N 2

module load openmpi

mpirun hostname

Out []: COMPLETED

STDOUT file content: /home/demo/.jupyter/wlm_magic/slurm-2.out

node001

node001

node002

node002


In []: print(f"Job id {my_job_id} was written to {my_job_out}")
print(f"Output lines: {open(my_job_out).readlines()}")
Out []: Job id 2 was written to /home/demo/.jupyter/wlm_magic/slurm-2.out
Output lines: ['node001\n', 'node001\n', 'node002\n', 'node002\n']


Users can also exploit Python variables to define the behavior of the Jupyter WLM Magic extension.
For example, they can define a Python boolean variable to submit a WLM job only if a condition is true:


**Example**


In []: run_job = 1 == 2

Out []:


In []: %%slurm_job --check-condition-var run_job

#SBATCH -J mpi-job-example

#SBATCH -N 2

module load openmpi

mpirun hostname
Out []: Variable run_job is 'False'. Skipping submit.


**16.9** **Jupyter Kubernetes Operators Manager**


The Jupyter Kubernetes Operators Manager tool is designed to make it easier to handle everyday tasks
involving Kubernetes.
Some of the items that the tool can manage are:


  - Pods


  - PostgreSQL databases


  - Spark tasks (jobs that process a lot of data)


**810** **The Jupyter Notebook Environment Integration**


  - Persistent Volume Claims (requests for specific storage space). Particularly handy is the ability to
move data between user folders and Persistent Volumes (special types of storage space in Kubernetes).


Jupyter Kubernetes Operators Manager can be accessed as follows in the Jupyter Notebooks web
interface (figure 16.17):


Figure 16.17: Jupyter Kubernetes Operators Manager: Kubernetes cluster list and selection


1. The NVIDIA Base Command Manager logo (on the left side of the screen, ) is clicked. A list of
Kubernetes clusters is then displayed.


2. The Cluster View button is used to select the cluster that is to be worked with.


Jupyter Kubernetes Operators Manager displays resources and objects via a tabbed view. This view
is for the restricted namespace to which the user has access. With Kubernetes as set up by BCM, this is
the namespace of the form < _user_ >-restricted .


**16.9.1** **Overview Tab**

The Overview tab (figure 16.18) provides a high-level overview of the current state of the selected Kubernetes cluster.


**16.9 Jupyter Kubernetes Operators Manager** **811**


Figure 16.18: Jupyter Kubernetes Operators Manager: overview


Among other useful details, it displays:


  - the cluster name


  - the Kubernetes version that is running


  - the number of namespaces and pods


**16.9.2** **Jupyter Kernel Overview Tab**
The Jupyter Kernel Overview tab (figure 16.19) lists active Jupyter kernel instances along with their
associated events.


Figure 16.19: Jupyter Kubernetes Operators Manager: Jupyter kernel overview tab


**812** **The Jupyter Notebook Environment Integration**


After a kernel is stopped or removed, these events can be found under the Events tab. Events are
discussed later on.


**16.9.3** **Jobs Tab**

The Jobs tab (figure 16.20) allows a data migration job to be run. A data migration job manages the
transfer of data between the user-accessible directories of the filesystem and the Persistent Volumes.
The transfer can be managed in either direction.
The data transfer is needed to enable access to the data for Spark instances, and for situations where
pods need to be run under a different user ID/group ID (UID/GID) from the original user.


Figure 16.20: Jupyter Kubernetes Operators Manager: Jupyter data migration jobs tab


To initiate a data migration job, several fields must be set. This can be done via a pop-up dialog, that
comes up on clicking either of these buttons:


 - New job from Config : allows a YAML file configuration to be submitted


 - New Job : allows direct configuration (figure 16.21)


**16.9 Jupyter Kubernetes Operators Manager** **813**


Figure 16.21: Jupyter Kubernetes Operators Manager: data migration jobs creation


Fields that may be set include:


 - **Job name** : specifies the name of the migration job.


 - **Direction** : sets the direction of the data migration.


**–** to-k8s : copies data to the Persistent Volume Claim (PVC) from the file system


**–** from-k8s : copies data from the PVC back to the file system


 - **Path** : provides the path on the filesystem to/from where the data is migrated


 - **PVC** : sets the name of the Persistent Volume Claim that is involved in the data migration.


Optionally, the Force Delete checkbox can be ticked. If ticked, then the migration job deletes data
from the target location if the corresponding file or directory does not exist in the source location.
In particular, if the source location is completely empty, then setting Force Delete results in the
removal of all target data. Setting Force Delete should therefore be done with caution due to the
significant data loss that it can cause.
The execution status of a job can be monitored in the status and events area. This section displays
the number of worker pods and their respective statuses, which include:


 - **Running** : the number of pods currently in operation.


 - **Completion** : the desired number of pods that should successfully complete the job. Not applicable
for migration jobs, but it can be used if a custom manifest is specified, as described later.


 - **Succeeded** : The number of pods that have successfully completed their tasks.


 - **Failed** : The number of pods that have failed to complete their tasks.


Additionally, a custom job manifest can be uploaded from the user’s workstation if required.


**16.9.4** **Pods Tab**

The Pods tab (figure 16.22) displays user pods, reads stdout, and shows associated events from pods.


**814** **The Jupyter Notebook Environment Integration**


Figure 16.22: Jupyter Kubernetes Operators Manager: pods overview tab


The tab also allows pod creation from a custom definition manifest uploaded from the user’s workstation, or by filling out a simplified form with commonly used fields:


1. **Name** : name of the Pod.


2. **Command** : program and its arguments that are to run inside the Pod.


3. **Image** : container image.


4. **Host Path** (Optional): path to mount from the filesystem. If used, the UID/GID of the running
process matches the UID/GID of the user.


5. **Environment Variables** (Optional): These variables are set for the process inside the running Pod.


6. **PVCs** (Optional): A list of Persistent Volume Claims and the path to mount them inside the Pod.


In figure 16.23 main.py has been downloaded earlier from the official PyTorch repository and placed
in the user’s home directory using wget :


wget https://raw.githubusercontent.com/pytorch/examples/main/mnist/main.py


**16.9 Jupyter Kubernetes Operators Manager** **815**


Figure 16.23: Jupyter Kubernetes Operators Manager: pod creation


**16.9.5** **PVCs Tab**

A Persistent Volume Claim (PVC) is a user’s request for a specific amount of storage space within a
Kubernetes cluster with defined characteristics.
The PVCs tab (figure 16.24) displays an overview of the PVCs.


Figure 16.24: Jupyter Kubernetes Operators Manager: PVCs overview tab


The tab allows users to manage existing PVCs or create new ones via a dialog.


**816** **The Jupyter Notebook Environment Integration**


To create a new PVC, several fields must be set. This can be done via a pop-up dialog, that comes up
on clicking either of these buttons:


  - the New PVC from Config button: This allows a YAML file configuration to be submitted to set
the fields.


  - the New PVC button: This allows the configuration to be set directly (figure 16.25).


Figure 16.25: Jupyter Kubernetes Operators Manager: PVC creation


To create a new PVC directly, the following fields need to be set in the form:


1. **Storage class** : The storage class is local-path for now in BCM version 11.


2. **Volume mode** : can be either


   - Filesystem, where the requested space is accessible as a formatted filesystem, or


   - Block, where the space is accessible as a raw block device.


For the local-path storage class, only Filesystem is available.


3. **Instance name** : arbitrary name of the PVC.


4. **Instance size (GB)** : requested size. It can be ignored for local-path, as quotas are not supported for shared filesystems. The resulting volumes for a cluster < _cluster_name_    - are located under
/cm/shared/apps/kubernetes/< _cluster_name_ >/var/volumes and are configurable during cluster
setup.


5. **Select access mode** :


   - **ReadWriteOnce** : The volume can be mounted as read-write by a single node. Multiple pods
can still access the volume if they are running on the same node.


   - **ReadOnlyMany** : The volume can be mounted as read-only by many nodes.


   - **ReadWriteMany** : The volume can be mounted as read-write by many nodes.


**16.9 Jupyter Kubernetes Operators Manager** **817**


**16.9.6** **PSQL Tab**

The PSQL tab (figure 16.26) provides a simplified interface for interacting with the Zalando PostgreSQL
Operator. It offers an overview of instances running on the cluster, it displays associated events, and
provides credentials and access points for running PSQL databases. This information can be used later
in Jupyter Notebooks or other PSQL clients.


Figure 16.26: Jupyter Kubernetes Operators Manager: PSQL overview


The tab allows users to manage existing PostgreSQL databases or to create new ones via a dialog.
An example notebook is located at /cm/shared/examples/jupyter/notebooks/psql-example.ipynb
(figure 16.27).


**818** **The Jupyter Notebook Environment Integration**


Figure 16.27: Jupyter Kubernetes Operators Manager: PSQL notebook


There are two buttons in figure 16.26:


 - New PSQL instance from Config : allows a YAML file configuration that sets the fields to be submitted


 - New instance : allows the fields to be set directly (figure 16.28)


Clicking either button displays a pop-up dialog for creating a new PostgreSQL instance. For example,
the New instance button displays the creation form in figure 16.28.


Figure 16.28: Jupyter Kubernetes Operators Manager: PSQL instance creation


The creation form accepts the following values:


1. **Instance name** : PSQL instance name. An auto-generated team name is prefixed to this name


2. **Database name** : arbitary database name


**16.9 Jupyter Kubernetes Operators Manager** **819**


3. **Admin user** (Optional): if not set, the name of the admin user is set to the database name


4. **Instance size (GB)** : data storage size requirement for the volumes


**16.9.7** **Spark Tab**
The Spark Jobs tab (figure 16.29) simplifies dealing with Spark clusters managed by the Google Spark
Operator. The tab lets users list, remove, and create Spark instances using a simplified interface. If a
particular option is not available in the simplified form, then a custom manifest can be uploaded.


Figure 16.29: Jupyter Kubernetes Operators Manager: Spark overview


There are two buttons in figure 16.29:


 - New Spark Job from Config : allows a YAML file configuration that sets the fields to be submitted


 - New Spark Job : allows the fields to be set directly (figure 16.30)


Clicking either button displays a pop-up dialog for creating a new Spark instance. For example, the New
Spark Job button displays the creation form in figure 16.30. The creation form requires the following
values:


1. **Name** : Arbitrary name of the Spark instance.


2. **Image** : Container image for the driver and executor.


3. **Spark Version** : Version of Spark used by the application.


4. **Command** : Application’s command with arguments.


5. **Executor Instances** : Number of executors.


6. **PVCs** (Optional): List of Persistent Volume Claims with mountpoints where these volumes are
mounted. Used to store the application and datasets, as well as packed virtual environment
archives.


7. **Virtual Environment** (Optional): Configuration for the ’spark.archives’ configuration variable for
the Python virtual environment.


**820** **The Jupyter Notebook Environment Integration**


   - **PVC** : Name of the Persistent Volume Claim with empty Volume which are used to store the
unpacked archive.


   - **Archive** : Full path to the archive.


   - **Python Path** (Optional): Python path (default /bin/python ).


8. **Driver Resources** (Optional):


   - **Memory** : Amount of memory to request for the pod.


   - **GPU** : List of key-value pairs such as nvidia.com/gpu, 3 .


   - **Cores** : Number of cores to use for the driver process.


   - **Environment** : List of key-value pairs for environment variables.


9. **Executor Resources** (Optional): Same as Driver Resources .


10. **Spark Config** (Optional): Custom configuration parameters if necessary. They are key-value pairs,
documented in the Spark documentation at [https://spark.apache.org/docs/latest/configuration.](https://spark.apache.org/docs/latest/configuration.html)

[html](https://spark.apache.org/docs/latest/configuration.html) .


**Example: Calculating Pi**
The simplest way to run Spark involves specifying just three values: the name, the script to execute,
and the Spark version. For example, the container registry image gcr.io/spark-operator/spark-py:
v3.1.1 provided by Google can be used, and an application to calculate the value for _π_ is located at
/opt/spark/examples/src/main/python/pi.py inside the image.


Figure 16.30: Jupyter Kubernetes Operators Manager: Spark creation


**16.9 Jupyter Kubernetes Operators Manager** **821**


The progress of execution can be monitored in the Pods tab (figure 16.31):


Figure 16.31: Jupyter Kubernetes Operators Manager: pods tab Spark example execution status


When the job is completed, the overview page is updated (figure 16.32):


Figure 16.32: Jupyter Kubernetes Operators Manager: pods tab Spark example completed status


**Example: Running MNIST**
The source files for the MNIST example are located in the /cm/shared/examples/jupyter/spark-operator-mnist
directory


**822** **The Jupyter Notebook Environment Integration**


**Example**


$ id

uid=1001(alice) gid=1001(alice) groups=1001(alice)

$ ls -l /home/alice/mnist/

total 12

-rwxr-xr-x 1 alice alice 241 Jun 28 16:02 create-venv.sh

drwxr-xr-x 2 alice alice 76 Jun 28 17:10 data

-rw-r--r-- 1 alice alice 2719 Jun 28 16:02 mnist.py

-rw-r--r-- 1 alice alice 46 Jun 28 16:02 requirements.txt

$ ls -l /home/alice/mnist/data

total 124952

-rw-rw-r-- 1 alice alice 18303650 Oct 1 2019 mnist_test.csv

-rw-rw-r-- 1 alice alice 109640201 Oct 1 2019 mnist_train.csv

-rw-r--r-- 1 alice alice 91 Jun 28 16:02 README.md


In the example the user is unable to train the model defined in mnist.py right away, as the image
gcr.io/spark-operator/spark-py:v3.1.1 does not have the required NumPy library. So, before running the Spark job, the virtual environment archive needs to be created.
The safest way to create the Python environment is to use the same context as where the archive is
to be used later on. That way there are no missing or conflicting libraries and paths, and the Python
version matches. The gcr.io/spark-operator/spark-py:v3.1.1 image itself can therefore be used to
create the archive. The script create-venv.sh creates the create archive from requirements.txt file
and packs it.
In this example, a newly persistent volume (PV) is used as an intermediate storage for all the data
and scripts, because using a file system where all the files are located would be a security concern. The
reason for this is that once the hostPath is used for the pod, the running process UID/GID is dropped,
and becomes the same as the original user (section 4.10.1 of the _Containerization Manual_ ). Spark images
are usually not designed with this assumption in mind, and use UID 185 to run the application ( [https:](https://spark.apache.org/docs/3.1.1/running-on-kubernetes.html#user-identity)
[//spark.apache.org/docs/3.1.1/running-on-kubernetes.html#user-identity](https://spark.apache.org/docs/3.1.1/running-on-kubernetes.html#user-identity) ).
With these criteria in mind, the steps to run the MNIST example are:


1. Create a PVC for storing scripts and datasets (figure 16.33). Since the resulting persistent volume
is expected to be mounted to all pods (driver and executors), its mode is set to ReadWriteMany .


Figure 16.33: Jupyter Kubernetes Operators Manager: PVC creation for Spark example


**16.9 Jupyter Kubernetes Operators Manager** **823**


2. Migrate data from the home folder to the volume. To do this, a migration job is created (figure 16.34), and allowed to finish (figure 16.35).


Figure 16.34: Jupyter Kubernetes Operators Manager: Data migration job creation for Spark example


Figure 16.35: Jupyter Kubernetes Operators Manager: Data migration job for Spark example successfully finished


3. Create a pod to build a packed virtual environment (figure 16.36). For this, mnist-data-pvc
is mounted by the user as the /mnist directory inside the pod. The command
/mnist/create-venv.sh /mnist/requirements.txt /mnist/venv.tar.gz is then executed.
This places the venv.tar.gz archive next to the other files in the volume.


**824** **The Jupyter Notebook Environment Integration**


Figure 16.36: Jupyter Kubernetes Operators Manager: pod creation for virtual environment


4. (Optional) If necessary, data can be downloaded from the volume back to the user’s home directory, to save the venv.tar.gz for future use (figure 16.37):


Figure 16.37: Jupyter Kubernetes Operators Manager: migrate venv to PVC


The venv.tar.gz file is placed in the /home/alice/mnist directory.


$ ls -l /home/alice/mnist/

total 261516

-rwxr-xr-x 1 alice alice 241 Jun 28 19:17 create-venv.sh

drwxr-xr-x 2 alice alice 99 Jun 28 19:17 data

-rw-r--r-- 1 alice alice 2719 Jun 28 19:17 mnist.py

-rw-r--r-- 1 alice alice 46 Jun 28 19:17 requirements.txt


**16.9 Jupyter Kubernetes Operators Manager** **825**


-rw-r--r-- 1 alice alice 237896720 Jun 28 19:17 venv.tar.gz


5. Another volume is created to store the unpacked virtual environment files (figure 16.38). This is
mounted to all pods (driver and executor). The driver unpacks the archive, and the content is used
by the executors.


Figure 16.38: Jupyter Kubernetes Operators Manager: volume creation for unpacked virtual environment files


6. The Spark job can now be created (figure 16.39):


**826** **The Jupyter Notebook Environment Integration**


Figure 16.39: Jupyter Kubernetes Operators Manager: create Spark job


The execution progress can be monitored in the Pods tab (figure 16.40):


**16.9 Jupyter Kubernetes Operators Manager** **827**


Figure 16.40: Jupyter Kubernetes Operators Manager: monitoring the Spark instance in the Pods tab


**16.9.8** **Events Tab**

The Events tab lists all events from the user’s namespace (figure 16.41):


Figure 16.41: Jupyter Kubernetes Operators Manager: events overview


**828** **The Jupyter Notebook Environment Integration**


**16.10** **Jupyter Environment Removal**


Before removing Jupyter, the administrator should ensure that all kernels have been halted, and that no
user is still logged onto the web interface. Stopping the cm-jupyterhub service with users that are still
logged in, or with running kernels, has undefined behavior.
To remove Jupyter, the script cm-jupyter-setup must be run, either in interactive mode, or with the
option --remove .
Removing Jupyter does not remove or affect Kubernetes or WLM deployments.
For a more complete cleanup, the following packages must be manually removed
from the nodes involved in the Jupyter deployment: cm-jupyter, cm-jupyter-local, and
cm-npm-configurable-http-proxy .


# **A**

### **Generated Files**

This appendix contains lists of system configuration files that are managed by CMDaemon, and system
configuration files that are managed by node-installer. These are files created or modified on the head
nodes (section A.1), and on the regular nodes (sections A.2.3 and A.2.3). These files should not be
confused with configuration files that are merely installed (section A.3).
Section 2.6.5 describes how system configuration files on all nodes are written out using the Cluster
Management Daemon (CMDaemon). CMDaemon is introduced in section 2.6.5 and its configuration
directives are listed in Appendix C.
All of these configuration files may be listed as Frozen Files in the CMDaemon configuration file
to prevent them from being modified further by CMDaemon. The files can be frozen for the head node
by setting the directive at /cm/local/apps/cmd/etc/cmd.conf . They can also be frozen on the regular
nodes by setting the directive in the software image, by default at /cm/images/default-image/cm/
local/apps/cmd/etc/cmd.conf .
A list of CMDeamon- and node-installer-managed files for nodes can be seen by running the command filewriteinfo in device mode. The command has options to run it for node groupings, as well
useful path and sort options.


**A.1** **System Configuration Files Created Or Modified By CMDeamon On Head**
**Nodes**


If the filewriteinfo command is run for the head node, then it displays the files that have been written
by CMDaemon on the head node. Running the filewriteinfo command for the head node might
display the following on a fresh installation:


[basecm11->device]% filewriteinfo basecm11

Hostname Path Timestamp Actor Frozen

-------- ------------------------------------------------------------------ ---------- ----- -----
basecm11 /cm/images/default-image/etc/mkinitrd_cm.conf Mon Oct... cmd no
basecm11 /cm/images/default-image/etc/modprobe.d/bright-cmdaemon.conf Mon Oct... cmd no
basecm11 /cm/images/default-image/etc/securetty Mon Oct... cmd no
basecm11 /etc/chrony.conf Mon Oct... cmd no
basecm11 /etc/dhcp/dhclient.conf Mon Oct... cmd no
basecm11 /etc/dhcpd.conf Mon Oct... cmd no
basecm11 /etc/exports Mon Oct... cmd no
basecm11 /etc/genders Mon Oct... cmd no

basecm11 /etc/named.conf Mon Oct... cmd no

basecm11 /etc/postfix/canonical Mon Oct... cmd no
basecm11 /etc/postfix/generic Mon Oct... cmd no
basecm11 /etc/postfix/main.cf Mon Oct... cmd no

basecm11 /etc/resolv.conf Mon Oct... cmd no

basecm11 /etc/security/pam_bright.d/cm-check-alloc.conf Mon Oct... cmd no


**830** **Generated Files**


basecm11 /etc/shorewall.staging/interfaces Mon Oct... cmd no
basecm11 /etc/shorewall.staging/netmap Mon Oct... cmd no
basecm11 /etc/shorewall.staging/policy Mon Oct... cmd no
basecm11 /etc/shorewall.staging/snat Mon Oct... cmd no
basecm11 /etc/shorewall.staging/zones Mon Oct... cmd no
basecm11 /etc/sysconfig/network-scripts/ifcfg-eth1 Mon Oct... cmd no
basecm11 /tftpboot/images/default-image//boot Mon Oct... cmd no
basecm11 /tftpboot/images/default-image/initrd Mon Oct... cmd no
basecm11 /tftpboot/images/default-image/vmlinuz Mon Oct... cmd no
basecm11 /tftpboot/mtu.conf Mon Oct... cmd no
basecm11 /tftpboot/pxelinux.cfg/category.default Mon Oct... cmd no

basecm11 /var/run/cmd.url Mon Oct... cmd no

basecm11 /var/spool/cmd/my.cmd.url Mon Oct... cmd no
basecm11 /var/spool/cmd/my.master.cmd.url Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-chrony.conf Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-dhcp-dhclient.conf Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-dhcpd.conf Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-exports Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-named.conf Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-postfix-canonical Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-postfix-generic Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-postfix-main.cf Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-resolv.conf Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-shorewall.staging-interfaces Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-shorewall.staging-netmap Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-shorewall.staging-policy Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-shorewall.staging-snat Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-shorewall.staging-zones Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/etc-sysconfig-network-scripts
ifcfg-eth1 Mon Oct... cmd no
basecm11 /var/spool/cmd/saved-config-files/tftpboot-mtu.conf Mon Oct... cmd no


The filewriteinfo command is covered in more detail in section A.2.

The more important head node files that are managed by CMDaemon are listed here for a plain
installation on the various distributions.


**Some of the more important files managed automatically on the head node by CMDaemon In RHEL and**

**derivatives, Ubuntu 22.04, 24.04, SLES15**


**File** **Part** **Comment**


/cm/local/apps/openldap/etc/ Section CMDaemon modifies this when edge, cloud or
slapd.conf HA are activated


/cm/local/apps/<PBS>/var/cm/ Section <PBS> can be one of openpbs pbspro

cm-pbs.conf


_. . . continues_


**A.1 System Configuration Files Created Or Modified By CMDeamon On Head Nodes** **831**


_...continued_


**File** **Part** **Comment**


/cm/local/modulefiles/<module> Entire di- <module> is a file or directory for a modules enrectory vironment module (section 2.2.4). For example,
slurm, which is automatically created and made
available for use after the Slurm workload man
ager is set up with cm-wlm-setup (section 7.3).


/cm/node-installer/etc/ Section

sysconfig/clock


/etc/aliases Section


/etc/bind/named.conf Entire file Ubuntu only. For zone additions use /etc/
bind/named.conf.include [1] . For options additions, use /etc/bind/named.conf.global.

options.include .


/etc/chrony.conf Section RHEL8,9 and derivatives only


/etc/dhcpd.conf Entire file


/etc/dhcp/dhclient.conf Section Not for SLES


/etc/dhcpd.internalnet.conf Entire file For internal networks other than internalnet,
corresponding files are generated if node booting (table 3.1) is enabled


/etc/exports Section


/etc/fstab Section


/etc/genders Section


/etc/hosts Section


/etc/localtime Symlink


/etc/logrotate.d/slurm Entire file


/etc/logrotate.d/slurmdbd Entire file


/etc/named.conf Entire file Non-Ubuntu distributions only (Ubuntu uses
/etc/bind/named.conf ). For zone additions
use /etc/named.conf.include [1] . For options additions, use /etc/named.conf.global.

options.include .


/etc/ntp.conf Section Ubuntu and SUSE only


/etc/postfix/canonical Section


/etc/postfix/generic Section


/etc/postfix/main.cf Section


_. . . continues_


**832** **Generated Files**


_...continued_


**File** **Part** **Comment**


/etc/resolv.conf Section The stub resolver can alternatively be
provided by systemd-resolved ( man
systemd-resolved.8, page 86)


/etc/shorewall6.staging/ Section

interfaces


/etc/shorewall6.staging/policy Section


/etc/shorewall6.staging/rules Section


/etc/shorewall6.staging/snat Section


/etc/shorewall6.staging/zones Section


/etc/shorewall/interfaces Section


/etc/shorewall/netmap Section


/etc/shorewall/policy Section


/etc/shorewall/rules Section


/etc/shorewall/snat Section


/etc/shorewall/zones Section


/etc/snmp/snmptrapd.conf Section


/etc/sysconfig/bmccfg Entire file BMC configuration and BCM configuration


/etc/sysconfig/clock Section


/etc/sysconfig/dhcpd Entire file


/etc/sysconfig/network-scripts/ Section

ifcfg-*


/tftpboot/mtu.conf Entire file BCM configuration


/tftpboot/pxelinux.cfg/category. Entire file BCM configuration

default


/var/lib/named/*.zone [1,2] Entire file For SLES distributions only. For custom additions use /var/lib/named/*.zone.include

/var/named/*.zone [1,2] Entire file For RHEL8, RHEL9 distributions only. For
custom additions use /var/named/*.zone.

include


1
User-added zone files ending in *.zone that are placed for a corresponding zone statement in the


include file /etc/[bind/]named.conf.include are wiped by CMDaemon activity. Another pattern,


eg: *.myzone, must therefore be used instead

2 For Ubuntu, the zone files are under /etc/bind/


**A.2** **System Configuration Files Created Or Modified Directly On The Node**


Files that are created or modified by CMDaemon or the node-installer directly on the node by CMDeamon can be seen with the filewriteinfo command.

For example, for a particular node, in this case node002 (some output elided):


**Example**


[basecm11->device]% filewriteinfo node002

Hostname Path Timestamp Actor Frozen

----------- --------------------------------------- ------------------------- --------------- -----

**A.2 System Configuration Files Created Or Modified Directly On The Node** **833**


node002 /certificates/fa-16-3e-54-bb-a1/cert Thu Jul 14 12:16:00 2022 node-installer no

...

node002 /etc/chrony.conf Thu Jul 14 12:17:08 2022 node-installer no

...

node002 /etc/exports Thu Jul 14 12:17:58 2022 cmd no

...


In the preceding, /etc/exports is seen to have been changed by cmd, which is listed under the Actor
column.


**A.2.1** **Options To** filewriteinfo
Options to filewriteinfo can be viewed with the help filewwriteinfo command.
Some of the options are:


 - -n|--node : This can be used to specify a node list (page 67).


 - --field : The --field option can be used with, for example, the mac field, as follows (some output
elided):


**Example**


[basecm11->device]% get node002 mac

FA:16:3E:54:BB:A1

[basecm11->device]% filewriteinfo --field mac=FA:16:3E:54:BB:A1

Hostname Path Timestamp Actor Frozen

----------- --------------------------------------- ------------------------- --------------- -----
node002 /certificates/fa-16-3e-54-bb-a1/cert Thu Jul 14 12:16:00 2022 node-installer no

...

node002 /etc/chrony.conf Thu Jul 14 12:17:08 2022 node-installer no

...

node002 /etc/exports Thu Jul 14 12:17:58 2022 cmd no

...


The preceding example has the same output as for the session with filewriteinfo node002 on
page 832.


**–** A pitfall to avoid is the following: The columns headers of the output of the filewriteinfo
command, such as Actor, are not keys for the --field option.


**Example**


[basecm11->device]% filewriteinfo node002 --field Actor=cmd #this is incorrect


Instead, as is the norm for a device mode command, it is the fields of the mode that are the
key=value pairs (for keys that are valid for the device concerned). The fields of the device
mode are displayed when the format command (page 55) is run.


 - --sort : This sorts the filewriteinfo output according to column headers ( Actor, Timestamp and
so on).


 - --path : This can be used to specify a file.


**Example**


[basecm11->device]% filewriteinfo --path /etc/chrony.conf --sort actor

Hostname Path Timestamp Actor Frozen

---------------- ----------------- ------------------------- --------------- -----------
basecm11 /etc/chrony.conf Thu Jul 14 12:14:25 2022 cmd no
node001 /etc/chrony.conf Thu Jul 14 12:17:08 2022 node-installer no
node002 /etc/chrony.conf Thu Jul 14 12:17:08 2022 node-installer no


**834** **Generated Files**


**A.2.2** **Files Created On Regular Nodes By CMDaemon**
Files on a regular node that are modified by CMDaemon can be seen in the output of filewriteinfo .
The filewriteinfo command displays a list of the last files written by the cluster manager.
For a default installation, the list is as shown in the following table:


**A.2 System Configuration Files Created Or Modified Directly On The Node** **835**


**System configuration files created or modified on a default regular nodes image by CMDaemon**


**File** **Part** **Comment**


/etc/aliases Section


/etc/fstab Section SLES only


/etc/hosts Section


/etc/nslcd.conf Section RHEL8 and derivatives, and
Ubuntu only


/etc/pam.d/sshd Section


/etc/postfix/main.cf Section


/etc/rsyslog.conf Section RHEL9 and derivatives, and
SLES only


/etc/security/pam_bright.d/cm-check-alloc.conf Entire file


/var/run/cmd.url Entire file


/var/spool/cmd/my.cmd.url Entire file


/var/spool/cmd/my.master.cmd.url Entire file


/var/spool/cmd/saved-config-files/etc-aliases Entire file
Section


/var/spool/cmd/saved-config-files/etc-fstab Entire file SLES Only


/var/spool/cmd/saved-config-files/etc-hosts Entire file


/var/spool/cmd/saved-config-files/etc-nslcd.conf Entire file RHEL8 and derivatives, and
Ubuntu only


/var/spool/cmd/saved-config-files/etc-pam.d-sshd Entire file


/var/spool/cmd/saved-config-files/etc-postfix-main.cf Entire file


/var/spool/cmd/saved-config-files/etc-rsyslog.conf Entire file RHEL9 and derivatives, and
SUSE only


**A.2.3** **Files Created On Regular Nodes By The Node-Installer**
The list of files on a regular node that are modified by the node-installer during the last installation
session can be viewed in the logs at /var/log/modified-by-node-installer.log on the node, and in
the output of filewriteinfo . For a default installation, these are as shown in the following table:


**836** **Generated Files**


**System configuration files created or modified on regular nodes by the node-installer in RHEL8, RHEL9 and**

**derivatives**


**File** **Part** **Comment**


/etc/sysconfig/network-scripts/ifcfg-* Entire Interfaces for RHEL8, RHEL9 and derivatives only


/etc/network/interfaces.d/ifcfg-* Entire file Ubuntu only


/etc/sysconfig/network/ifcfg-* Entire file SUSE only,


/etc/sysconfig/network Section Only for RHEL8, RHEL9 and derivatives


/etc/sysconfig/network/config Section Only for SLES


/etc/sysconfig/network/routes Section Only for SLES


/etc/resolv.conf Entire file Only for RHEL8, RHEL9 and derivatives


/etc/hosts Section


/etc/fstab Section Not for SLES. In SLES it is managed by CMDaemon


/etc/postfix/main.cf Section


/etc/chrony.conf Entire file RHEL8,RHEL9 and derivatives only


/etc/ntp.conf Entire file SUSE and Ubuntu only


/etc/systemd/resolved.conf Entire file Ubuntu only


/etc/hostname Section


/cm/local/apps/cmd/etc/cert.key Section


/cm/local/apps/cmd/etc/cert.pem Section


/cm/local/apps/cmd/etc/cluster.pem Section


/cm/local/apps/openldap/etc/certs/ldap.key Section


/cm/local/apps/openldap/etc/certs/ldap.pem Section


/var/log/modified-by-node-installer.log Section


/var/log/node-installer Section


/var/log/rsyncd.log Section


/var/spool/cmd/disks.xml Section


**A.3** **Files Not Generated, But Installed In RHEL And Derivatives**


This appendix (Appendix A) is mainly about generated configuration files. This section (A.3) of the
appendix discusses a class of files that is not generated, but may still be confused with generated files.
The discussion in this section clarifies the issue, and explains how to check if non-generated installed
files differ from the standard distribution installation.
A design goal of BCM is that of minimal interference. That is, to stay out of the way of the distributions that it works with as much as is reasonable. Still, there are inevitably cluster manager configuration
files that are not generated, but installed from a cluster manager package. A cluster manager configuration file of this kind overwrites the distribution configuration file with its own special settings to get the
cluster running, and the file is then not maintained by the node-installer or CMDaemon. Such files are
therefore not listed on any of the tables in this chapter.
Sometimes the cluster file version may differ unexpectedly from the distribution version. To look
into this, the following steps may be followed:


**Is the configuration file a BCM version or a distribution version?** A convenient way to check if a
particular file is a cluster file version is to grep for it in the packages list for the cluster packages. For
example, for nsswitch.conf :


**A.3 Files Not Generated, But Installed In RHEL And Derivatives** **837**


[root@basecm11 ~]# repoquery -l $(repoquery -a | grep -F _cmHEAD) | grep nsswitch.conf$


The inner repoquery displays a list of all the packages. By grepping for the cluster manager version
string, for example _cmHEAD for NVIDIA Base Command Manager 11, the list of cluster manager packages is found. The outer repoquery displays the list of files within each package in the list of cluster
manager packages. By grepping for nsswitch.conf$, any file paths ending in nsswitch.conf in the
cluster manager packages are displayed. The output is:


/cm/conf/etc/nsswitch.conf


Files under /cm/conf are placed by BCM packages when updating the head node. From there they
are copied over during the post-install section of the RPM to where the distribution version configuration files are located by the cluster manager, but only during the initial installation of the cluster. The
distribution version file is overwritten in this way to prevent RPM dependency conflicts of the BCM
version with the distribution version. The configuration files are not copied over from /cm/conf during subsequent reboots after the initial installation. The cm/conf files are however updated when BCM
packages are updated. During such a BCM update, a notification is displayed that new configuration
files are available.
Inverting the cluster manager version string match displays the files not provided by BCM. These
are normally the files provided by the distribution:


[root@basecm11 ~]# repoquery -l $(repoquery -a | grep -F -v _cmHEAD) | grep nsswitch.conf$

...

/usr/share/factory/etc/nsswitch.conf
/usr/share/factory/etc/nsswitch.conf

/etc/authselect/nsswitch.conf

/etc/authselect/user-nsswitch.conf

/usr/share/authselect/default/minimal/nsswitch.conf

/usr/share/authselect/default/sssd/nsswitch.conf

/usr/share/authselect/default/winbind/nsswitch.conf

/var/lib/authselect/nsswitch.conf

/etc/authselect/nsswitch.conf

/etc/authselect/user-nsswitch.conf

/usr/share/authselect/default/minimal/nsswitch.conf

/usr/share/authselect/default/sssd/nsswitch.conf

/usr/share/authselect/default/winbind/nsswitch.conf

/var/lib/authselect/nsswitch.conf

/etc/nsswitch.conf

/etc/nsswitch.conf

/usr/share/authselect/vendor/libnss-mysql/nsswitch.conf

/usr/share/rear/skel/default/etc/nsswitch.conf


**Which package provides the file in BCM and in the distribution?** The packages that provide these
files can be found by running the “ yum whatprovides * ” command on the paths given by the preceding
output, for example:


~# yum whatprovides */cm/conf/etc/nsswitch.conf

...

cm-config-ldap-client< _various types and versions are seen_ 

This reveals that some BCM LDAP packages can provide an nsswitch.conf file. The file is a plain
file provided by the unpacking and placement that takes place when the package is installed. The file is
not generated or maintained periodically after placement, which is the reason why this file is not seen
in the tables of sections A.1 and A.2.3 of this appendix.
Similarly, looking through the output for the less specific case:


**838** **Generated Files**


~# yum whatprovides */etc/nsswitch.conf

...

cm-config-ldap-client*

glibc*

rear*

systemd*


shows that glibc provides a distribution version of the nsswitch.conf file, that the rear package from
the distribution provides a version of it, and that there is also a systemd version of this file available
from the distribution packages. The glob - in the output in this manual represents a variety of types and
versions. The actual display that is seen on the screen is an expansion of the glob.


**Similar Ubuntu queries:** For Ubuntu, a query of the form dpkg -S < _filename_ - shows the packages
that provide a file with the pattern < _filename_ - .


**Example**


root@head:~# dpkg -S "nsswitch.conf"
cm-config-ldap-client-master: /cm/conf/etc/nsswitch.conf
manpages: /usr/share/man/man5/nsswitch.conf.5.gz

libc-bin: /usr/share/libc-bin/nsswitch.conf


To work out which Ubuntu package is a distribution package and which is a BCM package, queries
similar to the following can be run:


**Example**


root@head:~# dpkg-query -W -f='${binary:Package} ${Version}\n' $(dpkg -S "nsswitch.conf" | cut -f1 -d:) |\

grep cm10.0

cm-config-ldap-client-master 10.0-155-cm10.0
root@head:~# dpkg-query -W -f='${binary:Package} ${Version}\n' $(dpkg -S "nsswitch.conf" | cut -f1 -d:) |\

grep -v cm10.0

libc-bin 2.35-0ubuntu3.8

manpages 5.10-1ubuntu1


**What are the differences between the BCM version and the distribution versions of the file?** Sometimes it is helpful to compare a distribution version and cluster version of nsswitch.conf to show the
differences in configuration. The versions of the RPM packages containing the nsswitch.conf can be
downloaded, their contents extracted, and their differences compared as follows:


~# mkdir yumextracted ; cd yumextracted

~# yumdownloader glibc-2.34
~# rpm2cpio glibc-2.34-100.el9_4.4.x86_64.rpm | cpio -idmv

~# yumdownloader cm-config-ldap-client-master
~# rpm2cpio cm-config-ldap-client-master-HEAD-155_cmHEAD.noarch.rpm | cpio -idmv

~# diff etc/nsswitch.conf cm/conf/etc/nsswitch.conf

...


**What are the configuration files in an RPM package?** An RPM package allows files within it to be
marked as configuration files. Files marked as configuration files can be listed with rpm -qc < _package_ - .
Optionally, piping the list through “ sort -u ” filters out duplicates.


**Example**


**A.3 Files Not Generated, But Installed In RHEL And Derivatives** **839**


~# rpm -qc glibc | sort -u
/etc/gai.conf

/etc/ld.so.cache

/etc/ld.so.conf

/etc/nsswitch.conf

/etc/rpc
/usr/lib64/gconv/gconv-modules
/usr/lib/gconv/gconv-modules
/var/cache/ldconfig/aux-cache


**How does an RPM installation deal with local configuration changes? Are there configuration files**
**or critical files that BCM misses?** Whenever an RPM installation detects a file with local changes, it
can treat the local system file as if:


1. the local system file is frozen [1] . The installation does not interfere with the local file, but places the
updated file as an .rpmnew file in the same directory.


2. the local system file is not frozen. The installation changes the local file. It copies the local file to
an .rpmsave file in the same directory, and installs a new file from the RPM package.


When building BCM packages, the package builders can specify which of these two methods apply.
When dealing with the built package, the system administrator can use an rpm query method to determine which of the two methods applies for a particular file in the package. For example, for glibc, the
following query can be used and grepped:


rpm -q --queryformat '[%{FILENAMES}\t%{FILEFLAGS:fflags}\n]' glibc | egrep '[[:space:]].*(c|n).*$' | sort -u
/etc/gai.conf cmng
/etc/ld.so.cache cmng

/etc/ld.so.conf cn

/etc/nsswitch.conf cn

/etc/rpc cn
/usr/lib64/gconv/gconv-modules cn
/usr/lib/gconv/gconv-modules cn
/var/cache/ldconfig/aux-cache cmng


Here, the second column of the output displayed shows which of the files in the package have a
configuration ( c ) flag or a noreplace ( n ) flag. The c flag without the n flag indicates that an .rpmsave file
will be created, while a c flag together with an n flag indicates that an .rpmnew file will be created.
In any case, files that are not marked as configuration files are overwritten during installation.
So:


  - If a file is not marked as a configuration file, and it has been customized by the system administrator, and this file is provided by an RPM package, and the RPM package is updated on the system,
then the file is overwritten silently.


  - If a file is marked as a configuration file, and it has been customized by the system administrator,
and this file is provided by an RPM package, and the RPM package is updated on the system, then
it is good practice to look for .rpmsave and .rpmnew versions of that file, and run a comparison
on detection.


BCM should however mark all critical files as configuration files in BCM packages.
Sometimes, RPM updates can overwrite a particular file that the administrator has changed locally
and then would like to keep frozen.
To confirm that this is the problem, the following should be checked:


1 This freezing should not be confused with the FrozenFile directive (Appendix C), where the file or section of a file is being
maintained by CMDaemon, and where freezing the file prevents CMDaemon from maintaining it.


**840** **Generated Files**


  - The --queryformat option should be used to check that file can indeed be overwritten by updates.
If the file has an n flag (regardless of whether it is a configuration file or not) then overwriting due
to RPM updates does not happen, and the local file remains frozen. If the file has no n flag, then
replacement occurs during RPM updates.


For files with no n flag, but where the administrator would still like to freeze the file during updates, the
following can be considered:


  - The file text content should be checked to see if it is a CMDaemon-maintained file (section 2.6.5),
or checked against the list of generated files (Appendix A). This is just to make sure to avoid
confusion about how changes are occurring in such a file.


**–**
If it is a CMDaemon-maintained file, then configuration changes put in by the administrator will also not persist in the maintained section of the file unless the FrozenFile directive
(section C) is used to freeze the change.


**–**
If it is only a section that CMDaemon maintains, then configuration changes can be placed
outside of the maintained section.


Wherever the changes are placed in such a file, these changes are in any case by default overwritten
on RPM updates if the file has no n flag.


  - Some regular node updates can effectively be maintained in a desired state with the help of a
finalize script (Appendix E).


  - Updates can be excluded from YUM/zypper (section 9.3.2), thereby avoiding the overwriting of
that file by the excluded package.


A request to change the package build flag may be sent to the BCM support team if the preceding
suggested options are unworkable.