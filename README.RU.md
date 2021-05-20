# Swar's Chia Plot Manager 

#### Plot Manager для засева Chia: https://www.chia.net/
[English](README.md) / [Русский](README.RU.md)

![The view of the manager](https://i.imgur.com/hIhjXt0.png "View")

##### Development Version: v0.0.1

Это кросс-платформенный Chia Plot Manager работает на большинстве операционных систем. Это не засеиватель. Целью этой библиотеки является управление процессом вашего засева и запуск новых полей с настройками которые вы укажете. Каждая система уникальна, поэтому кастомизация является важной функцией данной библиотеки.

Эта библиотека простая, легкая в использовании, надежная в генерации новых плотов.

Эта библиотека протес тирована на Windows и Linux.


## Возможности

* Распределите засев полей так, чтобы избежать высоких накрузок на ресурсы вашего компьютера.
* Доступен список катологов назначения.
* Используйте потенциал временного хранилища по максимуму, начав новый участок раньше.
* Запускайте максимальное количество участков одновременно, избегая конкуренции полей и ограничений использования ресурсов.
* Более информативный экран активных полей.


## Спонсирование / Поддержка данной библиотеки

Эта библиотека потребовала много времени и усилий, чтобы представить ее сегодня вам. Подумайте о спонсировании или поддержке библиотеки. Это не обязательно, но скорее добрый жест.

* XCH Address: xch134evwwqkq50nnsmgehnnag4gc856ydc7ached3xxr6jdk7e8l4usdnw39t
* ETH Address: 0xf8F7BD24B94D75E54BFD9557fF6904DBE239322E
* BTC Address: 36gnjnHqkttcBiKjjAekoy68z6C3BJ9ekS
* Paypal: https://www.paypal.com/biz/fund?id=XGVS7J69KYBTY


## Техподдержка / Вопросы

Пожалуйста, не используйте GitHub issues по вопросам, касающимся ваших персональных установок. Проблемы должны описывать либо фактические ошибки в коде, либо новые идеи. На данный момент утилита уже протестирована многими людьми для Windows, Linux и Mac OS. Поэтому любые вопросы, касающиеся технической поддержки, настройки конфигурации или вещей, относящихся к вашим индивидуальным случаям использования, должны быть размещены по любой из приведенных ниже ссылок.
* Discord Server: https://discord.gg/XyvMzeQpu2
    * Официальный Discord сервер - Swar's Chia Community (Английский)
    * Также вы можете получить помощь на Discord сервере Русскоязычного Сообщества Chia (не имеет отношения к Swar). Ссылка в разделе [Перевод на Русский](#перевод-на-русский)
* Официальная группа Chia Keybase: https://keybase.io/team/chia_network.public
    * Канал #swar 
* Дискуссионная доска GitHub: https://github.com/swar/Swar-Chia-Plot-Manager/discussions


## Часто задаваемые вопросы

##### Могу ли я перезагрузить свой конфиг?
* Да, ваш конфиг может быть перезагружен с помощью команды `python manager.py restart` или вы можете остановить и запустить диспетчер снова. Обратите внимание, что будут сброшены количество ваших заданий, а также порядок каталогов temporary2 и destination.
* Обратите внимание, что если вы измените какой-либо каталог для задания, он будет мешать существующим заданиям, а `manager` и режим `view` не смогут идентифицировать старое задание. Если вы меняете каталоги заданий при наличии активных засевов, пожалуйста, измените значение `max_plots` для текущего задания на 0 и создайте отдельное задание с новыми каталогами. Я **не рекомендую** менять каталоги во время выполнения засева.

##### Если я остановлю manager, это остановит мои плоты?
* Нет. Плоты выгружаются в фоновом режиме и это не уничтожит уже существующие плоты. Если вы хотите остановить засевы, получите доступ к их PID через диспетчер задач вашей ОС  и остановите их вручную. Помните, что вам также потребуется удалить .tmp файлы. Я не могу сделать это вместо вас.

##### Как выбираются temporary2 и destination если я указываю список?
* Они выбираются по порядку. Если у вас есть две директории, первый плот выберет первую из них, второй выберет вторую, третий выберет первую директорию.

##### Что такое `temporary2_destination_sync`?
* Некоторым пользователям нравится указывать одининаковый каталог для temporary2 и destination. При включении этого параметра в качестве диска назнвчения всегда будет использоваться диск temporary2. Используя этот параметр, вы можете указать для temporary2 пустой список.

##### Какой конфиг лучше всего подходит для моего ПК?
* Пожалуйста, перешлите этот вопрос в Keybase или на вкладку Discussion.


## All Commands [Нужен перевод]

##### Example Usage of Commands
```text
> python3 manager.py start

> python3 manager.py restart

> python3 manager.py stop

> python3 manager.py view

> python3 manager.py status

> python3 manager.py analyze_logs
```

### start

This command will start the manager in the background. Once you start it, it will always be running unless all jobs have had their `max_plots` completed or there is an error. Errors will be logged in a file created `debug.log`

### stop

This command will terminate the manager in the background. It does not stop running plots, it will only stop new plots from getting created.

### restart

This command will run start and stop sequentially.

### view

This command will show the view that you can use to keep track of your running plots. This will get updated every X seconds defined by your `config.yaml`.

### status

This command will a single snapshot of the view. It will not loop.

### analyze_logs

This command will analyze all completed plot logs in your log folder and calculate the proper weights and line ends for your computer's configuration. Just populate the returned values under the `progress` section in your `config.yaml`. This only impacts the progress bar.


## Установка [Нужен перевод]

#### NOTE: If `python` does not work, please try `python3`.

Установка этой библиотеки проста. Ниже я приложил подробные инструкции, которые помогут вам начать работу.

1. Скачайте и установите Python 3.7 или новее: https://www.python.org/
2. `git clone` этот репозитарий или скачайте его.
3. Откройте Командную строку / PowerShell / Terminal и смените директорию `cd` в основную папку библиотеки.
   * Например: `cd C:\Users\Swar\Documents\Swar-Chia-Plot-Manager`
4. НЕ ОБЯЗАТЕЛЬНО: Создайте виртуальную среду для Python. Это рекомендуется, если вы используете Python для других целей.
	1. Создайте новую Python среду: `python -m venv venv`
	   * Второе `venv` можно переименовать как вам нравится. Я выбрал `venv`потому что это стандарт.
	2. Активация виртуальной среды. Это обязательно делать *каждый раз* открывая новое окно.
	   * Пример Windows: `venv\Scripts\activate`
	   * Пример Linux: `. ./venv/bin/activate` или `source ./venv/bin/activate`
	   * Пример Mac OS: `/Applications/Chia.app/Contents/Resources/app.asar.unpacked/daemon/chia`
	3. Убедитесь что появился префикс `(venv)` в подтверждение активации среды. Префикс будет меняться в зависимости от того, как вы её назвали.
5. Установите необходимые модули: `pip install -r requirements.txt`
	* If you plan on using Notifications or Prometheus then run the following to install the required modules: `pip install -r requirements-notification.txt`
6. Скопируйте `config.yaml.default` и переименуйте в `config.yaml` в той же директории.
7. Отредактируйте и настройте config.yaml на ваши персональные установки. Ниже приведена дополнительная информация по этому вопросу.
	* Вам также нужно будет добавить параметр `chia_location`! Который должен указывать на ваш исполняемый файл chia.
9. Запустите менеджер: `python manager.py start`
   * Это запустит в фоновом режиме процесс, который будет управлять плотами на основе введенных вами настроек.
10. Запустите режим просмотра: `python manager.py view`
   * Это приведет к циклическому просмотру экрана с подробными сведениями об активных участках.

## Настройка

Конфигурация этой библиотеки уникальна для каждого конечного пользователя. Файл `config.yaml` - это место, где будет находиться конфигурация.

Plot manager работает на основе идеи заданий. Каждое задание будет иметь свои собственные параметры, которые вы можете настроить и настроить. Нет двух уникальных дисков, поэтому это обеспечит гибкость для ваших собственных ограничений и требований.

### chia_location

Это одна переменная, которая должна указывать на местоположение вашего исполняемого файла chia. Это исполняемый файл блокчейна.

* Windows пример: `C:\Users\<USERNAME>\AppData\Local\chia-blockchain\app-1.1.3\resources\app.asar.unpacked\daemon\chia.exe`
* Linux пример: `/usr/lib/chia-blockchain/resources/app.asar.unpacked/daemon/chia`
* Другой Linux пример: `/home/swar/chia-blockchain/venv/bin/chia`

### manager

Эти параметры конфигурации будут использоваться только Plot Manager'ом.

* `check_interval` - Количество секунд задержки между проверками того, следует ли начинать новое задание.
* `log_level` - оставьте ERROR, чтобы записывать только когда есть ошибки. Измените на INFO, чтобы увидеть более подробные логи. Осторожно: INFO будет писать много информации.

### log

* `folder_path` - В эту папку будут сохраняться фалы логов засеивания полей.

### view

Эти настройки используются в режиме просмотра.

* `check_interval` - Количество секунд между обновлениями экрана.
* `datetime_format` - Формат datetime для отображения. Подробне про форматирование смотри: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
* `include_seconds_for_phase` - указывает включены ли секунды в время фазы.
* `include_drive_info` - указывает будет ли отображаться информация о диске.
* `include_cpu` - указывает будет ли отображаться информация о процессоре.
* `include_ram` - указывает будет ли отображаться информация об оперативной памяти.
* `include_plot_stats` - указывает будет ли отображаться статистика поля.

### notifications

Различные настройки уведомлений при запуске Plot Manager'а и когда новое поле готово.

### instrumentation [Нужен перевод]

Settings for enabling Prometheus to gather metrics.

* `prometheus_enabled` - If enabled, metrics will be gathered and an HTTP server will start up to expose the metrics for Prometheus.
* `prometheus_port` - HTTP server port.

List of Metrics Gathered

- **chia_running_plots**: A [Gauge](https://prometheus.io/docs/concepts/metric_types/#gauge) to see how many plots are currently being created.
- **chia_completed_plots**: A [Counter](https://prometheus.io/docs/concepts/metric_types/#counter) for completed plots.

### progress

* `phase_line_end` - параметр, который будет использоваться для определения того, когда заканчивается фаза. Предполагается, что этот параметр указывает на порядковый номер строки, на которой завершится фаза. Параметр используется механизмом вычисления прогресса вместе с существующим файлом журнала для вычисления процента прогресса.
* `phase_weight` - вес, который следует присвоить каждой фазе в расчетах хода выполнения. Как правило, фазы 1 и 3 являются самыми длинными фазами, поэтому они будут иметь больший вес, чем другие.

### global [Нужен перевод]
* `max_concurrent` - Максимальное количество полей, которые может засеять ваша система. Менеджер не будет паралелльно запускать больше, чем это количество участков на протяжении всего времени.
* `max_for_phase_1` - The maximum number of plots that your system can run in phase 1.
* `minimum_minutes_between_jobs` - The minimum number of minutes before starting a new plotting job, this prevents multiple jobs from starting at the exact same time. This will alleviate congestion on destination drive. Set to 0 to disable.

### job [Нужен перевод]

Each job must have unique temporary directories.

Настройки, которые будут использоваться каждым заданием. Обратите внимание, что у вас может быть несколько заданий, и каждое задание должно быть в формате YAML, чтобы оно было правильно интерпретировано. Почти все значения здесь будут переданы в исполняемый файл Chia.

Проверьте более подробную информацию о CLI Chia здесь: https://github.com/Chia-Network/chia-blockchain/wiki/CLI-Commands-Reference

* `name` - Имя задания.
* `max_plots` - Максимальное количество заданий, выполняемых за один запуск менеджера. При любом перезапуске диспетчера эта переменная будет сброшена. Он здесь только для того, чтобы помочь в краткосрочном планировании засева.
* [ОПЦИЯ]`farmer_public_key` - Ваш публичный ключ фермера. Если не указан, менеджер не будет передавать эту переменную исполняемому файлу chia, что приведет к использованию ваших ключей по умолчанию. Этот параметр необходим только в том случае, если на компьютере нет ваших учетных данных chia.
* [ОПЦИЯ]`pool_public_key` - Ваш публичный ключ пула. Аналогично как и выше. 
* `temporary_directory` - Временное место для засева. Может иметь одно или несколько значений. Обычно размещается на SSD диске. These directories must be unique from one another.
* [ОПЦИЯ]`temporary2_directory` - Может иметь одно или несколько значений. Это необязательный параметр для использования второго временного каталога засева полей Chia.
* `destination_directory` - Может иметь одно или несколько значений. Указывает на финальную директорию куда будет помещено готовое поле. Если вы укажете несколько, готовые поля будут размещаться по одному на каждый следующий диск поочереди.
* `size` - соответствует размеру поля (сложности k). Здесь вам следует указывать например 32, 33, 34, 35 и т.д.
* `bitfield` - укажите хотите ли вы использовать bitfield (битовое поле) или нет в своем засеве. Обычно следует оставить true.
* `threads` - Количество потоков которое вы хотите использовать при засеве. Только первая фаза использует более 1 потока.
* `buckets` - Число корзин для использования. Значение по умолчанию, предоставленное Chia, равно 128.
* `memory_buffer` - Объем памяти, который вы хотите выделить задаче.
* `max_concurrent` - Максимальное количество участков для этой задачи на всё время.
* `max_concurrent_with_start_early` - Максимальное количество участков для этой задачи в любой момент времени, включая фазы, которые начались раньше.
* `initial_delay_minutes` - This is the initial delay that is used when initiate the first job. It is only ever considered once. If you restart manager, it will still adhere to this value.
* `stagger_minutes` - Количество минут ожидания перед запуском следующего задания. Вы можете установить это значение равным нулю, если хотите, чтобы ваши засевы запускались немедленно, когда это позволяют одновременные ограничения
* `max_for_phase_1` - Максимальное число засевов в фазе 1 для этой задачи.
* `concurrency_start_early_phase` - Фаза, в которой вы хотите начать засеивание заранее. Рекомендуется использовать 4.
* `concurrency_start_early_phase_delay` - Максимальное количество минут ожидания до запуска нового участка при обнаружении ранней фазы запуска.
* `temporary2_destination_sync` - Представлять каталог назначения как каталог второй временный каталог. Эти два каталога будут синхронизированы, так что они всегда будут представлены как одно и то же значение.
* `exclude_final_directory` - Whether to skip adding `destination_directory` to harvester for farming. This is a Chia feature.
* `skip_full_destinations` - When this is enabled it will calculate the sizes of all running plots and the future plot to determine if there is enough space left on the drive to start a job. If there is not, it will skip the destination and move onto the next one. Once all are full, it will disable the job.
* `unix_process_priority` - UNIX Only. This is the priority that plots will be given when they are spawned. UNIX values must be between -20 and 19. The higher the value, the lower the priority of the process.
* `windows_process_priority` - Windows Only. This is the priority that plots will be given when they are spawned. Windows values vary and should be set to one of the following values:
	* 16384 `BELOW_NORMAL_PRIORITY_CLASS`
	* 32    `NORMAL_PRIORITY_CLASS`
	* 32768 `ABOVE_NORMAL_PRIORITY_CLASS`
	* 128   `HIGH_PRIORITY_CLASS`
	* 256   `REALTIME_PRIORITY_CLASS`
* `enable_cpu_affinity` - Enable or disable cpu affinity for plot processes. Systems that plot and harvest may see improved harvester or node performance when excluding one or two threads for plotting process.
* `cpu_affinity` - List of cpu (or threads) to allocate for plot processes. The default example assumes you have a hyper-threaded 4 core CPU (8 logical cores). This config will restrict plot processes to use logical cores 0-5, leaving logical cores 6 and 7 for other processes (6 restricted, 2 free).


### Перевод на Русский
Оригинальный текст на Английском языке Вы можете найти по адресу [https://github.com/swar/Swar-Chia-Plot-Manager](https://github.com/swar/Swar-Chia-Plot-Manager)
Переведено [Anton Kokarev](https://github.com/akokarev).
Об ошибках или неточностях перевода сообщайте админам Discord сервера Chia Russian Community [https://discord.gg/9vV7KRZ26Z](https://discord.gg/9vV7KRZ26Z).
Вопросы задавайте на канале #need_help.
