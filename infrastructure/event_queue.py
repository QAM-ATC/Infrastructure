from queue import PriorityQueue


class EventQueue(PriorityQueue):
    def __init__(self, start_time, *args, **kwargs):
        self.current_time = start_time
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):  # may be bad for performance
        event = super().get(*args, **kwargs)
        self.current_time = event.event_time
        return event

    def update_future_data(self, future_data):
        for data_event in future_data:
            self.put(data_event)
    # we may or may not want to use this.. can manually put in the "main loop"
