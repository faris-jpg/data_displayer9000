from tkinter import *
from tkinter.ttk import *
from copy import deepcopy
from prettytable import PrettyTable
from math import floor

class Process:
    def __init__(self, name, arrival_time, burst_time, priority):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.executed_before = False
        self.finishing_time = 0
        self.postprocess_arrival_time = arrival_time

def data_displayer9000(method, processes, timeline):
    table = PrettyTable()
    table.field_names = ["Process", "Arrival Time", "Burst Time", "Finishing Time", "Turnaround Time", "Waiting Time"]

    for process in processes:
        table.add_row([
            process.name,
            process.arrival_time, 
            process.burst_time, 
            process.finishing_time, 
            process.finishing_time - process.arrival_time, 
            (process.finishing_time - process.arrival_time) - process.burst_time
        ])

    gantt_chart = [f"{process[0]}({process[1]}-{process[2]})" for process in timeline]
    gantt_chart_str = " -> ".join(gantt_chart)

    result_text.insert(END, f"{method}\n")
    result_text.insert(END, table.get_string())
    result_text.insert(END, "\n")
    result_text.insert(END, f"{timeline}\n\n")
    result_text.insert(END, "\nGantt Chart:\n")
    result_text.insert(END, gantt_chart_str)
    result_text.insert(END, "\n\n")

def plot_gantt_chart(timeline):
    windowSize = 270 #SET WINDOW SIZE HERE (if no global)
    timeEnd = timeline[-1][2] 
    timediv = floor(windowSize / timeEnd - 2) #finds the floor of each timedivision (how many char per second)
    
    #gets the output for all the process names
    nameOutput = ''
    for task in timeline:
        duration = task[2] - task[1]
        nameOutput += task[0].ljust(timediv * duration, ' ') + '|'

    #gets output for all the seconds
    timeOutput = '|'
    for task in timeline:
        duration = task[2] - task[1]
        timeOutput += str(task[1]).ljust( timediv * duration, ' ') + '|'
    timeOutput += str(timeEnd)

    #outputs the table with borders
    border = '+' + ''.join('-' for x in range(len(timeOutput) - 1)) + '+'
    print(border)
    print('|' + nameOutput)
    print(timeOutput)
    print(border)

def remove_duplicates(timeline):
    updated_timeline = []  # new list for new timeline
    i = 0  #iterator

    while i < len(timeline):
        current_process = timeline[i]
        end_time = current_process[2] 

        #checks next process if it is the same id
        while i + 1 < len(timeline) and current_process[0] == timeline[i + 1][0]:
            end_time = timeline[i + 1][2]  #update end time
            i += 1

        updated_timeline.append((current_process[0], current_process[1], end_time)) #appends
        i += 1

    return(updated_timeline)

def round_robin(processes):
    quantum = 3
    processes_copy = deepcopy(processes)
    ready_queue = processes_copy.copy()
    timeline = []
    current_time = 0

    while ready_queue:
        ready_queue.sort(key=lambda x: (x.postprocess_arrival_time, x.priority, x.executed_before))

        current_process = ready_queue.pop(0)
        execution_time = min(quantum, current_process.remaining_time)
        current_process.remaining_time -= execution_time
        timeline.append((current_process.name, current_time, current_time + execution_time))
        current_time += execution_time
        current_process.postprocess_arrival_time = current_time

        if current_process.remaining_time > 0:
            ready_queue.append(current_process)
            current_process.executed_before = True
        else:
            current_process.finishing_time = current_time

    data_displayer9000("Round Robin", processes_copy, timeline)

def non_preemp_sjf(processes):
    processes_copy = deepcopy(processes)
    ready_queue = processes_copy.copy()
    timeline = []
    current_time = 0
    ready_queue.sort(key=lambda x: (x.burst_time, x.priority, x.arrival_time))

    while ready_queue:
        for i in range(len(ready_queue)):
            if ready_queue[i].arrival_time <= current_time:
                current_process = ready_queue.pop(i)
                break

        timeline.append((current_process.name, current_time, current_time + current_process.remaining_time))
        current_time += current_process.remaining_time
        current_process.finishing_time = current_time
        current_process.remaining_time = 0

    data_displayer9000("Non Preemptive SJF", processes_copy, timeline)

