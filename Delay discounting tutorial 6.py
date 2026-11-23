#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PSY310 - Delay Discounting Experiment (PsychoPy Coder version)

Each trial:
  1. Fixation cross (0.05 x 0.05) for 1 s.
  2. A choice appears, e.g. "GBP 11 today or GBP 30 after 7 days".
  3. The participant presses T (take the reward TODAY) or L (wait for the LATER reward).

The 7 choices come from conditions.csv (put it in the same folder as this script).
They are shown in random order, repeated N_REPS times.

Output (in a 'data' folder next to this script):
  <participant>_DelayDiscounting_<date>.csv          -> every choice
  <participant>_DelayDiscounting_<date>_summary.txt  -> estimated k (discounting value)

Press ESC at any time to quit (data collected so far is saved).
"""

import os
import math
from psychopy import visual, core, event, data, gui

# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------
CURRENCY = 'GBP'   # the tutorial allows rupees instead, e.g. 'Rs.'
N_REPS = 15        # 7 choices x 15 = 105 trials (about 100 per participant, as the guide asks).
                   # 7 x 14 = 98 if you need to stay under 100.

# ------------------------------------------------------------------
# PARTICIPANT INFO + DATA FILE
# ------------------------------------------------------------------
expName = 'DelayDiscounting'
expInfo = {'participant': '', 'session': '001'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if not dlg.OK:
    core.quit()
expInfo['date'] = data.getDateStr()
expInfo['expName'] = expName

thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(thisDir)
conditions_path = os.path.join(thisDir, 'conditions.csv')
if os.path.exists(conditions_path):
    conditions = data.importConditions(conditions_path)
else:
    # the same 7 choices as conditions.csv, used if the file is missing
    print('conditions.csv not found - using the built-in conditions')
    conditions = [{'reward_today': a, 'future_reward': b, 'delay': d}
                  for a, b, d in ((11, 30, 7), (15, 35, 13), (27, 50, 21), (40, 55, 62),
                                  (49, 60, 89), (67, 75, 119), (78, 80, 162))]

os.makedirs(os.path.join(thisDir, 'data'), exist_ok=True)
filename = os.path.join(thisDir, 'data',
                        '%s_%s_%s' % (expInfo['participant'], expName, expInfo['date']))
thisExp = data.ExperimentHandler(name=expName, extraInfo=expInfo,
                                 dataFileName=filename,
                                 savePickle=False, saveWideText=True)

# ------------------------------------------------------------------
# WINDOW + STIMULI
# ------------------------------------------------------------------
win = visual.Window(fullscr=True, color=[0, 0, 0], colorSpace='rgb',
                    units='height', allowGUI=False)
Fixation = visual.ShapeStim(win, name='Fixation', vertices='cross', size=(0.05, 0.05),
                            pos=(0, 0), fillColor='white', lineColor='white')
text = visual.TextStim(win, name='text', height=0.05, wrapWidth=1.4, color='white', pos=(0, 0))
reminder = visual.TextStim(win, height=0.03, color='white', pos=(0, -0.3),
                           text='Press T for the reward TODAY      Press L for the LATER reward')
message = visual.TextStim(win, height=0.035, wrapWidth=1.3, color='white')
clock = core.Clock()


def quit_and_save():
    thisExp.saveAsWideText(filename + '.csv')
    thisExp.abort()  # prevents a second, duplicate save
    win.close()
    core.quit()


def show_message(msg):
    message.text = msg
    message.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        quit_and_save()


def item_k(today, future, delay):
    """k at which both options are worth the same: future / (1 + k*delay) = today."""
    return (future / today - 1) / delay


# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------
show_message(
    "In each trial you will choose between two amounts of money:\n"
    "a smaller amount you get TODAY, or a larger amount you get LATER.\n\n"
    "Press T to take the money today.\nPress L to wait for the later amount.\n\n"
    "There are no right or wrong answers - choose what you would really prefer.\n\n"
    "Press SPACE to begin.")

trials = data.TrialHandler(trialList=conditions, nReps=N_REPS, method='random', name='trials')
thisExp.addLoop(trials)
choices = []
for thisTrial in trials:
    today = thisTrial['reward_today']
    future = thisTrial['future_reward']
    delay = thisTrial['delay']
    text.text = (CURRENCY + " " + str(today) + " today" + " or" + " " + CURRENCY + " "
                 + str(future) + " after " + str(delay) + " days")

    # fixation 0-1 s
    clock.reset()
    while clock.getTime() < 1.0:
        Fixation.draw()
        win.flip()
        if event.getKeys(['escape']):
            quit_and_save()

    # choice from 1 s until T or L is pressed
    text.draw()
    reminder.draw()
    win.callOnFlip(clock.reset)
    win.callOnFlip(event.clearEvents)
    win.flip()
    while True:
        keys = event.getKeys(keyList=['t', 'l', 'escape'], timeStamped=clock)
        if keys:
            key, rt = keys[0]
            if key == 'escape':
                quit_and_save()
            break
        text.draw()
        reminder.draw()
        win.flip()

    k_item = item_k(today, future, delay)
    trials.addData('key_resp.keys', key)
    trials.addData('key_resp.rt', rt)
    trials.addData('choice', 'today' if key == 't' else 'later')
    trials.addData('chose_later', 1 if key == 'l' else 0)
    trials.addData('k_indifference', k_item)
    thisExp.nextEntry()
    choices.append((k_item, 1 if key == 'l' else 0))

# ------------------------------------------------------------------
# ESTIMATED DISCOUNTING VALUE (k), Kirby-style consistency scoring
# ------------------------------------------------------------------
# Someone with discount rate k should choose LATER when an item's k is larger
# than their own k, and TODAY when it is smaller. The candidate k values are the
# geometric means of neighbouring item k values (plus the two ends). The estimate
# is the candidate that agrees with the most choices; ties are combined by their
# geometric mean.
item_ks = sorted({k for k, _ in choices})
candidates = [item_ks[0] / 2]
candidates += [math.sqrt(a * b) for a, b in zip(item_ks, item_ks[1:])]
candidates += [item_ks[-1] * 2]


def consistency(kc):
    return sum(1 for k, later in choices if (later == 1) == (k > kc)) / len(choices)


scores = [(consistency(kc), kc) for kc in candidates]
best = max(s for s, _ in scores)
tied = [kc for s, kc in scores if s == best]
k_est = math.exp(sum(math.log(kc) for kc in tied) / len(tied))

lines = ['Participant: %s' % expInfo['participant'], '',
         'Item k      Proportion of LATER choices']
for k in sorted(item_ks, reverse=True):
    later = [c for kk, c in choices if kk == k]
    lines.append('%-10.5f  %.2f  (%d of %d)' % (k, sum(later) / len(later), sum(later), len(later)))
lines += ['', 'Estimated discounting value k = %.5f' % k_est,
          'ln(k) = %.2f' % math.log(k_est),
          'Consistency of choices with this k = %.0f%%' % (best * 100)]
if best < 0.75:
    lines.append('Note: consistency below 75% - choices were not very consistent.')
summary = '\n'.join(lines)
print(summary)
with open(filename + '_summary.txt', 'w') as f:
    f.write(summary)

show_message("Thank you! The experiment is complete.\n\nPress SPACE to exit.")
thisExp.saveAsWideText(filename + '.csv')
thisExp.abort()
win.close()
core.quit()