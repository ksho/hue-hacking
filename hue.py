import requests
import json
import random
import time
import math

import processimage
from sympy import Point, Line, Polygon

ip = '10.0.1.2'
path = '/api/newdeveloper/'
lights = {
    '1': 'lights/1/',
    '2': 'lights/2/',
    '3': 'lights/3/'
}

BRIGHTNESS = 200

pr = Point(0.675, 0.322, evaluate=False)
pg = Point(0.409, 0.518, evaluate=False)
pb = Point(0.167, 0.0625, evaluate=False)

gamut_tri = Polygon(pr, pg, pb)

## lines
# l1 = Line(pb, pg) ## top-left
# l2 = Line(pg, pr) ## top-right
# l3 = Line(pr, pb) ## bottom

## location polys
# bottom_poly = Polygon(pr, pb, Point(0.175, 0.0, evaluate=False), Point(0.73, 0.26, evaluate=False))
# top_right_poly = Polygon(pr, pg, Point(0.4, 0.59, evaluate=False))
# top_left_poly = Polygon(pg, pb, Point(0.15, 0.02, evaluate=False), Point(0.08, 0.15, evaluate=False), Point(0.01, 0.5, evaluate=False), Point(0.01, 0.7, evaluate=False), Point(0.06, 0.83, evaluate=False), Point(0.3, 0.68, evaluate=False))

grid = [
    ['blue', 'blue', 'purple', 'light_purple', 'magenta', 'magenta', 'red', 'red', 'red'],
    ['blue', 'blue', 'blue', 'purple', 'magenta', 'magenta', 'red', 'red', 'red'],
    ['blue', 'blue', 'light_blue', 'pink', 'pink', 'magenta', 'red', 'red', 'red'],
    ['blue', 'blue', 'light_blue', 'light_blue', 'white', 'light_orange', 'orange_red', 'red', 'red'],
    ['blue', 'light_blue', 'light_blue', 'yellow', 'yellow', 'yellow', 'orange_yellow', 'orange_yellow', 'red'],
    ['light_blue', 'light_blue', 'light_blue', 'green', 'green', 'green ', 'yellow', 'yellow', 'orange'],
    ['light_blue', 'light_blue', 'green', 'green', 'green', 'green ', 'yellow', 'yellow', 'orange'],
    ['green', 'green', 'green', 'green', 'green', 'green ', 'yellow', 'yellow', 'orange'],
]

color_map = {
    'red': [0.674, 0.322],
    'orange_red': [0.6408, 0.3463],
    'orange': [0.5932, 0.3812],
    'orange_yellow': [0.5043, 0.4464],
    'light_orange': [0.5248, 0.4018],
    'yellow': [0.4635, 0.4759],
    'green': [0.4077, 0.5154],
    'blue': [0.168, 0.041],
    'light_blue': [0.2187, 0.1415],
    'purple': [0.2259, 0.0731],
    'light_purple': [0.2882, 0.155],
    'pink': [0.4081, 0.2517],
    'magenta': [0.3742, 0.1555],
}   

## color polys
# blue_poly = Polygon(pb, Point(0.15, 0.02, evaluate=False), Point(0.08, 0.15, evaluate=False), Point(0.01, 0.5, evaluate=False), Point(0.01, 0.7, evaluate=False), Point(0.4, 0.3, evaluate=False))


def random_lights():
    while(1):
        hues = {
            '1': random.randint(1,65000),
            '2': random.randint(1,65000),
            '3': random.randint(1,65000)
        }
        print 'alala'
        for k in hues:
            url = 'http://' + ip + path + lights[k] + 'state'
            print url
            data = json.dumps({
                "sat": 255,
                "bri": BRIGHTNESS,
                "hue": hues[k]
            })
            print data
            r = requests.put(url, data)
            print 'foo'
        time.sleep(1)

def set_all_lights_one_color(data):
    for l in lights:
        url = 'http://' + ip + path + lights[l] + 'state'
        r = requests.put(url, data)


