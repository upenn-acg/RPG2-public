import os
import subprocess
import sys
import time
import signal
import re

#NOTE: run "make" on workload with -DSIGNAL flag before running
#NOTE: requires name of CRONO workload as an argument (pagerank, sssp, bfs, bc), 
#      and optional additional "synth" argument to run synthetic inputs (for pagerank, bc)

# print for cases when not one or two arguments are given
if (len(sys.argv) == 1):
  print("name of CRONO workload required as an argument")
  exit()
elif (len(sys.argv) > 3):
  print("takes in one argument, the name of CRONO workload, and optional second argument \"synth\"")
  exit()

synth = False

workload = str(sys.argv[1])

if workload == "bc":
  synth = True

if len(sys.argv) == 3:
  if str(sys.argv[2]) == "synth":
    synth = True
  else: 
    print("type \"synth\" as the second argument to run synthetic inputs")
    exit()

path_fd = open("script_config.txt", "r")
path_lines = path_fd.readlines()
path_fd.close()

machine = path_lines[0].replace('\n', '')
log_path = path_lines[5].replace('\n', '')

#create error log for inputs with three consecutive errors in pg2
err_path = log_path + workload + "_" + machine + "_error.txt" 
err_touch_cmd = "touch " + err_path
subprocess.run(err_touch_cmd.split())

extract_cmd = "../extract_call_sites"
subprocess.run(extract_cmd.split())

pg2_err_path = "../log/" + workload + "/pg2/"
bolt_err_path = "../log/" + workload + "/bolt/"
pf_dist_err_path = "../log/" + workload + "/pf_dist/"
large_err_path = "../log/" + workload + "/large/"
nochild_err_path = "../log/" + workload + "/nochild/"
other_err_path = "../log/" + workload + "/other/"

err_path = log_path + workload + "_" + machine + "_error.txt" 

# make directories for log
pg2_err_mkdir_cmd = "mkdir " + pg2_err_path
bolt_err_mkdir_cmd = "mkdir " + bolt_err_path
pf_dist_err_mkdir_cmd = "mkdir " + pf_dist_err_path
large_err_mkdir_cmd = "mkdir " + large_err_path
nochild_err_mkdir_cmd = "mkdir " + nochild_err_path 
other_err_mkdir_cmd = "mkdir " + other_err_path

subprocess.run(pg2_err_mkdir_cmd.split())
subprocess.run(bolt_err_mkdir_cmd.split())
subprocess.run(pf_dist_err_mkdir_cmd.split())
subprocess.run(large_err_mkdir_cmd.split())
subprocess.run(nochild_err_mkdir_cmd.split())
subprocess.run(other_err_mkdir_cmd.split())

def main(workload, synth):
  if synth and not (workload == "pagerank" or workload == "bc"):
    print("synthetic input is not supported for provided workload.")
    exit()
    '''
    bc_inputs = ["56384 8","40000 10","10000 1000", "20000 500", "20000 200", "20000 100", "20000 50", "20000 10", "20000 5"]
    pagerank_inputs = ["200000 5 ","200000 10 ","200000 20 ", "200000 50 ", "200000 100 ", "200000 500 "]
    if workload == "pagerank":
      for item in pagerank_inputs:
        split = item.split()
        v = split[0]
        d = split[1]
        filename = "V=" + v + "_D=" + d + ".txt"
        run(workload, filename, synth)
      
    elif workload == "bc":
      for item in bc_inputs:
        split = item.split()
        v = split[0]
        d = split[1]
        filename = "V=" + v + "_D=" + d + ".txt"
        run(workload, filename, synth)
    else:
      print("synthetic input is not supported for provided workload.")
      exit()
    '''
  elif workload == "bfs":
    bfs_inputs_fd = open("bfs_inputs.txt", "r")
    #bfs_inputs_fd = open("bfs_inputs_large.txt", "r")
    bfs_inputs = bfs_inputs_fd.readlines()
    bfs_inputs_fd.close()
    for input_line in bfs_inputs:
      filename = input_line.strip()
      run(workload, filename, synth)
  else:
    if workload == "bc":
      inputs_path = "/home/soyoon/floar/script_files_for_bolt_testing/bcSynthIterCounts" 
    elif synth and workload == "pagerank":
      inputs_path = "/home/soyoon/floar/script_files_for_bolt_testing/pagerankSynthIterCounts" 
    else:
      path_fd = open("script_config.txt", "r")
      path_lines = path_fd.readlines()
      path_fd.close()

      machine = path_lines[0].replace('\n', '')
      inputs_path = path_lines[1].replace('\n', '')
    
    #iterate over all txt files in inputs folder
    for dirpath, dirnames, filenames in os.walk(inputs_path):
      for filename in filenames:
        run(workload, filename, synth)


