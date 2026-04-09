# MPI Cheatsheet

## Overview

MPI (Message Passing Interface) is a standardized communication protocol for parallel computing. It defines an API that programs use to send and receive data between processes running concurrently, whether on a single machine or across a cluster of nodes.

### Goals

- **Portability**: the MPI standard is implemented by multiple vendors (OpenMPI, MPICH, Intel MPI) and runs on laptops, HPC clusters, and supercomputers without changing application code.
- **Performance**: designed for low-latency, high-throughput communication over fast interconnects (InfiniBand, Ethernet).
- **Scalability**: the same program can run on 1 process or 100,000 processes with no structural changes.
- **Flexibility**: supports point-to-point messaging, collective operations (broadcast, reduce, scatter, gather), and one-sided communication.

### Design

MPI follows the SPMD (Single Program, Multiple Data) model. Every process runs the same program, but each is assigned a unique integer identifier called its **rank** (0 to N-1). Processes use their rank to determine what portion of the data to work on and who to communicate with.

Key concepts:

- **Communicator**: a group of processes that can communicate with each other. `MPI_COMM_WORLD` is the default group containing all processes.
- **Rank**: the index of a process within a communicator. Used to route messages and divide work.
- **Tag**: an integer label attached to a message, allowing the receiver to distinguish between different message types.
- **Blocking vs non-blocking**: `MPI_Send`/`MPI_Recv` block until the operation completes; `MPI_Isend`/`MPI_Irecv` return immediately and let the program overlap communication with computation.
- **Collective operations**: operations that all processes in a communicator must call together, such as `MPI_Bcast` (one-to-all), `MPI_Reduce` (all-to-one aggregation), and `MPI_Barrier` (synchronization point).

In climate and weather models like Isca, MPI is used to decompose the horizontal grid across processes. Each process owns a slab of the domain, computes dynamics and physics on it, and exchanges boundary values with neighboring processes at each time step.

## Running Jobs

```bash
# Run with N processes
mpirun -np 4 ./your_program

# Allow more processes than available slots (useful in containers/VMs)
mpirun -np 4 --oversubscribe ./your_program

# Bind processes to cores
mpirun -np 4 --bind-to core ./your_program

# Specify hosts
mpirun -np 4 --host node1:2,node2:2 ./your_program

# Use a hostfile
mpirun -np 4 --hostfile hosts.txt ./your_program
```

## Diagnostics

```bash
# Show MPI version
mpirun --version
ompi_info --version

# Show available hardware threads
mpirun -np 1 --report-bindings ./your_program

# Show full OpenMPI configuration
ompi_info

# List available MCA parameters
ompi_info --param all all

# Check number of available slots without running
mpirun -np 1 --display-map ./your_program
```

## Slot and Resource Control

```bash
# Override slot count (allow oversubscription)
mpirun -np 8 --oversubscribe ./your_program

# Use hardware threads as slots instead of cores
mpirun -np 8 --use-hwthread-cpus ./your_program

# Set slots in a hostfile
# hosts.txt:
# localhost slots=4

# Set MCA parameter to suppress warnings
mpirun -np 4 --mca btl_base_warn_component_unused 0 ./your_program
```

## Environment and Debugging

```bash
# Pass environment variable to all ranks
mpirun -np 4 -x MY_VAR=value ./your_program

# Export existing env var to all ranks
mpirun -np 4 -x OMP_NUM_THREADS ./your_program

# Enable verbose MPI output
mpirun -np 4 --mca mpi_show_handle_leaks 1 ./your_program

# Tag output lines with rank number
mpirun -np 4 --tag-output ./your_program

# Timestamp output
mpirun -np 4 --timestamp-output ./your_program
```

## Process Binding

```bash
# Bind one process per socket
mpirun -np 2 --bind-to socket ./your_program

# Bind one process per NUMA node
mpirun -np 4 --bind-to numa ./your_program

# No binding
mpirun -np 4 --bind-to none ./your_program

# Report bindings
mpirun -np 4 --report-bindings ./your_program
```

## Common Fix: Not Enough Slots

If you see "There are not enough slots available":

```bash
# Option 1: oversubscribe
mpirun -np 4 --oversubscribe ./your_program

# Option 2: use hardware threads
mpirun -np 4 --use-hwthread-cpus ./your_program

# Option 3: reduce process count to match available slots
mpirun -np 2 ./your_program
```
