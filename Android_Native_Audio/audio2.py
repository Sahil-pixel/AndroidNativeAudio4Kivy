from jnius import autoclass
from android.runnable import run_on_ui_thread

# Android Classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
context = PythonActivity.mActivity

Build_VERSION = autoclass('android.os.Build$VERSION')
AudioAttributesBuilder = autoclass('android.media.AudioAttributes$Builder')
SoundPoolBuilder = autoclass('android.media.SoundPool$Builder')
SoundPoolLegacy = autoclass('android.media.SoundPool')
AudioAttributes = autoclass('android.media.AudioAttributes')

# Singleton SoundPoolManager
class SoundPoolManager:
    _instance = None

    def __init__(self, max_streams=20):
        if SoundPoolManager._instance:
            raise Exception("Use get_instance() instead!")

        if Build_VERSION.SDK_INT >= 21:
            audio_attributes = AudioAttributesBuilder() \
                .setUsage(AudioAttributes.USAGE_GAME) \
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                .build()

            self.sound_pool = SoundPoolBuilder() \
                .setMaxStreams(max_streams) \
                .setAudioAttributes(audio_attributes) \
                .build()
        else:
            self.sound_pool = SoundPoolLegacy(max_streams, 3, 0)  # STREAM_MUSIC = 3

        print("SoundPoolManager initialized.")

    @classmethod
    def get_instance(cls, max_streams=20):
        if cls._instance is None:
            cls._instance = cls(max_streams)
        return cls._instance

    def release(self):
        self.sound_pool.release()
        SoundPoolManager._instance = None
        print("SoundPool released.")

# Sound Class
class Sound:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sound_pool_manager = SoundPoolManager.get_instance()
        self.sound_pool = self.sound_pool_manager.sound_pool

        # Load from file path (not assets)
        self.sound_id = self.sound_pool.load(file_path, 1)

        self._volume = 1.0
        self._loop = 0
        self.rate = 1.0
        self.stream_id = None

        print(f"[Sound] Loaded '{file_path}' with ID {self.sound_id}")

    @run_on_ui_thread
    def play(self):
        self.stream_id = self.sound_pool.play(
            self.sound_id,
            self._volume,
            self._volume,
            1,    # Priority
            self._loop,
            self.rate
        )
        if self.stream_id == 0:
            print(f"[Sound] Failed to play '{self.file_path}'")
        else:
            print(f"[Sound] Playing '{self.file_path}' Stream ID: {self.stream_id}")

    @run_on_ui_thread
    def stop(self):
        print(self.stream_id)
        if self.stream_id:
            self.sound_pool.stop(self.stream_id)
            print(f"[Sound] Stopped '{self.file_path}' Stream ID: {self.stream_id}")

    @run_on_ui_thread
    def pause(self):
        if self.stream_id is not None:
            self.sound_pool.pause(self.stream_id)
            print(f"[Sound] Paused '{self.file_path}' Stream ID: {self.stream_id}")

    @run_on_ui_thread
    def resume(self):
        if self.stream_id is not None:
            self.sound_pool.resume(self.stream_id)
            print(f"[Sound] Resumed '{self.file_path}' Stream ID: {self.stream_id}")

    def unload(self):
        self.sound_pool.unload(self.sound_id)
        print(f"[Sound] Unloaded '{self.file_path}'")

    # Volume Property
    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = float(max(0.0, min(1.0, value)))
        if self.stream_id is not None:
            self.sound_pool.setVolume(self.stream_id, self._volume, self._volume)
        print(f"[Sound] Volume set to {self._volume} for '{self.file_path}'")

    # Loop Property
    @property
    def loop(self):
        return self._loop == -1

    @loop.setter
    def loop(self, value):
        if isinstance(value, bool):
            self._loop = -1 if value else 0
        elif isinstance(value, int):
            self._loop = value
        else:
            raise ValueError("Loop must be a boolean or an integer (-1 for infinite, 0 for no loop)")
        print(f"[Sound] Loop set to {self._loop} for '{self.file_path}'")

# SoundLoader Class
class SoundLoader:
    @staticmethod
    def load(file_path):
        return Sound(file_path)

# Example Usage
if __name__ == '__main__':
    jump_sound = SoundLoader.load('/sdcard/Download/jump.ogg')  # Load from file path
    shoot_sound = SoundLoader.load('/sdcard/Download/shoot.ogg')

    jump_sound.play()
    shoot_sound.play()

    jump_sound.loop = True
    jump_sound.play()

    shoot_sound.volume = 0.5
    shoot_sound.play()

    jump_sound.pause()
    jump_sound.resume()

    jump_sound.stop()
    jump_sound.unload()
    shoot_sound.unload()

    SoundPoolManager.get_instance().release()