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
import cv2

IM_WIDTH = 640
IM_HEIGHT = 480

def process_img(image, name):
    print("Frame: "+str(image.frame)+", timestamp: "+str(image.timestamp))
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    cv2.imshow(name, i3)
    cv2.waitKey(1)

    if image.frame % 20 == 0:
        image.save_to_disk('_out/%06d.png' % image.frame)
    return i3/255.0


actor_list = []
try:
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(10)

    world = client.get_world()

    # 1. Choose blueprint for the vehicle
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints
    
    vehicle = blueprint_library.find('vehicle.tesla.model3') # vehicle_bp = blueprint_library.filter('model3')[0]
    vehicle.set_attribute('color', '255,0,0')
    print(vehicle)

    # 2. Choose spawn point
    # manually
    # spawn_point = carla.Transform(carla.Location(x=, y=, z=), 
    # carla.Rotation(pitch=, yaw=, roll=))
    
    # automatically
    spawn_point_vehicle = random.choice(world.get_map().get_spawn_points())
    print(spawn_point_vehicle)

    # 3. Spawn the vehicles
    # spawn the actor
    actor_vehicle = world.spawn_actor(vehicle, spawn_point_vehicle)
 
    # set control mode. https://carla.readthedocs.io/en/latest/python_api/#carla.Vehicle
    # vehicle.apply_control(carla.VehicleControl(throttle=0.1, steer=0.0))
    actor_vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.

    # append to the actor_list
    actor_list.append(actor_vehicle)

    # 4. Get the blueprint for this sensor: https://carla.readthedocs.io/en/latest/core_sensors/
    sensor = blueprint_library.find('sensor.camera.rgb')
    # Change the dimensions of the image
    sensor.set_attribute('image_size_x', f'{IM_WIDTH}')
    sensor.set_attribute('image_size_y', f'{IM_HEIGHT}')
    sensor.set_attribute('fov', '110')
    
    # 5. Adjust sensor relative to vehicle
    # choose the relative spawn point
    spawn_point_sensor = carla.Transform(carla.Location(x=2.5, z=1.0), carla.Rotation(pitch=-15))
    print(spawn_point_sensor)

    # spawn the sensor and attach to vehicle.
    actor_sensor = world.spawn_actor(sensor, spawn_point_sensor, attach_to=actor_vehicle)

    # add sensor to list of actors
    actor_list.append(actor_sensor)

    # 6. Process the collected images: https://carla.readthedocs.io/en/latest/core_sensors/#listening
    # Use the data collected by the sensor. The lambda function can be customized
    actor_sensor.listen(lambda data: process_img(data, "camera1"))
    # actor_sensor.listen(lambda image: image.save_to_disk('output/%06d.png' % image.frame))

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')