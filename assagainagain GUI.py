import tkinter as tk
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


def plot_gantt_chart(timeline):
    timeline = removeDuplicates(timeline)
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
    
    output = border + '\n' 
            + '|' + nameOutput + '\n'
            + timeOutput + '\n'
            + border
    return output


def data_displayer9000(method, processes, timeline):
    result = f"{method}\n"
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

    result += str(table) + "\n" + plot_gantt_chart(timeline)
    return result

def round_robin(processes, quantum, output_text):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0

    while ready_queue:
        ready_queue.sort(key=lambda x: (x.postprocess_arrival_time, x.priority, x.executed_before))
        current_process = ready_queue.pop(0)

        execution_time = min(quantum, current_process.remaining_time)
        current_process.remaining_time -= execution_time
        timeline.append((current_process.name, current_time, current_time + execution_time))
        current_time += execution_time

        if current_process.remaining_time > 0:
            current_process.postprocess_arrival_time = current_time
            ready_queue.append(current_process)
            current_process.executed_before = True
        else:
            current_process.finishing_time = current_time

    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, data_displayer9000("Round Robin", processes, timeline))
    output_text.config(state=tk.DISABLED)

def non_preemp_sjf(processes, output_text):
    ready_queue = processes.copy()
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

    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, data_displayer9000("Non Preemptive SJF", processes, timeline))
    output_text.config(state=tk.DISABLED)


def non_preemp_prio(processes, output_text):
    ready_queue = processes.copy()
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

    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, data_displayer9000("Non Preemptive Priority", processes, timeline))
    output_text.config(state=tk.DISABLED)


def preemp_sjk(processes, output_text):
    ready_queue = processes.copy()
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

    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, data_displayer9000("Preemptive SJF", processes, timeline))
    output_text.config(state=tk.DISABLED)


def preemp_prio(processes, output_text):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0
    current_process = None

    while ready_queue:
        ready_queue.sort(key=lambda x: (x.priority, x.postprocess_arrival_time))
        index = None
        for i in range(len(ready_queue)):
            if current_process is not None and ready_queue[i].name == current_process.name:
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

    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, data_displayer9000("Preemptive Priority", processes, timeline))
    output_text.config(state=tk.DISABLED)

def run_algorithm(algorithm, process_entries, quantum_entry, output_text):
    processes = []
    for i, entry_row in enumerate(process_entries):
        arrival_time = int(entry_row[0].get())
        burst_time = int(entry_row[1].get())
        priority = int(entry_row[2].get())
        processes.append(Process(f"P{i}", arrival_time, burst_time, priority))

    if algorithm == round_robin:
        quantum = int(quantum_entry.get())
        algorithm(deepcopy(processes), quantum, output_text)
    elif algorithm in [non_preemp_sjf, non_preemp_prio, preemp_prio, preemp_sjk]:
        algorithm(deepcopy(processes), output_text)
    else:
        algorithm(deepcopy(processes), output_text, quantum_entry)

def create_gui():
    window = tk.Tk()
    window.title("OS Scheduling Simulator")

    process_entries = []
    labels = ["Arrival Time", "Burst Time", "Priority"]

    num_processes_var = IntVar()
    num_processes_label = Label(window, text="Number of Processes:")
    num_processes_label.grid(row=0, column=0, padx=10)
    num_processes_entry = Entry(window, textvariable=num_processes_var)
    num_processes_entry.grid(row=0, column=1, padx=10)

    def get_num_processes():
        num_processes = num_processes_var.get()
        process_entries.clear()

        for i in range(num_processes):
            entry_row = []
            for j, label in enumerate(labels):
                entry_label = Label(window, text=f"{label} P{i}")
                entry_label.grid(row=i + 7, column=j * 2, padx=10)  
                entry = Entry(window)
                entry.grid(row=i + 7, column=j * 2 + 1, padx=10)  
                entry_row.append(entry)
            process_entries.append(entry_row)

    num_processes_button = Button(window, text="Set Processes", command=get_num_processes)
    num_processes_button.grid(row=0, column=2, padx=10)

    quantum_label = Label(window, text="Time Quantum for Round Robin:")
    quantum_label.grid(row=0, column=3, padx=10)

    quantum_entry = Entry(window)
    quantum_entry.grid(row=0, column=4, padx=10)

    run_button_rr = Button(window, text="Run Round Robin", command=lambda: run_algorithm(round_robin, process_entries, quantum_entry, output_text))
    run_button_rr.grid(row=0, column=5, padx=10)

    run_button_sjf = Button(window, text="Run Non-Preemptive SJF", command=lambda: run_algorithm(non_preemp_sjf, process_entries, quantum_entry, output_text))
    run_button_sjf.grid(row=1, column=5, padx=10)

    run_button_prio = Button(window, text="Run Non-Preemptive Priority", command=lambda: run_algorithm(non_preemp_prio, process_entries, quantum_entry, output_text))
    run_button_prio.grid(row=2, column=5, padx=10)

    run_button_sjk = Button(window, text="Run Preemptive SJF", command=lambda: run_algorithm(preemp_sjk, process_entries, quantum_entry, output_text))
    run_button_sjk.grid(row=3, column=5, padx=10)

    run_button_prio_preemp = Button(window, text="Run Preemptive Priority", command=lambda: run_algorithm(preemp_prio, process_entries, quantum_entry, output_text))
    run_button_prio_preemp.grid(row=4, column=5, padx=10)

    output_text = Text(window, height=20, width=125, state=tk.DISABLED)
    output_text.grid(row=6, column=0, columnspan=10, padx=10, pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
