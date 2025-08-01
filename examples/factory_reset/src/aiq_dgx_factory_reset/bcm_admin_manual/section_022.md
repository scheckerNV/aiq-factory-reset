# **B**

### **Bright Computing Public Key**

-----BEGIN PGP PUBLIC KEY BLOCK----
Version: GnuPG v1.4.0 (GNU/Linux)


mQGiBEqtYegRBADStdQjn1XxbYorXbFGncF2IcMFiNA7hamARt4w7hjtwZoKGHbC

zSLsQTmgZO+FZs+tXcZa50LjGwhpxT6qhCe8Y7zIh2vwKrKlaAVKj2PUU28vKj1p
2W/OIiG/HKLtahLiCk0L3ahP0evJHh8B7elClrZOTKTBB6qIUbC5vHtjiwCgydm3

THLJsKnwk4qZetluTupldOEEANCzJ1nZxZzN6ZAMkIBrct8GivWClT1nBG4UwjHd
EDcGlREJxpg/OhpEP8TY1e0YUKRWvMqSVChPzkLUTIsd/O4RGTw0PGCo6Q3TLXpM
RVoonYPR1tRymPNZyW8VJeTUEn0kdlCaqZykp1sRb3jFAiJIRCmBRc854i/jRXmo
foTPBACJQyoEH9Qfe3VcqR6+vR2tX9lPvkxS7A5AnJIRs3Sv6yM4oV+7k/HrfYKt

fyl6widtEbQ1870s4x3NYXmmne7lz1nGxBfAxzPG9rtjRSXyVxc+KGVd6gKeCV6d
o7kS/LJHRi0Lb5G4NZRFy5CGqg64liJwp/f2J4uyRbC8b+/LQbQ7QnJpZ2h0IENv

bXB1dGluZyBEZXZlbG9wbWVudCBUZWFtIDxkZXZAYnJpZ2h0Y29tcHV0aW5nLmNv

bT6IXgQTEQIAHgUCSq1h6AIbAwYLCQgHAwIDFQIDAxYCAQIeAQIXgAAKCRDvaS9m

+k3m0JO0AKC0GLTZiqoCQ6TRWW2ijjITEQ8CXACgg3o4oVbrG67VFzHUntcA0YTE
DXW5Ag0ESq1h6xAIAMJiaZI/0EqnrhSfiMsMT3sxz3mZkrQQL82Fob7s+S7nnMl8
A8btPzLlK8NzZytCglrIwPCYG6vfza/nkvyKEPh/f2it941bh7qiu4rBLqr+kGx3

zepSMRqIzW5FpIrUgDZOL9J+tWSSUtPW0YQ5jBBJrgJ8LQy9dK2RhAOLuHfbOSVB
JLIwNKxafkhMRwDoUNS4BiZKWyPFu47vd8fM67IPT1nMl0iCOR/QBn29MYuWnBcw
61344pd/IjOu3gM6YBqmRRU6yBeVi0TxxbYYnWcts6tEGAlTjHUOQ7gxVp4RDia2
jLVtbee8H464wxkkC3SSkng216RaBBAoaAykhzcAAwUH/iG4WsJHFw3+CRhUqy51

jnmb1FTFO8KQXI8JlPXM0h6vv0PtP5rw5D5V2cyVe2i4ez9Y8XMVfcbf60lptKyY

bRUjQq+9SNjt12ESU67YyLstSN68ach9Af03PoSZIKkiNwfA0+VBILv2Mhn7xd74
5L0M/eJ7lHSpeJA2Rzs6szc234Ob/VxGfGWjogaK3NElSYOzQo+/k0VMdMWsQm/8
Ras19IA9P5jlSbcZQlHlPjndS4x4XQ8P41ATczsIDyWhsJC51rTuw9/QO7fqvvPn

xsRz1pFmiiN7I4JLjw0nAlXexn4EaeVa7Eb+uTjvxJZNdShs7Td74OmlF7RKFccI
wLuISQQYEQIACQUCSq1h6wIbDAAKCRDvaS9m+k3m0C/oAJsHMmKrLPhjCdZyHbB1

e19+5JABUwCfU0PoawBN0HzDnfr3MLaTgCwjsEE=

=WJX7

-----END PGP PUBLIC KEY BLOCK----

# **C**

### **CMDaemon Configuration File** **Directives**

This appendix lists all configuration file directives that may be used in the cluster management daemon
configuration file. If a change is needed, then the directives are normally changed on the head node, or
on both head nodes in the high availability configuration, in:


/cm/local/apps/cmd/etc/cmd.conf


The directives can also be set in some cases for the regular nodes, via the software image in /cm/
images/default-image/cm/local/apps/cmd/etc/cmd.conf on the head node. Changing the defaults
already there is however not usually needed, and is not recommended.
Only one directive is valid per cmd.conf file.
To activate changes in a cmd.conf configuration file, the cmd service associated with it must be
restarted.


  - For the head node this is normally done with the command:


systemctl restart cmd


  - For regular nodes, cmd running on the nodes is restarted. Often, the image should be updated
before cmd is restarted. How to carry out these procedures for a directive is described with an
example where the FrozenFile directive is activated on a regular node on page 857.


**Master directive**


**Syntax:** Master = _hostname_
**Default:** Master = master


The cluster management daemon treats the host specified in the Master directive as the head node. A
cluster management daemon running on a node specified as the head node starts in _head_ mode. On a
regular node, it starts in _node_ mode.


**Port directive**


**Syntax:** Port = _number_
**Default:** Port = 8080


The _number_ used in the syntax above is a number between 0 and 65535. The default value is 8080.
The Port directive sets the value of the port of the cluster management daemon to listen for nonSSL HTTP calls. By default, this happens only during init. All other communication with the cluster


**844** **CMDaemon Configuration File Directives**


