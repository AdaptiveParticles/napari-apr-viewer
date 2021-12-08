from typing import TYPE_CHECKING
import pyapr
from magicgui import magic_factory

if TYPE_CHECKING:
    import napari


@magic_factory(call_button="Run")
def convert_apr_to_image(
        layer: "napari.types.ImageData",
        output_name: str = 'reconstruction_result'
) -> "napari.types.LayerDataTuple":
    """Reconstruct pixel image from an APR in a given layer"""
    if not isinstance(layer, pyapr.APRSlicer):
        print('Layer data is already a pixel image')
        return None
    par = layer.apr.get_parameters()
    scale = [x * 2**(-layer.patch.level_delta) for x in (par.dz, par.dx, par.dy)]
    shape = layer.apr.shape()
    scale = [scale[i] for i in range(3) if shape[i] > 1]
    return layer[:, :, :], {'name': output_name, 'scale': scale}, 'image'