def run(workload, filename, synth):
  #config_path = "/home/soyoon/floar/pg2_reloc/config"
  config_path = "../config"
  #config_rm_cmd = "rm " + config_path
  config_touch_cmd = "touch " + config_path

  pg2_err_path = "../log/" + workload + "/pg2/"
  bolt_err_path = "../log/" + workload + "/bolt/"
  pf_dist_err_path = "../log/" + workload + "/pf_dist/"
  large_err_path = "../log/" + workload + "/large/"
  nochild_err_path = "../log/" + workload + "/nochild/"
  other_err_path = "../log/" + workload + "/other/"

  tmp_touch_cmd = "touch tmp.txt"
  tmp2_touch_cmd = "touch tmp2.txt"
  tmp3_touch_cmd = "touch tmp3.txt"
  tmp_rm_cmd = "rm tmp.txt"
  tmp2_rm_cmd = "rm tmp2.txt"
  tmp3_rm_cmd = "rm tmp3.txt"

  tracer_cmd = "../tracer"

  # read from script_config.txt file to fill up paths
  path_fd = open("script_config.txt", "r")
  path_lines = path_fd.readlines()
  path_fd.close()

  machine = path_lines[0].replace('\n', '')
  inputs_path = path_lines[1].replace('\n', '')
  CRONO_path = path_lines[2].replace('\n', '')
  pg2_data_path = path_lines[3].replace('\n', '')
  results_path = path_lines[4].replace('\n', '') + workload + "/" + machine + "/"
  log_path = path_lines[5].replace('\n', '')
  llvmbolt_path = path_lines[6]
  perf2bolt_line = path_lines[7]
  batdump_line = path_lines[8]
  lib_line = path_lines[9]

  '''
  # MODIFY ALL PATHS BELOW! (username and machine)
  machine = "cascade" #<-- cat or cascade
  inputs_path = "/home/soyoon/floar/inputs/"
  CRONO_path = "/home/soyoon/floar/pg2_reloc/workloads/CRONO/"
  pg2_data_path = "/home/soyoon/pg2_data/"
  results_path = "/home/soyoon/floar/pg2_reloc/results/" + workload + "/" + machine + "/"
  log_path = "/home/soyoon/floar/pg2_reloc/log/"
  llvmbolt_path = "/home/soyoon/BOLT/build/bin/llvm-bolt"
  perf2bolt_line = "perf2bolt=/home/soyoon/BOLT/build/bin/perf2bolt\n"
  batdump_line = "bat-dump=/home/soyoon/llvm-17.0/build/bin/llvm-bat-dump\n"
  lib_line = "lib=/home/soyoon/floar/pg2_reloc/\n"
  '''
  llvmbolt_line = "llvm-bolt=" + llvmbolt_path + "\n"
  tmp_data_dir_line = "tmp_data_dir=" + pg2_data_path + "\n"
  pf_loc_path = pg2_data_path + "prefetch_loc.txt"

  err_path = log_path + workload + "_" + machine + "_error.txt" 

  
  if (filename.endswith(".txt")) and (not os.path.isfile(results_path + filename)):
    input = filename.split(".")[0]
    print("\ninput: %s" % input)
    
    output = results_path + filename
    output_touch_cmd = "touch " + output
    subprocess.run(output_touch_cmd.split())

    if workload == "pagerank":
      program = workload + "_lock"
    else:
      program = workload
    
    workload_path = CRONO_path + program + "/" + program
    bolt_path = pg2_data_path + program + "_optimal.bolt"
    pkill_cmd = "pkill -9 " + program
    
    #NOTE: DO NOT CHANGE THE iter_path BELOW!
    if synth:
      iter_path = "/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "SynthIterCounts"
    else:
      iter_path = "/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "NewIterCounts"
    
    # read iter counts from pre-made txt file
    f = open(os.path.join(iter_path, filename), "r")
    lines = f.readlines()
    iter = str(lines[0])
    f.close()

    if synth:
      f_split = re.split(r'[=_.]', filename)
      v = f_split[1]
      d = f_split[3]

      if workload == "bc":
        prefix = workload_path
      else: #elif workload == "pagerank":
        prefix = workload_path + " 0"
      cmd = prefix + " 1 " + v + " " + d + " " + iter
    else:
      cmd = workload_path + " 1 1 " + inputs_path + filename + " " + iter
    
    cmd_line = "cmd=" + cmd

    subprocess.run(tmp_touch_cmd.split())
    subprocess.run(tmp2_touch_cmd.split())
    subprocess.run(tmp3_touch_cmd.split())
    
    #touch config file
    subprocess.run(config_touch_cmd.split())
    
    #write all the required lines to the config file
    config_fd = open(config_path, "w")
    config_fd.writelines([llvmbolt_line, perf2bolt_line, batdump_line, tmp_data_dir_line, lib_line, cmd_line])
    config_fd.close()

    count = 0
    err_count = 0
    skip = False
    
    # run pg2 & corresponding BOLTed binary 5 times
    while count < 5:
      print("\ncount: %d" % count)
      pf_dist = -1

      subprocess.run(pkill_cmd.split())

      tmp_fd = open("tmp.txt", "w")
      tmp2_fd = open("tmp2.txt", "w")
      subprocess.run(tracer_cmd.split(), stdout=tmp_fd, stderr=tmp2_fd)
      tmp_fd.close()
      tmp2_fd.close()

      core_dumped = parse_bolt_error("tmp2.txt")

      if core_dumped:
        err = True

        ##bolt_err = bolt_err_path + input + "_" + str(count) + "_" + str(err_count) + ".txt" 
        bolt_err = bolt_err_path + input + "_" + str(count) + ".txt" 
        cp_bolt_err_cmd = "cp tmp2.txt " + bolt_err
        
        ##bolt_err_pf_loc = bolt_err_path + input + "_" + str(count) + "_" + str(err_count) + "_pf_loc.txt"
        bolt_err_pf_loc = bolt_err_path + input + "_" + str(count) + "_pf_loc.txt"
        cp_pf_loc_cmd = "cp " + pf_loc_path + " " + bolt_err_pf_loc
        
        #bolt_err_bolt = bolt_err_path + input + "_" + str(count) + ".bolt"
        #cp_bolt_cmd = "cp " + bolt_path + " " + bolt_err_bolt

        subprocess.run(cp_bolt_err_cmd.split())
        subprocess.run(cp_pf_loc_cmd.split())
        subprocess.run(pkill_cmd.split())

        bolt_err_stdout = bolt_err_path + input + "_" + str(count) + "_stdout.txt" 
        cp_bolt_err_stdout_cmd = "cp tmp.txt " + bolt_err_stdout
        subprocess.run(cp_bolt_err_stdout_cmd.split())

        bolt_err_perf = bolt_err_path + input + "_" + str(count) + "_perf.data" 
        cp_bolt_err_perf_cmd = "cp " + pg2_data_path + "perf.data " + bolt_err_perf
        subprocess.run(cp_bolt_err_perf_cmd.split())
     
      #TODO: delete following block if it works
      '''
      if synth:
        pid = get_process_pid(cmd)
      else:
        pid = get_process_pid(filename)
      '''

      time.sleep(0.1)
      
      pid = get_process_pid(cmd)

      if pid < 0:
        print("could not grab pid for child process")
        #indicate separately when there was no child process
        ##nochild_err = nochild_err_path + input + "_" + str(count) + "_" + str(err_count) + ".txt"
        nochild_err = nochild_err_path + input + "_" + str(count) + ".txt"
        cp_nochild_err_cmd = "cp tmp.txt " + nochild_err
        subprocess.run(cp_nochild_err_cmd.split())
        #subprocess.run(pkill_cmd.split())

      else: 
        print("waiting on pid: %d" % pid)

        # wait for workload to finish
        while os.path.exists("/proc/" + str(pid)):
          time.sleep(3)
         
        print("child process completed")
      
      tmp_fd = open("tmp.txt", "r")
      lines = tmp_fd.readlines()
      
      err = False
      perf_err = False

      #subprocess.run(pkill_cmd.split())
      
      # grab optimal prefetch distance from redirected file
      # check if error occurred
      for item in lines:
        line = str(item)
        if line.startswith("[tracer][error]"):
          err = True
          print(line)
          if line.startswith("[tracer][error] error in run_perf_report") or line.startswith("[tracer][error] prefetch_loc.txt is empty."):
            err = False
            perf_err = True
            if count == 0:
              err_count += 1
            pg2_err = pg2_err_path + input + "_" + str(count) + "_" + str(err_count) + ".txt" 
            ##pg2_err = pg2_err_path + input + "_" + str(count) + ".txt" 
            cp_pg2_err_cmd = "cp tmp.txt " + pg2_err
            subprocess.run(cp_pg2_err_cmd.split())

            if err_count == 5:
              print("run_perf_report error for all first five times, skipping the input")
              skip = True
          
          elif line.startswith("[tracer][error] after PTRACE_CONT,"):
            print("input graph is too large, skipping the input")
            skip = True
            
            ##large_err = large_err_path + input + "_" + str(count) + "_" + str(err_count) + ".txt" 
            large_err = large_err_path + input + "_" + str(count) + ".txt" 
            cp_large_err_cmd = "cp tmp.txt " + large_err
            subprocess.run(cp_large_err_cmd.split())
          else: 
            ##other_err = other_err_path + input + "_" + str(count) + "_" + str(err_count) + ".txt" 
            other_err = other_err_path + input + "_" + str(count) + ".txt" 
            cp_other_err_cmd = "cp tmp.txt " + other_err
            subprocess.run(cp_other_err_cmd.split())
         
          break
        elif line.startswith("[tracer] optimal pref_dist = "):
          split = line.split(" ")
          pf_dist = int(split[-1])
          print("optimal prefetch distance: %d" % pf_dist)
      
      if not err:
        # grab execution time
        t_pg2 = parse_time(lines, workload)
        print("pg2 execution time: %f" % t_pg2)
        if t_pg2 < 0:
          print("could not grab pg2 execution time")
          err = True
        if (not perf_err) and (pf_dist < 0):
          print("could not grab optimal prefetch distance")
          err = True
          #err_count += 1

          ##pf_dist_err = pf_dist_err_path + input + "_" + str(count) + "_" + str(err_count) + ".txt" 
          pf_dist_err = pf_dist_err_path + input + "_" + str(count) + ".txt" 
          cp_pf_dist_err_cmd = "cp tmp.txt " + pf_dist_err
          subprocess.run(cp_pf_dist_err_cmd.split())
          
          #if err_count == 3:
          #  print("error occurred three times in a row, skipping the input")
          #  skip = True

      tmp_fd.close()
      
      if skip and (not perf_err):
        break
      elif err:
        continue
      #else:
      
      # if perf error, skip recording optimal prefetch distance and BOLTed binary
      if not perf_err:
        

        pf_loc_fd = open(pf_loc_path, "r")
        lines = pf_loc_fd.readlines()
        pf_loc_fd.close()
        
        split = lines[0].split()

        '''
        # check if prefetch_loc.txt file contains more than one column
        if len(split) < 2:
          print("prefetch_loc.txt does not contain prefetch location")
          #TODO: potentially record the error
          continue
        '''

        # modify prefetch distances of prefetch_loc.txt file
        for i in range(2, len(split), 2):
          split[i] = str(pf_dist)

        pf_loc_newline = " ".join(split)
        print("prefetch_loc: %s" % pf_loc_newline)

        pf_loc_fd = open(pf_loc_path, "w")
        pf_loc_fd.write(pf_loc_newline)
        pf_loc_fd.close()

        make_bolt_cmd = llvmbolt_path + " --enable-bat --inject-prefetch --prefetch-location-file=" + pf_loc_path + " " + workload_path + " -o " + bolt_path 

        tmp3_fd = open("tmp3.txt", "w")
        subprocess.run(make_bolt_cmd.split(), stdout=subprocess.DEVNULL, stderr=tmp3_fd)
        tmp3_fd.close()
        
        core_dumped = parse_bolt_error("tmp3.txt")

        if core_dumped:
          bolt_err = bolt_err_path + input + "_" + str(count) + ".txt" 
          cp_bolt_err_cmd = "cp tmp3.txt " + bolt_err
          
          bolt_err_pf_loc = bolt_err_path + input + "_" + str(count) + "_pf_loc.txt"
          cp_pf_loc_cmd = "cp " + pf_loc_path + " " + bolt_err_pf_loc
          
          subprocess.run(cp_bolt_err_cmd.split())
          subprocess.run(cp_pf_loc_cmd.split())
          continue
        
        if synth:
          if workload == "bc":
            bolt_prefix = bolt_path
          else:
            bolt_prefix = bolt_path + " 0"
          bolt_cmd = bolt_prefix + " 1 " + v + " " + d + " " + iter 
        else:
          bolt_cmd = bolt_path + " 1 1 " + inputs_path + filename + " " + iter 

        #run same command on BOLTed version 
        tmp_fd = open("tmp.txt", "w")
        subprocess.run(bolt_cmd.split(), stdout=tmp_fd)
        tmp_fd.close()
        
        # parse the file for BOLTed execution time
        tmp_fd = open("tmp.txt", "r")
        lines = tmp_fd.readlines()
        t_bolt = parse_time(lines, workload)
        tmp_fd.close()

        print("BOLTed execution time: %f" % t_bolt)
      
      out_fd = open(output, "a")
      if perf_err:
        out_fd.write("%f\n" % t_pg2)
      else:
        out_fd.write("%f\t%f\t%s\n" % (t_pg2, t_bolt, pf_dist))
        count += 1
      out_fd.close()

      if skip:
        break

      #################  END OF WHILE LOOP #######################
    
    #if core_dumped:
    #  continue

    if skip:
      # write name of skipped input to error log 
      err_fd = open(err_path, "a")
      err_fd.write("%s\n" % filename)
      err_fd.close()
      if not perf_err:
        #continue
        return

    # run original command
    tmp_fd = open("tmp.txt", "w")
    subprocess.run(cmd.split(), stdout=tmp_fd)
    tmp_fd.close()
    
    # parse the file for original execution time
    tmp_fd = open("tmp.txt", "r")
    lines = tmp_fd.readlines()
    t_orig = parse_time(lines, workload)
    tmp_fd.close()

    print("Original execution time: %f" % t_orig)
    out_fd = open(output, "a")
    out_fd.write("%s" % t_orig)
    out_fd.close()
