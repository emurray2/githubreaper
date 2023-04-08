# This script allows remote collaboration for Reaper projects
# via GitHub

# Things you need:
# 1. Update your system to latest software (usually good to do)
# 2. Update Python (this script uses 3.11.2)
# 3. Update Reaper (currently using v6.78 macOS-arm64)
# 4. Update pip (Python package manager) using 'pip3 install --upgrade pip' (currently using 23.0.1)
# 5. Install required modules below using 'pip3 install <required module>'
  # - 'pip3 install GitPython'
  # - 'pip3 install python-reapy'
# 6. Install ReaPack: https://reapack.com/
# 7. Install ReaImGui through ReaPack: https://github.com/cfillion/reaimgui

import sys
sys.path.append(RPR_GetResourcePath() + '/Scripts/ReaTeam Extensions/API')

import imgui_python
import reapy
import git

# Find the Reaper project inside this repo
project = reapy.Project('remotecollaboration')

# Find the Git repo inside the working directory (same as project path)
repo = git.Repo(project.path)

# Get the origin
origin = repo.remotes.origin

def init():
  global ctx
  ctx = imgui_python.ImGui_CreateContext('GitHub Reaper')
  loop()

def loop():
  imgui_python.ImGui_SetNextWindowSize(ctx, 700, 500, imgui_python.ImGui_Cond_FirstUseEver())
  visible, open = imgui_python.ImGui_Begin(ctx, 'GitHub Reaper', True)

  if visible:
    if imgui_python.ImGui_Button(ctx, 'Fetch Origin'):
      updateBranchList(debugMode = False)

    imgui_python.ImGui_End(ctx)

  if open:
    RPR_defer('loop()')

def fetchOrigin(debugMode = False):
  repo.delete_remote(origin)
  repo.create_remote('origin','https://github.com/emurray2/reaperfun')
  origin.fetch()

  if debugMode:
    reapy.print('Successfully fetched:', origin.name)
    reapy.print('at:',origin.url)
    reapy.print('branches:',origin.refs)
    reapy.print('')

def updateBranchList(debugMode = False):
  remote_branch_names = []

  fetchOrigin(debugMode = debugMode)

  # Add heads from remote
  for ref in origin.refs:
    remote_branch_names.append(ref.remote_head)
    if ref.remote_head not in repo.heads:
      new_head = repo.create_head(ref.remote_head, ref)
      new_head.set_tracking_branch(ref)

  # Delete heads not on remote (for the sake of simplicity)
  for head in repo.heads:
    if head.name not in remote_branch_names:
      repo.delete_head(head.name)

  if debugMode:
    reapy.print('local heads:',repo.heads)
    reapy.print('local refs:',repo.refs)
    reapy.print('remote refs:',origin.refs)
    reapy.print('')

RPR_defer('init()')
