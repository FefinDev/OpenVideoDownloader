from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import yt_dlp

from . import __app_name__, __version__


# ============================================================
# CONFIGURATION
# ============================================================

APP_DIR = Path.home() / ".ovd"
CONFIG_FILE = APP_DIR / "config.json"

DEFAULT_CONFIG = {
    "output": str(Path.home() / "Downloads"),
    "quality": "best",
    "format": "mp4",
    "audio_format": "mp3",
    "overwrite": False,
}


# ============================================================
# TERMINAL COLORS
# ============================================================

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


# ============================================================
# UI
# ============================================================

def banner() -> None:
    print()

    print(c("   ██████╗ ██╗   ██╗██████╗", Colors.CYAN))
    print(c("  ██╔═══██╗██║   ██║██╔══██╗", Colors.CYAN))
    print(c("  ██║   ██║██║   ██║██║  ██║", Colors.CYAN))
    print(c("  ██║   ██║╚██╗ ██╔╝██║  ██║", Colors.CYAN))
    print(c("  ╚██████╔╝ ╚████╔╝ ██████╔╝", Colors.CYAN))
    print(c("   ╚═════╝   ╚═══╝  ╚═════╝", Colors.CYAN))

    print()
    print(c("  Open Video Downloader", Colors.WHITE))
    print(c(f"  Version {__version__}", Colors.GRAY))
    print()


def header() -> None:
    print(c("OVD", Colors.CYAN), c("•", Colors.GRAY), "Open Video Downloader")
    print(c("─" * 58, Colors.GRAY))


def section(title: str) -> None:
    print()
    print(c(title, Colors.CYAN))
    print(c("─" * 58, Colors.GRAY))


def success(message: str) -> None:
    print(c("✓", Colors.GREEN), message)


def warning(message: str) -> None:
    print(c("!", Colors.YELLOW), message)


def error(message: str) -> None:
    print(c("✗", Colors.RED), message)


def info(message: str) -> None:
    print(c("•", Colors.CYAN), message)


def field(name: str, value: object) -> None:
    print(
        f"{c(name.upper().ljust(10), Colors.GRAY)}"
        f"{value}"
    )


def spinner_line(message: str) -> None:
    print(c("›", Colors.CYAN), message)


# ============================================================
# CONFIG
# ============================================================

def ensure_config() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4),
            encoding="utf-8",
        )


def load_config() -> dict:
    ensure_config()

    try:
        return json.loads(
            CONFIG_FILE.read_text(encoding="utf-8")
        )

    except Exception:
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)

    CONFIG_FILE.write_text(
        json.dumps(config, indent=4),
        encoding="utf-8",
    )


# ============================================================
# SYSTEM
# ============================================================

def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def detect_platform(url: str) -> str:
    url_lower = url.lower()

    platforms = {
        "YouTube": [
            "youtube.com",
            "youtu.be",
        ],
        "Instagram": [
            "instagram.com",
        ],
        "TikTok": [
            "tiktok.com",
        ],
        "X / Twitter": [
            "x.com",
            "twitter.com",
        ],
        "Facebook": [
            "facebook.com",
            "fb.watch",
        ],
        "Vimeo": [
            "vimeo.com",
        ],
        "Twitch": [
            "twitch.tv",
        ],
    }

    for platform, domains in platforms.items():
        if any(domain in url_lower for domain in domains):
            return platform

    return "Other"


# ============================================================
# QUALITY
# ============================================================

def choose_quality() -> str:
    section("Quality")

    print("  1. Best available")
    print("  2. 1080p")
    print("  3. 720p")
    print("  4. 480p")
    print("  5. 360p")

    print()

    choice = input(
        c("  Select quality [1]: ", Colors.WHITE)
    ).strip()

    qualities = {
        "1": "best",
        "2": "1080",
        "3": "720",
        "4": "480",
        "5": "360",
    }

    return qualities.get(choice, "best")


# ============================================================
# FORMAT SELECTION
# ============================================================

