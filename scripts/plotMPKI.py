import os
import matplotlib.pyplot as plt
import numpy as np

def parse_file(filename):
    with open(filename, 'r') as file:
        instr_count, miss_count = map(int, file.readline().strip().split())
        return instr_count, miss_count

def calculate_mpki(instr_count, miss_count):
    return (miss_count / instr_count) * 1000

def plot_mpki_barchart(file_names, mpki_valuesPG2, mpki_valuesNOPG2, output_dir):
    #width = 0.2
    fig, ax = plt.subplots(figsize=(15, 9))
    x = np.arange(len(file_names))
    #mpki_valuesPG2.append(np.mean(mpki_valuesPG2))
    #mpki_valuesNOPG2.append(np.mean(mpki_valuesNOPG2))
    #file_names.append("average")
    rects1 = ax.bar(x - width, mpki_valuesPG2, width, label='pg2')
    rects2 = ax.bar(x, mpki_valuesNOPG2, width, label='original')
    ax.set_ylabel('MPKI (Misses per Kiloinstruction)')
    ax.set_title('MPKI for Pagerank on Cascade Lake')
    ax.set_xticks(x)
    ax.set_yscale('log')
    ax.set_xticklabels(file_names, rotation='vertical')
    ax.legend()

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mpki_scatter.png'))
    plt.close()

def mpki_vs_speedup(mpki_valuesPG2, mpki_valuesNOPG2, output_dir, times_PG2, times_orig):

    percent_increase_mpki = []
    speedup = []
    for i in range(len(mpki_valuesPG2)):
        #mpki = 100 * (mpki_valuesNOPG2[i] - mpki_valuesPG2[i]) / mpki_valuesNOPG2[i]
        mpki = mpki_valuesPG2[i] - mpki_valuesNOPG2[i]
        speedupNum = times_orig[i] / times_PG2[i]
        if mpki_valuesNOPG2[i] < mpki_valuesPG2[i]:
            print(mpki_valuesNOPG2[i], mpki_valuesPG2[i], times_orig[i], times_PG2[i])
        #if mpki > 1200 or speedupNum > 2:
        #continue
        percent_increase_mpki.append(mpki)
        speedup.append(speedupNum)
    
    plt.scatter(percent_increase_mpki, speedup)

    # Add labels and title
    plt.xlabel('Change in LLC MPKI')
    plt.ylabel('Speedup')
    plt.title('LLC MPKI')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mpki_scatter.png'))
    print("saved figure at " + output_dir + "/mpki_scatter")
    plt.close()

def parsePG2(file_path):
    baseline = None
    pg2_all = []
    with open(file_path, 'r') as file:
        lines = [line for line in file]
        if len(lines) < 2:
            return None, None
        for line in lines[:-1]:
            elements = line.strip().split()
            pg2_all.append(float(elements[0]))
        elements = lines[-1].strip().split()
        baseline = float(elements[0])
    if len(pg2_all) == 0:
        return None, None
    return (sum(pg2_all) / len(pg2_all)), baseline

    
def plot_instr_count_barchart(file_names, instr_countsPG2, instr_countsNOPG2, output_dir):
    #width = 0.2
    #fig, ax = plt.subplots(figsize=(15, 9))
    #x = np.arange(len(file_names))
    #instr_countsPG2.append(np.mean(instr_countsPG2))
    #instr_countsNOPG2.append(np.mean(instr_countsNOPG2))
    plt.figure(figsize=(10, 6))
    num_bins = 20
    res = []
    for i in range(len(instr_countsPG2)):
        res.append(instr_countsPG2[i] / instr_countsNOPG2[i])
    plt.hist(res, num_bins, edgecolor='black')
    #rects1 = ax.bar(x - width, instr_countsPG2, width, label='pg2')
    #rects2 = ax.bar(x, instr_countsNOPG2, width, label='original')
    #ax.set_ylabel('Dynamic Instruction Count')
    #ax.set_title('Dynamic Instruction Counts for Different Inputs')
    #ax.set_xticks(x)
    #ax.set_yscale('log')
    #ax.set_xticklabels(file_names, rotation='vertical')
    #ax.legend()

    #def autolabel(rects):
     #   for rect in rects:
      #      height = rect.get_height()
       #     ax.annotate('{}'.format(height),
        #                xy=(rect.get_x() + rect.get_width() / 2, height),
         #               xytext=(0, 3),  # 3 points vertical offset
          #              textcoords="offset points",
           #             ha='center', va='bottom')

    #plt.xlabel('Normalized Dynamic Instruction Count')
    plt.ylabel('Frequency')
    plt.title('Normalized Dynamic Instruction Count')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dynamic_instr_count_hist.png'))
    print("saved instruction count histogram at " + output_dir + "/dynamic_instr_count_hist")
def main(workload, machine):
    homeDirec = "/home/nsobotka/floar/pg2_reloc/"
    if machine == "cascade":
        homeDirec = "/home/soyoon/floar/pg2_reloc/"
    input_folderPG2 = homeDirec + 'results/' + workload + '_mpki/' + machine + '/data'
    input_folderNOPG2 = homeDirec + 'results/' + workload + '_mpki/' + machine + '/data_nopg2'
    output_dir = '../results/' + workload + '_mpki' + '/' +  machine + '/graphs'

    file_names = []
    mpki_valuesPG2 = []
    instr_countsPG2 = []
    mpki_valuesNOPG2 = []
    instr_countsNOPG2 = []

    times_PG2 = []
    times_orig = []

    for filename in os.listdir(input_folderPG2):
        if filename.endswith('.txt'):
            
            file_name = os.path.splitext(filename)[0]
            file_path = os.path.join(input_folderPG2, filename)
            instr_count, miss_count = parse_file(file_path)
            mpki = calculate_mpki(instr_count, miss_count)

            if miss_count > 8000:
                if not os.path.exists("/home/soyoon/floar/pg2_reloc/results/" + workload + "/" + machine + "/" + filename):
                    continue
                newTimePG2, newTimeOrig = parsePG2("/home/soyoon/floar/pg2_reloc/results/" + workload + "/" + machine + "/" + filename)
                if newTimePG2 == None:
                    continue
                times_PG2.append(newTimePG2)
                times_orig.append(newTimeOrig)
                
                file_names.append(file_name)
                mpki_valuesPG2.append(mpki)
                instr_countsPG2.append(instr_count)

                # Parse second file which contains the original execution data
                file_path = os.path.join(input_folderNOPG2, filename)
                instr_count, miss_count = parse_file(file_path)
                mpki = calculate_mpki(instr_count, miss_count)
                mpki_valuesNOPG2.append(mpki)
                instr_countsNOPG2.append(instr_count)


    #plot_mpki_barchart(file_names, mpki_valuesPG2, mpki_valuesNOPG2, output_dir)
    mpki_vs_speedup(mpki_valuesPG2, mpki_valuesNOPG2, output_dir, times_PG2, times_orig)
    plot_instr_count_barchart(file_names, instr_countsPG2, instr_countsNOPG2, output_dir)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python plot_data.py <workload> <machine>")
    else:
        main(sys.argv[1], sys.argv[2])
