from jnius import autoclass

MediaPlayer = autoclass('android.media.MediaPlayer')

class Sound:
    def __init__(self, file_path, loop=False, volume=1.0):
        self.media_player = MediaPlayer()
        self.media_player.setDataSource(file_path)
        self.media_player.prepare()

        self._loop = loop
        self.setloop(loop)

        self._volume = 1.0  # Default volume to prevent None issues
        self.setvolume(volume)  # Ensure valid volume

    def play(self):
        self.media_player.start()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()
        self.media_player.prepare()  # Required before replaying

    def setloop(self, loop=False):
        self.media_player.setLooping(loop)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        if self._loop != value:
            self._loop = value
            self.setloop(value)

    def setvolume(self, volume):
        """ Set volume between 0.0 and 1.0, ensuring correct range """
        if not isinstance(volume, (int, float)):
            raise TypeError(f"Volume must be a number, got {type(volume)}")

        volume = max(0.0, min(1.0, float(volume)))  # Clamping value
        #print(f"Setting volume: {volume}")  # Debugging statement

        self.media_player.setVolume(volume, volume)  # Left & Right channels
        self._volume = volume  # Store validated volume

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self.setvolume(value)  # Use setvolume to validate & set

class SoundLoaderL:
    @staticmethod
    def load(file_path, loop=False, volume=1.0):
        return Sound(file_path, loop, volume)

# Usage Example
if __name__ == "__main__":
    sound = SoundLoader.load("/sdcard/Music/sample.mp3", loop=True, volume=0.5)
    sound.play()

    try:
        sound.volume = 1.2  # Invalid value (should be clamped)
    except ValueError as e:
        print("Error:", e)  # Debugging

    sound.volume = 0.8  # Valid volume update
    sound.loop = False  # Toggle looping
