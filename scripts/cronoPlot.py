import os
import sys
import matplotlib.pyplot as plt
import numpy as np

#pagerank
pagerank_pg2_path = "/home/soyoon/floar/pg2_reloc/results/pagerank/cascade"
pagerank_apt_path = "/home/soyoon/floar/apt-get/scripts_pr/pagerankData"
pagerank_bolt_path = "/home/soyoon/floar/script_files_for_bolt_testing/pagerankBoltOptimal"

#sssp
sssp_pg2_path = "/home/soyoon/floar/pg2_reloc/results/sssp/cascade"
sssp_bolt_path = "/home/nsobotka/floar/script_files_for_bolt_testing/ssspBoltOptimal"

#bfs
bfs_pg2_path = "/home/soyoon/floar/pg2_reloc/results/bfs/cascade"
bfs_bolt_path = "/home/nsobotka/floar/script_files_for_bolt_testing/bfsBoltOptimal"

#bc
bc_pg2_path = "/home/soyoon/floar/pg2_reloc/results/bc/cascade"
bc_apt_path = "/home/soyoon/floar/apt-get/scripts_bc/bcData"
bc_bolt_path = "/home/nsobotka/floar/script_files_for_bolt_testing/bcBoltOptimal"

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

def parse_apt(file_path):
    values = []
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        for line in lines:
            elements = line.strip().split()
            values.append(float(elements[0]))
    return values
                   

