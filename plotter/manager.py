import dateparser
import json
import os
import psutil
import re
import subprocess
import time

from copy import deepcopy
from datetime import datetime, timedelta
from termcolor import cprint, colored


from plotter.commands import plots
from plotter.parse.configuration import get_config_info
from plotter.utilities.objects import Job, Work


def pretty_print_time(seconds):
    total_minutes, second = divmod(seconds, 60)
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02}:{minute:02}:{second:02}"


def jobs_to_do(jobs):
    for job in jobs:
        if job.total_completed < job.max_plots:
            return True
    return False


def get_log_file_name(log_directory, job, datetime):
    return os.path.join(log_directory, f'{job.name}_{str(datetime).replace(" ", "_").replace(":", "_").replace(".", "_")}.log')


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


def get_destination_directory(job):
    if isinstance(job.destination_directory, list):
        return job.destination_directory[(job.total_completed + job.total_running) % len(job.destination_directory)]

    return job.destination_directory


def start_work(job, chia_location, log_directory):
    now = datetime.now()
    log_file_path = get_log_file_name(log_directory, job, now)
    destination_directory = get_destination_directory(job)

    work = deepcopy(Work())
    work.job = job
    work.log_file = log_file_path
    work.datetime_start = now
    work.work_id = job.current_work_id

    job.current_work_id += 1

    plot_command = plots.create(
        chia_location=chia_location,
        size=job.size,
        memory_buffer=job.memory_buffer,
        temporary_directory=job.temporary_directory,
        destination_directory=destination_directory,
        threads=job.threads,
        buckets=job.buckets,
        bitfield=job.bitfield,
        temporary2_directory=None
    )

    log_file = open(log_file_path, 'a')
    process = subprocess.Popen(
        args=plot_command,
        stdout=log_file,
        stderr=log_file,
    )
    pid = process.pid
    psutil.Process(pid).nice(psutil.REALTIME_PRIORITY_CLASS)

    # THIS IS JUST TEST CODE
    # import random
    # pid = random.randint(1, 1000000)
    # work.log_file = random.choice([r'S:\logs\plotter\fake.log', r'S:\logs\plotter\fake2.log'])

    work.pid = pid
    job.total_running += 1
    job.running_work = job.running_work + [pid]

    return job, work


chia_location, log_directory, config_jobs, log_check_seconds = get_config_info()

job_log = {}
jobs = []
for info in config_jobs:
    job = deepcopy(Job())
    job.total_running = 0

    job.name = info['name']
    job.max_plots = info['max_plots']

    job.max_concurrent = info['max_concurrent']
    job.max_concurrent_with_disregard = info['max_concurrent_with_disregard']
    job.max_for_phase_1 = info['max_for_phase_1']
    job.stagger_minutes = info.get('stagger_minutes', None)
    job.max_for_phase_1 = info.get('max_for_phase_1', None)
    job.concurrency_disregard_phase = info.get('concurrency_disregard_phase', None)
    job.concurrency_disregard_phase_delay = info.get('concurrency_disregard_phase_delay', None)

    job.temporary_directory = info['temporary_directory']
    job.destination_directory = info['destination_directory']

    job.size = info['size']
    job.bitfield = info['bitfield']
    job.threads = info['threads']
    job.buckets = info['buckets']
    job.memory_buffer = info['memory_buffer']
    jobs.append(job)


next_plot = {}

next_log_check = datetime.now()
next_job_work = {}

running_work = {}

override_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'OVERRIDE.json')
stop_plotting = False
while jobs_to_do(jobs):
    if not stop_plotting and os.path.exists(override_file_path):
        f = open(override_file_path, 'r')
        contents = f.read()
        f.close()
        try:
            override = json.loads(contents)
        except:
            override = {}
        stop_plotting = override.get('stop_plotting', False)

    # CHECK LOGS
    # CHECKING FOR DELETED WORK
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

        job = None
        for job in jobs:
            if job.name != work.job.name:
                continue
            if pid in job.running_work:
                job.running_work.remove(pid)
            job.total_running -= 1
            job.total_completed += 1
            break
        del running_work[pid]

    next_log_check = datetime.now() + timedelta(seconds=log_check_seconds)

    # DETERMINE IF JOB NEEDS TO START
    for i, job in enumerate(jobs):
        if stop_plotting:
            continue
        phase_1_count = 0
        for pid in job.running_work:
            if running_work[pid].current_phase > 1:
                continue
            phase_1_count += 1
        if job.max_for_phase_1 and phase_1_count >= job.max_for_phase_1:
            continue
        if job.total_completed >= job.max_plots:
            continue
        if job.name in next_job_work and next_job_work[job.name] > datetime.now():
            continue
        discount_running = 0
        if job.concurrency_disregard_phase is not None:
            for pid in job.running_work:
                work = running_work[pid]
                if work.current_phase < job.concurrency_disregard_phase:
                    continue
                if datetime.now() <= (work.phase_dates[job.concurrency_disregard_phase - 1] + timedelta(minutes=job.concurrency_disregard_phase_delay)):
                    continue
                discount_running += 1
        if (job.total_running - discount_running) >= job.max_concurrent:
            continue
        if job.total_running >= job.max_concurrent_with_disregard:
            continue
        if job.stagger_minutes:
            next_job_work[job.name] = datetime.now() + timedelta(minutes=job.stagger_minutes)
        if job.max_concurrent == job.total_running:
            pass
        job, work = start_work(job=job, chia_location=chia_location, log_directory=log_directory)
        jobs[i] = deepcopy(job)
        next_log_check = datetime.now()
        running_work[work.pid] = work

    # DETERMINE RUNNING PROCESSES
    # TODO: Check Running Processes
    # TODO: Audit and count running work to minus 1 so job can kick off again.
    statuses = []
    headers = ['job', 'wid', 'pid', 'start', 'elapsed_time', 'current', 'phase1', 'phase2', 'phase3', 'phase4', 'progress']
    statuses.append(headers)
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                pprint(f'Missing pid - {pid}')
                continue
            work = running_work[pid]
            phase_times = work.phase_times
            elapsed_time = (datetime.now() - work.datetime_start)
            elapsed_time = pretty_print_time(elapsed_time.seconds)
            row = [job.name, work.work_id, pid, work.datetime_start.strftime('%Y-%m-%d %H:%M:%S'), elapsed_time, work.current_phase, phase_times.get(1, ''), phase_times.get(2, ''), phase_times.get(3, ''), phase_times.get(4, ''), work.progress]
            statuses.append([str(cell) for cell in row])

    max_characters = [0 for cell in statuses[0]]
    for row in statuses:
        for i, cell in enumerate(row):
            length = len(cell)
            if len(cell) <= max_characters[i]:
                continue
            max_characters[i] = length

    headers = "   ".join([colored(cell.center(max_characters[i]), 'blue') for i, cell in enumerate(statuses[0])])
    separator = colored('=', 'green') * (sum(max_characters) + 3 * len(max_characters))
    console = [separator, headers, separator]
    for row in statuses[1:]:
        console.append("   ".join([colored(cell.ljust(max_characters[i]), 'blue') for i, cell in enumerate(row)]))
    console.append(separator)
    print("\n".join(console))
    cprint(f"Next log check at {next_log_check.strftime('%Y-%m-%d %H:%M:%S')}", 'blue')
    if stop_plotting:
        cprint(f"Plotting has been disabled", 'red')
    print()

    time.sleep(log_check_seconds)
