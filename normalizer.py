from wav_utils import pcm_to_numpy
from spec_utils import estimate_db_correction
from scipy import signal
import numpy as np

class Normalizer:
    def __init__(self, target_log_power=-12, time_filter_length=0.3):
        self.target_log_power = target_log_power
        self.state = int(10 * time_filter_length) * [0] # Initial correction is 0 db
        self.offset = 0

    def normalize(self, batch):
        batch = pcm_to_numpy(batch)
        _, _, spectrogram = signal.spectrogram(
            batch,
            fs=16e3,
            window='hamming',
            nperseg=16*25,
            noverlap=16*15,
            scaling='spectrum')
        corrections_db, state, offset = estimate_db_correction(
            spectrogram,
            output_shape=len(batch),
            ref=self.target_log_power,
            state=self.state,
            offset=self.offset)
        self.state = state
        self.offset = offset
        corrected = np.sqrt(np.exp(corrections_db)) * batch
        scaled_and_clipped = np.clip(corrected * (2**15), -2**15, 2**15 - 1)
        return list(scaled_and_clipped)
