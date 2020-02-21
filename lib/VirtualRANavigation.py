#!/usr/bin/python3

# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua
import avango.script

#
import time
import math

class VirtualRANavigation(avango.script.Script):
	# output field
	sf_navigation_matrix = avango.gua.SFMatrix4()
	sf_navigation_matrix.value = avango.gua.make_identity_mat()

	def __init__(self):
		self.super(VirtualRANavigation).__init__()
		self.cur_node = 1
		self.create_path()
		self.animation_start_time = None
		self.animation_start_pos = None
		self.animation_target_pos = None


	def set_inputs(self, scenegraph, navigation_node, head_node):
		self.scenegraph = scenegraph
		self.navigation_node = navigation_node
		self.head_node = head_node
		self.always_evaluate(True)

	def create_path(self):
		self.path = {1:[(2,avango.gua.Vec3(0,0,2))],2:[(3,avango.gua.Vec3(0,0,2))]}

	def end(self):
		boolean = True

	def evaluate(self):
		if (self.animation_start_pos != None):
			direction_animation =  self.animation_target_pos - self.animation_start_pos
			speed = 0.3
			dist = math.sqrt(direction_animation.x**2+direction_animation.y**2+direction_animation.z**2)
			total_time = dist / speed
			elapsed_time = time.time() - self.animation_start_time
			fraction = elapsed_time / total_time
			self.navigation_node.Transform.value = avango.gua.make_trans_mat(self.animation_start_pos.x + fraction * direction_animation.x, self.animation_start_pos.y + fraction * direction_animation.y, self.animation_start_pos.z + fraction * direction_animation.z)
			if (elapsed_time >= total_time):
			    self.navigation_node.Transform.value = avango.gua.make_trans_mat(self.animation_target_pos.x, self.animation_target_pos.y, self.animation_target_pos.z)
			    self.animation_start_pos = None
			    self.animation_start_time = None
			    self.animation_target_pos = None
			    self.cur_node = self.path[self.cur_node][0][0]
		else:
			self.new_start()
#		self.navigation_node.Transform.value *= avango.gua.make_trans_mat(movement_vector.x*0.1,movement_vector.y*0.1,movement_vector.z*0.1) 
#		print(self.sf_navigation_matrix.value)
#		self.cur_node = self.path[self.cur_node][0][0]
		if self.cur_node == 3:
			self.always_evaluate(False)
			print("Stop")

	def new_start(self):
		print(self.cur_node)
		movement_vector = self.path[self.cur_node][0][1]
		self.animation_target_pos = (self.navigation_node.Transform.value * avango.gua.make_trans_mat(movement_vector)).get_translate()
		self.animation_start_pos = self.navigation_node.Transform.value.get_translate()
		self.animation_start_time = time.time()

