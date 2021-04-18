import os
import pathlib
import psutil
import sys
import time

from datetime import datetime, timedelta

from plotmanager.library.parse.configuration import get_config_info
from plotmanager.library.utilities.exceptions import ManagerError, TerminationException
from plotmanager.library.utilities.jobs import load_jobs
from plotmanager.library.utilities.log import analyze_log_dates, check_log_progress, analyze_log_times
from plotmanager.library.utilities.print import print_view
from plotmanager.library.utilities.processes import get_manager_processes, get_running_plots, start_process


def start_manager():
    if get_manager_processes():
        raise ManagerError('Manger is already running.')

    directory = pathlib.Path().resolve()
    stateless_manager_path = os.path.join(directory, 'stateless-manager.py')
    if not os.path.exists(stateless_manager_path):
        raise FileNotFoundError('Failed to find stateless-manager.')
    manager_log_file_path = os.path.join(directory, 'manager.log')
    manager_log_file = open(manager_log_file_path, 'a')
    python_file_path = sys.executable
    pythonw_file_path = '\\'.join(python_file_path.split('\\')[:-1] + ['pythonw.exe'])
    if os.path.exists(pythonw_file_path):
        python_file_path = pythonw_file_path
    args = [python_file_path, stateless_manager_path]
    start_process(args=args, log_file=manager_log_file)
    time.sleep(3)
    if not get_manager_processes():
        raise ManagerError('Failed to start Manager.')
    print('Manager has started...')


def stop_manager():
    processes = get_manager_processes()
    if not processes:
        print("No manager processes were found.")
        return
    for process in processes:
        try:
            process.terminate()
        except psutil.NoSuchProcess:
            pass
    if get_manager_processes():
        raise TerminationException("Failed to stop manager processes.")
    print("Successfully stopped manager processes.")


def view():
    chia_location, log_directory, config_jobs, log_check_seconds, max_concurrent, progress_settings = get_config_info()
    analysis = {'files': {}}
    drives = {'temp': [], 'tmp2': [], 'dest': []}
    jobs = load_jobs(config_jobs)
    for job in jobs:
        drive = job.temporary_directory.split('\\')[0]
        if drive in drives['temp']:
            continue
        drives['temp'].append(drive)
        if isinstance(job.destination_directory, list):
            for directory in job.destination_directory:
                drive = directory.split('\\')[0]
                if drive in drives['dest']:
                    continue
                drives['dest'].append(drive)
        else:
            drive = job.destination_directory.split('\\')[0]
            if drive in drives['dest']:
                continue
            drives['dest'].append(drive)
        if isinstance(job.temporary2_directory, list):
            for directory in job.temporary2_directory:
                drive = directory.split('\\')[0]
                if drive in drives['tmp2']:
                    continue
                drives['tmp2'].append(drive)
        else:
            if job.temporary2_directory is not None:
                drive = job.temporary2_directory.split('\\')[0]
                if drive in drives['tmp2']:
                    continue
                drives['tmp2'].append(drive)

    while True:
        running_work = {}
        try:
            analysis = analyze_log_dates(log_directory=log_directory, analysis=analysis)
            jobs = load_jobs(config_jobs)
            jobs, running_work = get_running_plots(jobs=jobs, running_work=running_work)
            check_log_progress(jobs=jobs, running_work=running_work, progress_settings=progress_settings)
            print_view(jobs=jobs, running_work=running_work, analysis=analysis, drives=drives, next_log_check=datetime.now() + timedelta(seconds=60))
            time.sleep(60)
            has_file = False
            if len(running_work.values()) == 0:
                has_file = True
            for work in running_work.values():
                if not work.log_file:
                    continue
                has_file = True
                break
            if not has_file:
                print("Restarting view due to psutil going stale...")
                system_args = [f'"{sys.executable}"'] + sys.argv
                os.execv(sys.executable, system_args)
        except KeyboardInterrupt:
            print("Stopped view.")
            exit()


def analyze_logs():
    chia_location, log_directory, config_jobs, log_check_seconds, max_concurrent, progress_settings = get_config_info()
    analyze_log_times(log_directory)
