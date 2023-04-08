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
# 6. Install ReaPack: https://reapack.com/ (currently using v1.2.4.3 macOS arm64)
# 7. Install ReaImGui through ReaPack: https://github.com/cfillion/reaimgui (currently using 0.8.5)

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

# Keep track of branches
local_branch_names = []
remote_branch_names = []

def init():
  global ctx
  global current_local_branch
  global current_remote_branch
  ctx = imgui_python.ImGui_CreateContext('GitHub Reaper')
  updateBranchList()
  current_local_branch = [repo.active_branch]
  current_remote_branch = [remote_branch_names[0]]
  loop()

# Render cycle for drop-down menu
def cycleDropdown():
  if imgui_python.ImGui_BeginCombo(ctx, 'Local Branches', current_local_branch[0]):
    for branch in local_branch_names:
      is_selected = (current_local_branch[0] == branch)
      (begin_select, is_selected) = imgui_python.ImGui_Selectable(ctx, branch, is_selected)
      if begin_select:
        # Set the menu binding
        current_local_branch[0] = branch
        # Checkout the selected branch
        repo.heads[branch].checkout()
        # Open the project for the selected branch
        reapy.open_project(project.path + '/remotecollaboration.rpp')
      if is_selected:
        imgui_python.ImGui_SetItemDefaultFocus(ctx)
    imgui_python.ImGui_EndCombo(ctx)
  if imgui_python.ImGui_BeginCombo(ctx, 'Remote Branches', current_remote_branch[0]):
    for branch in remote_branch_names:
      is_selected = (current_remote_branch[0] == branch)
      (begin_select, is_selected) = imgui_python.ImGui_Selectable(ctx, branch, is_selected)
      if begin_select:
        # Set the menu binding
        current_remote_branch[0] = branch
        # Check if ref exists in local
        ref = origin.refs[str.split(branch,'/')[1]]
        if ref.remote_head not in repo.heads:
          new_head = repo.create_head(ref.remote_head, ref)
          new_head.set_tracking_branch(ref)
          local_branch_names.append(new_head.name)
        repo.heads[ref.remote_head].checkout()
        current_local_branch = str.split(branch,'/')[1]
        # Open the project for the selected branch
        reapy.open_project(project.path + '/remotecollaboration.rpp')
      if is_selected:
        imgui_python.ImGui_SetItemDefaultFocus(ctx)
    imgui_python.ImGui_EndCombo(ctx)

def loop():
  imgui_python.ImGui_SetNextWindowSize(ctx, 700, 500, imgui_python.ImGui_Cond_FirstUseEver())
  visible, open = imgui_python.ImGui_Begin(ctx, 'GitHub Reaper', True)

  if visible:
    if imgui_python.ImGui_Button(ctx, 'Fetch Origin'):
      updateBranchList()
    cycleDropdown()
    if imgui_python.ImGui_Button(ctx, 'Delete Selected Local Branch'):
      # Store menu binding for deletion
      deleting_head = current_local_branch[0]
      # Set menu binding to default branch
      current_local_branch[0] = repo.heads[0]
      # Checkout default branch to avoid errors
      repo.heads[0].checkout()
      # Open the project for default branch
      reapy.open_project(project.path + '/remotecollaboration.rpp')
      repo.delete_head(deleting_head)
      local_branch_names.remove(deleting_head)
    if imgui_python.ImGui_Button(ctx, 'Push Changes'):
        reapy.print('push changes')
        #repo.remotes.origin.push()
    imgui_python.ImGui_End(ctx)

  if open:
    RPR_defer('loop()')

def fetchOrigin(debugMode = False):
  ssh_cmd = 'ssh -i id_deployment_key'
  with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
    repo.remotes.origin.fetch()

  if debugMode:
    reapy.print('Successfully fetched:', origin.name)
    reapy.print('at:',origin.url)
    reapy.print('branches:',origin.refs)
    reapy.print('')

def updateBranchList(debugMode = False):

  fetchOrigin(debugMode = debugMode)

  # Reset branch list
  local_branch_names.clear()
  remote_branch_names.clear()

  # Get local branch list
  for head in repo.heads:
    local_branch_names.append(head.name)

  # Get remote branch list
  for ref in origin.refs:
    remote_branch_names.append(ref.name)

  if debugMode:
    reapy.print('local heads:',repo.heads)
    reapy.print('local refs:',repo.refs)
    reapy.print('remote refs:',origin.refs)
    reapy.print('local branches:',local_branch_names)
    reapy.print('remote branches:',remote_branch_names)
    reapy.print('')

RPR_defer('init()')
