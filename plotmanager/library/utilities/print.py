import os
import psutil
import json
import requests

from datetime import datetime, timedelta
from requests.exceptions import HTTPError
from plotmanager.library.utilities.processes import get_manager_processes, get_chia_drives


def _get_row_info(pid, running_work, view_settings):
    work = running_work[pid]
    phase_times = work.phase_times
    elapsed_time = (datetime.now() - work.datetime_start)
    elapsed_time = pretty_print_time(elapsed_time.seconds)
    phase_time_log = []
    for i in range(1, 5):
        if phase_times.get(i):
            phase_time_log.append(phase_times.get(i))

    row = [
        work.job.name if work.job else '?',
        work.k_size,
        pid,
        work.datetime_start.strftime(view_settings['datetime_format']),
        elapsed_time,
        work.current_phase,
        ' / '.join(phase_time_log),
        work.progress,
        pretty_print_bytes(work.temp_file_size, 'gb', 0, " GiB"),
    ]
    return [str(cell) for cell in row]


def pretty_print_bytes(size, size_type, significant_digits=2, suffix=''):
    if size_type.lower() == 'gb':
        power = 3
    elif size_type.lower() == 'tb':
        power = 4
    else:
        raise Exception('Failed to identify size_type.')
    calculated_value = round(size / (1024 ** power), significant_digits)
    calculated_value = f'{calculated_value:.{significant_digits}f}'
    return f"{calculated_value}{suffix}"


def pretty_print_time(seconds, include_seconds=True):
    total_minutes, second = divmod(seconds, 60)
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02}:{minute:02}{f':{second:02}' if include_seconds else ''}"


def pretty_print_table(rows):
    max_characters = [0 for cell in rows[0]]
    for row in rows:
        for i, cell in enumerate(row):
            length = len(cell)
            if len(cell) <= max_characters[i]:
                continue
            max_characters[i] = length

    headers = "   ".join([cell.center(max_characters[i])
                         for i, cell in enumerate(rows[0])])
    separator = '=' * (sum(max_characters) + 3 * len(max_characters))
    console = [separator, headers, separator]
    for row in rows[1:]:
        console.append("   ".join(
            [cell.ljust(max_characters[i]) for i, cell in enumerate(row)]))
    console.append(separator)
    return "\n".join(console)


def get_job_data(jobs, running_work, view_settings, completed_plots_today, completed_plots_yesterday):
    dashboard_response = ""
    rows = []
    headers = ['num', 'job', 'k', 'pid', 'start', 'elapsed_time',
               'phase', 'phase_times', 'progress', 'temp_size']
    added_pids = []
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                continue
            rows.append(_get_row_info(pid, running_work, view_settings))
            added_pids.append(pid)
    for pid in running_work.keys():
        if pid in added_pids:
            continue
        rows.append(_get_row_info(pid, running_work, view_settings))
        added_pids.append(pid)
    rows.sort(key=lambda x: (x[4]), reverse=True)
    for i in range(len(rows)):
        rows[i] = [str(i+1)] + rows[i]
    if view_settings.get('update_dashboard'):
        dashboard_response = chia_dashboard(plots=rows, completed_plots_today=completed_plots_today,
                                            completed_plots_yesterday=completed_plots_yesterday, view_settings=view_settings)
    rows = [headers] + rows
    return pretty_print_table(rows), dashboard_response


def get_drive_data(drives):
    chia_drives = get_chia_drives()
    headers = ['type', 'drive', 'used', 'total', 'percent', 'plots']
    rows = [headers]
    for drive_type, drives in drives.items():
        for drive in drives:
            try:
                usage = psutil.disk_usage(drive)
            except FileNotFoundError:
                continue
            rows.append([drive_type, drive, f'{pretty_print_bytes(usage.used, "tb", 2, "TiB")}',
                         f'{pretty_print_bytes(usage.total, "tb", 2, "TiB")}', f'{usage.percent}%',
                         str(chia_drives[drive_type].get(drive, '?'))])
    return pretty_print_table(rows)


def chia_dashboard(plots, completed_plots_today, completed_plots_yesterday, view_settings):
    data = {
        "plotter": {
            "completedPlotsToday": completed_plots_today,
            "completedPlotsYesterday": completed_plots_yesterday,
            "jobs": chia_dashboard_data(plots)
        }
    }
    data = json.dumps(data)
    url = "https://chia-dashboard-api.foxypool.io/api/satellite"
    headers = {
        'Authorization': "Bearer " + view_settings.get('dashboard_api_key'),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.patch(url, headers=headers, data=data)
        if response.status_code == 204 or response.status_code == 429:
            dashboard_status = "Connected"
        else:
            response.raise_for_status()
    except HTTPError as e:
        if e.response.status_code == 401:
            dashboard_status = "Unauthorized. Possibly invalid API key?"
        else:
            dashboard_status = "Disconnected"
    return dashboard_status


def chia_dashboard_data(plots):
    data = []
    for plot in plots:
        arr = {
            "id": plot[3],
            "startedAt": plot[4],
            "state": "RUNNING",
            "kSize": plot[2],
            "phase": plot[6],
            "progress": float(plot[8].strip('%'))/100
        }
        data.append(arr)
    return data


def print_view(jobs, running_work, analysis, drives, next_log_check, view_settings):
    # Job Table
    completed_plots_yesterday = analysis["summary"].get(
        datetime.now().date() - timedelta(days=1), 0)
    completed_plots_today = analysis["summary"].get(datetime.now().date(), 0)
    job_data = get_job_data(jobs=jobs, running_work=running_work, view_settings=view_settings,
                            completed_plots_yesterday=completed_plots_yesterday, completed_plots_today=completed_plots_today)

    # Drive Table
    drive_data = ''
    if view_settings.get('include_drive_info'):
        drive_data = get_drive_data(drives)

    manager_processes = get_manager_processes()

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(job_data[0])
    print(f'Manager Status: {"Running" if manager_processes else "Stopped"}')
    print()

    if view_settings.get('include_drive_info'):
        print(drive_data)
    if view_settings.get('include_cpu'):
        print(f'CPU Usage: {psutil.cpu_percent()}%')
    if view_settings.get('include_ram'):
        ram_usage = psutil.virtual_memory()
        print(f'RAM Usage: {pretty_print_bytes(ram_usage.used, "gb")}/{pretty_print_bytes(ram_usage.total, "gb", 2, "GiB")}'
              f'({ram_usage.percent}%)')
    print()
    if view_settings.get('include_plot_stats'):
        print(f'Plots Completed Yesterday: {str(completed_plots_yesterday)}')
        print(f'Plots Completed Today: {str(completed_plots_today)}')
        print()
    if view_settings.get('update_dashboard'):
        print(
            f'Chia Dashboard: {job_data[1]} (https://dashboard.chia.foxypool.io/)')
    print()
    print(f"Next log check at {next_log_check.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