[management daemon is carried out over the SSL port. Pre-init port adjustment can be carried out in](http://kb.brightcomputing.com/faq/index.php?action=artikel&cat=2&id=155)
[the node-installer.conf configuration. Shorewall may need to be modified to allow traffic through for a](http://kb.brightcomputing.com/faq/index.php?action=artikel&cat=2&id=155)
[changed port.](http://kb.brightcomputing.com/faq/index.php?action=artikel&cat=2&id=155)


**SSLPort directive**


**Syntax:** SSLPort = _number_
**Default:** SSLPort = 8081


The _number_ used in the syntax above is a number between 0 and 65535. The default value is 8081.
The SSLPort directive sets the value of the SSL port of the cluster management daemon to listen for
SSL HTTP calls. By default, it is used for all communication of CMDaemon with Base View and cmsh,
except for when CMDaemon is started up from init.
This directive does not change the firewall port settings to match the value of the SSL port for CMDaemon communication. The firewall port settings value does however change if using the cm-cmd-ports
utility (page 73 of the _Installation Manual_ ) instead.


**SSLPortOnly directive**


**Syntax:** SSLPortOnly = yes | no
**Default:** SSLPortOnly = no


The SSLPortOnly directive allows the non-SSL port to be disabled. By default, during normal running,
both SSL and non-SSL ports are listening, but only the SSL port is used. Also by default, the non-SSL
port is only used during CMDaemon start up.
If bootloaderprotocol (section 5.1.6) is set to HTTP, then SSLPortOnly must be set to no . The HTTPS
protocol is unsupported by most bootloaders.


**CertificateFile directive**


**Syntax:** CertificateFile = _filename_
**Default:** CertificateFile = "/cm/local/apps/cmd/etc/cert.pem"


The CertificateFile directive specifies the PEM-format certificate which is to be used for authentication purposes. On the head node, the certificate used also serves as a software license.


**PrivateKeyFile directive**


**Syntax:** PrivateKeyFile = _filename_
**Default:** PrivateKeyFile = "/cm/local/apps/cmd/etc/cert.key"


The PrivateKeyFile directive specifies the PEM-format private key which corresponds to the certificate
that is being used.


**CACertificateFile directive**


**Syntax:** CACertificateFile = _filename_
**Default:** CACertificateFile = "/cm/local/apps/cmd/etc/cacert.pem"


The CACertificateFile directive specifies the path to the BCM PEM-format root certificate. It is normally not necessary to change the root certificate.


**845**


**ClusterCertificateFile directive**


**Syntax:** ClusterCertificateFile = _filename_
**Default:** ClusterCertificateFile = "/cm/local/apps/cmd/etc/cluster.pem"


The ClusterCertificateFile directive specifies the path to the BCM PEM-format cluster certificate file
used as a software license, and to sign all client certificates


**ClusterPrivateKeyFile directive**


**Syntax:** ClusterPrivateKeyFile = _filename_
**Default:** ClusterPrivateKeyFile = "/cm/local/apps/cmd/etc/cluster.key"


The ClusterPrivateKeyFile directive specifies the path to the BCM PEM-format private key which
corresponds to the cluster certificate file.


**RandomSeedFile directive**


**Syntax:** RandomSeedFile = _filename_
**Default:** RandomSeedFile = "/dev/urandom"


The RandomSeedFile directive specifies the path to a source of randomness for a random seed.


**RandomSeedFileSize directive**


**Syntax:** RandomSeedFileSize = _number_
**Default:** RandomSeedFileSize = 8192


The RandomSeedFileSize directive specifies the size of the random seed.


**DHParamFile directive**


**Syntax:** DHParamFile = _filename_
**Default:** DHParamFile = "/cm/local/apps/cmd/etc/dh1024.pem"


The DHParamFile directive specifies the path to the Diffie-Hellman parameters.


**SSLHandshakeTimeout directive**


**Syntax:** SSLHandshakeTimeout = _number_
**Default:** SSLHandshakeTimeout = 10


The SSLHandShakeTimeout directive controls the time-out period (in seconds) for SSL handshakes.


**SSLSessionCacheExpirationTime directive**


**Syntax:** SSLSessionCacheExpirationTime = _number_
**Default:** SSLSessionCacheExpirationTime = 300


The SSLSessionCacheExpirationTime directive controls the period (in seconds) for which SSL sessions
are cached. Specifying the value 0 can be used to disable SSL session caching.


**846** **CMDaemon Configuration File Directives**


**DBHost directive**


**Syntax:** DBHost = _hostname_
**Default:** DBHost = "localhost"


The DBHost directive specifies the hostname of the MySQL database server.


**DBPort directive**


**Syntax:** DBPort = _number_
**Default:** DBHost = 3306


The DBPort directive specifies the TCP port of the MySQL database server.


**DBUser directive**


**Syntax:** DBUser = _username_
**Default:** DBUser = cmdaemon


The DBUser directive specifies the username used to connect to the MySQL database server.


**DBPass directive**


**Syntax:** DBPass = _password_
**Default:** DBPass = "<random string set during installation> "


The DBPass directive specifies the password used to connect to the MySQL database server.


**DBName directive**


**Syntax:** DBName = _database_
**Default:** DBName = "cmdaemon"


The DBName directive specifies the database used on the MySQL database server to store CMDaemon
related configuration and status information.


**DBUnixSocket directive**


**Syntax:** DBUnixSocket = _filename_
**Default:** DBUnixSocket = "/var/lib/mysql/mysql.sock"


The DBUnixSocket directive specifies the named pipe used to connect to the MySQL database server if
it is running on the same machine.


**DBUpdateFile directive**


**Syntax:** DBUpdateFile = _filename_
**Default:** DBUpdateFile = "/cm/local/apps/cmd/etc/cmdaemon_upgrade.sql"


The DBUpdateFile directive specifies the path to the file that contains information on how to upgrade
the database from one revision to another.


**847**


**EventBucket directive**


**Syntax:** EventBucket = _filename_
**Default:** EventBucket = "/var/spool/cmd/eventbucket"


The EventBucket directive (section 10.10.3) specifies the path to the named pipe that is created to listen
for incoming events from a user.


**EventBucketFilter directive**


**Syntax:** EventBucketFilter = _filename_
**Default:** EventBucketFilter = "/cm/local/apps/cmd/etc/eventbucket.filter"


The EventBucketFilter directive (section 10.10.3) specifies the path to the file that contains regular
expressions used to filter out incoming messages on the event-bucket.


**LDAPHost directive**


**Syntax:** LDAPHost = _hostname_
**Default:** LDAPHost = "localhost"


The LDAPHost directive specifies the hostname of the LDAP server to connect to for user management.


**LDAPUser directive**


**Syntax:** LDAPUser = _username_
**Default:** LDAPUser = "root"


The LDAPUser directive specifies the username used when connecting to the LDAP server.


**LDAPPass directive**


**Syntax:** LDAPPass = _password_
**Default:** LDAPPass = "<random string set during installation>"


The LDAPPass directive specifies the password used when connecting to the LDAP server. It can be
changed following the procedure described in Appendix I.


**LDAPReadOnlyUser directive**


**Syntax:** LDAPReadOnlyUser = _username_
**Default:** LDAPReadOnlyUser = "readonlyroot"


The LDAPReadOnlyUser directive specifies the username that will be used when connecting to the LDAP
server during LDAP replication. The user is a member of the "rogroup" group, whose members have a
read-only access to the whole LDAP directory.


**LDAPReadOnlyPass directive**


**Syntax:** LDAPReadOnlyPass = _password_
**Default:** LDAPReadOnlyPass = "<random string set during installation>"


The LDAPReadOnlyPass directive specifies the password that will be used when connecting to the LDAP
server during LDAP replication.


**848** **CMDaemon Configuration File Directives**


**LDAPSearchDN directive**


**Syntax:** LDAPSearchDN = _dn_
**Default:** LDAPSearchDN = "dc=cm,dc=cluster"


The LDAPSearchDN directive specifies the Distinguished Name (DN) used when querying the LDAP

server.


**LDAPProtocol directive**


**Syntax:** LDAPProtocol = ldap|ldaps
**Default:** LDAPProtocol = "ldaps"


The LDAPProtocol directive specifies the LDAP protocol to be used when querying the LDAP server.


**LDAPPort directive**


**Syntax:** LDAPPort = _number_
**Default:** LDAPPort = 636


The LDAPPort directive specifies the port to be used when querying the LDAP server.


**LDAPCACertificate directive**


**Syntax:** LDAPCACertificate = _filename_
**Default:** LDAPCACertificate = "/cm/local/apps/openldap/etc/certs/ca.pem"


The LDAPCACertificate directive specifies the CA certificate to be used when querying the LDAP

server.


**LDAPCertificate directive**


**Syntax:** LDAPCertificate = _filename_
**Default:** LDAPCertificate = "/cm/local/apps/openldap/etc/certs/ldap.pem"


The LDAPCertificate directive specifies the LDAP certificate to be used when querying the LDAP

server.


**LDAPPrivateKey directive**


**Syntax:** LDAPPrivateKey= _filename_
**Default:** LDAPPrivateKey= "/cm/local/apps/openldap/etc/certs/ldap.key"


The LDAPPrivateKey directive specifies the LDAP key to be used when querying the LDAP server.


**HomeRoot directive**


**Syntax:** HomeRoot = _path_
**Default:** HomeRoot = "/home"


The HomeRoot directive specifies the default user home directory used by CMDaemon. It is used for
automatic mounts, exports, and when creating new users.


**849**


**DocumentRoot directive**


**Syntax:** DocumentRoot = _path_
**Default:** DocumentRoot = "/cm/local/apps/cmd/etc/htdocs"


The DocumentRoot directive specifies the directory mapped to the web-root of the CMDaemon. The
CMDaemon acts as a HTTP-server, and can therefore in principle also be accessed by web-browsers.


**SpoolDir directive**


**Syntax:** SpoolDir = _path_
**Default:** SpoolDir = "/var/spool/cmd"


The SpoolDir directive specifies the directory which is used by the CMDaemon to store temporary and
semi-temporary files.


**EnableShellService directive**


**Syntax:** EnableShellService = true | false
**Default:** EnableShellService = true


The EnableShellService directive allows shells to be started from Base View.

The connection runs over CMDaemon, which is running over SSL, which means that between Base
View and the device, the connection is encrypted.
The directive does not affect cmsh ’s rshell, rconsole telnet, and ssh commands.


**DisableRemoteShell directive**


**Syntax:** AdvancedConfig = {"DisableRemoteShell=0|1", ...}
**Default:** DisableRemoteShell=0

DisableRemoteShell is a parameter of the AdvancedConfig (page 862) directive.
By default CMDaemon provides access to devices via rshell, rconsole (SOL), telnet, and ssh .
Setting the directive to 1 disables all RPC shell access.
A more fine-grained disabling is possible with the following AdvancedConfig directives, which follow the same syntax:


 - **DisableRemoteRShell directive** : disables a remote shell to the head node.


 - **DisableRemoteRShellImage directive** : disables a remote shell to the chrooted software image.


 - **DisableRemoteRShellNode directive** : disables a remote shell to the regular nodes.


 - **DisableRemoteRShellTelnet directive** : disables a telnet shell to a device.


 - **DisableRemoteRShellSSH directive** : disables SSH to a device.


 - **DisableRemoteSOL directive** : disables a console via SOL to a device.


**EnableWebSocketService directive**


**Syntax:** EnableWebSocketService = true | false
**Default:** EnableWebSocketService = true


The EnableWebSocketService directive allows the use of CMDaemon Lite (section 2.6.7).


**850** **CMDaemon Configuration File Directives**


**EnablePrometheusMetricService directive**


**Syntax:** EnablePrometheusMetricService = true | false
**Default:** EnablePrometheusMetricService = true


If true, the EnablePrometheusMetricService directive creates an HTTP endpoint for Prometheus-style
exporters that do not have their own HTTP endpoint.


**PrometheusMetricServicePath directive**


**Syntax:** PrometheusMetricServicePath = _path_
**Default:** PrometheusMetricServicePath = SCRIPTS_DIR"metrics/prometheus"


The PrometheusMetricServicePath directive is the path from which CMDaemon can serve Prometheus
metrics. SCRIPTS_DIR is the stem path /cm/local/apps/cmd/scripts by default.


**EnablePrometheusExporterService directive**


**Syntax:** EnablePrometheusExporterService = true | false
**Default:** EnablePrometheusExporterService = false


If true, the EnablePrometheusExporterService directive allows a Prometheus server to pull data from
CMDaemon.

To collect all data, the external Prometheus YAML configuration ( [https://prometheus.io/docs/](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
[prometheus/latest/configuration/configuration/](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) ) should have all nodes with a monitoring role
added to it:


**Example**


#

# - job_name: cmdaemon-head01
# metrics_path: /exporter

# static_configs:
# - targets: ['https://head01:8081']

#


Configuring CMDaemon to sample metrics from a Prometheus exporter instead is covered in section 3.17.


**PrometheusExporterRequireCertificate directive**


**Syntax:** AdvancedConfig = {"PrometheusExporterRequireCertificate=0|1", ...}
**Default:** PrometheusExporterRequireCertificate = 1


PrometheusExporterRequireCertificate is a parameter of the AdvancedConfig (page 862) directive.


  - If set to 0, then all users can use the Prometheus service to pull data using CMDaemon.


  - If set to 1, then only users using certificate-based access can use the Prometheus service to pull
data using CMDaemon.


Certificate-based access can be configured as follows:
A custom profile with the name prometheus can be created for BCM users with profile mode (section 6.4) as follows:


**851**


[basecm11->profile]% add prometheus

[basecm11->profile*[prometheus*]]% append tokens PROMETHEUS_EXPORTER_TOKEN

[basecm11->profile*[prometheus*]]% set nonuser yes

[basecm11->profile*[prometheus*]]% commit


A 2048-bit SSL certificate called myprommcert can be created for a non-privileged user prometheus
with 3650 days validity using the createcertificate command (section 6.4.2) as follows:


[basecm11->profile[prometheus]]% cert

[basecm11->cert]% createcertificate 2048 mypromcert "" "" "" "" "" prometheus "" 3650 /tmp/prometheus.key _\_
/tmp/prometheus.pem
Certificate key written to file: /tmp/prometheus.key
Certificate pem written to file: /tmp/prometheus.pem


The PEM certificate is the public part of the key pair. The private key must be owned and be readable
by the Prometheus instance that is scraping from the node exporter.
To configure SSL authentication between Prometheus server and the Prometheus exporter node:


  - On the Prometheus server:


**–** A directive value of:


        - [0] [ means that the session key is a temporary key that is auto-generated for any user]


        - [1] [ means that the user (the Prometheus server) must provide a certificate]


**–**
CMDaemon in a default cluster manager installation uses a self-signed certificate. A copy of
certificate can be picked up on the head node with:


**Example**


[root@basecm11 ~]# ca_cert="/etc/prometheus/cmdaemon-$(hostname)-ca.pem"

[root@basecm11 ~]# cat /cm/local/apps/cmd/etc/{cacert,cluster}.pem > ${ca_cert}

[root@basecm11 ~]# chmod 600 ${ca_cert}


The Prometheus server should be configured to specify this CA certificate.

If the certificate used by CMDaemon is not a self-signed certificate—that is to say, it is signed
by a recognized CA—then the certificate issued by CMDaemon is legitimate, and the Prometheus
server does not need to have that CA certificate explicitly specified.


  - The Prometheus exporter always uses TLS, which is automatically managed by CMDaemon.


**EnablePrometheusPushService directive**


**Syntax:** EnablePrometheusPushService = true | false
**Default:** EnablePrometheusPushService = false


If true, the EnablePrometheusPushService directive allows a Prometheus server to push data to CMDaemon:


**Example**


myhead # cat <<EOF > "$file"
myhead # test_prometheus_push{hello="world"} 42

myhead # EOF
myhead # curl -k -X POST --data-binary "@$file" https://localhost:8081/prometheuspush/job/test


**852** **CMDaemon Configuration File Directives**


**CMDaemonAudit directive**


**Syntax:** CMDaemonAudit = yes | no
**Default:** CMDaemonAudit = no


When the CMDaemonAudit directive is set to yes, and a value is set for the CMDaemon auditor file with
the CMDaemonAuditorFile directive, then CMDaemon actions are time-stamped and logged in the CMDaemon auditor file.


**CMDaemonAuditorFile directive**


**Syntax:** CMDaemonAuditorFile = _path to_ audit.log _file_

or

**Syntax:** CMDaemonAuditorFile = _path to_ audit.json _file_

or

**Syntax:** CMDaemonAuditorFile = _http(s) path to JSON server_


**Default:** CMDaemonAuditorFile = "/var/spool/cmd/audit.log"


The CMDaemonAuditorFile directive sets where the audit logs for CMDaemon actions are logged. The
log format for a .log file in a standard directory path is:
( _time stamp_ ) _profile_ [ _IP-address_ ] _action_ ( _unique key_ )


**Example**


(Mon Jan 31 12:41:37 2011) Administrator [127.0.0.1] added Profile: arbitprof(4294967301)


The directive can be set in the following kinds of formats:


 - CMDaemonAuditorFile = "/var/spool/cmd/audit.log"


 - CMDaemonAuditorFile = "/var/spool/cmd/audit.json"


 - CMDaemonAuditorFile = "http://< _IP address_ >:< _port_ >/ _some_ / _path_ "


 - CMDaemonAuditorFile = "https://< _IP address_ >:< _port_ >/ _some_ / _path_ "


A simple POST web service can be faked using netcat :


**Example**


nc -l 1234 -k


The JSON file always contains a valid array. An RPC call looks like this:


**Example**


...


"entity": "node001",

"rpc":

"address": "127.0.0.1",

"call": "updateDevice",

"service": "cmdevice",

"timestamp": 1579185696,

"user": "Administrator.root"

,

"task_id": 0,

"updated": true

,

...


**853**


**DisableAuditorForProfiles directive**


**Syntax:** DisableAuditorForProfiles = {profile [, profile] ...}
**Default:** DisableAuditorForProfiles = {NODE}


The DisableAuditorForProfiles directive sets the profile for which an audit log for CMDaemon actions is disabled. A profile (section 2.3.4) defines the services that CMDaemon provides for that profile
user. More than one profile can be set as a comma-separated list. Out of the profiles that are available on
a newly-installed system: node, admin, cmhealth, and readonly ; only the profile node is enabled by default. New profiles can also be created via the profile mode of cmsh or via the navigation path Identity
Management - Profiles - of Base View, thus making it possible to disable auditing for arbitrary groups
of CMDaemon services.


**EventLogger directive**


**Syntax:** EventLogger = true | false
**Default:** EventLogger = true


The EventLogger directive sets whether to log events. If active, then by default it logs events to /var/
spool/cmd/events.log on the active head. If a failover takes place, then the event logs on both heads
should be checked and merged for a complete list of events.
The location of the event log on the filesystem can be changed using the EventLoggerFile directive
(page 853).
Whether events are logged in files or not, events are cached and accessible using cmsh or Base
View. The number of events cached by CMDaemon is determined by the parameter MaxEventHistory
(page 853).


**EventLoggerFile directive**


**Syntax:** EventLoggerFile = _filename_
**Default:** EventLogger = "/var/spool/cmd/events.log"


The EventLogger directive sets where the events seen in the event viewer (section 10.10) are logged.


**MaxEventHistory directive**


**Syntax:** AdvancedConfig = {"MaxEventHistory= _number_ ", ...}
**Default:** MaxEventHistory=8192
MaxEventHistory is a parameter of the AdvancedConfig (page 862) directive.
By default, when not explicitly set, the maximum number of events that is retained by CMDaemon
is 8192. Older events are discarded.

The parameter can take a value from 0 to 1000000. However, CMDaemon is less responsive with
larger values, so in that case, setting the EventLogger directive (page 853) to true, to activate logging to
a file, is advised instead.


**TimingOverview directive**


**Syntax:** TimingOverview = _filename_
**Default:** TimingOverview = true | false


If set to true, the TimingOverview directive records timing information for CMDaemon.


**854** **CMDaemon Configuration File Directives**


**TimingOverviewFile directive**


**Syntax:** TimingOverviewFile = _filename_
**Default:** TimingOverviewFile = "/var/spool/cmd/timing.overview.log"


The TimingOverviewFile directive sets the file where the timing data values for CMDaemon go.


**PublicDNS directive**


**Syntax:** PublicDNS = true | false
**Default:** PublicDNS = false


By default, internal hosts are resolved only if requests are from the internal network. Setting PublicDNS
to true allows the head node name server to resolve internal network hosts for any network, including
networks that are on other interfaces on the head node. Separate from this directive, port 53/UDP must
also be opened up in Shorewall (section 7.2 of the _Installation Manual_ ) if DNS is to be provided for queries
from an external network.


**MaximalSearchDomains directive**


**Syntax:** GlobalConfig = {"MaximalSearchDomains = _number_ ", ...}
**Default:** _none_


The MaximalSearchDomains directive is a parameter of the GlobalConfig (page 863) directive.
By default, the number of names that can be set as search domains used by the cluster has a maximum limit of 6. This is a hardcoded limit imposed by the Linux operating system in older versions.
More recent versions of glibc (glibc > 2.17-222.el7 in RHEL7) no longer set a limit. However using more than 6 search domains currently requires the use of the GlobalConfig directive,
MaximalSearchDomains . For example, to set 30 domains, the directive setting would be: GlobalConfig
= { "MaximalSearchDomains=30" }


**LockDownDhcpd directive**


**Syntax:** LockDownDhcpd = true | false
**Default:** LockDownDhcpd = false


LockDownDhcpd is a deprecated legacy directive. If set to true, a global DHCP “deny unknown-clients”
option is set. This means no new DHCP leases are granted to unknown clients for all networks. Unknown clients are nodes for which BCM has no MAC addresses associated with the node. The directive

LockDownDhcpd is deprecated because its globality affects clients on all networks managed by BCM,
which is contrary to the general principle of segregating the network activity of networks.
The recommended way now to deny letting new nodes boot up is to set the option for specific
networks by using cmsh or Base View (section 3.2.1: figure 3.5 and table 3.1). Setting the cmd.conf
LockDownDhcpd directive overrides lockdowndhcpd values set by cmsh or Base View.


**MaxNumberOfProvisioningThreads directive**


**Syntax:** MaxNumberOfProvisioningThreads = _number_
**Default:** MaxNumberOfProvisioningThreads = 10000


The MaxNumberOfProvisioningThreads directive specifies the cluster-wide total number of nodes that
can be provisioned simultaneously. Individual provisioning servers typically define a much lower
bound on the number of nodes that may be provisioned simultaneously.


**855**


**SetupBMC directive**


**Syntax:** SetupBMC = true | false
**Default:** SetupBMC = true


Automatically configure the username and password for the BMC interface of the head node. This may
also be valid for regular nodes. The SetupBMC directive should not be confused with the setupBmc field
of the node-installer configuration file, described in section 5.8.7.
The node-installer normally takes care of BMC interface configuration on regular nodes by acting on
the node-installer configuration file field setupBmc . The CMDaemon directive SetupBMC can only work
on regular nodes if the node-installer is not configuring the regular nodes. If the boolean parameters
installbootrecord and allownetworkingrestart for a regular node are set to yes, then the SetupBMC
directive is able to work for that regular node. Setting the boolean parameters at category level also
makes the directive work for the associated nodes.


**BMCSessionTimeout directive**


**Syntax:** BMCSessionTimeout = _number_
**Default:** BMCSessionTimeout = 2000


The BMCSessionTimeout specifies the time-out for BMC calls in milliseconds.


**BMCIdentifyScript directive**


**Syntax:** AdvancedConfig = {"BMCIdentify= _filename_ ", ...}
**Default:** _unset_

BMCIdentifyScript is a parameter of the AdvancedConfig (page 862) directive.
The parameter takes a full file path to a script that can be used for identification with a BMC (section 3.7.4).


**BMCIdentifyScriptTimeout directive**


**Syntax:** AdvancedConfig = {"BMCIdentifyScriptTimeout= _number from 1 to 360_ ", ...}
**Default:** 60

BMCIdentifyScriptTimeout is a parameter of the AdvancedConfig (page 862) directive.
CMDaemon waits at the most BMCIdentifyScriptTimeout seconds for the script used by the
BMCIdentify directive to complete.


**BMCIdentifyCache directive**


**Syntax:** AdvancedConfig = {"BMCIdentifyCache=0|1", ...}
**Default:** 1

BMCIdentifyCache is a parameter of the AdvancedConfig (page 862) directive.
If set to 1, then CMDaemon remembers the last value of the output of the script used by the
BMCIdentify directive.


**SnmpSessionTimeout directive**


**Syntax:** SnmpSessionTimeout = _number_
**Default:** SnmpSessionTimeout = 500000


The SnmpSessionTimeout specifies the time-out for SNMP calls in microseconds.


**856** **CMDaemon Configuration File Directives**


**PowerOffPDUOutlet directive**


**Syntax:** PowerOffPDUOutlet = true | false
**Default:** PowerOffPDUOutlet = false


Enabling the PowerOffPDUOutlet directive allows PDU ports to be powered off for clusters that have
both PDU and IPMI power control. Section 4.1.3 has more on this.


**PowerThreadPoolSize directive**


**Syntax:** AdvancedConfig = {"PowerThreadPoolSize=< _integer_ >", ...}
**Default:** PowerThreadPoolSize=32


PowerThreadPoolSize is a parameter of the AdvancedConfig (page 862) directive.
The parameter can take positive integer values. Increasing its value increases the number of threads
that are used to power up the nodes in a cluster (section 4.2.3), so that the cluster is fully operational
quicker. The administrator should however take into account the power surge due to increasing the
number of threads (number of subprocesses ) before increasing the value beyond its default.


**DisableBootLogo directive**


**Syntax:** DisableBootLogo = true | false
**Default:** DisableBootLogo = false


When DisableBootLogo is set to true, the BCM logo is not displayed on the first boot menu when nodes
PXE boot.


**StoreBIOSTimeInUTC directive**


**Syntax:** StoreBIOSTimeInUTC = true | false
**Default:** StoreBIOSTimeInUTC = false


When StoreBIOSTimeInUTC is set to true, the system relies on the time being stored in BIOS as being
UTC rather than local time.


**FreezeChangesTo<** _**wlm**_ **>Config directives:**
**FreezeChangesToPBSPro directive**
**FreezeChangesToSlurmConfig directive**
**FreezeChangesToLSFConfig directive**


**Syntax:** FreezeChangesTo< _wlm_ >Config= true | false
**Default:** FreezeChangesTo< _wlm_ >Config = false


When FreezeChangesTo< _wlm_ >Config is set to true, the CMDaemon running on that node does not
make any modifications to the workload manager configuration for that node. Workload managers for
which this value can be set are:


  - PBSPro


  - Slurm


 - LSF


Monitoring of jobs, and workload accounting and reporting continues for frozen workload man
agers.


**857**


Upgrades to newer workload manager versions may still require some manual adjustments of the
configuration file, typically if a newer version of the workload manager configuration changes the syntax of one of the options in the file.


**FrozenFile directive**


**Syntax:** FrozenFile = { _filename_ [, _filename_ ]... }
**Example:** FrozenFile = { "/etc/dhcpd.conf", "/etc/postfix/main.cf" }
The FrozenFile directive is used to prevent the CMDaemon-maintained sections of configuration files
from being automatically generated. This is useful when site-specific modifications to configuration files
have to be made.

To avoid problems, the file that is frozen should not be a symlink, but should be the ultimate destination file. The readlink -f < _symlinkname_ - command returns the ultimate destination file of a symlink
called < _symlinkname_ - . This is also the case for an ultimate destination file that is reached via several
chained symlinks.


**FrozenFile directive for regular nodes**

**FrozenFile directive for regular nodes for CMDaemon**
The FrozenFile directive can be used within the cmd.conf file of the regular node.


**Example**


To freeze the file /etc/named.conf on the regular nodes running with the image default-image, the file:


/cm/images/default-image/cm/local/apps/cmd/etc/cmd.conf


can have the following directive set in it:


FrozenFile = { "/etc/named.conf" }


The path of the file that is to be frozen on the regular node must be specified relative to the root of
the regular node.
The running node should then have its image updated. This can be done with the imageupdate
command in cmsh (section 5.6.2), or the Update node button in Base View (section 5.6.3). After the
update, CMDaemon should be restarted within that category of nodes:


**Example**


[root@basecm11 ~]# pdsh -v -g category=default systemctl restart cmd
node002: Waiting for CMDaemon (25129) to terminate...
node001: Waiting for CMDaemon (19645) to terminate...

node002: [ OK ]

node001: [ OK ]

node002: Waiting for CMDaemon to start...[ OK ]
node001: Waiting for CMDaemon to start...[ OK ]


**FrozenFile regex specification**
The FrozenFile directive allows regexes to be used for a path, if the path begins with the | character:


**Example**


[root@head current]# egrep -e '^FrozenFile' /cm/local/apps/cmd/etc/cmd.conf
FrozenFile = { "/etc/postfix/main.cf", "|/cm/images/.*?/etc/postfix/main.cf" }


In the preceding entry, all image directories under /cm/images/ are matched for the path
etc/postfix/main.cf .


**858** **CMDaemon Configuration File Directives**


**FrozenFile directive for regular nodes for the node-installer**
CMDaemon directives only affect files on a regular node after CMDaemon starts up on the node during
the init stage. So files frozen by the CMDaemon directive stay unchanged by CMDaemon after this
stage, but they may still be changed before this stage.
Freezing files so that they also stay unchanged during the pre-init stage—that is during the nodeinstaller stage—is possible with node-installer directives.
Node-installer freezing is independent of CMDaemon freezing, which means that if a file freeze is
needed for the entire startup process as well as beyond, then both a node-installer as well as a CMDaemon freeze are sometimes needed.

Node-installer freezes can be done with the node-installer directives in /cm/node-installer/

scripts/node-installer.conf, introduced in section 5.4:


 - frozenFilesPerNode


 - frozenFilesPerCategory


For the node-installer.conf file in multidistro and multiarch (section 9.7) configurations, the directory
path /cm/node-installer takes the form:
/cm/node-installer- _<distribution>-<architecture>_
The values for _<distribution>_ and _<architecture>_ can take the values outlined on page 528.


**Example**


Per node:


frozenFilesPerNode = "*:/localdisk/etc/ntp.conf", "node003:/localdisk/etc/hosts"


Here, the  - wildcard means that no restriction is set. Setting node003 means that only node003 is
frozen.


**Example**


Per category:


frozenFilesPerCategory = "mycategory:/localdisk/etc/sysconfig/network-scripts/ifcfg-eth1"


Here, the nodes in the category mycategory are prevented from being changed by the node-installer.


**The Necessity Of A** FrozenFile **Directive**
In a configuration file after a node is fully up, the effect of a statement earlier on can often be overridden
by a statement later in the file. So, the following useful behavior is independent of whether FrozenFile
is being used for a configuration file or not: A configuration file, for example /etc/postfix/main.cf,
with a configuration statement in an earlier CMDaemon-maintained part of the file, for example:


mydomain = eth.cluster


can often be overridden by a statement later on outside the CMDaemon-maintained part of the file:


mydomain = eth.gig.cluster


Using FrozenFile in CMDaemon or the node-installer can thus sometimes be avoided by the use of
such overriding statements later on.
Whether overriding later on is possible depends on the software being configured. It is true for Postfix configuration files, for example, but it may not be so for the configuration files of other applications.


**859**


**EaseNetworkValidation directive**


**Syntax:** EaseNetworkValidation = 0 | 1 | 2
**Default:** EaseNetworkValidation = 0


CMDaemon enforces certain requirements on network interfaces and management/node-booting networks by default. In heavily customized setups, such as is common in Type 3 networks (section 3.3.9 of
the _Installation Manual_ ), the user may wish to disable these requirements.


 - 0 enforces all requirements.


 - 1 allows violation of the requirements, with validation warnings. This value should never be set
except under instructions from BCM support.


 - 2 allows violation of the requirements, without validation warnings. This value should never be
set except under instructions from BCM support.


**CustomUpdateConfigFileScript directive**


**Syntax:** CustomUpdateConfigFileScript = _filename_
**Default:** _commented out in the default_ cmd.conf _file_


Whenever one or more entities have changed, the custom script at _filename_, specified by a full path, is
called 30s later. Python bindings can be used to get information on the current setup.


**ConfigDumpPath directive**


**Syntax:** ConfigDumpPath = _filename_
**Default:** ConfigDumpPath = /var/spool/cmd/cmdaemon.config.dump


The ConfigDumpPath directive sets a dump file for dumping the configuration used by the power control
script /cm/local/apps/cmd/scripts/pctl/pctl . The pctl script is a fallback script to allow power
operations if CMDaemon is not running.


  - If no directive is set ( ConfigDumpPath = "" ), then no dump is done.


  - If a directive is set, then the administrator must match the variable cmdconfigfile in the
powercontrol configuration file /cm/local/apps/cmd/scripts/pctl/config.py to the value of
ConfigDumpPath . By default, the value of cmdconfigfile is set to /var/spool/cmd/cmdaemon.
config.dump .


**SyslogHost directive**


**Syntax:** SyslogHost = _hostname_
**Default:** SyslogHost = "localhost"


The SyslogHost directive specifies the hostname of the syslog host.


**SyslogFacility directive**


**Syntax:** SyslogFacility = _facility_
**Default:** SyslogFacility = "LOG_LOCAL6"


The default value of LOG_LOCAL6 is set in:


 - /etc/rsyslog.conf in RHEL, Ubuntu.


**860** **CMDaemon Configuration File Directives**


 - /etc/syslog-ng/syslog-ng.conf in SLES versions


These are the configuration files for the default syslog daemons syslog, rsyslog, and syslog-ng,
respectively, that come with the distribution. BCM redirects messages from CMDaemon to
/var/log/cmdaemon only for the default syslog daemon that the distribution provides. So, if another
syslog daemon other than the default is used, then the administrator has to configure the non-default
syslog daemon facilities manually.
The value of _facility_ must be one of: LOG_KERN, LOG_USER, LOG_MAIL, LOG_DAEMON, LOG_AUTH,

LOG_SYSLOG or LOG_LOCAL0..7


**NameServerLocalhostLocation directive**


**Syntax:** AdvancedConfig = {"NameServerLocalhostLocation=0|1", ...}
**Default:** NameServerLocalhostLocation=0


NameServerLocalhostLocation is a parameter of the AdvancedConfig (page 862) directive.
When set to 1, the location of the localhost as specified by the nameserver directive in
/etc/resolv.conf is moved to the bottom of the list of nameserver entries. The default value of 0
places it at the top of those entries.


**ResolveToExternalName directive**


**Syntax:** ResolveToExternalName = true | false
**Default:** ResolveToExternalName = false


The value of the ResolveToExternalName directive determines under which domain name the primary
and secondary head node hostnames are visible from within the head nodes, and to which IP addresses
their hostnames are resolved. Enabling this directive resolves the head nodes’ hostnames to the IP
addresses of their external interfaces.

Thus, on head nodes and regular nodes in both single-head and failover clusters


  - with ResolveToExternalName disabled, the master hostname and the actual hostname of the head
node (e.g. head1, head2 ) by default always resolve to the internal IP address of the head node.


  - with ResolveToExternalName enabled, the master hostname and the actual hostname of the head
node (e.g. head1, head2 ) by default always resolve to the external IP address of the head node.


The resolution behavior can be summarized by the following table:


_ResolveToExternalName Directive Effects_

|on simple head,<br>resolving:<br>master head|on failover head,<br>resolving:<br>master head1 head2|on regular node,<br>resolving:<br>master head(s)|Using<br>the<br>DNS?|
|---|---|---|---|
|**ResolveToExternalName = False**|**ResolveToExternalName = False**|**ResolveToExternalName = False**|**ResolveToExternalName = False**|



I I I I I I I No


I I I I I I I Yes


**ResolveToExternalName = True**


E E E E E E E No


E E E E E E E Yes


Key: I: resolves to internal IP address of head


E: resolves to external IP address of head


**861**


The system configuration files on the head nodes that get affected by this directive include /etc/hosts
and, on SLES systems, also the /etc/HOSTNAME . Also, the DNS zone configuration files get affected.
Additionally, in both the single-head and failover clusters, using the “ hostname -f ” command on
a head node while ResolveToExternalName is enabled results in the host’s Fully Qualified Domain
Name (FQDN) being returned with the host’s external domain name. That is, the domain name of the
network that is specified as the "External network" in the base partition in cmsh (the output of “ cmsh -c
"partition use base; get externalnetwork" ”).
Modifying the value of the ResolveToExternalName directive and restarting the CMDaemon while
important system services (e.g. Slurm) are running should not be done. Doing so is likely to cause
problems with accessing such services due to them then running with a different domain name than the
one with which they originally started.
On a tangential note that is closely, but not directly related to the ResolveToExternalName directive:
the cluster can be configured so that the “ hostname -f ” command executed on a regular node returns
the FQDN of that node, and so that the FQDN in turn resolves to an external IP for that regular node.
The details on how to do this are in the BCM Knowledge Base at http://kb.brightcomputing.com/ . A
search query for FQDN leads to the relevant entry.


**ResolveMasterToExternalName directive**


**Syntax:** AdvancedConfig = {"ResolveMasterToExternalName=0|1", ...}
**Default:** ResolveMasterToExternalName = 1


ResolveMasterToExternalName is a parameter of the AdvancedConfig (page 862) directive.
ResolveMasterToExternalName can only be used if ResolveToExternalName (page 860) is active.
If set to 1 (the default), then the master head node, as specified by the name master, resolves to the
IP address as set by ResolveToExternalName .
If set to 0 then the master head node resolves to the internal shared IP address.


**ResolveMasterToExternalDomainName directive**


**Syntax:** AdvancedConfig = {"ResolveMasterToExternalDomainName=0|1", ...}
**Default:** ResolveMasterToExternalDomainName = 1


ResolveMasterToExternalDomainName is a parameter of the AdvancedConfig (page 862) directive.
ResolveMasterToExternalDomainName can only be used if ResolveToExternalName (page 860) is
active.

The external domain name as defined for the external network, in the form master. < _external do-_
_main_ >, can be used in /etc/hosts during name resolution.
If set to 1 (the default), then the external domain name is used in /etc/hosts .
If set to 0, then the external domain name is not used in /etc/hosts .
Resolution occurs as shown in the following table:


**862** **CMDaemon Configuration File Directives**


_ResolveMasterToExternalDomainName Directive Effects_

|on simple head,<br>resolving:<br>master head|on failover head,<br>resolving:<br>master head1 head2|on regular node,<br>resolving:<br>master head(s)|Using<br>the<br>DNS?|
|---|---|---|---|
|**ResolveToExternalName = False**|**ResolveToExternalName = False**|**ResolveToExternalName = False**|**ResolveToExternalName = False**|



I I I I I I I No


I I I I I I I Yes


**ResolveToExternalName = True**


E E I E E I I No


E E I E E I E Yes


Key: I: resolves to internal IP address of head


E: resolves to external IP address of head


**DisableLua directive**


**Syntax:** DisableLua = true | false
**Default:** DisableLua = false


The value of the DisableLua directive determines if Lua code (section L.6) used in monitoring expressions can be executed.


**AdvancedConfig directive**


**Syntax:** AdvancedConfig = { "<key1>=<value1>", "<key2>=<value2>", ... }
**Default:** _Commented out in the default_ cmd.conf _file_
The AdvancedConfig directive is not part of the standard directives. It takes a set of key/value pairs
as parameters, with each key/value pair allowing a particular functionality, and is quite normal in
that respect. However, the functionality of a parameter to this directive is often applicable only under
restricted conditions, or for non-standard configurations. The AdvancedConfig parameters are therefore
generally not recommended for use by the administrator, nor are they generally documented.
Like for the other directives, only one AdvancedConfig directive line is used. This means that whatever functionality is to be enabled by this directive, its corresponding parameters must be added to that
one line. These key/value pairs are therefore added by appending them to any existing AdvancedConfig
key/value pairs, which means that the directive line can be a long list of key/value pairs to do with a
variety of configurations.


**Managing Key/Value Pairs With The** cm-manipulate-advanced-config.py **Utility**
The cm-manipulate-advanced-config.py utility can be used to make it easier to manage AdvancedConfig
key/value pairs.
For example, to add a key/value pair key8=value8 :


[root@basecm11 ~]# cm-manipulate-advanced-config.py key8=value8
Updated: /cm/local/apps/cmd/etc/cmd.conf


To show the current state of the AdvancedConfig, the -s|--show option can be used:


[root@basecm11 ~]# cm-manipulate-advanced-config.py -s
=== /cm/local/apps/cmd/etc/cmd.conf ===

VirtualCluster=1

key8=value8


A key/value pair can be removed by specifying its key with the -r|--remove option:


**863**


[root@basecm11 ~]# cm-manipulate-advanced-config.py -r key8
Updated: /cm/local/apps/cmd/etc/cmd.conf

[root@basecm11 ~]# cm-manipulate-advanced-config.py -s
=== /cm/local/apps/cmd/etc/cmd.conf ===

VirtualCluster=1


The utility can be used on cmd.conf in node images too, using the -i|--image option.


[root@basecm11 ~]# cm-manipulate-advanced-config.py -i /cm/images/default-image
Updated: /cm/images/default-image/cm/local/apps/cmd/etc/cmd.conf


The -q option causes the utility to exit with code 1 if cmd.conf has changed.
Further options can be seen with the -h|--help option.


**GlobalConfig directive**


**Syntax:** GlobalConfig = { "<key1>=<value1>", "<key2>=<value2>", ... }
**Default:** _not in the default_ cmd.conf _file_
The GlobalConfig directive is not part of the standard directives. It takes a set of key/value pairs as
parameters, with each key/value pair allowing a particular functionality, and is quite normal in that
respect. However, the parameter to this directive only needs to be specified on the head node. The
non-head node CMDaemons take this value upon connection, which means that the cmd.conf file on
the non-head nodes do not need to have this specified.
This allows nodes to set up, for example, their search domains using the MaximalSearchDomains
GlobalConfig directive (page 854).
Like for the other directives, only one GlobalConfig directive line is used. This means that whatever
functionality is to be enabled by this directive, its corresponding parameters must be added to that
one line. These key/value pairs are therefore added by appending them to any existing GlobalConfig
key/value pairs, which means that the directive line can be a long list of key/value pairs to do with a
variety of configurations.


**ScriptEnvironment directive**


**Syntax:** ScriptEnvironment = { "CMD_ENV1=<value1>", "CMD_ENV2=<value2>", ... }
**Default:** _Commented out in the default_ cmd.conf _file_


The ScriptEnvironment directive sets extra environment variables for CMDaemon and child processes.
For example, if CMDaemon is running behind a web proxy, then the environment variable
http_proxy may need to be set for it. If, for example, the proxy is the host brawndo, and it is accessed
via port 8080 using a username/password pair of joe / electrolytes, then the directive becomes:


ScriptEnvironment = { "http_proxy=joe:electrolytes@brawndo:8080" }


**BurnSpoolDir directive**


**Syntax:** BurnSpoolDir = _path_
**Default:** BurnSpoolDir = "/var/spool/burn/"


The BurnSpoolDir directive specifies the directory under which node burn log files are placed (Chapter 11 of the _Installation Manual_ ). The log files are logged under a directory named after the booting
MAC address of the NIC of the node. For example, for a MAC address of 00:0c:29:92:55:5e the directory
is /var/spool/burn/00-0c-29-92-55-5e .


**864** **CMDaemon Configuration File Directives**


**IdleThreshold directive**


**Syntax:** IdleThreshold = _number_
**Default:** IdleThreshold = 1.0


The IdleThreshold directive sets a threshold value for loadone . If loadone exceeds this value, then
data producers that have Only when idle (page 558) set to true ( enabled ), will not run. If the data
producer is sampled on a regular node rather than on the head node, then cmd.conf on the regular node
should be modified and its CMDaemon restarted.


**MonitoringPath directive**


**Syntax:** AdvancedConfig = {"MonitoringPath= _path_ ", ...}
**Default:** Implicit value: "MonitoringPath=/var/spool/cmd/monitoring/"


MonitoringPath is a parameter of the AdvancedConfig (page 862) directive.
Its value determines the path of the directory in which monitoring data is saved (section 14.8).


**MaxServiceFailureCount directive**


**Syntax:** AdvancedConfig = {"MaxServiceFailureCount= _number_ ", ...}
**Default:** Implicit value: "MaxServiceFailureCount=10"


MaxServiceFailureCount is a parameter of the AdvancedConfig (page 862) directive.
Its value determines the number of times a service failure event is logged (page 170). Restart attempts
on the service still continue when this number is exceeded.


**InitdScriptTimeout directive**


**Syntax:** AdvancedConfig = {"InitdScriptTimeout[. _service_ ]= _timeout_ ", ...}
**Default:** Implicit value: "InitdScriptTimeout=30"


InitdScriptTimeout is a parameter of the AdvancedConfig (page 862) directive. It can be set globally
or locally:


 - **Global (all services)**
InitdScriptTimeout can be set as a global value for init scripts, by assigning _timeout_ as a period
in seconds. If an init script fails to start up its service within this period, then CMDaemon kills the
service and attempts to restart it.


**–** If InitdScriptTimeout has a value for _timeout_ set, then all init scripts have a default timeout
of _timeout_ seconds.


**–** If InitdScriptTimeout has no _timeout_ value set, then all init scripts have a default timeout of
30 seconds.


 - **Local (for a specific service)**
If InitdScriptTimeout. _service_ is assigned a _timeout_ value, then the init script for that _service_ times
out in _timeout_ seconds. This timeout overrides, for that service only, any existing global default
timeout.


When a timeout happens for an init script attempting to start a service, the event is logged. If the
number of restart attempts exceeds the value determined by the MaxServiceFailureCount directive
(page 864), then the event is no longer logged, but the restart attempts continue.


**Example**


**865**


An fhgfs startup takes a bit longer than 30 seconds, and therefore times out with the default timeout
value of 30s. This results in the following logs in /var/log/cmdaemon :


cmd: [SERVICE] Debug: ProgramRunner: /etc/init.d/fhgfs-client restart

[DONE] 0 9

cmd: [SERVICE] Debug: /etc/init.d/fhgfs-client restart, exitcode = 0,

signal = 9


Here, _service_ is fhgfs-client, so setting the parameter can be done with:


AdvancedConfig = { ..., "initdScriptTimeout.fhgfs-client=60", ...}


This allows a more generous timeout of 60 seconds instead.
Restarting CMDaemon then should allow the fhgs startup to complete