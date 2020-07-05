### Platform

Windows7

### Library 

- python==3.7
- pandas==0.23.4
- numpy==1.15.1
- xrld==1.1.0
- openpyxl==2.5.0
- xlsxwriter==1.1.0
- matplotlib==2.2.3


### Folder structure
outpatientRecord.xlsx is the data without sensitive information.

possionTest.py
input: The parameter "caiyangcishu" sets the sampling times.
output:Estimated number of walk-ins arriving in each time slot based on all data.

waitingQueue.py
output:Data in "outpatientRecord.xlsx" is processed and saved in the file "patients_guahao_time_sorted.txt" and "patients_jiezhen_time_sorted.txt". The difference of these two files is that one is sorted by registration time and the other is sorted by service start time. During this process, it computes the waiting time of each patient.  computed. Besides, it records changes in waiting queue length in the file "waitingQueue".

resortedForPatients.py
input: The parameters "test_para" and "test_date" should be setted. The parameter "test_para" has three values corresponding to three different scheduling strategies: "non-test" means scheduled outpatients first, "test1" means walk-ins first, "test2" means first come first serve.
output: average waiting time of walk-ins/scheduled outpatients/all outpatients before/after optimization, average shortened waiting time of walk-ins/scheduled outpatients/all outpatients.

patientsArrivingCount.py
input: The parameter "caiyangcishu" sets the sampling times.
output: Optimal number of service cycles used for estimation and its standard deviation.

dataProcess.py is used to realize data cleaning.
grayPredict.py is used to predict walk-ins arriving in each time slot with gray prediction method.

