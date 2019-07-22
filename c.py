import bpy

class Wall:
	def __init__(self, fv, fh, tv, th, name):
		self.fv = fv
		self.fh = fh
		self.tv = tv
		self.th = th
		self.name = name
		
		print(self.size, self.location)
	
	@property
	def size(self):
		return (self.th - self.fh, self.tv - self.fv, 1)
		
	@property
	def location(self):
		return (self.th/2 + self.fh/2, self.tv/2 + self.fv/2, 0)

class House:
	def __init__(self, plan):
		self.plan = plan
		self.walls = []
		
	def add_wall(self, f, t):
		fv,fh = f.split(':')
		tv,th = t.split(':')
		w = Wall(self.plan.v[fv], self.plan.h[fh], self.plan.v[tv], self.plan.h[th], '%s_%s' % (f, t))
		self.walls.append(w)

class Plan:
	def __init__(self):
		pass
		
	v = {}
	h = {}
	
# -----------------------------------------------------

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
	
	bpy.context.view_layer.objects.active = object
	bpy.ops.object.modifier_apply(modifier = mod_bool.name)
	
	if delete_deleter:
		bpy.context.view_layer.objects.active = deleter
		bpy.ops.object.delete()

		
def bpy_obj_plus_obj(object, addition):
	obs = [object, addition]
	c = {}
	c['object'] = c['active_object'] = obs[0]
	c['selected_objects'] = c['selected_editable_objects'] = obs
	bpy.ops.object.join(c)


class BlenderHouse:
	def __init__(self, house):
		self.house = house
		
	def render(self):
		for wall in self.house.walls:
			bpy_add_cube(wall.size, wall.location, wall.name)
	
# -----------------------------------------------------		
		
p = Plan()

p.v['A'] = 0
p.v['B'] = p.v['A']+1.590
p.v['C'] = p.v['B']+1.500
p.v['D'] = p.v['C']+2.800
p.v['E'] = p.v['D']+2.100
p.v['F'] = p.v['E']+1.400
p.v['G'] = p.v['F']+3.600

p.h['1'] = 0
p.h['2'] = p.h['1']+3.050
p.h['3'] = p.h['2']+3.290
p.h['4'] = p.h['3']+1.520
p.h['5'] = p.h['4']+2.450
p.h['6'] = p.h['5']+2.360
		
		
h = House(p)

h.add_wall('B:2', 'B:6')
h.add_wall('B:6', 'G:6')
h.add_wall('G:6', 'G:2')
h.add_wall('G:2', 'B:2')

bh = BlenderHouse(h)
bh.render()