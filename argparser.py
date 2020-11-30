import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Builds agc server')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port on which to run the server.')
    parser.add_argument('--buffer', type=int, default=1000,
                        help='Default buffer size in milliseconds.')
    parser.add_argument('--target_log_power', type=float, default=-8.5,
                        help='Default target log power for top resonants.')
    parser.add_argument('--time_filter_length', type=float, default=0.3,
                        help='Time over which AGC correction is smoothed. in sec.')
    args = parser.parse_args()
    return args
