from state import State

import threading

class unknown(State):
    def on_event(self, event):
        if event == 'off' or event == 'single':
            return off()
        elif event == 'double':
            return double()
        elif event == 'hold':
            return pressed()
        return self

class on(State):
    def __on_entry__(self):
        sendOnCommand()

    def on_event(self, event):
        if event == 'off' or event == 'single':
            return off()
        elif event == 'double':
            return double()
        elif event == 'hold':
            return pressed()
        return self

class off(State):
    def __on_entry__(self):
        sendOffCommand()

    def on_event(self, event):
        if event == 'on':
            return on()
        elif event == 'single':
            sendApiCommand('PL=3&A=250')
            return on()
        elif event == 'double':
            return double()
        elif event == 'hold':
            return pressed()
        return self

class pressed(State):
    def __on_entry__(self):
        self.do_run = True
        self.n_runs = 0
        self.thread = threading.Thread(target=self.thread_inc)
        self.thread.start()

    def on_event(self, event):
        if event == 'release':
            self.do_run = False
            self.thread.join()
            return on()
        return self

    def thread_inc(self):
        if self.do_run and self.n_runs < 30:
            threading.Timer(0.15, self.thread_inc).start()
            sendIncrementCommand(min(self.n_runs + 1, 5))
            self.n_runs += 1

class double(State):
    def __on_entry__(self):
        sendApiCommand('PL=1')

    def on_event(self, event):
        if event == 'off' or event == 'single':
           return off()
        elif event == 'double':
           sendApiCommand('PL=2')
        elif event == 'hold':
           return pressed()
        return self

#    def thread_inc(self):
#        if self.do_run and self.n_runs < 30:
#            threading.Timer(0.15, self.thread_inc).start()
#            sendIncrementCommand(min(self.n_runs + 1, 5))
#            self.n_runs += 1


class SwithStateMachine(object):
    def __init__(self):
        # Start with a default state.
        self.state = unknown()

    def on_event(self, event):
        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)

if __name__ == "__main__":
	import time
	from mock_cmd import *

	eventList = ['single', 'hold', '', '', 'release', 'single', 'single', 'hold', 'release', 'single', 'hold', '', 'release', 'single', 'single', 'hold', 'release', 'single', 'off', 'on', 'on', 'on', 'giberish']
	sm = SwithStateMachine()
	for ev in eventList:
		sm.on_event(ev)
		time.sleep(0.5)

