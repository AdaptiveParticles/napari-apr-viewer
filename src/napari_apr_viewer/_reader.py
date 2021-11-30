import pyapr
from typing import List, Any, Optional, Union, Tuple, Dict
from napari.types import ReaderFunction
from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_get_reader(path: Union[str, List[str]]) -> Optional[ReaderFunction]:
    """
    Return a function capable of reading APR files into napari layer data.

    Parameters
    ----------
    path : str or list of str
        Path to a '.apr' file, or list of such paths.

    Returns
    -------
    function or None
        If the path is of the correct format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
        Otherwise returns ``None``.
    """
    if isinstance(path, list):
        for p in path:
            if not isinstance(p, str) or p.endswith('.apr'):
                return None
    elif isinstance(path, str):
        if not path.endswith('.apr'):
            return None
    return apr_reader


def apr_reader(path: Union[str, List[str]]) -> List[Tuple[Any, Dict, str]]:
    """
    Take a path or list of paths to '.apr' files and return a list of LayerData tuples.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is an APRSlicer, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer
        (currently always 'image').
    """

    def get_kwargs(apr, parts):
        par = apr.get_parameters()
        return {'rgb': False,
                'multiscale': False,
                'contrast_limits': [parts.min(), parts.max()],
                'scale': [par.dz, par.dx, par.dy]}

    def read_apr(path: str):
        apr, parts = pyapr.io.read(path)
        return pyapr.data_containers.APRSlicer(apr, parts)

    if isinstance(path, str):
        path = [path]
    data = [read_apr(p) for p in path]
    return [(dd, get_kwargs(dd.apr, dd.parts), 'image') for dd in data]
