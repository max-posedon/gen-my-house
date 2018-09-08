import bpy

class House:
	class Foundation:
		def __init__(self, height, shift):
			self.height = height
			self.shift = shift
			
	class Floor:
		def __init__(self, height):
			self.height = height

	def __init__(self, width, depth):
		self.width = width
		self.depth = depth
		self.foundation = None
		self.floors = []
	
	def add_foundation(self, height, shift):
		self.foundation = House.Foundation(height, shift)
	
	def add_floor(self, height):
		floor = House.Floor(height)
		self.floors.append(floor)
		return floor

		
B_E = 0.001

def bpy_add_cube(size, location, name=None):
	bpy.ops.mesh.primitive_cube_add(location=location)
	bco = bpy.context.object
	if name is not None:
		bco.name = name
	
	bco.scale = (size[0]/2, size[1]/2, size[2]/2)
	return bco


def bpy_obj_minus_obj(object, deleter, delete_deleter=True):
	mod_bool = object.modifiers.new('modifier', 'BOOLEAN')
	mod_bool.operation = 'DIFFERENCE'
	mod_bool.object = deleter
	
	bpy.context.scene.objects.active = object
	bpy.ops.object.modifier_apply(modifier = 'modifier')

	if delete_deleter:
		deleter.select = True
		bpy.ops.object.delete()
	
	
class BlenderHouse:
	def __init__(self, house):
		self.house = house
	
	def render(self):
		self.render_bounds()
		self.render_foundation()
	
	def render_bounds(self):
		h = bpy_add_cube(size=(house.width, house.depth, B_E), location=(0,0,B_E/2), name='bounds')
	
	def render_foundation(self):
		if not house.foundation:
			return
		
		h = bpy_add_cube(
			size=(house.width - house.foundation.shift, house.depth - house.foundation.shift, house.foundation.height), 
			location=(0,0,house.foundation.height/2), 
			name='foundation'
			)


# house configuration
house = House(width=10.5, depth=12.5)
house.add_foundation(height=0.2, shift=0.1)
house.add_floor(height=3)

# render ground
bpy_add_cube(name='ground', size=(30,50,B_E), location=(0,0,-B_E/2))

# render house
hb = BlenderHouse(house)
hb.render()

