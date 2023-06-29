import time

from functools import wraps


class DeltaTime:
    """A class to keep track of time between calls.

        delta_time = DeltaTime()
        print(dt.dt)
        sleep(1)
        print(dt.dt)

    Pygame comes with its own time tracking function in pygame.time, but
    Cooldown and DeltaTime are still useful enough for other frameworks like
    pyglet, so we're tracking time outself.
    """

    def __init__(self):
        self.prev = time.time()

    @property
    def dt(self):
        now = time.time()
        dt = now - self.prev
        self.prev = now
        return dt


class CooldownLegacy:
    """A cooldown class, checking the delta time between start and now.

        cooldown = Cooldown(5)
        cooldown = Cooldown(5, start=1)

    A trigger class to wait for n seconds.

    The optional 'start' parameter gives an initial start time, so a Cooldown
    with 5 seconds can be created, that is already cold or has only 1 frame
    left.

    If started, it saves the current time as t0.  On every check, it compares
    the then current time with t0 and returns as 'cold' if the cooldown time
    has passed.

    The cooldown can be paused, in which case it saves the time left.  On
    restart, it'll set again t0 to the current time and continues to compare as
    normal against the left cooldown time.

    At any time, the cooldown can be reset to its initial or a new value.

    Parameters:

        seconds: float - Seconds to cool down

    Attributes:

        temperature: float - "temperature" to cool down from
        init: float - default to initialize the cooldown after each reset()
        paused: bool = False - to temporarily disable the cooldown

    Methods:

        start()

            set start time of cooldown to now, start comparing delta time

            The cooldown is started at creation time, but can be immediately
            paused by chaining.  See pause below.

        pause()

            remember time left, stop comparing delta time.  This can also be
            used to create an cooldown that's not yet running by chaining to
            the constructor:

                cooldown = Cooldown(10).pause()


        reset()
        reset(new_cooldown_time)

            set t0 to now, leave pause state as is, optionally set delta time
            to new value


    Synopsis:

        cooldown = Cooldown(5)

        while True:
            do_stuff()

            if key_pressed
                if key == 'P':
                    cooldown.pause()
                elif key == 'ESC':
                    cooldown.start()

            if cooldown.cold:
                launch_stuff()
                cooldown.reset()

    """

    def __init__(self, temperature, start=None):
        self.init = temperature
        self.paused = False

        self.reset()

        if start:
            self._temperature = start

    def reset(self, new=None):
        """reset the cooldown, optionally pass a new temperature

            cooldown.reset(new_temp) -> self

        Can be chained.
        """

        if new:
            self.init = new

        self.t0 = time.time()
        self._temperature = self.init
        self.paused = False

        return self

    @property
    def temperature(self):
        """the temperature of the cooldown object

            time_left = cooldown.temperature
        """
        if self.paused:
            return self._temperature
        else:
            passed = time.time() - self.t0
            return self._temperature - passed

    @temperature.setter
    def temperature(self, val):
        self._temperature = val

    @property
    def cold(self):
        """the state of the cooldown

            if cooldown.cold:
                ...

        the cooldown is cold, if all its time has passed.  From here, you can
        either act on it and/or reset.

        Note that this will return the time left in the cooldown, if it is paused.
        """
        if self.paused:
            return self._temperature <= 0
        else:
            return self.t0 + self._temperature < time.time()

    def pause(self):
        """pause the cooling down

            cooldown.pause()

        """
        self.paused = True
        self._temperature -= time.time() - self.t0

        return self

    def start(self):
        """(re-)start the cooldown after a pause.

            cooldown.start()
        """
        self.t0 = time.time()
        self.paused = False

        return self


