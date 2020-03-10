#!/usr/bin/python3

# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua
import avango.script
from avango.script import field_has_changed

#
import time
import math
from lib.Picker import *

class VirtualRANavigation(avango.script.Script):

	# input fields
	sf_controller_matrix = avango.gua.SFMatrix4()
	sf_controller_matrix.value = avango.gua.make_identity_mat()

	sf_rocker = avango.SFFloat()
	sf_rocker.value = 0.0

	sf_grip_button = avango.SFBool()
	sf_grip_button.value = False

	# constant fields
	damping_const = 5

	# output field
	sf_navigation_matrix = avango.gua.SFMatrix4()
	sf_navigation_matrix.value = avango.gua.make_identity_mat()

	def __init__(self):
		self.super(VirtualRANavigation).__init__()
		self.cur_node = 1
		self.boolean = True
		self.create_path()
		self.lf_time = time.time()
		self.animation_start_time = None
		self.animation_start_pos = None
		self.animation_target_pos = None
		self.user_pos = None


	def set_inputs(self, scenegraph, navigation_node, head_node, user_node, controller_node, controller_sensor):
		self.scenegraph = scenegraph
		self.navigation_node = navigation_node
		self.head_node = head_node
		self.user_node = user_node
		self.controller_node = controller_node
		self.controller_sensor = controller_sensor
		self.sf_controller_matrix.connect_from(self.controller_node.Transform)
		self.sf_rocker.connect_from(self.controller_sensor.Value3)
		self.sf_grip_button.connect_from(self.controller_sensor.Button2)
		
	def run(self):
		print("Start")
		self.always_evaluate(self.boolean)
		
	def create_path(self):
		self.path = {}
		self.path = {1:[(2,avango.gua.Vec3(-4,0,-10))],2:[(3,avango.gua.Vec3(20,0,-10))],3:[(4,avango.gua.Vec3(-4,0,-10))],4:[(5,avango.gua.Vec3(-4,0,-10))],5:[(6,avango.gua.Vec3(-4,0,-10))],6:[(7,avango.gua.Vec3(-4,0,-10))]}

	def evaluate(self):

		if self.sf_rocker.value:
			print("user moves")
			self.user_movement()
		else:
			print("at center")
			self.user_node.Transform.value = avango.gua.make_identity_mat()

		position = self.head_node.WorldTransform.value.get_translate()
		trans_y = 0
		height_figure = 2
		picker = Picker(self.scenegraph)
		result = picker.compute_pick_result(position,avango.gua.Vec3(0.0, -1.0, 0.0),10,['invisible'])

		if (result != None):
			if (result.Distance.value < height_figure):
			    trans_y += 0.01
			elif (result.Distance.value > height_figure):
			    trans_y -= 0.01

		if (self.cur_node >= (len(self.path))+1):
			self.boolean = False
			print("Stop")
		else:
			if (self.animation_start_pos != None):
				self.animation_target_pos.y += trans_y
				direction_animation =  self.animation_target_pos - self.animation_start_pos
				dist = math.sqrt(direction_animation.x**2+direction_animation.z**2)
				total_time = dist / self.speed_control_platform()
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
		self.always_evaluate(self.boolean)

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
		# compute movement vector
		now = time.time()

		position = self.head_node.WorldTransform.value.get_translate()
		trans_y = 0
		height_figure = 2
		picker = Picker(self.scenegraph)
		result = picker.compute_pick_result(position,avango.gua.Vec3(0.0, -1.0, 0.0),100,['invisible'])

		if (result != None):
			if (result.Distance.value < height_figure):
			    trans_y += 0.01
			elif (result.Distance.value > height_figure):
			    trans_y -= 0.01

		speed = self.sf_rocker.value * self.speed_control_user() * (now - self.lf_time)
		forward_matrix = self.controller_node.WorldTransform.value * \
		    avango.gua.make_trans_mat(0.0, 0.0, -1.0)
		forward_vector = forward_matrix.get_translate() - \
		    self.controller_node.WorldTransform.value.get_translate()
		forward_vector.normalize()
		movement_vector = forward_vector * speed

		# restrict movements to ground plane
		movement_vector.y = 0.0
		print(movement_vector)
		self.user_node.Transform.value *= avango.gua.make_trans_mat(movement_vector)
		self.lf_time = now
		
	def select_node(self):
		return 0

	def speed_control_platform(self):
		return 2

	def speed_control_user(self):
		base = avango.gua.make_identity_mat()
		spring_length = self.user_node.Transform.value.get_translate() - base.get_translate()
		dist = math.sqrt(spring_length.x ** 2 + spring_length.y ** 2 + spring_length.z ** 2)
		if dist != 0:
			return self.damping_const/dist
		else:
			return self.damping_const
