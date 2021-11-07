import time


class Event:
    def __init__(self, name):
        self.name = name
        self.time_generated = time.time()


class EventsManager:
    _events = []

    @classmethod
    def get_all_events(cls):
        return cls._events

    @classmethod
    def add_event(cls, event: Event):
        cls._events.append(event)

    @classmethod
    def get_next_event(cls):
        try:
            return cls._events.pop(-1)
        except IndexError:
            return None

    @classmethod
    def clear_all_events(cls):
        cls._events.clear()
