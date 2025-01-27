#!/usr/bin/env python3

import sys
import time
import threading
import itertools

class LoadingSpinner:
    def __init__(self, description="Loading"):
        self.description = description
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.running = False
        self.spinner_thread = None

    def spin(self):
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.description}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f"\r✓ {self.description}\n")
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()