from typing import TYPE_CHECKING
import pyapr
from magicgui import magic_factory

if TYPE_CHECKING:
    import napari


@magic_factory(call_button="Run",
               threshold={'widget_type': 'FloatSlider', 'min': 0, 'max': 10000})
def threshold(data: "napari.types.ImageData", threshold: float) -> "napari.types.LabelsData":
    """Threshold an image and return a mask."""
    if not isinstance(data, pyapr.APRSlicer):
        return (data > threshold).astype(int)
    return pyapr.APRSlicer(data.apr, data.parts.copy() > threshold, tree_mode='max')
