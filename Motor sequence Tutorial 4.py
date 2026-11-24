#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PSY310 - Motor Sequence Learning Experiment (PsychoPy Coder version)

Four vertical lines are shown, mapped to the keys Z X C V (left to right).
A small triangle (the probe) appears above one line; the participant presses
the matching key as fast as possible.

Block 1 (Sequential): the 4 rows of sequence_conditions.csv repeat in the SAME order
                      (x, v, c, z, x, v, c, z, ...)
Block 2 (Random):     the same rows in fully random order

Put sequence_conditions.csv in the same folder as this script
(if it is missing or wrong, the script uses the same 4 rows built in).

Output (in a 'data' folder next to this script):
  <participant>_SequenceLearning_<date>.csv  -> one row per trial (opens in Excel)

Press ESC during a trial to quit (data collected so far is saved).
"""

import os
import sys
import traceback

# If anything goes wrong, write the error to error_log.txt next to this script
_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error_log.txt')


def _log_error(exc_type, exc, tb):
    text = ''.join(traceback.format_exception(exc_type, exc, tb))
    print(text)
    with open(_LOG, 'w') as f:
        f.write(text)


sys.excepthook = _log_error

from psychopy import visual, core, event, data, gui

# ------------------------------------------------------------------
# SETTINGS (change these if your instructor asks for different values)
# ------------------------------------------------------------------
N_REPS = 50              # repeats of the 4-row sequence per block.
                         # 50 x 4 = 200 trials per block, 400 in total.
                         # The tutorial uses 24 (96 per block, 192 in total).
FIX_DURATION = 1.0       # fixation cross alone: 0 - 1 s
LINES_ONSET = 1.0        # lines appear at 1 s
PROBE_ONSET = 2.0        # probe (triangle) appears at 2 s; RT is measured from here
COUNTERBALANCE = False   # False = Sequential block first for everyone (as in the tutorial)
                         # True  = odd participant numbers: Sequential first,
                         #         even participant numbers: Random first
FIX_COLOR = 'white'      # the tutorial suggests grey (-0.2549, 0.2392, 0.2549)
LINE_COLOR = 'white'
PROBE_COLOR = 'white'

# ------------------------------------------------------------------
# PARTICIPANT INFO + DATA FILE
# ------------------------------------------------------------------
expName = 'SequenceLearning'
expInfo = {'participant': '', 'session': '001'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if not dlg.OK:
    core.quit()
expInfo['date'] = data.getDateStr()
expInfo['expName'] = expName

thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(thisDir)
os.makedirs(os.path.join(thisDir, 'data'), exist_ok=True)
filename = os.path.join(thisDir, 'data',
                        '%s_%s_%s' % (expInfo['participant'], expName, expInfo['date']))

thisExp = data.ExperimentHandler(name=expName, extraInfo=expInfo,
                                 dataFileName=filename,
                                 savePickle=False, saveWideText=True)

BUILT_IN = [{'pos': -50, 'corr_resp': 'x'},
            {'pos': 150, 'corr_resp': 'v'},
            {'pos': 50, 'corr_resp': 'c'},
            {'pos': -150, 'corr_resp': 'z'}]
conditions_path = os.path.join(thisDir, 'sequence_conditions.csv')
conditions = None
if os.path.exists(conditions_path):
    loaded = data.importConditions(conditions_path)
    if loaded and all(('pos' in row and 'corr_resp' in row) for row in loaded):
        conditions = loaded
        print('Using conditions file:', conditions_path)
    else:
        print('sequence_conditions.csv does not have the columns pos and corr_resp '
              '- using the built-in conditions instead')
if conditions is None:
    # Same 4 rows as sequence_conditions.csv (from the tutorial)
    if not os.path.exists(conditions_path):
        print('sequence_conditions.csv not found - using the built-in conditions')
    conditions = BUILT_IN
# make sure values are the right type even if the CSV has stray spaces
conditions = [{'pos': float(str(c['pos']).strip()),
               'corr_resp': str(c['corr_resp']).strip().lower()} for c in conditions]

# ------------------------------------------------------------------
# WINDOW + STIMULI (units = pixels, as in the tutorial)
# ------------------------------------------------------------------
win = visual.Window(fullscr=True, color=[0, 0, 0], colorSpace='rgb',
                    units='pix', allowGUI=False)

fixation = visual.ShapeStim(win, name='Fixation', vertices='cross',
                            size=(10, 10), pos=(0, 0),
                            fillColor=FIX_COLOR, lineColor=FIX_COLOR)

# four vertical lines: a 100 x 10 rectangle rotated 90 degrees
lines = [visual.Rect(win, name='line%d' % (i + 1), width=100, height=10,
                     pos=(x, 0), ori=90,
                     fillColor=LINE_COLOR, lineColor=LINE_COLOR)
         for i, x in enumerate([-150, -50, 50, 150])]

probe = visual.ShapeStim(win, name='probe', vertices='triangle',
                         size=(10, 10), pos=(0, 60),
                         fillColor=PROBE_COLOR, lineColor=PROBE_COLOR)

message = visual.TextStim(win, height=24, wrapWidth=900, color='white')

trial_clock = core.Clock()
rt_clock = core.Clock()


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------
def quit_and_save():
    thisExp.saveAsWideText(filename + '.csv')
    thisExp.abort()  # prevents a second, duplicate save
    win.close()
    core.quit()


def show_message(text):
    """Show text and wait for the space bar (ESC quits)."""
    message.text = text
    message.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        quit_and_save()


def run_trial(pos, corr_resp):
    """One trial: fixation -> lines -> probe; returns (key, rt, correct)."""
    probe.pos = (pos, 60)
    event.clearEvents()
    trial_clock.reset()
    probe_shown = False

    while True:
        t = trial_clock.getTime()
        if t < FIX_DURATION:
            fixation.draw()
        if t >= LINES_ONSET:
            for line in lines:
                line.draw()
        if t >= PROBE_ONSET:
            probe.draw()
            if not probe_shown:
                win.callOnFlip(rt_clock.reset)   # RT starts when the probe appears
                win.callOnFlip(event.clearEvents)  # ignore keys pressed before the probe
                probe_shown = True
        win.flip()

        if probe_shown:
            keys = event.getKeys(timeStamped=rt_clock)
            if keys:
                key, rt = keys[0]
                if key == 'escape':
                    quit_and_save()
                correct = 1 if key == corr_resp else 0
                return key, rt, correct
        elif event.getKeys(keyList=['escape']):
            quit_and_save()


def run_block(block_name, loop_type, block_number):
    trials = data.TrialHandler(trialList=conditions, nReps=N_REPS,
                               method=loop_type, name=block_name)
    thisExp.addLoop(trials)
    trial_in_block = 0
    for thisTrial in trials:
        trial_in_block += 1
        key, rt, correct = run_trial(thisTrial['pos'], thisTrial['corr_resp'])
        trials.addData('block', block_name)
        trials.addData('block_number', block_number)
        trials.addData('trial_in_block', trial_in_block)
        trials.addData('key_resp.keys', key)
        trials.addData('key_resp.corr', correct)
        trials.addData('key_resp.rt', rt)
        thisExp.nextEntry()


# ------------------------------------------------------------------
# BLOCK ORDER
# ------------------------------------------------------------------
blocks = [('Sequential', 'sequential'), ('Random', 'fullRandom')]
if COUNTERBALANCE:
    try:
        if int(expInfo['participant']) % 2 == 0:
            blocks.reverse()
    except ValueError:
        pass  # non-numeric participant ID: keep Sequential first

# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------
show_message(
    "Place the fingers of your left and right hands on the keys Z, X, C and V.\n\n"
    "You will see four vertical lines. Each line matches one key:\n"
    "1st line = Z    2nd line = X    3rd line = C    4th line = V\n\n"
    "A small triangle will appear above one of the lines. "
    "Press the matching key as QUICKLY and ACCURATELY as you can.\n\n"
    "Press SPACE to begin.")

for i, (block_name, loop_type) in enumerate(blocks, start=1):
    run_block(block_name, loop_type, i)
    if i < len(blocks):
        show_message("Take a short break.\n\nPress SPACE when you are ready to continue.")

show_message("Thank you! The experiment is complete.\n\nPress SPACE to exit.")
thisExp.saveAsWideText(filename + '.csv')
thisExp.abort()
win.close()
core.quit()