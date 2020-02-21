#!/usr/bin/python3

# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua
import avango.script

class VirtualRANavigation(avango.script.Script):
	# output field
	sf_navigation_matrix = avango.gua.SFMatrix4()
	sf_navigation_matrix.value = avango.gua.make_identity_mat()

	def __init__(self):
		self.super(VirtualRANavigation).__init__()
		self.cur_node = 1
		self.create_path()

	def set_inputs(self, scenegraph, navigation_node, head_node):
		self.scenegraph = scenegraph
		self.navigation_node = navigation_node
		self.head_node = head_node
		self.always_evaluate(True)

	def create_path(self):
		self.path = {1:[(2,avango.gua.Vec3(2,2,2))],2:[(3,avango.gua.Vec3(2,2,2))]}

	def end(self):
		boolean = True

	def evaluate(self):
		self.sf_navigation_matrix.value *= avango.gua.make_trans_mat(self.path[self.cur_node][0][1])
		self.navigation_node = self.sf_navigation_matrix.value
		print(self.sf_navigation_matrix.value)
		self.cur_node = self.path[self.cur_node][0][0]
		if self.cur_node == 3:
			self.always_evaluate(False)