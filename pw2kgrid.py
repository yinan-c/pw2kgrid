import os
import re
import sys
import subprocess

BGW_path = "/mnt/zfsusers/ychen/programs/2019/BerkeleyGW-master/bin/"
if len(sys.argv) != 3:
    print("Usage: python3 atom_pos_v3.py scf_file output_kgrid_file")
    sys.exit()

output_file = sys.argv[2]

kgird = input("Enter 1x3 k gird: ")
# check user input for kgird for valid input of 3 integers
while True:
    try:
        kgird = [int(i) for i in kgird.split()]
        if len(kgird) == 3:
            break
        else:
            print("Error: invalid input")
            kgird = input("Enter 1x3 k gird: ")
    except ValueError:
        print("Error: invalid input")
        kgird = input("Enter 1x3 k gird: ")

kgird_shift = input("Enter 1x3 kgird shift: ")
# check user input for kgird shift for valid input of 3 floats
while True:
    try:
        kgird_shift = [float(i) for i in kgird_shift.split()]
        if len(kgird_shift) == 3:
            break
        else:
            print("Error: invalid input")
            kgird_shift = input("Enter 1x3 kgird shift: ")
    except ValueError:
        print("Error: invalid input")
        kgird_shift = input("Enter 1x3 kgird shift: ")

small_qgrid = input("Enter small 1x3 qgrid: ")
while True:
    try:
        small_qgrid = [float(i) for i in small_qgrid.split()]
        if len(small_qgrid) == 3:
            break
        else:
            print("Error: invalid input")
            small_qgrid = input("Enter small 1x3 q grid: ")
    except ValueError:
        print("Error: invalid input")
        small_qgrid = input("Enter small 1x3 q grid: ")

# dictionary for atomic symbols to numbers, add more if needed
symbol_dict = {"H": 1, "C": 6, "N": 7, "O": 8, "S": 16, "Pb": 82, "Cs": 55, "I": 53, "Br": 35, "Cl": 17, "Cu": 29}

with open(sys.argv[1], 'r') as f:
    file_contents = f.read()

# extract crystal lattice information
lattice = re.findall(r'a\(\d\)\s*=\s*\(\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*\)\s*', file_contents)

# extract FFT dimensions from file contents
fft_dim_match = re.search(r'FFT dimensions:\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', file_contents)
if fft_dim_match:
    fft_dim = (int(fft_dim_match.group(1)), int(fft_dim_match.group(2)), int(fft_dim_match.group(3)))
else:
    print("Error: could not find FFT dimensions in input file")
    sys.exit()

# extract number of atoms from file contents
num_atoms_match = re.search(r'number of atoms/cell\s*=\s*(\d+)', file_contents)
if num_atoms_match:
    num_atoms = int(num_atoms_match.group(1))
else:
    print("Error: could not find number of atoms in input file")
    sys.exit()

# find all atomic positions using regex
positions = re.findall(r'\s+\d+\s+([A-Za-z]+)\s+tau\(\s*\d+\)\s*=\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)', file_contents)

# print out output file as in format for BGW kgrid.x
with open(output_file, 'w') as f:
    print(kgird[0], kgird[1], kgird[2], file=f)
    print(kgird_shift[0], kgird_shift[1], kgird_shift[2], file=f)
    print(small_qgrid[0], small_qgrid[1], small_qgrid[2], file=f)
    for i in range(3):
        print(lattice[i][0], lattice[i][1], lattice[i][2], file=f)
    print(num_atoms, file=f)
    for i, position in enumerate(positions):
        if i < num_atoms:
            atomic_symbol = position[0]
            if atomic_symbol in symbol_dict:
                atomic_num = symbol_dict[atomic_symbol]
            else:
                atomic_num = -1  # to indicate unknown symbol
            print(atomic_num, position[1], position[2], position[3], file=f)
        else:
            break
    print(fft_dim[0], fft_dim[1], fft_dim[2], file=f)
    print(".false.", file=f) 

out_file = os.path.splitext(output_file)[0] + ".out"
log_file = os.path.splitext(output_file)[0] + ".log"

subprocess.run([BGW_path+"kgrid.x", output_file, out_file, log_file])
