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
    print('start simulation.')
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(5.0)
    world = client.get_world()

    # 1. Choose blueprint
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints
    
    # Find out the blueprint of the traffic cone or construction cone. 
    # This link provides the name of the default blueprint provided by awwwwwaaaaaaaaaaaaawwwwwwwwwwwwwCARLA. Check this page: https://carla.readthedocs.io/en/latest/bp_library/
    cone_bp_1 = blueprint_library.find('static.prop.constructioncone')
    cone_bp_2 = blueprint_library.find('static.prop.trafficcone01')
    cone_bp_3 = blueprint_library.find('static.prop.trafficcone02')


    # 2. Choose spawn point

    # Manually choose a coordinate of the point
    transform_1 = carla.Transform(carla.Location(x=-30, y=10, z=0))
    transform_2 = carla.Transform(carla.Location(x=-31, y=9, z=0))
    transform_3 = carla.Transform(carla.Location(x=-32, y=11, z=0))

    # 3. Spawn the actor
    cone_1 = world.spawn_actor(cone_bp_1, transform_1)
    print('construction cone is generated at location (%.1f, %.1f).' % (transform_1.location.x, transform_1.location.y))
    cone_2 = world.spawn_actor(cone_bp_2, transform_2)
    print('traffic cone 01 is generated at location (%.1f, %.1f).' % (transform_2.location.x, transform_2.location.y))
    cone_3 = world.spawn_actor(cone_bp_3, transform_3)
    print('traffic cone 02 is generated at location (%.1f, %.1f).' % (transform_3.location.x, transform_3.location.y))

    # 4. Append to the actor_list
    actor_list.append(cone_1)
    actor_list.append(cone_2)
    actor_list.append(cone_3)


    # 5. Set the simulation time in second
    time.sleep(30)

finally:
    print('destroying actors')
    destroy()
    print('done.')