def non_preemp_prio(processes):
    processes_copy = deepcopy(processes)
    ready_queue = processes_copy.copy()
    timeline = []
    current_time = 0
    ready_queue.sort(key=lambda x: (x.priority, x.arrival_time))

    while ready_queue:
        for i in range(len(ready_queue)):
            if ready_queue[i].arrival_time <= current_time:
                current_process = ready_queue.pop(i)
                break

        timeline.append((current_process.name, current_time, current_time + current_process.remaining_time))
        current_time += current_process.remaining_time
        current_process.finishing_time = current_time
        current_process.remaining_time = 0

    data_displayer9000("Non Preemptive Priority", processes_copy, timeline)

def preemp_sjk(processes):
    processes_copy = deepcopy(processes)
    ready_queue = processes_copy.copy()
    timeline = []
    current_time = 0

    while ready_queue:
        ready_queue.sort(key=lambda x: (x.remaining_time, x.priority, x.postprocess_arrival_time))
        for i in range(len(ready_queue)):
            if ready_queue[i].arrival_time <= current_time:
                current_process = ready_queue[i]
                index = i
                break

        timeline.append((current_process.name, current_time, current_time + 1))
        current_time += 1
        current_process.remaining_time -= 1
        current_process.postprocess_arrival_time = current_time

        if current_process.remaining_time == 0:
            current_process.finishing_time = current_time
            ready_queue.pop(index)

    data_displayer9000("Preemptive SJF", processes_copy, timeline)

def preemp_prio(processes):
    processes_copy = deepcopy(processes)
    ready_queue = processes_copy.copy()
    timeline = []
    current_time = 0
    current_process = None

    while ready_queue:
        ready_queue.sort(key=lambda x: (x.priority, x.postprocess_arrival_time))
        index = None
        for i in range(len(ready_queue)):
            if current_process != None and ready_queue[i].name == current_process.name:
                index = i
                break

            if ready_queue[i].arrival_time <= current_time and (
                    current_process is None or current_process.priority != ready_queue[i].priority):
                current_process = ready_queue[i]
                index = i
                break

        if index is None:
            current_time += 1
            continue

        timeline.append((current_process.name, current_time, current_time + 1))
        current_time += 1
        current_process.remaining_time -= 1
        current_process.postprocess_arrival_time = current_time

        if current_process.remaining_time == 0:
            current_process.finishing_time = current_time
            ready_queue.pop(index)
            current_process = None

    data_displayer9000("Preemptive Prio", processes_copy, timeline)

def display_round_robin():
    result_text.delete(1.0, END)
    round_robin(processes)

def display_non_preemp_sjf():
    result_text.delete(1.0, END)
    non_preemp_sjf(processes)

def display_non_preemp_prio():
    result_text.delete(1.0, END)
    non_preemp_prio(processes)

def display_preemp_sjk():
    result_text.delete(1.0, END)
    preemp_sjk(processes)

def display_preemp_prio():
    result_text.delete(1.0, END)
    preemp_prio(processes)

# processes
processes = [
    Process("P0", 0, 6, 3),
    Process("P1", 1, 4, 3),
    Process("P2", 5, 6, 1),
    Process("P3", 6, 6, 1),
    Process("P4", 7, 6, 5),
    Process("P5", 8, 6, 6)

]

# GUI setup
root = Tk()
root.title("OS Scheduling Simulator")

round_robin_button = Button(root, text="Round Robin", command=display_round_robin)
round_robin_button.pack()

non_preemp_sjf_button = Button(root, text="Non Preemptive SJF", command=display_non_preemp_sjf)
non_preemp_sjf_button.pack()

non_preemp_prio_button = Button(root, text="Non Preemptive Priority", command=display_non_preemp_prio)
non_preemp_prio_button.pack()

preemp_sjk_button = Button(root, text="Preemptive SJF", command=display_preemp_sjk)
preemp_sjk_button.pack()

preemp_prio_button = Button(root, text="Preemptive Priority", command=display_preemp_prio)
preemp_prio_button.pack()

result_text = Text(root, height=20, width=120)
result_text.pack()

root.mainloop()
