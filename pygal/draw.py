from matplotlib import pyplot as plt
from matplotlib import cm
import matplotlib.patches as patches
from matplotlib.path import Path

import pygal

from multipledispatch import dispatch

import numpy as np
import math  


def draw_point(point, fig=None, ax=None, **kwargs):
	plt.scatter([float(point.x())], [float(point.y())], **kwargs)

def draw_list(point_list, fig=None, ax=None, **kwargs):
	for point in point_list:
		draw_point(point, **kwargs)

def draw_vector(vector, start=-5, stop=5, units='xy', angles='xy', scale_units='xy', scale=1, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	vector_x = float(vector.x())
	vector_y = float(vector.y())

	q = ax.quiver(np.array(0), np.array(0), np.array(vector_x), np.array(vector_y), units=units, angles=angles, scale_units=scale_units, scale=scale,**kwargs)
	ax.set_aspect('equal')
	
	plt.xlim(start,stop)
	plt.ylim(start,stop)

def draw_ray(ray, stop=0, num=100, color = '#1f77b4', units='xy', angles='xy', scale_units='xy', scale=1, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()
	
	def set_xmargin(ax, left=0.0, right=0.0):
	    ax.set_xmargin(0)
	    ax.autoscale_view()
	    lim = ax.get_xlim()
	    delta = np.diff(lim)
	    left = lim[0] - delta*left
	    right = lim[1] + delta*right
	    ax.set_xlim(left,right)

	source_x = float(ray.source().x())
	source_y = float(ray.source().y())
	direction_x = float(ray.direction().dx()) + source_x
	direction_y = float(ray.direction().dy()) + source_y

	if (source_x > direction_x):
		is_superior = True
		if (stop >= source_x or stop == 0):
			stop = source_x - 5
			x = np.linspace(stop,source_x,num)
		else:
			x = np.linspace(stop, source_x, num)
	else:
		is_superior = False
		if(stop <= source_x or stop == 0):
			stop = source_x + 5
			x = np.linspace(source_x,stop,num)
		else:
			x = np.linspace(source_x, stop, num)

	line = ray.supporting_line()
	y = (-line.a()*x-line.c())/line.b()

	ax.plot(x, y, color=color, **kwargs)
	draw_point(ray.source(), color=color)
	
	if(is_superior):
		set_xmargin(ax, left=0, right=0.05)
	else:
		set_xmargin(ax, left=0.05, right=0)

def draw_direction(direction, start=-2, stop=2, units='xy', angles='xy', scale_units='xy', scale=1, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	direction_x = float(direction.dx())
	direction_y = float(direction.dy())

	normalized_x = direction_x/math.sqrt(direction_x**2 + direction_y**2)
	normalized_y= direction_y/math.sqrt(direction_x**2 + direction_y**2)	

	q = ax.quiver(np.array(0), np.array(0), np.array(normalized_x), np.array(normalized_y),units=units, angles=angles, scale_units=scale_units, scale=scale, **kwargs)
	ax.set_aspect('equal')
	
	plt.xlim(start,stop)
	plt.ylim(start,stop)

def draw_bbox(bbox, display_range = 5, fill = False, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	x_min = float(bbox.xmin())
	x_max = float(bbox.xmax())
	y_min = float(bbox.ymin())
	y_max = float(bbox.ymax())

	plt.gca().add_patch(patches.Rectangle(
		(x_min, y_min), x_max - x_min, y_max - y_min, fill=fill, **kwargs))

	plt.xlim(x_min - display_range, x_max + display_range)
	plt.ylim(y_min - display_range, x_max + display_range)

def draw_line(line, start=-5, stop=5, num=100, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	x = np.linspace(start,stop,num)
	y = (-line.a()*x-line.c())/line.b()

	ax.plot(x, y, **kwargs)
	ax.margins(0)

def draw_iso_rectangle(rectangle, display_range = 5, fill = False, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	x_min = float(rectangle.xmin())
	x_max = float(rectangle.xmax())
	y_min = float(rectangle.ymin())
	y_max = float(rectangle.ymax())

	plt.gca().add_patch(patches.Rectangle(
		(x_min, y_min), x_max - x_min, y_max - y_min, fill=fill, **kwargs))

	plt.xlim(x_min - display_range, x_max + display_range)
	plt.ylim(y_min - display_range, y_max + display_range)

def draw_segment(segment, color = '#1f77b4', fig= None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	plt.plot([segment.source().x(), segment.target().x()], [segment.source().y(), segment.target().y()], color = color, **kwargs)
	draw_list([segment.source(), segment.target()], color=color, **kwargs)

def draw_circle(circle, display_range = 5, fill = False, fig=None, ax=None, **kwargs):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	center_x = float(circle.center().x())
	center_y = float(circle.center().y())
	radius = math.sqrt(float(circle.squared_radius()))

	circle_displayed = plt.Circle((center_x, center_y), radius, fill=fill, **kwargs)

	ax.add_artist(circle_displayed)
	ax.set_aspect('equal')
	
	plt.xlim(center_x - radius - display_range, center_x + radius + display_range)
	plt.ylim(center_y - radius - display_range, center_y + radius + display_range)

def to_list_of_tuples(iterable):
	return [(float(p.x()), float(p.y())) for p in iterable]

def draw_polygon(poly=None,poly_with_holes=None, vertices=None, plt=plt, facecolor='none', point_color='none', line_width = 2, plot_vertices=True, fig=None, ax=None):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	vertices = to_list_of_tuples(poly.vertices) + [(0, 0)]
	poly_length = 0
	
	for v in poly.vertices:
		poly_length += 1
		if plot_vertices:
			draw_point(v, color=point_color)

	codes = [Path.MOVETO] + [Path.LINETO] * (poly_length - 1) + [Path.CLOSEPOLY]
	path = Path(vertices, codes)
	plt.gca().add_patch(patches.PathPatch(path, facecolor=facecolor, lw=line_width))
	
	if poly_with_holes:
		for hole in poly_with_holes.holes:
			hole_length = 0
			vertices = to_list_of_tuples(hole.vertices) + [(0, 0)]
			for v in hole.vertices:
				hole_length += 1
				if plot_vertices:
					draw_point(v, color=point_color)
			
			codes = [Path.MOVETO] + [Path.LINETO] * (hole_length - 1) + [Path.CLOSEPOLY]
			path = Path(vertices, codes)
			plt.gca().add_patch(patches.PathPatch(path, facecolor='white', lw=line_width))

	plt.gca().relim()
	plt.gca().autoscale_view()

def draw_voronoi(voronoi,display_range = 3, edges_color='blue', sites_color='red', vertices_color ='None', finite_edges_color='blue', fig=None, ax=None):
	if fig == None and ax == None:
		fig, ax = plt.gcf(), plt.gca()

	for edge in voronoi.edges:
		source, target = edge.source(), edge.target()
		if source and target:
			plt.plot([source.point().x(), target.point().x()], [source.point().y(), target.point().y()], color = edges_color)

	bbox = pygal.Bbox2()
	for site in voronoi.sites:
		bbox += site.bbox()
		draw_point(site, color=sites_color, fig=fig, ax=ax)

	for vertice in voronoi.vertices:
		draw_point(vertice.point(), color=vertices_color)

	for el in voronoi.finite_edges:
		draw(el, color=finite_edges_color, fig=fig, ax=ax)

	plt.xlim(bbox.xmin() - display_range, bbox.xmax() + display_range)
	plt.ylim(bbox.ymin() - display_range, bbox.ymax() + display_range)

@dispatch(pygal._pygal.Point2)
def draw(object, **kwargs):
	draw_point(object, **kwargs)

@dispatch(list)
def draw(object, **kwargs):
	for el in object:
		draw(el, **kwargs)

@dispatch(pygal._pygal.Vector2)
def draw(object, **kwargs):
	draw_vector(object, **kwargs)

@dispatch(pygal._pygal.Ray2)
def draw(object, **kwargs):
	draw_ray(object, **kwargs)

@dispatch(pygal._pygal.Direction2)
def draw(object, **kwargs):
	draw_direction(object, **kwargs)

@dispatch(pygal._pygal.Bbox2)
def draw(object, **kwargs):
	draw_bbox(object, **kwargs)

@dispatch(pygal._pygal.Line2)
def draw(object, **kwargs):
	draw_line(object, **kwargs)

@dispatch(pygal._pygal.IsoRectangle2)
def draw(object, **kwargs):
	draw_iso_rectangle(object, **kwargs)

@dispatch(pygal._pygal.Segment2)
def draw(object, **kwargs):
	draw_segment(object, **kwargs)

@dispatch(pygal._pygal.Circle2)
def draw(object, **kwargs):
	draw_circle(object, **kwargs)

@dispatch(pygal._pygal.Polygon)
def draw(object, **kwargs):
	draw_polygon(object, **kwargs)

@dispatch(pygal._pygal.PolygonWithHoles)
def draw(object, **kwargs):
	draw_polygon(object, **kwargs)

@dispatch(pygal._pygal.voronoi.VoronoiDiagram)
def draw(object, **kwargs):
	draw_voronoi(object, **kwargs)

