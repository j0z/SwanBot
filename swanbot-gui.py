from PyQt4 import QtCore, QtGui
from ui import Ui_MainWindow
import client
import sys

class SwanBot_GUI(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self.ui.list_nodelist.itemClicked.connect(self.select_node)
		
		self.client = client.Client('localhost',
			'934a26c6ec10c1c44e1e140c6ffa25036166c0afd0efcfe638693e6a')
		
		for node in self.client.get_nodes(self.client.find_nodes({'type': 'test_node'})):
			_item = QtGui.QTreeWidgetItem([str(node['type']),
								str(node['id']),
								str(node['created'])])
			_item.addChild(QtGui.QTreeWidgetItem(['der','nope']))
			self.ui.list_nodelist.addTopLevelItem(_item)
	
	def select_node(self):
		for selected in self.ui.list_nodelist.selectedItems():
			_node_id = selected.text(1)
			node = self.client.get_nodes([int(_node_id)])[0]
			
			_col_count = 0
			for key in node:
				if isinstance(node[key],unicode) or isinstance(node[key],int):
					self.ui.list_nodeinfo.headerItem().setText(_col_count,key)
					_col_count+=1
			
			#print node
			_iter_node = node.copy()
			for key in _iter_node:
				if not isinstance(node[key],unicode) and not isinstance(node[key],int):
					del node[key]
				else:
					node[key] = str(node[key])
			
			_item = QtGui.QTreeWidgetItem(node.values())
			self.ui.list_nodeinfo.addTopLevelItem(_item)
			
			for key in node:
				self.ui.list_nodeinfo.resizeColumnToContents(node.keys().index(key))

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	servergui = SwanBot_GUI()
	servergui.show()
	sys.exit(app.exec_())