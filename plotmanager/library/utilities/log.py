import dateparser
import os
import psutil
import re

from plotmanager.library.utilities.print import pretty_print_time


def get_log_file_name(log_directory, job, datetime):
    return os.path.join(log_directory, f'{job.name}_{str(datetime).replace(" ", "_").replace(":", "_").replace(".", "_")}.log')


def _analyze_log_file(contents):
    match = re.search(r'total time = ([\d\.]+) seconds\. CPU \([\d\.]+%\) [A-Za-z]+\s([^\n]+)\n', contents, flags=re.I)
    if not match:
        return False
    total_seconds, date_raw = match.groups()
    total_seconds = pretty_print_time(int(float(total_seconds)))
    parsed_date = dateparser.parse(date_raw)
    return dict(
        total_seconds=total_seconds,
        date=parsed_date,
    )


def _get_summary(analysis):
    summary = analysis.get('summary', {})
    for file_path in analysis['files'].keys():
        if analysis['files'][file_path]['checked']:
            continue
        analysis['files'][file_path]['checked'] = True
        end_date = analysis['files'][file_path]['data']['date'].date()
        if end_date not in summary:
            summary[end_date] = 0
        summary[end_date] += 1
    analysis['summary'] = summary
    return analysis


def analyze_logs(log_directory, analysis):
    files = os.listdir(log_directory)
    for file in files:
        file_path = os.path.join(log_directory, file)
        if file_path in analysis['files']:
            continue
        f = open(file_path, 'r')
        contents = f.read()
        f.close()
        if 'Total time = ' not in contents:
            continue
        data = _analyze_log_file(contents)
        if data is None:
            continue
        analysis['files'][file_path] = {'data': data, 'checked': False}
    analysis = _get_summary(analysis)
    return analysis


def get_phase_info(contents):
    phase_times = {}
    phase_dates = {}

    for phase in range(1, 5):
        match = re.search(rf'time for phase {phase} = ([\d\.]+) seconds\. CPU \([\d\.]+%\) [A-Za-z]+\s([^\n]+)\n', contents, flags=re.I)
        # match = re.search(rf'time for phase {phase} = ([\d\.]+) seconds', contents, flags=re.I)
        if match:
            seconds, date_raw = match.groups()
            phase_times[phase] = pretty_print_time(int(float(seconds)))
            parsed_date = dateparser.parse(date_raw)
            phase_dates[phase] = parsed_date

    return phase_times, phase_dates


def get_progress(line_count):
    progress = 0
    if line_count > 801:
        progress += 32.9
    else:
        progress += 32.9 * (line_count / 801)
        return progress
    if line_count > 835:
        progress += 19.6
    else:
        progress += 19.6 * ((line_count - 801) / (835 - 801))
        return progress
    if line_count > 1957:
        progress += 44
    else:
        progress += 44 * ((line_count - 835) / (1933 - 835))
        return progress
    if line_count > 2112:
        progress += 3.5
    else:
        progress += 3.5 * ((line_count - 1933) / (2089 - 1933))
    return progress


def check_log_progress(jobs, running_work):
    for pid, work in list(running_work.items()):
        f = open(work.log_file, 'r')
        data = f.read()
        f.close()

        line_count = (data.count('\n') + 1)

        progress = get_progress(line_count)

        phase_times, phase_dates = get_phase_info(data)
        current_phase = 1
        if phase_times:
            current_phase = max(phase_times.keys()) + 1
        work.phase_times = phase_times
        work.phase_dates = phase_dates
        work.current_phase = current_phase
        work.progress = f'{progress:.4f}%'

        if psutil.pid_exists(pid) and 'renamed final file from ' not in data:
            continue

        for job in jobs:
            if job.name != work.job.name:
                continue
            if pid in job.running_work:
                job.running_work.remove(pid)
            job.total_running -= 1
            job.total_completed += 1
            break
        del running_work[pid]
