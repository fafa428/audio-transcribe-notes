# Audio Transcribe Notes

把本地音频、视频转成文字稿，并整理成 Markdown 笔记。

这个项目适合处理课程录音、会议录音、直播回放、访谈、技术讲解、比赛说明、网课视频等内容。你可以把一个 `.mp4`、`.mp3`、`.wav`、`.m4a` 等文件交给它，它会生成带时间戳的转写稿，后续可以继续整理成会议纪要、学习笔记、技术文档或摘要。

## 它能做什么

- 把音频或视频转成文字。
- 自动给每段文字加时间戳，方便回看原视频。
- 支持长录音和长视频，会自动分段处理。
- 某一段处理失败时，会自动切成更短的小段重试。
- 输出 Markdown、TXT 和 JSON 三种格式。
- 可以用 CPU 跑，也可以用 NVIDIA 显卡 GPU 加速。
- 可以作为 Codex Skill 使用，让 Codex 帮你完成“转写 + 整理笔记”。

## 适合谁使用

如果你有下面这些需求，这个项目就适合你：

- 想把会议录音整理成会议纪要。
- 想把课程视频整理成学习笔记。
- 想把直播、讲座、访谈转成文字。
- 想给长视频生成带时间戳的文字稿。
- 想把中文音视频资料交给 AI 继续总结、提炼重点。

## 支持哪些文件

常见音频和视频一般都可以处理。

常见音频：

- `.mp3`
- `.wav`
- `.m4a`
- `.aac`
- `.flac`
- `.ogg`
- `.opus`

常见视频：

- `.mp4`
- `.mov`
- `.mkv`
- `.webm`
- `.avi`
- `.m4v`

最推荐的格式：

- 音频：`.mp3`、`.wav`、`.m4a`
- 视频：`.mp4`、`.mkv`

如果某个文件无法识别，可以先用 FFmpeg 转成 `.mp3` 或 `.wav` 再处理。

## 快速开始

下面以 Windows 为例。第一次使用需要安装环境，之后每次只需要运行一条命令。

### 第一步：下载项目

打开 PowerShell，运行：

```powershell
git clone https://github.com/fafa428/audio-transcribe-notes.git
cd audio-transcribe-notes
```

如果你不会使用 Git，也可以在 GitHub 页面点击 `Code`，再点击 `Download ZIP` 下载压缩包，解压后进入文件夹。

### 第二步：安装 Python

推荐安装 Python 3.11。

下载地址：

```text
https://www.python.org/downloads/
```

安装时建议勾选：

```text
Add python.exe to PATH
```

安装完成后，在 PowerShell 中检查：

```powershell
python --version
```

如果显示类似下面内容，就说明 Python 可用：

```text
Python 3.11.x
```

### 第三步：创建运行环境

在项目目录中运行：

```powershell
python -m venv .venv
```

激活环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示不允许运行脚本，先执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后重新激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 第四步：安装依赖

普通用户建议先使用 CPU 版本，安装简单，稳定性高：

```powershell
python -m pip install -U pip wheel
python -m pip install "setuptools<81" faster-whisper==1.2.1 ctranslate2==4.5.0 av
```

如果下载速度慢，可以使用清华镜像：

```powershell
python -m pip install -U pip wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install "setuptools<81" faster-whisper==1.2.1 ctranslate2==4.5.0 av -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第五步：开始转写

假设你有一个文件：

```text
meeting.mp4
```

把它放到项目目录里，然后运行：

```powershell
python scripts\audio_to_transcript.py `
  --input "meeting.mp4" `
  --model "large-v3" `
  --device cpu `
  --output-prefix "meeting_transcript"
```

第一次运行时，模型可能会自动下载，需要等待一段时间。`large-v3` 模型比较大，下载慢是正常的。

运行完成后，你会看到这些文件：

```text
meeting_transcript.md
meeting_transcript.txt
meeting_transcript.segments.json
meeting_transcript_chunks/
```

最常用的是：

```text
meeting_transcript.md
meeting_transcript.txt
```

## 输出文件怎么看

### `.md` 文件

Markdown 格式，适合放进 Obsidian、Typora、Notion、飞书文档、语雀等工具，也适合继续交给 AI 整理。

示例：

```markdown
# Transcript

## Segments

- [00:00:00.000 - 00:00:04.200] 大家好，我们今天开始讲这个项目。
```

### `.txt` 文件

纯文本格式，适合直接复制：

```text
[00:00:00.000 --> 00:00:04.200] 大家好，我们今天开始讲这个项目。
```

### `.segments.json` 文件

结构化数据，适合程序进一步处理。普通用户一般不用打开它，但建议保留。

### `_chunks` 文件夹

这里存放分段转写结果。长视频会被切成很多小段处理。如果转写中断，重新运行同一条命令时，已经完成的小段通常可以跳过。

## 常用命令

### 转写 MP4 视频

```powershell
python scripts\audio_to_transcript.py `
  --input "video.mp4" `
  --model "large-v3" `
  --device cpu `
  --output-prefix "video_transcript"
