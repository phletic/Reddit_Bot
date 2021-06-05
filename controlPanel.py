import tkinter as tk
from tkinter import font as tkfont
from tkinter.constants import S
import redditBot
import json
import threading
import submissionCollector
import time
import credibilityChecker


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.Bot = None
        self.title_font = tkfont.Font(
            family='Helvetica', size=35, weight="bold", slant="roman")
        self.subtitle_font = tkfont.Font(
            family='Helvetica', size=20, weight="bold")
        self.normal_font = tkfont.Font(family='Helvetica', size=15)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LogInPage, LogIn, MainWindow):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame("LogInPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        self.title(page_name)
        frame = self.frames[page_name]
        frame.on_activated()
        frame.tkraise()


class window(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def on_activated(self):
        pass


class LogInPage(window):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

    def on_activated(self):
        self.welcome_label = tk.Label(
            self, text="ASR_SG Reddit Bot Control Panel Log In Page", font=self.controller.title_font)
        self.welcome_label.grid(
            column=0, row=0, ipady=10, ipadx=100, sticky="N")
        self.log_in_button = tk.Button(
            self, text="Log in", font=self.controller.normal_font, command=lambda: self.controller.show_frame("LogIn"))
        self.log_in_button.grid(column=0, row=1, ipady=10, ipadx=100)


class LogIn(window):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

    def Loading(self):
        text = self.loadingText
        delta = 500
        delay = 0
        count = 0
        while count < 100:
            for i in range(len(text) + 1):
                self.canvas.after(delay, lambda s=text[:i]: self.canvas.itemconfigure(
                    self.canvas_text, text=s))
                delay += delta
            count += 1
        return 0

    def on_activated(self):
        self.canvas = tk.Canvas(self)
        self.canvas.grid()
        self.canvas_text = self.canvas.create_text(
            10, 10, text='', anchor=tk.NW, font=self.controller.title_font)
        self.loadingText = "Loading..."
        self.loadingThread = threading.Thread(
            target=self.Loading, args=(), daemon=True)
        self.loadingThread.start()
        loggingThread = threading.Thread(target=self.log, args=(), daemon=True)
        loggingThread.start()

    def log(self):
        time.sleep(2)
        # get authentication details
        with open("authentication.json") as read_file:
            data_dict = json.loads(read_file.read())
        # create bot
        print("logged in")
        self.controller.Bot = redditBot.reddit_bot(data_dict, False, "ASR_SG")
        submissionCollector.updateEntires(self.controller.Bot)
        print("done")
        self.canvas.delete("all")
        self.controller.show_frame("MainWindow")  # continue from here
        return


class MainWindow(window):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

    def on_activated(self):
        self.Title = tk.Label(
            self, text="ASR_SG Reddit Bot Control Panel", font=self.controller.title_font)
        self.Title.grid(column=0, row=0, ipady=10, ipadx=100, sticky="N")
        self.updateDateBase = Command(self, controller=self.controller, commandText="Update Database",
                                      Bot=self.controller.Bot, function=submissionCollector.updateEntires,)
        self.updateDateBase.grid(column=0, row=1, ipadx=150)
        self.checkCredible = Command(self, controller=self.controller, commandText="checkCredible",
                                     Bot=self.controller.Bot, function=credibilityChecker.checkCredible)
        self.checkCredible.grid(column=0, row=10, ipadx=170)


class Command(tk.Frame):
    def __init__(self, parent, controller, commandText, Bot, function):
        self.Bot = Bot
        self.function = function
        self.time_interval = tk.IntVar()
        self.thread = threading.Thread(target=self.function)
        tk.Frame.__init__(self, parent, borderwidth=10, relief="groove")
        self.controller = controller
        self.Title = tk.Label(self, text=commandText,
                              font=self.controller.subtitle_font)
        self.Title.grid(column=0, row=0)
        self.Activity = tk.Label(
            self, text="", font=self.controller.subtitle_font)
        self.Activity.grid(column=1, row=0)
        self.start_button = tk.Button(
            self, text="Start once", font=self.controller.normal_font, command=self.action)
        self.start_button.grid(column=0, row=1,)
        self.start_repeatedly_button = tk.Button(
            self, text="Start repeatedly", font=self.controller.normal_font, command=self.RepeatedAction)
        self.start_repeatedly_button.grid(column=1, row=1)
        self.interval_des = tk.Label(
            self, font=self.controller.normal_font, text="interval per repeat")
        self.interval_des.grid(column=3, row=1, ipadx=50)
        self.interval = tk.Entry(
            self, font=self.controller.normal_font, textvariable=self.time_interval)
        self.interval.grid(column=4, row=1, ipadx=50)
        self.stop_repeating = tk.Button(
            self, text="Stop repeating", font=self.controller.normal_font, command=self.setStopRepeating)
        self.stop_repeating.grid(column=5, row=1)
        self.isActive = False
        self.isStopRepeating = False
        self.set_inactive()

    def setStopRepeating(self):
        self.isStopRepeating = True

    def set_active(self):
        self.isActive = True
        self.Activity.configure(text="Active", bg="green")
        self.start_button.configure(state="disabled")
        self.start_repeatedly_button.configure(state="disabled")

    def set_inactive(self):
        self.isActive = False
        self.Activity.configure(text="Inactive", bg="red")
        self.start_button.configure(state="normal")
        self.start_repeatedly_button.configure(state="normal")

    def action(self):
        self.run()
        self.after(1000, self.threadActive)

    def RepeatedAction(self):
        self.run()
        self.set_active()
        self.after(500, self.repeatedThreadActive)
        self.after(500, self.shouldRepeat)

    def shouldRepeat(self):
        if self.isActive == True:
            self.after(500, self.shouldRepeat)
        else:
            if self.isStopRepeating == True:
                self.set_inactive()
                return
            else:
                self.after(self.time_interval.get() *
                           1000*60, self.RepeatedAction)

    def run(self):
        self.thread = threading.Thread(target=self.function, args=(self.Bot,))
        self.thread.start()

    def repeatedThreadActive(self):
        if self.thread.is_alive():
            self.isActive = True
            self.after(1000, self.repeatedThreadActive)
        else:
            self.isActive = False

    def threadActive(self):
        if self.thread.is_alive():
            self.set_active()
            self.after(1000, self.threadActive)
        else:
            self.set_inactive()


if __name__ == "__main__":
    app = App()
    app.mainloop()
