abstract sig PU {services : some Service}
// Las máquinas deben de estar relacionadas con servicios 
abstract sig QPU extends PU {}
abstract sig CPU extends PU {}

// Signaturas dependientes del Caso de Estudio
/* Defintion of QPU Machines */
/*
lone abstract sig Aquila extends QPU {}
lone abstract sig Aria_1 extends QPU {}
lone abstract sig Aria_2 extends QPU {}
lone abstract sig Aspen_m_3 extends QPU {}
lone abstract sig Forte_1 extends QPU {}
lone abstract sig Harmony extends QPU {}
lone abstract sig Lucy extends QPU {}
*/
lone abstract sig Dm1 extends QPU {}
lone abstract sig Sv1 extends QPU {}
lone abstract sig Tn1 extends QPU {}
lone abstract sig Local extends QPU {}

/* Definition of CPU Machines */
/*
lone abstract sig T2_nano extends CPU {}
lone abstract sig T2_micro extends CPU {}
lone abstract sig T2_small extends CPU {}
lone abstract sig T2_medium extends CPU {}
lone abstract sig T2_large extends CPU {}
lone abstract sig T2_xlarge extends CPU {}
lone abstract sig T2_2xlarge extends CPU {}
lone abstract sig T3_nano extends CPU {}
lone abstract sig T3_micro extends CPU {}
lone abstract sig T3_small extends CPU {}
*/
lone abstract sig T3_medium extends CPU {}
lone abstract sig T3_large extends CPU {}
lone abstract sig T3_xlarge extends CPU {}
lone abstract sig T3_2xlarge extends CPU {}

/* Definition of Services */
abstract sig Service {machines : some PU}
abstract sig Classical_Service extends Service {}
abstract sig Quantum_Service extends Service {}
abstract sig Hybrid_Service {
	classical_service : one Classical_Service,
	quantum_service : one Quantum_Service
}
/* Defining Services for Study Case */
sig Sensor_Service extends Classical_Service{} // Solo declaro uno porque las 3 instancias van a ser exactamente iguales 
sig Aggregator_Service  extends Classical_Service{}
sig Grover extends Hybrid_Service{}
//sig Binary_Search_Service  extends Classical_Service{}
sig Processing_Service  extends Classical_Service{}

//Defining Deployments for Study Case
sig Hybrid_Deployment {
	sensor_services : some Sensor_Service,
	aggregator : one Aggregator_Service,
	grover : one Grover,
	processing_service: one Processing_Service
}
/*
sig Classical_Deployment {
	sensor_services : some Sensor_Service,
	aggregator : one Aggregator_Service,
	binary_search : one Binary_Search_Service,
	processing_service: one Processing_Service
}
*/
fact {
/* Architectural Restrictions */
// Servicios Clásicos no pueden Relacionarse con Servicios Cuánticos

// Un servici clásico, no puede relacionarse con una máquina cuántica
all cs: Classical_Service | #(cs.machines & QPU) = 0
// Para todas las máquinas clásicas, su conjunto de servicios no pueden ser cuánticos
all c: CPU | #(c.services & Quantum_Service) = 0
// Un servicio clásico, no puede estar alojado en una misma instancia de máquina clásica que otro servicio clásico (No co-alojados)
all cs1, cs2 : Classical_Service | cs1 != cs2 implies #(cs1.machines & cs2.machines) = 0
// Un servicio clásico, no puede estar alojado en la misma instancia de máquina clásica que un servicio híbrido
all sc: Classical_Service, hs: Hybrid_Service | (not (sc in hs.classical_service)) implies #(sc.machines & hs.classical_service.machines) = 0
// Un servicio clásico, no puede estar relacionado con más de una instancia de máquina clásica.
all sc: Classical_Service | #sc.machines < 2
// Un servicio clásico, tiene que tener una instancia de máquina clásica asociada.
all sc: Classical_Service | #sc.machines > 0
// Un servicio cuántico, no puede estar alojado en una máquina clásica
all qs: Quantum_Service | #(qs.machines & CPU) = 0
// Un servicio cuántico, no puede estar alojado en más de una máquina cuántica
all qs: Quantum_Service | #qs.machines < 2
//Un servicio cuántico, tiene que tener una instancia de máquina cuántica asociada.
all qs: Quantum_Service | #qs.machines > 0
// Para todas las máquinas clásicas, su conjunto de servicios no pueden ser cuánticos
all q: QPU | #(q.services & Classical_Service) = 0
// Un servicio híbrido, no puede estar alojado en la misma instancia de máquina que un servicio clásico (¿Esta condición no se cumple con la restricción previa?
all  hs: Hybrid_Service, sc: Classical_Service | (not (sc in hs.classical_service)) implies #(hs.classical_service.machines & sc.machines ) = 0
// Un servicio híbrido, no puede estar alojado en la misma instancia de máquina clásica que un servicio híbrido
all  hs1, hs2: Hybrid_Service | hs1 != hs2 implies #(hs1.classical_service.machines & hs2.classical_service.machines) = 0
// Un servicio híbrido sí puede compartir instancia de máquina cuántica con otro servicio. (Ya se cumple)
// Un servicio híbrido, tiene que tener una instancia de máquina clásica y máquina cuántica asociadas. (Se cumple por el one en los atributos de la signatura)
// Para todo despliegue que tenga servicio grover, debe de tener asociado 1 máquina cuántica y una máquina clásica (Se cumple por el one de los atributos de la signatura)
// Creo que al definir lo de one en servicios híbridos, ya se cumple
// Un servicio híbrido no puede estar relacionado con más de una máquina cuántica.


// Design Restrictions
// Todo despliegue debe de estar compuesto por un procesamiento, un grover, un aggregador y 3 servicios de sensores (No se si es redundante con la de arriba)
all d: Hybrid_Deployment | #d.processing_service = 1 and  #d.grover = 1 and #d.aggregator=1 and #d.sensor_services = 3 
 // Los servicios de datos de sensores solo están conectados con el servicio agregador.

// El servicio agregador solo puede estar conectado al servicio híbrido Grover y a los servicios de Datos de Sensores.
// El servicio híbrido solo puede estar conectado con el agregador y servicio de procesamiento de resultado

}

pred show {
all d: Hybrid_Deployment |  #d.sensor_services = 3 and #d.grover = 1  and #d.processing_service = 1 and #d.aggregator = 1
}

//run show for 7  but  exactly 1 Hybrid_Deployment, exactly 3 Sensor_Service, exactly 1 Aggregator_Service, exactly 1 Grover, exactly 1 Processing_Service
run show for 800 but exactly 3 Sensor_Service, exactly 1 Aggregator_Service, exactly 1 Grover, exactly 1 Processing_Service
