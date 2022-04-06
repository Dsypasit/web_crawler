from web_ui import Ui_App
from domain_ui import DomainFilter
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
        self.current_domains = {}

        self.updateKeywords()

        self.ui.SearchList.itemDoubleClicked.connect(self.selectKeywordsData)
        self.ui.base_table.doubleClicked.connect(self.openLink)
        self.ui.pushButton.clicked.connect(self.filterDomainPopup)
        self.ui.searchButton.clicked.connect(self.searchKeyword)

    def updateKeywords(self):
        self.keywords = self.keyword_manager.get_all_keywords()
        self.ui.SearchList.clear()
        self.ui.SearchList.addItems(self.keywords)
    
    def showTable(self):
        self.model = PandasTableModel(self.data)
        self.ui.base_table.setModel(self.model)
        self.ui.base_table.setColumnWidth(0, 200)
        self.ui.base_table.setColumnWidth(1, 200)
    
    def searchKeyword(self):
        self.keyword = self.ui.Search_LineEdit.text()
        self.data = self.keyword_manager.search_keyword(self.keyword)
        self.showTable()
        self.ui.status_base_label.setText(f"{len(self.data.index)} links")
        domains_list = self.keyword_manager.get_domain(self.keyword)
        self.current_domains = {name: False for name in domains_list}
        self.ui.base_label.setText(self.keyword)
        self.updateKeywords()
        self.ui.Search_LineEdit.clear()
        
    def selectKeywordsData(self, item):
        self.keyword = item.text()
        self.data = self.keyword_manager.search_keyword(self.keyword)
        self.showTable()
        self.ui.status_base_label.setText(f"{len(self.data.index)} links")
        domains_list = self.keyword_manager.get_domain(self.keyword)
        self.current_domains = {name: False for name in domains_list}
        self.ui.base_label.setText(self.keyword)
   
    def openLink(self, item):
        for index in self.ui.base_table.selectionModel().selectedIndexes():
            value = str(self.data.iloc[index.row()][index.column()])
            if value.startswith("https://") or value.startswith("http://"):
                webbrowser.open(value)
                return
    
    def filterDomainPopup(self):
        print(self.current_domains)
        filter_dialog = DomainFilter(self)
        filter_dialog.show()
    
    def filterDomain(self):
        domains = [domain for domain in self.current_domains.keys() if self.current_domains[domain]]
        self.data = self.keyword_manager.filter_domain(self.keyword, *domains)
        self.showTable()

        

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())