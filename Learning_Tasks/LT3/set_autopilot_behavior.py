import glob
import os
import sys
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

import random
import time
import numpy as np
import math


actor_list = []

def destroy():
    for actor in actor_list:
        actor.destroy()


try:
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(20.0)

    world = client.get_world()

    # 1. Spawn two example vehicles
    # Get the blueprint library
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints

    # Get all the spawn points
    spawn_points = world.get_map().get_spawn_points()

    # Spawn the vehicles
    vehicle_1_bp = blueprint_library.filter('model3')[0]
    spawn_point_1 = spawn_points[0]
    vehicle_1 = world.spawn_actor(vehicle_1_bp, spawn_point_1)
    vehicle_1.set_autopilot(True)
    actor_list.append(vehicle_1)

    vehicle_2_bp = blueprint_library.filter('cybertruck')[0]
    # spawn_point_2 = spawn_points[1]
    spawn_point_2 = carla.Transform(spawn_point_1.location-carla.Location(x=6), spawn_point_1.rotation)
    vehicle_2 = world.spawn_actor(vehicle_2_bp, spawn_point_2)
    vehicle_2.set_autopilot(True)
    actor_list.append(vehicle_2)

    
    # 2. Set autopilot behavior.
    # Get the traffic manager.  https://carla.readthedocs.io/en/latest/python_api/#carla.TrafficManager.
    tm = client.get_trafficmanager(8000)

    # Set the autopilot behavior. https://carla.readthedocs.io/en/latest/adv_traffic_manager/#configuring-autopilot-behavior.
    # Set vehicle_1 as a general automated vehicle, which keeps at least 2 meters from other vehicles, and drives 20% faster than the current speed limit.
    current_veh = vehicle_1
    tm.distance_to_leading_vehicle(current_veh,2)
    tm.vehicle_percentage_speed_difference(current_veh,-20)

    # Set vehicle_2 as a dangerous vehicle, which ignores all traffic lights, keeps no safety distance from other vehicles, and drive 40% faster than the current speed limit.
    danger_car = vehicle_2
    tm.ignore_lights_percentage(danger_car,100)
    tm.distance_to_leading_vehicle(danger_car,0)
    tm.vehicle_percentage_speed_difference(danger_car,-40)


    # 3. Set the spectator.
    # Get the spectator. https://carla.readthedocs.io/en/latest/tuto_G_getting_started/#the-spectator
    spectator = world.get_spectator()

    # Use the while loop to update the location and rotation of the spectator.
    while True:
        transform = vehicle_2.get_transform()

        # Select one transform and uncomment the other one.
        # spectator transform 1: bird's-eye view
        spectator_location = transform.location + carla.Location(z=20)
        spectator_rotation = carla.Rotation(pitch=-90)

        # spectator transform 2: first-person view
        # spectator_location = transform.location + carla.Location(z=2)
        # spectator_rotation = carla.Rotation(pitch=0, yaw=transform.rotation.yaw)

        # Update the transform
        spectator.set_transform(carla.Transform(spectator_location, spectator_rotation))
        time.sleep(0.02)

finally:
    print('destroying actors')
    destroy()
    print('done.')