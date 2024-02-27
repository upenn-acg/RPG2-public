rm -rf /home.local/zyuxuan/mongodb/data
mkdir /home.local/zyuxuan/mongodb/data

#/home.local/zyuxuan/mongodb/mongod_server_pgo2/bin/mongod --dbpath /home.local/zyuxuan/mongodb/data > /dev/null &
./mongod.bolt --dbpath /home.local/zyuxuan/mongodb/data > /dev/null &


sleep 8

/home.local/zyuxuan/mongodb/YCSB/ycsb-mongodb/bin/ycsb load mongodb -s -P /home.local/zyuxuan/mongodb/YCSB/ycsb-mongodb/workloads/workloade > /dev/null
sleep 2
rm -rf r00*ue
#pid=$(ps -ef | grep '/home.local/zyuxuan/mongodb/mongod_server_pgo2/bin/mongod' | head -n 1 | awk '{print $2}')

pid=$(ps -ef | grep 'mongod.bolt' | head -n 1 | awk '{print $2}')


echo "PID=$pid"

amplxe-cl -collect uarch-exploration -data-limit=4096 -target-pid $pid >tmpfile.txt &

/home.local/zyuxuan/mongodb/YCSB/ycsb-mongodb/bin/ycsb run mongodb -s -P /home.local/zyuxuan/mongodb/YCSB/ycsb-mongodb/workloads/workloade > /dev/null

pkill -9 mongod
