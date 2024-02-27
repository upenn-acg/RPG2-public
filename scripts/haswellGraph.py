import matplotlib.pyplot as plt
import os

def parsePG2(filepath):
    with open(filepath, 'r') as f:
        av = []
        for line in f:
            elements = line.strip().split()
            if len(elements) == 3:
               av.append(float(elements[0]))
        if len(av) == 0:
            return None
        return sum(av) / len(av)
            
def main():
    n = "/home/nsobotka/floar/pg2_reloc/results/"
    s = "/home/soyoon/floar/pg2_reloc/results/"
    
    # Replace the following with your actual speedup data as a list
    speedup_values = []
    # pagerank
    pagerank_cat = [file for file in os.listdir(n + "pagerank/cat")]
    for file in pagerank_cat:
        if not os.path.exists(s + "pagerank/cascade/" + file):
            continue
        cat_av = parsePG2(n + "pagerank/cat/" + file)
        cascade_av = parsePG2(s + "pagerank/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    # sssp
    sssp_cat = [file for file in os.listdir(n + "sssp/cat")]
    for file in sssp_cat:
        if not os.path.exists(s + "sssp/cascade/" + file):
            continue
        cat_av = parsePG2(n + "sssp/cat/" + file)
        cascade_av = parsePG2(s + "sssp/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    # bc
    bc_cat = [file for file in os.listdir(n + "bc/cat")]
    for file in bc_cat:
        if not os.path.exists(s + "bc/cascade/" + file):
            continue
        cat_av = parsePG2(n + "bc/cat/" + file)
        cascade_av = parsePG2(s + "bc/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    # bfs
    bfs_cat = [file for file in os.listdir(n + "bfs/cat")]
    for file in bfs_cat:
        if not os.path.exists(s + "bfs/cascade/" + file):
            continue
        cat_av = parsePG2(n + "bfs/cat/" + file)
        cascade_av = parsePG2(s + "bfs/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    # cg
    cg_cat = [file for file in os.listdir(n + "cg/cat")]
    for file in cg_cat:
        if not os.path.exists(s + "cg/cascade/" + file):
            continue
        cat_av = parsePG2(n + "cg/cat/" + file)
        cascade_av = parsePG2(s + "cg/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    # is
    is_cat = [file for file in os.listdir(n + "is/cat")]
    for file in is_cat:
        if not os.path.exists(s + "is/cascade/" + file):
            continue
        cat_av = parsePG2(n + "is/cat/" + file)
        cascade_av = parsePG2(s + "is/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    # randacc
    randacc_cat = [file for file in os.listdir(n + "randacc/cat")]
    for file in randacc_cat:
        if not os.path.exists(s + "randacc/cascade/" + file):
            continue
        cat_av = parsePG2(n + "randacc/cat/" + file)
        cascade_av = parsePG2(s + "randacc/cascade/" + file)
        if cat_av == None or cascade_av == None:
            continue
        speedup_values.append(cascade_av / cat_av)

    
    # Sort the speedup data in ascending order
    sorted_speedup = sorted(speedup_values)

    # Create the bar graph
    plt.bar(range(len(sorted_speedup)), sorted_speedup, align='center', color='b')

    # Add the black dotted line at 1
    plt.axhline(y=1, color='black', linestyle='dotted')

    # Remove x-axis labels
    plt.xticks([])

    # Add labels and title
    plt.ylabel('Speedup')
    plt.title('Speedup Comparison between Haswell and Cascade Lake')

    # Save the plot as an image in the specified directory (change '/path/to/directory' to your desired directory)
    plt.tight_layout()
    plt.savefig('/home/nsobotka/floar/pg2_reloc/results/haswellComparison/haswellComparison.png')
    print("Figure saved to /home/nsobotka/floar/pg2_reloc/results/haswellComparison/haswellComparison.png")

if __name__ == "__main__":
    main()
