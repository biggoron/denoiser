from wav_utils import pcm_to_numpy, numpy_to_pcm
import torch
from collections import namedtuple
from denoiser.enhance import get_estimate

class Denoiser:
    def __init__(self, model_path):
        self.model = torch.load(model_path)
        self.model.eval()
        # Replicates the args of the denoiser lib
        self.args = namedtuple('EstimateArgs', ['batch_size', 'streaming', 'dry'])(batch_size=1, streaming=True, dry=0)
        
    def denoise(self, pcm):
        input_audio = torch.Tensor(pcm_to_numpy(pcm)).unsqueeze(dim=0).unsqueeze(dim=0)
        output_audio = get_estimate(self.model, input_audio, self.args).numpy()
        return numpy_to_pcm(output_audio)
        
    
