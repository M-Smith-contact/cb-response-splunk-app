# Cb Response Splunk App

Current Version: 1.0.0

The Carbon Black App for Splunk allows administrators to leverage the industry's leading EDR solution to see, 
detect and take action upon endpoint activity from directly within Splunk.

## Features

* **Custom Commands**: These commands can be used in your Splunk pipeline to use the power of Splunk's
  visualization and searching capability against Cb Response data, without ingesting all of the 
  raw endpoint data into Splunk itself.
  * `sensorsearch`: Search for sensors in your Cb Response server by IP address or hostname
  * `processsearch`: Search for processes in your Cb Response server
  * `binarysearch`: Search for binaries in your Cb Response server

* **Dashboards**: These pre-built dashboards provide you a quick check on the health of your Cb server,
  status of your Cb Response deployment, and an overview of the detected threats on your network. Eight
  example dashboards are distributed with this app; not all of these may be populated with data depending
  on what events are being forwarded to Splunk via the [Cb Event Forwarder](https://developer.carbonblack.com/reference/enterprise-response/event-forwarder/)
  * **Overview**: Provides a quick overview including the number of sensors reporting alerts and the
    top feed and watchlist hits across the enterprise.
  * **Binary Search**: Search the Cb Response binary holdings via the `binarysearch` custom command.
  * **Process Search**: Search the processes tracked by Cb Response via the `processsearch` custom command.
  * **Process Timeline**: Produce a simple timeline of events given a Cb Response process GUID.
  * **Sensor Search**: Search endpoints tracked by Cb Response via the `sensorsearch` custom command.
  * **Cb Response Endpoint Status**: Display information about the total number of reported sensors,
    OS and Cb Response agent version distribution across all endpoints.
  * **Cb Response Network Overview**: Show visualizations related to incoming and outgoing network
    connections recorded by Cb Response. Note that this view is only populated if *netconn* events are
    forwarded via the Cb Event Forwarder.
  * **Cb Response Binary Status**: Display information about attempts to execute banned processes,
    and information on new executables and shared libraries discovered by Cb Response.

* **Adaptive Response Alert Actions**: Splunk's new *Adaptive Response* capability now allows you to
  take action straight from the Splunk console. The Cb Response Splunk app currently includes three
  Adaptive Response Alert Actions that allow you to take action either as a result of automated
  Correlation Searches or on an ad-hoc basis through the Splunk Enterprise Security Incident Review page.
  * **Kill Process**: Kill a given process that is actively running on an endpoint running the Cb Response sensor. 
    The process must be identified by a Cb Response event ID. Killing processes allow the security analyst 
    to quickly respond to attackers who may be using tools that cannot otherwise be banned by hash 
    (for example, reusing a legitimate administrative tool for malicious purposes).
  * **Ban MD5 Hash**: Ban a given MD5 hash from executing on any host running the Cb Response sensor. 
    The MD5 hash can be specified by a custom hash field. This allows incident responders to quickly respond 
    to evolving threats by keeping attackers’ tools from executing while the threat can be properly 
    remediated and the attacker expelled from the network. 
  * **Isolate Sensor**: isolate a given endpoint from the network. The endpoint to isolate can be 
    specified by either a custom IP address field (shown below) or a sensor ID that’s provided in 
    Carbon Black Response events plumbed through to Splunk. Network isolation is useful when malware 
    is active on an endpoint, and you need to perform further investigative tasks 
    (for example, retrieving files or killing processes through Carbon Black Live Response) 
    remotely from your management console, but at the same time prevent any connections to active 
    C2 or exfiltration of sensitive data.

* **Saved Searches**: Included in this release are 58 saved searches to jump-start Threat Hunting
  from within the Splunk environment, thanks to community contributions from Mike Haag and others.
  
* **Workflow Actions**: This app includes workflow actions to provide additional context from Cb Response
  on events originated from any product that pushes data into your Splunk server. These context menu items
  include:
  * **Deep links**: Deep links into the Cb Response server for any event originated from a Cb Response
    sensor. Allows you to access the powerful process tree and other data available from Cb Response from
    a single link inside Splunk.
  * **Process search by IP, MD5**: Search the Cb Response server for processes associated with a given
    IP address or MD5 hash from any event in Splunk.
  * **Sensor info by IP**: Search the Cb Response server for detailed endpoint information associated with
    a given IP address from any event in Splunk.

## Requirements

This app requires a functional Carbon Black server, version 5.1 or above, and Splunk version 6.3 or above.
The app works with Cb Response clusters. Currently the Cb Response Unified View (Federated) server is not
supported.

No additional hardware requirements are necessary for running this app above the standard requirements for both
Carbon Black and Splunk.

## Getting Started

Once the integration is installed, you must configure it to connect to your Carbon Black server. The Integration requires a Carbon Black API token from a user with Search privileges to enable all current features.

To retrieve the Carbon Black API Token, see the documentation on the Developer Network website at
https://developer.carbonblack.com/reference/enterprise-response/authentication/.

1.  Log into your Carbon Black server, click your user profile on the top right banner and select "Profile Info".
2.  On this page, click "API Token" on the left hand side and copy  the API token

To setup the Splunk App:

1. Navigate to the Apps Manager page.
2. Look for the Cb Response App
3. Click 'Set up'
4. Enter your server URL in the 'CB server URL' text box. (example: https://cbserver.mycompany.com)
5. Paste the Carbon Black API Token into the text box labelled 'API Key'.
6. Click 'Save'

## Usage

The Carbon Black Splunk Application contains two major components. These components are process/binary search within
the app and workflow actions that enable pivoting from standardized fields into Carbon Black searches.

### Process/Binary Search

The main tab within the Cb Response Splunk App allows users to perform either a process or binary search
within Carbon Black.  The results will be displayed within the same screen.  Users can also use Carbon Black search features
using the following custom search commands.

*   process search

        Example: processsearch query="process_name:cmd.exe"

*   binary search

        Example: binarysearch query="md5=fd3cee0bbc4e55838e65911ff19ef6f5"

### Workflow Actions

Workflow Actions allow users to pivot into Carbon Black searches from standardized fields.  To Perform a workflow action, drilldown into an event and click the 'Event Actions' button.  From this menu the available workflow actions from this app will be displayed.  A User can pivot directly from a field given that a workflow action is available for that field.  Current supported workflow actions:

| Workflow Action                  | Supported Fields                           |
|----------------------------------|--------------------------------------------|
| CB Binary Search by MD5          | md5, file_hash, process_md5                |
| CB Process Search by IP          | src_ip, dest_ip, local_ip, remote_ip, ipv4 |
| CB Process Search by MD5         | md5, file_hash                             |
| CB Process Search by FileName    | file_name, file_path                       |
| CB Process Search by Domain      | domain                                     |

### Splunk Distributed Environment Configuration

It is recommended to install this app on a search head and not have it replicate to indexers.
To prevent replication to indexers add the following stanza and variables to your distsearch.conf.
Located at SPLUNK_HOME/etc/system/local/distsearch.conf

        [replicationBlacklist]
        carbonblack = apps/DA-ESS-CbResponse/...

http://docs.splunk.com/Documentation/ES/latest/Install/InstallTechnologyAdd-ons#Import_add-ons_with_a_different_naming_convention.

## Contacting Carbon Black Support

E-mail: dev-support@carbonblack.com

### Reporting Problems

When you contact Carbon Black Support with an issue, please provide the following:

* Your name, company name, telephone number, and e-mail address
* Product name/version, CB Server version, CB Sensor version
* Splunk version
* Hardware configuration of the Carbon Black Server or computer (processor, memory, and RAM)
* For documentation issues, specify the version of the manual you are using.
* Action causing the problem, error message returned, and event log output (as appropriate)
* Problem severity