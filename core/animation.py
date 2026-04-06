from typing import Optional

from core.model import RealTimeModel # Assuming RealTimeModel is defined in core.model

class AnimationHandler:
    """
    This class is a handler for animations in game. It uses an underlying RealTimeModel and offers some
    methods to run animations, query states, etc. (Ported from animationhandlerunit.pas)
    """
    def __init__(self, a_model: RealTimeModel):
        self._already_triggered: bool = False
        self._anim_pos: float = 0.0 # Current position in the animation (0.0 to 1.0)
        self._anim_seconds: float = 1.0 # Duration of the current animation in seconds
        self._anim_num: int = 0 # Index of the current animation
        self._model: RealTimeModel = a_model

        self.start(0, 1.0) # Initialize with default animation

    @property
    def current_anim(self) -> int:
        return self._anim_num

    @property
    def position(self) -> float:
        return self._anim_pos

    @position.setter
    def position(self, value: float):
        self._anim_pos = value

    @property
    def model(self) -> RealTimeModel:
        return self._model

    def update(self, delta: float) -> bool:
        """
        Move the animation by delta. If the animation finishes, it restarts.
        Returns true if the animation finished (looped).
        """
        self._anim_pos += delta / self._anim_seconds
        if self._anim_pos >= 1.0:
            self._already_triggered = False
            self._anim_pos -= 1.0 # Loop the animation
            return True
        return False

    def restart(self):
        """Restart the current animation."""
        self._anim_pos = 0.0
        self._already_triggered = False

    def start(self, anim_num: int, anim_seconds: float):
        """
        Start a new animation. You must specify the animation index and the desired duration in seconds.
        """
        self._anim_pos = 0.0
        self._anim_num = anim_num
        self._anim_seconds = anim_seconds
        self._already_triggered = False

    def trigger(self) -> bool:
        """
        Tells if the animation encountered the trigger. This call returns true only once per animation,
        and only if the trigger position is passed.
        """
        result = (not self._already_triggered) and self._model.trigger_passed(self._anim_num, self._anim_pos)
        if result:
            self._already_triggered = True
        return result

    def change_current_anim(self, num: int):
        """
        Change the current animation leaving unaltered the position and the duration of the previous animation.
        """
        self._anim_num = num

    def interpolate(self):
        """
        Interpolate the underlying model with the data (anim index and position) from this handler.
        """
        self._model.interpolate(self._anim_num, self._anim_pos)