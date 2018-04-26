'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.

Student Name: Zheng Fan
Matriculation No.: U099126N
'''
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        
        self.remaining_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    schedule = []
    current_time = 0
    waiting_time = 0
    count = 0
    index = -1
    
    # initialize the remaining time
    for process in process_list:
        process.remaining_time = process.burst_time
    
    while count < len(process_list):
        # find the next arrived and unfinished process               
        index = (index + 1) % len(process_list)
        process = process_list[index]
        if process.remaining_time == 0:
            continue
        if current_time < process.arrive_time:
            if index == count:
                current_time = process.arrive_time  #no more unfinished process, fast-forward
            else:
                index = -1  #check from process no.0
                continue
            
        # append to schedule if it is not the same as previous one
        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != process.id:
            schedule.append( (current_time, process.id) )
            
        # run the process for the remaining time or the time_quantum
        run_time = min(process.remaining_time, time_quantum)
        current_time += run_time
        process.remaining_time -= run_time        
        if process.remaining_time == 0:
            waiting_time += current_time - process.arrive_time - process.burst_time
            count += 1
    
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    schedule = []
    current_time = 0
    waiting_time = 0
    count = 0
    
    # initialize the remaining time
    for process in process_list:
        process.remaining_time = process.burst_time
    
    while count < len(process_list):
        srt = sys.maxint
        proc = None
        next_arrive = -1
        # find the process with shortest remaining time, and the next arriving process
        for i in range(0, len(process_list)):
            process = process_list[i]
            if process.arrive_time <= current_time:
                if process.remaining_time < srt and process.remaining_time != 0:
                    srt = process.remaining_time
                    proc = process
            else:
                next_arrive = i
                break
        
        # if no more unfinished process, fast-forward
        if not proc:
            current_time = process_list[next_arrive].arrive_time
            continue
        
        # get the next arrival time
        if next_arrive == -1:
            next_arrival_time = sys.maxint
        else:
            next_arrival_time = process_list[next_arrive].arrive_time
        
        # append to schedule if it is not the same as previous one
        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != proc.id:
            schedule.append( (current_time, proc.id) )
        
        # run the process for the remaining time until the next arrival comes
        run_time = min(next_arrival_time - current_time, proc.remaining_time)
        current_time += run_time
        proc.remaining_time -= run_time
        if proc.remaining_time == 0:
            waiting_time += current_time - proc.arrive_time - proc.burst_time
            count += 1
                
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time

def SJF_scheduling(process_list, alpha):
    schedule = []
    current_time = 0
    waiting_time = 0
    predict_time = {}
    arrived = {}
    count = 0
    index = 0
    
    # initialize the remaining time
    for process in process_list:
        process.remaining_time = process.burst_time
    
    while count < len(process_list):
        proc = None
        # put the arrived process into arrived array
        for i in range(index, len(process_list)):
            process = process_list[i]
            if process.remaining_time == 0:
                continue
            if process.arrive_time > current_time:
                index = i
                break
            if process.id not in predict_time:
                predict_time[process.id] = 5
            if process.id not in arrived:
                arrived[process.id] = []
            arrived[process.id].append(process)
        
        # sort the predict time, get the first element of the shortest process id
        sort = sorted(predict_time, key = predict_time.get)            
        for i in sort:
            if len(arrived[i]) != 0:
                proc = arrived[i].pop(0)
                break
        
        # if no more unfinished process, fast-forward
        if not proc:
            current_time = process_list[index].arrive_time
            continue
        
        # append to schedule if it is not the same as previous one
        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != proc.id:
            schedule.append( (current_time, proc.id) )
        
        # run the process for the remaining time
        current_time += proc.remaining_time
        proc.remaining_time = 0
        count += 1
        waiting_time += current_time - proc.arrive_time - proc.burst_time          
        predict_time[proc.id] = alpha * predict_time[proc.id] + (1 - alpha) * proc.burst_time
        
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])