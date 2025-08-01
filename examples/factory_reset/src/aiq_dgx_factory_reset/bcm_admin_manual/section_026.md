# **M**

### A Tree View Of cmsh



**M.1** **Modes**


A 3-level tree of the modes in cmsh is:


|-- category
| |-- biossettings
| |-- bmcsettings
| |-- dpusettings
| | `-- keyvaluesettings
| |-- fsexports

| |-- fsmounts

| |-- gpusettings

| |-- kernelmodules

| |-- roles

| | |-- advancedsettings
| | |-- commsettings
| | |-- configs
| | |-- configurations
| | |-- connectionsettings

| | |-- domains

| | |-- engines

| | |-- environments

| | |-- excludelistsnippets
| | |-- genericresources

| | |-- interfaces

| | |-- logsettings
| | |-- momsettings
| | |-- nginxreverseproxy

| | |-- nodecustomizations

| | |-- openports
| | |-- policies
| | |-- powerprofiles
| | |-- resourceproviders

| | |-- routes

| | |-- servers

| | |-- spawner
| | |-- storagedrivers
| | |-- storagebackends

| | `-- zones

| |-- selinuxsettings
| | `-- keyvaluesettings

| |-- services


**1020** **A Tree View Of** cmsh


| |-- staticroutes

| `-- ztpsettings

|-- cert

|-- cloud

| |-- extensions

| |-- instancepools
| |-- ocigpumemoryclusters
| |-- regions
| |-- types
| `-- vpcs
|-- configurationoverlay

| |-- customizations

| `-- roles

| |-- advancedsettings
| |-- commsettings
| |-- configs
| |-- configurations
| |-- connectionsettings

| |-- domains

| |-- engines

| |-- environments

| |-- excludelistsnippets
| |-- genericresources

| |-- interfaces

| |-- logsettings
| |-- momsettings
| |-- nginxreverseproxy

| |-- nodecustomizations

| |-- openports
| |-- policies
| |-- powerprofiles
| |-- resourceproviders

| |-- routes

| |-- servers

| |-- spawner
| |-- storagedrivers
| |-- storagebackends

| `-- zones

|-- device

| |-- accesssettings
| |-- biosettings
| |-- bmcsettings
| |-- chassisposition
| |-- cloudsettings

| | |-- disks

| | |-- platformconfig
| | `-- storage
| |-- dpusettings
| | `-- keyvaluesettings
| |-- fsexports

| |-- fsmounts

| |-- gpusettings

| |-- interfaces

| |-- kernelmodules

| |-- nvconfiguration


**M.1 Modes** **1021**


| |-- prometheusmetricforwarders
| |-- rackposition

| |-- roles

| | |-- advancedsettings
| | |-- commsettings
| | |-- configs
| | |-- configurations
| | |-- connectionsettings

| | |-- domains

| | |-- engines

| | |-- environments

| | |-- excludelistsnippets
| | |-- genericresources

| | |-- interfaces

| | |-- logsettings
| | |-- momsettings
| | |-- nginxreverseproxy

| | |-- nodecustomizations

| | |-- openports
| | |-- policies
| | |-- powerprofiles
| | |-- resourceproviders

| | |-- routes

| | |-- servers

| | |-- spawner
| | |-- storagedrivers
| | |-- storagebackends

| | `-- zones

| |-- selinuxsettings
| | `-- keyvaluesettings

| |-- services

| |-- snmpsettings

| |-- staticroutes

| `-- ztpsettings
| `-- keyvaluesettings
|-- edgesite

|-- etcd

|-- fspart
| `-- excludelistsnippets
|-- group
|-- hierarchy

| |-- sources

| `-- targets

|-- kubernetes

| |-- appgroups
| | `-- applications

| |-- labelsets

| `-- users

|-- main

|-- monitoring

| |-- action

| |-- consolidator

| | `-- consolidators

| |-- labeledentity

| |-- measurable


**1022** **A Tree View Of** cmsh


| |-- query

| | `-- drilldown

| |-- report
| |-- setup
| | |-- dpusettings
| | |-- executionmultiplexers
| | |-- jobmetricsettings

| | `-- nodeexecutionfilters

| |-- standalone

| `-- trigger
| `-- expression

|-- network

|-- nodegroup
|-- partition
| |-- accesssettings

| |-- archos

| |-- bmcsettings
| |-- burnconfigs
| |-- dpusettings
| | `-- keyvaluesettings

| |-- failover

| |-- failovergroups
| |-- leakactionpolicies

| | `-- rules

| |-- netqsettings
| | `-- prometheusmetricforwarders
| |-- nmxmsettings
| | `-- prometheusmetricforwarders
| |-- prometheusmetricforwarders
| |-- provisioningsettings
| |-- resourcepools
| |-- selinuxsettings
| | `-- keyvaluesettings
| |-- snmpsettings
| |-- ufmsettings
| |-- wlmjobpowerusagesettings
| |-- ztpnewswitchsettings
| | `-- keyvaluesettings
| `-- ztpsettings
| `-- keyvaluesettings
|-- powercircuit
|-- process
|-- profile

|-- rack

|-- session

|-- softwareimage

| |-- kernelmodules

| `-- selection

|-- task

|-- user

| `-- projectmanager

`-- wlm

|-- accounting
|-- cgroups
|-- chargeback


**M.1 Modes** **1023**


|-- jobqueue
|-- jobs

|-- licenses

|-- ocisettings
|-- pelogs
|-- placeholders
|-- prssettings

`-- topologysettings
|-- blocksettings
|-- parameters
|-- topographsettings

`-- treesettings


# **N**

### **BCM And NVIDIA AI** **Enterprise**

Some features of BCM are certified for NVIDIA AI Enterprise ( [https://docs.nvidia.com/ai-enterprise/](https://docs.nvidia.com/ai-enterprise/index.html)
[index.html](https://docs.nvidia.com/ai-enterprise/index.html) ).


**N.0.1** **Certified Features Of BCM For NVIDIA AI Enterprise**

The BCM Feature Matrix at:


[https://support.brightcomputing.com/feature-matrix/](https://support.brightcomputing.com/feature-matrix/)


has a complete list of the features of BCM that are certified for NVIDIA AI Enterprise.


**N.0.2** **NVIDIA AI Enterprise Compatible Servers**
BCM must be deployed on NVIDIA AI Enterprise compatible servers.
The NVIDIA Qualified System Catalog at:


[https://www.nvidia.com/en-us/data-center/data-center-gpus/qualified-system-catalog/](https://www.nvidia.com/en-us/data-center/data-center-gpus/qualified-system-catalog/)


displays a complete list of NVIDIA AI Enterprise compatible servers if the NVAIE Compatible option
is selected.


**N.0.3** **NVIDIA Software Versions Supported**
NVIDIA AI Enterprise supports specific versions of NVIDIA software, including


  - NVIDIA drivers


  - NVIDIA containers


  - the NVIDIA Container Toolkit


  - the NVIDIA GPU Operator


  - the NVIDIA Network Operator


The NVIDIA AI Enterprise Catalog On NGC at:


[https://catalog.ngc.nvidia.com/enterprise](https://catalog.ngc.nvidia.com/enterprise)


lists the specific versions of software included in a release.


**N.0.4** **NVIDIA AI Enterprise Product Support Matrix**
The NVIDIA AI Enterprise Product Support Matrix at:


[https://docs.nvidia.com/ai-enterprise/latest/product-support-matrix/index.html](https://docs.nvidia.com/ai-enterprise/latest/product-support-matrix/index.html)


lists the platforms that are supported.