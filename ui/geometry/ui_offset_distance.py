# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_offset_distance.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_OffsetDistance(object):
    def setupUi(self, OffsetDistance):
        OffsetDistance.setObjectName(_fromUtf8("OffsetDistance"))
        OffsetDistance.resize(327, 241)
        self.gridLayout = QtGui.QGridLayout(OffsetDistance)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.sel_features_lbl = QtGui.QLabel(OffsetDistance)
        self.sel_features_lbl.setObjectName(_fromUtf8("sel_features_lbl"))
        self.gridLayout.addWidget(self.sel_features_lbl, 0, 2, 1, 1)
        self.offset_distance = QtGui.QDoubleSpinBox(OffsetDistance)
        self.offset_distance.setMaximum(999999999.0)
        self.offset_distance.setObjectName(_fromUtf8("offset_distance"))
        self.gridLayout.addWidget(self.offset_distance, 2, 2, 1, 2)
        self.selected_line_lbl = QtGui.QLabel(OffsetDistance)
        self.selected_line_lbl.setObjectName(_fromUtf8("selected_line_lbl"))
        self.gridLayout.addWidget(self.selected_line_lbl, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 2, 1, 1)
        self.preview_btn = QtGui.QPushButton(OffsetDistance)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.gridLayout.addWidget(self.preview_btn, 3, 2, 1, 1)
        self.run_btn = QtGui.QPushButton(OffsetDistance)
        self.run_btn.setObjectName(_fromUtf8("run_btn"))
        self.gridLayout.addWidget(self.run_btn, 3, 3, 1, 1)
        self.cancel_btn = QtGui.QPushButton(OffsetDistance)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 3, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.label_24 = QtGui.QLabel(OffsetDistance)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.gridLayout.addWidget(self.label_24, 0, 0, 1, 2)
        self.label_28 = QtGui.QLabel(OffsetDistance)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.gridLayout.addWidget(self.label_28, 1, 0, 1, 2)
        self.label_11 = QtGui.QLabel(OffsetDistance)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout.addWidget(self.label_11, 2, 0, 1, 2)

        self.retranslateUi(OffsetDistance)
        QtCore.QMetaObject.connectSlotsByName(OffsetDistance)

    def retranslateUi(self, OffsetDistance):
        OffsetDistance.setWindowTitle(_translate("OffsetDistance", "Form", None))
        self.sel_features_lbl.setText(_translate("OffsetDistance", "0", None))
        self.selected_line_lbl.setText(_translate("OffsetDistance", "0", None))
        self.preview_btn.setText(_translate("OffsetDistance", "Preview", None))
        self.run_btn.setText(_translate("OffsetDistance", "Run", None))
        self.cancel_btn.setText(_translate("OffsetDistance", "Cancel", None))
        self.label_24.setText(_translate("OffsetDistance", "Selected features:", None))
        self.label_28.setText(_translate("OffsetDistance", "Selected line:", None))
        self.label_11.setText(_translate("OffsetDistance", "Offset distance:", None))

