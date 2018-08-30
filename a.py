import bpy

B_E = 0.01

class Wall:
	def __init__(self, size=(1,1,1)):
		self.size = size
		self.holes = []
		
	def add_hole(self, size, location):
		self.holes.append({'size': size, 'location': location})
		

class Floor:
	def __init__(self):
		self.walls = []
		
	def add_wall(self, wall, location):
		self.walls.append({'wall': wall, 'location': location})
	

class House:

	def __init__(self, length=9, width=6, plate=0.2, height=3, wall=0.5, floors=1, plate_dw=-0.1):
		self.length = length
		self.width = width
		self.plate = plate
		self.height = height
		self.wall = wall
		self.plate_dw = plate_dw
		self.floors = floors
		
		self.o_floors = {}
		for n_floor in range(1, floors+1):
			w = Wall(size=(self.length, self.width, self.height))
			w.add_hole(
				size=(self.length-2*self.wall, self.width-2*self.wall, self.height),
				location=(0,0,0)
				)
			
			for j in ((-1,0), (1,0), (0,-1), (0,1)):
				size = (
					2.08*abs(j[0]) + (self.wall+B_E)*abs(j[1]),
					(self.wall+B_E)*abs(j[0]) + 2.08*abs(j[1]),
					1.42,
				)
				for i in (1,0,-1):
					location = (
						(i*self.length/3)*abs(j[0]) + (self.length/2-self.wall/2)*j[1], 
						(self.width/2-self.wall/2)*j[0] + (i*self.length/3)*abs(j[1]),
						0
					)
					w.add_hole(size=size, location=location)
			
			f = Floor()
			f.add_wall(wall=w, location=(0,0,0))
			
			self.o_floors[n_floor] = {
				'floor': f,
				'location': (0, 0, self.plate*n_floor+self.height*(n_floor-0.5)),
			}
	
	@property
	def plate_scale(self):
		return (self.length/2+self.plate_dw/2, self.width/2+self.plate_dw/2, self.plate/2)
	
	def get_plate_location(self, floor):
		return (0, 0, self.plate/2 + floor*(self.plate+self.height) )
		
	@property
	def walls_scale(self):
		return (self.length/2, self.width/2, self.height/2)
		
	def get_walls_location(self, floor):
		return (0, 0, self.plate+self.height/2 + floor*(self.plate+self.height) )
		
	@property
	def walls_delta(self):
		return (H.wall, H.wall, 0)
		
		
def bpy_add_cube(scale, location, name=None):
	bpy.ops.mesh.primitive_cube_add(location=location)
	bco = bpy.context.object
	if name is not None:
		bco.name = name 
	bco.scale = scale
	return bco

def bpy_add_empty_cube(scale, location, delta, name=None):
	object = bpy_add_cube(name=name, scale=scale, location=location)
	hole_scale = (
		scale[0]-delta[0]+B_E,
		scale[1]-delta[1]+B_E,
		scale[2]-delta[2]+B_E,
	)
	deleter = bpy_add_cube(scale=hole_scale, location=location)
	bpy_obj_minus_obj(object=object, deleter=deleter)
	return object
	
def bpy_obj_minus_obj(object, deleter, delete_deleter=True):
	mod_bool = object.modifiers.new('modifier', 'BOOLEAN')
	mod_bool.operation = 'DIFFERENCE'
	mod_bool.object = deleter
	
	bpy.context.scene.objects.active = object
	bpy.ops.object.modifier_apply(modifier = 'modifier')

	if delete_deleter:
		deleter.select = True
		bpy.ops.object.delete()
		
def bpy_obj_plus_obj(object, addition, delete_addition=True):
	mod_bool = object.modifiers.new('modifier', 'BOOLEAN')
	mod_bool.operation = 'UNION'
	mod_bool.object = addition
	
	bpy.context.scene.objects.active = object
	bpy.ops.object.modifier_apply(modifier = 'modifier')

	if delete_addition:
		addition.select = True
		bpy.ops.object.delete()

		
class WallBlender:
	def __init__(self, wall, location):
		self.wall = wall
		self.location = location
		self.b_wall = None
	
	def render(self):
		b_wall = bpy_add_cube(
			scale=(self.wall.size[0]/2, self.wall.size[1]/2, self.wall.size[2]/2),
			location=(0,0,0)
			)
		
		for hole in self.wall.holes:
			h = bpy_add_cube(
				scale=(hole['size'][0]/2+B_E, hole['size'][1]/2+B_E, hole['size'][2]/2+B_E),
				location=(hole['location'][0], hole['location'][1], hole['location'][2])
			)
			bpy_obj_minus_obj(object=b_wall, deleter=h)
			
		b_wall.location = self.location
		self.b_wall = b_wall
		
		
class FloorBlender:
	def __init__(self, floor, location, name):
		self.floor = floor
		self.location = location
		self.name = name
		self.b_floor = None
		
	def render(self):
		first = None
		for the_wall in self.floor.walls:
			wb = WallBlender(wall=the_wall['wall'], location=the_wall['location'])
			wb.render()
			if first is None:
				first = wb.b_wall
				first.name = self.name
			else:
				bpy_obj_plus_obj(object=first, addition=wb.b_wall)
		first.location = self.location
		self.b_floor = first


class HouseBlender():

	def __init__(self, house):
		self.house = house
		self.plates = {}
		self.walls = {}
		
	def render(self):
		self.render_plates()
		self.render_walls()
	
	def render_plates(self):
		for floor in range(0, self.house.floors):
			self.render_plates_floor(floor)
			
	def render_plates_floor(self, floor):
		self.plates[floor] = bpy_add_cube(
			name='plate%i' % floor,
			scale=self.house.plate_scale,
			location=self.house.get_plate_location(floor)
			)
	
	def render_walls(self):
		for n_floor in range(1, self.house.floors+1):
			self.render_walls_floor(self.house.o_floors[n_floor], 'floor%i' % (n_floor))
					
	def render_walls_floor(self, the_floor, the_name):
		fb = FloorBlender(the_floor['floor'], the_floor['location'], the_name)
		fb.render()

	
h_params = {
	'length': 12,
	'width': 12,
	'wall': 0.375,
	'height': 2.75,
	'floors': 2,
}

H = House(**h_params)

bpy_add_cube(name='human', scale=(0.6/2, 0.2/2, 1.78/2), location=(0, 0, 1.78/2+H.plate))
bpy_add_cube(name='ground', scale=(15,15,B_E), location=(0,0,0))

HB = HouseBlender(H)
HB.render()
