"""Sets the necessary environment variables, for calling HSPICE and VPR.
"""

import os

#HSPICE command
os.environ["HSPICE"] = "/usr/synopsys/hspice-D-2010.03/hspice/bin/hspice" 

#VPR command
os.environ["VPR"] = "/home/vtr-verilog-to-routing/build/vpr" 

#Maximum parallel number of HSPICE jobs (depends on both the number of cores and licenses)
os.environ["HSPICE_CPU"] = "16"

#Maximum number of parallel VPR and other non-SPICE jobs
os.environ["VPR_CPU"] = "4"
