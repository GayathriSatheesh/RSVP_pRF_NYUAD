#Add in code snippet in beginning of experiment 
##########Before experiment##################################           
from pypixxlib.propixx import PROPixxCTRL

triggerkey='q' # to quit when waiting for trigger, then on its esc
skiptrig='s'
datapixx=False #set to 1 to test in scanner 
scanner=False #set to 1 to test in scanner with trigger
samekey=20 # red button 
diffkey=18 # green button 

###########Start experiment################################
kb= keyboard.Keyboard()
Trigtext = visual.TextStim(win=win, name='text',
    text='waiting for trigger',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);

if  scanner or datapixx==True: 
    my_device = PROPixxCTRL()
    din_state = my_device.din.getValue()
    trig=bin(din_state)[15] 

conRoutine = True
while conRoutine:
     Trigtext.setAutoDraw(True)
     win.flip()
     key=kb.getKeys()
     for thiskey in key:
         if thiskey==triggerkey:
            print('keyboard trigger using:', triggerkey)
            conRoutine = False
            core.quit()
     if  scanner ==False: 
         for thiskey in key:
            if thiskey==skiptrig:
                print('keyboard trigger using:', skiptrig)
                Trigtext.setAutoDraw(False)
                conRoutine = False
     else:
         old_state = din_state
         trig_old=bin(old_state)[15]
         my_device.updateRegisterCache()
         din_state = my_device.din.getValue()
         trig=bin(din_state)[15]
         if (trig_old) is not (trig):
             print('triggered!')
             conRoutine = False
             Trigtext.setAutoDraw(False)
         else:
             print('waiting for trigger')
###########BUTTON PRESSES#################################
# Scroll to key press part of code and look for section that 
#says  if {key_resp}.status == STARTED and not waitOnFlip:
#add
            if datapixx==False:
# After  key_resp.rt = _key_resp_allKeys[-1].rt
#add 
            else:
                 my_device.updateRegisterCache()
                 din_state = my_device.din.getValue()
                 if bin(din_state)[samekey]=='1':
                    _key_resp_allKeys.append('1')
                 if bin(din_state)[diffkey]=='1':
                    _key_resp_allKeys.append('2')
                 if len(_key_resp_allKeys):
                     key_resp.keys = _key_resp_allKeys[-1] 
# make sure if ({key_resp}.keys == str('1')) or ({key_resp}.keys == '1'): is inline with
# if datapixx==False 
# makie sure key_resp.keys, _key_resp._allKeys are named the same as they are defined
# at the start of the routine