# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\web_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_App(object):
    def setupUi(self, App):
        App.setObjectName("App")
        App.resize(978, 602)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/images/icons8-bookmark-384.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        App.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(App)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.mainTab = QtWidgets.QTabWidget(self.centralwidget)
        self.mainTab.setObjectName("mainTab")
        self.base_tab = QtWidgets.QWidget()
        self.base_tab.setObjectName("base_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.base_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.base_label = QtWidgets.QLabel(self.base_tab)
        self.base_label.setStyleSheet("font: 11pt \"Helvetica\";")
        self.base_label.setObjectName("base_label")
        self.gridLayout_2.addWidget(self.base_label, 0, 0, 1, 1)
        self.base_table = QtWidgets.QTableView(self.base_tab)
        self.base_table.setAcceptDrops(True)
        self.base_table.setObjectName("base_table")
        self.gridLayout_2.addWidget(self.base_table, 2, 0, 1, 2)
        self.status_base_label = QtWidgets.QLabel(self.base_tab)
        self.status_base_label.setObjectName("status_base_label")
        self.gridLayout_2.addWidget(self.status_base_label, 3, 1, 1, 1, QtCore.Qt.AlignRight)
        self.pushButton = QtWidgets.QPushButton(self.base_tab)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 0, 1, 1, 1)
        self.mainTab.addTab(self.base_tab, "")
        self.gridLayout_3.addWidget(self.mainTab, 0, 0, 1, 1)
        App.setCentralWidget(self.centralwidget)
        self.searchWidget = QtWidgets.QDockWidget(App)
        self.searchWidget.setObjectName("searchWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.line = QtWidgets.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 2)
        self.label_10 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 1)
        self.SearchList = QtWidgets.QListWidget(self.dockWidgetContents)
        self.SearchList.setAcceptDrops(False)
        self.SearchList.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SearchList.setDragEnabled(True)
        self.SearchList.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.SearchList.setObjectName("SearchList")
        self.gridLayout.addWidget(self.SearchList, 4, 0, 1, 3)
        self.Search_LineEdit = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.Search_LineEdit.setObjectName("Search_LineEdit")
        self.gridLayout.addWidget(self.Search_LineEdit, 0, 1, 1, 1)
        self.searchWidget.setWidget(self.dockWidgetContents)
        App.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.searchWidget)
        self.menuExit = QtWidgets.QAction(App)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/images/icons8-emergency-exit-96.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuExit.setIcon(icon1)
        self.menuExit.setObjectName("menuExit")
        self.menuImport = QtWidgets.QAction(App)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/images/icons8-document-384.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuImport.setIcon(icon2)
        self.menuImport.setObjectName("menuImport")
        self.actionUnion = QtWidgets.QAction(App)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/images/icons8-group-layouts-96.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUnion.setIcon(icon3)
        self.actionUnion.setObjectName("actionUnion")
        self.searchButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.searchButton.setObjectName("searchButton")
        self.gridLayout.addWidget(self.searchButton, 0, 2, 1, 1)

        self.retranslateUi(App)
        self.mainTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(App)

    def retranslateUi(self, App):
        _translate = QtCore.QCoreApplication.translate
        App.setWindowTitle(_translate("App", "web crawler"))
        self.base_label.setText(_translate("App", "Keyword"))
        self.status_base_label.setText(_translate("App", "0 links"))
        self.pushButton.setText(_translate("App", "Domain"))
        self.mainTab.setTabText(self.mainTab.indexOf(self.base_tab), _translate("App", "Base"))
        self.searchWidget.setWindowTitle(_translate("App", "Search Window"))
        self.label_10.setText(_translate("App", "Search"))
        self.searchButton.setText(_translate("App", "Search"))
        self.menuExit.setText(_translate("App", "Exit"))
        self.menuImport.setText(_translate("App", "Import"))
        self.actionUnion.setText(_translate("App", "Union"))
        self.base_table.setSortingEnabled(True)
        self.base_table.setEditTriggers(QtWidgets.QTableView.NoEditTriggers)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    App = QtWidgets.QMainWindow()
    ui = Ui_App()
    ui.setupUi(App)
    App.show()
    sys.exit(app.exec_())
