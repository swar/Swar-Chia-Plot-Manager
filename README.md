# Swar's Chia Plot Manager 

#### A plot manager for Chia plotting: https://www.chia.net/

##### Development Version: v0.0.1

This is a cross-platform Chia Plot Manager that will work on the major operating systems. This is not a plotter. The purpose of this library is to manage your plotting and kick off new plots with the settings that you configure. Everyone's system is unique so customization is an important feature that was engraved into this library.

## Installation

The installation of this library is straightforward. I have attached detailed instructions below that should help you get started. 

1. Download and Install Python 3.7 or higher: https://www.python.org/
2. `git clone` this repo or download it.
3. Open CommandPrompt / PowerShell / Terminal and `cd` into the main library folder.
   * Example: `cd C:\Users\Swar\Documents\Swar-Chia-Plot-Manager`
4. OPTIONAL: Create a virtual environment for Python. This is recommended if you use Python for other things.
	1. Create a new python environment: `python -m venv venv`
	   * The second `venv` can be renamed to whatever you want. I prefer `venv` because it's a standard.
	2. Activate the virtual environment. This must be done *every single time* you open a new window.
	   * Example Windows: `venv\Scripts\activate`
	   * Example Linux: `./venv/bin/activate`
	3. Confirm that it has activated by seeing the `(venv)` prefix. The prefix will change depending on what you named it.
5. Install the required modules: `pip install -r requirements.txt`
6. Copy `config.yaml.DEFAULT` and name it as `config.yaml` in the same directory.
7. Edit and set up the config.yaml to your own personal settings. There is more help on this below.
8. Run the Manager: `python manager.py start`
   * This will start a process in the background that will manage plots based on your inputted settings.
9. Run the View: `python manager.py view`
   * This will loop through a view screen with details about active plots.

