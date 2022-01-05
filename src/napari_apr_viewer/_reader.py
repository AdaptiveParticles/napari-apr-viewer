import os.path
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
        Path to a '.apr' file, or a list of such paths.

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
    Take a path or list of paths to '.apr' files and return a list of LayerData tuples, with one layer
    for each particle field (channel) in each file. The returned layers are given names in the format
    'file_name:particles_name'. Particle fields with 'segmentation' or 'label' in the name are returned
    as 'labels' layers, unless the data is floating point. Remaining fields are returned as 'image' layers.

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

    def get_kwargs(apr, parts, name, ltype='image'):
        par = apr.get_parameters()
        if ltype == 'image':
            meta = {'name': name,
                    'rgb': False,
                    'multiscale': False,
                    'contrast_limits': [parts.min(), parts.max()],
                    'scale': [par.dz, par.dx, par.dy]}
        else:
            meta = {'name': name,
                    'multiscale': False,
                    'scale': [par.dz, par.dx, par.dy]}
        return meta

    def read_apr(path: str):
        particle_fields = pyapr.io.get_particle_names(path)
        apr = pyapr.io.read_apr(path)
        base_name = path.split(os.path.sep)[-1].split('.')[0]
        particle_data = [(pyapr.io.read_particles(path, parts_name=p), p) for p in particle_fields]
        layer_types = ['labels' if (('label' in name or 'segmentation' in name)
                                    and not isinstance(parts, pyapr.FloatParticles))
                       else 'image' for parts, name in particle_data]
        return [(pyapr.data_containers.APRSlicer(apr, parts, tree_mode='max' if ltype == 'labels' else 'mean'),
                 '{}:{}'.format(base_name, name),
                 ltype)
                for (parts, name), ltype in zip(particle_data, layer_types)]

    if isinstance(path, str):
        path = [path]
    data = [x for p in path for x in read_apr(p)]
    return [(dd, get_kwargs(dd.apr, dd.parts, name, ltype), ltype) for dd, name, ltype in data]
