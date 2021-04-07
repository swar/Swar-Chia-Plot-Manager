from datetime import datetime
from termcolor import cprint, colored

# Let's get us a file we can send to a webserver with the statuses
printStatusFile = True #TODO: move to config file

# define our clear screen function
def clear():
  
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        
def statusFile(content):
    text_file = open("plotstatus.txt", "w") #TODO: move to config file
    n = text_file.write(content)
    text_file.close()

def pretty_print_time(seconds):
    total_minutes, second = divmod(seconds, 60)
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02}:{minute:02}:{second:02}"

def print_table(jobs, running_work, next_log_check, stop_plotting):
    statuses = []
    headers = ['job', 'wid', 'pid', 'start', 'elapsed_time', 'current', 'phase1', 'phase2', 'phase3', 'phase4', 'progress']
    statuses.append(headers)
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                continue
            work = running_work[pid]
            phase_times = work.phase_times
            elapsed_time = (datetime.now() - work.datetime_start)
            elapsed_time = pretty_print_time(elapsed_time.seconds)
            row = [job.name, work.work_id, pid, work.datetime_start.strftime('%Y-%m-%d %H:%M:%S'), elapsed_time,
                   work.current_phase, phase_times.get(1, ''), phase_times.get(2, ''), phase_times.get(3, ''),
                   phase_times.get(4, ''), work.progress]
            statuses.append([str(cell) for cell in row])

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
    
    clear() #clear screen before print
    
    print("\n".join(console))
    
    if printStatusFile == True: # If enabled, create text file suitable for sending to webserver
        statusFile("\n".join(console))
        
    print(f"Next log check at {next_log_check.strftime('%Y-%m-%d %H:%M:%S')}")
    if stop_plotting:
        cprint(f"Plotting has been disabled", 'red')
    print()
