# This script allows remote collaboration for Reaper projects
# via GitHub

import reapy

# Find the Reaper project inside this repo
project = reapy.Project('remotecollaboration')

reapy.print(project)
