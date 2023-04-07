# This script allows remote collaboration for Reaper projects
# via GitHub
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
      origin.fetch()
      reapy.print('Successfully fetched:', origin.name,'at:',origin.url,'branches:',origin.refs)

    imgui_python.ImGui_End(ctx)

  if open:
    RPR_defer('loop()')

RPR_defer('init()')
