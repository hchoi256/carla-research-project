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

try:
    print('start simulation.')
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(5.0)
    world = client.get_world()

    # 1. Get the weather object. 
    weather = world.get_weather()

    # 2. Set the weather parameters. Check this link: https://carla.readthedocs.io/en/latest/python_api/#carla.WeatherParameters
    # Example 1: foggy sunset
    weather.sun_altitude_angle = -30
    weather.fog_density = 65
    weather.fog_distance = 10
    world.set_weather(weather)

    time.sleep(10)

    # Example 2: Rainy afternoon
    weather.sun_altitude_angle = 10
    weather.cloudiness = 10
    weather.precipitation = 80
    weather.precipitation_deposits = 60
    world.set_weather(weather)


finally:
    print('done.')