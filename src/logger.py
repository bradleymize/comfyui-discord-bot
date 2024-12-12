import logging
import collections
import itertools

class LastNLinesHandler(logging.Handler):
    def __init__(self, max_lines=100):
        self.max_lines = max_lines
        self.buffer = collections.deque(maxlen=max_lines)
        super().__init__()

    def emit(self, record):
        self.buffer.append(self.format(record))
        if len(self.buffer) > self.max_lines:
            self.buffer.popleft()

    def get_last_n_lines(self):
        return '\n'.join(self.buffer)