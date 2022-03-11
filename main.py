########################################################################
## CONVERT .UI & .QRC
# pyrcc5 resources.qrc -o resource_rc.py
# pyuic5 -x football.ui -o football_interface.py 
########################################################################

########################################################################
## IMPORTS
########################################################################
import os
import sys
import re
import webbrowser
from CrawlerManager import CrawlerManager
from model import PandasTableModel
########################################################################
# IMPORT GUI FILE
from football_interface import *
from PyQt5.QtWidgets import QFileDialog, QListWidget, QTableWidgetItem, QApplication, QMainWindow, qApp, QListWidgetItem
from PyQt5.QtCore import Qt
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.crawler_manager = CrawlerManager()

        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.ui.pushButton.clicked.connect(self.search)
        self.ui.tableWidget.doubleClicked.connect(self.open_link)
        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show()
        #######################################################################

    ########################################################################
    ## FUNCTION
    ########################################################################
    def search(self):
        # self.crawler_manager.get_all_links()
        self.data = self.crawler_manager.get_n_gram_data(self.ui.lineEdit.text())
        self.model = PandasTableModel(self.data[:20])
        self.ui.tableWidget.setModel(self.model)
    
    def open_link(self, item):
        for index in self.ui.tableWidget.selectionModel().selectedIndexes():
            value = str(self.data.iloc[index.row()][index.column()])
            webbrowser.open(value)
            return

    ########################################################################

########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ########################################################################
    ##
    ########################################################################
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################