def build_format(
    quality: str,
    output_format: str,
    platform: str,
) -> str:

    # Audio-only formats
    if output_format in {
        "mp3",
        "m4a",
        "opus",
        "wav",
        "flac",
    }:
        return "bestaudio/best"

    # Platforms where a direct MP4 is preferable.
    if platform in {
        "Instagram",
        "TikTok",
        "X / Twitter",
        "Facebook",
    }:

        if quality == "best":
            return "best[ext=mp4]/best"

        return (
            f"best[height<={quality}][ext=mp4]/"
            f"best[height<={quality}]/best"
        )

    # General platforms.
    if quality == "best":
        return (
            "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/"
            "best[ext=mp4]/"
            "bestvideo+bestaudio/best"
        )

    return (
        f"bestvideo[height<={quality}][vcodec^=avc1]+"
        "bestaudio[ext=m4a]/"
        f"best[height<={quality}][ext=mp4]/"
        f"bestvideo[height<={quality}]+bestaudio/"
        f"best[height<={quality}]/best"
    )


# ============================================================
# PROGRESS
# ============================================================

def progress_hook(data: dict) -> None:
    status = data.get("status")

    if status == "downloading":
        downloaded = data.get("downloaded_bytes", 0)

        total = (
            data.get("total_bytes")
            or data.get("total_bytes_estimate")
        )

        if not total:
            return

        percent = downloaded / total * 100

        width = 38
        filled = int(width * percent / 100)

        bar = (
            "█" * filled
            + "░" * (width - filled)
        )

        speed = data.get("_speed_str", "--")
        eta = data.get("_eta_str", "--")

        print(
            f"\r"
            f"{c(bar, Colors.CYAN)} "
            f"{percent:6.2f}% "
            f"{c(speed, Colors.WHITE)} "
            f"ETA {c(eta, Colors.GRAY)}",
            end="",
            flush=True,
        )

    elif status == "finished":
        print()


# ============================================================
# DOWNLOAD
# ============================================================

def download_video(
    url: str,
    config: dict,
    quality: str | None = None,
    output_format: str | None = None,
    audio: bool = False,
) -> bool:

    platform = detect_platform(url)

    if quality is None:
        quality = config.get("quality", "best")

        if quality == "interactive":
            quality = choose_quality()

    output_format = (
        output_format
        or config.get("format", "mp4")
    )

    if audio:
        output_format = config.get(
            "audio_format",
            "mp3",
        )

    output_dir = Path(
        config["output"]
    ).expanduser()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    section("Download")

    field("URL", url)
    field("Platform", platform)

    quality_display = (
        "Best available"
        if quality == "best"
        else f"{quality}p"
    )

    field("Quality", quality_display)
    field("Format", output_format.upper())
    field("Output", output_dir)

    print()

    # --------------------------------------------------------
    # FFmpeg
    # --------------------------------------------------------

    if ffmpeg_available():
        success("FFmpeg detected")
    else:
        warning("FFmpeg was not detected in PATH")

        if output_format in {
            "mp3",
            "m4a",
            "opus",
            "wav",
            "flac",
        }:
            warning(
                "Audio conversion may not work without FFmpeg"
            )

    print()

    # --------------------------------------------------------
    # yt-dlp configuration
    # --------------------------------------------------------

    ydl_format = build_format(
        quality,
        output_format,
        platform,
    )

    options = {
        "format": ydl_format,

        "outtmpl": str(
            output_dir / "%(title)s.%(ext)s"
        ),

        "windowsfilenames": True,

        "noplaylist": True,

        "retries": 5,
        "fragment_retries": 5,

        "progress_hooks": [
            progress_hook
        ],

        "quiet": True,
        "no_warnings": True,
    }

    # --------------------------------------------------------
    # Audio extraction
    # --------------------------------------------------------

    if output_format in {
        "mp3",
        "m4a",
        "opus",
        "wav",
        "flac",
    }:

        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": output_format,
                "preferredquality": "192",
            }
        ]

    # --------------------------------------------------------
    # Container formats
    # --------------------------------------------------------

    elif output_format == "mkv":
        options["merge_output_format"] = "mkv"

    elif output_format == "webm":
        options["merge_output_format"] = "webm"

    elif output_format == "mov":
        options["merge_output_format"] = "mov"

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    spinner_line("Downloading...")

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        print()

        success("Download completed")

        print()
        field("Saved to", output_dir)

        return True

    except Exception as exc:

        print()

        error("Download failed")

        print()
        print(c("Reason:", Colors.GRAY))
        print(str(exc))

        print()
        print(c("Try:", Colors.GRAY))
        print("  • Check that FFmpeg is installed")
        print("  • Try another quality")
        print("  • Run `ovd info <URL>`")
        print()

        return False


# ============================================================
# INFO
# ============================================================

