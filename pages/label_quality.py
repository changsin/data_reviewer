from collections import namedtuple

import shapely
import streamlit as st

import utils
from adq_labels import AdqLabels
from charts import *
from dart_labels import DartLabels

Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')


def chart_label_quality(selected_project):
    class_labels, overlap_areas, dimensions = load_label_files("Label quality", selected_project.label_files)

    chart_class_count = plot_chart("Class Count", "class", "count", class_labels)
    if chart_class_count:
        display_chart(selected_project.id, "class_count", chart_class_count)

    chart_overlap_areas = plot_chart("Overlap Areas",
                                     x_label="overlap %", y_label="count",
                                     data_dict=overlap_areas)
    if chart_overlap_areas:
        display_chart(selected_project.id, "overlap_areas", chart_overlap_areas)

    # create DataFrame from dictionary
    df_dimensions = pd.DataFrame.from_dict(dimensions, orient='index', columns=['width', 'height'])

    # apply function to split pairs into dictionary
    dimension_dict = dict(zip(df_dimensions['width'], df_dimensions['height']))

    # widths, heights = zip(*df_dimensions.apply(lambda x: tuple(x)))
    # df_dimensions = pd.concat([pd.Series(widths), pd.Series(heights)], axis=1)
    chart_dimensions = plot_chart("Dimensions",
                                  x_label="width", y_label="height",
                                  data_dict=dimension_dict, chart_type="circle")
    if chart_dimensions:
        display_chart(selected_project.id, "dimensions", chart_dimensions)


def load_label_files(title: str, files_dict: dict):
    st.markdown(title)

    if files_dict is None or len(files_dict.items()) == 0:
        return

    class_labels = dict()
    label_objects = []

    for folder, files in files_dict.items():
        for file in files:
            json_labels = utils.from_file("{}",
                                          folder,
                                          file)
            adq_labels = AdqLabels.from_json(json_labels)
            # convert to dart label format for easier processing
            dart_labels = DartLabels.from_adq_labels(adq_labels)
            label_objects.append(dart_labels)

    for labels in label_objects:
        for image in labels.images:
            for object in image.objects:
                if class_labels.get(object.label):
                    class_labels[object.label] += 1
                else:
                    class_labels[object.label] = 1

    overlap_areas = dict()
    dimensions = dict()
    for labels in label_objects:
        for image in labels.images:
            count = len(image.objects)
            for ob_id1 in range(count):
                xtl1, ytl1, xbr1, ybr1 = image.objects[ob_id1].points
                rect1 = Rectangle(xtl1, ytl1, xbr1, ybr1)
                width1 = rect1.xmax - rect1.xmin
                height1 = rect1.ymax - rect1.ymin
                dimensions[image.name] = (width1, height1)

                for ob_id2 in range(ob_id1 + 1, count):
                    xtl2, ytl2, xbr2, ybr2 = image.objects[ob_id2].points
                    rect2 = Rectangle(xtl2, ytl2, xbr2, ybr2)

                    overlap_area, max_area = calculate_overlapping_rect(rect1, rect2)

                    # overlap_percent = 0
                    if overlap_area > 0:
                        overlap_percent = format(overlap_area/max_area, '.2f')
                        overlap_percent = float(overlap_percent) * 100
                        if overlap_areas.get(overlap_percent):
                            overlap_areas[overlap_percent] += 1
                        else:
                            overlap_areas[overlap_percent] = 1

    return class_labels, overlap_areas, dimensions


def triangle_area(vertices):
    # Calculates the area of a triangle given its vertices using the cross product formula
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    x3, y3 = vertices[2]
    return abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)) / 2


def polygon_area(vertices):
    # Calculates the area of a polygon given its vertices using the shoelace formula
    x = [vertex[0] for vertex in vertices]
    y = [vertex[1] for vertex in vertices]
    return 0.5 * abs(sum(x[i]*y[i+1] - x[i+1]*y[i] for i in range(-1,len(x)-1)))


def overlapping_area(poly1, poly2):
    # Calculates the overlapping area of two polygons
    intersect = poly1.intersection(poly2)
    if intersect.is_empty:
        return 0
    triangles = []
    for poly in [poly1, poly2]:
        points = list(poly.exterior.coords)
        for i in range(poly.interiors.__len__()):
            points += list(poly.interiors[i].coords)
        for j in range(-1, len(points)-2):
            triangles.append((points[0], points[j+1], points[j+2]))
    contained_triangles = []
    for triangle in triangles:
        in_poly1 = poly1.contains(shapely.geometry.Point(triangle[0])) and poly1.contains(shapely.geometry.Point(triangle[1])) and poly1.contains(shapely.geometry.Point(triangle[2]))
        in_poly2 = poly2.contains(shapely.geometry.Point(triangle[0])) and poly2.contains(shapely.geometry.Point(triangle[1])) and poly2.contains(shapely.geometry.Point(triangle[2]))
        if in_poly1 and not in_poly2:
            contained_triangles.append(triangle)
        elif in_poly2 and not in_poly1:
            contained_triangles.append(triangle)
    overlapping_area = sum(triangle_area(triangle) for triangle in triangles) - sum(triangle_area(triangle) for triangle in contained_triangles)
    return overlapping_area


def calculate_overlapping_rect(a, b):
    overlapping_area = 0.0
    max_area = 0.0

    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    if (dx >= 0) and (dy >= 0):
        area1 = (a.xmax - a.xmin) * (a.ymax - a.ymin)
        area2 = (b.xmax - b.xmin) * (b.ymax - b.ymin)

        max_area = max(area1, area2)
        overlapping_area = dx*dy

    return overlapping_area, max_area