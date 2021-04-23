import os
import psutil
import re
import subprocess

from copy import deepcopy
from datetime import datetime

from plotmanager.library.utilities.objects import Work


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
            if not re.search(r'^pythonw?(?:\d+\.\d+)?\.exe$', process.name()):
                continue
            if not _contains_in_list('python', process.cmdline()) or \
                    not _contains_in_list('stateless-manager.py', process.cmdline()):
                continue
            processes.append(process)
        except psutil.NoSuchProcess:
            pass
    return processes


def get_chia_drives():
    drive_stats = {'temp': {}, 'tmp2': {}, 'dest': {}}
    for process in psutil.process_iter():
        if process.name() != 'chia.exe':
            continue
        if 'plots' not in process.cmdline() or 'create' not in process.cmdline():
            continue
        commands = process.cmdline()
        try:
            tmp2_index = commands.index('-2') + 1
            temp_index = commands.index('-t') + 1
            dest_index = commands.index('-d') + 1
        except ValueError:
            try:
                temp_index = commands.index('-t') + 1
                dest_index = commands.index('-d') + 1
            except ValueError:
                continue

        temp_drive = commands[temp_index].split('\\')[0]
        if temp_drive not in drive_stats['temp']:
            drive_stats['temp'][temp_drive] = 0
        drive_stats['temp'][temp_drive] += 1


        try:
            tmp2_drive = commands[tmp2_index].split('\\')[0]
            if tmp2_drive not in drive_stats['tmp2']:
                drive_stats['tmp2'][tmp2_drive] = 0
            drive_stats['tmp2'][tmp2_drive] += 1
        except:
            continue

        dest_drive = commands[dest_index].split('\\')[0]
        if dest_drive not in drive_stats['dest']:
            drive_stats['dest'][dest_drive] = 0
        drive_stats['dest'][dest_drive] += 1

    return drive_stats


def get_running_plots(jobs, running_work):
    chia_processes = []
    for process in psutil.process_iter():
        if process.name() != 'chia.exe':
            continue
        if 'plots' not in process.cmdline() or 'create' not in process.cmdline():
            continue
        datetime_start = datetime.fromtimestamp(process.create_time())
        chia_processes.append([datetime_start, process])
    chia_processes.sort(key=lambda x: (x[0]))

    for datetime_start, process in chia_processes:
        drives = []
        log_file_path = None
        for file in process.open_files():
            if '.mui' == file.path[-4:]:
                continue
            if file.path[-4:] not in ['.log', '.txt']:
                drives.append(file.path[0])
                continue
            log_file_path = file.path
        drives = list(set(drives))
        assumed_job = None
        for job in jobs:
            if job.temporary_directory[0] not in drives:
                continue
            assumed_job = job
            break

        work = deepcopy(Work())
        work.job = assumed_job
        work.log_file = log_file_path
        work.datetime_start = datetime_start
        work.pid = process.pid
        work.work_id = '?'
        if assumed_job:
            work.work_id = assumed_job.current_work_id
            assumed_job.current_work_id += 1
            assumed_job.total_running += 1
            assumed_job.running_work = assumed_job.running_work + [process.pid]
        running_work[work.pid] = work

        try:
            commands = process.cmdline()
            tmp2 = commands[commands.index('-2') + 1].split('\\')[0]
            tmp = commands[commands.index('-t') + 1].split('\\')[0]
            dst = commands[commands.index('-d') + 1].split('\\')[0]
            work.working_drives = ' ' + tmp + ' ' + tmp2 + ' ' + dst
        except ValueError:
            try:
                tmp = commands[commands.index('-t') + 1].split('\\')[0]
                dst = commands[commands.index('-d') + 1].split('\\')[0]
                work.working_drives = ' ' + tmp + '    ' + dst
            except ValueError:
                work.working_drives = '    ?'
                continue

    return jobs, running_work


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
