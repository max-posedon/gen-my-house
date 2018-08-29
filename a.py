import bpy

B_E = 0.01

class House:

	def __init__(self, length=9, width=6, plate=0.2, height=3, wall=0.5, plate_dw=-0.1):
		self.length = length
		self.width = width
		self.plate = plate
		self.height = height
		self.wall = wall
		self.plate_dw = plate_dw
	
	@property
	def plate_scale(self):
		return (self.length/2+self.plate_dw/2, self.width/2+self.plate_dw/2, self.plate/2)
	
	@property
	def plate_location(self):
		return (0, 0, self.plate/2)
		
	@property
	def plate_1_location(self):
		return (0, 0, self.plate+self.height+self.plate/2)
		
	@property
	def walls_scale(self):
		return (self.length/2, self.width/2, self.height/2)
	
	@property
	def walls_location(self):
		return (0, 0, self.plate+self.height/2)
		
	@property
	def walls_1_location(self):
		return (0, 0, self.plate*2+self.height*1.5)
		
	@property
	def walls_delta(self):
		return (H.wall, H.wall, 0)
		
def bpy_add_cube(name, scale, location):
	bpy.ops.mesh.primitive_cube_add(location=location)
	bco = bpy.context.object
	if name is not None:
		bco.name = name 
	bco.scale = scale
	return bco

def bpy_add_empty_cube(name, scale, location, delta):
	object = bpy_add_cube(name=name, scale=scale, location=location)
	hole_scale = (
		scale[0]-delta[0]+B_E,
		scale[1]-delta[1]+B_E,
		scale[2]-delta[2]+B_E,
	)
	deleter = bpy_add_cube(name=None, scale=hole_scale, location=location)
	bpy_obj_minus_obj(object=object, deleter=deleter, delete_deleter=True)
	return object
	
def bpy_obj_minus_obj(object, deleter, delete_deleter):
	mod_bool = object.modifiers.new('modifier', 'BOOLEAN')
	mod_bool.operation = 'DIFFERENCE'
	mod_bool.object = deleter
	
	bpy.context.scene.objects.active = object
	bpy.ops.object.modifier_apply(modifier = 'modifier')

	if delete_deleter:
		deleter.select = True
		bpy.ops.object.delete()

h_params = {
	'length': 12,
	'width': 12,
	'wall': 0.375,
	'height': 2.75,
}

H = House(**h_params)

bpy_add_cube(name='human', scale=(0.6/2, 0.2/2, 1.78/2), location=(0,0,1.78/2+H.plate))
bpy_add_cube(name='ground', scale=(15,15,B_E), location=(0,0,0))

walls = {}

plate = bpy_add_cube(name='plate', scale=H.plate_scale, location=H.plate_location)
walls[1] = bpy_add_empty_cube(name='walls', scale=H.walls_scale, location=H.walls_location, delta=H.walls_delta)
plate1 = bpy_add_cube(name='plate1', scale=H.plate_scale, location=H.plate_1_location)

walls[2] = bpy_add_empty_cube(name='walls1', scale=H.walls_scale, location=H.walls_1_location, delta=H.walls_delta)


for floor in (1,2):
	for j in ((-1,0), (1,0), (0,-1), (0,1)):
		scale = (
			2.08/2*abs(j[0])+(H.wall/2+B_E*10)*abs(j[1]),
			(H.wall/2+B_E*10)*abs(j[0])+2.08/2*abs(j[1]),
			1.42/2,
		)
		for i in (1,0,-1):
			w_params = {
				'scale': scale,
				'location': (
					(i*H.length/3)*abs(j[0]) + (H.length/2-H.wall/2)*j[1], 
					(H.width/2-H.wall/2)*j[0] + (i*H.length/3)*abs(j[1]),
					H.plate*floor+H.height*(floor-0.5),
					)
			}
			window = bpy_add_cube(name=None,**w_params)
			bpy_obj_minus_obj(object=walls[floor], deleter=window, delete_deleter=True)