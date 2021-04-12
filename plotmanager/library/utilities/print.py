import os

from datetime import datetime

from plotmanager.library.utilities.processes import get_manager_processes


def _get_row_info(pid, running_work):
    work = running_work[pid]
    phase_times = work.phase_times
    elapsed_time = (datetime.now() - work.datetime_start)
    elapsed_time = pretty_print_time(elapsed_time.seconds)
    row = [work.job.name if work.job else '?', pid, work.datetime_start.strftime('%Y-%m-%d %H:%M:%S'),
           elapsed_time, work.current_phase, phase_times.get(1, ''), phase_times.get(2, ''), phase_times.get(3, ''),
           phase_times.get(4, ''), work.progress]
    return [str(cell) for cell in row]


def pretty_print_time(seconds):
    total_minutes, second = divmod(seconds, 60)
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02}:{minute:02}:{second:02}"


def print_table(jobs, running_work, next_log_check, stop_plotting):
    statuses = []
    headers = ['num', 'job', 'pid', 'start', 'elapsed_time', 'current', 'phase1', 'phase2', 'phase3', 'phase4', 'progress']
    added_pids = []
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                continue
            statuses.append(_get_row_info(pid, running_work))
            added_pids.append(pid)
    for pid in running_work.keys():
        if pid in added_pids:
            continue
        statuses.append(_get_row_info(pid, running_work))
        added_pids.append(pid)
    statuses.sort(key=lambda x: (x[3]), reverse=True)
    for i in range(len(statuses)):
        statuses[i] = [str(i+1)] + statuses[i]
    statuses = [headers] + statuses

    max_characters = [0 for cell in statuses[0]]
    for row in statuses:
        for i, cell in enumerate(row):
            length = len(cell)
            if len(cell) <= max_characters[i]:
                continue
            max_characters[i] = length

    headers = "   ".join([cell.center(max_characters[i]) for i, cell in enumerate(statuses[0])])
    separator = '=' * (sum(max_characters) + 3 * len(max_characters))
    console = [separator, headers, separator]
    for row in statuses[1:]:
        console.append("   ".join([cell.ljust(max_characters[i]) for i, cell in enumerate(row)]))
    console.append(separator)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print("\n".join(console))
    print(f'Manager Status: {"Running" if get_manager_processes() else "Stopped"}')
    print()
    print(f"Next log check at {next_log_check.strftime('%Y-%m-%d %H:%M:%S')}")
    if stop_plotting:
        print("Plotting has been disabled...")
    print()
