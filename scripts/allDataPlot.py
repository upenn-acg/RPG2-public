import os
import sys
import matplotlib.pyplot as plt
import numpy as np

def parse_pg2(file_path):
    pg2_values_all = []
    pg2_values_only5 = []
    bolt_values = []
    pref_dist = []
    baseline = None
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        if len(lines) == 0:
            return (None, None, None, None, None)
        for line in lines[:-1]:
            elements = line.strip().split()
            if len(elements) == 3:
            #if len(elements) == 3 and len(pg2_values) == 0:
                pg2_values_all.append(float(elements[0]))
                pg2_values_only5.append(float(elements[0]))
                bolt_values.append(float(elements[1]))
                pref_dist.append(float(elements[2]))
            if len(elements) == 1:
                pg2_values_all.append(float(elements[0]))

        elements = lines[-1].strip().split()
        if (len(elements) != 1):
            return (None, None, None, None, None)
        baseline = float(elements[0])
    if pg2_values_all and baseline != None and len(pg2_values_all) > 0 and len(bolt_values) > 0:
        return (pg2_values_all, bolt_values, baseline, pref_dist, pg2_values_only5)
    else:
        return (None, None, None, None, None)

def parse_apt_get(file_path):
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        apt_values = []
        for line in lines:
            elements = line.strip().split()
            apt_values.append(float(elements[0]))
        return (sum(apt_values) / len(apt_values), min(apt_values), max(apt_values))

def parse_bolt_optimal(file_path):
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        bolt_values = []
        for line in lines[1:]:
            print(line.strip())
            elements = line.strip().split()
            if len(elements) > 0:
                bolt_values.append(float(elements[0]))
        return (sum(bolt_values) / len(bolt_values), min(bolt_values), max(bolt_values))

def g_mean(x):
    a = np.log(x)
    return np.exp(a.mean())


def averages(pg2_values_all, bolt_values, baseline, pref_dist, pg2_values_only5):
    return (sum(pg2_values_all) / len(pg2_values_all), sum(bolt_values) / len(bolt_values), baseline, None, sum(pg2_values_only5) / len(pg2_values_only5))

def minMax(pg2_values_all, bolt_values, pg2_values_only5):
    return (min(pg2_values_all), max(pg2_values_all), min(bolt_values), max(bolt_values), min(pg2_values_only5), max(pg2_values_only5))




