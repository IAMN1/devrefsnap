<a id="изоляция-сохранность-и-эксплуатация-redis"></a>
# Redis isolation, durability, and operations

[Русский](../../../../ru/databases/non-relational/redis/operations.md)

[Redis](README.md)

Use this page to run an isolated instance, choose a persistence mechanism, or diagnose Redis.

| Task | Technique | Example |
| --- | --- | --- |
| Back up and verify a restore | Completed RDB file and a new instance | [Quick reference](#create-and-restore-an-rdb-backup) · [Complete program](backup-and-restore.md#complete-example) |
| Back up AOF and restore the data | Manifest, BASE, and INCR after shutdown | [AOF reference](#create-and-restore-an-aof-backup) · [Complete program](aof-backup-and-restore.md#complete-example) |
| Set up an instance for other examples | Unix socket with persistence disabled | [Practice instance](#practice-instance) |
| Choose a durability mechanism | RDB, AOF, and replication | [Comparison](#durability-and-recovery) |
| Diagnose eviction or latency | maxmemory, eviction, and INFO | [Memory and monitoring](#memory-and-monitoring) |
| Choose availability or key distribution | Replication, Sentinel, and Cluster | [Scope of each mechanism](#replication-sentinel-and-cluster) |
| Restrict commands and connections | ACL, socket permissions, and TLS | [Access](#access-and-security) |

| Item | Details |
| --- | --- |
| Level | Advanced. The first examples also require the local setup. |
| Prerequisites | Redis 8.2 and familiarity with networks, files, permissions, and recovery requirements |

<a id="учебный-экземпляр"></a>
## Practice instance

The data, caching, and messaging examples require REDIS_URL and use a random `cheatsheet:{id}:` namespace.
The backup examples create their own processes. See [RDB setup](backup-and-restore.md#setup) or [AOF setup](aof-backup-and-restore.md#setup).
The examples delete only the keys they create.
They require no FLUSHDB or FLUSHALL.
Use a dedicated process with synthetic data.
Keep your running system service separate.

After installing Redis, open a separate terminal.
Create a temporary directory.
Start a foreground process with a Unix socket, TCP disabled, and persistence disabled.
This complete shell example creates temporary files and leaves system service settings untouched.

```bash
umask 077
redis_demo_dir="$(mktemp -d)"
printf 'Practice Redis socket: %s/redis.sock\n' "$redis_demo_dir"
redis-server --port 0 --unixsocket "$redis_demo_dir/redis.sock" --unixsocketperm 700 \
  --save "" --appendonly no --dir "$redis_demo_dir"
```

Wait for the process to become ready.
In another terminal, set REDIS_URL using the **printed** path.
Use the form `unix:///absolute/path/redis.sock?db=0` and substitute the actual path.
Check PING, for example with `redis-cli -s /absolute/path/redis.sock PING` using that path.
The expected reply is PONG.
After finishing, stop this foreground process with Ctrl-C.
Persistence is disabled, so its data disappear on shutdown.
Use this setup for practice.

<a id="сохранность-и-восстановление"></a>
## Durability and recovery

| Mechanism | Purpose | What to check |
| --- | --- | --- |
| RDB | Snapshot of the data | Changes since the latest snapshot can be lost. Check fork and disk resources and restore the file in a separate process. |
| AOF | Write log | Check appendfsync, disk errors, rewrites, and multipart AOF. With everysec, a failure can lose roughly the latest second of writes. |
| RDB + AOF | Combines persistence methods | Check which files Redis loads on startup and how to back up every required file |
| Replication | Copy for reads and availability | Usually asynchronous. Failover can lose acknowledged writes. |
| Backup stored outside the instance | Recovery after deletion or failure | Separate storage, access controls, retention, and regular restore tests |

MULTI/EXEC does not automatically enable AOF or fsync.
WAIT waits for replica acknowledgments.
`WAIT` does not guarantee strong consistency. Acknowledged writes can still be lost in some failures.
Replicas also reproduce accidental deletions.
Keep an independent backup.
To verify a backup, restore it in a separate instance with a compatible version and check application data.

<a id="создать-и-восстановить-rdb-копию"></a>
## Create and restore an RDB backup

Use RDB for a point-in-time backup and verify it in a separate Redis instance.
RDB is a data snapshot file. TTL is the time a key has left before expiration.

Create the snapshot, wait for completion, and copy the finished file.
Load it in a new instance with a separate directory and AOF disabled.

The outline shows the steps in the [standalone program](backup-and-restore.md#complete-example).

```text
Source: BGSAVE → wait for completion using INFO persistence and check for status ok
Backup: copy the completed dump.rdb to backup.rdb
Restore: place backup.rdb as dump.rdb in a new directory before starting Redis
Verify: compare values, PEXPIRETIME, and remaining PTTL
```

`PEXPIRETIME` returns the absolute expiration time. `PTTL` returns the remaining time in milliseconds.
The snapshot values are restored, the TTL decreases during downtime, and expired keys are absent.
The backup contains the state at snapshot time.
Restoration preserves the original expiration times.

Do not use this procedure to replace the RDB file of a running Redis instance.
Wait for BGSAVE to finish before copying the file.
RDB and AOF require different restore procedures.
See [setup, versions, and the single-file program](backup-and-restore.md#setup).

<a id="создать-и-восстановить-aof-копию"></a>
## Create and restore an AOF backup

Use this approach to restore from an AOF log when a short source shutdown is acceptable.
AOF logs write operations that Redis replays on startup.
The manifest lists the parts. BASE contains the initial state, and INCR contains later changes.

Finish the AOF rewrite and shut down the source cleanly.
Copy the entire `appenddirname` directory into the new instance's directory before starting it.
Set `appendonly yes` on the destination.

The outline shows the steps in the [standalone program](aof-backup-and-restore.md#complete-example).

```text
Source: finish BGREWRITEAOF → write updates to INCR → SHUTDOWN NOSAVE
Backup: copy the entire appendonlydir, including the manifest, BASE, and INCR
Restore: load the copied files with appendonly yes
Verify: compare data, absolute expiration, and remaining TTL
```

On a clean shutdown, `SHUTDOWN NOSAVE` flushes AOF without creating a separate RDB snapshot.
The restored database contains both the initial data and changes from INCR.
The original expiration time remains in effect.
A key that expired during downtime is absent.

Restore the complete AOF file set, including the manifest and INCR files.
This procedure requires the source to be stopped after the rewrite finishes.
Use a separate procedure to back up a running Redis instance.
See [file composition, setup, and the complete program](aof-backup-and-restore.md).

<a id="память-и-наблюдение"></a>
## Memory and monitoring

Set maxmemory with headroom for overhead, persistence, and replication.
Choose an eviction policy for your workload.
When memory runs out, noeviction rejects some writes.
allkeys-lru and allkeys-lfu evict keys.
The volatile policies select only keys with an expiration time.
Track expiration and eviction separately.
Large values and commands that return large results increase latency.
Limit pipeline size.

Use these Redis commands individually for inspection.

```text
INFO server
INFO memory
INFO persistence
INFO replication
INFO stats
SLOWLOG GET 5
LATENCY DOCTOR
```

Monitor evicted_keys, expired_keys, cache hits and misses, latency, memory, AOF and RDB status, and replica lag.
Some diagnostic commands require privileges and prior configuration.
SLOWLOG can contain command arguments.
Restrict access to it.
UNLINK removes the key and defers freeing the value's memory.

<a id="репликация-sentinel-и-cluster"></a>
## Replication, Sentinel, and Cluster

Sentinel monitors replication and coordinates failover.
Redis Cluster distributes keys across 16384 hash slots and requires a client that supports redirects.
A hash tag inside braces colocates related keys.
Multi-key operations and transactions usually require a single slot.
Cluster uses database 0.
SELECT cannot separate tenants into different Cluster databases.
Adding a shard leaves each individual large or hot key on one shard.

<a id="доступ-и-безопасность"></a>
## Access and security

Restrict network and socket access.
Configure ACLs even when protected mode is enabled.
In production, use separate ACL users with the minimum command categories and key or channel patterns.
AUTH sends credentials over the connection. Use TLS to encrypt remote connections and verify certificates.
Keep secrets out of published URLs, commands, and logs.
A caching application needs no administrative CONFIG, DEBUG, SHUTDOWN, or FLUSH* commands or access to other applications' keys.
Use access controls as the security boundary between clients.

<a id="источники"></a>
## Sources

- [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [WAIT](https://redis.io/docs/latest/commands/wait/).
- [Eviction](https://redis.io/docs/latest/develop/reference/eviction/), [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/).
- [Security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/), [TLS](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/).
