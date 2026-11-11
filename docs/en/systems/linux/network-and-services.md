<a id="сеть-службы-и-пакеты-linux"></a>
# Linux networking, services, and packages

[Русский](../../../ru/systems/linux/network-and-services.md)

Use this page when a Linux application is unavailable or you need to inspect a service or package.
Start by reading the state. Practice changes to services and packages on a separate training system.

| Task | Approach | Example |
| --- | --- | --- |
| Locate the failing network layer | Address → route → listener → DNS → HTTP | [Network diagnostics](#inspect-the-network-state-first) |
| Find the owner of a TCP port | An exact `ss` filter and PID verification | [Port and process](process-by-port.md#find-a-tcp-listener) |
| Distinguish a stopped service from disabled startup | `is-active`, `is-enabled`, and logs | [systemd](#systemd-services) |
| Choose a package command | Check the distribution and manager version | [APT and DNF](#choose-package-commands-for-your-distribution) |
| Diagnose disk and memory use | Compare `df`, `du`, and available memory | [Resources](#disk-and-resources) |

Advanced level. Prerequisites include a Linux system and an understanding of IP, HTTP, and administration rules.
[Linux reference](README.md).
[Find a process by port](process-by-port.md#find-a-tcp-listener) for commands, output, permissions, and namespaces.

Commands on this page are reference fragments.
The [process lookup exercise](process-by-port.md#standalone-practice-example) creates its own socket on Linux.
Test changes on a separate Linux training system with the owner's permission.

<a id="сеть-сначала-чтение-состояния"></a>
## Inspect the network state first

If an HTTP service on port `8000` is not responding, check its address, route, and listener before changing configuration.

| Layer | Command | Visible state |
| --- | --- | --- |
| Interfaces, iproute2 | `ip -brief address` | Interface addresses and state |
| Routes, iproute2 | `ip route` | The current network namespace's routing table |
| TCP listeners, iproute2 | `ss -lnt` | Listening addresses and ports without DNS substitution |
| Process on TCP port 8000 | `ss -lntp 'sport = :8000'` | [PID, permissions, and namespaces](process-by-port.md#find-a-tcp-listener) |
| System name resolution through NSS, glibc | `getent ahosts example.com` | The system name resolution result |
| HTTP/TLS, curl | `curl --fail-with-body --connect-timeout 5 --max-time 10 https://example.com` | A time-limited HTTP request requiring external network access |

`ss` displays the listener's local address. `curl` tests a separate HTTP request.
`--fail-with-body` requires curl 7.76.0 or later. HTTP errors usually return `22` and preserve the response body.
Connection failures and timeouts have different codes. Compare the code with curl's diagnostic output.

`127.0.0.1:8000` listens on loopback. `0.0.0.0:8000` listens on all IPv4 interfaces in the namespace.
The bind address alone does not establish reachability through a firewall, NAT, or proxy.
`ping` tests ICMP, which can be blocked even when HTTP works.
`dig` sends DNS queries. Its result can differ from application name resolution through NSS and hosts files.
Minimal images may lack `getent` or iproute2.
`curl -k` disables TLS verification. Check the CA, server name, and system time to diagnose certificate problems.

On your first SSH connection, verify the address and server key. Prefer configured authentication keys.
Replace the placeholders in `ssh user@host` with actual values.
Keep host key checking enabled when investigating warnings.
Changes to addresses, routes, and firewalls can disconnect you. This page does not present them as a quick fix.

<a id="службы-systemd"></a>
## systemd services

If a service should be running but the application does not respond, compare its current state, startup setting, and recent logs.
Use these commands on systems where systemd manages services.
Replace `NAME.service` with an existing unit name. Permissions may restrict access to some logs.

```text
systemctl status NAME.service
systemctl is-active NAME.service
systemctl is-enabled NAME.service
systemctl cat NAME.service
journalctl -u NAME.service -n 50 --no-pager
journalctl -u NAME.service --since '1 hour ago'
```

`active` describes the current state. `enabled` describes activation settings. Either can exist without the other.
`is-active` and `is-enabled` return status codes. An inactive result need not mean the diagnostic command malfunctioned.
`status` can also return a nonzero code for an inactive or failed service.
User services use `systemctl --user`. That command addresses a different manager or namespace and does not bypass root permissions.

| Change | Reference command | Consequence |
| --- | --- | --- |
| Start now | `sudo systemctl start NAME.service` | Runs ExecStart and dependencies |
| Stop | `sudo systemctl stop NAME.service` | May interrupt request handling |
| Restart | `sudo systemctl restart NAME.service` | Stops and starts the service, with possible downtime |
| Enable at boot | `sudo systemctl enable NAME.service` | Creates startup links and usually does not start immediately without `--now` |
| Reread a changed unit | `sudo systemctl daemon-reload` | Rereads unit definitions, which differs from reloading the application |

Application `reload` support depends on the unit. Inspect `systemctl cat`, ExecReload, and the service documentation.
Preserve logs and determine the cause before restarting a service because its status is red.
Containers can run processes directly without systemd. macOS uses different tools.

<a id="пакеты-учитывать-дистрибутив"></a>
## Choose package commands for your distribution

If a practice recipe needs a missing utility, find the package and read its description before installation.
Package names and managers depend on the system.

Read `/etc/os-release` first. Check `command -v apt`, `command -v dnf`, and the versions of the installed tools.
The presence of one command does not identify the whole system. Use this table as a reference.

| Task | Debian/Ubuntu, APT | RPM systems with DNF |
| --- | --- | --- |
| Search | `apt search PACKAGE` | `dnf search PACKAGE` |
| Information | `apt show PACKAGE` | `dnf info PACKAGE` |
| Update metadata | `sudo apt update` | `sudo dnf makecache` |
| Install a package | `sudo apt install PACKAGE` | `sudo dnf install PACKAGE` |
| Remove a package | `sudo apt remove PACKAGE` | `sudo dnf remove PACKAGE` |

Search and description commands help you select a package while preserving the installed set.
Replace `PACKAGE` with a verified name.
Installation and removal change the system and dependencies. Review the proposed transaction.
`apt update` refreshes metadata without upgrading all installed packages.
For Debian automation, use the documented apt-get and apt-cache interfaces instead of interactive apt.
DNF4 and DNF5 differ in some commands and options. Check documentation for the installed version.
Arch, Alpine, and other systems have their own managers and conventions. APT and DNF commands are not universal.

<a id="диск-и-ресурсы"></a>
## Disk and resources

If a directory appears small while its file system is nearly full, compare file system usage with the size of that directory tree.
The following fragment inspects an existing `project` directory.

```bash
df -h .
du -sh project
```

The first command describes the current directory's file system. The second measures the `project` tree.

`df -h` reports file systems. `du -sh path` estimates the space used by a tree.
These are different quantities. Deleted but open files, sparse files, and file system snapshots can explain discrepancies.
On Linux, `free -h` and `/proc/meminfo` help inspect memory.
A small free-memory value does not imply that available memory is exhausted.

<a id="источники"></a>
## Sources

[Linux ip](https://man7.org/linux/man-pages/man8/ip.8.html), [ss](https://man7.org/linux/man-pages/man8/ss.8.html),
[curl](https://curl.se/docs/manpage.html),
[systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html),
[journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html),
[Debian APT](https://manpages.debian.org/bookworm/apt/apt.8.en.html),
[DNF](https://dnf.readthedocs.io/en/latest/command_ref.html).
