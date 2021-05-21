import argparse

from plotmanager.library.utilities.exceptions import InvalidArgumentException
from plotmanager.library.utilities.commands import start_manager, stop_manager, view, json_output, analyze_logs


parser = argparse.ArgumentParser(description='This is the central manager for Swar\'s Chia Plot Manager.')

help_description = '''
There are a few different actions that you can use: "start", "restart", "stop", "view", "status", "json", and 
"analyze_logs". "start" will start a manager process. If one already exists, it will display an error message. 
"restart" will try to kill any existing manager and start a new one. "stop" will terminate the manager, but all 
existing plots will be completed. "view" can be used to display an updating table that will show the progress of your 
plots. Once a manager has started it will always be running in the background unless an error occurs. This field is 
case-sensitive.

"analyze_logs" is a helper command that will scan all the logs in your log_directory to get your custom settings for
the progress settings in the YAML file.
'''

parser.add_argument(
    dest='action',
    type=str,
    help=help_description,
)

args = parser.parse_args()

if args.action == 'start':
    start_manager()
elif args.action == 'restart':
    stop_manager()
    start_manager()
elif args.action == 'stop':
    stop_manager()
elif args.action == 'view':
    view()
elif args.action == 'json':
    json_output()
elif args.action == 'status':
    view(loop=False)
elif args.action == 'analyze_logs':
    analyze_logs()
else:
    error_message = 'Invalid action provided. The valid options are "start", "restart", "stop", "view", "status", "json" and ' \
                    '"analyze_logs".'
    raise InvalidArgumentException(error_message)
