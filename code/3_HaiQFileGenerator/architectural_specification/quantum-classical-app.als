
//	Alumno: Álvaro Manuel Aparicio Morales
//	Tutores: Javier Cámara y Jose Garcia-Alonso
//	Máster Universitario en Ingeniería Informática
//	Universidad de Málaga
//	Descripcion:
//	Especificación del modelo arquitectural de aplicaciones híbridas (clásico-cuánticas)

ModelType: dtmc;

abstract sig PU {services : some Service}
</
formula cpulogicalperformancefactor;
formula cpuram;
formula cpubandwidth;
formula cpucostfactor;
formula qpuprize;
/>
abstract sig QPU extends PU {}
</
formula cpulogicalperformancefactor;
formula cpuram;
formula cpubandwidth;
formula cpucostfactor;
formula qpuprize;
var dummy : bool init false
[services:qpair] true -> (dummy'=true);
/>
abstract sig CPU extends PU {}
</
formula cpulogicalperformancefactor;
formula cpuram;
formula cpubandwidth;
formula cpucostfactor;
formula qpuprize;
var dummy : bool init false
[services:cpair] true -> (dummy'=true);
/>
abstract sig Service {
	machines : some PU,
	deployment : one Deployment,
	hybrid_service: set Service, // Simular el concepto de hybrid_service
	link: some Service // Comunicación entre servicios del caso de uso
}
</
    formula mslogicalperformancefactor;
    formula msram;
    formula msbandwidth;
    formula msexecutiontime;
    formula msavailability;
    formula shots;
/>
abstract sig ClassicalService extends Service {}
</
    formula mslogicalperformancefactor;
    formula msram;
    formula msbandwidth;
    formula msexecutiontime;
    formula msavailability;
    formula shots;
/>
abstract sig QuantumService extends Service {}
</
    formula mslogicalperformancefactor;
    formula msram;
    formula msbandwidth;
    formula msexecutiontime;
    formula msavailability;
    formula shots;
/>
abstract sig Deployment {services: some Service}
</
    formula dummy;
/>
abstract sig HybridDeployment extends Deployment {}
</
    formula dummy;
    var finished : bool init false;
    [] (finished=false) -> (finished'=true);
/>
abstract sig ClassicalDeployment extends Deployment {}
</
    formula dummy;
    var finished : bool init false;
    [] (finished=false) -> (finished'=true);
/>
lone sig HybridUseCase extends HybridDeployment {}
</
    formula dummy = 0;
/>
lone sig ClassicalUseCase extends ClassicalDeployment {}
</
    formula dummy = 0;
/>

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
