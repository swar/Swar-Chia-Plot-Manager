import logging
import platform
import psutil
import re
import subprocess

from copy import deepcopy
from datetime import datetime

from plotmanager.library.utilities.objects import Work


def _contains_in_list(string, lst, case_insensitive=False):
    if case_insensitive:
        string = string.lower()
    for item in lst:
        if case_insensitive:
            item = item.lower()
        if string not in item:
            continue
        return True
    return False


def get_manager_processes():
    processes = []
    for process in psutil.process_iter():
        try:
            if not re.search(r'^pythonw?(?:\d+\.\d+)?(?:\.exe)?$', process.name(), flags=re.I):
                continue
            if not _contains_in_list('python', process.cmdline(), case_insensitive=True) or \
                    not _contains_in_list('stateless-manager.py', process.cmdline()):
                continue
            processes.append(process)
        except psutil.NoSuchProcess:
            pass
    return processes


def is_windows():
    return platform.system() == 'Windows'


def get_chia_executable_name():
    return f'chia{".exe" if is_windows() else ""}'


def get_chia_drives():
    drive_stats = {'temp': {}, 'dest': {}}
    chia_executable_name = get_chia_executable_name()
    for process in psutil.process_iter():
        if process.name() != chia_executable_name:
            continue
        if 'plots' not in process.cmdline() or 'create' not in process.cmdline():
            continue
        commands = process.cmdline()
        try:
            temp_index = commands.index('-t') + 1
            dest_index = commands.index('-d') + 1
        except ValueError:
            continue
        temp_drive = commands[temp_index].split('\\')[0]
        dest_drive = commands[dest_index].split('\\')[0]
        if temp_drive not in drive_stats['temp']:
            drive_stats['temp'][temp_drive] = 0
        drive_stats['temp'][temp_drive] += 1
        if dest_drive not in drive_stats['dest']:
            drive_stats['dest'][dest_drive] = 0
        drive_stats['dest'][dest_drive] += 1
    return drive_stats


def get_running_plots(jobs, running_work):
    chia_processes = []
    logging.info(f'Getting running plots')
    chia_executable_name = get_chia_executable_name()
    for process in psutil.process_iter():
        if process.name() != chia_executable_name:
            continue
        if 'plots' not in process.cmdline() or 'create' not in process.cmdline():
            continue
        logging.info(f'Found chia plotting process: {process.pid}')
        datetime_start = datetime.fromtimestamp(process.create_time())
        chia_processes.append([datetime_start, process])
    chia_processes.sort(key=lambda x: (x[0]))

    for datetime_start, process in chia_processes:
        logging.info(f'Finding log file for process: {process.pid}')
        drives = []
        log_file_path = None
        for file in process.open_files():
            if '.mui' == file.path[-4:]:
                continue
            if file.path[-4:] not in ['.log', '.txt']:
                drives.append(file.path[0])
                continue
            log_file_path = file.path
            logging.info(f'Found log file: {log_file_path}')
        drives = list(set(drives))
        assumed_job = None
        logging.info(f'Finding associated job')
        for job in jobs:
            if job.temporary_directory[0] not in drives:
                continue
            logging.info(f'Found job: {job.name}')
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
    logging.info(f'Finished finding running plots')

    return jobs, running_work


def start_process(args, log_file):
    kwargs = {}
    if is_windows():
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
