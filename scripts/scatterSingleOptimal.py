import pandas as pd
import os
import matplotlib.pyplot as plt

pagerank_single_optimal = ["wiki-topcats.txt", "athletes_edges.txt", "company_edges.txt", "deezer_europe_edges.txt", "email-Eu-core.txt", "facebook_combined.txt", "government_edges.txt", "HR_edges.txt", "HU_edges.txt", "musae_crocodile_edges.txt", "musae_DE_edges.txt", "musae_ENGB_edges.txt", "musae_ES_edges.txt", "musae_facebook_edges.txt", "musae_FR_edges.txt", "musae_PTBR_edges.txt", "musae_RU_edges.txt", "musae_squirrel_edges.txt", "new_sites_edges.txt", "p2p-Gnutella04.txt", "p2p-Gnutella05.txt", "p2p-Gnutella06.txt", "politician_edges.txt", "public_figure_edges.txt", "soc-sign-bitcoinotc-edit.txt", "soc-sign-Slashdot090221-edit.txt", "wiki-Vote.txt"]

bfs_single_optimal = ["loc-gowalla_edges.txt"]

#bc_single_optimal = ["V=20000_D=50.txt", "V=20000_D=500.txt"]
bc_single_optimal = []

sssp_single_optimal = ["amazon0302.txt", "amazon0312.txt", "amazon0505.txt", "athlete_edges.txt", "CollegeMsg-edit.txt", "company_edges.txt", "HR_edges.txt", "lastfm_asia_edges.txt", "loc-gowalla_edges.txt", "musae_DE_edges.txt", "musae_ENGB_edges.txt", "musae_ES_edges.txt", "musae_FR_edges.txt", "musae_git_edges.txt", "musae_PTBR_edges.txt", "musae_RU_edges.txt", "musae_squirrel_edges.txt", "new_sites_edges.txt", "p2p-Gnutella04.txt", "p2p-Gnutella06.txt", "politician_edges.txt", "public_figure_edges.txt", "soc-sign-bitcoinotc-edit.txt", "soc-sign-bitcoinotc-edit.txt", "soc-sign-Slashdot090221-edit.txt", "wiki-Vote.txt"]

def parse_single_optimal(optimal_path):
    with open(optimal_path, 'r') as optimal_f:
        lines = [line for line in optimal_f]
        if len(lines) != 4:
            return None, None
        optimal_pf = float(lines[0].strip())
        av = 0
        for l in lines[1:3]:
            av = av + float(l.strip())
        optimal_time = av / 3.0
    return optimal_pf, optimal_time

def parse_pg2(filepath):
    pg2_pf = []
    pg2_time = []
    with open(filepath, 'r') as f:
        lines = [line for line in f]
        for line in lines:
            elements = line.strip().split()
            if len(elements) == 3:
                pg2_pf.append(float(elements[2]))
                pg2_time.append(float(elements[0]))
    return pg2_pf, pg2_time

def generate_scatter_plot(percentage_dist, normalized_runtime):
    plt.figure(figsize=(10, 6))
    plt.scatter(percentage_dist, normalized_runtime, marker='o', alpha=0.5)
    plt.xlabel('Distance from Optimal Prefetch Distance')
    plt.ylabel('PG2 Speedup')
    plt.title('Speedup vs Distance from Optimal Prefetch Distance on all Single Optimal Inputs')
    plt.grid(True)
    plt.savefig("/home/nsobotka/floar/pg2_reloc/results/scatter/scatter.png")
    print("Saved figure at /home/nsobotka/floar/pg2_reloc/results/scatter/scatter.py")

def main():
    percentage_dist = []
    normalized_runtime = []
    # bfs
    files = [file for file in os.listdir("/home/soyoon/floar/pg2_reloc/results/bfs/cascade")]
    for file in files:
        optimal_path = "/home/nsobotka/floar/script_files_for_bolt_testing/bfsBoltOptimal/" + file
        pg2_path = "/home/soyoon/floar/pg2_reloc/results/bfs/cascade/" + file
        if not os.path.exists(optimal_path) or file not in bfs_single_optimal:
            continue
        optimal_pf, optimal_time = parse_single_optimal(optimal_path)
        if optimal_pf is None:
            continue
        pg2_pf, pg2_time = parse_pg2(pg2_path)
        if len(pg2_pf) == 0:
            continue
        percentage_dist = percentage_dist + [abs(optimal_pf - x) for x in pg2_pf]
        normalized_runtime = normalized_runtime + [optimal_time / x for x in pg2_time]
    # bc
    files = [file for file in os.listdir("/home/soyoon/floar/pg2_reloc/results/bc/cascade")]
    for file in files:
        optimal_path = "/home/nsobotka/floar/script_files_for_bolt_testing/bcBoltOptimal/" + file
        pg2_path = "/home/soyoon/floar/pg2_reloc/results/bc/cascade/" + file
        if not os.path.exists(optimal_path) or file not in bc_single_optimal:
            continue
        optimal_pf, optimal_time = parse_single_optimal(optimal_path)
        if optimal_pf is None:
            continue
        pg2_pf, pg2_time = parse_pg2(pg2_path)
        if len(pg2_pf) == 0:
            continue
        percentage_dist = percentage_dist + [abs(optimal_pf - x) for x in pg2_pf]
        normalized_runtime = normalized_runtime + [optimal_time / x for x in pg2_time]
    # sssp
    files = [file for file in os.listdir("/home/soyoon/floar/pg2_reloc/results/sssp/cascade")]
    for file in files:
        optimal_path = "/home/nsobotka/floar/script_files_for_bolt_testing/ssspBoltOptimal/" + file
        pg2_path = "/home/soyoon/floar/pg2_reloc/results/sssp/cascade/" + file
        if not os.path.exists(optimal_path) or file not in bfs_single_optimal:
            continue
        optimal_pf, optimal_time = parse_single_optimal(optimal_path)
        if optimal_pf is None:
            continue
        pg2_pf, pg2_time = parse_pg2(pg2_path)
        if len(pg2_pf) == 0:
            continue
        percentage_dist = percentage_dist + [abs(optimal_pf - x) for x in pg2_pf]
        normalized_runtime = normalized_runtime + [optimal_time / x for x in pg2_time]
    # pagerank
    files = [file for file in os.listdir("/home/soyoon/floar/pg2_reloc/results/pagerank/cascade")]
    for file in files:
        optimal_path = "/home/nsobotka/floar/script_files_for_bolt_testing/pagerankBoltOptimal/" + file
        pg2_path = "/home/soyoon/floar/pg2_reloc/results/pagerank/cascade/" + file
        if not os.path.exists(optimal_path) or file not in pagerank_single_optimal:
            continue
        optimal_pf, optimal_time = parse_single_optimal(optimal_path)
        if optimal_pf is None:
            continue
        pg2_pf, pg2_time = parse_pg2(pg2_path)
        if len(pg2_pf) == 0:
            continue
        percentage_dist = percentage_dist + [abs(optimal_pf - x) for x in pg2_pf]
        normalized_runtime = normalized_runtime + [optimal_time / x for x in pg2_time]

    generate_scatter_plot(percentage_dist, normalized_runtime)

if __name__ == "__main__":
    main()
