from web_ui import Ui_App
from domain_ui import Ui_Dialog
from model import PandasTableModel

from KeywordManager import KeywordManager

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
import sys
import webbrowser

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_App()
        self.ui.setupUi(self)
        self.keyword_manager = KeywordManager()

        self.updateKeywords()

        self.ui.SearchList.itemDoubleClicked.connect(self.showKeywordsData)
        self.ui.base_table.doubleClicked.connect(self.openLink)

    def updateKeywords(self):
        self.keywords = self.keyword_manager.get_all_keywords()
        self.ui.SearchList.clear()
        self.ui.SearchList.addItems(self.keywords)
    
    def showTable(self):
        self.model = PandasTableModel(self.data)
        self.ui.base_table.setModel(self.model)
        self.ui.base_table.setColumnWidth(0, 200)
        self.ui.base_table.setColumnWidth(1, 200)
    
    def showKeywordsData(self, item):
        self.keyword = item.text()
        self.data = self.keyword_manager.search_keyword(self.keyword)
        self.showTable()
        self.ui.status_base_label.setText(f"{len(self.data.index)} links")
   
    def openLink(self, item):
        for index in self.ui.base_table.selectionModel().selectedIndexes():
            value = str(self.data.iloc[index.row()][index.column()])
            if value.startswith("https://") or value.startswith("http://"):
                webbrowser.open(value)
                return

        

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())