#!/usr/bin/python3

# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua
import avango.vive

# import application libraries
import config

# appends a camera node, screen nodes, and navigation capabilities to the scenegraph
class ViveViewingSetup:

    def __init__(self, scenegraph):
        self.scenegraph = scenegraph

        # create daemon stations
        device_service = avango.daemon.DeviceService()
        self.hmd_sensor = avango.daemon.nodes.DeviceSensor(
            DeviceService=device_service)
        self.hmd_sensor.Station.value = 'gua-device-hmd-0-0'
        self.controller1_sensor = avango.daemon.nodes.DeviceSensor(
            DeviceService=device_service)
        self.controller1_sensor.Station.value = 'gua-device-hmd-0-1'

        # navigation node
        self.navigation_node = avango.gua.nodes.TransformNode(
            Name='navigation_node')
        self.scenegraph.Root.value.Children.value.append(self.navigation_node)
        self.navigation_node.Transform.value = avango.gua.make_trans_mat(-24,0,-24)
        # user node
        self.user_node = avango.gua.nodes.TransformNode(
            Name='user_node')

        # screen nodes
        self.left_screen_node = avango.gua.nodes.ScreenNode(
            Name='left_screen_node')
        self.right_screen_node = avango.gua.nodes.ScreenNode(
            Name='right_screen_node')

        # camera node (head)
        self.camera_node = avango.gua.nodes.CameraNode(Name='Vive-HMD-User')
        self.camera_node.SceneGraph.value = self.scenegraph.Name.value
        self.camera_node.EnableStereo.value = True
        self.camera_node.EnableFrustumCulling.value = False
        self.camera_node.LeftScreenPath.value = '/navigation_node/user_node/Vive-HMD-User/left_screen_node'
        self.camera_node.RightScreenPath.value = '/navigation_node/user_node/Vive-HMD-User/right_screen_node'
        self.camera_node.BlackList.value = ['invisible']
        self.camera_node.Transform.connect_from(self.hmd_sensor.Matrix)

        # attach nodes
        self.navigation_node.Children.value.append(self.user_node)
        self.user_node.Children.value.append(self.camera_node)
        self.camera_node.Children.value.append(self.left_screen_node)
        self.camera_node.Children.value.append(self.right_screen_node)

        # controller transform nodes for external use
        self.controller1_transform = avango.gua.nodes.TransformNode(
            Name='controller_node')
        self.controller1_transform.Transform.connect_from(
            self.controller1_sensor.Matrix)
        self.user_node.Children.value.append(self.controller1_transform)

        # controller geometries
        self.controller1 = self.create_controller_object()
        self.controller1_transform.Children.value.append(self.controller1)

    # creates a virtual model representing a vive controller
    def create_controller_object(self):
        loader = avango.gua.nodes.TriMeshLoader()
        controller = loader.create_geometry_from_file('controller',
                                                      'data/objects/vive_controller/vive_controller.obj',
                                                      avango.gua.LoaderFlags.LOAD_MATERIALS)
        controller.Material.value.set_uniform('Roughness', 0.5)
        controller.Material.value.set_uniform('Emissivity', 1.0)
        controller.ShadowMode.value = avango.gua.ShadowMode.OFF
        return controller

    # registers a vive window created in the class Renderer with the camera node
    def register_window(self, window):
        self.left_screen_node.Width.value = window.LeftScreenSize.value.x
        self.left_screen_node.Height.value = window.LeftScreenSize.value.y
        self.left_screen_node.Transform.value = avango.gua.make_trans_mat(
            window.LeftScreenTranslation.value)

        self.right_screen_node.Width.value = window.RightScreenSize.value.x
        self.right_screen_node.Height.value = window.RightScreenSize.value.y
        self.right_screen_node.Transform.value = avango.gua.make_trans_mat(
            window.RightScreenTranslation.value)

        self.camera_node.OutputWindowName.value = window.Title.value
        self.camera_node.Resolution.value = window.Size.value
        self.camera_node.EyeDistance.value = window.EyeDistance.value

        avango.gua.register_window(window.Title.value, window)

    # registers a pipeline description in the class Renderer with the camera node
    def register_pipeline_description(self, pipeline_description):
        self.camera_node.PipelineDescription.value = pipeline_description

    # applys a material uniform to all TriMeshNode instances below the specified start node
    def apply_material_uniform_recursively(self, start_node, uniform_name, uniform_value):
        if start_node.__class__.__name__ == "TriMeshNode":
            start_node.Material.value.set_uniform(uniform_name, uniform_value)

        for child in start_node.Children.value:
            self.apply_material_uniform_recursively(
                child, uniform_name, uniform_value)

    # applys a backface culling value to all TriMeshNode instances below the specified start node
    def apply_backface_culling_recursively(self, start_node, boolean):
        if start_node.__class__.__name__ == "TriMeshNode":
            start_node.Material.value.EnableBackfaceCulling.value = boolean

        for child in start_node.Children.value:
            self.apply_backface_culling_recursively(child, boolean)
