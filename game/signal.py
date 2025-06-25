class Signal:
    def __init__(self):
        self._subscribers = []
        self._subscribers_to_remove = []

    def is_connected(self, callback):
        return callback in self._subscribers

    def connect(self, callback):
        if callable(callback) and callback not in self._subscribers:
            self._subscribers.append(callback)

    def connect_once(self, callback):
        if not callable(callback):
            return

        def wrapper(*args):
            self.disconnect(wrapper)
            callback(args)

        self._subscribers.append(wrapper)

    def disconnect(self, callback):
        if callback in self._subscribers:
            self._subscribers_to_remove.append(callback)

    def emit(self, *args):
        for callback in self._subscribers:
            callback(args)

        for callback in self._subscribers_to_remove:
            self._subscribers.remove(callback)

        self._subscribers_to_remove.clear()
