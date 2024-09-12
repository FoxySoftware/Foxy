import readchar


class Event:
    pass


class KeyPressed(Event):
    def __init__(self, value):
        self.value = value


class Repaint(Event):
    pass

class KeyEventGeneratorOriginal:
    def __init__(self, key_generator=None):
        self._key_gen = key_generator or readchar.readkey

    def next(self):
        return KeyPressed(self._key_gen())

class KeyEventGenerator:
    def __init__(self, key_generator=None):
        self._key_gen = key_generator or readchar.readkey

    def next(self):
        key = self._key_gen()
        if key  == "\x1a":
            raise KeyCtrlZInterrupt
        return KeyPressed(key)

class KeyCtrlZInterrupt(Exception):
    """Base class for custom exceptions."""
    def __init__(self, message= "Ctrl + Z Interruption ", code=100):
        super().__init__(message)  
        self.code = code          

    def __str__(self):
        # Provide a custom string representation
        return f"{self.args[0]} (Error code: {self.code})"
