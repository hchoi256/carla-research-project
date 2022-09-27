import glob
import os
import sys
import pandas as pd
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

VEH_NUM = 5
actor_list = []

def destroy():
    for actor in actor_list:
        actor.destroy()

try:
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(5.0)

    world = client.get_world()

    # 1. Choose blueprint
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints
    vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))

    # 2. Choose spawn point
    spawn_points = world.get_map().get_spawn_points()

    # 3. Spawn the vehicles
    for i in range(VEH_NUM):

        # Choose random blueprint and choose the i-th default spawn points
        vehicle_bp_i = random.choice(blueprint_library.filter('vehicle.*.*'))
        spawn_point_i = spawn_points[i]

        # Spawn the actor
        vehicle_i = world.spawn_actor(vehicle_bp_i, spawn_point_i)

        # Set control mode for v_i. https://carla.readthedocs.io/en/latest/python_api/#carla.Vehicle
        vehicle_i.set_autopilot(True)

        # Append to the actor_list
        actor_list.append(vehicle_i)

    # 4. Print the realtime information of the agents
    world_snapshot = world.get_snapshot()
    cur_t = world_snapshot.timestamp.elapsed_seconds
    terminating_point = cur_t # curr time

    # dataset = dict() #added
    frames = []
    timestamps = []
    vehicle_ID = []
    location_X = []
    location_Y = []
    velocity_X = []
    velocity_Y = []
    acceleration_X = []
    acceleration_Y = []

    while True:
        # Retrieve a snapshot of the world at current frame.
        world_snapshot = world.get_snapshot()
        frame = world_snapshot.frame
        timestamp = world_snapshot.timestamp.elapsed_seconds # Get the time reference
        # frames.append(world_snapshot.frame) #added
        # timestamps.append(world_snapshot.timestamp.elapsed_seconds) #added

        INFO = '' 
        global_status = 'Frame:{%s}, Timestamp:{%.3f s}. \n' %(frame, timestamp)
        INFO += global_status
        for i in range(len(actor_list)):
            actor_i = actor_list[i]
            loc = actor_i.get_location()
            vel = actor_i.get_velocity()
            acc = actor_i.get_acceleration()
    
            actor_i_status = 'Vehicle_ID:{%s}, Location_X:{%.3f}, Location_Y:{%.3f}, Velocity_X:{%.3f}, Velocity_Y:{%.3f}, Acceleration_X:{%.3f}, Acceleration_Y:{%.3f}.' %(i, loc.x, loc.y, vel.x, vel.y, acc.x, acc.y)
            
            frames.append(world_snapshot.frame) #added
            timestamps.append(world_snapshot.timestamp.elapsed_seconds) #added
            vehicle_ID.append(i) #added
            location_X.append(loc.x) #added
            location_Y.append(loc.y) #added
            velocity_X.append(vel.x) #added
            velocity_Y.append(vel.x) #added
            acceleration_X.append(acc.x) #added
            acceleration_Y.append(acc.y) #added
            
            INFO += actor_i_status
        
        # Set the print inteval
        if round(abs(timestamp - cur_t), 1) == 0.1:
            print('-------------------------------------------------------------------------------')
            print(INFO)
            print('-------------------------------------------------------------------------------\n')
            cur_t = timestamp

        # Breaking point
        if abs(terminating_point - cur_t) > .1:
            break

    print('Escaped the loop')
    df = pd.DataFrame({'Frame': frames, 
                        'Timestamp': timestamps, 
                        'Vehicle_ID': vehicle_ID, 
                        'Location_X': location_X, 
                        'Location_Y': location_Y, 
                        'Velocity_X': velocity_X,
                        'Velocity_Y': velocity_Y, 
                        'Acceleration_X': acceleration_X, 
                        'Acceleration_Y': acceleration_Y})
    
    df.to_excel("./actor_info.xlsx")

    time.sleep(30)

# except:
#     destroy()

finally:
    print('destroying actors')
    destroy()
    print('done.')