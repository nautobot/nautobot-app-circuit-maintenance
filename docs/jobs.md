# Jobs

## Run Handle Notifications Job

There is an asynchronous task defined as a **Nautobot Job**, **Handle Circuit Maintenance Notifications** that will connect to the emails sources defined under the Notification Sources section (step above), and will fetch new notifications received since the last notification was fetched.
Each notification will be parsed using the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser) library, and if a valid parsing is executed, a new **Circuit Maintenance** will be created, or if it was already created, it will updated with the new data.

So, for each email notification received, several objects will be created:

### Notification

Each notification received will create a related object, containing the raw data received, and linking to the corresponding **parsed notification** in case the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser) was able to parse it correctly.

### Parsed Notification

When a notification was successfully parsed, it will create a **parsed notification** object, that will contain the structured output from the parser library , following the recommendation defined in [draft NANOG BCOP](https://github.com/jda/maintnote-std/blob/master/standard.md), and a link to the related **Circuit Maintenance** object created.

### Circuit Maintenance

The **Circuit Maintenance** is where all the necessary information related to a Circuit maintenance is tracked, and reuses most of the data model defined in the parser library.

Attributes:

- Name: name or identifier of the maintenance.
- Description: description of the maintenance.
- Status: current state of the maintenance.
- Start time: defined start time of the maintenance work.
- End time: defined end time of the maintenance work.
- Ack: boolean to show if the maintenance has been properly handled by the operator.
- Circuits: list of circuits and its specific impact linked to this maintenance.
- Notes: list of internal notes linked to this maintenance.
- Notifications: list of all the parsed notifications that have been processed for this maintenance.

![Circuit Maintenance Job](images/circuit_maintenance.png)

## Circuit Overlap Job

The circuit overlap job that gets included with the Circuit Maintenance Plugin is a job that is going to search for possible overlapping maintenances, which **may** cause an outage of a site. The variable `overlap_job_exclude_no_impact ` controls on the check if a maintenance notification has an expected impact. Default is `False` for this setting, that any maintenance notification will be alerted on within the Nautobot Job. 

Use the Job regularly to search for the overlap and review any log message that has a Warning level that will indicate that there is a possible overlapping maintenance.