def cooldown(f):
    """Save us from seeing the cooldown boilerplate 10 times in every GameState.

    The class of the decorated method is expected to have a Cooldown instance
    named cooldown.  That's it.

    Class attributes:

        self.cooldown           The current cooldown timer

    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.cooldown.cold:
            self.cooldown.reset()
            return f(self, *args, **kwargs)
        return self.cooldown.temperature
    return wrapper


class Cooldown:
    """A cooldown class, checking the delta time between start and now.

        cooldown = Cooldown(5)
        cooldown = Cooldown(5, start=1)

    A trigger class to wait for n seconds.

    The optional 'start' parameter gives an initial start time, so a Cooldown
    with 5 seconds can be created, that is already cold or has only 1 frame
    left.

    If started, it saves the current time as t0.  On every check, it compares
    the then current time with t0 and returns as 'cold' if the cooldown time
    has passed.

    The cooldown can be paused, in which case it saves the time left.  On
    restart, it'll set again t0 to the remaining time and continues to compare
    as normal against the left cooldown time.

    At any time, the cooldown can be reset to its initial or a new value.

    Parameters:

        duration: float - Seconds to cool down

    Attributes:

        remaining: float        - "temperature" to cool down from
        [temperature:           - aliased to remaining for backward compatibility]
        duration: float         - default to initialize the cooldown after each reset()
        paused: bool = False    - to temporarily disable the cooldown
        hot: bool               - there is stil time remaining before cooldown
        cold: bool              - time of the cooldown has run out

    Methods:

        start()

            set start time of cooldown to now, start comparing delta time

            The cooldown is started at creation time, but can be immediately
            paused by chaining.  See pause below.

        pause()

            remember time left, stop comparing delta time.  This can also be
            used to create an cooldown that's not yet running by chaining to
            the constructor:

                cooldown = Cooldown(10).pause()


        reset()
        reset(new_cooldown_time)

            set t0 to now, remove pause state, optionally set delta time to new
            value


    Synopsis:

        cooldown = Cooldown(5)

        while True:
            do_stuff()

            if key_pressed
                if key == 'P':
                    cooldown.pause()
                elif key == 'ESC':
                    cooldown.start()

            if cooldown.cold:
                launch_stuff()
                cooldown.reset()

    """
    def __init__(self, duration, start=None):
        self.duration = duration
        self.t0 = time.time()
        self.paused = False

        if start:
            self._remaining = self.duration - start 

    def reset(self, new=None):
        """reset the cooldown, optionally pass a new temperature

            cooldown.reset(new_temp) -> self

        Can be chained.
        """
        if new:
            self.duration = new
        self.t0 = time.time()
        self.paused = False
        return self

    @property
    def cold(self):
        """the state of the cooldown

            if cooldown.cold:
                ...

        the cooldown is cold, if all its time has passed.  From here, you can
        either act on it and/or reset.
        """
        return self.remaining <= 0

    @property
    def hot(self):
        """the state of the cooldown

            if cooldown.hot:
                return

        the cooldown is hot, when there is still time remaining.  Use this to
        bail out, if you are waiting for a cooldown.
        """
        return not self.cold

    @property
    def remaining(self):
        """the remaining time before cooldown.  This is also aliased to
        "temperature"

            time_left = cooldown.remaining
            time_left = cooldown.temperature

        Assigning to this value will change the current stateof the cooldown
        accordingly.
        """
        if self.paused:
            return self._remaining
        else:
            remaining = self.duration - (time.time() - self.t0)
            return remaining if remaining >= 0 else 0

    @remaining.setter
    def remaining(self, t):
        if self.paused:
            self._remaining = t
        if not self.paused:
            self.t0 = time.time() - (self.duration - t)

    def pause(self):
        """pause the cooling down

            cooldown.pause()

        This function can be chained to directly pause from the constructor:

            cd = Cooldown(60).pause()
        """
        self._remaining = self.remaining
        self.paused = True

        return self

    def start(self):
        """(re-)start the cooldown after a pause.

            cooldown.start()
        """
        if not self.paused: return self

        self.paused = False
        self.remaining = self._remaining

        return self
