import os
import sys
import matplotlib.pyplot as plt
import numpy as np

#cg
cg_pg2_path = "/home/soyoon/floar/pg2_reloc/results/cg/cascade"
cg_apt_path = "/home/nsobotka/floar/apt-get/scripts_cgo2017/cgData"
cg_bolt_path = "/home/nsobotka/floar/script_files_for_bolt_testing/cgBoltOptimal"
cg_hand_path = "/home/nsobotka/floar/pg2_reloc/results/cg/cascadeSWPF"

#is
is_pg2_path = "/home/soyoon/floar/pg2_reloc/results/is/cascade"
is_apt_path = "/home/nsobotka/floar/apt-get/scripts_cgo2017/isData"
is_bolt_path = "/home/nsobotka/floar/script_files_for_bolt_testing/isBoltOptimal"
is_hand_path = "/home/nsobotka/floar/pg2_reloc/results/is/cascadeSWPF"

#randacc
randacc_pg2_path = "/home/soyoon/floar/pg2_reloc/results/randacc/cascade"
randacc_apt_path = "/home/nsobotka/floar/apt-get/scripts_cgo2017/randaccData"
randacc_bolt_path = "/home/nsobotka/floar/script_files_for_bolt_testing/randaccBoltOptimal"
randacc_hand_path = "/home/nsobotka/floar/pg2_reloc/results/randacc/cascadeSWPF"

def parse_pg2(file_path):
    baseline = None
    pg2_all = []
    pg2_succ = []
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        if len(lines) < 2:
            return None, None, None
        for line in lines[:-1]:
            elements = line.strip().split()
            if len(elements) == 3:
                pg2_succ.append(float(elements[0]))
                pg2_all.append(float(elements[0]))
            elif len(elements) == 1:
                pg2_all.append(float(elements[0]))
        elements = lines[-1].strip().split()
        baseline = float(elements[0])
    return baseline, pg2_all, pg2_succ
            
def parse_bolt(file_path):
    values = []
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        for line in lines[1:]:
            elements = line.strip().split()
            if len(elements) > 0:
                values.append(float(elements[0]))
    return values
            
def parse_apt_hand(file_path):
    values = []
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        for line in lines:
            elements = line.strip().split()
            values.append(float(elements[0]))
    return values
        
