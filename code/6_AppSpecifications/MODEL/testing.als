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
	instance: one QPU_Types
}

/*
// Defining CPUs
sig CPU_Machine {
	computing_mode: CPU
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
*/

pred show {}

run show for  25
