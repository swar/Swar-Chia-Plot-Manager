import os
import psutil
import json
import requests
import threading
import time
import logging

from datetime import datetime, timedelta
from requests.exceptions import HTTPError
from plotmanager.library.parse.configuration import get_config_info
from plotmanager.library.utilities.jobs import load_jobs
from plotmanager.library.utilities.log import analyze_log_dates, check_log_progress
from plotmanager.library.utilities.processes import get_running_plots, identify_drive, get_system_drives
from plotmanager.library.utilities.print import _get_row_info

chia_location, log_directory, config_jobs, manager_check_interval, max_concurrent, max_for_phase_1, \
minimum_minutes_between_jobs, progress_settings, notification_settings, debug_level, view_settings, \
instrumentation_settings, dashboard_settings, backend = get_config_info()


def dashboard_thread():
    newThread = threading.Thread(target=update_dashboard, args=())
    newThread.start()


def update_dashboard():
    while True:
        analysis = {'files': {}}
        running_work = {}
        system_drives = get_system_drives()
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

        analysis = analyze_log_dates(log_directory=log_directory, analysis=analysis)
        jobs, running_work = get_running_plots(jobs=jobs, running_work=running_work,
                                               instrumentation_settings=instrumentation_settings, backend=backend)
        check_log_progress(jobs=jobs, running_work=running_work, progress_settings=progress_settings,
                           notification_settings=notification_settings, view_settings=view_settings,
                           instrumentation_settings=instrumentation_settings, backend=backend)
        job_data = get_job_data(jobs=jobs, running_work=running_work, backend=backend)
        drive_data = get_drive_data(drives)
        dashboard_request(plots=job_data, drives=drive_data, analysis=analysis)
        time.sleep(60)  # setting this too low can cause problems. recommended 60


def get_job_data(jobs, running_work, backend='chia'):
    rows = []
    added_pids = []
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                continue
            rows.append(_get_row_info(pid, running_work, backend))
            added_pids.append(pid)
    for pid in running_work.keys():
        if pid in added_pids:
            continue
        rows.append(_get_row_info(pid, running_work, backend))
        added_pids.append(pid)
    rows.sort(key=lambda x: (float(x[7][:-1])), reverse=True)
    for i in range(len(rows)):
        rows[i] = [str(i + 1)] + rows[i]
    return rows


def _get_row_info(pid, running_work, backend='chia'):
    work = running_work[pid]
    phase_times = work.phase_times
    elapsed_time = (datetime.now() - work.datetime_start)
    phase_time_log = []
    for i in range(1, 5):
        if phase_times.get(i):
            phase_time_log.append(phase_times.get(i))

    row = [
        work.job.name if work.job else '?',
        work.k_size,
        pid,
        work.datetime_start,
        elapsed_time,
        work.current_phase,
        ' / '.join(phase_time_log),
        work.progress
    ]

    return [str(cell) for cell in row]


def get_drive_data(drives):
    rows = []
    drive_types = {}
    for drive_type, all_drives in drives.items():
        for drive in all_drives:
            if drive in drive_types:
                drive_type_list = drive_types[drive]
            else:
                drive_type_list = ""
            if drive_type == 'temp' or drive_type == 'temp2':
                drive_type_list = 't'
            elif drive_type == 'dest':
                drive_type_list = 'd'
            else:
                drive_type_list = '-'
            drive_types[drive] = drive_type_list

    checked_drives = []
    for all_drives in drives.values():
        for drive in all_drives:
            if drive in checked_drives:
                continue
            checked_drives.append(drive)
            try:
                usage = psutil.disk_usage(drive)
            except (FileNotFoundError, TypeError):
                continue
            drive_type = drive_types[drive]
            if os.path.basename(drive) != "":
                drive = os.path.basename(drive)
            row = [
                drive,
                drive_type,
                usage.used,
                usage.total,
                usage.percent
            ]
            rows.append(row)
    return rows


def set_dashboard_data(plots):
    data = []
    for plot in plots:
        arr = {
            "id": plot[3],
            "startedAt": plot[4],
            "state": "RUNNING",
            "kSize": plot[2],
            "phase": plot[6],
            "progress": float(plot[8].strip('%')) / 100
        }
        data.append(arr)
    return data


def set_drive_data(drives):
    data = []
    for drive in drives:
        arr = {
            "letter": drive[0],
            "type": drive[1],
            "used": drive[2],
            "total": drive[3],
            "percent": drive[4]
        }
        data.append(arr)
    return data


def dashboard_request(plots, drives, analysis):
    ram_usage = psutil.virtual_memory()
    data = {
        "plotter": {
            "cpu": str(round(psutil.cpu_percent())) + "%",
            "ram": str(round(ram_usage.percent)) + "%",
            "completedPlotsToday": analysis["summary"].get(datetime.now().date(), 0),
            "completedPlotsYesterday": analysis["summary"].get(datetime.now().date() - timedelta(days=1), 0),
            "jobs": set_dashboard_data(plots),
            "drives": set_drive_data(drives)
        }
    }
    data = json.dumps(data)
    url = dashboard_settings.get('dashboard_update_url')
    headers = {
        'Authorization': "Bearer " + dashboard_settings.get('dashboard_api_key'),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.patch(url + '/api/satellite', headers=headers, data=data)
        if response.status_code == 204:
            dashboard_status = "[Dashboard] Connected"
            logging.info(dashboard_status)
        elif response.status_code == 429:
            dashboard_status = "[Dashboard] Too many Requests. Slow down."
            logging.error(dashboard_status + str(response))
        else:
            response.raise_for_status()
    except HTTPError:
        if response.status_code == 401:
            dashboard_status = "[Dashboard] Unauthorized. Possibly invalid API key?"
            logging.error(dashboard_status + str(response))
        else:
            dashboard_status = "[Dashboard] Unable to connect."
            logging.error(dashboard_status + str(response))
    except requests.exceptions.ConnectionError:
        dashboard_status = "[Dashboard] Connection Error. Chiadashboard.com may not be responding."
        logging.error(dashboard_status)
    return dashboard_status
