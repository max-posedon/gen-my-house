import bpy

class House:
	class Foundation:
		def __init__(self, height, shift):
			self.height = height
			self.shift = shift

	class Overlap:
		def __init__(self, height, shift, altitude):
			self.height = height
			self.shift = shift
			self.altitude = altitude
			
	class Floor:
		class Wall:
			class Hole:
				def __init__(self, size, location):
					self.size = size
					self.location = location

			def __init__(self, size, location):
				self.size = size
				self.location = location
				self.holes = []
				
			@property
			def bound_left(self):
				return self.location[0]-self.size[0]/2
			
			@property
			def bound_right(self):
				return self.location[0]+self.size[0]/2
			
			@property
			def bound_back(self):
				return self.location[1]+self.size[1]/2
			
			@property
			def bound_front(self):
				return self.location[1]-self.size[1]/2
			
			def add_w_hole(self, relative_width, width, height, base_height):
				size = (width, self.size[1], height)
				location = (self.size[0]/2*relative_width, 0, base_height+(height-self.size[2])/2)
				hole = House.Floor.Wall.Hole(size, location)
				self.holes.append(hole)
				return hole
			
			def add_d_hole(self, relative_depth, depth, height, base_height):
				size = (self.size[0], depth, height)
				location = (0, self.size[1]/2*relative_depth, base_height+(height-self.size[2])/2)
				hole = House.Floor.Wall.Hole(size, location)
				self.holes.append(hole)
				return hole
	
		def __init__(self, height, thickness, altitude, width, depth):
			self.height = height
			self.thickness = thickness
			self.altitude = altitude
			self.width = width
			self.depth = depth
			self.walls = {}
			
			self.add_d_wall((-1,1), -1+thickness/width, thickness, "left")
			self.add_d_wall((-1,1),  1-thickness/width, thickness, "right")
			self.add_w2_wall("left", "right",  1-thickness/depth, thickness, "back")
			self.add_w2_wall("left", "right", -1+thickness/depth, thickness, "front")
			
		def add_w_wall(self, relative_width, relative_depth, thickness, name):
			size = (self.width*(relative_width[1]-relative_width[0])/2, thickness, self.height)
			location = (self.width*(relative_width[1]+relative_width[0])/4, self.depth/2*relative_depth, 0)
			wall = House.Floor.Wall(size, location)
			self.walls[name] = wall
			return wall
			
		def add_d_wall(self, relative_depth, relative_width, thickness, name):
			size = (thickness, self.depth*(relative_depth[1]-relative_depth[0])/2, self.height)
			location = (self.width/2*relative_width, self.depth*(relative_depth[1]+relative_depth[0])/4, 0)
			wall = House.Floor.Wall(size, location)
			self.walls[name] = wall
			return wall
			
		def add_w2_wall(self, left, right, relative_depth, thickness, name):
			left_wall = self.walls[left]
			right_wall = self.walls[right]
			size = (right_wall.bound_left-left_wall.bound_right, thickness, self.height)
			location = ((right_wall.bound_left+left_wall.bound_right)/2, self.depth/2*relative_depth, 0)
			wall = House.Floor.Wall(size, location)
			self.walls[name] = wall
			return wall
		
		def add_d2_wall(self, front, back, relative_width, thickness, name):
			front_wall = self.walls[front]
			back_wall = self.walls[back]
			size = (thickness, back_wall.bound_front-front_wall.bound_back, self.height)
			location = (self.width/2*relative_width, (back_wall.bound_front+front_wall.bound_back)/2, 0)
			wall = House.Floor.Wall(size, location)
			self.walls[name] = wall
			return wall
		
	def __init__(self, width, depth):
		self.width = width
		self.depth = depth
		self.foundation = None
		self.floors = []
		self.overlaps = []
		self.altitude = 0
	
	def add_foundation(self, height, shift):
		self.foundation = House.Foundation(height, shift)
		self.altitude += height
	
	def add_floor(self, height, thickness):
		floor = House.Floor(height, thickness, self.altitude, self.width, self.depth)
		self.floors.append(floor)
		self.altitude += height
		return floor
		
	def add_overlap(self, height, shift):
		overlap = House.Overlap(height, shift, self.altitude)
		self.overlaps.append(overlap)
		self.altitude += height
		return overlap

		
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
		
