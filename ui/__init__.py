"""
Created on Apr 18, 2021

@author: gosha
"""

from math import ceil, pi

ticks_per_step = 20


def tk_color(color):
    return "#{:02X}{:02X}{:02X}".format(*map(lambda v: ceil(v * 255), color))


def charge_color(charge, initial_charge):
    parts_charged = charge / initial_charge
    if parts_charged > 0.5:
        return 2 - parts_charged * 2, 1, 0
    else:
        return 1, parts_charged * 2, 0


def border_charge_color(charge, initial_charge):
    return tuple(map(lambda x: x / 2, charge_color(charge, initial_charge)))


def inactive_charge_color(*_):
    return 0.5, 0.5, 0.5


def inactive_border_charge_color(*_):
    return 0.75, 0.75, 0.75


def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth=True)


def robot_move_curve(time_fraction):
    return time_fraction


def apply_robot_move_curve(time_fraction, x0, x1, y0, y1):
    motion_point1 = robot_move_curve(time_fraction)
    motion_point0 = 1 - motion_point1
    return x0 * motion_point0 + x1 * motion_point1, y0 * motion_point0 + y1 * motion_point1


def robot_turn_curve(time_fraction):
    return time_fraction


def apply_robot_turn_curve(time_fraction, angle0, angle1):
    if angle1 - angle0 > pi / 2:
        angle1 -= pi * 2

    motion_point1 = robot_move_curve(time_fraction)
    motion_point0 = 1 - motion_point1
    return angle0 * motion_point0 + angle1 * motion_point1


def robot_appearance_curve(time_fraction):
    return time_fraction * time_fraction


def apply_appearance_curve(time_fraction):
    return robot_appearance_curve(time_fraction)


def apply_disappearance_curve(time_fraction):
    return robot_appearance_curve(1 - time_fraction)
