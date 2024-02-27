# run program with python3 mpkiOverTime.py <workload> <synth Number>
# for example, python3 mpkiOverTime.py pagerank

import subprocess
import sys
import os
import matplotlib.pyplot as plt
import time
import re
from threading import Thread


config_path = "../config"
tracer_cmd = "../tracer"
extract_cmd = "../extract_call_sites"

def threaded_function():
    subprocess.run(tracer_cmd)


def parse_numbers(input_string):
    pattern = r"V=(\d+)_D=(\d+)"
    match = re.search(pattern, input_string)

    if match:
        number1 = match.group(1)
        number2 = match.group(2)
        print(number1, number2)
        return number1, number2
    else:
        return None, None

def main():
    args = sys.argv[1:]
    workload = args[0]
    synth = args[1]

    directory_path = '../../inputs/'
    #directory_path = '/home/soyoon/floar/script_files_for_bolt_testing/pagerankSynthIterCounts'
    files_and_dirs = os.listdir(directory_path)
    files_list = [file for file in files_and_dirs if os.path.isfile(os.path.join(directory_path, file))]
    for file in files_list:
        if os.path.exists("/home/soyoon/floar/pg2_reloc/results/pagerank_mpki/cascade/data/" + file) or file.startswith("sx"):
        #if os.path.exists("/home/soyoon/floar/pg2_reloc/results/pagerank_mpki/cascade/data/" + file):
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

            # update config file to have the correct input and iteration count
            with open(config_path, 'r') as file:
                lines = file.readlines()

                # Modify the last line to replace placeholders with variables
                last_line = lines[-1].strip()

                if workload == "pagerank" and synth == "1":
                    last_line = "cmd=/home/soyoon/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock " + synth + " 1 /home/soyoon/floar/inputs/sx-mathoverflow-edit.txt 67454"
                elif workload == "pagerank" and synth == "0":
                    number1, number2 = parse_numbers(filename)
                    last_line = "cmd=/home/soyoon/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock 0 1 " + number1 + " " + number2 + " " + iter
                    lines[-1] = last_line
                if workload == "bfs":
                    last_line = "cmd=/home/soyoon/floar/pg2_reloc/workloads/CRONO/bfs/bfs 1 1 /home/soyoon/floar/inputs/sx-mathoverflow-edit.txt 67454"
                if workload == "sssp":
                    last_line = "cmd=/home/soyoon/floar/pg2_reloc/workloads/CRONO/sssp/sssp 1 1 /home/soyoon/floar/inputs/sx-mathoverflow-edit.txt 67454"
                if workload == "bc":
                    last_line = "cmd=/home/soyoon/floar/pg2_reloc/workloads/CRONO/bc/bc 1 56384 8"
                    lines[-1] = last_line


                last_slash_index = last_line.rfind('/')

        if last_slash_index != -1 and workload != "bc" and not (workload == "pagerank" and synth == "0"):
            print("In here")
            # Replace everything after the last "/" with the variables
            updated_last_line = last_line[:last_slash_index+1] + filename + ".txt " + iter
            lines[-1] = updated_last_line + '\n'

        # Write the updated content back to the .txt file
        with open(config_path, 'w') as file:
            file.writelines(lines)
    

        to_kill = "pkill -9 " + workload
        subprocess.run(to_kill.split())
        subprocess.run("pkill -9 pagerank_lock".split())
        subprocess.run(extract_cmd)
        
        #spawn second thread to start pg2, so that we don't wait until it finishes to start recording
        #os.system(tracer_cmd)
        thread = Thread(target = threaded_function)
        thread.start()
        time.sleep(0.1)
        
        #pid = get_process_pid(workload)
        pid = get_process_pid(workload + "_lock")
        if pid is not None:
            (instructions, llc) = measure_ipc(pid)
            result_file = "../results/" + workload + "_mpki/cascade/data/" + filename + ".txt"
            with open(result_file, "w") as f:
                line = f"{instructions} {llc}\n"
                f.write(line)


def get_process_pid(process_name):
    try:
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        lines = ps_output.strip().split('\n')
        for line in lines:
            if process_name in line and 'grep' not in line and "python" not in line:
                print(line)
                pid = int(line.split()[1])
                return pid
    except subprocess.CalledProcessError:
        print(f"Error: Unable to get the PID for process '{process_name}'")
    return None

def measure_ipc(pid, measurement_interval=0.3):
    while True:
        try:
            perf_output = subprocess.check_output(
                ['perf', 'stat', '-e', 'instructions:u,LLC-load-misses:u', '-p', str(pid)],
                stderr=subprocess.STDOUT
            ).decode('utf-8')
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
            break
        except KeyboardInterrupt:
            print("Measurement interrupted by user. Stopping IPC measurements.")
            break
    return None

if __name__ == "__main__":
    main()

