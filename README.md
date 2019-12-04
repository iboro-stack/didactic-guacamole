# Grafana metric display
![image](https://user-images.githubusercontent.com/9170568/42430694-990514a4-82f5-11e8-8f89-3abfe55129a9.png)
# JSON data aggregation
Uses fluentd and later kafka for RFC7464 JSON sequence.
# Reduction system
All systems use CQRS
Command Query Responsibility Segregation
https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs
and
Event Sourcing
https://martinfowler.com/eaaDev/EventSourcing.html

This means we first store all data in a stream in append-only fashion
in a RFC7474 JSON sequence. Sometimes, there is a prefix on each line
that looks like this:
```
20180704T143646-0700	mainstream	{"created_at_ms":"1530740205000","id":"c2cd10a50b068e0e696771621d61fb60","ip":"34.220.251.198","cmd":"time","nodename":"overlord"}
20180704T143651-0700	mainstream	{"created_at_ms":"1530740211000","id":"211c590441101f66c2e4c74b25d23721","ip":"34.220.251.198","cmd":"time","nodename":"overlord"}
```
to remove it and convert back to RFC7464 JSON sequence we use:
```
zcat /var/log/dmges/_data/data.2018070*.log.gz| grep -o '{.*' |  ./hashrate/hashrate
```
Additionally, all our parsers are supposed to be insensitive to the
presence or absence of the 0x1e charcter at the start of each record.
Since we are newline separated ASCII there is no ambiguity.

On top of that we add basic temporal indexing
and then we play and replay these data and process them both in realtime
and in batches in a variety of languages and modes. These include
node javascript, C++, and ruby scripts.

We materialize views in Mysql and Influxdb and previously Splunk.
We display metrics in Grafana after loading into Mysql or Influxdb.
We currently run the metrics on developer machines ad hoc but intend to
run them continuously once we have a decent and complete looking
dashboard.

# Mine controller

This repository contains a few scripts and software configurations that make up
the mine controller.

When set up, the mine controller is a simple Debian instance running dnsmasq,
which provides DNS and DHCP service to mining hardware. dnsmasq is configured
to run a script when DHCP leases are created or removed. This script maintains
a directory structure containing simple files that reflects the current state
of each miner.

Another script polls miners for more in-depth stats related to mining and
hardware performance, and inserts each data point into the directory structure.

Finally, a third script called 'minectl' allows administrators to query the
mine and perform actions on miners.

An OpenVPN connection is opened from each mine controller to the DMG VPN, which
allows for remote access.


