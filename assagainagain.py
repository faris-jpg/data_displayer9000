from copy import deepcopy
from prettytable import PrettyTable

class Process:
    # Class for each process with necessary attributes
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
    print(method)
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
    print(table)
    print(timeline)


def round_robin(processes, quantum):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0

    while ready_queue:
        #Sort the queue first by arrival time, and then by priority,
        #and finally by whether or not it has been executed before.
        #Use postprocess arrvial time as original arrival time should be kept for
        #data to be displayed.
        ready_queue.sort(key=lambda x: (x.postprocess_arrival_time, x.priority, x.executed_before))

        #Take the first process in the queue.
        current_process = ready_queue.pop(0)

        #Time it takes to execute is the minimum of remaining time and quantum,
        # as if remaining time is less than quantum it wont take the full time.
        execution_time = min(quantum, current_process.remaining_time)
        current_process.remaining_time -= execution_time

        #Timeline for gantt chart
        timeline.append((current_process.name, current_time, current_time + execution_time))

        current_time += execution_time
        current_process.postprocess_arrival_time = current_time

        if current_process.remaining_time > 0:
            #Puts the process back to the queue if it hasnt completed.
            ready_queue.append(current_process)
            current_process.executed_before = True

        else:
            current_process.finishing_time = current_time

    data_displayer9000("Round Robin", processes, timeline)

    return

def non_preemp_sjf(processes):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0
    #Sort the queue by burst time as shortest job first. 
    #Also sorted by priority, if two processes have equal burst, less priority will go first
    #Finally sorted by arrival time if same priority, as FCFS in that case
    ready_queue.sort(key= lambda x: (x.burst_time, x.priority, x.arrival_time))

    while ready_queue:
        #Finds the process with lowest burst that has arrived and executes it
        #Breaks out when found
        for i in range(len(ready_queue)):
            if (ready_queue[i].arrival_time <= current_time):
                current_process = ready_queue.pop(i)
                break

        timeline.append((current_process.name, current_time, current_time + current_process.remaining_time))

        current_time += current_process.remaining_time
        current_process.finishing_time = current_time
        current_process.remaining_time = 0

    data_displayer9000("Non Preemptive SJF", processes, timeline)

    return


def non_preemp_prio(processes):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0
    #Sort the queue by priority as lowest priority first
    ready_queue.sort(key= lambda x: (x.priority, x.arrival_time))

    while ready_queue:
        #Finds the process with lowest priority that has arrived and executes it
        #Breaks out when found
        for i in range(len(ready_queue)):
            if (ready_queue[i].arrival_time <= current_time):
                current_process = ready_queue.pop(i)
                break

        timeline.append((current_process.name, current_time, current_time + current_process.remaining_time))

        current_time += current_process.remaining_time
        current_process.finishing_time = current_time
        current_process.remaining_time = 0

    data_displayer9000("Non Preemptive Priority", processes, timeline)

    return

def preemp_sjk(processes):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0

    while ready_queue:
        #Sorts by rem time and then by priority, and finally by arrival for FCFS
        ready_queue.sort(key= lambda x: (x.remaining_time, x.priority, x.postprocess_arrival_time))
        
        #Finds the shortest burst time that has arrived, saves its index
        for i in range(len(ready_queue)):
            if (ready_queue[i].arrival_time <= current_time):
                current_process = ready_queue[i]
                index = i
                break

        timeline.append((current_process.name, current_time, current_time + 1))
        current_time += 1
        current_process.remaining_time -= 1
        current_process.postprocess_arrival_time = current_time

        #Checks if it has completed, and if it has, pop it
        if current_process.remaining_time == 0:
            current_process.finishing_time = current_time
            ready_queue.pop(index)
    
    data_displayer9000("Preemptive SJF", processes, timeline)
    return


def preemp_prio(processes):
    ready_queue = processes.copy()
    timeline = []
    current_time = 0
    current_process = None

    while ready_queue:
        ready_queue.sort(key=lambda x: (x.priority, x.postprocess_arrival_time))

        index = None
        for i in range(len(ready_queue)):
            #As the queue keeps being sorted, keep track of the current process index
            #due to "SAME PRIORITY, NO PREEMPTION, TO REDUCE CONTEXT SWITCH" assumption
            if current_process != None and ready_queue[i].name == current_process.name:
                index = i
                break

            #Again, same priority, no preemption
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

    data_displayer9000("Preemptive Prio", processes, timeline)
    return

if __name__ == "__main__":
    num_processes = int(input("Number of processes: "))
    processes = []
    
    for i in range(num_processes):
        process_name = f"P{i}"
        arrival_time = int(input(f"Arrival time for {process_name}: "))
        burst_time = int(input(f"Burst time for {process_name}: "))
        priority = int(input(f"Priority for {process_name}: "))
        processes.append(Process(process_name, arrival_time, burst_time, priority))
    
    quantum = int(input("Time Quantum for Round Robin: "))

    round_robin(deepcopy(processes), quantum)
    non_preemp_sjf(deepcopy(processes))
    non_preemp_prio(deepcopy(processes))
    preemp_sjk(deepcopy(processes))
    preemp_prio(deepcopy(processes))


