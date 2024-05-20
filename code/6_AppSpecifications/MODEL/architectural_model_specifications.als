/*
	Alumno: Álvaro Manuel Aparicio Morales
	Tutores: Javier Cámara y Jose Garcia-Alonso
	Máster Universitario en Ingeniería Informática
	Universidad de Málaga
	Descripcion:
	Especificación del modelo arquitectural de aplicaciones híbridas (clásico-cuánticas)
*/
// Las máquinas deben de estar relacionadas con servicios 
abstract sig PU {services : some Service}
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
//sig Dm1 extends QPU {}
//sig Sv1 extends QPU {}
sig Tn1 extends QPU {}
sig Local extends QPU {}

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
//lone abstract sig T3_medium extends CPU {}
//lone abstract sig T3_large extends CPU {}
sig T3_xlarge extends CPU {}
sig T3_2xlarge extends CPU {}

/* Definition of Services */
abstract sig Service {
	machines : some PU,
	deployment : one Deployment,
	hybrid_service: set Service, // Simular el concepto de hybrid_service
//	link: some Service // Comunicación entre servicios del caso de uso
}
abstract sig Classical_Service extends Service {}
abstract sig Quantum_Service extends Service {}
/*Definition of Deployment*/
abstract sig Deployment {services: some Service}
sig Hybrid_Deployment extends Deployment {}
//abstract sig Classical_Deployment extends Deployment {}

