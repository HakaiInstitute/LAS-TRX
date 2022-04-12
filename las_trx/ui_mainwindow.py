# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(576, 690)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_input = QFrame(self.centralwidget)
        self.frame_input.setObjectName(u"frame_input")
        self.frame_input.setFrameShape(QFrame.StyledPanel)
        self.frame_input.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_input)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_input = QLabel(self.frame_input)
        self.label_input.setObjectName(u"label_input")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_input.sizePolicy().hasHeightForWidth())
        self.label_input.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_input.setFont(font)

        self.verticalLayout_5.addWidget(self.label_input)

        self.line_input = QFrame(self.frame_input)
        self.line_input.setObjectName(u"line_input")
        self.line_input.setFrameShape(QFrame.HLine)
        self.line_input.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_5.addWidget(self.line_input)

        self.widget_input_file = QWidget(self.frame_input)
        self.widget_input_file.setObjectName(u"widget_input_file")
        self.horizontalLayout = QHBoxLayout(self.widget_input_file)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.label_input_file = QLabel(self.widget_input_file)
        self.label_input_file.setObjectName(u"label_input_file")

        self.horizontalLayout.addWidget(self.label_input_file)

        self.lineEdit_input_file = QLineEdit(self.widget_input_file)
        self.lineEdit_input_file.setObjectName(u"lineEdit_input_file")

        self.horizontalLayout.addWidget(self.lineEdit_input_file)

        self.toolButton_input_file = QToolButton(self.widget_input_file)
        self.toolButton_input_file.setObjectName(u"toolButton_input_file")

        self.horizontalLayout.addWidget(self.toolButton_input_file)


        self.verticalLayout_5.addWidget(self.widget_input_file)

        self.widget = QWidget(self.frame_input)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.toolButton_help = QToolButton(self.widget)
        self.toolButton_help.setObjectName(u"toolButton_help")
        self.toolButton_help.setLayoutDirection(Qt.LeftToRight)
        self.toolButton_help.setAutoFillBackground(False)
        self.toolButton_help.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.toolButton_help.setAutoRaise(True)

        self.horizontalLayout_3.addWidget(self.toolButton_help)


        self.verticalLayout_5.addWidget(self.widget)

        self.widget_input_options = QWidget(self.frame_input)
        self.widget_input_options.setObjectName(u"widget_input_options")
        self.gridLayout = QGridLayout(self.widget_input_options)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, -1, 0, -1)
        self.spinBox_input_utm_zone = QSpinBox(self.widget_input_options)
        self.spinBox_input_utm_zone.setObjectName(u"spinBox_input_utm_zone")
        self.spinBox_input_utm_zone.setEnabled(True)
        self.spinBox_input_utm_zone.setMinimum(7)
        self.spinBox_input_utm_zone.setMaximum(22)
        self.spinBox_input_utm_zone.setValue(10)

        self.gridLayout.addWidget(self.spinBox_input_utm_zone, 5, 1, 1, 1)

        self.comboBox_input_coordinates = QComboBox(self.widget_input_options)
        self.comboBox_input_coordinates.addItem("")
        self.comboBox_input_coordinates.addItem("")
        self.comboBox_input_coordinates.addItem("")
        self.comboBox_input_coordinates.setObjectName(u"comboBox_input_coordinates")

        self.gridLayout.addWidget(self.comboBox_input_coordinates, 5, 0, 1, 1)

        self.comboBox_input_reference = QComboBox(self.widget_input_options)
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.addItem("")
        self.comboBox_input_reference.setObjectName(u"comboBox_input_reference")

        self.gridLayout.addWidget(self.comboBox_input_reference, 1, 0, 1, 1)

        self.dateEdit_input_epoch = QDateEdit(self.widget_input_options)
        self.dateEdit_input_epoch.setObjectName(u"dateEdit_input_epoch")
        self.dateEdit_input_epoch.setTime(QTime(8, 0, 0))
        self.dateEdit_input_epoch.setMaximumDateTime(QDateTime(QDate(9998, 1, 8), QTime(7, 59, 59)))
        self.dateEdit_input_epoch.setDisplayFormat(u"yyyy-MM-dd")
        self.dateEdit_input_epoch.setCalendarPopup(True)
        self.dateEdit_input_epoch.setTimeSpec(Qt.UTC)
        self.dateEdit_input_epoch.setDate(QDate(2010, 1, 1))

        self.gridLayout.addWidget(self.dateEdit_input_epoch, 1, 1, 1, 1)

        self.label_input_reference = QLabel(self.widget_input_options)
        self.label_input_reference.setObjectName(u"label_input_reference")

        self.gridLayout.addWidget(self.label_input_reference, 0, 0, 1, 1)

        self.label_input_utm_zone = QLabel(self.widget_input_options)
        self.label_input_utm_zone.setObjectName(u"label_input_utm_zone")

        self.gridLayout.addWidget(self.label_input_utm_zone, 3, 1, 1, 1)

        self.label_input_coordinates = QLabel(self.widget_input_options)
        self.label_input_coordinates.setObjectName(u"label_input_coordinates")

        self.gridLayout.addWidget(self.label_input_coordinates, 3, 0, 1, 1)

        self.label_input_epoch = QLabel(self.widget_input_options)
        self.label_input_epoch.setObjectName(u"label_input_epoch")

        self.gridLayout.addWidget(self.label_input_epoch, 0, 1, 1, 1)

        self.label_input_vertical_reference = QLabel(self.widget_input_options)
        self.label_input_vertical_reference.setObjectName(u"label_input_vertical_reference")

        self.gridLayout.addWidget(self.label_input_vertical_reference, 6, 0, 1, 1)

        self.comboBox_input_vertical_reference = QComboBox(self.widget_input_options)
        self.comboBox_input_vertical_reference.addItem("")
        self.comboBox_input_vertical_reference.setObjectName(u"comboBox_input_vertical_reference")

        self.gridLayout.addWidget(self.comboBox_input_vertical_reference, 7, 0, 1, 1)


        self.verticalLayout_5.addWidget(self.widget_input_options)


        self.verticalLayout.addWidget(self.frame_input)

        self.frame_output = QFrame(self.centralwidget)
        self.frame_output.setObjectName(u"frame_output")
        self.frame_output.setFrameShape(QFrame.StyledPanel)
        self.frame_output.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_output)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_output = QLabel(self.frame_output)
        self.label_output.setObjectName(u"label_output")
        sizePolicy.setHeightForWidth(self.label_output.sizePolicy().hasHeightForWidth())
        self.label_output.setSizePolicy(sizePolicy)
        self.label_output.setFont(font)

        self.verticalLayout_6.addWidget(self.label_output)

        self.line_output = QFrame(self.frame_output)
        self.line_output.setObjectName(u"line_output")
        self.line_output.setFrameShape(QFrame.HLine)
        self.line_output.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_6.addWidget(self.line_output)

        self.widget_output_file = QWidget(self.frame_output)
        self.widget_output_file.setObjectName(u"widget_output_file")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_output_file)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, 0, -1)
        self.label_output_file = QLabel(self.widget_output_file)
        self.label_output_file.setObjectName(u"label_output_file")

        self.horizontalLayout_2.addWidget(self.label_output_file)

        self.lineEdit_output_file = QLineEdit(self.widget_output_file)
        self.lineEdit_output_file.setObjectName(u"lineEdit_output_file")

        self.horizontalLayout_2.addWidget(self.lineEdit_output_file)

        self.toolButton_output_file = QToolButton(self.widget_output_file)
        self.toolButton_output_file.setObjectName(u"toolButton_output_file")

        self.horizontalLayout_2.addWidget(self.toolButton_output_file)


        self.verticalLayout_6.addWidget(self.widget_output_file)

        self.widget_output_options = QWidget(self.frame_output)
        self.widget_output_options.setObjectName(u"widget_output_options")
        self.gridLayout_2 = QGridLayout(self.widget_output_options)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setVerticalSpacing(6)
        self.gridLayout_2.setContentsMargins(0, -1, 0, -1)
        self.label_output_vertical_reference = QLabel(self.widget_output_options)
        self.label_output_vertical_reference.setObjectName(u"label_output_vertical_reference")

        self.gridLayout_2.addWidget(self.label_output_vertical_reference, 7, 0, 1, 1)

        self.comboBox_output_reference = QComboBox(self.widget_output_options)
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.addItem("")
        self.comboBox_output_reference.setObjectName(u"comboBox_output_reference")
        self.comboBox_output_reference.setEnabled(True)

        self.gridLayout_2.addWidget(self.comboBox_output_reference, 3, 0, 1, 1)

        self.label_output_coordinates = QLabel(self.widget_output_options)
        self.label_output_coordinates.setObjectName(u"label_output_coordinates")

        self.gridLayout_2.addWidget(self.label_output_coordinates, 4, 0, 1, 1)

        self.label_output_reference = QLabel(self.widget_output_options)
        self.label_output_reference.setObjectName(u"label_output_reference")

        self.gridLayout_2.addWidget(self.label_output_reference, 1, 0, 1, 1)

        self.label_output_epoch = QLabel(self.widget_output_options)
        self.label_output_epoch.setObjectName(u"label_output_epoch")

        self.gridLayout_2.addWidget(self.label_output_epoch, 1, 1, 1, 1)

        self.spinBox_output_utm_zone = QSpinBox(self.widget_output_options)
        self.spinBox_output_utm_zone.setObjectName(u"spinBox_output_utm_zone")
        self.spinBox_output_utm_zone.setEnabled(True)
        self.spinBox_output_utm_zone.setMinimum(7)
        self.spinBox_output_utm_zone.setMaximum(22)
        self.spinBox_output_utm_zone.setValue(10)
        self.spinBox_output_utm_zone.setDisplayIntegerBase(10)

        self.gridLayout_2.addWidget(self.spinBox_output_utm_zone, 5, 1, 1, 1)

        self.dateEdit_output_epoch = QDateEdit(self.widget_output_options)
        self.dateEdit_output_epoch.setObjectName(u"dateEdit_output_epoch")
        self.dateEdit_output_epoch.setEnabled(False)
        self.dateEdit_output_epoch.setTime(QTime(8, 0, 0))
        self.dateEdit_output_epoch.setDisplayFormat(u"yyyy-MM-dd")
        self.dateEdit_output_epoch.setCalendarPopup(True)
        self.dateEdit_output_epoch.setTimeSpec(Qt.UTC)
        self.dateEdit_output_epoch.setDate(QDate(2010, 1, 1))

        self.gridLayout_2.addWidget(self.dateEdit_output_epoch, 3, 1, 1, 1)

        self.comboBox_output_coordinates = QComboBox(self.widget_output_options)
        self.comboBox_output_coordinates.addItem("")
        self.comboBox_output_coordinates.addItem("")
        self.comboBox_output_coordinates.addItem("")
        self.comboBox_output_coordinates.setObjectName(u"comboBox_output_coordinates")

        self.gridLayout_2.addWidget(self.comboBox_output_coordinates, 5, 0, 1, 1)

        self.label_output_utm_zone = QLabel(self.widget_output_options)
        self.label_output_utm_zone.setObjectName(u"label_output_utm_zone")

        self.gridLayout_2.addWidget(self.label_output_utm_zone, 4, 1, 1, 1)

        self.comboBox_output_vertical_reference = QComboBox(self.widget_output_options)
        self.comboBox_output_vertical_reference.addItem("")
        self.comboBox_output_vertical_reference.addItem("")
        self.comboBox_output_vertical_reference.addItem("")
        self.comboBox_output_vertical_reference.addItem("")
        self.comboBox_output_vertical_reference.setObjectName(u"comboBox_output_vertical_reference")
        self.comboBox_output_vertical_reference.setEnabled(True)

        self.gridLayout_2.addWidget(self.comboBox_output_vertical_reference, 8, 0, 1, 1)

        self.checkBox_epoch_trans = QCheckBox(self.widget_output_options)
        self.checkBox_epoch_trans.setObjectName(u"checkBox_epoch_trans")
        self.checkBox_epoch_trans.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout_2.addWidget(self.checkBox_epoch_trans, 0, 1, 1, 1)


        self.verticalLayout_6.addWidget(self.widget_output_options)


        self.verticalLayout.addWidget(self.frame_output)

        self.widget_actions = QWidget(self.centralwidget)
        self.widget_actions.setObjectName(u"widget_actions")
        sizePolicy.setHeightForWidth(self.widget_actions.sizePolicy().hasHeightForWidth())
        self.widget_actions.setSizePolicy(sizePolicy)
        self.horizontalLayout_4 = QHBoxLayout(self.widget_actions)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, -1, 0, -1)
        self.progressBar = QProgressBar(self.widget_actions)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.horizontalLayout_4.addWidget(self.progressBar)

        self.pushButton_convert = QPushButton(self.widget_actions)
        self.pushButton_convert.setObjectName(u"pushButton_convert")

        self.horizontalLayout_4.addWidget(self.pushButton_convert)


        self.verticalLayout.addWidget(self.widget_actions)

        MainWindow.setCentralWidget(self.centralwidget)
