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

	# input fields
	limit = 5
	# output field
	#sf_navigation_matrix = avango.gua.SFMatrix4()
	#sf_navigation_matrix.value = avango.gua.make_identity_mat()


	def __init__(self):
		self.super(VirtualRANavigation).__init__()
		self.cur_node = 1
		self.create_path()
		self.animation_start_time = None
		self.animation_start_pos = None
		self.animation_target_pos = None


	def set_inputs(self, scenegraph, navigation_node, head_node, user_node):
		self.scenegraph = scenegraph
		self.navigation_node = navigation_node
		self.head_node = head_node
		self.user_node = user_node
		self.always_evaluate(True)

	def create_path(self):
		#self.path = {}
		self.path = {1:[(2,avango.gua.Vec3(-4,0,40)),(3,avango.gua.Vec3(-40,0,4)),(4,avango.gua.Vec3(40,0,4))],2:[(5,avango.gua.Vec3(-10,0,0))],3:[(6,avango.gua.Vec3(3,0,5))],4:[(7,avango.gua.Vec3(3,0,5))],5:[(8,avango.gua.Vec3(3,0,5))],6:[(9,avango.gua.Vec3(3,0,0))]}

	def end(self):
		boolean = True

	def evaluate(self):
		if (self.cur_node >= (len(self.path))+1):
			self.always_evaluate(False)
			print("Stop")
		else:
			if (self.animation_start_pos != None):
				direction_animation =  self.animation_target_pos - self.animation_start_pos
				dist = math.sqrt(direction_animation.x**2+direction_animation.y**2+direction_animation.z**2)
				total_time = dist / self.speed_control()
				elapsed_time = time.time() - self.animation_start_time
				fraction = elapsed_time / total_time
				user_dist = self.head_node.Transform.value.get_translate() - self.navigation_node.Transform.value.get_translate()
				#print(user_dist)
				self.navigation_node.Transform.value = avango.gua.make_trans_mat(self.animation_start_pos.x + fraction * direction_animation.x, self.animation_start_pos.y + fraction * direction_animation.y, self.animation_start_pos.z + fraction * direction_animation.z)
				#self.user_movement()
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

	def new_start(self):
		print(self.cur_node)
		new_node = self.select_node()
		if len(self.path[self.cur_node]) == 3:
			movement_vector = self.path[self.cur_node][new_node][1]
		else:
			movement_vector = self.path[self.cur_node][0][1]
		self.animation_target_pos = (self.navigation_node.Transform.value * avango.gua.make_trans_mat(movement_vector)).get_translate()
		self.animation_start_pos = self.navigation_node.Transform.value.get_translate()
		self.animation_start_time = time.time()

	def user_movement(self):
		print('a')
		to_travel = avango.gua.Vec3(0,0,-0.001)
		to_travel = avango.gua.make_rot_mat(self.head_node.WorldTransform.value.get_rotate()) * avango.gua.make_trans_mat(to_travel)
		to_travel = to_travel.get_translate()
		print(to_travel)
		user_pos = self.head_node.Transform.value.get_translate()
		pos = self.user_node.Transform.value.get_translate()
		if ((pos.z <= self.limit) and (pos.z >= -self.limit)):	
			self.user_node.Transform.value = self.user_node.Transform.value * avango.gua.make_trans_mat(to_travel)
		

	def select_node(self):
		print(self.head_node.WorldTransform.value.get_rotate().w)
		if ((self.head_node.WorldTransform.value.get_rotate().w) > 0.2 and (self.head_node.WorldTransform.value.get_rotate().w) < 0.8):
			return 0
		elif (self.head_node.WorldTransform.value.get_rotate().w) < 0.2:
			return 1
		else:
			return 2
		return 0

	def speed_control(self):
		return 0.5