fact {
/*-------------------------------------------- Architectural-Restrictions ------------------------------------------------------*/

/*-------------------------------------------- Machines- Restrictions------------------------------------------------------*/
// Toda máquina debe estar asociada a algún servicio
all pu: PU | #pu.services > 0
// Si un servicio está desplegado en una máquina, entonces esa máquina solo puede estar relacionada con ese servicio
all pu: PU, s: Service | s in pu.services implies s.machines = pu
// Para todas las máquinas clásicas, su conjunto de servicios no pueden ser cuánticos
all c: CPU | #(c.services & Quantum_Service) = 0
// Todos los servicios deben de estar asociados a un despliege
// Para todas las máquinas clásicas, su conjunto de servicios no pueden ser cuánticos
all q: QPU | #(q.services & Classical_Service) = 0
/*-------------------------------------------------------------------------------------------------------------------------*/

/*-------------------------------------------- Services- Restrictions------------------------------------------------------*/
//all s: Service | #(s.deployment) = 1 // Ya se cumple
all s: Service | #(s.deployment & Hybrid_Deployment) = 0 implies #(s.hybrid_service) = 0
// Todo servicio tiene que estar asociado a un despliegue. Aquí se define para ambos lados, desde servicios y desde despliegue
all s: Service, d: Deployment | (s in d.services implies d in s.deployment) and (s.deployment = d implies s in d.services)
/*-------------------------------------------------------------------------------------------------------------------------*/

/*------------------------------------------- Classical-Restrictions-------------------------------------------------- */
// Un servicio clásico, no puede relacionarse con una máquina cuántica
all cs: Classical_Service | #(cs.machines & QPU) = 0
// Un servicio clásico, no puede estar alojado en una misma instancia de máquina clásica que otro servicio clásico (No co-alojados)
all cs1, cs2 : Classical_Service | cs1 != cs2 implies #(cs1.machines & cs2.machines) = 0
// Un servicio clásico, no puede estar alojado en la misma instancia de máquina clásica que un servicio híbrido (Se cumple con la anterior)
// Un servicio clásico, no puede estar relacionado con más de una instancia de máquina clásica.
all sc: Classical_Service | #sc.machines < 2
// Un servicio clásico, tiene que tener una instancia de máquina clásica asociada.
all sc: Classical_Service | #sc.machines > 0
/*----------------------------------------------------------------------------------------------------------------------------*/

/*--------------------------------------------- Quantum-Restrictions-------------------------------------------------*/
// Un servicio cuántico, no puede estar alojado en una máquina clásica
all qs: Quantum_Service | #(qs.machines & CPU) = 0
// Un servicio cuántico, no puede estar alojado en más de una máquina cuántica
all qs: Quantum_Service | #qs.machines < 2
//Un servicio cuántico, tiene que tener una instancia de máquina cuántica asociada.
all qs: Quantum_Service | #qs.machines > 0
// Un servicio cuántico, no puede estar en un despliegue clásico
//all qs: Quantum_Service | #(qs.deployment & Classical_Deployment) = 0
// Toda máquina cuántica debe tener un servicio asociado
all qs: Quantum_Service, q: QPU | qs.machines = q implies qs in q.services
// Todo servicio cuántico debe tener un servicio clásico asociado
all qs: Quantum_Service | #(qs.hybrid_service) = 1  and #(qs.hybrid_service & Quantum_Service) = 0

/*-----------------------------------------------------------------------------------------------------------------------------*/

/*----------------------------------------Hybrid-Services-Restrictions----------------------------------------------------------*/
// Todo servicio cuántico tiene que estar asociado a un servicio clásico 
all qs: Quantum_Service | qs in Classical_Service.hybrid_service
// Para todos los servicios clásicos y cuánticos que conforman un servicio híbrido, deben pertenecer al mismo despliegue
all s1, s2: Service | s1 !=s2 and s1 in s2.hybrid_service and s2 in s1.hybrid_service implies s1.deployment = s2.deployment
// Un servicio cuántico no puede compartir el servicio clásico con el que está asociado
all qs1, qs2: Quantum_Service | qs1 != qs2 and #(qs1.hybrid_service) = 1 and #(qs2.hybrid_service) = 1 implies #(qs1.hybrid_service & qs2.hybrid_service) = 0
// El servicio cuántico y clásico que conformen un servicio híbrido, solo pueden estar relacionado entre ellos
all qs:Quantum_Service, cs: Classical_Service | (cs in qs.hybrid_service implies qs in cs.hybrid_service) and (qs in cs.hybrid_service implies cs in qs.hybrid_service)
// Dos servicios clásicos no pueden formar un servicio híbrido. Un servicio consigo mismo tampoco puede formar un servicio híbrido
all cs1, cs2: Classical_Service, hd: Hybrid_Deployment | (cs1 in hd.services and cs2 in hd.services) implies not (cs1 in cs2.hybrid_service) and not ( cs2 in cs2.hybrid_service)
/*--------------------------------------------------------------------------------------------------------------------------------*/

/*--------------------------------------------------Deployment-Restrictions-------------------------------------------------*/
// Todos los servicios deben de pertenecer a un despliegue (Se cumple con el one en Deployment)
all hd: Hybrid_Deployment | #(hd.services & Quantum_Service) > 0 and #(hd.services & Classical_Service) > 0
//all cd: Classical_Deployment | #(cd.services & Quantum_Service) = 0
/*---------------------------------------------------------------------------------------------------------------------------*/
 
/*--------------------------------------------------Use-Case----------------------------------------------------------------*/
// Los servicios de datos de sensores solo están conectados con el servicio agregador.
// El servicio agregador solo puede estar conectado al servicio híbrido Grover y a los servicios de Datos de Sensores.
// El servicio híbrido solo puede estar conectado con el agregador y servicio de procesamiento de resultado
/*---------------------------------------------------------------------------------------------------------------------------*/
}

pred show {
// Todo despliegue híbrido debe de contar con 6 servicios clásicos y 1 servicio cuántico
all d: Hybrid_Deployment | #(d.services & Classical_Service) = 6 and  #(d.services & Quantum_Service) = 1  
// Todo despliegue debe de estar compuesto por un procesamiento, un grover, un aggregador y 3 servicios de sensores (No se si es redundante con la de arriba)
//all d: Hybrid_Deployment |  #d.sensor_services = 3 and #d.grover = 1  and #d.processing_service = 1 and #d.aggregator = 1
}
run show for 25





