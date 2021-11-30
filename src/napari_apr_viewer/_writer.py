import os
import pyapr
from typing import List, Tuple, Dict, Any, Optional, Union
from napari.types import WriterFunction
from napari_plugin_engine import napari_hook_implementation

supported_types = ['image', 'labels']


@napari_hook_implementation
def napari_get_writer(path: str,
                      layer_types: List[str]) -> Optional[WriterFunction]:
    """
    Return a function capable of writing APR layer data to ``path``.

    Parameters
    ----------
    path : str
        Path to file or directory where data is to be written.
    layer_types : list of str
        List of layer types that will be provided to the writer function. Supported
        types are 'image' and 'labels'.

    Returns
    -------
    Callable or None
        A writer function that accepts the path, a list of ``LayerData`` tuples.
        If unable to write to the path or write the layer_data, returns ``None``.
    """
    for lt in set(layer_types):
        if lt not in supported_types:
            return None
    return napari_write_image if path else None


@napari_hook_implementation
def napari_write_image(path: str, data: List[Tuple[Any, Dict, str]]) -> List[Union[Any, str]]:
    """
    Write napari APR layer data to ``path``.

    Parameters
    ----------
    path : str
        Path to file where data is to be written

    data : list of tuples
        ``LayerData`` tuples to be written to file

    Returns
    -------
    ret : str, list of str or None
        The path(s) of successfully written data, or None if data could not be written.
    """
    def write_apr(path, data):
        if isinstance(data, pyapr.APRSlicer):
            if not path.endswith('.apr'):
                path = path + '.apr'
            pyapr.io.write(path, data.apr, data.parts)
            return path
        return None

    if isinstance(data, list):
        if not os.path.isdir(path):
            os.mkdir(path)
        ret = []
        for dd, meta, lt in data:
            name = meta['name'] + '.apr'
            ret.append(write_apr(os.path.join(path, name), dd))
        return ret
    elif isinstance(data, tuple):
        return write_apr(path, data[0])
    return write_apr(path, data)
