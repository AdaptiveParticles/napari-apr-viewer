from napari_apr_viewer import napari_get_reader, napari_get_writer, napari_write_image
import os


# tmp_path is a pytest fixture
def test_writer(tmp_path):
    """Test writer plugin."""
    file_dir = os.path.dirname(os.path.abspath(__file__))
    my_test_file = os.path.join(file_dir, 'files', 'spheres_tiny.apr')
    orig_size = os.path.getsize(my_test_file)

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

    sizes = [os.path.getsize(p) for p in paths]
    for sz in sizes:
        assert sz == orig_size

    # write single
    target_path = os.path.join(tmp_path, 'myfile.apr')
    path = napari_write_image(target_path, layer_data_tuple)
    assert path is not None
    assert os.path.getsize(path) == orig_size
