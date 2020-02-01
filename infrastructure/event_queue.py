from queue import PriorityQueue


class EventQueue(PriorityQueue):
    def __init__(self, start_time, *args, **kwargs):
        self.current_time = start_time
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):  # may be bad for performance
        event = super().get(*args, **kwargs)
        self.current_time = event.event_time
        return event