def bpy_obj_plus_obj(object, addition):
	obs = [object, addition]
	ctx = bpy.context.copy()
	ctx['active_object'] = obs[0]
	ctx['selected_objects'] = obs
	ctx['selected_editable_bases'] = [bpy.context.scene.object_bases[ob.name] for ob in obs]
	bpy.ops.object.join(ctx)
	
	
class BlenderHouse:
	def __init__(self, house):
		self.house = house
	
	def render(self):
		self.render_bounds()
		self.render_foundation()
		self.render_floors()
		self.render_overlaps()
	
	def render_bounds(self):
		bpy_add_cube(size=(house.width, house.depth, B_E), location=(0,0,B_E/2), name='bounds')
	
	def render_foundation(self):
		if not house.foundation:
			return
		
		bpy_add_cube(
			size=(house.width - 2*house.foundation.shift, house.depth - 2*house.foundation.shift, house.foundation.height), 
			location=(0,0,house.foundation.height/2), 
			name='foundation'
			)
	
	def render_floors(self):
		n = 0
		for floor in house.floors:
			n += 1
			f = bpy_add_cube(
				size=(1, 1, 1),
				location=(0,0, floor.altitude+floor.height/2),
				name='floor%i' % n
				)
			e = bpy_add_cube(size=(1+B_E, 1+B_E, 1+B_E), location=(0,0, floor.altitude+floor.height/2))
			bpy_obj_minus_obj(f, e)
			
			for name,wall in floor.walls.items():
				w = bpy_add_cube(
					size=wall.size,
					location=(wall.location[0], wall.location[1], floor.altitude + wall.size[2]/2)
					)
					
				for hole in wall.holes:
					h = bpy_add_cube(
						size=(hole.size[0]+B_E, hole.size[1]+B_E, hole.size[2]+B_E),
						location=(w.location[0]+hole.location[0], w.location[1]+hole.location[1], w.location[2]+hole.location[2])
						)
					bpy_obj_minus_obj(w, h)
				
				bpy_obj_plus_obj(f, w)	
	
	def render_overlaps(self):
		n = 0
		for overlap in house.overlaps:
			n += 1
			bpy_add_cube(
				size=(house.width - 2*overlap.shift, house.depth - 2*overlap.shift, overlap.height),
				location=(0,0,overlap.altitude+overlap.height/2),
				name='overlap%i' % n
			)


# house configuration
house = House(width=10.5+0.6, depth=12.5+0.6)
house.add_foundation(height=0.2, shift=0.1)
f1 = house.add_floor(height=3, thickness=0.6)
house.add_overlap(height=0.2, shift=0.1)
f2 = house.add_floor(height=3, thickness=0.6)

IWT = 0.3

f1.add_d2_wall("front", "back", 0, IWT, "f1d0")
f1.add_w2_wall("left", "f1d0", 0.33, IWT, "f1w1")
f1.add_w2_wall("f1d0", "right", 0.33, IWT, "f1w2")
f1.add_d2_wall("front", "f1w1", -0.5, IWT, "f1d3")
f1.add_w2_wall("f1d0", "right", -0.33, IWT, "f1w4")
f1.add_w2_wall("left", "f1d3", -0.33, IWT, "f1w5")

IWT = 0.3

f2.add_w2_wall("left", "right", 0.33, IWT, "f2w0")
f2.add_d2_wall("f2w0", "back", 0, IWT, "f2d1")
f2.add_d_wall((-0.68, 0.3), -0.5, IWT, "f2d2")

f2.add_w2_wall("left", "f2d2", 0.1, IWT, "f2w3")
f2.add_w2_wall("left", "f2d2", -0.33, IWT, "f2w4")
f2.add_w2_wall("left", "f2d2", -0.66, IWT, "f2w5")

f2.add_d_wall((-1,-0.33), 0, IWT, "f2d6")
f2.add_w_wall((0,1), -0.33, IWT, "f2w7")

# render ground
bpy_add_cube(name='ground', size=(30,50,B_E), location=(0,0,-B_E/2))

# render house
hb = BlenderHouse(house)
hb.render()