def generate_graph():
    #pagerank
    pagerank_files = [file for file in os.listdir(pagerank_pg2_path)]
    pagerank_al = []
    pagerank_s = []
    pagerank_ap = []
    pagerank_b = []
    for file in pagerank_files:
        if not os.path.exists(pagerank_apt_path + "/" + file) or not os.path.exists(pagerank_bolt_path + "/" + file):
            continue
        baseline, pagerank_pg2_all, pagerank_pg2_succ = parse_pg2(pagerank_pg2_path + "/" + file)
        pagerank_apt_data = parse_apt(pagerank_apt_path + "/" + file)
        pagerank_bolt_data = parse_bolt(pagerank_bolt_path + "/" + file)
        if len(pagerank_pg2_all) == 0 or len(pagerank_pg2_succ) == 0:
            continue
        pagerank_al.append(baseline / (sum(pagerank_pg2_all) / len(pagerank_pg2_all)))
        pagerank_s.append(baseline / (sum(pagerank_pg2_succ) / len(pagerank_pg2_succ)))
        pagerank_ap.append(baseline / (sum(pagerank_apt_data) / len(pagerank_apt_data)))
        pagerank_b.append(baseline / (sum(pagerank_bolt_data) / len(pagerank_bolt_data)))

    #sssp
    sssp_files = [file for file in os.listdir(sssp_pg2_path)]
    sssp_al = []
    sssp_s = []
    sssp_b = []
    for file in sssp_files:
        if not os.path.exists(sssp_bolt_path + "/" + file):
            continue
        baseline, sssp_pg2_all, sssp_pg2_succ = parse_pg2(sssp_pg2_path + "/" + file)
        sssp_bolt_data = parse_bolt(sssp_bolt_path + "/" + file)
        if len(sssp_pg2_all) == 0 or len(sssp_pg2_succ) == 0:
            continue
        sssp_al.append(baseline / (sum(sssp_pg2_all) / len(sssp_pg2_all)))
        sssp_s.append(baseline / (sum(sssp_pg2_succ) / len(sssp_pg2_succ)))
        sssp_b.append(baseline / (sum(sssp_bolt_data) / len(sssp_bolt_data)))

    #bfs
    bfs_files = [file for file in os.listdir(bfs_pg2_path)]
    bfs_al = []
    bfs_s = []
    bfs_b = []
    for file in bfs_files:
        if not os.path.exists(bfs_bolt_path + "/" + file):
            continue
        baseline, bfs_pg2_all, bfs_pg2_succ = parse_pg2(bfs_pg2_path + "/" + file)
        bfs_bolt_data = parse_bolt(bfs_bolt_path + "/" + file)
        if len(bfs_pg2_all) == 0 or len(bfs_pg2_succ) == 0:
            continue
        bfs_al.append(baseline / (sum(bfs_pg2_all) / len(bfs_pg2_all)))
        bfs_s.append(baseline / (sum(bfs_pg2_succ) / len(bfs_pg2_succ)))
        bfs_b.append(baseline / (sum(bfs_bolt_data) / len(bfs_bolt_data)))

    #bc
    bc_files = [file for file in os.listdir(bc_pg2_path)]
    bc_al = []
    bc_s = []
    bc_ap = []
    bc_b = []
    for file in bc_files:
        if not os.path.exists(bc_apt_path + "/" + file) or not os.path.exists(bc_bolt_path + "/" + file):
            continue
        baseline, bc_pg2_all, bc_pg2_succ = parse_pg2(bc_pg2_path + "/" + file)
        bc_apt_data = parse_apt(bc_apt_path + "/" + file)
        bc_bolt_data = parse_bolt(bc_bolt_path + "/" + file)
        if bc_pg2_all == None or len(bc_pg2_all) == 0 or len(bc_pg2_succ) == 0 or len(bc_apt_data) == 0 or len(bc_bolt_data) == 0:
            continue
        bc_al.append(baseline / (sum(bc_pg2_all) / len(bc_pg2_all)))
        bc_s.append(baseline / (sum(bc_pg2_succ) / len(bc_pg2_succ)))
        bc_ap.append(baseline / (sum(bc_apt_data) / len(bc_apt_data)))
        if baseline / (sum(bc_apt_data) / len(bc_apt_data)) > 2:
            print(baseline, bc_apt_data)
            print(file)
        #print(bc_ap)
        bc_b.append(baseline / (sum(bc_bolt_data) / len(bc_bolt_data)))


    x_labels = ["Pagerank All Data", "Pagerank Speedup", "Pagerank Slowdown", "SSSP All Data", "SSSP Speedup", "SSSP Slowdown", "BFS All Data", "BFS Speedup", "BFS Slowdown", "BC All Data", "BC Speedup", "BC Slowdown"]
    x = np.arange(len(x_labels))
    fig, ax = plt.subplots(figsize=(12, 8))

    pagerank_al_sp = [x for x, y in zip(pagerank_al, pagerank_b) if y >= 1]
    pagerank_al_sl = [x for x, y in zip(pagerank_al, pagerank_b) if y < 1]

    pagerank_succ_sp = [x for x, y in zip(pagerank_s, pagerank_b) if y >= 1]
    pagerank_succ_sl = [x for x, y in zip(pagerank_s, pagerank_b) if y < 1]

    pagerank_apt_sp = [x for x, y in zip(pagerank_ap, pagerank_b) if y >= 1]
    pagerank_apt_sl = [x for x, y in zip(pagerank_ap, pagerank_b) if y < 1]

    pagerank_bolt_sp = [x for x, y in zip(pagerank_b, pagerank_b) if y >= 1]
    pagerank_bolt_sl = [x for x, y in zip(pagerank_b, pagerank_b) if y < 1]
    

    
    sssp_al_sp = [x for x, y in zip(sssp_al, sssp_b) if y >= 1]
    sssp_al_sl = [x for x, y in zip(sssp_al, sssp_b) if y < 1]

    sssp_succ_sp = [x for x, y in zip(sssp_s, sssp_b) if y >= 1]
    sssp_succ_sl = [x for x, y in zip(sssp_s, sssp_b) if y < 1]

    sssp_apt_sp = [0]
    sssp_apt_sl = [0]

    sssp_bolt_sp = [x for x, y in zip(sssp_b, sssp_b) if y >= 1]
    sssp_bolt_sl = [x for x, y in zip(sssp_b, sssp_b) if y < 1]


    
    bfs_al_sp = [x for x, y in zip(bfs_al, bfs_b) if y >= 1]
    bfs_al_sl = [x for x, y in zip(bfs_al, bfs_b) if y < 1]

    bfs_succ_sp = [x for x, y in zip(bfs_s, bfs_b) if y >= 1]
    bfs_succ_sl = [x for x, y in zip(bfs_s, bfs_b) if y < 1]

    bfs_apt_sp = [0]
    bfs_apt_sl = [0]

    bfs_bolt_sp = [x for x, y in zip(bfs_b, bfs_b) if y >= 1]
    bfs_bolt_sl = [x for x, y in zip(bfs_b, bfs_b) if y < 1]


    bc_al_sp = [x for x, y in zip(bc_al, bc_b) if y >= 1]
    bc_al_sl = [x for x, y in zip(bc_al, bc_b) if y < 1]

    bc_succ_sp = [x for x, y in zip(bc_s, bc_b) if y >= 1]
    bc_succ_sl = [x for x, y in zip(bc_s, bc_b) if y < 1]

    bc_apt_sp = [x for x, y in zip(bc_ap, bc_b) if y >= 1]
    bc_apt_sl = [x for x, y in zip(bc_ap, bc_b) if y < 1]

    bc_bolt_sp = [x for x, y in zip(bc_b, bc_b) if y >= 1]
    bc_bolt_sl = [x for x, y in zip(bc_b, bc_b) if y < 1]

    counts = [len(pagerank_b), len([x for x in pagerank_b if x >= 1]), len([x for x in pagerank_b if x < 1]),
              len(sssp_b), len([x for x in sssp_b if x >= 1]), len([x for x in sssp_b if x < 1]),
              len(bfs_b), len([x for x in bfs_b if x >= 1]), len([x for x in bfs_b if x < 1]),
              len(bc_b), len([x for x in bc_b if x >= 1]), len([x for x in bc_b if x < 1])]
    

    pg2_all = [np.mean(pagerank_al), np.mean(pagerank_al_sp), np.mean(pagerank_al_sl), np.mean(sssp_al), np.mean(sssp_al_sp), np.mean(sssp_al_sl), np.mean(bfs_al), np.mean(bfs_al_sp), np.mean(bfs_al_sl), np.mean(bc_al), np.mean(bc_al_sp), np.mean(bc_al_sl)]
    pg2_all_std = [np.std(pagerank_al), np.std(pagerank_al_sp), np.std(pagerank_al_sl), np.std(sssp_al), np.std(sssp_al_sp), np.std(sssp_al_sl), np.std(bfs_al), np.std(bfs_al_sp), np.std(bfs_al_sl), np.std(bc_al), np.std(bc_al_sp), np.std(bc_al_sl)]
    
    pg2_succ = [np.mean(pagerank_s), np.mean(pagerank_succ_sp), np.mean(pagerank_succ_sl), np.mean(sssp_s), np.mean(sssp_succ_sp), np.mean(sssp_succ_sl), np.mean(bfs_s), np.mean(bfs_succ_sp), np.mean(bfs_succ_sl), np.mean(bc_s), np.mean(bc_succ_sp), np.mean(bc_succ_sl)]
    pg2_succ_std = [np.std(pagerank_s), np.std(pagerank_succ_sp), np.std(pagerank_succ_sl), np.std(sssp_s), np.std(sssp_succ_sp), np.std(sssp_succ_sl), np.std(bfs_s), np.std(bfs_succ_sp), np.std(bfs_succ_sl), np.std(bc_s), np.std(bc_succ_sp), np.std(bc_succ_sl)]
    
    apt_all = [np.mean(pagerank_ap), np.mean(pagerank_apt_sp), np.mean(pagerank_apt_sl), 0, np.mean(sssp_apt_sp), np.mean(sssp_apt_sl), 0, np.mean(bfs_apt_sp), np.mean(bfs_apt_sl), np.mean(bc_ap), np.mean(bc_apt_sp), np.mean(bc_apt_sl)]
    apt_all_std = [np.std(pagerank_ap), np.std(pagerank_apt_sp), np.std(pagerank_apt_sl), 0, np.std(sssp_apt_sp), np.std(sssp_apt_sl), 0, np.std(bfs_apt_sp), np.std(bfs_apt_sl), np.std(bc_ap), np.std(bc_apt_sp), np.std(bc_apt_sl)]
    
    bolt_all = [np.mean(pagerank_b), np.mean(pagerank_bolt_sp), np.mean(pagerank_bolt_sl), np.mean(sssp_b), np.mean(sssp_bolt_sp), np.mean(sssp_bolt_sl), np.mean(bfs_b), np.mean(bfs_bolt_sp), np.mean(bfs_bolt_sl), np.mean(bc_b), np.mean(bc_bolt_sp), np.mean(bc_bolt_sl)]
    bolt_all_std = [np.std(pagerank_b), np.std(pagerank_bolt_sp), np.std(pagerank_bolt_sl), np.std(sssp_b), np.std(sssp_bolt_sp), np.std(sssp_bolt_sl), np.std(bfs_b), np.std(bfs_bolt_sp), np.std(bfs_bolt_sl), np.std(bc_b), np.std(bc_bolt_sp), np.std(bc_bolt_sl)]
    
    
    # Set the width of the bars
    bar_width = 0.2
    
    plt.bar(x - 1.5 * bar_width, pg2_all, bar_width, yerr=pg2_all_std, capsize=5, label='All PG2 Results')
    plt.bar(x - 0.5 * bar_width, pg2_succ, bar_width, yerr=pg2_succ_std, capsize=5, label='Successful PG2 Results')
    plt.bar(x + 0.5 * bar_width, bolt_all, bar_width, yerr=bolt_all_std, capsize=5, label='Optimal Bolt')
    plt.bar(x + 1.5 * bar_width, apt_all, bar_width, yerr=apt_all_std, capsize=5, label='APT-GET')
    plt.axhline(y=1.0, color='black', linestyle='dashed', label='Baseline')


    # Add in the counts of each group size
    for i, v in enumerate(counts):
        plt.text(i, 1.6, str(v), ha='center', va='bottom')

    # Add labels and title
    plt.ylabel('Speedup')
    plt.title('CRONO Workloads')
    plt.xticks(x, x_labels, rotation='vertical')
    plt.legend()
    plt.legend(title='Error Bars (std)')
    plt.tight_layout()

    # Save the plot
    plt.savefig("/home/nsobotka/floar/pg2_reloc/results/cronoPlot/cronoPlot.png")
    print("graph saved at /home/nsobotka/floar/pg2_reloc/results/cronoPlot/cronoPlot.png")

        
        

if __name__ == "__main__":
    generate_graph()

