import subprocess
import operator
import sys
print(sys.argv)
if len(sys.argv) != 3:
	print("need 3 arguments!")
exe = sys.argv[1]
degree = sys.argv[2]

p0 = subprocess.Popen(["perf", "record", "-e", "mem_load_uops_retired.l3_miss:p,instructions", "--", "./"+exe,"-k",degree,"-g","24","-n","20"])
p0.wait()

p1 = subprocess.Popen(["perf" , "script"],stdout=subprocess.PIPE)
output = p1.communicate()[0].splitlines()
miss_address_count = {}
inst_count = 0
LLC_load_miss_count = 0
for line in output:
	words = line.split()
	if words[len(words)-1] == "(/home.local/zyuxuan/floar/gapbs/"+exe+")":
		if (words[4]=="instructions:"):
			inst_count = inst_count + 1
		else:
			index = ""
			for i in range (6,len(words)-1):
				index = index + words[i]
			if index!="":
				LLC_load_miss_count = LLC_load_miss_count + 1
				if index in miss_address_count:
					miss_address_count[index] = miss_address_count[index] + 1
				else:
					miss_address_count[index] = 1
# sort the result
sorted_miss_addr = sorted(miss_address_count.items(), key=operator.itemgetter(1))

sorted_miss_addr.reverse()



count = 0
for item in sorted_miss_addr:
	if count > 19:
		break
	print(item[0])	
	count = count + 1;
count = 0
for item in sorted_miss_addr:
	if count > 19:
		break
	print(str(float(item[1])*1000/inst_count))	
	count = count + 1;
count = 0
for item in sorted_miss_addr:
	if count > 19:
		break
	print(str(float(item[1])*100/LLC_load_miss_count)+"%")	
	count = count + 1;

