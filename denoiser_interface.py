from wav_utils import pcm_to_numpy, numpy_to_pcm
import torch
from collections import namedtuple
from denoiser.enhance import get_estimate

class Denoiser:
    def __init__(self, model_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = torch.load(model_path).to(self.device)
        self.model.eval()
        # Replicates the args of the denoiser lib
        self.args = namedtuple('EstimateArgs', ['batch_size', 'streaming', 'dry'])(batch_size=1, streaming=True, dry=0)
        
    def denoise(self, pcm):
        input_audio = torch.Tensor(pcm_to_numpy(pcm)).unsqueeze(dim=0).unsqueeze(dim=0).to(self.device)
        output_audio = get_estimate(self.model, input_audio, self.args).cpu().numpy()
        return output_audio
        
    
