from state import State
import threading


class Unknown(State):
    def on_event(self, event):
        if event == 'off':
            return Off()
        elif event == 'on':
            return On()
        return self


class On(State):
    def __on_entry__(self):
        pass

    def on_event(self, event):
        if event == 'off':
            return Off()
        elif event == 'brightness_move_up':
            return HoldIncrement()
        elif event == 'brightness_move_down':
            return HoldDecrement()
        return self


class Off(State):
    def __on_entry__(self):
        sendOffCommand()

    def on_event(self, event):
        if event == 'on':
            sendApiCommand('PL=1')
            return On()
        elif event == 'brightness_move_up':
            sendApiCommand('PL=1&A=1')
            return HoldIncrement()
        return self


class DeIncrement(State):
    def __on_entry__(self):
        self.do_run = True
        self.n_runs = 0
        self.thread = threading.Thread(target=self.thread_inc)
        self.thread.start()

    def on_event(self, event):
        if event == 'brightness_stop':
            self.do_run = False
            self.thread.join()
            return On()
        return self

    def thread_inc(self):
        if self.do_run and self.n_runs < 30:
            threading.Timer(0.15, self.thread_inc).start()
            sendIncrementCommand(self.inc_multiplier * min(self.n_runs + 1, 5))
            self.n_runs += 1


class HoldIncrement(DeIncrement):
    def __on_entry__(self):
        self.inc_multiplier = 2
        DeIncrement.__on_entry__(self)


class HoldDecrement(DeIncrement):
    def __on_entry__(self):
        self.inc_multiplier = -2
        DeIncrement.__on_entry__(self)



class SwitchStateMachine(object):
    def __init__(self):
        # Start with a default state.
        self.state = Unknown()


    def on_event(self, event):
        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)


if __name__ == "__main__":
    import time
    from mockCmd import *

    eventList = ['off', 'on', '', '', 'brightness_move_up', '', '', 'brightness_stop', 'off', 'off', 'off', 'on',
                 'brightness_move_down', '', 'brightness_stop', 'on', 'off', 'on', 'giberish']

    sm = SwitchStateMachine()
    for ev in eventList:
        sm.on_event(ev)
        time.sleep(0.5)