def show_info(url: str) -> None:

    section("Media Information")

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            data = ydl.extract_info(
                url,
                download=False,
            )

        title = data.get("title")
        uploader = data.get("uploader")
        duration = data.get("duration_string")
        resolution = data.get("resolution")
        extension = data.get("ext")
        media_id = data.get("id")

        field(
            "Title",
            title or "Unknown",
        )

        field(
            "Platform",
            detect_platform(url),
        )

        field(
            "Channel",
            uploader or "Unknown",
        )

        field(
            "Duration",
            duration or "Unknown",
        )

        field(
            "Resolution",
            resolution or "Unknown",
        )

        field(
            "Format",
            extension or "Unknown",
        )

        field(
            "ID",
            media_id or "Unknown",
        )

        print()

    except Exception as exc:

        error("Could not retrieve media information")
        print()
        print(str(exc))


# ============================================================
# BATCH
# ============================================================

def batch_download(
    filename: str,
    config: dict,
) -> None:

    path = Path(filename)

    if not path.exists():
        error(f"File not found: {path}")
        return

    try:
        urls = [
            line.strip()
            for line in path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
            and not line.strip().startswith("#")
        ]

    except Exception as exc:
        error(f"Could not read file: {exc}")
        return

    if not urls:
        warning("No URLs were found in the file.")
        return

    section("Batch Download")

    print(
        c(
            f"{len(urls)} URL(s) queued",
            Colors.WHITE,
        )
    )

    successful = 0
    failed = 0

    for index, url in enumerate(
        urls,
        start=1,
    ):

        print()

        print(
            c(
                f"[{index}/{len(urls)}]",
                Colors.CYAN,
            ),
            url,
        )

        if download_video(
            url,
            config,
        ):
            successful += 1
        else:
            failed += 1

    print()

    section("Batch Summary")

    field("Total", len(urls))
    field("Completed", successful)
    field("Failed", failed)

    print()


# ============================================================
# PLATFORMS
# ============================================================

def show_platforms() -> None:

    section("Supported Platforms")

    platforms = [
        "YouTube",
        "Instagram",
        "TikTok",
        "X / Twitter",
        "Facebook",
        "Vimeo",
        "Twitch",
    ]

    for platform in platforms:
        print(
            f"  {c('•', Colors.CYAN)} "
            f"{platform}"
        )

    print()

    print(
        c(
            "OVD uses yt-dlp, so additional supported "
            "websites may work as well.",
            Colors.GRAY,
        )
    )

    print()


# ============================================================
# CONFIG COMMANDS
# ============================================================

def config_show(config: dict) -> None:

    section("Configuration")

    field(
        "Output",
        config.get("output"),
    )

    field(
        "Quality",
        config.get("quality"),
    )

    field(
        "Format",
        config.get("format"),
    )

    field(
        "Audio",
        config.get("audio_format"),
    )

    field(
        "Overwrite",
        config.get("overwrite"),
    )

    print()

    field(
        "Config",
        CONFIG_FILE,
    )

    print()


def config_set(
    config: dict,
    key: str,
    value: str,
) -> None:

    if key not in DEFAULT_CONFIG:

        error(
            f"Unknown configuration key: {key}"
        )

        print()

        print(c("Available keys:", Colors.GRAY))

        for item in DEFAULT_CONFIG:
            print(f"  • {item}")

        print()

        return

    if key == "overwrite":

        value = value.lower() in {
            "true",
            "1",
            "yes",
            "y",
            "si",
            "sí",
        }

    elif key == "output":

        value = str(
            Path(value)
            .expanduser()
            .resolve()
        )

    config[key] = value

    save_config(config)

    success(
        f"Configuration updated: {key}"
    )


def config_reset() -> None:

    save_config(
        DEFAULT_CONFIG.copy()
    )

    success(
        "Configuration restored to defaults"
    )


# ============================================================
# HELP
# ============================================================

