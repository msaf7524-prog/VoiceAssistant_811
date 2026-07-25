import threading


class AssistantService:

    def __init__(self):
        self.running = False
        self.worker = None

    def start(self, target):
        if self.running:
            return

        self.running = True

        self.worker = threading.Thread(
            target=target,
            daemon=True
        )

        self.worker.start()

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running
