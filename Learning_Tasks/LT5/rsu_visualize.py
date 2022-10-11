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

# Toggles. 1=True, 0=False
SPAWN_NPC_VEHICLES = 1
SPAWM_CONSTRUCTION_CONES = 1
SPAWN_CONSTRUCTION_VEHICLES = 1
VISUALIZE_CONSTRUCTION_ZONE = 1
VISUALIZE_DETECTION_AREA = 1
VISUALIZE_COMMUNICATION= 1

NPC_VEH_NUM = 40
DETECTION_RANGE = 12

actor_list = []
vehicle_list = []
cone_list = []

def destroy():
    for actor in actor_list:
        actor.destroy()
    for cone in cone_list:
        cone.destroy()

try:
    # 0. Set the cilent and the world
    
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    # Reload the world to destroy all the existing actors. You do not need to restart Carla anymore.
    client.reload_world()
    client.set_timeout(2.0)
    world = client.get_world()

    # 1. Initialize the blueprint library and the spawn points
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints
    spawn_points = world.get_map().get_spawn_points()

    
    # 2. Spawn the RSU
    rsu_bp_1 = blueprint_library.find('static.prop.streetsign04')
    spawn_point_rsu1 = carla.Transform(carla.Location(x=-57, y=61.22, z=6.5), carla.Rotation(pitch=0, yaw=0, roll=0))
    rsu1 = world.spawn_actor(rsu_bp_1, spawn_point_rsu1)
    actor_list.append(rsu1)
    
    

    # 3. Set the view of spectator to the RSU
    spectator = world.get_spectator()
    rsu_transform = rsu1.get_transform()
    # View 1:
    # spectator.set_transform(carla.Transform(rsu_transform.location, carla.Rotation(pitch=-35)))
    # View 2:
    spectator.set_transform(carla.Transform(carla.Location(x=-57,y=61,z=20), carla.Rotation(pitch=-63)))
    # View 3:
    # spectator.set_transform(carla.Transform(carla.Location(x=-37,y=61,z=20), carla.Rotation(pitch=-60,yaw=180)))


    # 4. Set construction zones
    # Spawn construction cones
    if SPAWM_CONSTRUCTION_CONES == 1:
        cone_bp = blueprint_library.find('static.prop.trafficcone01')
        spawn_point_cone1 = carla.Transform(carla.Location(x=-55, y=58, z=0))
        spawn_point_cone2 = carla.Transform(carla.Location(x=-51, y=58, z=0))
        spawn_point_cone3 = carla.Transform(carla.Location(x=-51, y=61, z=0))
        spawn_point_cone4 = carla.Transform(carla.Location(x=-51, y=65, z=0))
        spawn_point_cone5 = carla.Transform(carla.Location(x=-55, y=65, z=0))
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

    # Spawn construction vehicles
    if SPAWN_CONSTRUCTION_VEHICLES == 1:
        veh_construction_bp = blueprint_library.find('vehicle.carlamotors.carlacola')
        spawn_point_veh_con = carla.Transform(carla.Location(x=-53, y=61.2, z=1), carla.Rotation(yaw=90))
        veh_construction = world.spawn_actor(veh_construction_bp, spawn_point_veh_con)
        actor_list.append(veh_construction)


    # 5. Spawn the vehicles
    # Generate NPC vehicles
    if SPAWN_NPC_VEHICLES == 1:
        for i in range(NPC_VEH_NUM):
            # Choose random blueprint and choose the i-th default spawn points
            vehicle_bp_i = random.choice(blueprint_library.filter('vehicle.*.*'))
            spawn_point_i = spawn_points[i]
            print(spawn_point_i.location, spawn_point_i.rotation)
            # Spawn the actor
            vehicle_i = world.try_spawn_actor(vehicle_bp_i, spawn_point_i)

            # Append to the actor_list
            if vehicle_i != None:
                actor_list.append(vehicle_i)
                vehicle_list.append(vehicle_i)
        print('%d vehicles are generated' % len(vehicle_list))

        # Set autopilot for each vehicle
        for vehicle_i in vehicle_list:
            vehicle_i.set_autopilot(True)
    
    # 6. Check the distance between the vehicles and the construction zonewe

    dt = 0.2
    max_iteration = 300
    max_time = max_iteration * dt
    iter = 0

    while True:
        if iter >= max_iteration:
            break
        world_snapshot = world.get_snapshot()
        timestamp = world_snapshot.timestamp.elapsed_seconds # Get the time reference
        
        if iter == 1:
            # Visulize static information:
            # Construction zone
            if VISUALIZE_CONSTRUCTION_ZONE == 1:
                h = carla.Location(x=0, y=0, z=1)
                # Add a text to the RSU
                world.debug.draw_string(location=rsu1.get_location(), text='RSU', draw_shadow=True, color=carla.Color(255, 0, 0), life_time=max_time)
                # Draw 5 boundaries
                world.debug.draw_line(begin=cone_1.get_location()+h, end=cone_2.get_location()+h, color=carla.Color(255, 0, 0), life_time=max_time)
                world.debug.draw_line(begin=cone_2.get_location()+h, end=cone_3.get_location()+h, color=carla.Color(255, 0, 0), life_time=max_time)
                world.debug.draw_line(begin=cone_3.get_location()+h, end=cone_4.get_location()+h, color=carla.Color(255, 0, 0), life_time=max_time)
                world.debug.draw_line(begin=cone_4.get_location()+h, end=cone_5.get_location()+h, color=carla.Color(255, 0, 0), life_time=max_time)
                world.debug.draw_line(begin=cone_5.get_location()+h, end=cone_1.get_location()+h, color=carla.Color(255, 0, 0), life_time=max_time)

            # Detection area
            if VISUALIZE_DETECTION_AREA:
                h_detect = 0.3
                corner_1 = carla.Location(x=rsu1.get_location().x, y=cone_1.get_location().y) + carla.Location(x=0, y=-DETECTION_RANGE, z=h_detect)
                corner_2 = cone_2.get_location() + carla.Location(x=DETECTION_RANGE, y=-DETECTION_RANGE, z=h_detect)
                corner_3 = cone_4.get_location() + carla.Location(x=DETECTION_RANGE, y=DETECTION_RANGE, z=h_detect)
                corner_4 = carla.Location(x=rsu1.get_location().x, y=cone_5.get_location().y) + carla.Location(x=0, y=DETECTION_RANGE, z=h_detect)
                # Draw 4 boundaries
                world.debug.draw_line(begin=corner_1, end=corner_2, thickness=0.03, color=carla.Color(255, 255, 0), life_time=max_time)
                world.debug.draw_line(begin=corner_2, end=corner_3, thickness=0.03, color=carla.Color(255, 255, 0), life_time=max_time)
                world.debug.draw_line(begin=corner_3, end=corner_4, thickness=0.03, color=carla.Color(255, 255, 0), life_time=max_time)
                world.debug.draw_line(begin=corner_4, end=corner_1, thickness=0.03, color=carla.Color(255, 255, 0), life_time=max_time)


        # Calculate the distance between each vehicle and each cone
        for i in range(len(vehicle_list)):
            vehicle = vehicle_list[i]
            v_x = vehicle.get_location().x
            v_y = vehicle.get_location().y
            
            for j in range(len(cone_list)):
                cone = cone_list[j]
                c_x = cone.get_location().x
                c_y = cone.get_location().y

                # Calculate the distance between each vehicle and each cone
                dist_x = np.abs(v_x - c_x)
                dist_y = np.abs(v_y - c_y)

                # If the vehicle is within the detection area, assume RSU could send this message to the vehicle.
                if dist_x < DETECTION_RANGE and dist_y < DETECTION_RANGE:
                    print("Timestamp:{%.3f s}. Vehicle %d is close to the construction zone. Slow down." % (timestamp, i+1))
                    # Visualize the communication process
                    if VISUALIZE_COMMUNICATION == 1:
                        world.debug.draw_line(begin=rsu1.get_location(), end=vehicle.get_location()+carla.Location(z=0.6), color=carla.Color(64, 255, 0), life_time=dt)
                    break
        iter += 1
        time.sleep(dt)


except KeyboardInterrupt:
    print('destroying actors')
    destroy()

finally:
    destroy()    
    print('done.')
