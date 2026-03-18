from pynput import keyboard


class HotKeyListener:
    def __init__(self, callback_press, callback_release, initial_keys=None):
        self.pressed = set()
        self.callback_press = callback_press
        self.callback_release = callback_release
        self.triggered = False

        # Default to Win + Shift if nothing is provided
        self.target_keys = initial_keys if initial_keys else ["cmd", "shift"]

        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()

    def update_keys(self, new_keys):
        """Update the target hotkey dynamically"""
        self.target_keys = new_keys
        self.pressed.clear()
        self.triggered = False

    def _is_combo_pressed(self):
        # Convert set of current keys to list of string names for comparison
        current_names = []
        for k in self.pressed:
            if hasattr(k, "name"):
                current_names.append(k.name)
            elif hasattr(k, "char"):
                current_names.append(k.char)

        # Check if all target keys are in the currently pressed set
        return all(target in current_names for target in self.target_keys)

    def on_press(self, key):
        self.pressed.add(key)
        if self._is_combo_pressed():
            if not self.triggered:
                self.triggered = True
                self.callback_press()

    def on_release(self, key):
        if key in self.pressed:
            self.pressed.discard(key)

        if self.triggered:
            if not self._is_combo_pressed():
                self.triggered = False
                self.callback_release()
