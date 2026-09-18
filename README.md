# Open Video Downloader

**Open Video Downloader (OVD)** is a command-line tool for downloading publicly accessible videos and media from multiple platforms using `yt-dlp`.

**Version:** `1.0.0`

---

## Features

* YouTube support
* Instagram support
* TikTok support
* X / Twitter support
* Facebook support
* Vimeo support
* Twitch support
* Batch downloads
* Media information
* Multiple video qualities
* Multiple output formats
* Audio extraction
* Configurable output directory
* FFmpeg detection
* Terminal progress bar
* Windows-friendly filenames
* Local configuration system

---

## Requirements

* Python 3.9 or newer
* FFmpeg
* Git — only required if installing from the Git repository

FFmpeg is recommended for media merging, conversion and audio extraction.

---

## Installation

### From GitHub

Clone the repository:

```bash
git clone https://github.com/FefinDev/OpenVideoDownloader.git
```

Enter the project directory:

```bash
cd OpenVideoDownloader
```

Upgrade `pip`:

```bash
python -m pip install -U pip
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Install OVD:

```bash
pip install -e .
```

Verify the installation:

```bash
ovd --version
```

Expected output:

```text
Open Video Downloader 1.0.0
```

---

## Virtual Environment

Using a virtual environment is recommended if you are developing or modifying OVD.

Create one:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on Windows CMD:

```cmd
.venv\Scripts\activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Install OVD:

```bash
pip install -e .
```

---

## FFmpeg

FFmpeg is recommended for OVD.

Check whether FFmpeg is installed:

```bash
ffmpeg -version
```

If FFmpeg is available in your system `PATH`, OVD can use it automatically for operations such as:

* Merging video and audio
* Converting media
* Extracting audio
* Processing certain formats

---

# Usage

## Download a video

```bash
ovd download "https://example.com/video"
```

OVD automatically detects the supported platform and selects an appropriate media format.

---

## Select quality

```bash
ovd download "https://example.com/video" --quality 1080
```

Available quality options:

```text
best
1080
720
480
360
```

Example:

```bash
ovd download "https://example.com/video" -q 720
```

---

## Select format

```bash
ovd download "https://example.com/video" --format mp4
```

Supported output formats include:

```text
mp4
mp3
m4a
opus
wav
flac
mkv
webm
mov
```

The formats actually available may depend on the source media and FFmpeg.

---

## Download audio

Use:

```bash
ovd download "https://example.com/video" --audio
```

Example:

```bash
ovd download "https://example.com/video" -a
```

Audio extraction uses FFmpeg when required.

---

## Choose an output directory

Use:

```bash
ovd download "https://example.com/video" -o "C:\Videos"
```

For example:

```powershell
ovd download "https://example.com/video" -o "C:\Users\feder\Descargas"
```

---

# Media Information

Use `info` to inspect a URL without downloading the media:

```bash
ovd info "https://example.com/video"
```

OVD can display information such as:

* Title
* Platform
* Channel or author
* Duration
* Resolution
* Available formats
* Media ID

---

# Batch Downloads

Create a text file containing one URL per line:

```text
https://example.com/video1
https://example.com/video2
https://example.com/video3
```

For example, save it as:

```text
videos.txt
```

Then run:

```bash
ovd batch videos.txt
```

OVD processes the URLs sequentially and displays a summary when finished.

Comments can be added using `#`:

```text
# My videos

https://example.com/video1
https://example.com/video2
```

Empty lines and comments are ignored.

---

# Supported Platforms

View the currently recognized platforms with:

```bash
ovd platforms
```

Currently recognized platforms include:

* YouTube
* Instagram
* TikTok
* X / Twitter
* Facebook
* Vimeo
* Twitch

OVD uses `yt-dlp` as its downloading engine, so other websites supported by `yt-dlp` may also work.

---

# Configuration

OVD stores its configuration locally in:

```text
~/.ovd/config.json
```

On Windows, this is located inside the user's home directory.

View the current configuration:

```bash
ovd config show
```

---

## Change the output directory

```bash
ovd config set output "C:\Users\feder\Descargas"
```

---

## Change the default quality

Use the best available quality:

```bash
ovd config set quality best
```

Or set a specific quality:

```bash
ovd config set quality 1080
```

Available values:

```text
best
1080
720
480
360
```

---

## Change the default format

```bash
ovd config set format mp4
```

---

## Change the default audio format

```bash
ovd config set audio_format mp3
```

---

## Reset configuration

```bash
ovd config reset
```

This restores the default configuration.

---

# Commands

```text
ovd download <URL>
ovd info <URL>
ovd batch <FILE>
ovd platforms

ovd config show
ovd config set <KEY> <VALUE>
ovd config reset

ovd --version
ovd --help
```

---

# Command Options

## `download`

```text
ovd download <URL>
```

Options:

```text
-q, --quality <QUALITY>
-f, --format <FORMAT>
-o, --output <PATH>
-a, --audio
```

Example:

```bash
ovd download "https://example.com/video" -q 1080 -f mp4
```

---

## `info`

```text
ovd info <URL>
```

Displays information about the media without downloading it.

---

## `batch`

```text
ovd batch <FILE>
```

Downloads every URL contained in the specified text file.

Example:

```bash
ovd batch videos.txt
```

---

## `platforms`

```text
ovd platforms
```

Displays the platforms recognized by OVD.

---

## `config`

Show the configuration:

```bash
ovd config show
```

Change a setting:

```bash
ovd config set <KEY> <VALUE>
```

Reset the configuration:

```bash
ovd config reset
```

---

# Examples

### Download a video

```bash
ovd download "https://example.com/video"
```

### Download in 1080p

```bash
ovd download "https://example.com/video" --quality 1080
```

### Download as MP4

```bash
ovd download "https://example.com/video" --format mp4
```

### Download audio

```bash
ovd download "https://example.com/video" --audio
```

### Save to a custom directory

```bash
ovd download "https://example.com/video" --output "C:\Videos"
```

### Get media information

```bash
ovd info "https://example.com/video"
```

### Download multiple URLs

```bash
ovd batch videos.txt
```

---

# Project Structure

```text
OpenVideoDownloader/
│
├── ovd/
│   ├── __init__.py
│   └── cli.py
│
├── .gitignore
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

# License

MIT License.

Open Video Downloader is an independent project that uses `yt-dlp` as its downloading engine.

Always respect the terms of service and copyright laws applicable to the content and platforms you use.
