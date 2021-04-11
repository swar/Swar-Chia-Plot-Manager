import psutil

from copy import deepcopy
from datetime import datetime

from plotmanager.library.utilities.objects import Work


def get_running_chia_processes(jobs, running_work):
    chia_processes = []
    for process in psutil.process_iter():
        if process.name() != 'chia.exe':
            continue
        datetime_start = datetime.fromtimestamp(process.create_time())
        chia_processes.append([datetime_start, process])
    chia_processes.sort(key=lambda x: (x[0]))

    for datetime_start, process in chia_processes:
        drives = []
        log_file_path = None
        for file in process.open_files():
            if '.mui' == file.path[-4:]:
                continue
            if '.log' != file.path[-4:]:
                drives.append(file.path[0])
                continue
            log_file_path = file.path
        drives = list(set(drives))
        assumed_job = None
        for job in jobs:
            if job.temporary_directory[0] not in drives:
                continue
            assumed_job = job
            break

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
        running_work[work.pid] = work

    return jobs, running_work
