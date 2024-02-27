# run program with python3 performaceOverTime.py <workload> <inputName>
# for example, python3 performanceOverTime.py pagerank roadNet-PA

import subprocess
import sys
import os
import matplotlib.pyplot as plt
import time
from threading import Thread


config_path = "../config"
tracer_cmd = "../tracer"
extract_cmd = "../extract_call_sites"

def threaded_function():
    subprocess.run(tracer_cmd)

def main():
    args = sys.argv[1:]
    workload = args[0]
    filename = args[1]
    
    # DO NOT CHANGE THE PATH BELOW!
    iter_path = "/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "NewIterCounts"
    
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

    if workload == "pagerank":
        last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock 1 1 /home/nsobotka/floar/inputs/sx-mathoverflow-edit.txt 67454"
    if workload == "bfs":
        last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/bfs/bfs 1 1 /home/nsobotka/floar/inputs/sx-mathoverflow-edit.txt 67454"
    if workload == "sssp":
        last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/sssp/sssp 1 1 /home/nsobotka/floar/inputs/sx-mathoverflow-edit.txt 67454"
    if workload == "bc":
        last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/bc/bc 1 56384 8"
        lines[-1] = last_line


    last_slash_index = last_line.rfind('/')

    if last_slash_index != -1 and workload != "bc":
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
    time.sleep(1)

    pid = get_process_pid(workload)
    if pid is not None:
        ipc_measurements = measure_ipc(pid)
        result_file = "../results/" + workload + "_performance/cat/data/" + filename + ".txt"
        with open(result_file, "w") as f:
            for time_since_start, ipc_value in ipc_measurements:
                line = f"{time_since_start:.1f} {ipc_value}\n"
                f.write(line)

        # generate graph
        result_graph = "../results/" + workload + "_performance/cat/graphs/" + filename + ".png"
        time_values, ipc_values = zip(*ipc_measurements)
        plt.plot(time_values, ipc_values, color='blue', marker='', linestyle='-')
        plt.xlabel('Time (seconds)')
        plt.ylabel('IPC')
        plt.title('IPC vs. Time on ' + filename)
        plt.grid(True)

        plt.savefig(result_graph)
        plt.close()


def get_process_pid(process_name):
    try:
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        lines = ps_output.strip().split('\n')
        for line in lines:
            if process_name in line and 'grep' not in line and "python3" not in line:
                pid = int(line.split()[1])
                return pid
    except subprocess.CalledProcessError:
        print(f"Error: Unable to get the PID for process '{process_name}'")
    return None

def measure_ipc(pid, measurement_interval=0.3):
    ipc_measurements = []

    start_time = time.time()
    while True:
        try:
            perf_output = subprocess.check_output(
                ['perf', 'stat', '-e', 'cycles:u,instructions:u', '-p', str(pid), '--', 'sleep', str(measurement_interval)],
                stderr=subprocess.STDOUT
            ).decode('utf-8')

            time_since_start = time.time() - start_time
            ipc_lines = perf_output.strip().split('\n')
            cycles = "1"
            for line in ipc_lines:
                if 'cycles' in line:
                    ipc_data = line.split()
                    cycles = ipc_data[0]
                if 'instructions' in line:
                    ipc_data = line.split()
                    instructions = ipc_data[0]
                    if (int(cycles) == 0):
                        return ipc_measurements
                    ipc = int(instructions) / int(cycles)
                    ipc_measurements.append((time_since_start, ipc))
                    print(time_since_start, ipc)
        except subprocess.CalledProcessError:
            print(f"Process with PID '{pid}' is no longer running. Stopping IPC measurements.")
            break
        except KeyboardInterrupt:
            print("Measurement interrupted by user. Stopping IPC measurements.")
            break
    ipc_measurements = ipc_measurements[:-3]
    return ipc_measurements

if __name__ == "__main__":
    main()

