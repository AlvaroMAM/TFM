abstract sig PU {}
// Las máquinas deben de estar relacionadas con servicios 
abstract sig QPU extends PU {}
abstract sig CPU extends PU {}

// Signaturas dependientes del Caso de Estudio
/* Defintion of QPU Machines */
lone abstract sig Aquila extends QPU {}
lone abstract sig Aria_1 extends QPU {}
lone abstract sig Aria_2 extends QPU {}
lone abstract sig Aspen_m_3 extends QPU {}
lone abstract sig Forte_1 extends QPU {}
lone abstract sig Harmony extends QPU {}
lone abstract sig Lucy extends QPU {}
lone abstract sig Dm1 extends QPU {}
lone abstract sig Sv1 extends QPU {}
lone abstract sig Tn1 extends QPU {}
lone abstract sig Local extends QPU {}

/* Definition of CPU Machines */
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
lone abstract sig T3_medium extends CPU {}
lone abstract sig T3_large extends CPU {}
lone abstract sig T3_xlarge extends CPU {}
lone abstract sig T3_2xlarge extends CPU {}

/* Definition of Services */

pred show {}

run show for 2
