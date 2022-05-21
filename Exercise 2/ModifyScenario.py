import argparse

import random

import subprocess
import os

import json


"""
Dictionary with a pedestrian schema. The currect script state allows to modify "targetIds", "position" and "velocity"
"""
pedestrianSchema = {
    "attributes" : {
        "id" : 1,
        "radius" : 0.2,
        "densityDependentSpeed" : False,
        "speedDistributionMean" : 1.34,
        "speedDistributionStandardDeviation" : 0.26,
        "minimumSpeed" : 0.5,
        "maximumSpeed" : 2.2,
        "acceleration" : 2.0,
        "footstepHistorySize" : 4,
        "searchRadius" : 1.0,
        "walkingDirectionCalculation" : "BY_TARGET_CENTER",
        "walkingDirectionSameIfAngleLessOrEqual" : 45.0
    },
    "source" : None,
    "targetIds" : [ None ],
    "nextTargetListIndex" : 0,
    "isCurrentTargetAnAgent" : False,
    "position" : {
        "x" : None,
        "y" : None
    },
    "velocity" : {
        "x" : None,
        "y" : None
    },
    "freeFlowSpeed" : 1.2131908770225284,
    "followers" : [ ],
    "idAsTarget" : -1,
    "isChild" : False,
    "isLikelyInjured" : False,
    "psychologyStatus" : {
        "mostImportantStimulus" : None,
        "threatMemory" : {
        "allThreats" : [ ],
        "latestThreatUnhandled" : False
        },
        "selfCategory" : "TARGET_ORIENTED",
        "groupMembership" : "OUT_GROUP",
        "knowledgeBase" : {
        "knowledge" : [ ],
        "informationState" : "NO_INFORMATION"
        },
        "perceivedStimuli" : [ ],
        "nextPerceivedStimuli" : [ ]
    },
    "healthStatus" : None,
    "infectionStatus" : None,
    "groupIds" : [ ],
    "groupSizes" : [ ],
    "agentsInGroup" : [ ],
    "trajectory" : {
        "footSteps" : [ ]
    },
    "modelPedestrianMap" : None,
    "type" : "PEDESTRIAN"
}

def addPedestrians(scenario, pedestriansStr):
    """For a given scenario dictionary returns a modified scenario with the pedestrians passed as a
    string. The string must be of the form: "[ (targetId, positionX, positionY, velocityX, velocityY), ... ]"

    Args:
        scenario (dict): Dictionary (from a JSON) with the scenario.
        pedestriansStr (_type_): String with the pedestrians to be added in the expected format.

    Returns:
        dict: Dictionary with the scenario after adding the pedestrians.
    """
    pedestriansToAdd = list(eval(pedestriansStr))

    editedScenario = scenario
    pedestrians = scenario["scenario"]["topography"]["dynamicElements"]
    for pedestrian in pedestriansToAdd:
        newPedestrian = pedestrianSchema.copy()

        newPedestrian["attributes"]["id"] = random.randint(pedestrian[0], pedestrian[0] + 1000)
        newPedestrian["targetIds"] = [pedestrian[0]]
        newPedestrian["position"]["x"] = pedestrian[1]
        newPedestrian["position"]["y"] = pedestrian[2]
        newPedestrian["velocity"]["x"] = pedestrian[3]
        newPedestrian["velocity"]["y"] = pedestrian[4]

        pedestrians.append(newPedestrian)

    editedScenario["scenario"]["topography"]["dynamicElements"] = pedestrians

    return editedScenario

def create_parser():
    """Creates and returns a parser with the options:
    - "file": to specify the scenario file path
    - "addpedestrians": a string with the pedestrians to be added in the scenario. Should have the format: "[ (targetId, positionX, positionY, velocityX, velocityY), ... ]"
    - "store": if set, the scenario should be stored in a new file
    - "execute": if set, the scenario should be executed

    Returns:
        parser: The parser with the options.
    """
    parser = argparse.ArgumentParser(description='This program is used to modify a Vadere scenario file.')
    parser.add_argument("file", type=str)
    parser.add_argument("--addpedestrians", type=str)
    parser.add_argument("--store", action="store_true")
    parser.add_argument("--execute", action="store_true")

    return parser

def main(args):
    """Receives the arguments and depending on the options, modifies the scenario file, saves the file
    and/or executes it.

    Args:
        args (dict): Dictionary with the input arguments.
    """
    with open(args.file) as json_file:
        try:
            scenario = json.load(json_file)
        except ValueError as e:
            print("This is not a valid JSON file.")
            return None

    if args.addpedestrians is not None:
        scenario = addPedestrians(scenario, args.addpedestrians)

    scenario["name"] = scenario["name"] + "_modified"

    newScenarioPath = scenario["name"] + ".scenario"

    if args.store:
        with open(newScenarioPath, "w") as outfile:
            json.dump(scenario, outfile)

    if args.execute:
        if not args.store:
            newScenarioPath = open(newScenarioPath, mode="w+")
            json.dump(scenario, newScenarioPath)
            newScenarioPath.close()
            os.chmod(newScenarioPath.name, 0o777)

        subprocess.call(['java', '-jar', 'vadere-console.jar', 'scenario-run',
                         '--scenario-file', '"{}"'.format(newScenarioPath.name),
                         '--output-dir=output/'])

        if not args.store:
            os.remove(newScenarioPath.name)

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)
