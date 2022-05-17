import argparse
import tempfile

import subprocess

import json

# Modify "targetIds", "position" and "velocity"
pedestrianSchema = {
    "attributes" : {
        "id" : 1,
        "radius" : 0.2,
        "densityDependentSpeed" : false,
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
    "source" : null,
    "targetIds" : [ None ],
    "nextTargetListIndex" : 0,
    "isCurrentTargetAnAgent" : false,
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
    "isChild" : false,
    "isLikelyInjured" : false,
    "psychologyStatus" : {
        "mostImportantStimulus" : null,
        "threatMemory" : {
        "allThreats" : [ ],
        "latestThreatUnhandled" : false
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
    "healthStatus" : null,
    "infectionStatus" : null,
    "groupIds" : [ ],
    "groupSizes" : [ ],
    "agentsInGroup" : [ ],
    "trajectory" : {
        "footSteps" : [ ]
    },
    "modelPedestrianMap" : null,
    "type" : "PEDESTRIAN"
}

def addPedestrians(scenario, pedestriansStr):
    pedestriansToAdd = list(eval(pedestriansStr))

    editedScenario = scenario
    pedestrians = scenario["scenario"]["topography"]["dynamicElements"]
    for pedestrian in pedestriansToAdd:
        newPedestrian = pedestrianSchema.copy()
        
        newPedestrian["targetIds"] = [pedestrian[0]]
        newPedestrian["position"]["x"] = pedestrian[1]
        newPedestrian["position"]["y"] = pedestrian[2]
        newPedestrian["velocity"]["x"] = pedestrian[3]
        newPedestrian["velocity"]["y"] = pedestrian[4]

        pedestrians.append(newPedestrian)

    editedScenario["scenario"]["topography"]["dynamicElements"] = pedestrians

    return editedScenario

def create_parser():
    parser = argparse.ArgumentParser(dexcription='This program is used to modify a Vadere scenario file.')
    parser.add_argument("file", type=str)
    parser.add_argument("--addpedestrians", type=str)
    parser.add_argument("--store", action="store_true")
    parser.add_argument("--execute", action="executre_true")

def main(args):
    with open(args.file) as json_file:
        try:
            scenario = json.load(json_file)
        except ValueError as e:
            print("This is not a valid JSON file.")
            return None

    if args.addpedestrians is not None:
        scenario = addPedestrians(scenario, args.addpedestrians)

    newScenarioPath = ""

    if args.store:
        newScenarioPath = "newScenario.json"
        with open(newScenarioPath, "w") as outfile:
            json.dump(scenario, outfile)

    if args.execute:
        if not args.store:
            newScenarioPath = tempfile.NamedTemporaryFile(mode="w+")
            json.dump(scenario, newScenarioPath)

        subprocess.call(['java', '-jar', 'vadere-console.jar', 'scenario-run',
                         '--scenario-file', newScenarioPath.name,
                         '--output-dir="./output/"'])

        if not args.store:
            newScenarioPath.close()

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)