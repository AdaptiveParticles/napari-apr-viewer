from napari_apr_viewer import napari_get_reader, napari_get_writer, napari_write_image
import pyapr
import numpy as np
import os


# tmp_path is a pytest fixture
def test_writer(tmp_path):
    """Test writer plugin."""
    file_dir = os.path.dirname(os.path.abspath(__file__))
    my_test_file = os.path.join(file_dir, 'files', 'spheres_tiny.apr')

    reader = napari_get_reader(my_test_file)
    layer_data_list = reader([my_test_file, my_test_file])
    layer_data_tuple = layer_data_list[0]

    # directory to write to
    target_path = os.path.join(tmp_path, 'some_dir')
    layer_types = [x[2] for x in layer_data_list]

    # get writer
    writer = napari_get_writer(target_path, layer_types)
    assert callable(writer)

    for i, x in enumerate(layer_data_list):
        if 'name' not in x[1]:
            x[1]['name'] = 'data{}'.format(i)

    # write multiple
    paths = writer(target_path, layer_data_list)
    assert isinstance(paths, list)
    assert len(paths) == len(layer_data_list) == 2
    assert None not in paths

    # check correctness
    apr_gt = layer_data_tuple[0].apr
    parts_gt = layer_data_tuple[0].parts
    assert _read_and_compare(paths, apr_gt, parts_gt)

    # write single
    target_path = os.path.join(tmp_path, 'myfile.apr')
    path = napari_write_image(target_path, layer_data_tuple)
    assert path is not None

    # check correctness
    assert _read_and_compare(path, apr_gt, parts_gt)


def _read_and_compare(path, apr_gt: pyapr.APR, parts_gt: pyapr.ShortParticles):
    if isinstance(path, str):
        apr, parts = pyapr.io.read(path)
        assert apr.total_number_particles() == apr_gt.total_number_particles() > 0
        assert all([apr.org_dims(i) == apr_gt.org_dims(i) for i in range(3)])
        assert len(parts) == len(parts_gt)
        np.testing.assert_allclose(np.array(parts, copy=False), np.array(parts_gt, copy=False))
        return True
    elif isinstance(path, list):
        return all([_read_and_compare(p, apr_gt, parts_gt) for p in path])
    return False
