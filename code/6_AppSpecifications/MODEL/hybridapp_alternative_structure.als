// Defining QPU and 
sig QPU {}
enum QPU_Types {
Aquila,
Aria_1,
Aria_2, 
Aspen_m_3, 
Forte_1,
Harmony, 
Lucy,
Dm1,
Sv1,
Tn1,
Local
}

sig QPU_Machine {
	computing_mode: one QPU
	instance: one QPU_Types
}

// Defining CPUs
sig CPU_Machine {
	computing_mode: one CPU
	instance: one CPU_Types
}
enum CPU_Types {
T2_nano,
T2_micro, 
T2_small,
T2_medium, 
T2_large,
T2_xlarge, 
T2_2xlarge, 
T3_nano,
T3_micro, 
T3_small,
T3_medium, 
T3_large,
T3_xlarge,
T3_2xlarge,
}


// Defining Services Types
sig Classical_Service {
	classical_machine : one CPU_Machine
}
sig Quantum_Service {
	quantum_machine : one QPU_Machine
}
sig Hybrid_Service {
	classical_service : one Classical_Service,
	quantum_service : one Quantum_Service
}
// Defining Services for Study Case
sig Sensor_Service extends Classical_Service{} // Solo declaro uno porque las 3 instancias van a ser exactamente iguales 
sig Aggregator_Service  extends Classical_Service{}
sig Grover extends Hybrid_Service{}
sig Binary_Search_Service  extends Classical_Service{}
sig Quantum_Processing_Service  extends Classical_Service{}

//Defining Deployments for Study Case
sig Hybrid_Deployment {
	sensor_services : some Sensor_Service,
	aggregator : one Aggregator_Service,
	grover : one Grover,
	processing_service: one Quantum_Processing_Service
}
sig Classical_Deployment {
	sensor_services : some Sensor_Service,
	aggregator : one Aggregator_Service,
	binary_search : one Binary_Search_Service,
	processing_service: one Quantum_Processing_Service
}

fact {
// Para todo despliegue se debe cumplir que el número de instancias de máquinas CPU debe ser igual a la suma de la totalidad de servicios que componen el despliegue 
//all d: Deployment | (#d.processing_service + #d.grover + #d.aggregator + #d.sensor_services) = 



// Restricciones documento
// Servicios Clásicos no pueden Relacionarse con Servicios Cuánticos
// Un servicio clásico, no puede estar alojado en una misma instancia de máquina clásica que otro servicio clásico (No co-alojados)
// Un servicio clásico, no puede estar alojado en la misma instancia de máquina clásica que un servicio híbrido
// Un servicio clásico, no puede estar relacionado con más de una instancia de máquina clásica.
// Un servicio clásico, tiene que tener una instancia de máquina clásica asociada.
// Un servicio híbrido, no puede estar alojado en la misma instancia de máquina que un servicio clásico
// Un servicio híbrido, no puede estar alojado en la misma instancia de máquina clásica que un servicio híbrido
// Un servicio híbrido sí puede compartir instancia de máquina cuántica con otro servicio.
// Un servicio híbrido, tiene que tener una instancia de máquina clásica y máquina cuántica asociadas.
// Para todo despliegue que tenga servicio grover, debe de tener asociado 1 máquina cuántica y una máquina clásica
all d: Hybrid_Deployment |  #d.grover = 1 implies #d.grover.quantum_machine = 1 and #d.grover.classical_machine = 1  // Creo que al definir lo de one en servicios híbridos, ya se cumple
// Un servicio híbrido no puede estar relacionado con más de una máquina cuántica.

// Design Restrictions
// Todo despliegue debe de estar compuesto por un procesamiento, un grover, un aggregador y 3 servicios de sensores (No se si es redundante con la de arriba)
all d: Hybrid_Deployment | one d.processing_service and one d.grover and one d.aggregator and #d.sensor_services = 3 
 // Los servicios de datos de sensores solo están conectados con el servicio agregador.
// El servicio agregador solo puede estar conectado al servicio híbrido Grover y a los servicios de Datos de Sensores.
// El servicio híbrido solo puede estar conectado con el agregador y servicio de procesamiento de resultado

}

pred show {

}

run show for 6 but 1 CPU, 1 QPU, 1 Hybrid_Deployment
