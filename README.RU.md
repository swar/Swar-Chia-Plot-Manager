# Swar's Chia Plot Manager 

#### Plot Manager для засева Chia: https://www.chia.net/
[English](README.md) / [Русский](README.RU.md)

![The view of the manager](https://i.imgur.com/SmMDD0Q.png "View")

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


## Support / Questions [Нужен перевод]

Please do not use GitHub issues for questions or support regarding your own personal setups. Issues should pertain to actual bugs in the code and ideas. It has been tested to work on Windows, Linux, and Mac OS by numerous people at this point. So any questions relating to tech support, configuration setup, or things pertaining to your own personal use cases should be posted at any of the links below.
* Discord Server: https://discord.gg/XyvMzeQpu2
    * This is the Official Discord Server - Swar's Chia Community 
* Official Chia Keybase Team: https://keybase.io/team/chia_network.public
    * The channel is #swar 
* GitHub Discussion Board: https://github.com/swar/Swar-Chia-Plot-Manager/discussions


## Frequently Asked Questions [Нужен перевод]

##### Can I reload my config?
* Yes, your config can be reloaded with the `python manager.py restart` command or separately you can stop and start manager again. Please note that your job counts will be reset and the temporary2 and destination directories order will be reset.
* Please note that if you change any of the directories for a job, it will mess with existing jobs and `manager` and `view` will not be able to identify the old job. If you are changing job directories while having active plots, please change the `max_plots` for the current job to 0 and make a separate job with the new directories. I **do not recommend** changing directories while plots are running.

##### If I stop manager will it kill my plots?
* No. Plots are kicked off in the background and they will not kill your existing plots. If you want to kill them, you have access to the PIDs which you can use to track them down in Task Manager (or the appropriate software for your OS) and kill them manually. Please note you will have to delete the .tmp files as well. I do not handle this for you.

##### How are temporary2 and destination selected if I have a list?
* They are chosen in order. If you have two directories the first plot will select the first one, the second the second one, and the third plot will select the first one.

##### What is `temporary2_destination_sync`?
* Some users like having the option to always have the same temporary2 and destination directory. Enabling this setting will always have temporary2 be the drive that is used as destination. You can use an empty temporary2 directory list if you are using this setting.

##### What is the best config for my setup?
* Please forward this question to Keybase or the Discussion tab.


## Установка

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
	3. Убедитесь что появился префикс `(venv)` в подтверждение активации среды. Префикс будет меняться в зависимости от того, как вы её назвали.
5. Установите необходимые модули: `pip install -r requirements.txt`
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

### progress

* `phase_line_end` - параметр, который будет использоваться для определения того, когда заканчивается фаза. Предполагается, что этот параметр указывает на порядковый номер строки, на которой завершится фаза. Параметр используется механизмом вычисления прогресса вместе с существующим файлом журнала для вычисления процента прогресса.
* `phase_weight` - вес, который следует присвоить каждой фазе в расчетах хода выполнения. Как правило, фазы 1 и 3 являются самыми длинными фазами, поэтому они будут иметь больший вес, чем другие.

### global
* `max_concurrent` - Максимальное количество полей, которые может засеять ваша система. Менеджер не будет паралелльно запускать больше, чем это количество участков на протяжении всего времени.

### job

Настройки, которые будут использоваться каждым заданием. Обратите внимание, что у вас может быть несколько заданий, и каждое задание должно быть в формате YAML, чтобы оно было правильно интерпретировано. Почти все значения здесь будут переданы в исполняемый файл Chia.

Проверьте более подробную информацию о CLI Chia здесь: https://github.com/Chia-Network/chia-blockchain/wiki/CLI-Commands-Reference

* `name` - Имя задания.
* `max_plots` - Максимальное количество заданий, выполняемых за один запуск менеджера. При любом перезапуске диспетчера эта переменная будет сброшена. Он здесь только для того, чтобы помочь в краткосрочном планировании засева.
* [ОПЦИЯ]`farmer_public_key` - Ваш публичный ключ фермера. Если не указан, менеджер не будет передавать эту переменную исполняемому файлу chia, что приведет к использованию ваших ключей по умолчанию. Этот параметр необходим только в том случае, если на компьютере нет ваших учетных данных chia.
* [ОПЦИЯ]`pool_public_key` - Ваш публичный ключ пула. Аналогично как и выше. 
* `temporary_directory` - Временное место для засева. Можно указать только одну папку. Обычно размещается на SSD диске.
* [ОПЦИЯ]`temporary2_directory` - Может иметь одно или несколько значений. Это необязательный параметр для использования второго временного каталога засева полей Chia.
* `destination_directory` - Может иметь одно или несколько значений. Указывает на финальную директорию куда будет помещено готовое поле. Если вы укажете несколько, готовые поля будут размещаться по одному на каждый следующий диск поочереди.
* `size` - соответствует размеру поля (сложности k). Здесь вам следует указывать например 32, 33, 34, 35 и т.д.
* `bitfield` - укажите хотите ли вы использовать bitfield (битовое поле) или нет в своем засеве. Обычно следует оставить true.
* `threads` - Количество потоков которое вы хотите использовать при засеве. Только первая фаза использует более 1 потока.
* `buckets` - Число корзин для использования. Значение по умолчанию, предоставленное Chia, равно 128.
* `memory_buffer` - Объем памяти, который вы хотите выделить задаче.
* `max_concurrent` - Максимальное количество участков для этой задачи на всё время.
* `max_concurrent_with_start_early` - Максимальное количество участков для этой задачи в любой момент времени, включая фазы, которые начались раньше.
* `stagger_minutes` - Количество минут ожидания перед запуском следующего задания. Вы можете установить это значение равным нулю, если хотите, чтобы ваши засевы запускались немедленно, когда это позволяют одновременные ограничения
* `max_for_phase_1` - Максимальное число засевов в фазе 1 для этой задачи.
* `concurrency_start_early_phase` - Фаза, в которой вы хотите начать засеивание заранее. Рекомендуется использовать 4.
* `concurrency_start_early_phase_delay` - Максимальное количество минут ожидания до запуска нового участка при обнаружении ранней фазы запуска.
* `temporary2_destination_sync` - Представлять каталог назначения как каталог второй временный каталог. Эти два каталога будут синхронизированы, так что они всегда будут представлены как одно и то же значение.

### Перевод на Русский
Оригинальный текст на Английском языке Вы можете найти по адресу [https://github.com/swar/Swar-Chia-Plot-Manager](https://github.com/swar/Swar-Chia-Plot-Manager)
Переведено [Русскоязычным Сообществом Chia](http://chia.net.ru/).
Об ошибках или неточностях перевода просьба сообщать администраторам Discord сервера [Chia.Net.Ru](http://discord.chia.net.ru/).
