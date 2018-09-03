from enum import Enum

import bpy

B_E = 0.001

class Hole:
	def __init__(self, size, location):
		self.size = size
		self.location = location


class Wall:
	def __init__(self, size=(1,1,1)):
		self.length = size[0]
		self.width = size[1]
		self.height = size[2]
		self.holes = []
		
	@property
	def size(self):
		return (self.length, self.width, self.height)
		
	def add_hole(self, size, location):
		self.holes.append(Hole(size=size, location=location))
		
	def add_l_hole(self, relative, length, height, base_height=0):
		s = (length, self.width, height)
		l = (self.length/2*relative, 0, base_height+(height-self.height)/2)	
		return self.add_hole(size=s, location=l)
		
	def add_w_hole(self, relative, width, height, base_height=0):
		s = (self.length, width, height)
		l = (0, self.width/2*relative, base_height+(height-self.height)/2)	
		return self.add_hole(size=s, location=l)
	
	
class Floor:
	class WallType(Enum):
		none = 0
		external = 1
		internal = 2
		thin = 3
		

	def __init__(self, length, width, height, external_wall, internal_wall, thin_wall):
		self.length = length
		self.width = width
		self.height = height
		self.external_wall = external_wall
		self.internal_wall = internal_wall
		self.thin_wall = thin_wall
		self.walls = []
		
		w = Wall(size=(1,1,1))
		w.add_hole(size=(1,1,1), location=(0,0,0))
		self.add_wall(wall=w, location=(0,0,0))
		
	@property
	def in_length(self):
		return self.length-2*self.external_wall
		
	@property
	def in_width(self):
		return self.width-2*self.external_wall
		
	def wall(self, wall_type=WallType.none):
		if wall_type == Floor.WallType.external:
			return self.external_wall
		elif wall_type == Floor.WallType.internal:
			return self.internal_wall
		elif wall_type == Floor.WallType.thin:
			return self.thin_wall
		else:
			raise NotImplementedError

		
	def add_wall(self, wall, location):
		return self.walls.append({'wall': wall, 'location': location})
		
	def add_l_wall(self, relative, size=(-1,1), wall_type=WallType.internal):
		wall = self.wall(wall_type)

		if wall_type == Floor.WallType.internal or wall_type == Floor.WallType.thin:
			s = (self.in_length*(size[1]-size[0])/2, wall, self.height)
			l = (self.in_length*(size[1]+size[0])/4, self.in_width/2*relative, 0)
		elif wall_type == Floor.WallType.external:
			s = (self.length*(size[1]-size[0])/2, wall, self.height)
			l = (self.length*(size[1]+size[0])/4, (self.width-wall)/2*relative, 0)	
		else:
			raise NotImplementedError
		
		w = Wall(size=s)
		self.walls.append({'wall': w, 'location': l})
		return w
		
	def add_w_wall(self, relative, size=(-1,1), wall_type=WallType.internal):
		wall = self.wall(wall_type)
	
		if wall_type == Floor.WallType.internal or wall_type == Floor.WallType.thin:
			s = (wall, self.in_width*(size[1]-size[0])/2, self.height)
			l = (self.in_length/2*relative, self.in_width*(size[1]+size[0])/4, 0)
		elif wall_type == Floor.WallType.external:
			s = (wall, self.width*(size[1]-size[0])/2, self.height)
			l = ((self.length-wall)/2*relative, self.width*(size[1]+size[0])/4, 0)
		else:
			raise NotImplementedError
		
		w = Wall(size=s)
		self.walls.append({'wall': w, 'location': l})
		return w
		
	def add_w_walls(self, relative, sizes, wall_type=WallType.internal):
		for size in sizes:
			self.add_w_wall(relative, size, wall_type)
			
	def add_l_walls(self, relative, sizes, wall_type=WallType.internal):
		for size in sizes:
			self.add_l_wall(relative, size, wall_type)
	

