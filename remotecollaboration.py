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
# 8. You'll need to configure your own SSH key to write to your repo
  # See: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
  # See: https://docs.github.com/en/get-started/getting-started-with-git/managing-remote-repositories#switching-remote-urls-from-https-to-ssh

import sys
import os
sys.path.append(RPR_GetResourcePath() + '/Scripts/ReaTeam Extensions/API')

import imgui_python
import reapy
import git

# Find the Reaper project inside this repo
project = reapy.Project('remotecollaboration')

# Find the Git repo inside the working directory (same as project path)
repo = git.Repo(project.path)

# Get the SSH key info
git_ssh_identity_file = os.path.expanduser('~/.ssh/id_ed25519')
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

# Get the origin
origin = repo.remotes.origin

# Keep track of branches
local_branch_names = []
remote_branch_names = []

def init():
  global ctx
  global current_local_branch
  global current_remote_branch
  global commit_message
  global new_branch_name
  ctx = imgui_python.ImGui_CreateContext('GitHub Reaper')
  updateBranchList()
  current_local_branch = [repo.active_branch]
  current_remote_branch = [remote_branch_names[0]]
  commit_message = ['']
  new_branch_name = ['']
  loop()

# Render cycle for drop-down menu
def renderDropdown(name: str, binding, branches):
  if imgui_python.ImGui_BeginCombo(ctx, name, binding[0]):
    for branch in branches:
      is_selected = (binding[0] == branch)
      (begin_select, is_selected) = imgui_python.ImGui_Selectable(ctx, branch, is_selected)
      if begin_select:
        # Set the menu binding
        binding[0] = branch
        # Checkout the selected branch
        checkout(branch)
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
    renderDropdown('Local Branches', current_local_branch, local_branch_names)
    renderDropdown('Remote Branches', current_remote_branch, remote_branch_names)
    if imgui_python.ImGui_Button(ctx, 'Delete Selected Local Branch'):
      # Store menu binding for deletion
      deleting_head = current_local_branch[0]
      # Set menu binding to default branch
      current_local_branch[0] = repo.heads[0]
      # Checkout default branch to avoid errors
      repo.heads.main.checkout()
      # Open the project for default branch
      reapy.open_project(project.path + '/remotecollaboration.rpp')
      repo.delete_head(deleting_head)
      local_branch_names.remove(deleting_head)
    if imgui_python.ImGui_Button(ctx, 'Delete Selected Remote Branch'):
      # Store menu binding for deletion
      deleting_branch = str.split(current_remote_branch[0],'/')[1]
      # Set menu binding to default branch
      current_local_branch[0] = repo.heads[0]
      current_remote_branch[0] = repo.heads[0]
      # Checkout default branch to avoid errors
      repo.heads.main.checkout()
      with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        origin.push(refspec=(":%s" % deleting_branch))
        updateBranchList()

    (show_textinput, message) = imgui_python.ImGui_InputText(ctx, 'Commit message', commit_message[0])
    if show_textinput:
      commit_message[0] = message
    (create_new_branch_name, branch_name) = imgui_python.ImGui_InputText(ctx, 'New branch name', new_branch_name[0])
    if create_new_branch_name:
      new_branch_name[0] = branch_name

    if imgui_python.ImGui_Button(ctx, 'Create Branch'):
      if new_branch_name[0] == '':
        reapy.show_message_box("Please enter a name for the new branch.", "Branch Name Empty")
      else:
        new_branch = repo.create_head(new_branch_name[0])
        new_branch.checkout()
        local_branch_names.append(new_branch_name[0])

    if imgui_python.ImGui_Button(ctx, 'Push Changes'):
        git_ssh_identity_file = os.path.expanduser('~/.ssh/id_ed25519')
        git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
        files = repo.git.diff(None, name_only=True)
        with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
          if commit_message[0] == '' and new_branch_name[0] == '':
            reapy.show_message_box("Please enter text for commit message", "Commit Failed")
          elif new_branch_name[0] != '':
            origin.push(new_branch_name[0])
            new_branch_name[0] = ''
            updateBranchList()
          elif len(files) == 0:
            reapy.show_message_box("No files have changed.", "Commit Failed")
          else:
            for f in files.split('\n'):
              repo.git.add(f)
            repo.index.commit(commit_message[0])
            origin.push()
            updateBranchList()
    imgui_python.ImGui_End(ctx)

  if open:
    RPR_defer('loop()')

def fetchOrigin(debugMode = False):
  with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    origin.update()

  if debugMode:
    reapy.print('Successfully fetched:', origin.name)
    reapy.print('at:',origin.url)
    reapy.print('branches:',origin.refs)
    reapy.print('')

def checkout(branch: str):
  try:
    repo.heads[branch].checkout()
  except:
    ref = origin.refs[str.split(branch,'/')[1]]
    if ref.remote_head not in repo.heads:
      new_head = repo.create_head(ref.remote_head, ref)
      new_head.set_tracking_branch(ref)
      local_branch_names.append(new_head.name)
    repo.heads[ref.remote_head].checkout()
    current_local_branch[0] = str.split(branch,'/')[1]

def updateBranchList(debugMode = False):
  fetchOrigin(debugMode = debugMode)

  # Reset branch list
  local_branch_names.clear()
  remote_branch_names.clear()

  # Get local branch list
  for head in repo.heads:
    if head.name != 'HEAD':
      local_branch_names.append(head.name)

  # Get remote branch list
  for ref in origin.refs:
    if ref.name != origin.name+'/'+'HEAD':
      remote_branch_names.append(ref.name)

  if debugMode:
    reapy.print('local heads:',repo.heads)
    reapy.print('local refs:',repo.refs)
    reapy.print('remote refs:',origin.refs)
    reapy.print('local branches:',local_branch_names)
    reapy.print('remote branches:',remote_branch_names)
    reapy.print('')

RPR_defer('init()')
