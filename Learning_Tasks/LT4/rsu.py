from dis import dis
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

NPC_VEH_NUM = 40
actor_list = []
vehicle_list = []

def destroy():
    for actor in actor_list:
        actor.destroy()
    for cone in cone_list:
        cone.destroy()
# def destroy_init():
#     existed_actors = world.get_actors()
#     for actor in existed_actors:
#         actor.destroy()

try:
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(2.0)
    world = client.get_world()
    # destroy_init()

    # 1. Initialize the blueprint library and the spawn points
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints
    spawn_points = world.get_map().get_spawn_points()

    # 2. Spawn the vehicles
    # Generate NPC vehicles
    for i in range(NPC_VEH_NUM):
        # Choose random blueprint and choose the i-th default spawn points
        vehicle_bp_i = random.choice(blueprint_library.filter('vehicle.*.*'))
        spawn_point_i = spawn_points[i]

        # Spawn the actor
        vehicle_i = world.try_spawn_actor(vehicle_bp_i, spawn_point_i)

        # Append to the actor_list
        if vehicle_i != None:
            actor_list.append(vehicle_i)
            vehicle_list.append(vehicle_i)
    print('%d vehicles are generated' % len(actor_list))

    # Set autopilot for each vehicle
    for vehicle_i in actor_list:
        vehicle_i.set_autopilot(True)

    # 3. Spawn the RSU
    rsu_bp_1 = blueprint_library.find('static.prop.streetsign04')
    spawn_point_rsu1 = carla.Transform(carla.Location(x=-57, y=61.22, z=6.5), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
    rsu1 = world.spawn_actor(rsu_bp_1, spawn_point_rsu1)
    actor_list.append(rsu1)


    # 4. Set the view of spectator to the RSU
    spectator = world.get_spectator()
    rsu_transform = rsu1.get_transform()
    spectator.set_transform(carla.Transform(rsu_transform.location, carla.Rotation(pitch=-35)))


    # 5. Set construction cones
    cone_list = []
    cone_bp = blueprint_library.find('static.prop.trafficcone01')
    spawn_point_cone1 = carla.Transform(carla.Location(x=-53, y=58, z=0))
    spawn_point_cone2 = carla.Transform(carla.Location(x=-51, y=58, z=0))
    spawn_point_cone3 = carla.Transform(carla.Location(x=-51, y=61, z=0))
    spawn_point_cone4 = carla.Transform(carla.Location(x=-51, y=64, z=0))
    spawn_point_cone5 = carla.Transform(carla.Location(x=-53, y=64, z=0))
    cone_1 = world.spawn_actor(cone_bp, spawn_point_cone1)
    cone_2 = world.spawn_actor(cone_bp, spawn_point_cone2)
    cone_3 = world.spawn_actor(cone_bp, spawn_point_cone3)
    cone_4 = world.spawn_actor(cone_bp, spawn_point_cone4)
    cone_5 = world.spawn_actor(cone_bp, spawn_point_cone5)
    cone_list.append(cone_1)
    cone_list.append(cone_2)
    cone_list.append(cone_3)
    cone_list.append(cone_4)
    cone_list.append(cone_5)



    # 6. Check the distance between the vehicles and the construction zone
    while True:
        world_snapshot = world.get_snapshot()
        timestamp = world_snapshot.timestamp.elapsed_seconds # Get the time reference

        # Set the detection range 
        detection_range = 10

        # Calculate the distance between each vehicle and each cone
        for i in range(len(vehicle_list)):
            vehicle = vehicle_list[i]
            v_x = vehicle.get_location().x
            v_y = vehicle.get_location().y
            
            for j in range(len(cone_list)):
                cone = cone_list[j]
                c_x = cone.get_location().x
                c_y = cone.get_location().y

                # Calculate the Euclidean distance
                dist = np.sqrt(np.square(v_x-c_x) + np.square(v_y-c_y))

                # If the vehicle is in the range, assume RSU could send this message to the vehicle.
                if dist < detection_range:
                    print("Timestamp:{%.3f s}. Vehicle %d is close to the construction zone. Slow down." % (timestamp, i+1))
                    break

        time.sleep(0.2)


except KeyboardInterrupt:
    print('destroying actors')
    destroy()

finally:
    print('done.')