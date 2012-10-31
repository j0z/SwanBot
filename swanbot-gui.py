from PyQt4 import QtCore, QtGui
from ui import Ui_MainWindow
import client
import sys

class SwanBot_GUI(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self.client = client.Client('localhost',
			'934a26c6ec10c1c44e1e140c6ffa25036166c0afd0efcfe638693e6a')
		
		for node in self.client.get_nodes(self.client.find_nodes({'type': 'test_node'})):
			print node['date']
			_item = QtGui.QTreeWidgetItem([str(node['type']),
								str(node['id']),
								str(node['created'])])
			self.ui.list_nodelist.addTopLevelItem(_item)

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	servergui = SwanBot_GUI()
	servergui.show()
	sys.exit(app.exec_())