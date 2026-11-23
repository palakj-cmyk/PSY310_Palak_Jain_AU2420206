#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PSY310 - Visual Search Experiment (PsychoPy Coder version)

Task: find the upright letter T among rotated L distractors and click on it.
Set sizes: 5 or 10 distractors (balanced, random order).
Trials: 200 per participant (100 per set size).

Output (in a 'data' folder next to this script):
  - <participant>_VisualSearch_<date>.csv   -> trial-by-trial data (opens in Excel)
  - <participant>_VisualSearch_<date>_summary.txt -> mean RT (correct trials) per set size + slope

Press ESC at any time to quit (data collected so far is saved).
"""

from psychopy import visual, core, event, data, gui
import random
import math
import os

# ------------------------------------------------------------------
# SETTINGS (change these if your instructor asks for different values)
# ------------------------------------------------------------------
SET_SIZES = [5, 10]        # number of L distractors per trial
REPS_PER_SET_SIZE = 100    # 100 x 2 set sizes = 200 trials
FIX_DURATION = 0.5         # seconds the fixation cross is shown before each display
LETTER_HEIGHT = 0.06       # same size for target and distractors (height units)
MIN_DISTANCE = 0.09        # minimum gap between items so letters do not overlap
FIELD_X = 0.5              # items appear within x = -0.5..0.5
FIELD_Y = 0.45             # items appear within y = -0.45..0.45 (keeps letters on screen)

# ------------------------------------------------------------------
# PARTICIPANT INFO + DATA FILE
# ------------------------------------------------------------------
expName = 'VisualSearch'
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

# ------------------------------------------------------------------
# WINDOW, STIMULI, MOUSE
# ------------------------------------------------------------------
win = visual.Window(fullscr=True, color=[0, 0, 0], colorSpace='rgb',
                    units='height', allowGUI=False)

fixation = visual.ShapeStim(win, name='Fixation', vertices='cross',
                            size=(0.1, 0.1), pos=(0, 0),
                            lineColor='white', fillColor='white')

target = visual.TextStim(win, name='Target', text='T', font='Open Sans',
                         height=LETTER_HEIGHT, color='white')

# Pre-create the maximum number of distractors once (faster than making new ones every trial)
distractor_pool = [visual.TextStim(win, name='distr', text='L', font='Open Sans',
                                   height=LETTER_HEIGHT, color='white')
                   for _ in range(max(SET_SIZES))]

instructions = visual.TextStim(win, height=0.035, wrapWidth=1.2, color='white', text=(
    "In each trial you will first see a cross in the centre of the screen.\n\n"
    "Then several letters will appear. Your task is to find the letter T "
    "among the L's and CLICK on the T with the mouse.\n\n"
    "Please be as fast and as accurate as you can.\n\n"
    "Click the mouse to begin."))

thanks = visual.TextStim(win, height=0.04, color='white',
                         text="Thank you! The experiment is complete.\n\nClick to exit.")

mouse = event.Mouse(win=win, visible=True)
rt_clock = core.Clock()


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------
def check_quit():
    """ESC ends the experiment and saves what has been collected."""
    if event.getKeys(keyList=['escape']):
        thisExp.saveAsWideText(filename + '.csv')
        thisExp.abort()  # prevents a second, duplicate save
        win.close()
        core.quit()


def wait_for_release():
    """Wait until no mouse button is held, so one click is not counted twice."""
    while any(mouse.getPressed()):
        check_quit()
        core.wait(0.01)
    mouse.clickReset()


def wait_for_click(stim):
    stim.draw()
    win.flip()
    wait_for_release()
    while not any(mouse.getPressed()):
        check_quit()
        stim.draw()
        win.flip()
    wait_for_release()


def random_positions(n_items):
    """Random positions that do not overlap each other or the screen centre."""
    positions = []
    attempts = 0
    while len(positions) < n_items:
        attempts += 1
        p = (random.uniform(-FIELD_X, FIELD_X), random.uniform(-FIELD_Y, FIELD_Y))
        too_close = any(math.dist(p, q) < MIN_DISTANCE for q in positions)
        too_central = math.dist(p, (0, 0)) < MIN_DISTANCE
        if attempts > 5000 or not (too_close or too_central):
            positions.append(p)
    return positions


# ------------------------------------------------------------------
# INSTRUCTIONS
# ------------------------------------------------------------------
wait_for_click(instructions)

# ------------------------------------------------------------------
# TRIAL LOOP
# ------------------------------------------------------------------
conditions = [{'num_distr': n} for n in SET_SIZES]
trials = data.TrialHandler(trialList=conditions, nReps=REPS_PER_SET_SIZE,
                           method='random', name='Trials')
thisExp.addLoop(trials)

results = []  # (num_distr, rt, correct) for the summary at the end

for thisTrial in trials:
    num_distr = thisTrial['num_distr']

    # --- set up the display for this trial ---
    positions = random_positions(num_distr + 1)
    target.pos = positions[0]
    active_distractors = distractor_pool[:num_distr]
    for distr, pos in zip(active_distractors, positions[1:]):
        distr.pos = pos
        distr.ori = random.randint(1, 360)

    # --- fixation ---
    wait_for_release()
    fix_timer = core.CountdownTimer(FIX_DURATION)
    while fix_timer.getTime() > 0:
        check_quit()
        fixation.draw()
        win.flip()

    # --- search display: RT starts when the display appears on screen ---
    win.callOnFlip(rt_clock.reset)
    mouse.clickReset()
    while True:
        target.draw()
        for distr in active_distractors:
            distr.draw()
        win.flip()
        check_quit()
        if any(mouse.getPressed()):
            rt = rt_clock.getTime()
            correct = 1 if mouse.isPressedIn(target) else 0
            click_x, click_y = mouse.getPos()
            break

    win.flip()  # clear screen

    # --- save this trial ---
    trials.addData('set_size', num_distr)
    trials.addData('rt', rt)
    trials.addData('correct', correct)
    trials.addData('target_x', target.pos[0])
    trials.addData('target_y', target.pos[1])
    trials.addData('click_x', click_x)
    trials.addData('click_y', click_y)
    thisExp.nextEntry()

    results.append((num_distr, rt, correct))

# ------------------------------------------------------------------
# SUMMARY: mean RT of correct trials per set size + slope
# ------------------------------------------------------------------
lines = ['Participant: %s' % expInfo['participant'], '']
means = {}
for n in SET_SIZES:
    correct_rts = [rt for (s, rt, c) in results if s == n and c == 1]
    all_n = [1 for (s, rt, c) in results if s == n]
    if correct_rts:
        means[n] = sum(correct_rts) / len(correct_rts)
        lines.append('Set size %d: mean RT (correct) = %.1f ms, accuracy = %d/%d'
                     % (n, means[n] * 1000, len(correct_rts), len(all_n)))

if len(means) == 2:
    lo, hi = min(SET_SIZES), max(SET_SIZES)
    slope = (means[hi] - means[lo]) / (hi - lo) * 1000
    lines.append('')
    lines.append('Slope (RT x set size) = %.1f ms per item' % slope)

summary_text = '\n'.join(lines)
print(summary_text)
with open(filename + '_summary.txt', 'w') as f:
    f.write(summary_text)

# ------------------------------------------------------------------
# END
# ------------------------------------------------------------------
wait_for_click(thanks)
thisExp.saveAsWideText(filename + '.csv')
thisExp.abort()
win.close()
core.quit()