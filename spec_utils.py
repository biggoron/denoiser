import numpy as np
from scipy import signal
from more_itertools import chunked
from itertools import chain

def get_ranges(offset, jump):
    # Defines 3 ranges corresponding to harmonics
    range1 = range(offset, offset+3)
    range2 = range(offset + jump, offset + jump + 3)
    range3 = range(offset + jump * 2, offset + jump * 2 + 3)
    return list(chain(range1, range2, range3))

def find_res(s):
    # Finds the mean power in the most likely resonance zone
    maximum = -10e10
    max_offset = 0
    max_jump = 3
    for offset in range(0, 10):
        for jump in range(5, 10):
            if offset + jump * 2 + 3 > 30:
                continue
            total = np.sort(s[get_ranges(offset, jump)].flatten())[-10:].mean()
            if total > maximum:
                max_offset = offset
                max_jump = jump
                maximum = total
    return maximum

def estimate_db_correction(s, output_shape, ref = -12, state=[0]*3, offset=0):
    corrections = []
    print(ref)
    for i in chunked(range(s.shape[1]), 10):
        # by chunk of 100ms, only on first 30 coeffs
        batch = np.log(s[:30, i])
        res = np.apply_along_axis(find_res, 0, batch.mean(axis=1))
        boolean = (res - batch.mean()) > 2 # Indicates if there is enough resonance to calculate correction
        if boolean:
            state[offset] = (ref - res)
            offset = (offset + 1) % len(state)
        corrections += [np.mean(state)]
    return signal.resample(corrections, output_shape),  state, offset
