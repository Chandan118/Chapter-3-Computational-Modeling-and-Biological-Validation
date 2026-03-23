#!/usr/bin/env python3
"""
gazebo_playback.py

Author      : Chandan Sheikder
Email       : chandan@bit.edu.cn
Phone       : +8618222390506
Affiliation : Beijing Institute of Technology (BIT)
Date        : 2026-03-23

Description:
    Gazebo Playback Script - Plays recorded simulation
"""

import json

import rospy


def load_simulation_data():
    with open("simulation_data.json", "r") as f:
        return json.load(f)


def play_in_gazebo():
    rospy.init_node("ant_simulation_playback")

    # Load data
    data = load_simulation_data()

    print("Playing simulation in Gazebo...")
    print(f"Total frames: {len(data['frames'])}")

    rate = rospy.Rate(10)  # 10 Hz

    for i, tick in enumerate(data["ticks"]):
        if rospy.is_shutdown():
            break

        # Update visualization based on data
        foraging = data["ants_foraging"][i]
        food = data["food_collected"][i]
        pheromone = data["pheromone"][i]

        print(f"Tick {tick}: Food={food}, Foraging={foraging}, Pheromone={pheromone:.3f}")

        rate.sleep()

    print("Playback complete!")


if __name__ == "__main__":
    try:
        play_in_gazebo()
    except rospy.ROSInterruptException:
        pass
