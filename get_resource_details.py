#!/usr/bin/env python3

import json
import psutil

def get_system_info():
    info = {}
    info['cpu'] = psutil.cpu_percent(interval=1, percpu=True)
    info['memory'] = psutil.virtual_memory()._asdict()
    info['disk'] = psutil.disk_usage('/')._asdict()
    info['filesystems'] = [dict(device=part.device, usage=psutil.disk_usage(part.mountpoint)._asdict()) for part in psutil.disk_partitions(all=True)]

    processes = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'memory_info']):
        try:
            with p.oneshot():
                proc_info = p.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent'])
                proc_info['rss'] = p.memory_info().rss
                proc_info['vms'] = p.memory_info().vms
                processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    info['top_cpu'] = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:6]
    info['top_mem'] = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:6]
    info['top_swap'] = sorted(processes, key=lambda p: p['vms'], reverse=True)[:6]

    return info

if __name__ == "__main__":
    print(json.dumps(get_system_info()))