def generate_graph():
    #cg
    cg_files = [file for file in os.listdir(cg_pg2_path)]
    cg_all = []
    cg_succ = []
    cg_apt = []
    cg_bolt = []
    cg_hand = []
    for file in cg_files:
        baseline, cg_pg2_all, cg_pg2_succ = parse_pg2(cg_pg2_path + "/" + file)
        cg_apt_data = parse_apt_hand(cg_apt_path + "/" + file)
        cg_bolt_data = parse_bolt(cg_bolt_path + "/" + file)
        cg_hand_data = parse_apt_hand(cg_hand_path + "/" + file)
        if len(cg_pg2_all) == 0 or len(cg_pg2_succ) == 0:
            continue
        cg_all.append(baseline / (sum(cg_pg2_all) / len(cg_pg2_all)))
        cg_succ.append(baseline / (sum(cg_pg2_succ) / len(cg_pg2_succ)))
        cg_apt.append(baseline / (sum(cg_apt_data) / len(cg_apt_data)))
        cg_bolt.append(baseline / (sum(cg_bolt_data) / len(cg_bolt_data)))
        cg_hand.append(baseline / (sum(cg_hand_data) / len(cg_hand_data)))


    #is
    is_files = [file for file in os.listdir(is_pg2_path)]
    is_all = []
    is_succ = []
    is_apt = []
    is_bolt = []
    is_hand = []
    for file in is_files:
        baseline, is_pg2_all, is_pg2_succ = parse_pg2(is_pg2_path + "/" + file)
        is_apt_data = parse_apt_hand(is_apt_path + "/" + file)
        is_bolt_data = parse_bolt(is_bolt_path + "/" + file)
        is_hand_data = parse_apt_hand(is_hand_path + "/" + file)
        if len(is_pg2_all) == 0 or len(is_pg2_succ) == 0:
            continue
        is_all.append(baseline / (sum(is_pg2_all) / len(is_pg2_all)))
        is_succ.append(baseline / (sum(is_pg2_succ) / len(is_pg2_succ)))
        is_apt.append(baseline / (sum(is_apt_data) / len(is_apt_data)))
        is_bolt.append(baseline / (sum(is_bolt_data) / len(is_bolt_data)))
        is_hand.append(baseline / (sum(is_hand_data) / len(is_hand_data)))

    #randacc
    randacc_files = [file for file in os.listdir(randacc_pg2_path)]
    randacc_all = []
    randacc_succ = []
    randacc_apt = []
    randacc_bolt = []
    randacc_hand = []
    for file in randacc_files:
        baseline, randacc_pg2_all, randacc_pg2_succ = parse_pg2(randacc_pg2_path + "/" + file)
        randacc_apt_data = parse_apt_hand(randacc_apt_path + "/" + file)
        randacc_bolt_data = parse_bolt(randacc_bolt_path + "/" + file)
        randacc_hand_data = parse_apt_hand(randacc_hand_path + "/" + file)
        if len(randacc_pg2_all) == 0 or len(randacc_pg2_succ) == 0:
            continue
        randacc_all.append(baseline / (sum(randacc_pg2_all) / len(randacc_pg2_all)))
        randacc_succ.append(baseline / (sum(randacc_pg2_succ) / len(randacc_pg2_succ)))
        randacc_apt.append(baseline / (sum(randacc_apt_data) / len(randacc_apt_data)))
        randacc_bolt.append(baseline / (sum(randacc_bolt_data) / len(randacc_bolt_data)))
        randacc_hand.append(baseline / (sum(randacc_hand_data) / len(randacc_hand_data)))


    x_labels = ["CG", "IS", "RANDACC"]
    x = np.arange(len(x_labels))
    fig, ax = plt.subplots(figsize(12, 8))

    pg2_all = [np.mean(cg_all), np.mean(is_all), np.mean(randacc_all)]
    pg2_all_std = [np.std(cg_all), np.std(is_all), np.std(randacc_all)]

    pg2_succ = [np.mean(cg_succ), np.mean(is_succ), np.mean(randacc_succ)]
    pg2_succ_std = [np.std(cg_succ), np.std(is_succ), np.std(randacc_succ)]

    apt_all = [np.mean(cg_apt), np.mean(is_apt), np.mean(randacc_apt)]
    apt_all_std = [np.std(cg_apt), np.std(is_apt), np.std(randacc_apt)]

    bolt_all = [np.mean(cg_bolt), np.mean(is_bolt), np.mean(randacc_bolt)]
    bolt_all_std = [np.std(cg_bolt), np.std(is_bolt), np.std(randacc_bolt)]

    hand_all = [np.mean(cg_hand), np.mean(is_hand), np.mean(randacc_hand)]
    hand_all_std = [np.std(cg_hand), np.std(is_hand), np.std(randacc_hand)]

    bar_width = 0.2

    plt.bar(x - 2 * bar_width, pg2_all, bar_width, yerr=pg2_all_std, capsize=5, label='All PG2 Results')
    plt.bar(x - 1 * bar_width, pg2_succ, bar_width, yerr=pg2_succ_std, capsize=5, label='Successful PG2 Results')
    plt.bar(x + bar_width, bolt_all, bar_width, yerr=bolt_all_std, capsize=5, label='Optimal Bolt')
    plt.bar(x + 1 * bar_width, apt_all, bar_width, yerr=apt_all_std, capsize=5, label='APT-GET')
    plt.bar(x + 2 * bar_width, hand_all, bar_width, yerr=hand_all_std, capsize=5, label='SW Prefetching')
    plt.axhline(y=1.0, color='black', linestyle='dashed', label='Baseline')

    
    # Add labels and title
    plt.ylabel('Speedup')
    plt.title('CGO2017 Workloads')
    plt.xticks(x, x_labels, rotation='vertical')
    plt.legend()
    plt.legend(title='Error Bars (std)')
    plt.tight_layout()
    
    # Save the plot
    plt.savefig("/home/nsobotka/floar/pg2_reloc/results/cgoPlot/cgoPlot.png")
    print("graph saved at /home/nsobotka/floar/pg2_reloc/results/cgoPlot/cgoPlot.png")
    

if __name__ == "__main__":
    generate_graph()
