'''
Copyright (c) 2023 Evan Murray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# This script contains a GUI for interacting with merge conflicts

import sys
import os
sys.path.append(RPR_GetResourcePath() + '/Scripts/ReaTeam Extensions/API')
import imgui_python
import reapy
import git

def init():
    global ctx
    # List of dictionaries containing the buttons states for each row
    global row_states
    # Reference containing the last button id the user pressed
    global last_button
    # Reference containing the last row number the user interacted with
    global last_row
    # List of conflicts
    global conflict_list

    ctx = imgui_python.ImGui_CreateContext('Conflict Resolver')
    row_states = []
    last_button = ['']
    last_row = [0]
    conflict_list = ['Conflict #1', 'Conflict #2', 'Conflict #3']
    loop()

def loop():
    imgui_python.ImGui_SetNextWindowSize(ctx, 700, 500, imgui_python.ImGui_Cond_FirstUseEver())
    visible, open = imgui_python.ImGui_Begin(ctx, 'Conflict Resolver', True)

    if visible:
        createConflictTable(conflict_list)
        imgui_python.ImGui_End(ctx)
    if open:
        RPR_defer('loop()')

def createConflictTable(conflicts):
    num_columns = 3

    imgui_python.ImGui_BeginTable(ctx, 'Conflict Table', num_columns)

    # Create the table header
    imgui_python.ImGui_TableSetupColumn(ctx, '')
    imgui_python.ImGui_TableSetupColumn(ctx, 'Side #1')
    imgui_python.ImGui_TableSetupColumn(ctx, 'Side #2')
    imgui_python.ImGui_TableHeadersRow(ctx)

    # Create rows with each conflict name and the corresponding buttons for each side
    addConflicts(conflicts, num_columns-1)

    imgui_python.ImGui_EndTable(ctx)

def addConflicts(conflicts, num_buttons: int):
    # Render (loop through) each row
    for row in range(0, len(conflicts)):
        imgui_python.ImGui_TableNextColumn(ctx)
        imgui_python.ImGui_Text(ctx, conflicts[row])
        addButtons(row, num_buttons)

def addButtons(row_number: int, num_buttons: int):
    # Create a dictionary for the row state if it doesn't exist
    if not 0 <= row_number < len(row_states):
        row_states.append({})

    # Get the reference dictionary for the current row being rendered
    button_states = row_states[row_number]

    # Loop through the buttons in this row
    for i in range(0, num_buttons):
        imgui_python.ImGui_TableNextColumn(ctx)
        button_id = str(row_number) + str(i)

        # If this button doesn't have a state already, add it to the dictionary
        if button_id not in button_states:
            button_states[button_id] = False

        # If this button is clicked, do the following:
        if imgui_python.ImGui_RadioButton(ctx, '##radio_table_' + str(button_id), button_states[button_id]):
            # Get the row number and id of the clicked button and store them in their respective references
            last_row[0] = row_number
            last_button[0] = button_id

        # Deactivate the other buttons in this row
        elif last_row[0] == row_number:
            button_states[button_id] = False

        # Keep the state of the last button pressed
        button_states[last_button[0]] = True

RPR_defer('init()')
