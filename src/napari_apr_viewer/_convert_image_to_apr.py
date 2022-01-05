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
               relative_error={'widget_type': 'FloatSlider', 'min': 0.0, 'max': 0.5, 'step': 0.01,
                               'tooltip': 'Sets the error bound in the reconstruction condition of the APR. '
                                          'The input pixel values can be reconstructed from the APR with an '
                                          'error (relative to the \"local intensity scale\") of at most this '
                                          'value.'},
               smoothing={'tooltip': 'Controls the level of B-spline smoothing used in internal steps '
                                     '(e.g. to compute the signal gradient). Higher values mean more '
                                     'smoothing, while 0 corresponds to no smoothing. Typical range: 0-10. '},
               intensity_threshold={'tooltip': 'The image gradient is set to 0 in regions of lower intensity '
                                               'than this threshold.', 'min': 0, 'max': 65535},
               sigma_threshold={'tooltip': 'The \"local intensity scale\" is clipped from below to this value. ',
                                'min': 0, 'max': 65535},
               grad_threshold={'tooltip': 'Gradient values below this value are set to 0.',
                               'min': 0, 'max': 65535},
               auto_find_sigma_and_grad_threshold={'tooltip': 'Automatically compute \'sigma_threshold\' and '
                                                              '\'grad_threshold\' using Li thresholding on the '
                                                              'local intensity scale and gradient. Regions where '
                                                              'the intensity is below \'intensity_threshold\' '
                                                              'are ignored in this process.'},
               output_name={'tooltip': 'Name of the resulting napari image layer.'})
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
    converter.get_apr(apr, layer)
    parts.sample_image(apr, layer)

    print('Computational ratio (#pixels / #particles): {:.2f}'.format(apr.computational_ratio()))

    ldata = pyapr.APRSlicer(apr, parts)
    meta = {'name': output_name,
            'rgb': False,
            'multiscale': False,
            'contrast_limits': [parts.min(), parts.max()],
            'scale': [par.dz, par.dx, par.dy]}
    return ldata, meta, 'image'
