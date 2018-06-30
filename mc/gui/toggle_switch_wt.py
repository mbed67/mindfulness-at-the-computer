from PyQt5 import QtCore
from PyQt5 import QtWidgets


class ToggleSwitchWt(QtWidgets.QWidget):
    toggled_signal = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.updating_gui_bool = False

        self.turn_on_off_qcb = QtWidgets.QCheckBox()
        self.turn_on_off_qcb.toggled.connect(self._on_toggled)
        on_off_qhl = QtWidgets.QHBoxLayout()
        on_off_qhl.setContentsMargins(0, 0, 0, 0)
        on_off_qhl.addWidget(QtWidgets.QLabel(self.tr("Turn the dialog and notifications on or off")))
        on_off_qhl.addStretch(1)
        on_off_qhl.addWidget(self.turn_on_off_qcb)
        self.setLayout(on_off_qhl)

    def _on_toggled(self, i_checked: bool):
        if self.updating_gui_bool:
            return
        self.toggled_signal.emit(i_checked)

    def update_gui(self, i_enabled: bool):
        pass