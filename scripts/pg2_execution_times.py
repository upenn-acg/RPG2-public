# run program with python3 pg2_execution_times.py <workload>
# for example, python3 performanceOverTime.py pagerank

import subprocess
import sys
import os
import matplotlib.pyplot as plt
import time
from threading import Thread
import psutil
import re

config_path = "/home/nsobotka/floar/pg2_reloc/config"
tracer_cmd = "../tracer"
extract_cmd = "../extract_call_sites"

def find_execution_time(lines, keyword):
    execution_time_lines = []
    for i, line in enumerate(lines):
        if keyword in line:
            execution_time_lines = lines[i:i+5]
    return execution_time_lines

def extract_float_numbers(lines):
    float_numbers = []
    pattern = r"[-+]?\b(?:\d+\.\d+|\d+)\b" 

    for line in lines:
        match = re.findall(pattern, line)
        if match:
            float_numbers.append(float(match[0]))

    return float_numbers

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
    
    # DO NOT CHANGE THE PATH BELOW!
    iter_path = "/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "NewIterCounts"
    #iter_path = "/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "SynthIterCounts"
    
    print("Workload: ", workload)
    
    #directory_path = '../../inputs/'
    #directory_path = '/home/soyoon/floar/script_files_for_bolt_testing/' + workload + 'SynthIterCounts'
    directory_path = '/home/soyoon/floar/script_files_for_bolt_testing/' + workload + 'NewIterCounts'
    files_and_dirs = os.listdir(directory_path)
    count = 0
    files_list = [file for file in files_and_dirs if os.path.isfile(os.path.join(directory_path, file))]
    for filename in files_list:
        #if os.path.exists("/home/nsobotka/floar/pg2_reloc/results/pg2_performance/" + workload + "/" + filename) or (filename.startswith("sx")):
        if os.path.exists("/home/nsobotka/floar/pg2_reloc/results/pg2_performance/" + workload + "/" + filename):
            continue;
        if not os.path.exists("/home/nsobotka/floar/inputs/" + filename):
            continue;
        count = count + 1
        # read iter counts from pre-made txt file
        f = open(os.path.join(iter_path, filename), "r")
        lines = f.readlines()
        iter = str(lines[0])
        f.close()
        if (int(iter) > 4):
            iter = str(int(int(iter) / 4))
        print(iter)
            
        # update config file to have the correct input and iteration count
        with open(config_path, 'r') as file:
            lines = file.readlines()

            # Modify the last line to replace placeholders with variables
            last_line = lines[-1].strip()
            number1, number2 = parse_numbers(filename)
            if workload == "pagerank":
                if number1 is None:
                    last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock 1 1 /home/nsobotka/floar/inputs/sx-mathoverflow-edit.txt 67454"
                else:
                    last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/pagerank_lock/pagerank_lock 0 1 " + number1 + " " + number2 + " " + iter
                    lines[-1] = last_line
            elif workload == "bfs":
                last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/bfs/bfs 1 1 /home/nsobotka/floar/inputs/sx-mathoverflow-edit.txt 67454"
            elif workload == "sssp":
                last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/sssp/sssp 1 1 /home/nsobotka/floar/inputs/sx-mathoverflow-edit.txt 67454"
            elif workload == "bc":
                last_line = "cmd=/home/nsobotka/floar/pg2_reloc/workloads/CRONO/bc/bc 1 " + number1 + " " + number2 + " " + iter
                lines[-1] = last_line
            else:
                print("Add workloads here")
                return

            last_slash_index = last_line.rfind('/')

            if last_slash_index != -1 and workload != "bc" and number1 is None:
                # Replace everything after the last "/" with the variables
                updated_last_line = last_line[:last_slash_index+1] + filename + " " + iter
                lines[-1] = updated_last_line + '\n'
                print("LINES at NEG 1: ", lines[-1])
                
                # Write the updated content back to the .txt file
            with open(config_path, 'w') as file:
                file.writelines(lines)
    

        to_kill = "pkill -9 " + workload
        subprocess.run(to_kill.split())
        subprocess.run("pkill -9 pagerank_lock".split())
        subprocess.run("pkill -9 tracer".split())
        
        subprocess.run(extract_cmd)

        try:
            time.sleep(0.2)
            process = subprocess.check_output(tracer_cmd, timeout=25).decode('utf-8')
            
            subprocess.run(to_kill.split())
            subprocess.run("pkill -9 pagerank_lock".split())
            subprocess.run("pkill -9 tracer".split())
            
            lines = process.split("\n")
            keyword_to_find = "pg2 overall execution time"
            result_lines = find_execution_time(lines, keyword_to_find)
            times = extract_float_numbers(result_lines)
            if len(times) != 5:
                continue
            
            with open("/home/nsobotka/floar/pg2_reloc/results/pg2_performance/" + workload + "/" + filename, 'w') as file:
                for item in times:
                    file.write(str(item) + '\n')

            time.sleep(1)
        except subprocess.CalledProcessError as e:
            continue
        except subprocess.TimeoutExpired:
            continue
    print("Count: ", count)
            

if __name__ == "__main__":
    main()