def get_xy_from_rgb(rgb):
    """
    Convert rgb color to CIE colorspace.
    """
    print "...GET_XY " + str(rgb) 
    c = [ v / float(255) for v in rgb ]
    print c[0], c[1], c[2]

    red = c[0]
    red = math.pow((red + 0.055) / (1.0 + 0.055), 2.4) if (red > 0.04045) else (red / 12.92)

    green = c[1]
    green = math.pow((green + 0.055) / (1.0 + 0.055), 2.4) if (green > 0.04045) else (green / 12.92)

    blue = c[2]
    blue = math.pow((blue + 0.055) / (1.0 + 0.055), 2.4) if (blue > 0.04045) else (blue / 12.92)
    # print red, green, blue


    X = red * 0.649926 + green * 0.103455 + blue * 0.197109 
    Y = red * 0.234327 + green * 0.743075 + blue * 0.022598
    Z = red * 0.0000000 + green * 0.053077 + blue * 1.035763
    # print X,Y,Z

    x = round(X / (X + Y + Z), 3)
    y = round(Y / (X + Y + Z), 3)
    # print x, y

    p = Point(x, y, evaluate=False)
    
    if gamut_tri.encloses_point(p):
        return x, y
    else:
        x, y = get_closest_color(x, y)
        print "GOT EM! " + str(x) + " " + str(y)
        print " "
        return x, y


# RED (0.675, 0.322)
# GREEN (0.409, 0.518)
# BLUE (0.167, 0.0625))
def get_closest_color(x, y):
    print "...GET_CLOSEST_COLOR " + str(x) + " " + str(y) 

    y_slot = int(str(x)[2:3])
    x_slot = int(str(y)[2:3])
    print x_slot, y_slot

    color_str = grid[x_slot][y_slot]

    return color_map[color_str][0], color_map[color_str][1]

    # point = Point(x, y, evaluate=False)
    # print "    " + str(point)

    # new_point = try_color_polys(point)
    # if new_point:
    #     return new_point.x, new_point.y

    # line = get_relative_line(point)
    
    # s1 = line.perpendicular_segment(point)
    # new_point = s1.points[1].evalf()
    # print "new_point: " + str(new_point.x) + " " + str(new_point.y)
    # if new_point.x == point.x:
    #     new_point = s1.points[0].evalf()
    # return new_point.x, new_point.y


def set_lights_different_colors(colors):
    l = 1
    print len(colors)
    for c in colors:
        data = json.dumps({
            # "sat": 255,
            "bri": BRIGHTNESS,
            "xy": [float(c[0]), float(c[1])]
            # 'hue': 25500
        })
        print data
        url = 'http://' + ip + path + lights[str(l)] + 'state'
        print url
        r = requests.put(url, data)
        l = l + 1
        time.sleep(1)


def get_relative_line(point):
    """
    Get side of triangle we're moving the outside point to.
    """
    print "...FIND_LINE"

    if bottom_poly.encloses_point(point):
        return l3
    elif top_right_poly.encloses_point(point):
        return l2
    else:
        return l1


def try_color_polys(point):
    

    if blue_poly.encloses_point(point):
        return Point(0.2, 0.1)
    else:
        return False





def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))


def do_rgb(rgbs):
    all_colors = []
    for r in rgbs:
        print 'LOOP'
        x, y = get_xy_from_rgb(r)
        all_colors.append((x,y))

    # print all_colors
    set_lights_different_colors(all_colors)

    # set_all_lights_one_color(data)


def do_screenshot():
    hexes = processimage.colorz('/Users/karlshouler/Desktop/vamp2.png', 3)
    print hexes
    rgbs = []
    for h in hexes:
        rgbs.append(hex_to_rgb(h))
        # rgbs.append(hex_to_rgb(h))
        # rgbs.append(hex_to_rgb(h))
    do_rgb(rgbs)

# random_lights()
print "...START"
do_screenshot()
# do_rgb()

# p = Polygon((0, 0), (4, 4), (4, 0))
# print p.encloses_point(Point(2, 0.5))




