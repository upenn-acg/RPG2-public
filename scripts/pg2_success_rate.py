# Create the pg2 success rate graph
import os
import matplotlib.pyplot as plt

def count_successes(dirpath):
    s = 0
    m = 0
    f = 0
    for file in os.listdir(dirpath):
        with open(dirpath + "/" + file) as fi:
            lines = [line for line in fi]
            breaker = 0
            for line in lines:
                elements = line.strip().split()
                if len(elements) == 3 and len(lines) == 6:
                    s += 1
                    breaker = 1
                    break
                elif len(elements) == 3:
                    breaker = 1
                    m += 1
                    break
            if breaker == 0:
                f += 1
    print(s, m, f)
    return s, m, f
                

def generate_plot():
    # Sample data (proportions for each category and each bar)
    bars = ['SSSP', 'BC', 'BFS', 'PR']
    successful = []
    mix = []
    fail = []

    #sssp
    s, m, f = count_successes("/home/soyoon/floar/pg2_reloc/results/sssp/cascade")
    total = s + m + f
    successful.append(s / total)
    mix.append(m / total)
    fail.append(f / total)
    
    #bc
    s, m, f = count_successes("/home/soyoon/floar/pg2_reloc/results/bc/cascade")
    total = s + m + f
    successful.append(s / total)
    mix.append(m / total)
    fail.append(f / total)
    
    #bfs
    s, m, f = count_successes("/home/soyoon/floar/pg2_reloc/results/bfs/cascade")
    total = s + m + f
    successful.append(s / total)
    mix.append(m / total)
    fail.append(f / total)

    #pagerank
    s, m, f = count_successes("/home/soyoon/floar/pg2_reloc/results/pagerank/cascade")
    total = s + m + f
    successful.append(s / total)
    mix.append(m / total)
    fail.append(f / total)

    # Create stacked bar chart
    fig, ax = plt.subplots()

    # Calculate the total for each bar to normalize the bars
    totals = [s + m + f for s, m, f in zip(successful, mix, fail)]

    # Plot each category as a stacked bar for each bar
    for i, bar in enumerate(bars):
        if i == 0:
            ax.bar(bar, successful[i], label='Success', color='green')
            ax.bar(bar, mix[i], bottom=successful[i], label='Mix', color='yellow')
            ax.bar(bar, fail[i], bottom=successful[i] + mix[i], label='Fail', color='red')
        else:
            ax.bar(bar, successful[i], color='green')
            ax.bar(bar, mix[i], bottom=successful[i], color='yellow')
            ax.bar(bar, fail[i], bottom=successful[i] + mix[i], color='red')

    # Set the maximum value of the y-axis to 1
    #ax.set_ylim(0, 1)

    # Add a legend
    ax.legend()

    # Add labels and title
    ax.set_xlabel('Workload')
    ax.set_ylabel('Proportions')
    ax.set_title('Proportions of Successes, Mixes, and Failures on CRONO Workloads')

    # Save the plot as an image file (e.g., PNG or PDF)
    plt.tight_layout()
    plt.savefig('/home/nsobotka/floar/pg2_reloc/results/pg2_success_rate/pg2_success_rate.png')
    print("Saved figure at /home/nsobotka/floar/pg2_reloc/results/pg2_success_rate/pg2_success_rate.png")

def main():
    generate_plot()

if __name__ == "__main__":
    main()

