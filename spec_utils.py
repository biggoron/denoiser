import numpy as np
from scipy import signal, interpolate
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
    for offset in range(0, 10):
        for jump in range(5, 10):
            if offset + jump * 2 + 3 > 30:
                continue
            total = s[get_ranges(offset, jump)].mean()
            if total > maximum:
                maximum = total
    return maximum

def estimate_db_correction(s, output_shape, ref = -12, state=[0]*3, offset=0):
    corrections = []
    print(ref)
    for i in chunked(range(s.shape[1]), 10):
        # by chunk of 100ms, only on first 30 coeffs
        batch = np.log(s[:30, i])
        res = find_res(batch.mean(axis=1))
        boolean = (res - batch.mean()) > 2 # Indicates if there is enough resonance to calculate correction
        if boolean:
            state[offset] = (ref - res)
            offset = (offset + 1) % len(state)
        corrections += [np.mean(state)]
    # return corrections, state, offset
    ratio = (output_shape - 2) / (len(corrections) - 1)
    x = [0] + [(elem * ratio)  + (ratio / 2) for elem in range(len(corrections))] + [output_shape - 1]
    y = [corrections[0]] + corrections + [corrections[-1]]
    f = interpolate.interp1d(x, y)
    signal_x = list(range(output_shape))
    return f(signal_x), state, offset
