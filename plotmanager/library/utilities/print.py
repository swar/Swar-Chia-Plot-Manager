import os
import psutil
import json

from datetime import datetime, timedelta

from plotmanager.library.utilities.processes import get_manager_processes

def _get_row_info(pid, running_work, view_settings, as_raw_values=False):
    work = running_work[pid]
    phase_times = work.phase_times
    elapsed_time = (datetime.now() - work.datetime_start)
    elapsed_seconds = elapsed_time.seconds
    est_overall_time = 10000/float(work.progress)*elapsed_seconds/100
    est_overall_time_h = int(est_overall_time/3600)
    est_overall_time_m = int((est_overall_time - est_overall_time_h*3600)/60)
    if est_overall_time_h <10 :
        est_overall_time_h = str('0'+str(est_overall_time_h))
    if est_overall_time_m <10 :
        est_overall_time_m = str('0'+str(est_overall_time_m))
    est_overall_time_str = str(str(est_overall_time_h)+':'+str(est_overall_time_m))
    est_remain = est_overall_time - elapsed_time.seconds
    est_remain_h = int(est_remain/3600)
    est_remain_m = int((est_remain - est_remain_h*3600)/60)
    if est_remain_h <10 :
        est_remain_h = str('0'+str(est_remain_h))
    if est_remain_m <10 :
        est_remain_m = str('0'+str(est_remain_m))
    est_remain_str = str(str(est_remain_h)+':'+str(est_remain_m))
    elapsed_time = pretty_print_time(elapsed_time.seconds + elapsed_time.days * 86400)
    phase_time_log = []
    plot_id_prefix = ''
    if work.plot_id:
        plot_id_prefix = work.plot_id[0:7]
    for i in range(1, 5):
        if phase_times.get(i):
            phase_time_log.append(phase_times.get(i))

    row = [
        work.job.name if work.job else '?',
        work.k_size,
        plot_id_prefix,
        pid,
        pretty_print_bytes(work.temp_file_size, 'gb', 0, " GiB"),
        work.datetime_start.strftime(view_settings['datetime_format']),
        est_overall_time_str,
        elapsed_time,
        est_remain_str,
        work.current_phase,
        ' / '.join(phase_time_log),
        work.progress+'%',
           ]
    if not as_raw_values:
        return [str(cell) for cell in row]
    return row

    
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

    headers = "   ".join([cell.center(max_characters[i]) for i, cell in enumerate(rows[0])])
    separator = '=' * (sum(max_characters) + 3 * len(max_characters))
    console = [separator, headers, separator]
    for row in rows[1:]:
        console.append("   ".join([cell.ljust(max_characters[i]) for i, cell in enumerate(row)]))
    console.append(separator)
    return "\n".join(console)


def get_job_data(jobs, running_work, view_settings, as_json=False):
    rows = []
    added_pids = []
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                continue
            rows.append(_get_row_info(pid, running_work, view_settings, as_json))
            added_pids.append(pid)
    for pid in running_work.keys():
        if pid in added_pids:
            continue
        rows.append(_get_row_info(pid, running_work, view_settings, as_json))
        added_pids.append(pid)
    rows.sort(key=lambda x: (x[5]), reverse=True)
    for i in range(len(rows)):
        rows[i] = [str(i+1)] + rows[i]
    if as_json:
        jobs = dict(jobs=rows)
        print(json.dumps(jobs, separators=(',', ':')))
        return jobs
    return rows


def pretty_print_job_data(job_data):
    headers = ['num', 'job', 'k', 'plot_id', 'pid', 'temp_size', 'start', 'overall', 'elapsed_time', 'remaining', 'phase', 'phase_times', 'progress']
    rows = [headers] + job_data
    return pretty_print_table(rows)


def get_drive_data(drives, running_work, job_data):
    headers = ['type', 'drive', 'used', 'total', '%', '#', 'temp', 'dest']
    rows = []

    pid_to_num = {}
    for job in job_data:
        pid_to_num[job[4]] = job[0]

    drive_types = {}
    has_temp2 = False
    for drive_type, all_drives in drives.items():
        for drive in all_drives:
            if drive in drive_types:
                drive_type_list = drive_types[drive]
            else:
                drive_type_list = ['-', '-', '-']
            if drive_type == 'temp':
                drive_type_list[0] = 't'
            elif drive_type == 'temp2':
                has_temp2 = True
                drive_type_list[1] = '2'
            elif drive_type == 'dest':
                drive_type_list[2] = 'd'
            else:
                raise Exception(f'Invalid drive type: {drive_type}')
            drive_types[drive] = drive_type_list

    checked_drives = []
    for all_drives in drives.values():
        for drive in all_drives:
            if drive in checked_drives:
                continue
            checked_drives.append(drive)
            temp, temp2, dest = [], [], []
            for job in running_work:
                if running_work[job].temporary_drive == drive:
                    temp.append(pid_to_num[str(running_work[job].pid)])
                if running_work[job].temporary2_drive == drive:
                    temp2.append(pid_to_num[str(running_work[job].pid)])
                if running_work[job].destination_drive == drive:
                    dest.append(pid_to_num[str(running_work[job].pid)])

            try:
                usage = psutil.disk_usage(drive)
            except (FileNotFoundError, TypeError):
                continue

            counts = ['-', '-', '-']
            if temp:
                counts[0] = str(len(temp))
            if temp2:
                counts[1] = str(len(temp2))
            if dest:
                counts[2] = str(len(dest))
            if not has_temp2:
                del counts[1]
                del drive_types[drive][1]
            drive_type = '/'.join(drive_types[drive])
            if usage.percent>90:
                color = "\u001b[31;1m "
            else: 
                if usage.percent>75:
                    color = "\u001b[0m\u001b[33;1m "
                else:
                    color = "\u001b[m\u001b[0m "
            row = [
                f'{color}{drive_type}',
                drive,
                f'{pretty_print_bytes(usage.used, "tb", 2, "TiB")}',
                f'{pretty_print_bytes(usage.total, "tb", 2, "TiB")}',
                f'{usage.percent}%',
                '/'.join(counts),
                '/'.join(temp),
                '/'.join(dest)+"\u001b[0m",
            ]
            if has_temp2:
                row.insert(-1, '/'.join(temp2))
            rows.append(row)
    if has_temp2:
        headers.insert(-1, 'temp2')
    rows = [headers] + rows
    return pretty_print_table(rows)


def print_json(jobs, running_work, view_settings):
    get_job_data(jobs=jobs, running_work=running_work, view_settings=view_settings, as_json=True)


def print_view(jobs, running_work, analysis, drives, next_log_check, view_settings, loop):
    # Job Table
    job_data = get_job_data(jobs=jobs, running_work=running_work, view_settings=view_settings)

    # Drive Table
    drive_data = ''
    if view_settings.get('include_drive_info'):
        drive_data = get_drive_data(drives, running_work, job_data)

    manager_processes = get_manager_processes()

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(pretty_print_job_data(job_data))
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
        print(f'Plots Completed Yesterday: {analysis["summary"].get(datetime.now().date() - timedelta(days=1), 0)}')
        print(f'Plots Completed Today: {analysis["summary"].get(datetime.now().date(), 0)}')
        print()
    if loop:
        print(f"Next log check at {next_log_check.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
