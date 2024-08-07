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
sig T3_medium extends CPU {}
//lone abstract sig T3_large extends CPU {}
sig T3_xlarge extends CPU {}
//sig T3_2xlarge extends CPU {}

/* Definition of Services */
abstract sig Service {
	machines : some PU,
	deployment : one Deployment,
	hybrid_service: set Service, // Simular el concepto de hybrid_service
	link: some Service // Comunicación entre servicios del caso de uso
}
abstract sig Classical_Service extends Service {}
abstract sig Quantum_Service extends Service {}
/*Definition of Deployment*/
abstract sig Deployment {services: some Service}
abstract sig Hybrid_Deployment extends Deployment {}
abstract sig Classical_Deployment extends Deployment {}


/* Definition of Use Case Services (Generic) */
lone sig HybridUseCase extends Hybrid_Deployment {}
lone sig ClassicalUseCase extends Classical_Deployment {}
/*APPLICATION SPECIFIC CASE*/
abstract sig Aggregator extends Classical_Service {}
abstract sig Sensor extends Classical_Service {}
abstract sig Grover_alg extends Classical_Service {}
abstract sig QuantumGrover_alg extends Quantum_Service{}
abstract sig Result_processing extends Classical_Service {}
abstract sig Binary_search extends Classical_Service {}
/* Instances definition */
one sig S1 extends Sensor {}
one sig S2 extends Sensor {}
one sig S3 extends Sensor {}
one sig A1 extends Aggregator {}
// lone para que la generación pueda ser clásica o cuántica
lone sig CG1 extends Grover_alg {}
lone sig QG1  extends QuantumGrover_alg {}
lone sig BS1 extends Binary_search {}
one sig RP1 extends Result_processing {}


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
// Ningún servicio puede estar relacionado consigo mismo
all s: Service | s not in s.link
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
// Dos servicios forman un servicio híbrido, entonces esos dos están relacionados a través de link
all s1, s2: Service | s1 !=s2 and s1 in s2.hybrid_service and s2 in s1.hybrid_service implies (s2 in s1.link and s1 in s2.link)
/*--------------------------------------------------------------------------------------------------------------------------------*/

/*--------------------------------------------------Deployment-Restrictions-------------------------------------------------*/
// Para todo despliegue si la interseccion con Hybrido entonces no clasico y viceversa
//all d: Deployment | #(d & Hybrid_Deployment) > 0 implies  #(d & Classical_Deployment) = 0 
//all d: Deployment | #(d & Classical_Deployment) > 0 implies  #(d & Hybrid_Deployment) = 0 
// Todos los servicios deben de pertenecer a un despliegue (Se cumple con el one en Deployment)
all hd: Hybrid_Deployment | #(hd.services & Quantum_Service) > 0 and #(hd.services & Classical_Service) > 0
all cd: Classical_Deployment | #(cd.services & Quantum_Service) = 0
/*---------------------------------------------------------------------------------------------------------------------------*/
 
/*--------------------------------------------------Use-Case----------------------------------------------------------------*/
// Los servicios de datos de sensores solo están conectados con el servicio agregador y agregador debe estar conectado tambien con datos.
all ds: Sensor,  ag: Aggregator | #(ds.link) = 1 and #(ds.link & Aggregator) > 0 and ds in ag.link and ds not in Grover_alg.link and ds not in Result_processing.link and ds not in QuantumGrover_alg.link and ds not in Binary_search.link
// Aggregator solo se conecta con ClassicalGrover o con Binary Search
all ag: Aggregator | #(ag.link & QuantumGrover_alg) = 0 and #(ag.link & Result_processing) = 0 
all cg: Grover_alg, ag: Aggregator | cg in ag.link and ag in cg.link and ag not in cg.hybrid_service.link
// Aggregator solo se conecta con Binary Search
all bs: Binary_search, ag: Aggregator | bs in ag.link and ag in bs.link
// El servicio híbrido está formado por QuantumGrover y ClassicalGrover
all qg: QuantumGrover_alg, cg: Grover_alg | qg in cg.hybrid_service and cg in qg.hybrid_service
// Para todo Quantum Grover, solo puede estar conectado a servicio ClassicalGrover
// El servicio de procesamiento de resultado, solo está conectado con el servicio Clasico de grover
all rp: Result_processing,  cg: Grover_alg | #(rp.link) = 1 and #(rp.link & Grover_alg) > 0 and rp in cg.link and rp not in QuantumGrover_alg.link and rp not in Aggregator.link and rp not in Sensor.link 
// El servicio de procesamiento de resultado, solo está conectado con el servicio de Búsqueda Binaria
all rp: Result_processing,  bs: Binary_search | #(rp.link) = 1 and #(rp.link & Binary_search) > 0 and rp in bs.link
// Para todo despliegue híbrido debe haber un grover clásico y un grover cuántico y ningún búsqueda binaria
all hd: Hybrid_Deployment | #(hd.services & QuantumGrover_alg) = 1 and #(hd.services & Grover_alg) = 1  and #(hd.services & Binary_search) = 0
// Para todo despliegue clásico no debe haber ningún gover clásico ni gover cuántico y un solo búsqueda binaria
all cd: Classical_Deployment | #(cd.services & QuantumGrover_alg) = 0 and #(cd.services & Grover_alg) = 0  and #(cd.services & Binary_search) = 1
/*---------------------------------------------------------------------------------------------------------------------------*/
/*TO BE COMPLETED WITH SERVICES MACHINES RESTRICTIONS HAIQ*/
// Creo que solo es necesario indicarlo por parte del punto de vista del servicio porque desde el punto de vista de la máquina se debe cumplir all pu: PU, s: Service | s in pu.services implies s.machines = pu
all rp: Result_processing | #(rp.machines & T3_xlarge) = 0 // Ejemplo
}

pred show {
// Todo despliegue híbrido debe de contar con 6 servicios clásicos y 1 servicio cuántico
//all d: Hybrid_Deployment | #(d.services & Classical_Service) = 6 and  #(d.services & Quantum_Service) = 1  
// Todo despliegue debe de estar compuesto por un procesamiento, un grover, un aggregador y 3 servicios de sensores (No se si es redundante con la de arriba)
}
run show for 25





