import os
import pathlib
import psutil
import socket
import sys
import time

from datetime import datetime, timedelta

from plotmanager.library.parse.configuration import get_config_info
from plotmanager.library.utilities.configuration import test_configuration
from plotmanager.library.utilities.exceptions import ManagerError, TerminationException
from plotmanager.library.utilities.jobs import load_jobs
from plotmanager.library.utilities.log import analyze_log_dates, check_log_progress, analyze_log_times
from plotmanager.library.utilities.notifications import send_notifications
from plotmanager.library.utilities.print import print_view, print_json
from plotmanager.library.utilities.processes import is_windows, get_manager_processes, get_running_plots, \
    start_process, identify_drive, get_system_drives


def start_manager():
    if get_manager_processes():
        raise ManagerError('Manager is already running.')

    directory = pathlib.Path().resolve()
    stateless_manager_path = os.path.join(directory, 'stateless-manager.py')
    if not os.path.exists(stateless_manager_path):
        raise FileNotFoundError('Failed to find stateless-manager.')
    debug_log_file_path = os.path.join(directory, 'debug.log')
    debug_log_file = open(debug_log_file_path, 'a')
    python_file_path = sys.executable

    chia_location, log_directory, config_jobs, manager_check_interval, max_concurrent, max_for_phase_1, \
        minimum_minutes_between_jobs, progress_settings, notification_settings, debug_level, view_settings, \
        instrumentation_settings, backend = get_config_info()

    load_jobs(config_jobs)

    test_configuration(chia_location=chia_location, notification_settings=notification_settings,
                       instrumentation_settings=instrumentation_settings)

    extra_args = []
    if is_windows():
        pythonw_file_path = '\\'.join(python_file_path.split('\\')[:-1] + ['pythonw.exe'])
    else:
        pythonw_file_path = '\\'.join(python_file_path.split('\\')[:-1] + ['python &'])
        extra_args.append('&')
    if os.path.exists(pythonw_file_path):
        python_file_path = pythonw_file_path

    args = [python_file_path, stateless_manager_path] + extra_args
    start_process(args=args, log_file=debug_log_file)
    time.sleep(3)
    if not get_manager_processes():
        raise ManagerError('Failed to start Manager. Please look at debug.log for more details on the error. It is in the same folder as manager.py.')

    send_notifications(
        title='Plot manager started',
        body=f'Plot Manager has started on {socket.gethostname()}...',
        settings=notification_settings,
    )
    print('Plot Manager has started...')


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


def json_output():
    chia_location, log_directory, config_jobs, manager_check_interval, max_concurrent, max_for_phase_1, \
        minimum_minutes_between_jobs, progress_settings, notification_settings, debug_level, view_settings, \
        instrumentation_settings, backend = get_config_info()

    system_drives = get_system_drives()

    drives = {'temp': [], 'temp2': [], 'dest': []}
    jobs = load_jobs(config_jobs)
    for job in jobs:
        directories = {
            'temp': job.temporary_directory,
            'dest': job.destination_directory,
            'temp2': job.temporary2_directory,
        }
        for key, directory_list in directories.items():
            if directory_list is None:
                continue
            if not isinstance(directory_list, list):
                directory_list = [directory_list]
            for directory in directory_list:
                drive = identify_drive(file_path=directory, drives=system_drives)
                if drive in drives[key]:
                    continue
                drives[key].append(drive)

    running_work = {}

    jobs = load_jobs(config_jobs)
    jobs, running_work = get_running_plots(jobs=jobs, running_work=running_work,
                                           instrumentation_settings=instrumentation_settings, backend=backend)
    check_log_progress(jobs=jobs, running_work=running_work, progress_settings=progress_settings,
                       notification_settings=notification_settings, view_settings=view_settings,
                       instrumentation_settings=instrumentation_settings, backend=backend)
    print_json(jobs=jobs, running_work=running_work, view_settings=view_settings, backend=backend)

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
    exit()


def view(loop=True):
    chia_location, log_directory, config_jobs, manager_check_interval, max_concurrent, max_for_phase_1, \
        minimum_minutes_between_jobs, progress_settings, notification_settings, debug_level, view_settings, \
        instrumentation_settings, backend = get_config_info()
    view_check_interval = view_settings['check_interval']
    system_drives = get_system_drives()
    analysis = {'files': {}}
    drives = {'temp': [], 'temp2': [], 'dest': []}
    jobs = load_jobs(config_jobs)
    for job in jobs:
        directories = {
            'dest': job.destination_directory,
            'temp': job.temporary_directory,
            'temp2': job.temporary2_directory,
        }
        for key, directory_list in directories.items():
            if directory_list is None:
                continue
            if not isinstance(directory_list, list):
                directory_list = [directory_list]
            for directory in directory_list:
                drive = identify_drive(file_path=directory, drives=system_drives)
                if drive in drives[key]:
                    continue
                drives[key].append(drive)

    while True:
        running_work = {}
        try:
            analysis = analyze_log_dates(log_directory=log_directory, analysis=analysis)
            jobs = load_jobs(config_jobs)
            jobs, running_work = get_running_plots(jobs=jobs, running_work=running_work,
                                                   instrumentation_settings=instrumentation_settings, backend=backend)
            check_log_progress(jobs=jobs, running_work=running_work, progress_settings=progress_settings,
                               notification_settings=notification_settings, view_settings=view_settings,
                               instrumentation_settings=instrumentation_settings, backend=backend)
            print_view(jobs=jobs, running_work=running_work, analysis=analysis, drives=drives,
                       next_log_check=datetime.now() + timedelta(seconds=view_check_interval),
                       view_settings=view_settings, loop=loop, backend=backend)
            if not loop:
                break
            time.sleep(view_check_interval)
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
                system_args = ['python'] + sys.argv
                os.execv(sys.executable, system_args)
        except KeyboardInterrupt:
            print("Stopped view.")
            exit()


def analyze_logs():
    chia_location, log_directory, config_jobs, manager_check_interval, max_concurrent, max_for_phase_1, \
        minimum_minutes_between_jobs, progress_settings, notification_settings, debug_level, view_settings, \
        instrumentation_settings, backend = get_config_info()
    analyze_log_times(log_directory, backend)
