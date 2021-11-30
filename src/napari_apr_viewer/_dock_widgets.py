from napari_plugin_engine import napari_hook_implementation
from ._APRViewer import APRViewer
from ._convert_image_to_apr import convert_image_to_apr
from ._threshold import threshold


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [APRViewer, convert_image_to_apr, threshold]
