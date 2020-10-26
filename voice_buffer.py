class VoiceBuffer():
    def __init__(self, size=16e3, start=0, end=0):
        self.buffer = None
        self.size = size
        self.start = start
        self.end = end
        
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
