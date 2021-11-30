import os
import numpy as np
import pyapr
from napari_apr_viewer import napari_get_reader


# tmp_path is a pytest fixture
def test_reader(tmp_path):
    file_dir = os.path.dirname(os.path.abspath(__file__))
    my_test_file = os.path.join(file_dir, 'files', 'spheres_tiny.apr')

    # get reader
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0

    # read the file using pyapr
    apr, parts = pyapr.io.read(my_test_file)

    # make sure it's the same
    assert layer_data_tuple[0].apr.total_number_particles() == apr.total_number_particles() > 0
    assert len(layer_data_tuple[0].parts) == len(parts) == apr.total_number_particles()
    np.testing.assert_allclose(np.array(parts), np.array(layer_data_tuple[0].parts))


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
