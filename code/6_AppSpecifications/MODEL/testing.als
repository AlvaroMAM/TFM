
sig Sensor_Service extends Classical_Service{ deployment: one Deployment}
sig Aggregator_Service extends Classical_Service{}
sig Grover_Service extends Hybrid_Service {}
sig Binary_Search_Service  extends Classical_Service{}
sig Processing_Service extends Classical_Service {}


//Defining Deployments for Study Case
/*sig Hybrid_Deployment {
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






