### Resources monitoring

`export RTMA_SENSOR`

Configure monitoring via `config.json` with the following fields:

- `interval`: the interval between usage statistics reports in seconds
    - default: `1`
    
- `cpu_times_fields`: CPU times percentage. Every attribute represents the seconds the CPU has spent in the given mode within time interval
    - `system` - processes in kernel mode
    - `user` - processes in user mode
    - `nice` - niced (prioritized) processes in user mode
    - `idle` - doing nothing
    - `iowait` - waiting fot I/O to complete
    - `irq` - hardware interrupts
    - `softirq` - software interrupts
    - `steal` - other OS running in virtualized env
    - `guest` - virtual CPU for guest OS
    - `guest_nice` - niced guest
    - default: `["system", "user", "nice", "idle", "iowait"]`
    
- `cpu_freq`: CPU current frequency
    - default: `false`
    
- `cpu_percpu`: whether to display `cpu_times_fields` and `cpu_freq` per each logical CPU or not
    - default: `false`

- `net_conn_fields`: socket connections
    - `fd` - socket file descriptor
    - `laddr` - local address as a (ip, port)
    - `raddr` - remote address as a (ip, port)
    - `status` - status of TCP connection
    - `pid` - PID of process opened the socket
    - default: `["fd", "laddr", "raddr", "pid"]`

- `net_conn_statuses`: statuses of socket connections to display
    - available: `ESTABLISHED, SYN_SENT, SYN_RECV, FIN_WAIT1, FIN_WAIT2, TIME_WAIT, CLOSE, CLOSE_WAIT, LAST_ACK, LISTEN, CLOSING, NONE`
    - default: `["ESTABLISHED"]`

- `net_io_fields`: amount of (sent, received) data
    - `bytes` - bytes (sent, received)
    - `drops` - drops while (sending, receiving)
    - default: `["bytes"]`
    
- `net_pernic`: whether to display `net_io_fields` per each network interface card or not
    - default: `false`

- `mem_usage_fields`: system memory usage
    - `used` - memory used
    - `buffers` - memory for things like FS metadata
    - `cached` - memory cached
    - `shared` - memory shared among multiple processes
    - default: `["used", "cached", "shared"]`
    
- `swp_usage_fields`: system swap usage
    - `used` - used swap 
    - default: `["used"]`
    
- `dsk_usage_fields`: disk usage
    - `used` - used disk memory
    - `read` - read speed
    - `write` - write speed
    - default: `["used", "read", "write"]`

- `dsk_perdisk`: whether to display read/write speed per each disk or not
    - default: `false`