```

### 转写 MP3 音频

```powershell
python scripts\audio_to_transcript.py `
  --input "audio.mp3" `
  --model "large-v3" `
  --device cpu `
  --output-prefix "audio_transcript"
```

### 只转写一小段

例如只转写第 60 秒到第 180 秒：

```powershell
python scripts\audio_to_transcript.py `
  --input "meeting.mp4" `
  --model "large-v3" `
  --device cpu `
  --clip-start 60 `
  --clip-end 180 `
  --output-prefix "meeting_part"
```

### 长视频更稳定的写法

默认每 60 秒切一段。如果你的电脑容易卡住，可以改成每 30 秒切一段：

```powershell
python scripts\audio_to_transcript.py `
  --input "long_video.mp4" `
  --model "large-v3" `
  --device cpu `
  --chunk-seconds 30 `
  --output-prefix "long_video_transcript"
```

### 转写英文内容

```powershell
python scripts\audio_to_transcript.py `
  --input "english.mp4" `
  --model "large-v3" `
  --device cpu `
  --language en `
  --output-prefix "english_transcript"
```

### 给专业内容加提示

如果音频里有很多专业词，可以加提示词，提高识别稳定性：

```powershell
python scripts\audio_to_transcript.py `
  --input "lecture.mp4" `
  --model "large-v3" `
  --device cpu `
  --initial-prompt "这是一段中文课程录音，包含人工智能、算法、数据集、模型训练和实验结果。" `
  --output-prefix "lecture_transcript"
```

## 如何整理成笔记

这个项目会先生成带时间戳的转写稿。生成后，你可以把 `.md` 或 `.txt` 文件交给 AI，让它继续整理。

比如你可以这样提问：

```text
请根据这份转写稿整理成结构化学习笔记，保留关键时间戳，提取重点、概念、方法、结论和待办事项。
```

会议纪要可以这样提问：

```text
请根据这份会议转写稿整理会议纪要，包括会议主题、核心结论、行动项、负责人、截止时间和关键时间戳。
```

技术讲解可以这样提问：

```text
请把这份技术讲解转写稿整理成技术文档，包含背景、流程、关键参数、算法思路、风险点和实现建议。
```

## 使用 GPU 加速

如果你只是想先跑起来，建议跳过本节，直接用 CPU。

如果你有 NVIDIA 显卡，并且希望速度更快，可以使用 GPU。GPU 模式需要：

- NVIDIA 显卡。
- NVIDIA 驱动。
- CUDA Toolkit 12.x。
- cuDNN 9.x。
- 正确安装 `faster-whisper` 和 `ctranslate2`。

仓库里有一份 Windows GPU 配置参考：

```text
references/windows-whisper-gpu.md
```

配置好后，可以用下面命令检查：

```powershell
python -c "import ctranslate2; print(ctranslate2.get_cuda_device_count())"
```

如果输出大于 `0`，说明 Python 能识别到 CUDA。

GPU 转写示例：

```powershell
python scripts\audio_to_transcript.py `
  --input "meeting.mp4" `
  --model "large-v3" `
  --device cuda `
  --output-prefix "meeting_transcript"
```

如果 cuDNN 没有加入系统路径，可以临时指定：

```powershell
python scripts\audio_to_transcript.py `
  --input "meeting.mp4" `
  --model "large-v3" `
  --device cuda `
  --prepend-path "D:\path\to\cudnn\bin;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2\bin" `
  --output-prefix "meeting_transcript"
