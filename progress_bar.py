from tkinter import ttk
from tkinter import *

class ProgressBarPanel():
    def __init__(self, parent_conainer) -> None:
        self.win = Toplevel(parent_conainer,
                       padx=20, pady=20)  # new window
        self.win.pack_propagate(0)
        self.win.title('CSV Instrument Dump')  # set border
        self.win.config()
        frame_setup = Frame(self.win,height=20)

        self.pb = ttk.Progressbar(
            frame_setup,
            orient='horizontal',
            mode='indeterminate',
            length=280,
            
        )
        frame_setup.pack(fill=BOTH,side=TOP)
        self.pb.pack(side=LEFT, fill=BOTH)
    def start_progress(self):
        self.pb.start(10)
    def stop_progress(self):
        self.pb.stop()
    def remove_bar(self):
        self.pb.destroy()
        self.win.destroy()