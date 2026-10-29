from manim_imports_ext import *


class BuildStills:
    """
    Scene mixin: saves a PNG of the frame at the end of every play() call
    (one per build) to <output dir>/stills/, next to the rendered video.
    Call save_still() to grab extra frames, e.g. while animations are skipped.
    For scenes built from long play() calls, set still_interval to also save
    a frame every still_interval seconds of scene time.
    """
    still_interval = None

    def setup(self):
        super().setup()
        self.still_count = 0
        self.next_interval_still_time = 0
        self.stills_dir = Path(self.file_writer.output_directory, "stills")
        if self.file_writer.write_to_movie:
            self.stills_dir.mkdir(parents=True, exist_ok=True)
            for old_still in self.stills_dir.glob("*.png"):
                old_still.unlink()

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        if not self.skip_animations:
            self.save_still()

    def emit_frame(self):
        super().emit_frame()
        if self.still_interval and not self.skip_animations and self.time >= self.next_interval_still_time:
            self.save_still()
            self.next_interval_still_time += self.still_interval

    def stills_every(self, interval):
        """Also save a still every `interval` seconds from now (None: stop)."""
        self.still_interval = interval
        self.next_interval_still_time = self.time

    def save_still(self):
        if not self.file_writer.write_to_movie:
            return
        self.camera.capture(*self.mobjects)
        self.still_count += 1
        path = Path(self.stills_dir, f"{self.__class__.__name__}_{self.still_count:03d}.png")
        self.camera.get_image().convert("RGB").save(path)