```

## 模型怎么选

`--model` 决定识别效果和速度。

常见选择：

- `large-v3`：效果好，但模型大，速度较慢。
- `medium`：速度和效果比较均衡。
- `small`：更快，但准确率可能下降。
- 本地模型目录：适合离线使用或提前下载好模型。

普通用户建议先用：

```text
large-v3
```

如果电脑比较慢，可以换成：

```text
medium
```

如果你已经下载好了 faster-whisper 模型，也可以直接写模型路径：

```powershell
--model "D:\models\faster-whisper-large-v3"
```

本地模型目录通常包含：

```text
config.json
model.bin
preprocessor_config.json
tokenizer.json
vocabulary.json
```

## 作为 Codex Skill 使用

这个仓库也可以作为 Codex Skill 使用。

安装到 Codex skills 目录：

```powershell
mkdir "$env:USERPROFILE\.codex\skills" -Force
git clone https://github.com/fafa428/audio-transcribe-notes.git "$env:USERPROFILE\.codex\skills\audio-transcribe-notes"
```

然后你可以在 Codex 中这样说：

```text
用 audio-transcribe-notes 帮我转写 D:\recordings\meeting.mp4，并生成结构化会议纪要。
```

或者：

```text
请把这个课程视频转成带时间戳的文字稿，并整理成 Markdown 学习笔记。
```

## 参数说明

常用参数：

| 参数 | 作用 |
| --- | --- |
| `--input` | 输入音频或视频文件。 |
| `--model` | 使用的 faster-whisper 模型。 |
| `--device` | 使用 `cpu` 或 `cuda`。 |
| `--output-prefix` | 输出文件名前缀。 |
| `--language` | 语言，中文是 `zh`，英文是 `en`。 |
| `--chunk-seconds` | 每段切多长，默认 60 秒。 |
| `--clip-start` | 从第几秒开始转写。 |
| `--clip-end` | 转写到第几秒结束。 |
| `--initial-prompt` | 给模型的提示词，适合专业内容。 |
| `--no-vad-filter` | 关闭静音过滤，漏字时可以尝试。 |
| `--local-files-only` | 只使用本地模型，不联网下载。 |
| `--prepend-path` | 临时添加 CUDA/cuDNN 路径。 |

一般只需要记住这四个：

```text
--input
--model
--device
--output-prefix
```

## 常见问题

### PowerShell 提示不能运行脚本

执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后重新激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 第一次运行很慢

第一次运行可能会下载模型。`large-v3` 模型很大，下载慢是正常的。

如果下载失败，可以换网络，或者提前下载 faster-whisper 模型到本地，再用本地路径作为 `--model`。

### 转写速度很慢

可能是因为使用了 CPU 或模型太大。

可以尝试：

```powershell
--model medium
```

或者配置 GPU 后使用：

```powershell
--device cuda
```

### 文字里有重复内容

音频静音、片头片尾、背景音乐、低音质内容可能导致 Whisper 生成重复文字。

可以尝试：

- 剪掉片头片尾。
- 用 `--clip-start` 和 `--clip-end` 只处理有效部分。
- 保留默认静音过滤，不要加 `--no-vad-filter`。
- 在整理笔记时让 AI 删除明显重复和无意义内容。

### 有些地方漏字

可以尝试关闭静音过滤：

```powershell
--no-vad-filter
```

也可以给更明确的提示词：

```powershell
--initial-prompt "这是一段中文会议录音，包含项目名称、人员姓名、任务安排和时间节点。"
```

### 某个视频打不开

可以先用 FFmpeg 抽取音频：

```powershell
ffmpeg -i input.mp4 -vn -ac 1 -ar 16000 output.wav
```

然后转写：

```powershell
python scripts\audio_to_transcript.py `
  --input "output.wav" `
  --model "large-v3" `
  --device cpu `
  --output-prefix "output_transcript"
```

### GPU 报错找不到 cuDNN

常见报错包括：

```text
Could not locate cudnn_ops64_9.dll
```

这说明 cuDNN 没有配置好。建议先看：

```text
references/windows-whisper-gpu.md
```

如果只是想完成转写，可以先改用 CPU：

```powershell
--device cpu
```

## 给新手的推荐用法

如果你不确定该怎么选，直接按下面方式使用：

1. 先用 CPU。
2. 先用 `large-v3`。
3. 输入文件优先用 `.mp4`、`.mp3`、`.wav`。
4. 输出前缀用英文或拼音，避免路径问题。
5. 长视频先试 1 到 3 分钟，确认效果后再跑完整文件。

试跑 3 分钟：

```powershell
python scripts\audio_to_transcript.py `
  --input "your_file.mp4" `
  --model "large-v3" `
  --device cpu `
  --clip-start 0 `
  --clip-end 180 `
  --output-prefix "test_transcript"
```

完整转写：

```powershell
python scripts\audio_to_transcript.py `
  --input "your_file.mp4" `
  --model "large-v3" `
  --device cpu `
  --output-prefix "full_transcript"
```

## 开发者说明

核心脚本是：

```text
scripts/audio_to_transcript.py
```

它的基本流程是：

1. 使用 PyAV 读取媒体时长。
2. 按 `--chunk-seconds` 切分音视频。
3. 每个切块用独立子进程调用 faster-whisper。
4. 失败切块自动二分重试。
5. 合并所有切块结果。
6. 输出 `.segments.json`、`.txt`、`.md`。

仓库默认忽略转写产物和缓存文件，避免把大文件提交到 Git。

## 许可

当前仓库尚未声明许可证。如果你计划让其他人复用、分发或二次开发，建议补充 `LICENSE` 文件。
