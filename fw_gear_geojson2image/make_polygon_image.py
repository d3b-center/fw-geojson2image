# Takes the QuPath output GeoJSON file & create a labelled annotation image
#       set up to operate on 1 QuPath "Annotation" object containing N nuclei "detection" objects

from PIL import Image
from PIL import ImageDraw
import random
import geojson
from glob import glob
import math

def format_coordinates(poly_coords):
# PIL needs a list of tuples, QuPath exports list of lists
    clean_coords = []
    ind=0
    for coord in poly_coords:
        clean_coords.append(tuple(coord))
        ind+=1
    return clean_coords

def detect_edge_polygons(poly_coords, img_width, img_height):
# if two or more coordinates include x/y at the max boundaries
# of the image it's an edge case
    n_edge_values = 0
    edge_values = [0, 1, img_width, img_height]
    for coord in poly_coords:
        x = math.ceil(coord[0]) # round up
        y = math.ceil(coord[1]) # round up
        if (x in edge_values) or (y in edge_values):
            n_edge_values+=1
    if n_edge_values >= 2:
        return 1
    else:
        return 0

# ================================================================

def create_labeled_image(gj_file, output_path):
    
    with open(gj_file) as f:
        gj = geojson.load(f)

    img_dims = gj["features"][0]["geometry"]["coordinates"][0][2]
    print(f'               image dimensions: {img_dims}')

    img = Image.new('RGB', (img_dims[0], img_dims[0])) # create a black image

    img2 = img.copy()
    draw = ImageDraw.Draw(img2)

    used_colors = [(0,0,0), (255,255,255)]
    for json_obj in gj["features"]:
        if json_obj["properties"]["objectType"] == "detection": # if it's a QuPath detection
            # get the polygon coordinates
            these_coords = json_obj["geometry"]["coordinates"][0]
            # transform into the format needed for PIL
            formatted_coords = format_coordinates(these_coords)
            # remove edge nuclei
            is_edge_case = detect_edge_polygons(formatted_coords, img_dims[0], img_dims[0])
            if is_edge_case == 0:
                # make a unique RGB value for this polygon
                unique_color = 0
                while unique_color == 0:
                    color_code = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
                    if color_code not in used_colors:
                        used_colors.append(color_code)
                        unique_color = 1
                # draw the polygon
                draw.polygon(formatted_coords, fill = color_code)

    img3 = Image.blend(img, img2, 1)
    # img3 = Image.blend(img, img2, 0.5) # transparent overlay

    img3.save(f'{output_path}')
