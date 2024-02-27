import subprocess
import sys
import os
import matplotlib.pyplot as plt
import time
from threading import Thread
import signal
from mpkiOverTime import *

filename = ""
workload = ""

def threaded_function():
    print("Starting tracking thread")
    measureMPKI()

def handler(signum, frame):
    print("Ignored sig")
    print("Started storing data")
    #thread = Thread(target = threaded_function)
    #thread.start()
    return

signal.signal(signal.SIGUSR1, handler)

def measureMPKI():
    pid = get_process_pid(workload)
    if pid is not None:
        print(pid)
        (instructions, llc) = measure_ipc(pid)
        print(instructions, llc)
        result_file = "../results/" + workload + "_mpki/cascade/data_nopg2/" + filename + ".txt"
        with open(result_file, "w") as f:
            line = f"{instructions} {llc}\n"
            f.write(line)

def get_process_pid(process_name):
    try:
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        lines = ps_output.strip().split('\n')
        for line in lines:
            if process_name in line and 'grep' not in line and "python" not in line:
                pid = int(line.split()[1])
                return pid
    except subprocess.CalledProcessError:
        print(f"Error: Unable to get the PID for process '{process_name}'")
    return None

def measure_ipc(pid):
    try:
        print(pid)
        perf_output = subprocess.check_output(
           ['perf', 'stat', '-e', 'instructions:u,LLC-load-misses:u', '-p', str(pid)],
          stderr=subprocess.STDOUT
        ).decode('utf-8')

        #perf_output = subprocess.check_output(["echo", "hi"]).decode('utf-8')
        print(perf_output)
        ipc_lines = perf_output.strip().split('\n')
        for line in ipc_lines:
            if 'instructions' in line:
                ipc_data = line.split()
                instructions = ipc_data[0]
            if 'LLC-load-misses' in line:
                ipc_data = line.split()
                llc = ipc_data[0]
                return (int(instructions), int(llc))
    except subprocess.CalledProcessError:
        print(f"Process with PID '{pid}' is no longer running. Stopping IPC measurements.")
    except KeyboardInterrupt:
        print("Measurement interrupted by user. Stopping IPC measurements.")
    return (None, None)


def main():
    global workload
    global filename
    args = sys.argv[1:]
    workload = args[0]
    synth = args[1]

    directory_path = '../../inputs/'
    #directory_path = '/home/soyoon/floar/script_files_for_bolt_testing/pagerankSynthIterCounts'
    files_and_dirs = os.listdir(directory_path)
    files_list = [file for file in files_and_dirs if os.path.isfile(os.path.join(directory_path, file))]
    for file in files_list:
        if os.path.exists("/home/soyoon/floar/pg2_reloc/results/pagerank_mpki/cascade/data_nopg2/" + file) or file.startswith("sx"):
            continue;
        filename = file[:-4]
        # DO NOT CHANGE THE PATH BELOW!
        iter_path = "/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "NewIterCounts"
        #iter_path = '/home/soyoon/floar/script_files_for_bolt_testing/pagerankSynthIterCounts'

        print("Workload: ", workload)
        print("Input: ", filename)
    
        # read iter counts from pre-made txt file
        if workload != "bc":
            f = open(os.path.join(iter_path, filename + ".txt"), "r")
            lines = f.readlines()
            iter = str(lines[0])
            f.close()
            print(iter)
        cmd = ""
        if workload == "pagerank" and synth == "1":
            cmd = "perf stat -e instructions:u,LLC-load-misses:u -- /home/soyoon/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock 1 1 " + "/home/soyoon/floar/inputs/" + filename + ".txt " + iter
        elif workload == "pagerank" and synth == "0":
            number1, number2 = parse_numbers(filename)
            cmd = "perf stat -e instructions:u,LLC-load-misses:u -- /home/soyoon/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock 0 1 " + number1 + " " + number2 + " " + iter

        print(cmd)
        perf_output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT).decode('utf-8')
        print(perf_output)
        ipc_lines = perf_output.strip().split('\n')
        instructions = 1
        llc = 1
        for line in ipc_lines:
            if 'instructions' in line:
                ipc_data = line.split()
                instructions = ipc_data[0]
            if 'LLC-load-misses' in line:
                ipc_data = line.split()
                llc = ipc_data[0]

        print(instructions, llc)
        result_file = "../results/" + workload + "_mpki/cascade/data_nopg2/" + filename + ".txt"
        with open(result_file, "w") as f:
            line = f"{instructions} {llc}\n"
            f.write(line)

if __name__ == "__main__":
    main()