####################### END OF RUN FUNCTION ##################################

def handler(signum, frame):
  print("SIGUSR1 ignored")

signal.signal(signal.SIGUSR1, handler)

def parse_time(lines, workload):
  t = -1.0
  for item in lines:
    line = str(item)
    if (workload == "pagerank"):
      if line.startswith("Time:"):
        split = str(line[5:]).split(" ")
        t = float(split[0])
        break
    elif (workload == "bc"):
      if line.startswith("Time:"):
        split = str(line).split(" ")
        t = float(split[1])
        break
    elif (workload == "sssp"):
      if line.startswith("Elapsed"):
        split = str(line[:-2]).split(" ")
        t = float(split[2])
        break
    elif (workload == "bfs"):
      if ((not line.startswith("Initialization")) and (line.endswith("seconds\n"))):
        split = line.split(" ")
        t = float(split[0])
        break
  return t

def parse_bolt_error(filepath):
  core_dumped = False
  fd = open(filepath, "r")
  lines = fd.readlines()
  fd.close()
  
  for item in lines:
    line = str(item)
    split = line.split()
    if ((len(split) > 0) and (split[-1] == "dumped)")):
      print("%s" % line)
      core_dumped = True

  return core_dumped

def get_process_pid(process_name):
    try:
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        lines = ps_output.strip().split('\n')
        for line in lines:
            print(line)
            if process_name in line and 'grep' not in line and "python3" not in line and "python" not in line:
                pid = int(line.split()[1])
                return pid
    except subprocess.CalledProcessError:
        print(f"Error: Unable to get the PID for process '{process_name}'")
    return -1

if __name__ == '__main__':
  main(workload, synth)
