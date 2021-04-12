import os
import psutil
import subprocess


def _contains_in_list(string, lst):
    for item in lst:
        if string not in item:
            continue
        return True
    return False


def get_manager_processes():
    processes = []
    for process in psutil.process_iter():
        try:
            if process.name() not in ['python.exe', 'pythonw.exe']:
                continue
            if not _contains_in_list('python', process.cmdline()) or \
                    not _contains_in_list('stateless-manager.py', process.cmdline()):
                continue
            processes.append(process)
        except psutil.NoSuchProcess:
            pass
    return processes


def start_process(args, log_file):
    kwargs = {}
    if 'nt' == os.name:
        flags = 0
        flags |= 0x00000008
        kwargs = {
            'creationflags': flags,
        }
    process = subprocess.Popen(
        args=args,
        stdout=log_file,
        stderr=log_file,
        shell=False,
        **kwargs,
    )
    return process