def summaryPlot(pg2_data_all, pg2_data_only5, bolt_data, apt_get_data, boltOpt, workload, machine):

    x_labels = ["All data", "Speedup", "Slowdown"]
    x = np.arange(len(x_labels))
    
    o_pg2_all_geomean = [g_mean(pg2_data_all), g_mean([x for x in pg2_data_all if x >= 1]), g_mean([x for x in pg2_data_all if x < 1])]
    minO_all = [min(pg2_data_all), min([x for x in pg2_data_all if x >= 1]), min([x for x in pg2_data_all if x < 1])]
    maxO_all = [max(pg2_data_all), max([x for x in pg2_data_all if x >= 1]), max([x for x in pg2_data_all if x < 1])]
    o_pg2_success_geomean = [g_mean(pg2_data_only5), g_mean([x for x in pg2_data_only5 if x >= 1]), g_mean([x for x in pg2_data_only5 if x < 1])]
    minO_succ = [min(pg2_data_only5), min([x for x in pg2_data_only5 if x >= 1]), min([x for x in pg2_data_only5 if x < 1])]
    maxO_succ = [max(pg2_data_only5), max([x for x in pg2_data_only5 if x >= 1]), max([x for x in pg2_data_only5 if x < 1])]
    o_bolt_geomean = [g_mean(bolt_data), g_mean([x for x in bolt_data if x >= 1]), g_mean([x for x in bolt_data if x < 1])]
    minO_bolt = [min(bolt_data), min([x for x in bolt_data if x >= 1]), min([x for x in bolt_data if x < 1])]
    maxO_bolt = [max(bolt_data), max([x for x in bolt_data if x >= 1]), max([x for x in bolt_data if x < 1])]
    if len(apt_get_data) > 0:
        o_apt_geomean = [g_mean(apt_get_data), g_mean([x for x in apt_get_data if x >= 1]), g_mean([x for x in apt_get_data if x < 1])]
        minO_apt = [min(apt_get_data), min([x for x in apt_get_data if x >= 1]), min([x for x in apt_get_data if x < 1])]
        maxO_apt = [max(apt_get_data), max([x for x in apt_get_data if x >= 1]), max([x for x in apt_get_data if x < 1])]

    greaterThan = [x for x in boltOpt if x >= 1]
    lessThan = [x for x in boltOpt if x < 1]
    if len(greaterThan) > 0:
        minG = min(greaterThan)
        maxG = max(greaterThan)
    else:
        minG = 1
        maxG = 1
    if len(lessThan) > 0:
        minL = min(lessThan)
        maxL = max(lessThan)
    else:
        minL = 1
        maxL = 1
    boltOpt_geo = [g_mean(boltOpt), g_mean([x for x in boltOpt if x >= 1]), g_mean([x for x in boltOpt if x < 1])]
    boltOpt_min = [min(boltOpt), minG, minL]
    boltOpt_max = [max(boltOpt), maxG, maxL]

    width = 0.15
    fig, ax = plt.subplots(figsize=(12, 8))
    rects1 = ax.bar(x - 2 * width, o_pg2_all_geomean, width, label = 'pg2_all_results')
    error_sizesAll = np.array([np.array(o_pg2_all_geomean) - np.array(minO_all), np.array(maxO_all) - np.array(o_pg2_all_geomean)])
    ax.errorbar(x - 2 * width, o_pg2_all_geomean, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black', label='Min/Max')

    if len(apt_get_data) > 0:
        rects2 = ax.bar(x - 1 * width, o_apt_geomean, width, label = 'apt-get')
        error_sizesAll = np.array([np.array(o_apt_geomean) - np.array(minO_apt), np.array(maxO_apt) - np.array(o_apt_geomean)])
        ax.errorbar(x - 1 * width, o_apt_geomean, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')

    rects3 = ax.bar(x + 1 * width, o_bolt_geomean, width, label = 'bolt')
    error_sizesAll = np.array([np.array(o_bolt_geomean) - np.array(minO_bolt), np.array(maxO_bolt) - np.array(o_bolt_geomean)])
    ax.errorbar(x + 1 * width, o_bolt_geomean, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')


    rects4 = ax.bar(x + 2 * width, o_pg2_success_geomean, width, label = 'pg2_successes')
    error_sizesAll = np.array([np.array(o_pg2_success_geomean) - np.array(minO_succ), np.array(maxO_succ) - np.array(o_pg2_success_geomean)])
    ax.errorbar(x + 2 * width, o_pg2_success_geomean, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')

    rects5 = ax.bar(x, boltOpt_geo, width, label = 'optimal_bolt')
    error_sizesAll = np.array([np.array(boltOpt_geo) - np.array(boltOpt_min), np.array(boltOpt_max) - np.array(boltOpt_geo)])
    ax.errorbar(x, boltOpt_geo, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')

    ax.axhline(y=1.0, color='black', linestyle='dashed', label='Baseline')

    ax.set_ylabel('Speedup (x)')
    ax.set_title('Speedup Comparison of ' + workload + ' on ' + machine)
    ax.legend()
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation='vertical')

    plt.tight_layout()
    
    result_graph = "../results/all_inputs/" + workload + "Summary.png"
    plt.savefig(result_graph)
    plt.close()

def generate_graph(workload, machine):
    homeDirec = "/home/nsobotka/"
    addOn = ""
    if machine == "cascade":
        homeDirec = "/home/soyoon/"
        #if workload == "pagerank":
         #   addOn = "_twosecond"

    files = [file for file in os.listdir(homeDirec + "floar/pg2_reloc/results/" + workload + "/" + machine + addOn + "/") if file.endswith('.txt')]
    #files = [file for file in os.listdir(homeDirec + "floar/pg2_reloc/results/" + workload + "/" + machine + "Old" + addOn + "/") if file.endswith('.txt')]
    pg2_data_all = []
    pg2_data_only5 = []
    bolt_data = []
    apt_get_data = []
    x_labels = []
    pref_dist = []
    bolt_opt = []

    allMins = []
    allMaxs = []
    boltMins = []
    boltMaxs = []
    onlyMins = []
    onlyMaxs = []
    aptMins = []
    aptMaxs = []
    boltOptMins = []
    boltOptMaxs = []

    for file in files:
        (pg2_values_all, bolt_values, baseline, pref_di, pg2_values_only5) = parse_pg2(homeDirec + "floar/pg2_reloc/results/" + workload + "/" + machine + addOn + "/" + file)
        #(pg2_average, bolt_average, baseline, pref_di) = parse_pg2(homeDirec + "floar/pg2_reloc/results/" + workload + "/" + machine + "Old" + addOn + "/" + file)
        if pg2_values_all is not None:
            if not os.path.exists("/home/soyoon/floar/script_files_for_bolt_testing/" + workload + "BoltOptimal/" + file) and (workload == "pagerank"):
                continue
            elif not os.path.exists("/home/nsobotka/floar/script_files_for_bolt_testing/" + workload + "BoltOptimal/" + file):
                continue
            (allMin, allMax, boltMin, boltMax, onlyMin, onlyMax) = minMax(pg2_values_all, bolt_values, pg2_values_only5)
            (pg2_average_all, bolt_average, baseline, pref_dist, pg2_average_only5) = averages(pg2_values_all, bolt_values, baseline, pref_dist, pg2_values_only5)

            if workload == "pagerank":
                (apt_av, apt_min, apt_max) = parse_apt_get(homeDirec + "floar/apt-get/scripts_pr/pagerankData/" + file)
                (boltOpt_av, boltOpt_min, boltOpt_max) = parse_bolt_optimal(homeDirec + "floar/script_files_for_bolt_testing/pagerankBoltOptimal/" + file)
                bolt_opt.append(baseline / boltOpt_av)
                boltOptMins.append(baseline / boltOpt_min)
                boltOptMaxs.append(baseline / boltOpt_max)
                apt_get_data.append(baseline / apt_av)
                aptMins.append(baseline / apt_min)
                aptMaxs.append(baseline / apt_max)
            elif workload == "bfs":
                #apt_get_data.append(baseline / parse_apt_get(homeDirec + "floar/apt-get/scripts_bfs/bfsData/" + file))
                apt_get_data = []
                (boltOpt_av, boltOpt_min, boltOpt_max) = parse_bolt_optimal(homeDirec + "floar/script_files_for_bolt_testing/bfsBoltOptimal/" + file)
                bolt_opt.append(baseline / boltOpt_av)
                boltOptMins.append(baseline / boltOpt_min)
                boltOptMaxs.append(baseline / boltOpt_max)
            elif workload == "sssp":
                apt_get_data = []
                (boltOpt_av, boltOpt_min, boltOpt_max) = parse_bolt_optimal("/home/nsobotka/floar/script_files_for_bolt_testing/ssspBoltOptimal/" + file)
                bolt_opt.append(baseline / boltOpt_av)
                boltOptMins.append(baseline / boltOpt_min)
                boltOptMaxs.append(baseline / boltOpt_max)
            elif workload == "bc":
                (apt_av, apt_min, apt_max) = parse_apt_get(homeDirec + "floar/apt-get/scripts_bc/bcData/" + file)
                (boltOpt_av, boltOpt_min, boltOpt_max) = parse_bolt_optimal(homeDirec + "floar/script_files_for_bolt_testing/bcBoltOptimal/" + file)
                bolt_opt.append(baseline / boltOpt_av)
                boltOptMins.append(baseline / boltOpt_min)
                boltOptMaxs.append(baseline / boltOpt_max)
                apt_get_data.append(baseline / apt_av)
                aptMins.append(baseline / apt_min)
                aptMaxs.append(baseline / apt_max)
            elif workload == "is" or workload == "cg" or workload == "randacc":
                apt_get_data = []
                (boltOpt_av, boltOpt_min, boltOpt_max) = parse_bolt_optimal("/home/nsobotka/floar/script_files_for_bolt_testing/" + workload + "BoltOptimal/" + file)
                bolt_opt.append(baseline / boltOpt_av)
                boltOptMins.append(baseline / boltOpt_min)
                boltOptMaxs.append(baseline / boltOpt_max)
            else:
                print("update file path for apt get")
                return

            pg2_data_all.append(baseline / pg2_average_all)
            pg2_data_only5.append(baseline / pg2_average_only5)
            bolt_data.append(baseline / bolt_average)

            allMins.append(baseline / allMin)
            allMaxs.append(baseline / allMax)
            boltMins.append(baseline / boltMin)
            boltMaxs.append(baseline / boltMax)
            onlyMins.append(baseline / onlyMin)
            onlyMaxs.append(baseline / onlyMax)
            
            x_labels.append(file.replace('.txt', ''))
            
    if not pg2_data_all:
        print("No valid data found for the specified workload.")
        return

    if (workload != "is") and workload != "randacc" and workload != "cg":
        summaryPlot(pg2_data_all, pg2_data_only5, bolt_data, apt_get_data, bolt_opt, workload, machine)

    x = np.arange(len(x_labels))
    width = 0.15

    fig, ax = plt.subplots(figsize=(24, 16))
    rects1 = ax.bar(x - 2 * width, pg2_data_all, width, label='pg2_allResults')
    if len(apt_get_data) != 0:
        rects2 = ax.bar(x, apt_get_data, width, label='apt-get')
    rects3 = ax.bar(x + width, bolt_data, width, label='bolt')  # Add "bolt" data here
    rects4 = ax.bar(x - width, pg2_data_only5, width, label='pg2_successes')
    rects5 = ax.bar(x + 2 * width, bolt_opt, width, label='optimal_bolt')

    arr1 = np.array(pg2_data_all)
    arr2 = np.array(allMins)
    arr3 = np.array(allMaxs)
    error_sizesAll = np.array([arr2 - arr1, arr1 - arr3])
    ax.errorbar(x - 2 * width, pg2_data_all, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black', label='Min/Max')

    arr1 = np.array(bolt_data)
    arr2 = np.array(boltMins)
    arr3 = np.array(boltMaxs)
    error_sizesAll = np.array([arr2 - arr1, arr1 - arr3])
    ax.errorbar(x + width, bolt_data, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')

    arr1 = np.array(pg2_data_only5)
    arr2 = np.array(allMins)
    arr3 = np.array(allMaxs)
    error_sizesAll = np.array([arr2 - arr1, arr1 - arr3])
    ax.errorbar(x - width, pg2_data_only5, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')

    if len(apt_get_data) > 0:
        arr1 = np.array(apt_get_data)
        arr2 = np.array(aptMins)
        arr3 = np.array(aptMaxs)
        error_sizesAll = np.array([arr2 - arr1, arr1 - arr3])
        ax.errorbar(x, apt_get_data, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')

    arr1 = np.array(bolt_opt)
    arr2 = np.array(boltOptMins)
    arr3 = np.array(boltOptMaxs)
    error_sizesAll = np.array([arr2 - arr1, arr1 - arr3])
    ax.errorbar(x + 2 * width, bolt_opt, yerr=error_sizesAll, fmt='o', capsize=2, markersize=2, color='black')
    
    ax.axhline(y=1.0, color='black', linestyle='dashed', label='Baseline')

    ax.set_ylabel('Speedup (x)')
    ax.set_title('Speedup Comparison of ' + workload + ' on ' + machine)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation='vertical')
    ax.legend()

    plt.tight_layout()
    
    result_graph = "../results/all_inputs/" + workload + ".png"
    plt.savefig(result_graph)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 script_name.py <workload> <machine>")
    else:
        workload = sys.argv[1]
        machine = sys.argv[2]
        generate_graph(workload, machine)
