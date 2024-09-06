
//	Alumno: Álvaro Manuel Aparicio Morales
//	Tutores: Javier Cámara y Jose Garcia-Alonso
//	Máster Universitario en Ingeniería Informática
//	Universidad de Málaga
//	Descripcion:
//	Especificación del modelo arquitectural de aplicaciones híbridas (clásico-cuánticas)


abstract sig PU {services : some Service}

abstract sig QPU extends PU {}

abstract sig CPU extends PU {}

abstract sig Service {
	machines : some PU,
	deployment : one Deployment,
	hybrid_service: set Service, // Simular el concepto de hybrid_service
	link: some Service // Comunicación entre servicios del caso de uso
}

abstract sig ClassicalService extends Service {}

abstract sig QuantumService extends Service {}

abstract sig Deployment {services: some Service}

abstract sig HybridDeployment extends Deployment {}

abstract sig ClassicalDeployment extends Deployment {}

lone sig HybridUseCase extends HybridDeployment {}

lone sig ClassicalUseCase extends ClassicalDeployment {}

fact {
//-------------------------------------------- Architectural-Restrictions ------------------------------------------------------

//-------------------------------------------- Machines- Restrictions------------------------------------------------------
// Toda máquina debe estar asociada a algún servicio
all pu: PU | #pu.services > 0
// Si un servicio está desplegado en una máquina, entonces esa máquina solo puede estar relacionada con ese servicio
all pu: PU, s: Service | s in pu.services implies s.machines = pu
// Para todas las máquinas clásicas, su conjunto de servicios no pueden ser cuánticos
all c: CPU | #(c.services & QuantumService) = 0
// Todos los servicios deben de estar asociados a un despliege
// Para todas las máquinas clásicas, su conjunto de servicios no pueden ser cuánticos
all q: QPU | #(q.services & ClassicalService) = 0
//-------------------------------------------------------------------------------------------------------------------------

//-------------------------------------------- Services- Restrictions------------------------------------------------------
//all s: Service | #(s.deployment) = 1 // Ya se cumple
all s: Service | #(s.deployment & HybridDeployment) = 0 implies #(s.hybrid_service) = 0
// Todo servicio tiene que estar asociado a un despliegue. Aquí se define para ambos lados, desde servicios y desde despliegue
all s: Service, d: Deployment | (s in d.services implies d in s.deployment) and (s.deployment = d implies s in d.services)
// Ningún servicio puede estar relacionado consigo mismo
all s: Service | s not in s.link
//-------------------------------------------------------------------------------------------------------------------------

//------------------------------------------- Classical-Restrictions-------------------------------------------------- 
// Un servicio clásico, no puede relacionarse con una máquina cuántica
all cs: ClassicalService | #(cs.machines & QPU) = 0
// Un servicio clásico, no puede estar alojado en una misma instancia de máquina clásica que otro servicio clásico (No co-alojados)
all cs1, cs2 : ClassicalService | cs1 != cs2 implies #(cs1.machines & cs2.machines) = 0
// Un servicio clásico, no puede estar alojado en la misma instancia de máquina clásica que un servicio híbrido (Se cumple con la anterior)
// Un servicio clásico, no puede estar relacionado con más de una instancia de máquina clásica.
all sc: ClassicalService | #sc.machines < 2
// Un servicio clásico, tiene que tener una instancia de máquina clásica asociada.
all sc: ClassicalService | #sc.machines > 0
//----------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------- Quantum-Restrictions-------------------------------------------------
// Un servicio cuántico, no puede estar alojado en una máquina clásica
all qs: QuantumService | #(qs.machines & CPU) = 0
// Un servicio cuántico, no puede estar alojado en más de una máquina cuántica
all qs: QuantumService | #qs.machines < 2
//Un servicio cuántico, tiene que tener una instancia de máquina cuántica asociada.
all qs: QuantumService | #qs.machines > 0
// Un servicio cuántico, no puede estar en un despliegue clásico
//all qs: QuantumService | #(qs.deployment & ClassicalDeployment) = 0
// Toda máquina cuántica debe tener un servicio asociado
all qs: QuantumService, q: QPU | qs.machines = q implies qs in q.services
// Todo servicio cuántico debe tener un servicio clásico asociado
all qs: QuantumService | #(qs.hybrid_service) = 1  and #(qs.hybrid_service & QuantumService) = 0

//-----------------------------------------------------------------------------------------------------------------------------

//----------------------------------------Hybrid-Services-Restrictions----------------------------------------------------------
// Todo servicio cuántico tiene que estar asociado a un servicio clásico 
all qs: QuantumService | qs in ClassicalService.hybrid_service
// Para todos los servicios clásicos y cuánticos que conforman un servicio híbrido, deben pertenecer al mismo despliegue
all s1, s2: Service | s1 !=s2 and s1 in s2.hybrid_service and s2 in s1.hybrid_service implies s1.deployment = s2.deployment
// Un servicio cuántico no puede compartir el servicio clásico con el que está asociado
all qs1, qs2: QuantumService | qs1 != qs2 and #(qs1.hybrid_service) = 1 and #(qs2.hybrid_service) = 1 implies #(qs1.hybrid_service & qs2.hybrid_service) = 0
// El servicio cuántico y clásico que conformen un servicio híbrido, solo pueden estar relacionado entre ellos
all qs:QuantumService, cs: ClassicalService | (cs in qs.hybrid_service implies qs in cs.hybrid_service) and (qs in cs.hybrid_service implies cs in qs.hybrid_service)
// Dos servicios clásicos no pueden formar un servicio híbrido. Un servicio consigo mismo tampoco puede formar un servicio híbrido
all cs1, cs2: ClassicalService, hd: HybridDeployment | (cs1 in hd.services and cs2 in hd.services) implies not (cs1 in cs2.hybrid_service) and not ( cs2 in cs2.hybrid_service)
// Dos servicios forman un servicio híbrido, entonces esos dos están relacionados a través de link
all s1, s2: Service | s1 !=s2 and s1 in s2.hybrid_service and s2 in s1.hybrid_service implies (s2 in s1.link and s1 in s2.link)
//--------------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------------Deployment-Restrictions-------------------------------------------------
// Para todo despliegue si la interseccion con Hybrido entonces no clasico y viceversa
//all d: Deployment | #(d & HybridDeployment) > 0 implies  #(d & ClassicalDeployment) = 0 
//all d: Deployment | #(d & ClassicalDeployment) > 0 implies  #(d & HybridDeployment) = 0 
// Todos los servicios deben de pertenecer a un despliegue (Se cumple con el one en Deployment)
all hd: HybridDeployment | #(hd.services & QuantumService) > 0 and #(hd.services & ClassicalService) > 0
all cd: ClassicalDeployment | #(cd.services & QuantumService) = 0
//---------------------------------------------------------------------------------------------------------------------------
 
}
abstract sig Aggregator extends ClassicalService {}

