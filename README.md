# PySA-SAT Solvers

This library implements SAT solver algorithms for PySA.  Currently two algorithm implementations
are available, one exact solver (DPLL-SAT) and one heuristic solver (Walk-SAT). SAT problems are accepted
in standard CNF format.

## Getting Started (Applications)

The standalone command line applications for the solvers are configured using CMake.
A C++17 compliant compiler is required. To build all targets, including examples and tests,

` cmake -DCMAKE_BUILD_TYPE=Release -S . -B ./build-release/ && cmake --build ./build-release`

The executables are built to `./build-release/src/dpll-sat.x ` and `./build-release/src/walk-sat.x`

DPLL-SAT  uses standard C++ concurrency to parallelize generic branch exploration.
Additionally, it supports distributing branches using `MPI` processes when compiled with `MPI` support by
passing `-DMPI=ON` to CMake, and optionally `-DMPIEXEC_EXECUTABLE=/path/to/mpiexec`.

### DPLL-SAT
DPLL-SAT enumerates all solutions up to a maximum number of unsatisfied clauses.
```text
Usage: dpll-sat.x cnf_file [max_unsat = 0] [n_threads = 0] [verbose = 0]
Solve SAT formula in CNF format using DPLL.

   max_unsat    Number of maximum unsatisfied clauses that a configuration can have (default = 0)
   n_threads    Number of threads to use (default = 0, that is suggested by the implementation)
   verbose      Level of verbosity (default = 0)
```
If compiled with MPI, the application can be started using `mpirun` with the number of
desired MPI processes.


### Walk-SAT
The Walk-SAT application is a heuristic solver. Its algorithmic parameter
is the walk probability `p`, which sets the probability of randomly flipping any variable
in an unsatisfied clause when no variable in the clause will cause other clauses to become
unsat when flipped. The algorithm is restarted if no solution is found after `max_steps`, up
until `cutoff_time` seconds have elapsed.

```text
Usage: walk-sat.x cnf_file max_steps [p = 0.5] [unsat = 0] [seed = 0] [cutoff_time = 0]
Find solutions to a SAT formula in CNF format using WalkSAT.

   max_steps    Maximum number of steps for each restart.
   p            WalkSAT probability of a walk move. (default = 0.5)
   unsat        Maximum number of unsatisfied clauses to target (default = 0)
   seed         Random seed (default = seed from entropy)
   cutoff_time  The cutoff benchmarking time in seconds (default = exit on first solution)

```
## Contributors

[Salvatore Mandrà](https://github.com/s-mandra)<br>
[Humberto Munoz-Bauza](https://github.com/hmunozb)<br>

## NASA Open Source Agreement and Contributions

See [NOSA](https://github.com/nasa/pysa/tree/main/docs/nasa-cla/).

## Notices

Copyright @ 2023, United States Government, as represented by the Administrator
of the National Aeronautics and Space Administration. All rights reserved.

## Disclaimer

_No Warranty_: THE SUBJECT SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF
ANY KIND, EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
TO, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
FREEDOM FROM INFRINGEMENT, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL BE ERROR
FREE, OR ANY WARRANTY THAT DOCUMENTATION, IF PROVIDED, WILL CONFORM TO THE
SUBJECT SOFTWARE. THIS AGREEMENT DOES NOT, IN ANY MANNER, CONSTITUTE AN
ENDORSEMENT BY GOVERNMENT AGENCY OR ANY PRIOR RECIPIENT OF ANY RESULTS,
RESULTING DESIGNS, HARDWARE, SOFTWARE PRODUCTS OR ANY OTHER APPLICATIONS
RESULTING FROM USE OF THE SUBJECT SOFTWARE.  FURTHER, GOVERNMENT AGENCY
DISCLAIMS ALL WARRANTIES AND LIABILITIES REGARDING THIRD-PARTY SOFTWARE, IF
PRESENT IN THE ORIGINAL SOFTWARE, AND DISTRIBUTES IT "AS IS."

_Waiver and Indemnity_:  RECIPIENT AGREES TO WAIVE ANY AND ALL CLAIMS AGAINST
THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS
ANY PRIOR RECIPIENT.  IF RECIPIENT'S USE OF THE SUBJECT SOFTWARE RESULTS IN ANY
LIABILITIES, DEMANDS, DAMAGES, EXPENSES OR LOSSES ARISING FROM SUCH USE,
INCLUDING ANY DAMAGES FROM PRODUCTS BASED ON, OR RESULTING FROM, RECIPIENT'S
USE OF THE SUBJECT SOFTWARE, RECIPIENT SHALL INDEMNIFY AND HOLD HARMLESS THE
UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY
PRIOR RECIPIENT, TO THE EXTENT PERMITTED BY LAW.  RECIPIENT'S SOLE REMEDY FOR
ANY SUCH MATTER SHALL BE THE IMMEDIATE, UNILATERAL TERMINATION OF THIS
AGREEMENT. 

## Licence

Copyright © 2023, United States Government, as represented by the Administrator
of the National Aeronautics and Space Administration. All rights reserved.

The PySA, a powerful tool for solving optimization problems is licensed under
the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
