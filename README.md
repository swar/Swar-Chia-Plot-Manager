# Swar's Chia Plot Manager 粉丝版本尽兴翻译
 
原地址：https://github.com/swar/Swar-Chia-Plot-Manager


它是一个 chia 的绘图管理器：[https://www.chia.net/](https://www.chia.net/)

[English](README_EN.md) / [中文](README.ZN.md)

![The view of the manager](https://i.imgur.com/SmMDD0Q.png "View")

开发版本：v0.0.1

这是一个跨平台的 Chia  绘图管理器，可以在主流的操作系统上工作。它不是用来绘图的。绘图还是 chia 做的事情，这个库的目的是管理你的 chia 尽兴绘图，并使用你配置的 config.yaml 置来启动新的绘图。每个人的系统都不尽相同，所以定制是这个库中的一个重要特征。

这个库很简单，易于使用，而且可靠，可以保持绘图的生成。

这个库已经在 Windows 和 Linux 上进行了测试，我本人（卧底小哥）在 mac 和 windows 上进行了测试

## 特点

错开你的绘图，这样你的计算机资源就可以避免高峰期。
允许一个目标目录列表。
通过交错时间提前启动一个新的绘图，最大限度地利用临时空间。
同时运行最大数量的绘图，以避免瓶颈或限制资源占用。
更深入的检测绘制过程。
 
## 支持/问题

请不要使用GitHub问题来提问或支持你自己的个人设置，问题应该与代码错误有关，因为在这一点上，它已经被许多人测试过，可以在 Windows、Linux 和 Mac OS 上工作。因此，任何与技术支持、配置设置有关的问题，或者与你自己的个人使用情况有关的问题，都应该在下面的任何一个链接中提问。

Discord：[https://discord.gg/XyvMzeQpu2](https://discord.gg/XyvMzeQpu2)
这是官方 Discord 服务器 - Swar's Chia 社区

官方Chia Keybase团队：[https://keybase.io/team/chia_network.public](https://keybase.io/team/chia_network.public)频道是#swar

GitHub讨论区: [https://github.com/swar/Swar-Chia-Plot-Manager/discussions](https://github.com/swar/Swar-Chia-Plot-Manager/discussions)


## 常见的问题


**我可以重新加载我的配置吗？**
- 是的，你的配置可以通过`python [manager.py](http://manager.py/) restart`命令来重新加载，或者单独停止并重新启动管理器。请注意，你的任务数将被重置！临时目录2和目标目录的顺序也将被重置。

- 请注意，如果你改变了任务的任何一个目录，它将扰乱现有的任务，管理器和视图将无法识别旧的任务。如果你在有活动绘图的情况下改变任务目录，请将当前任务的 `max_plots` 改为0，然后用新目录做一个单独的任务。我不建议在计划运行时改变目录。

**如果我停止管理器，是否会杀死我的任务？**
- 不会，绘图是在后台启动的，它们不会杀死你现有的绘图。如果你想结束它们，你可以访问PIDs，并手动结束它们。请注意，你还必须删除.tmp文件。我不为你处理这个问题。

**如果我有一个列表，如何选择临时2和目的地？**

- 它们是按顺序选择的。如果你有两个目录，第一个绘图会选择第一个，第二个会选择第二个，而第三个会选择第一个,这样循环 1 2 1 2 1 2 1...

**什么是 temporary2_destination_sync？**

一些用户喜欢选择总是拥有相同的临时2和目标目录。启用这个设置将总是让 `temporary2` 作为目的地的磁盘。如果你使用这个设置，你可以使用一个空的 `temporary2` ]

**对我的设置来说，什么是最好的配置？**

- 请把这个问题转发给 `Keybase` 或添加讨论标签。

## 安装

这个库的安装是很简单的。我在下面附上了详细的说明，应该可以帮助你开始安装。

1、下载并安装Python 3.7或更高版本：[https://www.python.org/](https://www.python.org/)

2、`git clone` 命令克隆库或者直接网页下载它。

3、打开 CommandPrompt / PowerShell / Terminal，等任何工具，然后cd到主库文件夹。

- 例如：cd C:\Users\Swar\Documents\Swar-Chia-Plot-Manager

4、可选：为Python创建一个虚拟环境。如果你用Python做其他事情，建议这样做：

- 创建一个新的Python环境： python -m venv venv

- 第二个venv可以重命名为你想要的任何东西。我更喜欢用venv，因为它是一个规范。

- 激活这个虚拟环境。每次打开新窗口时都必须这样做。
    -  Windows：`venv\Scripts\activate`
    -  Linux: `./venv/bin/activate` 或 `source ./venv/bin/activate`

- 通过看到(venv)的前缀来确认它已经激活。前缀会根据你给它起的名字而改变。

5、安装所需模块： `pip install -r requirements.txt`

6、在同一目录下复制 `config.yaml.default` 并命名为 `config.yaml`

7、按照你自己的个人设置编辑和设置`config.yaml` 下面有更多关于这方面的帮助

- 你还需要添加 `chia_location!` 这应该指向你的chia可执行文件（注意这个不是环境变量，这个工具不需要你配置环境变量）

8、运行管理器： python [manager.py](http://manager.py/) start

- 这将在后台启动一个进程，根据你输入的设置来管理绘图。

9、运行视图： python [manager.py](http://manager.py/) view

- 这将循环查看检测屏幕上的正在活动地块的详细信息。

## 配置

这个库的配置对每个终端用户都是独一无二的 `config.yaml` 文件是配置的所在。

这个绘图管理器是基于任务的概念来工作的。每个任务都有自己的设置，你可以对每个任务进行个性化设置，没有哪个是唯一的，所以这将为你提供灵活性。

### chia_location
这是一个单一的变量，应该包含你的 `chia` 可执行文件的位置。这就是 chia 的可执行文件。

- Windows的例子：`C:\Users\<USERNAME>\AppData\Local\chia-blockchain\app-1.1.2\resources\app.asar.unpacked\daemon\chia.exe`

- Linux的例子: `/usr/lib/chia-blockchain/resources/app.asar.unpacked/daemon/chia`

- 另一个Linux例子: `/home/swar/chia-blockchain/venv/bin/chia`
### 管理

这些是只由绘制管理器使用的配置设置。

- `check_interval` - 在检查是否有新任务开始之前的等待秒数。

- `log_level` - 保持在 ` ERROR ` 上，只在有错误时记录。把它改为 `INFO`，以便看到更详细的日志记录。警告:`INFO` 会写下大量的信息。

### 日志

- `folder_path` - 这是你的日志文件的文件夹，用于保存绘图。

### 视图
这些是视图将使用的设置

- `check_interval` - 更新视图前的等待秒数。
- `datetime_format` - 视图中希望显示的日期时间格式。格式化见这里：[https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
- `include_seconds_for_phase` - 这决定了时间转换格式是否包括秒。
- `include_drive_info` - 这决定了是否会显示驱动器信息。
- `include_cpu` - 这决定了是否会显示CPU的信息。
- `include_ram` - 这决定了是否显示RAM的信息。
- `include_plot_stats` - 这决定了是否会显示绘图统计信息。
### 通知
这些是不同的设置，以便在绘图管理器启动和绘图完成时发送通知。

### 进展
- `phase_line_end` - 这些设置将用于决定一个阶段在进度条中的结束时间。它应该反映出该阶段结束的线，这样进度计算就可以使用该信息与现有的日志文件来计算进度百分比。
- `phase_weight` - 这些是在进度计算中分配给每个阶段的权重,通常情况下，第1和第3阶段是最长的阶段，所以它们将比其他阶段拥有更多的权重。
### 全局
- `max_concurrent` - 你的系统可以运行的最大绘图数量,管理器在一段时间内启动的地块总数不会超过这个数量。
## 任务
- 这些是每个任务将使用的设置。请注意，你可以有多个任务，每个任务都应该是YAML格式的，这样才能正确配置。这里几乎所有的值都将被传递到Chia可执行文件中。

点击这里查看更多关于Chia CLI的细节：[https://github.com/Chia-Network/chia-blockchain/wiki/CLI-Commands-Reference](https://github.com/Chia-Network/chia-blockchain/wiki/CLI-Commands-Reference)

- `name` - 这是你要给的名字。
- `max_plots` - 这是在管理器的一次运行中，任务的最大数量。任何重新启动管理器的操作都会重置这个变量。它在这里只是为了帮助短期的绘图。
- [OPTIONAL] `farmer_public_key` - 你的chia耕种公钥。如果没有提供，它将不会把这个变量传给chia执行程序，从而导致你的默认密钥被使用。只有当你在一台没有你的证书的机器上设置了chia时才需要这个。
- [OPTIONAL] `pool_public_key` - 你的池公钥。与上述信息相同。
- `temporary_directory` - 这里应该只传递一个目录。这是将进行绘图的地方。
- [OPTIONAL]`temporary2_directory `- 可以是一个单一的值或一个值的列表。这是一个可选的参数，如果你想使用 Chia 绘图的 temporary2 目录功能，可以使用这个参数。
- `destination_directory` - 可以是一个单一的值或一个值的列表。这是绘图完成后将被转移到的最终目录。如果你提供一个列表，它将逐一循环浏览每个驱动器。
- `size` - 这指的是绘图的k大小。你可以在这里输入32、33、34、35......这样的内容。
- `bitfield` - 这指的是你是否想在你的绘图中使用bitfield。通常情况下，推荐使用 `true`。
- `threads` - 这是将分配给 plot 绘图的线程数。只有第1阶段使用1个以上的线程。（观众很多反馈：这个是每个 plot 的线程）
- `buckets` - 要使用的桶的数量。Chia提供的默认值是128。
- `memory_buffer` - 你想分配给进程的内存数量。
- `max_concurrent` - 这个任务在任何时候都要有的最大数量的绘图。
- `max_concurrent_with_start_early` - 这项工作在任何时候拥有的最大绘图数量，包括提前开始的阶段。
- `stagger_minutes` - 每个任务并发之间的交错时间单位 分钟。如果你想让你的 plot 在并发限制允许的情况下立即被启动，你甚至可以把它设置为零。
- `max_for_phase_1` - 这个任务在第1阶段的最大绘图数量。
- `concurrency_start_early_phase` - 你想提前启动一个绘图的阶段。建议使用4。
- `concurrency_start_early_phase_delay` - 当检测到提前开始阶段时，在新的绘图被启动之前的最大等待分钟数。 
- `temporary2_destination_sync` - 这个字段将始终提交目标目录作为临时2目录。这两个目录将是同步的，因此它们将总是以相同的值提交。