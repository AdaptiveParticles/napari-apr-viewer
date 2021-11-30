import pyapr
from napari.layers import Image, Labels


def apr_to_labels(apr, parts, **kwargs):
    """
    Return a Labels layer with an ``APRSlicer`` object as the data.

    Parameters
    ----------
    apr : pyapr.APR
        APR object.
    parts : ParticleData
        Particle labels.
    **kwargs : dict
        Keyword arguments passed to the Image layer. The option 'multiscale' is set to False.
        If 'scale' is not provided, it is set according to the voxel size of the APR parameters.

    Returns
    -------
    layer : Labels
        Labels layer constructed from the APR
    """
    kwargs['multiscale'] = False
    if 'scale' not in kwargs:
        par = apr.get_parameters()
        kwargs['scale'] = [par.dz, par.dx, par.dy]
    return Labels(data=pyapr.APRSlicer(apr, parts, tree_mode='max'), **kwargs)


def apr_to_image(apr, parts, **kwargs):
    """
    Return an Image layer with an ``APRSlicer`` object as the data.

    Parameters
    ----------
    apr : pyapr.APR
        APR object.
    parts : ParticleData
        Particle intensity values.
    **kwargs : dict
        Keyword arguments passed to the Image layer. The options 'multiscale' and 'rgb' are both set to False.
        If 'contrast_limits' and 'scale' are not provided, these are set according to the range of values in
        `parts` and the voxel size of the APR parameters, respectively.

    Returns
    -------
    layer : Image
        Image layer constructed from the APR
    """

    kwargs['multiscale'] = False
    kwargs['rgb'] = False
    if 'contrast_limits' not in kwargs:
        kwargs['contrast_limits'] = [parts.min(), parts.max()]
    if 'scale' not in kwargs:
        par = apr.get_parameters()
        kwargs['scale'] = [par.dz, par.dx, par.dy]
    return Image(data=pyapr.APRSlicer(apr, parts), **kwargs)
