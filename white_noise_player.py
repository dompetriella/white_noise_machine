import signal
import threading

from pathlib import Path
from gpiozero import Button
from enum import Enum
import pygame


BASE_AUDIO_PATH = "/home/white/audio"
BUTTON_BOUNCE_TIME = 0.05
DEFAULT_VOLUME = 5
MAX_VOLUME = 10
FADE_DURATION = 500

STOP_PIN = 26
VOLUME_UP_PIN = 23
VOLUME_DOWN_PIN = 24

class AudioPress(Enum):
    RAIN = (17, "rain_sounds.wav")
    RIVER = (27, "river_sounds.mp3")
    BEACH = (22, "beach_sounds.mp3")

    def __init__(self, gpio_pin: int, audio_file_path: str):
        self.gpio_pin = gpio_pin
        self.audio_file_path = Path(BASE_AUDIO_PATH) / audio_file_path


transition_lock = threading.Lock()

current_volume = DEFAULT_VOLUME

rain_button = Button(AudioPress.RAIN.gpio_pin, bounce_time=BUTTON_BOUNCE_TIME)
river_button = Button(AudioPress.RIVER.gpio_pin, bounce_time=BUTTON_BOUNCE_TIME)
beach_button = Button(AudioPress.BEACH.gpio_pin, bounce_time=BUTTON_BOUNCE_TIME)
stop_button = Button(STOP_PIN, bounce_time=BUTTON_BOUNCE_TIME)
volume_up_button = Button(VOLUME_UP_PIN, bounce_time=BUTTON_BOUNCE_TIME)
volume_down_button = Button(VOLUME_DOWN_PIN, bounce_time=BUTTON_BOUNCE_TIME)

def apply_volume():
    pygame.mixer.music.set_volume(current_volume / MAX_VOLUME)

def on_audio_button_pressed(audio_press: AudioPress):
    if not transition_lock.acquire(blocking=False):
        return
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(FADE_DURATION)
        print(f"Playing {audio_press.name}")
        pygame.mixer.music.load(audio_press.audio_file_path)
        apply_volume()
        pygame.mixer.music.play(loops=-1, fade_ms=FADE_DURATION)
    finally:
        transition_lock.release()
    

def on_stop_button_pressed():
    if not transition_lock.acquire(blocking=False):
        return
    try:
        print("Stopping all audio")
        pygame.mixer.music.fadeout(FADE_DURATION)
    finally:
        transition_lock.release()

def on_volume_up_pressed():
    global current_volume
    if current_volume < MAX_VOLUME:
        current_volume += 1
    apply_volume()
    print(f"Current Volume: {current_volume}")

def on_volume_down_pressed():
    global current_volume
    if current_volume > 0:
        current_volume -= 1
    apply_volume()
    print(f"Current Volume: {current_volume}")

def main():
    pygame.mixer.init()

    rain_button.when_pressed = lambda: on_audio_button_pressed(AudioPress.RAIN)
    river_button.when_pressed = lambda: on_audio_button_pressed(AudioPress.RIVER)
    beach_button.when_pressed = lambda: on_audio_button_pressed(AudioPress.BEACH)
    volume_up_button.when_pressed = on_volume_up_pressed
    volume_down_button.when_pressed = on_volume_down_pressed
    stop_button.when_pressed = on_stop_button_pressed
    print("Buttons Primed")

    print("Ready for Input")

    signal.pause()

if __name__ == "__main__":
    main();