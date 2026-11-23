#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PSY310 - Word Priming Experiment (PsychoPy Coder version)

Routine 1 - Study phase (study_conditions.csv, random order, 15 words)
    Each word is shown for 8 s with a 1-5 slider (Familiar ... Unfamiliar).
    The participant rates the word to move on.

Routine 2 - Test phase (test_conditions.csv, random order, 20 word fragments)
    Each fragment (e.g. l_pt_p) is shown for 10 s. The participant types the
    whole word in the box and clicks "Click to Submit".
    15 fragments are of studied words (old = primed), 5 are of new words
    (new = non-primed).

Put study_conditions.csv and test_conditions.csv in the same folder as this script.

Output (in a 'data' folder next to this script):
  <participant>_WordPriming_<date>.csv          -> every rating and every answer
  <participant>_WordPriming_<date>_summary.txt  -> proportions and priming score

Press ESC at any time to quit (data collected so far is saved).
"""

import os
import re
from psychopy import visual, core, event, data, gui

STUDY_DURATION = 8.0    # seconds the study word is shown
TEST_DURATION = 10.0    # seconds the word fragment is shown

# ------------------------------------------------------------------
# PARTICIPANT INFO + DATA FILE
# ------------------------------------------------------------------
expName = 'WordPriming'
expInfo = {'participant': '', 'session': '001'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if not dlg.OK:
    core.quit()
expInfo['date'] = data.getDateStr()
expInfo['expName'] = expName

thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(thisDir)
for name in ('study_conditions.csv', 'test_conditions.csv'):
    if not os.path.exists(os.path.join(thisDir, name)):
        msg = gui.Dlg(title='Conditions file not found')
        msg.addText('Could not find %s' % name)
        msg.addText('Put it in the same folder as this script: %s' % thisDir)
        msg.show()
        core.quit()

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
                    units='height', allowGUI=True)
mouse = event.Mouse(win=win, visible=True)

message = visual.TextStim(win, height=0.035, wrapWidth=1.3, color='white')

# Study phase
StudyText = visual.TextStim(win, height=0.08, color='white', pos=(0, 0.1))
Studyslider = visual.Slider(win, ticks=(1, 2, 3, 4, 5), labels=['Familiar', 'Unfamiliar'],
                            pos=(0, -0.3), size=(1.0, 0.05), granularity=1,
                            style='rating', color='white', fillColor='red',
                            borderColor='white', labelHeight=0.035)

# Test phase
TestText = visual.TextStim(win, height=0.08, color='white', pos=(0, 0.2))
test_textbox = visual.TextBox2(win, text='', placeholder='Type the whole word here...',
                               font='Arial', letterHeight=0.05, pos=(0, 0),
                               size=(0.7, 0.1), color='white', borderColor='white',
                               fillColor=None, editable=True, alignment='center')
submit_text = visual.TextStim(win, text='Click to Submit', height=0.045,
                              pos=(0, -0.3), color='white')
submit_box = visual.Rect(win, width=0.4, height=0.09, pos=(0, -0.3),
                         lineColor='white', fillColor=None)

clock = core.Clock()


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------
def quit_and_save():
    thisExp.saveAsWideText(filename + '.csv')
    thisExp.abort()  # prevents a second, duplicate save
    win.close()
    core.quit()


def show_message(text):
    message.text = text
    message.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        quit_and_save()


def clean(word):
    """Compare answers on letters only, ignoring case, spaces and hyphens (T-shirt = Tshirt)."""
    return re.sub(r'[^a-z]', '', str(word).lower())


def wait_for_mouse_release():
    while any(mouse.getPressed()):
        core.wait(0.01)


# ------------------------------------------------------------------
# ROUTINE 1: STUDY PHASE
# ------------------------------------------------------------------
show_message(
    "STUDY PHASE\n\n"
    "You will see a series of words, one at a time.\n"
    "Read each word carefully and rate how familiar it is to you "
    "by clicking on the scale (1 = Familiar, 5 = Unfamiliar).\n\n"
    "Press SPACE to begin.")

study = data.TrialHandler(trialList=data.importConditions('study_conditions.csv'),
                          nReps=1, method='random', name='trials')
thisExp.addLoop(study)
for thisTrial in study:
    StudyText.text = thisTrial['Study_word']
    Studyslider.reset()
    wait_for_mouse_release()
    event.clearEvents()
    clock.reset()
    while Studyslider.getRating() is None:
        if clock.getTime() < STUDY_DURATION:
            StudyText.draw()
        Studyslider.draw()
        win.flip()
        if event.getKeys(['escape']):
            quit_and_save()
    study.addData('phase', 'study')
    study.addData('Studyslider.response', Studyslider.getRating())
    study.addData('Studyslider.rt', Studyslider.getRT())
    thisExp.nextEntry()

# ------------------------------------------------------------------
# ROUTINE 2: TEST PHASE
# ------------------------------------------------------------------
show_message(
    "TEST PHASE\n\n"
    "Now you will see words with some letters missing, for example  l_pt_p.\n"
    "Type the first complete word that comes to mind in the box, "
    "then click 'Click to Submit'.\n\n"
    "If you cannot think of a word, make your best guess.\n\n"
    "Press SPACE to begin.")

test = data.TrialHandler(trialList=data.importConditions('test_conditions.csv'),
                         nReps=1, method='random', name='trials_2')
thisExp.addLoop(test)
results = []
for thisTrial in test:
    TestText.text = thisTrial['test_word']
    test_textbox.reset()
    test_textbox.text = ''
    test_textbox.hasFocus = True
    wait_for_mouse_release()
    event.clearEvents()
    clock.reset()
    while True:
        if clock.getTime() < TEST_DURATION:
            TestText.draw()
        test_textbox.draw()
        submit_box.draw()
        submit_text.draw()
        win.flip()
        if event.getKeys(['escape']):
            quit_and_save()
        if mouse.isPressedIn(submit_box):
            rt = clock.getTime()
            break
    answer = test_textbox.text.strip()
    correct = 1 if clean(answer) == clean(thisTrial['Reference']) else 0
    test.addData('phase', 'test')
    test.addData('test_textbox.text', answer)
    test.addData('correct', correct)
    test.addData('submit.rt', rt)
    thisExp.nextEntry()
    results.append((thisTrial['old_new'], correct))

# ------------------------------------------------------------------
# PRIMING SCORE
# ------------------------------------------------------------------
lines = ['Participant: %s' % expInfo['participant'], '']
props = {}
for kind, label in (('old', 'Primed (old) words'), ('new', 'Non-primed (new) words')):
    scores = [c for k, c in results if k == kind]
    props[kind] = sum(scores) / len(scores) if scores else 0
    lines.append('%s: %d of %d completed correctly = %.2f'
                 % (label, sum(scores), len(scores), props[kind]))
lines.append('')
lines.append('Priming score = proportion primed - proportion non-primed = %.2f'
             % (props['old'] - props['new']))
summary = '\n'.join(lines)
print(summary)
with open(filename + '_summary.txt', 'w') as f:
    f.write(summary)

show_message("Thank you! The experiment is complete.\n\nPress SPACE to exit.")
thisExp.saveAsWideText(filename + '.csv')
thisExp.abort()
win.close()
core.quit()