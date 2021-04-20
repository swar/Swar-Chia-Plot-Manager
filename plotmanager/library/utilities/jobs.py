import psutil

from copy import deepcopy
from datetime import datetime, timedelta

from plotmanager.library.commands import plots
from plotmanager.library.utilities.processes import start_process
from plotmanager.library.utilities.objects import Job, Work
from plotmanager.library.utilities.log import get_log_file_name

import platform

def has_active_jobs_and_work(jobs):
    for job in jobs:
        if job.total_completed < job.max_plots:
            return True
    return False


def get_destination_directory(job):
    if isinstance(job.destination_directory, list):
        return job.destination_directory[(job.total_completed + job.total_running) % len(job.destination_directory)]

    return job.destination_directory


def load_jobs(config_jobs):
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

    return jobs


def monitor_jobs_to_start(jobs, running_work, max_concurrent, next_job_work, chia_location, log_directory, next_log_check):
    for i, job in enumerate(jobs):
        if len(running_work.values()) >= max_concurrent:
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

    return jobs, running_work, next_job_work, next_log_check


def start_work(job, chia_location, log_directory):

    niceval = 5
    if platform.system() == 'Windows':
         niceval = psutil.REALTIME_PRIORITY_CLASS

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
    process = start_process(args=plot_command, log_file=log_file)
    pid = process.pid
    
    psutil.Process(pid).nice(niceval)

    work.pid = pid
    job.total_running += 1
    job.running_work = job.running_work + [pid]

    return job, work