def print_help() -> None:

    print()

    print(
        c(
            "Open Video Downloader",
            Colors.WHITE,
        )
    )

    print(
        c(
            f"Version {__version__}",
            Colors.GRAY,
        )
    )

    print()

    print(c("Usage", Colors.CYAN))
    print(
        "  ovd <command> [options]"
    )

    print()

    print(c("Commands", Colors.CYAN))

    print(
        "  download <URL>          Download media"
    )

    print(
        "  info <URL>              Show media information"
    )

    print(
        "  batch <FILE>            Download multiple URLs"
    )

    print(
        "  platforms               Show supported platforms"
    )

    print(
        "  config show             Show configuration"
    )

    print(
        "  config set <KEY> <VAL>  Change configuration"
    )

    print(
        "  config reset            Reset configuration"
    )

    print()

    print(c("Download options", Colors.CYAN))

    print(
        "  -q, --quality <value>   Video quality"
    )

    print(
        "  -f, --format <format>   Output format"
    )

    print(
        "  -o, --output <path>     Output directory"
    )

    print(
        "  -a, --audio             Download audio"
    )

    print()

    print(c("Examples", Colors.CYAN))

    print(
        "  ovd download https://youtube.com/watch?v=..."
    )

    print(
        "  ovd download https://... --quality 1080"
    )

    print(
        "  ovd download https://... --audio"
    )

    print(
        "  ovd info https://..."
    )

    print()

    print(c("Version", Colors.CYAN))

    print(
        "  ovd --version"
    )

    print()


# ============================================================
# DOWNLOAD ARGUMENTS
# ============================================================

def parse_download_args(
    args: list[str],
) -> dict:

    result = {
        "url": None,
        "quality": None,
        "format": None,
        "output": None,
        "audio": False,
    }

    index = 0

    while index < len(args):

        arg = args[index]

        # Quality
        if arg in {
            "-q",
            "--quality",
        }:

            if index + 1 >= len(args):
                raise ValueError(
                    "Missing value for --quality."
                )

            result["quality"] = args[
                index + 1
            ]

            index += 2
            continue

        # Format
        if arg in {
            "-f",
            "--format",
        }:

            if index + 1 >= len(args):
                raise ValueError(
                    "Missing value for --format."
                )

            result["format"] = args[
                index + 1
            ]

            index += 2
            continue

        # Output
        if arg in {
            "-o",
            "--output",
        }:

            if index + 1 >= len(args):
                raise ValueError(
                    "Missing value for --output."
                )

            result["output"] = args[
                index + 1
            ]

            index += 2
            continue

        # Audio
        if arg in {
            "-a",
            "--audio",
        }:

            result["audio"] = True

            index += 1
            continue

        # Unknown option
        if arg.startswith("-"):
            raise ValueError(
                f"Unknown option: {arg}"
            )

        # URL
        if result["url"] is None:

            result["url"] = arg

            index += 1
            continue

        raise ValueError(
            f"Unexpected argument: {arg}"
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    ensure_config()

    args = sys.argv[1:]

    # No arguments
    if not args:

        banner()
        print_help()

        return

    # Version
    if args[0] in {
        "--version",
        "-V",
        "version",
    }:

        print(
            f"{__app_name__} {__version__}"
        )

        return

    # Help
    if args[0] in {
        "--help",
        "-h",
        "help",
    }:

        banner()
        print_help()

        return

    config = load_config()

    command = args[0]

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    if command == "download":

        try:

            options = parse_download_args(
                args[1:]
            )

        except ValueError as exc:

            error(str(exc))

            return

        if not options["url"]:

            error("Missing URL.")

            return

        if options["output"]:

            config["output"] = str(
                Path(
                    options["output"]
                )
                .expanduser()
                .resolve()
            )

        download_video(
            options["url"],
            config,
            quality=options["quality"],
            output_format=options["format"],
            audio=options["audio"],
        )

        return

    # --------------------------------------------------------
    # INFO
    # --------------------------------------------------------

    if command == "info":

        if len(args) < 2:

            error("Missing URL.")

            return

        show_info(args[1])

        return

    # --------------------------------------------------------
    # BATCH
    # --------------------------------------------------------

    if command == "batch":

        if len(args) < 2:

            error("Missing file.")

            return

        batch_download(
            args[1],
            config,
        )

        return

    # --------------------------------------------------------
    # PLATFORMS
    # --------------------------------------------------------

    if command == "platforms":

        show_platforms()

        return

    # --------------------------------------------------------
    # CONFIG
    # --------------------------------------------------------

    if command == "config":

        if len(args) < 2:

            config_show(config)

            return

        subcommand = args[1]

        if subcommand == "show":

            config_show(config)

            return

        if subcommand == "reset":

            config_reset()

            return

        if subcommand == "set":

            if len(args) < 4:

                warning(
                    "Usage: ovd config set <KEY> <VALUE>"
                )

                return

            config_set(
                config,
                args[2],
                " ".join(args[3:]),
            )

            return

        error(
            f"Unknown config command: {subcommand}"
        )

        return

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    error(
        f"Unknown command: {command}"
    )

    print_help()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()