from threading import Thread, Condition

class PauseableThread(Thread):
    def __init__(self, name, callback, *args, **kwargs):
        super().__init__()
        self.daemon = True
        self.paused = True  # start out paused
        self.state = Condition()
        self.name = name
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.resume()
            while True:
                with self.state:
                    if self.paused:
                        self.state.wait()  # block execution until notified
                if self.callback:
                    self.callback(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
            print(f"thread {self.name} paused")
            self.paused = True

    def pause(self):
        with self.state:
            self.paused = True  # block
            print(f"thread {self.name} paused")

    def resume(self):
        with self.state:
            self.paused = False
            print(f"thread {self.name} resumed")
            self.state.notify()  # unblock if waiting