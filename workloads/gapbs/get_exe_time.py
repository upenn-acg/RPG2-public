import subprocess
import operator
import sys
import os
import time
print(sys.argv)
if len(sys.argv) != 3:
	print("need 3 arguments!")
	exit(-1)
exe = sys.argv[1]
degree = sys.argv[2]

results = 0.0
for i in range (20):
	start = time.time()
	os.system("./"+exe+" -k "+degree+" -g 24 -n 2 > /dev/null")
	end = time.time()
	print(end - start)
	results = results + end - start

print("average: "+str(results/20.0))


#p0 = subprocess.Popen(["/usr/bin/time", "./"+exe,"-k",degree,"-g","24","-n","20"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


