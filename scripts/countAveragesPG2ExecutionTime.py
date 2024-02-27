import os
import sys
import numpy as np

def read_floats_from_file(file_path):
    with open(file_path, 'r') as file:
        print(file_path)
        return [float(line.strip()) for line in file]

def get_file_paths_in_directory(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def calculate_average_of_numbers_across_files(directory):
    file_paths = get_file_paths_in_directory(directory)
    num_files = len(file_paths)
    num_floats = 5

    # Initialize an array to store the sums of each number across files
    sums = np.zeros(num_floats)

    for file_path in file_paths:
        # Read floats from the file
        floats = read_floats_from_file(file_path)

        # Accumulate the floats to the sums array
        sums += floats

    # Calculate the average of each number across all files
    averages = sums / num_files

    return averages

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <workload>")
        sys.exit(1)

    directory_path = "/home/nsobotka/floar/pg2_reloc/results/pg2_performance/" + sys.argv[1]

    averages = calculate_average_of_numbers_across_files(directory_path)

    for i, avg in enumerate(averages, 1):
        print(f"The average of the {i}st number across all files: {avg:.6f}")
