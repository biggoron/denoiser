from normalizer import Normalizer

class VoiceBuffer():
    def __init__(self, size=1000, start=0, end=0, target_log_power=-8.5):
        self.buffer = []
        self.size = 16 * size
        self.start = start
        self.end = end
        self.normalizer = Normalizer(target_log_power=target_log_power)
        
    @property
    def is_full(self):
        return (self.end - self.start) > self.size

    def append(self, data):
        if not self.buffer:
            self.buffer = data
        else:
            self.buffer += data
        nb_samples = len(data) / 2
        self.end += nb_samples

    def flush(self):
        self.start = self.end
        b = self.buffer
        self.buffer = []
        return b

    def set(self, start, end):
        self.start = start
        self.end = end

    def reset(self):
        self.buffer = []
        self.set(0, 0)
