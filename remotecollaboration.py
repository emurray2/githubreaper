# This script allows remote collaboration for Reaper projects
# via GitHub

import reapy
import git

# Find the Reaper project inside this repo
project = reapy.Project('remotecollaboration')

reapy.print(project)

# Find the Git repo inside the working directory (same as project path)
repo = git.Repo(project.path)

reapy.print(repo)

# Fetch the origin
origin = repo.remotes.origin
origin.fetch()

reapy.print(origin.refs)
