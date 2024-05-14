// Defining QPU and QPU_Machines
sig QPU {}
sig Aquila extends QPU{}
sig Aria_1 extends QPU {}
sig Aria_2 extends QPU {}
sig Aspen_m_3 extends QPU {}
sig Forte_1 extends QPU {}
sig Harmony extends QPU {}
sig Lucy extends QPU {}
sig Dm1 extends QPU {}
sig Sv1 extends QPU {}
sig Tn1 extends QPU {}
sig Local extends QPU {}
// Defining CPUs
sig CPU {}
sig T2_nano extends CPU{}
sig T2_micro extends CPU{}
sig T2_small extends CPU{}
sig T2_medium extends CPU{}
sig T2_large extends CPU{}
sig T2_xlarge extends CPU{}
sig T2_2xlarge extends CPU{}
sig T3_nano extends CPU{}
sig T3_micro extends CPU{}
sig T3_small extends CPU{}
sig T3_medium extends CPU{}
sig T3_large extends CPU{}
sig T3_xlarge extends CPU{}
sig T3_2xlarge extends CPU{}

// Defining Services of Hybrid Application

sig Sensor_Service {}
sig Sensor_Service_1 {}
sig Sensor_Service_2 {}
sig Sensor_Service_3 {}
sig Aggregator_Servicee {}
sig Grover_Quantum_Service {}
sig Grover_Classical_Service {}
sig Binary_Search_Service
sig Quantum_Processing_Service{}
pred show{}

run show for 3
