import napari
import numpy as np
import pyapr
from qtpy.QtWidgets import QWidget, QComboBox, QSlider, QLabel, QHBoxLayout, QVBoxLayout
from qtpy.QtCore import Qt


class APRViewer(QWidget):
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.setWindowTitle('APR Viewer settings')
        self.modes = ['constant', 'smooth', 'level']

        self.view_mode = QComboBox()
        self.view_mode.addItems(self.modes)
        self.view_mode.currentIndexChanged.connect(self._changeMode)

        self.mode_box = QHBoxLayout()
        self.mode_box.addWidget(QLabel('View mode:'))
        self.mode_box.addWidget(self.view_mode)

        self.res_slider = QSlider(Qt.Horizontal)
        self.res_slider.setRange(0, 5)
        self.res_slider.setValue(0)
        self.res_slider.valueChanged.connect(self._changeRes)

        self.res_label = QLabel('1:1')
        self.res_label.setAlignment(Qt.AlignHCenter)
        self.res_label.setMinimumWidth(50)

        self.ds_box = QHBoxLayout()
        self.ds_box.addWidget(QLabel('Downsample:'))
        self.ds_box.addWidget(self.res_slider)
        self.ds_box.addWidget(self.res_label)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.mode_box)
        self.vbox.addSpacing(10)
        self.vbox.addLayout(self.ds_box)
        self.setLayout(self.vbox)

    def _changeRes(self, value: int = 0):
        self.res_label.setText('1:{}'.format(str(2**value)))
        for layer in self.viewer.layers:
            if isinstance(layer.data, pyapr.APRSlicer):
                value_clamped = min(layer.data.apr.level_max() - 4, value)

                prev_value = layer.data.patch.level_delta
                layer.data.set_level_delta(-value_clamped)
                layer.translate = layer.translate * 2 ** (prev_value - value_clamped)
                par = layer.data.apr.get_parameters()
                layer.scale = [x * 2 ** value_clamped for x in [par.dz, par.dx, par.dy]]
                layer.refresh()

    def _changeMode(self, mode: [int, str]):
        mode = mode if isinstance(mode, str) else self.modes[mode]
        for layer in self.viewer.layers:
            if isinstance(layer.data, pyapr.APRSlicer) and isinstance(layer, napari.layers.Image):
                # set reconstruction mode
                layer.data.mode = mode

                # set reconstruction function
                if mode == 'constant':
                    layer.data.recon = pyapr.numerics.reconstruction.reconstruct_constant
                elif mode == 'smooth':
                    layer.data.recon = pyapr.numerics.reconstruction.reconstruct_smooth
                elif mode == 'level':
                    layer.data.recon = pyapr.numerics.reconstruction.reconstruct_level
                else:
                    raise ValueError('APRArray mode argument must be \'constant\', \'smooth\' or \'level\'')

                # set data type
                if mode == 'level':
                    layer.data.dtype = np.uint8
                else:
                    if isinstance(layer.data.parts, pyapr.FloatParticles):
                        layer.data.dtype = np.float32
                    elif isinstance(layer.data.parts, pyapr.LongParticles):
                        layer.data.dtype = np.uint64
                    elif isinstance(layer.data.parts, pyapr.ShortParticles):
                        layer.data.dtype = np.uint16
                    else:
                        raise ValueError('parts type not recognized')
                layer.refresh()