abstract sig Sensor extends ClassicalService {}

abstract sig GroverAlg extends ClassicalService {}

abstract sig BinarySearch extends ClassicalService {}

abstract sig QuantumGroverAlg extends QuantumService{}

abstract sig ResultProcessing extends ClassicalService {}

pred show {
//--------------------------------------------------Use-Case----------------------------------------------------------------
// Los servicios de datos de sensores solo están conectados con el servicio agregador y agregador debe estar conectado tambien con datos.
all ds: Sensor,  ag: Aggregator | #(ds.link) = 1 and #(ds.link & Aggregator) > 0 and ds in ag.link and ds not in GroverAlg.link and ds not in ResultProcessing.link and ds not in QuantumGroverAlg.link and ds not in BinarySearch.link
// Aggregator solo se conecta con ClassicalGrover o con Binary Search
all ag: Aggregator | #(ag.link & QuantumGroverAlg) = 0 and #(ag.link & ResultProcessing) = 0 
all cg: GroverAlg, ag: Aggregator | cg in ag.link and ag in cg.link and ag not in cg.hybrid_service.link
// Aggregator solo se conecta con Binary Search
all bs: BinarySearch, ag: Aggregator | bs in ag.link and ag in bs.link
// El servicio híbrido está formado por QuantumGrover y ClassicalGrover
all qg: QuantumGroverAlg, cg: GroverAlg | qg in cg.hybrid_service and cg in qg.hybrid_service
// Para todo Quantum Grover, solo puede estar conectado a servicio ClassicalGrover
// El servicio de procesamiento de resultado, solo está conectado con el servicio Clasico de grover
all rp: ResultProcessing,  cg: GroverAlg | #(rp.link) = 1 and #(rp.link & GroverAlg) > 0 and rp in cg.link and rp not in QuantumGroverAlg.link and rp not in Aggregator.link and rp not in Sensor.link 
// El servicio de procesamiento de resultado, solo está conectado con el servicio de Búsqueda Binaria
all rp: ResultProcessing,  bs: BinarySearch | #(rp.link) = 1 and #(rp.link & BinarySearch) > 0 and rp in bs.link
// Para todo despliegue híbrido debe haber un grover clásico y un grover cuántico y ningún búsqueda binaria
all hd: HybridDeployment | #(hd.services & QuantumGroverAlg) = 1 and #(hd.services & GroverAlg) = 1  and #(hd.services & BinarySearch) = 0
// Para todo despliegue clásico no debe haber ningún gover clásico ni gover cuántico y un solo búsqueda binaria
all cd: ClassicalDeployment | #(cd.services & QuantumGroverAlg) = 0 and #(cd.services & GroverAlg) = 0  and #(cd.services & BinarySearch) = 1
//---------------------------------------------------------------------------------------------------------------------------
all s:ResultProcessing | #(s.machines & t3small) = 0 and #(s.machines & t3medium) = 0
all s:BinarySearch | #(s.machines & t3small) = 0 and #(s.machines & t3medium) = 0
all s:Aggregator | #(s.machines & t3small) = 0
all s:GroverAlg | #(s.machines & t3small) = 0

}
run show for 25

sig aria1 extends QPU {}

sig aria2 extends QPU {}

sig aspenm3 extends QPU {}

sig harmony extends QPU {}

sig lucy extends QPU {}

sig dm1 extends QPU {}

sig sv1 extends QPU {}

sig local extends QPU {}

sig t3large extends CPU {}

sig t3xlarge extends CPU {}

sig t32xlarge extends CPU {}

sig t3medium extends CPU {}

sig t3small extends CPU {}


one sig resultprocessing0 extends ResultProcessing {}

lone sig binarysearch0 extends BinarySearch {}

one sig aggregator0 extends Aggregator {}

lone sig groveralg0 extends GroverAlg {}

one sig sensor0 extends Sensor {}

one sig sensor1 extends Sensor {}

one sig sensor2 extends Sensor {}

lone sig quantumgroveralg0 extends QuantumGroverAlg {}

