# This script allows remote collaboration for Reaper projects
# via GitHub

import reapy
import git

# Find the Reaper project inside this repo
project = reapy.Project('remotecollaboration')

# Find the Git repo inside the working directory (same as project path)
repo = git.Repo(project.path)

# Fetch the origin
origin = repo.remotes.origin
origin.fetch()
