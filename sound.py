import atexit
import ctypes
import shutil
import subprocess
import sys
from pathlib import Path

def resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path


SOUNDS_DIR = resource_path("Sounds")

MUSIC_EXTENSIONS = (".mp3", ".ogg", ".wav", ".flac")
ALIAS_MUSIC = "bomber_bgm"
ALIAS_SFX = "bomber_sfx"

_global_manager = None


def mci_send(cmd):
    return int(ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None))


def close_music_alias():
    if sys.platform == "win32":
        mci_send(f"close {ALIAS_MUSIC}")


def close_sfx_alias():
    if sys.platform == "win32":
        mci_send(f"close {ALIAS_SFX}")


def find_music_file():
    for ext in MUSIC_EXTENSIONS:
        p = resource_path(f"Sounds/Music{ext}")
        if p.is_file():
            return str(p)

    if SOUNDS_DIR.is_dir():
        for p in sorted(SOUNDS_DIR.glob("Music.*")):
            if p.suffix.lower() in MUSIC_EXTENSIONS:
                return str(p)
    return None


def play_background_windows(path, loop, volume):
    close_music_alias()
    s = str(path).replace("\\", "/")

    opened = False
    for cmd in (
        f'open "{s}" type mpegvideo alias {ALIAS_MUSIC}',
        f'open "{s}" type MPEGVideo alias {ALIAS_MUSIC}',
    ):
        if mci_send(cmd) == 0:
            opened = True
            break

    if not opened:
        if path.suffix.lower() == ".wav":
            if mci_send(f'open "{s}" type waveaudio alias {ALIAS_MUSIC}') != 0:
                return False
        else:
            return False

    vol = max(0, min(1000, int(volume * 1000)))
    mci_send(f"setaudio {ALIAS_MUSIC} volume to {vol}")

    play_cmd = f"play {ALIAS_MUSIC}" + (" repeat" if loop else "")
    return mci_send(play_cmd) == 0


def play_background_ffplay(path, loop, volume):
    ffplay = shutil.which("ffplay")
    if not ffplay:
        return None

    args = [
        ffplay,
        "-nodisp",
        "-hide_banner",
        "-loglevel",
        "quiet",
        "-af",
        f"volume={volume}",
    ]

    if loop:
        args.extend(["-loop", "0"])

    args.append(str(path))

    try:
        return subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except OSError:
        return None


def play_background_wav(path):
    import winsound

    try:
        winsound.PlaySound(
            str(path),
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
        )
        return True
    except RuntimeError:
        return False


def play_one_shot(path, volume):
    if not path.is_file():
        return

    if sys.platform == "win32":
        close_sfx_alias()
        s = str(path).replace("\\", "/")

        ok = mci_send(f'open "{s}" type mpegvideo alias {ALIAS_SFX}') == 0
        if not ok and path.suffix.lower() == ".wav":
            ok = mci_send(f'open "{s}" type waveaudio alias {ALIAS_SFX}') == 0

        if ok:
            vol = max(0, min(1000, int(volume * 1000)))
            mci_send(f"setaudio {ALIAS_SFX} volume to {vol}")
            mci_send(f"play {ALIAS_SFX}")
            return

    ffplay = shutil.which("ffplay")
    if ffplay:
        try:
            subprocess.Popen(
                [
                    ffplay,
                    "-nodisp",
                    "-hide_banner",
                    "-loglevel",
                    "quiet",
                    "-af",
                    f"volume={volume}",
                    "-autoexit",
                    str(path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
        except OSError:
            pass


def stop_music_impl(mgr):
    if mgr.backend == "mci":
        close_music_alias()

    elif mgr.backend == "wav":
        import winsound

        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except RuntimeError:
            pass

    elif mgr.backend == "ff" and mgr.ffplay_proc:
        try:
            mgr.ffplay_proc.terminate()
            mgr.ffplay_proc.wait(timeout=2)
        except Exception:
            try:
                mgr.ffplay_proc.kill()
            except Exception:
                pass
        mgr.ffplay_proc = None

    mgr.backend = None


def on_exit():
    global _global_manager
    if _global_manager:
        stop_music_impl(_global_manager)


atexit.register(on_exit)


class SoundManager:
    SFX_FILES = {
        "bonus": "Bonus.mp3",
        "win": "Win.mp3",
        "lose": "Lose.mp3",
        "explosion": "Explosion.mp3",
        "hit": "Hit.mp3",
        "button": "Button.mp3",
        "next_level": "NextLevel.mp3",
        "door": "Door.mp3",
    }

    def __init__(self):
        global _global_manager
        self.volume = 0.5
        self.music_path = None
        self.sfx_paths = {}

        for key, filename in self.SFX_FILES.items():
            p = resource_path(f"Sounds/{filename}")
            if p.is_file():
                self.sfx_paths[key] = str(p)

        self.backend = None
        self.ffplay_proc = None
        _global_manager = self

    def set_volume(self, v):
        self.volume = max(0.0, min(1.0, float(v)))
        if self.backend == "mci" and sys.platform == "win32":
            x = max(0, min(1000, int(self.volume * 1000)))
            mci_send(f"setaudio {ALIAS_MUSIC} volume to {x}")

    def set_music(self, path):
        self.music_path = path

    def play_music(self, loop=True):
        path_str = self.music_path or find_music_file()
        if not path_str:
            return

        path = Path(path_str)
        if not path.is_file():
            return

        stop_music_impl(self)

        if sys.platform == "win32" and play_background_windows(path, loop, self.volume):
            self.backend = "mci"
            return

        if path.suffix.lower() == ".wav" and play_background_wav(path):
            self.backend = "wav"
            return

        proc = play_background_ffplay(path, loop, self.volume)
        if proc:
            self.ffplay_proc = proc
            self.backend = "ff"

    def stop_music(self):
        stop_music_impl(self)

    def play_sound(self, name):
        path_str = self.sfx_paths.get(name)
        if not path_str:
            return
        play_one_shot(Path(path_str), self.volume)


sound_manager = SoundManager()