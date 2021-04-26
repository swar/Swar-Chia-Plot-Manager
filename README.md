# SWAR Chia Plot Manager 
This is a plot manager for Chia (http://chia.net)

Installation:
On Windows use 'python3', on Linux use 'python'

- Create a new python environment: `python -m venv /path/to/new/virtual/environment`
- Activate environment: Linux:  `. .\venv\Scripts\activate` Windows: `venv\bin\activate` 
- Install required modules: `pip install -r requirements.txt`
- Rename `config.yaml.DEFAULT` to `config.yaml`
- Edit and setup `config.yaml`
- Edit `plotter/parse/configuration.py` to set config file location
- Edit `log.py` to enable Discord/Sound notifications
- Run Plot Manager: `python manager.py start`
- Run View mode:  `python manager.py view`
- 
Configuration:
	`config.yaml` settings explained in config file.
