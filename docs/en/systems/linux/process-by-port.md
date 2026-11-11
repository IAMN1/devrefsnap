<a id="найти-процесс-по-порту-в-linux"></a>
# Find a process by port on Linux

[Русский](../../../ru/systems/linux/process-by-port.md)

Use this page when an application reports an occupied port or you need to identify the process accepting TCP connections on a port.
Start with the protocol, port number, and environment where the application runs.

| Situation | Approach | Example |
| --- | --- | --- |
| TCP port 8000 is occupied | An exact `ss` filter and process details | [Command and output](#find-a-tcp-listener) |
| A row appears without a PID | Check permissions and process visibility | [Permission limits](#when-the-pid-is-missing) |
| The application is in another container | Check the network namespace and `/proc` access | [Namespace limits](#when-the-process-is-in-another-namespace) |
| You need UDP or TCP states other than LISTEN | Change the protocol or state selection | [Other sockets](#check-udp-and-other-tcp-states) |
| Repeat the check from scratch | Create your own practice socket | [Standalone example](#standalone-practice-example) |

Intermediate level, with advanced namespace diagnostics.
Prerequisites include a Linux terminal, command execution, and understanding the difference between a local system, container, and remote server.
Inspection requires `ss` from iproute2 and `ps` from procps-ng. The practice example also requires Python 3.

The recipe locates a local socket and process. Firewall, production service, and external reachability diagnostics require separate steps.
macOS does not provide `ss` as a standard utility. Run this recipe inside Linux.

<a id="найти-tcp-listener"></a>
## Find a TCP listener

To identify the process accepting connections on TCP port 8000, first distinguish these terms.
A port is a network endpoint number, such as `8000`. TCP and UDP have separate port sets.
TCP transfers data over a connection. UDP sends individual messages without establishing that kind of connection.
A socket is an operating system object for network communication. A process can hold several sockets.
A TCP listener is a socket in `LISTEN` state, ready to accept connections.
A PID is the numeric process identifier in the visible process space.

Use this command fragment on your Linux system.

```bash
ss -lntp 'sport = :8000'
```

Replace `8000` with the required port.
`-l` selects listening sockets, and `-n` preserves numeric addresses and ports.
`-t` selects TCP, while `-p` adds process details when they are available.
The `sport` filter specifies the socket's local port. For a listener, select that port rather than a remote client's port.
Quotes pass the filter as one shell argument.
The exact filter distinguishes `8000` from `18000`, unlike a substring search with `grep 8000`.

The following output is an illustration.

```text
State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
LISTEN 0      8      127.0.0.1:8000    0.0.0.0:*        users:(("python3",pid=4312,fd=3))
```

The PID, process name, queues, descriptor, and alignment depend on your system.
`pid=4312` identifies the process. `fd=3` is that process's open socket descriptor number.
`127.0.0.1:8000` in `Local Address:Port` means a loopback binding in the current network namespace.
Loopback provides access from inside that network environment.
In the same column, `0.0.0.0:8000` means all IPv4 interfaces in the namespace.
`[::]:8000` is the IPv6 wildcard. IPv4 acceptance additionally depends on socket and kernel settings.
A listener's `Peer Address:Port` column does not identify a connected client.

For the PID you found, inspect the user and launch command. Replace `4312` with the actual PID from `ss`.

```bash
ps -p 4312 -o pid,user,comm,args
```

`ps` displays the PID, user, short name, and arguments.
In this example the name is usually `python3`, while arguments depend on how it was started.
The process can exit between `ss` and `ps`, and another process can later reuse its PID.
Before changing state, verify the process and its purpose again.
A listener does not establish HTTP health or reachability through a firewall, NAT, or proxy.
Multiple rows or processes can be valid with different addresses, IPv4/IPv6, inherited sockets, and `SO_REUSEPORT`.

<a id="если-pid-не-показан"></a>
## When the PID is missing

If a `LISTEN` row appears without `users:(...)`, consider the different access restrictions for socket and process details.
To map a socket to a process, `ss -p` reads available descriptor information from `/proc`.
`/proc` is a virtual file system with process and kernel information.
An ordinary user usually sees their own processes, while other users' PIDs may be hidden.

If you have administrative permission on this Linux system, repeat the inspection.

```bash
sudo ss -lntp 'sport = :8000'
```

`sudo` runs the command with permitted administrative privileges. This `ss` command only reads state.
Elevated privileges may reveal another user's process details, but availability is not guaranteed.
Root is the administrative user with numeric ID 0.
Capabilities are individual kernel permissions that can be restricted independently of the user name.
`/proc` settings, security policies, capabilities, and container restrictions can hide information even from root.
Root inside a container does not automatically have Linux-host root privileges.
Elevating privileges does not switch the network namespace.

If no data rows appear, check the protocol, address, socket state, and namespace.
Use `-H` to suppress the header.

```bash
ss -H -lntp 'sport = :8000'
```

Empty output with a successful exit means no matching visible TCP listener existed at inspection time.
It does not prove the port is free in every environment or for every binding method.
Evaluate command errors separately from an empty result.

<a id="если-процесс-в-другом-namespace"></a>
## When the process is in another namespace

A network namespace is a separate Linux network environment with its own interfaces, routes, and sockets.
The same port can be used independently in different network namespaces.
By default, `ss` inspects its own command's network namespace.
Containers often have separate network namespaces, but can share networking with another container or the host.

A PID namespace controls process visibility and numbering.
The same process can have different host and container PIDs.
Networking determines socket visibility, while process mapping also depends on visible processes and `/proc`.
With a shared network and separate PID namespaces, root can see a listener without its owner's name or PID.

Run `ss` inside the application's environment through an authorized container access mechanism.
Check that `ss` is installed there.
A published container port can differ from the application's internal port.
NAT forwarding can work without a separate application listener on the host's published port.

If a process PID in the target environment is known, compare the namespace links.
This fragment applies to a Linux system where PID `4312` is visible through `/proc`.

```bash
readlink /proc/self/ns/net
readlink /proc/4312/ns/net
```

Identical values such as `net:[4026532001]` indicate the same network namespace.
An access error or exited process prevents this comparison.

With sufficient privileges, a Linux-host administrator can run `ss` in a known process's network namespace.

```bash
sudo nsenter --target 4312 --net -- ss -lntp 'sport = :8000'
```

`nsenter` starts a new command in the selected namespace.
Replace `4312` with a PID visible from the context where you invoke `nsenter`.
`--net` changes only the network namespace. The PID namespace and `/proc` remain as before.
Obtaining the socket list therefore does not guarantee visibility of all processes.
Entry requires kernel permissions, including suitable capabilities. `sudo` inside a restricted container may be insufficient.

<a id="проверить-udp-и-другие-состояния-tcp"></a>
## Check UDP and other TCP states

Use a separate query for UDP port 8000.

```bash
ss -uanp 'sport = :8000'
```

`-u` selects UDP, and `-a` includes connected and unconnected UDP sockets.
UDP has no TCP `LISTEN` state. Expect states such as `UNCONN` or `ESTAB`.
A UDP port with the same number is not the same TCP socket.

To include TCP listeners and established connections on local port 8000, use this query.

```bash
ss -antp 'sport = :8000'
```

The query includes established connections and listeners.
Use `dport` instead of `sport` to select a remote port.

<a id="самостоятельный-учебный-пример"></a>
## Standalone practice example

Create a separate practice directory inside Linux and check the tools.

```bash
ss -V
ps --version
python3 --version
```

On Debian, `iproute2` provides `ss`, `procps` provides `ps`, and `python3` provides the interpreter.
Follow your training system's rules when installing packages.
The example requires no `sudo` when details of your own process are normally available.

Save [`port_probe.py`](../../../../examples/systems/linux/port_probe.py). Run `python3 port_probe.py` from its directory.
The program creates its own TCP socket on `127.0.0.1` and asks the operating system to select a free port.
It does not accept requests or publish files, and closes only its own socket.

[`linux/port_probe.py`](../../../../examples/systems/linux/port_probe.py)

Expect the chosen port, Python PID, `LISTEN` row, `ps` output, and a message that the listener disappeared after closing.
Run without `python3 -O` to preserve the `assert` checks.
Rarely, another process can take that port between closing and reinspection.
The example does not test delivery of network data.

<a id="источники"></a>
## Sources

- [ss manual for iproute2 6.15.0](https://github.com/iproute2/iproute2/blob/v6.15.0/man/man8/ss.8), [Debian trixie](https://manpages.debian.org/trixie/iproute2/ss.8.en.html).
- [iproute2 6.15 release announcement](https://lists.openwall.net/netdev/2025/05/26/230).
- [Network namespaces](https://man7.org/linux/man-pages/man7/network_namespaces.7.html), [PID namespaces and /proc](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html).
- [nsenter on Debian trixie](https://manpages.debian.org/trixie/util-linux/nsenter.1.en.html), [ps](https://manpages.debian.org/trixie/procps/ps.1.en.html).

[Linux reference](README.md) · [Networking and services](network-and-services.md) · [Task index](../../tasks/README.md#linux-and-shell)
