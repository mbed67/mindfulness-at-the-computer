import logging
from PyQt5 import QtGui

import mc.gui.toggle_switch_wt
from mc.gui.reusable_components import *
from mc.model import SettingsM
from mc import mc_global

MIN_INTERVAL_INT = 1  # -in minutes
MAX_INTERVAL_INT = 99


class TimingSettingsWt(QtWidgets.QWidget):
    rest_settings_updated_from_settings_signal = QtCore.pyqtSignal(str)
    breathing_settings_updated_from_settings_signal = QtCore.pyqtSignal(str)
    rest_reset_button_clicked_signal = QtCore.pyqtSignal()
    rest_slider_value_changed_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.updating_gui_bool = False

        self.notification_interval_qsb = QtWidgets.QSpinBox()
        self.show_after_qsb = QtWidgets.QSpinBox()
        self.rest_interval_qsb = QtWidgets.QSpinBox()
        self.rest_reminder_qsr = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)  # Previously: QProgressBar()
        self.rest_reminder_reset_qpb = QtWidgets.QPushButton()  # -"Reset timer"
        self.overview_qlw = TimingOverviewWt()

        self._init_ui()
        self._connect_slots_to_signals()

    def _init_ui(self):
        # Limit the input values of the interval spinboxes
        self.notification_interval_qsb.setMinimum(MIN_INTERVAL_INT)
        self.notification_interval_qsb.setMaximum(MAX_INTERVAL_INT)
        self.rest_interval_qsb.setMinimum(MIN_INTERVAL_INT)
        self.rest_interval_qsb.setMaximum(MAX_INTERVAL_INT)

        # configure the slider with the remaining rest time
        self.rest_reminder_qsr.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.rest_reminder_qsr.setPageStep(5)

        # configure the button that resets the slider
        self.rest_reminder_reset_qpb.setIcon(QtGui.QIcon(mc.mc_global.get_icon_path("reload-2x.png")))
        self.rest_reminder_reset_qpb.setToolTip(self.tr("Reset the rest timer"))

        notification_interval_qll = QtWidgets.QLabel(self.tr("Interval every:"))
        notification_interval_qll.setFixedWidth(100)
        notification_interval_qhl = HorizontalBox()
        notification_interval_qhl.addWidget(notification_interval_qll)
        notification_interval_qhl.addWidget(self.notification_interval_qsb)
        notification_interval_qhl.addWidget(QtWidgets.QLabel(self.tr("minutes")))
        notification_interval_qhl.addStretch(1)

        show_after_qll = QtWidgets.QLabel(self.tr("Show after:"))
        show_after_qll.setFixedWidth(100)
        show_after_qhl = HorizontalBox()
        show_after_qhl.addWidget(show_after_qll)
        show_after_qhl.addWidget(self.show_after_qsb)
        show_after_qhl.addWidget(QtWidgets.QLabel(self.tr("notifications")))
        show_after_qhl.addStretch(1)

        rest_interval_qll = QtWidgets.QLabel(self.tr("Interval every:"))
        rest_interval_qll.setFixedWidth(100)
        rest_interval_qhl = HorizontalBox()
        rest_interval_qhl.addWidget(rest_interval_qll)
        rest_interval_qhl.addWidget(self.rest_interval_qsb)
        rest_interval_qhl.addWidget(QtWidgets.QLabel(self.tr("minutes")))
        rest_interval_qhl.addStretch(1)

        time_remaining_qhl = QtWidgets.QHBoxLayout()
        time_remaining_qhl.addWidget(QtWidgets.QLabel(self.tr("Time until next break:")))
        time_remaining_qhl.addWidget(self.rest_reminder_qsr)
        time_remaining_qhl.addWidget(self.rest_reminder_reset_qpb)

        # PUT EVERYTHING ON THE PAGE......
        grid = PageGrid()

        # first grid column
        grid.addWidget(H2(self.tr("Breathing Notifications")), 0, 0)
        grid.addWidget(HorizontalLine(), 1, 0)
        grid.addLayout(notification_interval_qhl, 2, 0)
        grid.addWidget(QtWidgets.QLabel(), 3, 0)
        grid.addWidget(H2(self.tr("Breathing Dialog")), 4, 0)
        grid.addWidget(HorizontalLine(), 5, 0)
        grid.addLayout(show_after_qhl, 6, 0)
        grid.addWidget(QtWidgets.QLabel(), 7, 0)
        grid.addWidget(H2(self.tr("Rest Dialog")), 8, 0)
        grid.addWidget(HorizontalLine(), 9, 0)
        grid.addLayout(rest_interval_qhl, 10, 0)
        grid.addLayout(time_remaining_qhl, 11, 0)

        # second grid column
        grid.addWidget(QtWidgets.QLabel("This is an overview of your notifications"), 0, 1)
        grid.addWidget(self.overview_qlw, 1, 1, 11, 1)

        vbox_l2 = QtWidgets.QVBoxLayout()
        vbox_l2.addWidget(H1(self.tr("Settings for Timers")))
        vbox_l2.addWidget(HorizontalLine())
        vbox_l2.addStretch(1)
        vbox_l2.addLayout(grid)
        vbox_l2.addStretch(3)
        self.setLayout(vbox_l2)

        self.update_gui()

    def _connect_slots_to_signals(self):
        self.notification_interval_qsb.valueChanged.connect(
            self.on_time_btw_notifications_value_changed
        )
        self.show_after_qsb.valueChanged.connect(
            self.on_dlg_after_nr_notifications_value_changed
        )
        self.rest_interval_qsb.valueChanged.connect(
            self.on_time_before_rest_value_changed
        )
        self.rest_reminder_qsr.valueChanged.connect(self.on_rest_reminder_slider_value_changed)
        self.rest_reminder_reset_qpb.clicked.connect(self.on_rest_reset_clicked)

    def on_time_btw_notifications_value_changed(self, i_new_value: int):
        logging.debug("on_time_btw_notifications_value_changed, i_new_value = " + str(i_new_value))
        SettingsM.update_breathing_reminder_interval(i_new_value)
        self.overview_qlw.update_gui_time_overview()
        self.breathing_settings_updated_from_settings_signal.emit('settings')

    def on_dlg_after_nr_notifications_value_changed(self, i_new_value: int):
        logging.debug("on_dlg_after_nr_notifications_value_changed, i_new_value = " + str(i_new_value))
        SettingsM.update_breathing_reminder_nr_per_dialog(i_new_value)
        self.overview_qlw.update_gui_time_overview()
        self.breathing_settings_updated_from_settings_signal.emit('settings')

    def on_time_before_rest_value_changed(self, i_new_value: int):
        logging.debug("on_time_before_rest_value_changed, i_new_value = " + str(i_new_value))
        SettingsM.update_rest_reminder_interval(i_new_value)
        self.overview_qlw.update_gui_time_overview()
        self.rest_settings_updated_from_settings_signal.emit('settings')

    def on_rest_reminder_slider_value_changed(self, i_new_value: int):
        if self.updating_gui_bool:
            return
        mc.mc_global.rest_reminder_minutes_passed_int = i_new_value
        self.rest_slider_value_changed_signal.emit()

    def on_rest_reset_clicked(self):
        self.rest_reset_button_clicked_signal.emit()

    def update_gui(self):
        self.updating_gui_bool = True

        settings = SettingsM.get()
        self.notification_interval_qsb.setValue(settings.breathing_reminder_interval_int)
        self.show_after_qsb.setValue(settings.breathing_reminder_nr_before_dialog_int)
        self.rest_interval_qsb.setValue(settings.rest_reminder_interval_int)
        self.rest_reminder_qsr.setMinimum(0)
        self.rest_reminder_qsr.setMaximum(settings.rest_reminder_interval_int)
        self.rest_reminder_qsr.setValue(mc.mc_global.rest_reminder_minutes_passed_int)

        self.updating_gui_bool = False


class TimingOverviewWt(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()
        self.settings = mc.model.SettingsM.get()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.update_gui_time_overview()

    def update_gui_time_overview(self):
        self.clear()

        settings = mc.model.SettingsM.get()

        counter_int = 0
        while True:
            counter_int += 1
            minutes_int = counter_int * settings.breathing_reminder_interval_int
            if minutes_int >= settings.rest_reminder_interval:
                break
            elif settings.breathing_reminder_nr_before_dialog_int != 0 and \
                    (counter_int % settings.breathing_reminder_nr_before_dialog_int) == 0:
                self.addItem("Breathing dialog: " + str(minutes_int) + " minutes")
                self.set_size_hint(counter_int - 1)
            else:
                self.addItem("Breathing reminder: " + str(minutes_int) + " minutes")
                self.set_size_hint(counter_int - 1)

        self.addItem("Rest: " + str(settings.rest_reminder_interval) + " minutes")
        self.set_size_hint(counter_int - 1)

    def set_size_hint(self, counter_int):
        self.item(counter_int).setSizeHint(
            QtCore.QSize(self.item(counter_int).sizeHint().width(), mc_global.LIST_ITEM_HEIGHT_INT))
