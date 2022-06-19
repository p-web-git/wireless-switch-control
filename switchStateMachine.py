from state import State

import threading


class unknown(State):
    def on_event(self, event):
        if event == 'off':
            return off()
        return self


class on(State):
    def __on_entry__(self):
        sendOnCommand()

    def on_event(self, event):
        if event == 'off':
            return off()
        elif event == 'brightness_move_up':
            return pressed()
        return self


class off(State):
    def __on_entry__(self):
        sendOffCommand()

    def on_event(self, event):
        if event == 'on':
            sendApiCommand('PL=1&A=250')
            return on()
        elif event == 'brightness_move_up':
            return pressed()
        return self


class pressed(State):
    def __on_entry__(self):
        self.do_run = True
        self.n_runs = 0
        self.thread = threading.Thread(target=self.thread_inc)
        self.thread.start()

    def on_event(self, event):
        if event == 'brightness_stop':
            self.do_run = False
            self.thread.join()
            return on()
        return self

    def thread_inc(self):
        if self.do_run and self.n_runs < 30:
            threading.Timer(0.15, self.thread_inc).start()
            sendIncrementCommand(min(self.n_runs + 1, 5))
            self.n_runs += 1


class SwitchStateMachine(object):
    def __init__(self):
        # Start with a default state.
        self.state = unknown()

    def on_event(self, event):
        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)


if __name__ == "__main__":
    import time
    from mockCmd import *

    eventList = ['off', 'on', '', '', 'brightness_move_up', '', '', 'brightness_stop', 'off', 'off', 'off', 'on']
               #  'release', 'single', 'single', 'hold', 'release', 'single', 'off', 'on', 'on', 'on', 'giberish']
    sm = SwitchStateMachine()
    for ev in eventList:
        sm.on_event(ev)
        time.sleep(0.5)
