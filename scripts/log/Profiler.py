import time


class Profiler:
    def __init__(self, verbose=True):
        self.timers = {}
        self.verbose = verbose

    def start(self, label):
        """Start the timer for a given label."""
        self.timers[label] = time.time()

    def measure(self, label):
        """Return the elapsed time for a given label without removing it."""
        if label not in self.timers:
            raise ValueError(f"Timer '{label}' has not been started")
        return time.time() - self.timers[label]

    def finalize(self, label, verbose=None):
        """Return the elapsed time and remove the label from tracking."""
        verbose = verbose if verbose is not None else self.verbose

        if label not in self.timers:
            raise ValueError(f"Timer '{label}' has not been started")
        elapsed = time.time() - self.timers[label]
        del self.timers[label]
        if verbose:
            print(f"{label}: {elapsed:.3f}s")
        return elapsed
