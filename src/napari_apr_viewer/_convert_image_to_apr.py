from enum import Enum
from typing import TYPE_CHECKING
import pyapr
from magicgui import magic_factory

if TYPE_CHECKING:
    import napari


class DTypes(Enum):
    uint16 = 'uint16'
    float32 = 'float32'


@magic_factory(call_button="Run",
               relative_error={'widget_type': 'FloatSlider', 'min': 0.0, 'max': 1.0, 'step': 0.01})
def convert_image_to_apr(
        layer: "napari.types.ImageData",
        data_type: DTypes,
        relative_error: float = 0.1,
        voxel_size_dim0: float = 1.0,
        voxel_size_dim1: float = 1.0,
        voxel_size_dim2: float = 1.0,
        smoothing: float = 1.0,
        intensity_threshold: float = 0.0,
        sigma_threshold: float = 0.0,
        grad_threshold: float = 0.0,
        auto_find_sigma_and_grad_threshold: bool = True,
        inverted_intensity: bool = False,
        output_name: str = 'conversion_result'
) -> "napari.types.LayerDataTuple":
    """
    Convert a pixel image in a given layer to an APR.
    """
    par = pyapr.APRParameters()
    par.dz = voxel_size_dim0
    par.dx = voxel_size_dim1
    par.dy = voxel_size_dim2
    par.gradient_smoothing = smoothing
    par.Ip_th = intensity_threshold
    par.rel_error = relative_error
    par.sigma_th = sigma_threshold
    par.grad_th = grad_threshold
    par.auto_parameters = auto_find_sigma_and_grad_threshold

    converter = pyapr.converter.FloatConverter()
    converter.set_parameters(par)
    converter.verbose = True

    apr = pyapr.APR()
    parts = pyapr.ShortParticles() if data_type.value == 'uint16' else pyapr.FloatParticles()

    layer = layer.astype(data_type.value)
    print(layer.shape)
    converter.get_apr(apr, layer.max()-layer if inverted_intensity else layer)
    parts.sample_image(apr, layer)

    print('Computational ratio (#pixels / #particles): {:.2f}'.format(apr.computational_ratio()))

    ldata = pyapr.APRSlicer(apr, parts)
    meta = {'name': output_name,
            'rgb': False,
            'multiscale': False,
            'contrast_limits': [parts.min(), parts.max()],
            'scale': [par.dz, par.dx, par.dy]}
    return ldata, meta, 'image'
