
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.Qt import QThread

from caDlg import Ui_Dialog
from test_station.konica_minolta.ca310 import CA310
import serial.tools.list_ports


class CaMeasureXylv(QThread):
    def __init__(self, ca):
        # type: (CA310) -> None
        super(CaMeasureXylv, self).__init__()
        self._ca = ca
        self.MeasureValues = (0, 0, 0)

    def run(self):
        self.MeasureValues = self._ca.measurexyLv()

class QDialgCa(QDialog):
    def __init__(self, ui_dlg):
        # type: (Ui_Dialog) -> None
        super(QDialog, self).__init__()
        self._ui_dlg = ui_dlg  # type: Ui_Dialog
        self._ui_dlg.setupUi(self)
        self._ca = None  # type: CA310
        self._mes = None  # type: CaMeasureXylv
        cbo = serial.tools.list_ports.comports()
        for item in cbo:
            if item[2].upper().find(r'USB VID:PID=132B:210D') != -1:
                self._ui_dlg.cbSerialItems.addItem(item[0], item)
        self.btnStatusConfig(False)
        self.update_measure_values()

    def update_measure_values(self, valu=None):
        if isinstance(valu, tuple):
            (x, y, lv) = valu
            self._ui_dlg.lblReadCIE1931_x.setText('x: {0:f}'.format(x))
            self._ui_dlg.lblReadCIE1931_y.setText('y: {0:f}'.format(y))
            self._ui_dlg.lblReadCIE1931_lv.setText('lv: {0:f}'.format(lv))
        else:
            self._ui_dlg.lblReadCIE1931_x.setText('x: -')
            self._ui_dlg.lblReadCIE1931_y.setText('y: -')
            self._ui_dlg.lblReadCIE1931_lv.setText('lv: -')

    def btnStatusConfig(self, status):
        self._ui_dlg.cbSerialItems.setEnabled(not status)
        self._ui_dlg.btnOpenCA.setEnabled(not status)
        self._ui_dlg.btnZeroCal.setEnabled(status)
        self._ui_dlg.btnReadValue.setEnabled(status)
        self._ui_dlg.btnCloseCA.setEnabled(status)

    def btn_open_ca_click(self, e):
        item = self._ui_dlg.cbSerialItems.currentData()
        if isinstance(item, tuple):
            self._ca = CA310(item[0])
            self._ca.initialize()
            if self._ca.test_connection():
                self.btnStatusConfig(True)
            else:
                self._ca.close_camera()

    def btn_zerocalc_click(self, e):
        if self._ca is not None:
            self._ca.zero_cal()

    def btn_close_ca_click(self, e):
        if self._ca is not None:
            self._ca.close_camera()
            self.btnStatusConfig(False)

    def _measureXylv(self):
        self._ui_dlg.btnReadValue.setEnabled(True)
        self.update_measure_values(self._mes.MeasureValues)

    def btn_read_xylv_click(self, e):
        if self._ca is not None:
            self._ui_dlg.btnReadValue.setEnabled(False)
            self.update_measure_values()
            self._mes = CaMeasureXylv(self._ca)
            self._mes.finished.connect(self._measureXylv)
            self._mes.start()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    cu = Ui_Dialog()
    dlg = QDialgCa(cu)
    dlg.setFixedSize(1024, 800)

    dlg.show()

    sys.exit(app.exec_())
