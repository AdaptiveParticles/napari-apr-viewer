from typing import TYPE_CHECKING
import pyapr
from magicgui import magic_factory

if TYPE_CHECKING:
    import napari


@magic_factory(call_button="Run",
               threshold={'widget_type': 'FloatSpinBox', 'max': 65536})
def threshold(data: "napari.types.ImageData", threshold: float) -> "napari.types.LayerDataTuple":
    """Threshold an image and return a mask."""
    if not isinstance(data, pyapr.reconstruction.APRSlicer):
        return (data > threshold).astype(int), {}, 'labels'
    par = data.apr.get_parameters()
    meta = {'scale': [par.dz, par.dx, par.dy]}
    mask = pyapr.ByteParticles(data.parts.copy() > threshold)
    return pyapr.reconstruction.APRSlicer(data.apr, mask, tree_mode='max'), meta, 'labels'
