# Cb Response Splunk App

Current Version: 1.0.0

The Carbon Black App for Splunk allows administrators to leverage the industry's leading EDR solution to see, 
detect and take action upon endpoint activity from directly within Splunk.

## Requirements

This app requires a functional Carbon Black server, version 5.1 or above, and Splunk version 6.3 or above.
The app works with Cb Response clusters. Currently the Cb Response Unified View (Federated) server is not
supported.

No additional hardware requirements are necessary for running this app above the standard requirements for both
Carbon Black and Splunk.

## Getting Started

Once the Cb Response app for Splunk is installed, then you must configure it to connect to your Cb Response server.
This is done by using the Cb Response REST API. For more information on the Cb Response REST API and how
to generate an API key, see the [Cb Developer Network](https://developer.carbonblack.com/reference/enterprise-response/).

The Cb Response app for Splunk uses a Cb Response API key to:

1. Power the `sensorsearch`, `processsearch` and `binarysearch` custom commands by performing searches via the Cb Response API.
2. Enable the "Endpoint Isolation" Adaptive Response Action by requesting endpoint isolation through the Cb Response API
3. Enable the "Ban Hash" Adaptive Response Action by using the Cb Response API to add an MD5 hash to the list of banned hashes
4. Enable the "Kill Process" Adaptive Response Action by using the Cb Response Live Response API to kill a process on a remote endpoint (note that Live Response must be enabled on the Cb Response server for this to function; see the Cb Response User Guide for more information on Live Response)

To configure the Cb Response app for Splunk to connect to your Cb Response server:

1. Click the Apps drop down next to the Splunk icon on the top of the Splunk dashboard.
2. Click the Manage Apps menu item.
3. Click the Set Up action to the right of the Cb Response app.
4. Retrieve an API key for a Global Administrator user on the Cb Response server. For detailed instructions, see the documentation on the Developer Network website at
https://developer.carbonblack.com/reference/enterprise-response/authentication/.
5. Return to the Splunk configuration page and do the following:
    1. Paste the API token into the apikey field.
    2. Enter the URL for your Cb Response server instance in the cburl field. For example, enter: https://cbserver.mycompany.com
6.	Click Save to save the new configuration.

The Cb Response app for Splunk uses Splunk’s encrypted credential storage facility to store the API token for your Cb Response server, so the API key is stored securely on the Splunk server.

### Splunk Distributed Environment Configuration

It is recommended to install this app on a search head and not have it replicate to indexers.
To prevent replication to indexers add the following stanza and variables to your distsearch.conf.
Located at SPLUNK_HOME/etc/system/local/distsearch.conf

        [replicationBlacklist]
        carbonblack = apps/DA-ESS-CbResponse/...

http://docs.splunk.com/Documentation/ES/latest/Install/InstallTechnologyAdd-ons#Import_add-ons_with_a_different_naming_convention.

## Features

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

* **Custom Commands**: These commands can be used in your Splunk pipeline to use the power of Splunk's
  visualization and searching capability against Cb Response data, without ingesting all of the 
  raw endpoint data into Splunk itself.
  * `sensorsearch`: Search for sensors in your Cb Response server by IP address or hostname
  * `processsearch`: Search for processes in your Cb Response server
  * `binarysearch`: Search for binaries in your Cb Response server

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

### Dashboards

Once the app is installed, a new icon appears on the left hand side of the Splunk front page with the Cb Response logo. 
Clicking the logo brings you to the default dashboard of the Cb Repsonse for Splunk app. 
Additional dashboards include an overview of endpoint status, including a breakdown of OS and sensor versions, 
as well as data on the latest new binaries seen in the environment.

The Process, Binary, and Sensor Search dashboards allow you to perform Cb searches directly from within Splunk.
These dashboards use the respective custom commands to perform the search through the REST API without ingesting
the data into Splunk. The results will be displayed within the same screen.  Users can also use Carbon Black search features
using the following custom search commands.

*   process search

        Example: processsearch query="process_name:cmd.exe"

*   binary search

        Example: binarysearch query="md5:fd3cee0bbc4e55838e65911ff19ef6f5"

### Custom Commands

The Splunk app includes three custom commands to perform searches on the Carbon Black datastore from Splunk: 
`binarysearch`, `processsearch`, and `sensorsearch`. These three commands also have corresponding views 
in the Carbon Black app: "Binary Search", "Process Search", and "Sensor Search".

To use the custom commands in your Splunk searches, first ensure that you’re using the Cb Response context by 
invoking the search through the Splunk > Search menu inside the Cb Response app. Then you can use any of the 
search commands by appending the Cb Response query as a “query” parameter. For example:

    | sensorsearch query=”ip:172.22.5.141” 

will send an API request to Cb Response to query for all sensors that have reported an IP address of 172.22.5.141. 
The result of this query can be piped through to other Splunk commands for aggregation, visualization, and correlation.

### Saved Searches

Several example reports and saved searches are included in this app release. A full list of these searches can be 
found by the Settings > Searches, reports, and alerts menu item from the Cb Response app. Note that none of these 
are run or scheduled by default, and some will not return any data unless certain data types 
(netconns, procstarts, etc) are forwarded via the Cb Event Forwarder into Splunk.

### Adaptive Response Alert Actions

The Cb Response app for Splunk now integrates with Splunk’s Adaptive Response framework and provides three Adaptive 
Response Alert Actions:

* Isolate Endpoint
* Ban MD5 Hash
* Kill Process

Each of these Actions can be performed either on an ad-hoc basis on a notable event surfaced in Enterprise Security, 
or on an automated basis as part of a Splunk Correlation Search. In addition, the Isolate Endpoint and Ban MD5 Hash 
actions can be invoked based on search results from any Splunk search, as long as a field is present that provides 
an IP address (for Isolate Endpoint) or an MD5 hash (for Ban Hash). Currently, only events surfaced via the Cb 
Event Forwarder can be used as input for the Kill Process alert action.


### Workflow Actions

Workflow Actions allow users to pivot into Carbon Black searches from standardized fields.
The Cb Response app for Splunk includes Workflow Actions that provide you with context about events in any 
Splunk view, including Enterprise Security’s Notable Event table. 
To Perform a workflow action, drilldown into an event and click the 'Event Actions' button.
From this menu the available workflow actions from this app will be displayed.
A User can pivot directly from a field given that a workflow action is available for that field.
The following Workflow Actions are included:

* Sensor Information by IP: find detailed information about a Cb Response sensor given an IP address field
* Binary Search by MD5 hash: retrieve context around a binary given an MD5 file hash
* Search for Processes contacting IP: retrieve a list of processes from Cb Response which have made a connection to or received a connection from the given IP address
* Search for Processes related to MD5 hash: retrieve a list of processes from Cb Response which have links to the given MD5 hash (a loaded module/DLL, the executable itself, a file write to an executable with the given MD5 hash)
* Search for Processes contacting Domain: retrieve a list of processes from Cb Response which have made a connection to or received a connection from the given domain name
* Search for Processes related to filename: retrieve a list of processes from Cb Response which have referred to the given filename (written/modified the file, etc.)

In addition, for events that were generated by Cb Response (forwarded into Splunk via the Cb Event Forwarder), 
additional Workflow Actions are enabled to provide deep links into the Cb Response console directly from the event 
in Splunk, where applicable. These deep links require the Cb Event Forwarder to be configured properly to generate 
these links at event generation time (see the Cb Event Forwarder configuration file for more details).

* Deep Link to target process's Process Analysis page
* Deep Link to parent process's Process Analysis page
* Deep Link to child process's Process Analysis page
* Deep Link to Binary Analysis page
* Deep Link to Sensor page

## Performance

This app contains one Data Model, representing Cb alerts plus watchlist/feed hits. 
This data model is accelerated by default.

None of the saved searches included in this app are scheduled to run by default.

## Support

For issues with this app, please post on the [Carbon Black User eXchange](https://community.carbonblack.com/community/developer-relations).
When you contact Carbon Black Support with an issue, please provide the following:

* Your name, company name, telephone number, and e-mail address
* Product name/version, CB Server version, CB Sensor version
* Splunk version
* Hardware configuration of the Carbon Black Server or computer (processor, memory, and RAM)
* For documentation issues, specify the version of the manual you are using.
* Action causing the problem, error message returned, and event log output (as appropriate)
* Problem severity

### Diagnostics

The Cb Response App for Splunk writes its log files into the standard Splunk log directory. The following log 
files (all located under $SPLUNK_HOME/var/log/splunk) are used by the App:

1. da-ess-cbresponse.log --- main log file for common Cb Response helper functions, including the search Custom Commands
2. isolate_modalert.log --- log file for the Isolate Endpoint Adaptive Response Action
3. banhash_modalert.log --- log file for the Ban Hash Adaptive Response Action
4. killprocess_modalert.log --- log file for the Kill Process Adaptive Response Action
