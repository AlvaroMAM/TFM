// Defining QPU and QPU_Machines
sig QPU {}
sig CPU {}

sig QPU_Machine {
	type: QPU // Indicar Que las máquinas cuánticas son de tipo QPU, esta variable  creo que ayudara a poder realizar las restricciones en la distribución
}
sig Aquila extends QPU_Machine{}
sig Aria_1 extends QPU_Machine {}
sig Aria_2 extends QPU_Machine {}
sig Aspen_m_3 extends QPU_Machine {}
sig Forte_1 extends QPU_Machine {}
sig Harmony extends QPU_Machine {}
sig Lucy extends QPU_Machine {}
sig Dm1 extends QPU_Machine {}
sig Sv1 extends QPU_Machine {}
sig Tn1 extends QPU_Machine {}
sig Local extends QPU_Machine {}
// Defining CPUs
sig CPU_Machine {
	type: CPU
}
sig T2_nano extends CPU_Machine{}
sig T2_micro extends CPU_Machine{}
sig T2_small extends CPU_Machine{}
sig T2_medium extends CPU_Machine{}
sig T2_large extends CPU_Machine{}
sig T2_xlarge extends CPU_Machine{}
sig T2_2xlarge extends CPU_Machine{}
sig T3_nano extends CPU_Machine{}
sig T3_micro extends CPU_Machine{}
sig T3_small extends CPU_Machine{}
sig T3_medium extends CPU_Machine{}
sig T3_large extends CPU_Machine{}
sig T3_xlarge extends CPU_Machine{}
sig T3_2xlarge extends CPU_Machine{}

// Defining Services of Hybrid Application
sig Sensor_Service{
		classical_machine: one CPU_Machine
} // ¿Está bien?, es decir voy a tener 3 servicios iguales, lo único que cambia es que están conectados a otro sensor
sig Sensor_Service_1 extends Sensor_Service {}
sig Sensor_Service_2 extends Sensor_Service{}
sig Sensor_Service_3 extends Sensor_Service{}
sig Aggregator_Service {
	classical_machine: one CPU_Machine
}
sig Grover {
	quantum_machine: one QPU_Machine,
	classical_machine : one CPU_Machine
}
//sig Grover_Quantum_Service extends QPU_Service {} // Aquí tengo otra duda, poruqe no sé si definir una clase que sea HybridService y que contenga 2 servicios uno clásico y otro cuántic
//sig Grover_Classical_Service extends CPU_Service{}
sig Binary_Search_Service{
	classical_machine: one CPU_Machine
}
sig Quantum_Processing_Service{
	classical_machine: one CPU_Machine
}


fact {
no c: CPU_Machine, q: QPU_Machine | c -> q
no q: QPU_Machine, c: CPU_Machine | q -> c


}

pred show{}

run show for 4
