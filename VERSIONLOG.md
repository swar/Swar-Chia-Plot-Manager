# Version Log
The version log history will be kept in this file.

### v.0.1.0b
**THIS BRANCH IS CURRENTLY IN DEVELOPMENT!** The first feature packed improvement of the plot manager.

#### New Features
- Adding `exclude_final_directory` as an option in the `config.yaml`. ([#35](https://github.com/swar/Swar-Chia-Plot-Manager/pull/35))
- Skipping `manager.log` as a file and renaming to `debug.log`. ([#38](https://github.com/swar/Swar-Chia-Plot-Manager/pull/38))
- Added destination directory skipping when a drive is full. It will calculate size of total running plots and the predicted size of the new plot prior to making that judgement. ([#36](https://github.com/swar/Swar-Chia-Plot-Manager/pull/36), [#193](https://github.com/swar/Swar-Chia-Plot-Manager/pull/193))
- Added list support for temporary directories. This will cycle through all temporary directories in the order that they are listed for a job. ([#150](https://github.com/swar/Swar-Chia-Plot-Manager/pull/150), [#153](https://github.com/swar/Swar-Chia-Plot-Manager/pull/153/files), [#182](https://github.com/swar/Swar-Chia-Plot-Manager/pull/182))
- Added CPU affinity support on the job level. This allows you to select and dedicate specific threads to your jobs. ([#134](https://github.com/swar/Swar-Chia-Plot-Manager/pull/134), [#281](https://github.com/swar/Swar-Chia-Plot-Manager/pull/281))
- Added process priority levels on the job level. This allows you to set the priority levels to whatever you choose. Some people want low priority, while others want higher priorities. ([#282](https://github.com/swar/Swar-Chia-Plot-Manager/pull/282))
- Added an option to delay a job by a set number of minutes. If you started manager and there is a stagger for the job, it will use the initial delay only if it is longer than the stagger. ([#283](https://github.com/swar/Swar-Chia-Plot-Manager/pull/283)) 
- Added an option in `manager.py` to spit out a single instance of the view using the `status` argument as well as `json` format of the jobs. ([#300](https://github.com/swar/Swar-Chia-Plot-Manager/pull/300), [#374](https://github.com/swar/Swar-Chia-Plot-Manager/pull/374))
- Added support for Telegram notifications. ([#316](https://github.com/swar/Swar-Chia-Plot-Manager/pull/316), [#364](https://github.com/swar/Swar-Chia-Plot-Manager/pull/364))
- Added support for instrumentation using Prometheus ([#87](https://github.com/swar/Swar-Chia-Plot-Manager/pull/87), [#196](https://github.com/swar/Swar-Chia-Plot-Manager/pull/196))

#### Changes
- Switching notification imports to a separate requirements file and turning them into lazy imports. ([#159](https://github.com/swar/Swar-Chia-Plot-Manager/pull/159), [196](https://github.com/swar/Swar-Chia-Plot-Manager/pull/196))
- Reworked the Drives Table in the view to include associated jobs. This includes minor tweaks to the display to remove ambiguity such as renaming plots to "#". ([#191](https://github.com/swar/Swar-Chia-Plot-Manager/pull/191), [#368](https://github.com/swar/Swar-Chia-Plot-Manager/pull/368))

#### Bug Fixes
- Fixed a bug where `max_plots` was not working properly. It was counting running plots when you restarted manager. Now it will only count new plots kicked off.
- Fixed a bug in elpased_time column where elapsed days greater than 24 hours were resulting in calculations being off by a day. ([#190](https://github.com/swar/Swar-Chia-Plot-Manager/pull/190))  
- Skipping processes that result in an `AccessDenied` error when finding manager processes. ([#147](https://github.com/swar/Swar-Chia-Plot-Manager/pull/147)) 
- Fixed a bug where psutil going stale on Linux users was not allowing the script to restart on its own. ([#197](https://github.com/swar/Swar-Chia-Plot-Manager/pull/197))
- Fixed a bug where NFS drives weren't being identified. ([#284](https://github.com/swar/Swar-Chia-Plot-Manager/pull/284))
- Removed the hardcoded next log check date in the view.

### v0.0.1
This is the initial public release of the plot manager with additional bug fixes to account for edge cases on various operating systems.


### Alpha
This is the initial version of the plot manager that was privately used by me.