#if QT_CONFIG(shortcut)
        self.label_input_file.setBuddy(self.lineEdit_input_file)
        self.label_input_reference.setBuddy(self.comboBox_input_reference)
        self.label_input_utm_zone.setBuddy(self.spinBox_input_utm_zone)
        self.label_input_coordinates.setBuddy(self.comboBox_input_coordinates)
        self.label_input_epoch.setBuddy(self.dateEdit_input_epoch)
        self.label_input_vertical_reference.setBuddy(self.comboBox_input_vertical_reference)
        self.label_output_file.setBuddy(self.lineEdit_output_file)
        self.label_output_vertical_reference.setBuddy(self.comboBox_output_vertical_reference)
        self.label_output_coordinates.setBuddy(self.comboBox_output_coordinates)
        self.label_output_reference.setBuddy(self.comboBox_output_reference)
        self.label_output_epoch.setBuddy(self.dateEdit_output_epoch)
        self.label_output_utm_zone.setBuddy(self.spinBox_output_utm_zone)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.lineEdit_input_file, self.toolButton_input_file)
        QWidget.setTabOrder(self.toolButton_input_file, self.comboBox_input_reference)
        QWidget.setTabOrder(self.comboBox_input_reference, self.dateEdit_input_epoch)
        QWidget.setTabOrder(self.dateEdit_input_epoch, self.comboBox_input_coordinates)
        QWidget.setTabOrder(self.comboBox_input_coordinates, self.spinBox_input_utm_zone)
        QWidget.setTabOrder(self.spinBox_input_utm_zone, self.comboBox_input_vertical_reference)
        QWidget.setTabOrder(self.comboBox_input_vertical_reference, self.lineEdit_output_file)
        QWidget.setTabOrder(self.lineEdit_output_file, self.toolButton_output_file)
        QWidget.setTabOrder(self.toolButton_output_file, self.comboBox_output_reference)
        QWidget.setTabOrder(self.comboBox_output_reference, self.dateEdit_output_epoch)
        QWidget.setTabOrder(self.dateEdit_output_epoch, self.comboBox_output_coordinates)
        QWidget.setTabOrder(self.comboBox_output_coordinates, self.spinBox_output_utm_zone)
        QWidget.setTabOrder(self.spinBox_output_utm_zone, self.comboBox_output_vertical_reference)
        QWidget.setTabOrder(self.comboBox_output_vertical_reference, self.pushButton_convert)

        self.retranslateUi(MainWindow)

        self.comboBox_input_coordinates.setCurrentIndex(2)
        self.comboBox_input_reference.setCurrentIndex(1)
        self.comboBox_output_coordinates.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LAS TRX", None))
        self.label_input.setText(QCoreApplication.translate("MainWindow", u"Origin", None))
        self.label_input_file.setText(QCoreApplication.translate("MainWindow", u"Input File", None))
        self.toolButton_input_file.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.toolButton_help.setText(QCoreApplication.translate("MainWindow", u"Batch Mode?", None))
        self.comboBox_input_coordinates.setItemText(0, QCoreApplication.translate("MainWindow", u"Geographic", None))
        self.comboBox_input_coordinates.setItemText(1, QCoreApplication.translate("MainWindow", u"Cartesian", None))
        self.comboBox_input_coordinates.setItemText(2, QCoreApplication.translate("MainWindow", u"UTM", None))

        self.comboBox_input_reference.setItemText(0, QCoreApplication.translate("MainWindow", u"NAD83(CSRS)", None))
        self.comboBox_input_reference.setItemText(1, QCoreApplication.translate("MainWindow", u"ITRF2014", None))
        self.comboBox_input_reference.setItemText(2, QCoreApplication.translate("MainWindow", u"ITRF2008", None))
        self.comboBox_input_reference.setItemText(3, QCoreApplication.translate("MainWindow", u"ITRF2005", None))
        self.comboBox_input_reference.setItemText(4, QCoreApplication.translate("MainWindow", u"ITRF2000", None))
        self.comboBox_input_reference.setItemText(5, QCoreApplication.translate("MainWindow", u"ITRF97", None))
        self.comboBox_input_reference.setItemText(6, QCoreApplication.translate("MainWindow", u"ITRF96", None))
        self.comboBox_input_reference.setItemText(7, QCoreApplication.translate("MainWindow", u"ITRF94", None))
        self.comboBox_input_reference.setItemText(8, QCoreApplication.translate("MainWindow", u"ITRF93", None))
        self.comboBox_input_reference.setItemText(9, QCoreApplication.translate("MainWindow", u"ITRF92", None))
        self.comboBox_input_reference.setItemText(10, QCoreApplication.translate("MainWindow", u"ITRF91", None))
        self.comboBox_input_reference.setItemText(11, QCoreApplication.translate("MainWindow", u"ITRF90", None))
        self.comboBox_input_reference.setItemText(12, QCoreApplication.translate("MainWindow", u"ITRF89", None))
        self.comboBox_input_reference.setItemText(13, QCoreApplication.translate("MainWindow", u"ITRF88", None))

        self.label_input_reference.setText(QCoreApplication.translate("MainWindow", u"Reference Frame", None))
        self.label_input_utm_zone.setText(QCoreApplication.translate("MainWindow", u"UTM Zone", None))
        self.label_input_coordinates.setText(QCoreApplication.translate("MainWindow", u"Coordinates", None))
        self.label_input_epoch.setText(QCoreApplication.translate("MainWindow", u"Epoch (YYYY-MM-DD)", None))
        self.label_input_vertical_reference.setText(QCoreApplication.translate("MainWindow", u"Vertical Reference", None))
        self.comboBox_input_vertical_reference.setItemText(0, QCoreApplication.translate("MainWindow", u"GRS80", None))

        self.label_output.setText(QCoreApplication.translate("MainWindow", u"Destination", None))
        self.label_output_file.setText(QCoreApplication.translate("MainWindow", u"Output file", None))
        self.toolButton_output_file.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_output_vertical_reference.setText(QCoreApplication.translate("MainWindow", u"Vertical Reference", None))
        self.comboBox_output_reference.setItemText(0, QCoreApplication.translate("MainWindow", u"NAD83(CSRS)", None))
        self.comboBox_output_reference.setItemText(1, QCoreApplication.translate("MainWindow", u"ITRF2014", None))
        self.comboBox_output_reference.setItemText(2, QCoreApplication.translate("MainWindow", u"ITRF2008", None))
        self.comboBox_output_reference.setItemText(3, QCoreApplication.translate("MainWindow", u"ITRF2005", None))
        self.comboBox_output_reference.setItemText(4, QCoreApplication.translate("MainWindow", u"ITRF2000", None))
        self.comboBox_output_reference.setItemText(5, QCoreApplication.translate("MainWindow", u"ITRF97", None))
        self.comboBox_output_reference.setItemText(6, QCoreApplication.translate("MainWindow", u"ITRF96", None))
        self.comboBox_output_reference.setItemText(7, QCoreApplication.translate("MainWindow", u"ITRF94", None))
        self.comboBox_output_reference.setItemText(8, QCoreApplication.translate("MainWindow", u"ITRF93", None))
        self.comboBox_output_reference.setItemText(9, QCoreApplication.translate("MainWindow", u"ITRF92", None))
        self.comboBox_output_reference.setItemText(10, QCoreApplication.translate("MainWindow", u"ITRF91", None))
        self.comboBox_output_reference.setItemText(11, QCoreApplication.translate("MainWindow", u"ITRF90", None))
        self.comboBox_output_reference.setItemText(12, QCoreApplication.translate("MainWindow", u"ITRF89", None))
        self.comboBox_output_reference.setItemText(13, QCoreApplication.translate("MainWindow", u"ITRF88", None))

        self.label_output_coordinates.setText(QCoreApplication.translate("MainWindow", u"Coordinates", None))
        self.label_output_reference.setText(QCoreApplication.translate("MainWindow", u"Reference Frame", None))
        self.label_output_epoch.setText(QCoreApplication.translate("MainWindow", u"Epoch (YYYY-MM-DD)", None))
        self.comboBox_output_coordinates.setItemText(0, QCoreApplication.translate("MainWindow", u"Geographic", None))
        self.comboBox_output_coordinates.setItemText(1, QCoreApplication.translate("MainWindow", u"Cartesian", None))
        self.comboBox_output_coordinates.setItemText(2, QCoreApplication.translate("MainWindow", u"UTM", None))

        self.label_output_utm_zone.setText(QCoreApplication.translate("MainWindow", u"UTM Zone", None))
        self.comboBox_output_vertical_reference.setItemText(0, QCoreApplication.translate("MainWindow", u"GRS80", None))
        self.comboBox_output_vertical_reference.setItemText(1, QCoreApplication.translate("MainWindow", u"CGVD2013/CGG2013a", None))
        self.comboBox_output_vertical_reference.setItemText(2, QCoreApplication.translate("MainWindow", u"CGVD2013/CGG2013", None))
        self.comboBox_output_vertical_reference.setItemText(3, QCoreApplication.translate("MainWindow", u"CGVD28/HT2_2010v70", None))

        self.checkBox_epoch_trans.setText(QCoreApplication.translate("MainWindow", u"Epoch Transformation", None))
        self.pushButton_convert.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
    # retranslateUi

