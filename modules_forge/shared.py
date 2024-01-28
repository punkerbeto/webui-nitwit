import cv2
import os
import torch

from modules.paths import models_path
from ldm_patched.modules import model_management
from ldm_patched.modules.model_patcher import ModelPatcher


controlnet_dir = os.path.join(models_path, 'ControlNet')
os.makedirs(controlnet_dir, exist_ok=True)

preprocessor_dir = os.path.join(models_path, 'ControlNetPreprocessor')
os.makedirs(preprocessor_dir, exist_ok=True)

shared_preprocessors = {}


def add_preprocessor(preprocessor):
    global shared_preprocessors
    p = preprocessor()
    shared_preprocessors[p.name] = p
    return


class PreprocessorParameter:
    def __init__(self, minimum=0.0, maximum=1.0, step=0.01, label='Parameter 1', value=0.5, visible=False, **kwargs):
        self.gradio_update_kwargs = dict(
            minimum=minimum, maximum=maximum, step=step, label=label, value=value, visible=visible, **kwargs
        )


class PreprocessorBase:
    def __init__(self):
        self.name = 'PreprocessorBase'
        self.tag = None
        self.slider_1 = PreprocessorParameter()
        self.slider_2 = PreprocessorParameter()
        self.slider_3 = PreprocessorParameter()
        self.model_patcher = None

    def setup_model_patcher(self, model, load_device=None, offload_device=None, **kwargs):
        if load_device is None:
            load_device = model_management.get_torch_device()

        if offload_device is None:
            offload_device = torch.device('cpu')

        self.model_patcher = ModelPatcher(model=model, load_device=load_device, offload_device=offload_device, **kwargs)
        return

    def process_before_every_sampling(self, process, cnet):
        return


class PreprocessorNone(PreprocessorBase):
    def __init__(self):
        super().__init__()
        self.name = 'None'

    def __call__(self, input_image, slider_1=None, slider_2=None, slider_3=None, **kwargs):
        return input_image


class PreprocessorCanny(PreprocessorBase):
    def __init__(self):
        super().__init__()
        self.name = 'canny'
        self.tag = 'Canny'
        self.slider_1 = PreprocessorParameter(minimum=0, maximum=256, step=1, value=100, label='Low Threshold', visible=True)
        self.slider_2 = PreprocessorParameter(minimum=0, maximum=256, step=1, value=200, label='High Threshold', visible=True)

    def __call__(self, input_image, slider_1=100, slider_2=200, slider_3=None, **kwargs):
        canny_image = cv2.cvtColor(cv2.Canny(input_image, int(slider_1), int(slider_2)), cv2.COLOR_GRAY2RGB)
        return canny_image


add_preprocessor(PreprocessorNone)
add_preprocessor(PreprocessorCanny)
