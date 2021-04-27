import logging
import os
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
            if not re.search(r'^pythonw?(?:\d+\.\d+|\d+)?(?:\.exe)?$', process.name(), flags=re.I):
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


def get_plot_directories(commands):
    try:
        temporary_index = commands.index('-t') + 1
        destination_index = commands.index('-d') + 1
    except ValueError:
        return None, None, None
    try:
        temporary2_index = commands.index('-2') + 1
    except ValueError:
        temporary2_index = None
    temporary_directory = commands[temporary_index]
    destination_directory = commands[destination_index]
    temporary2_directory = None
    if temporary2_index:
        temporary2_directory = commands[temporary2_index]
    return temporary_directory, temporary2_directory, destination_directory


def get_plot_drives(commands, drives=None):
    if not drives:
        drives = get_system_drives()
    temporary_directory, temporary2_directory, destination_directory = get_plot_directories(commands=commands)
    temporary_drive = identify_drive(file_path=temporary_directory, drives=drives)
    destination_drive = identify_drive(file_path=destination_directory, drives=drives)
    temporary2_drive = None
    if temporary2_directory:
        temporary2_drive = identify_drive(file_path=temporary2_directory, drives=drives)
    return temporary_drive, temporary2_drive, destination_drive


def get_chia_drives():
    drive_stats = {'temp': {}, 'temp2': {}, 'dest': {}}
    chia_executable_name = get_chia_executable_name()
    for process in psutil.process_iter():
        if process.name() != chia_executable_name:
            continue
        if 'plots' not in process.cmdline() or 'create' not in process.cmdline():
            continue
        commands = process.cmdline()
        temporary_drive, temporary2_drive, destination_drive = get_plot_drives(commands=commands)
        if not temporary_drive and not destination_drive:
            continue

        if temporary_drive not in drive_stats['temp']:
            drive_stats['temp'][temporary_drive] = 0
        drive_stats['temp'][temporary_drive] += 1
        if destination_drive not in drive_stats['dest']:
            drive_stats['dest'][destination_drive] = 0
        drive_stats['dest'][destination_drive] += 1
        if temporary2_drive:
            if temporary2_drive not in drive_stats['temp2']:
                drive_stats['temp2'][temporary2_drive] = 0
            drive_stats['temp2'][temporary2_drive] += 1

    return drive_stats


def get_system_drives():
    drives = []
    for disk in psutil.disk_partitions():
        drive = disk.mountpoint
        if is_windows():
            drive = os.path.splitdrive(drive)[0]
        drives.append(drive)
    drives.sort(reverse=True)
    return drives


def identify_drive(file_path, drives):
    for drive in drives:
        if drive not in file_path:
            continue
        return drive
    return None


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
        log_file_path = None
        temp_file_size = 0
        for file in process.open_files():
            temp_file_size += os.path.getsize(file.path)
            if '.mui' == file.path[-4:]:
                continue
            if file.path[-4:] not in ['.log', '.txt']:
                continue
            log_file_path = file.path
            logging.info(f'Found log file: {log_file_path}')
        assumed_job = None
        logging.info(f'Finding associated job')

        temporary_directory, temporary2_directory, destination_directory = get_plot_directories(commands=process.cmdline())
        for job in jobs:
            if temporary_directory != job.temporary_directory:
                continue
            if destination_directory not in job.destination_directory:
                continue
            if temporary2_directory and temporary2_directory not in job.temporary2_directory:
                continue
            logging.info(f'Found job: {job.name}')
            assumed_job = job
            break

        temporary_drive, temporary2_drive, destination_drive = get_plot_drives(commands=process.cmdline())
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
        work.temporary_drive = temporary_drive
        work.temporary2_drive = temporary2_drive
        work.destination_drive = destination_drive
        work.temp_file_size = temp_file_size

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
