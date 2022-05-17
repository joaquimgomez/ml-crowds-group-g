import argparse
import os
import tempfile

import subprocess

import json


def addPedestrians(scenario, pedestriansStr):
    pedestriansToAdd = list(eval(pedestriansStr))

    for pedestrian in pedestriansToAdd:
        # TODO: Add pedestrians to the scenario
        pass

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