class House:

	def __init__(self, length=9, width=6, plate=0.2, height=3, external_wall=0.4, internal_wall=0.2, thin_wall=0.1, floors=1, plate_dw=-0.1, generate=False):
		self.length = length
		self.width = width
		self.plate = plate
		self.height = height
		self.external_wall = external_wall
		self.internal_wall = internal_wall
		self.thin_wall = thin_wall
		self.plate_dw = plate_dw
		self.floors = floors
		
		self.o_floors = {}
		for n_floor in range(1, floors+1):
			f = Floor(length=length, width=width, height=height, external_wall=external_wall, internal_wall=internal_wall, thin_wall=thin_wall)
			
			l_walls = [ f.add_l_wall(-1, wall_type=Floor.WallType.external), f.add_l_wall(1, wall_type=Floor.WallType.external) ]
			r_walls = [ f.add_w_wall(-1, wall_type=Floor.WallType.external), f.add_w_wall(1, wall_type=Floor.WallType.external) ]
			
			if generate:
				for w in l_walls:
					for i in (-0.66, 0, 0.66):
						w.add_l_hole(i, 2.08, 1.42, 0.5)
				for w in r_walls:
					for i in (0.66, 0, -0.66):
						w.add_w_hole(i, 2.08, 1.42, 0.5)
			
			self.o_floors[n_floor] = {
				'floor': f,
				'location': (0, 0, self.plate*n_floor+self.height*(n_floor-0.5)),
			}
	
	@property
	def plate_scale(self):
		return (self.length/2+self.plate_dw/2, self.width/2+self.plate_dw/2, self.plate/2)
	
	def get_plate_location(self, floor):
		return (0, 0, self.plate/2 + floor*(self.plate+self.height) )
				
		
def bpy_add_cube(scale, location, name=None):
	bpy.ops.mesh.primitive_cube_add(location=location)
	bco = bpy.context.object
	if name is not None:
		bco.name = name 
	bco.scale = scale
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


def bpy_obj_plus_obj(object, addition):
	obs = [object, addition]
	ctx = bpy.context.copy()
	ctx['active_object'] = obs[0]
	ctx['selected_objects'] = obs
	ctx['selected_editable_bases'] = [bpy.context.scene.object_bases[ob.name] for ob in obs]
	bpy.ops.object.join(ctx)

		
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
				scale=(hole.size[0]/2+B_E, hole.size[1]/2+B_E, hole.size[2]/2+B_E),
				location=(hole.location)
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

'''
h_params = {
	'length': 12,
	'width': 12,
	'wall': 0.4,
	'height': 3,
	'floors': 1,
}
H = House(generate=True, **h_params)
w = H.o_floors[1]['floor'].add_l_wall(0.5, (0,1), 0.2)
w.add_l_hole(0, 1, 2)	
w.add_l_hole(1, 1, 2)
w.add_l_hole(-1, 1, 2)

w = H.o_floors[1]['floor'].add_w_wall(0, (-1,1), 0.2)
w.add_w_hole(0, 1, 2)	
w.add_w_hole(0.5, 1, 2)
w.add_w_hole(-0.5, 1, 2)
'''

h_params = {
	'length': 10.5,
	'width': 12.5,
	'height': 3,
	'floors': 2,
}

H = House(generate=True, **h_params)

w = H.o_floors[1]['floor'].add_w_wall(0, (-1,1))
w.add_w_hole(-0.8, 1, 2)
w.add_w_hole(-0.5, 1, 2)
w.add_w_hole(0.2, 1, 2)

w = H.o_floors[1]['floor'].add_w_wall(-0.5, (-1, 0.33))
w.add_w_hole(-0.8, 1, 2)
w.add_w_hole(0.8, 1, 2)

w = H.o_floors[1]['floor'].add_l_wall(0.33, (-1,1))
w.add_l_hole(-0.8, 1, 2)
w.add_l_hole(0.2, 1.5, 2)
w.add_l_hole(0.7, 2, 2)

w = H.o_floors[1]['floor'].add_l_wall(-0.33, (-1,1))
w.add_l_hole(-0.25, 2, 2)
w.add_l_hole(0.2, 1, 2)

H.o_floors[2]['floor'].add_w_walls(0, [(-1,-0.33), (0.33,1)])

w = H.o_floors[2]['floor'].add_l_wall(0.33, (-1, 1))
w.add_l_hole(-0.2, 1, 2)
w.add_l_hole(0.2, 1, 2)

H.o_floors[2]['floor'].add_l_wall(-0.33, (-1, -0.5))
w = H.o_floors[2]['floor'].add_l_wall(-0.33, (0, 1))
w.add_l_hole(-0.6, 1, 2)

w = H.o_floors[2]['floor'].add_w_wall(-0.5, (-0.6, 0.33))
w.add_w_hole(-0.7, 1, 2)
w.add_w_hole(0.7, 1, 2)

bpy_add_cube(name='human', scale=(0.2/2, 0.5/2, 1.78/2), location=(0, 0, 1.78/2+H.plate))
bpy_add_cube(name='ground', scale=(15,15,B_E), location=(0,0,0))

HB = HouseBlender(H)
HB.render()
