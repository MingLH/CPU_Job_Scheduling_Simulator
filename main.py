"""
TMF2234 Operating System Semester 1, 2024/2025
Lecturer: Dr. Noralifah Binti Annuar
Lecture Group 4
Project Group 8 
Group Member:
1. Lee Hao Ming (99451)
2. Javin Sim Chuin Cai (97468)
3. Neasthy Laade (97625)
4. Isaac Shagal Anak Tinggal (99176)
5. Muhammad Kalil Bin Sammat (99955)
"""

import queue
from job import jobs_data
import os # this module is just use for clear the screen

# Reset all the jobs to their initial state.
def reset_jobs_data(jobs_data):
    for job in jobs_data:
        job.remaining_operations = job.operations[:]  # Copy of operations to track remaining tasks
        job.completed_operations = 0  # Counter for completed operations
        job.total_interrupts = 0  # count the number of interrupts
        job.completed = False  # Flag to mark if the job is completed
        job.completion_time = 0  # Time when the job is finished
        job.turnaround_time = 0  # Turnaround time (completion time - arrival time)
        job.waiting_time = 0  # Waiting time (time spent waiting in the ready queue)
        job.io_time_remaining = 0   # Time left for ongoing I/O
        job.first_op_type_io = False  # Flag to track if the first operation is I/O
        job.remaining_context_switch = 0  # Track context switches remaining for the job

# Perform Round Robin Scheduling Algorithm
def round_robin(jobs, time_quantum):
    ready_queue = queue.Queue()  # Queue of jobs needed the CPU 
    io_jobs = []  # List of jobs performing I/O
    current_time = 0  # The overall timeline of the execution
    job_index = 0  # Unique id for each Job
    total_turnaround_time = 0  # total turnaround time of all jobs
    total_waiting_time = 0  # total waiting time of all jobs
    total_interrupts = 0  # total interrupts of all jobs

    # Keep looping until all jobs in the list have completed their operations
    while not all(job.completed for job in jobs):

        # Check if any jobs have arrived at the current time
        while job_index < len(jobs) and jobs[job_index].arrival_time <= current_time:
            
            # Directly access the job that has just arrived
            arriving_job = jobs[job_index]  

            # Retrieve the current operation of the arriving job
            current_operation = arriving_job.get_current_operation()

            # If the job has a valid operation, determine its type
            if current_operation:
                type_of_op, _ = current_operation  # Extract the type and duration of the operation

                # If the operation type is 'CPU', add the job to the ready queue
                if type_of_op == 'CPU':
                    ready_queue.put(arriving_job)

                # If the operation type is 'I/O', start the I/O operation and add the job to the I/O jobs list
                elif type_of_op == 'I/O':
                    arriving_job.start_io_operation()
                    io_jobs.append(arriving_job)

                # Move to the next job in the jobs list
                job_index += 1
            else:
                # If no operation is defined for the job, output an error and move to the next job
                print("Error: Job has no operation")
                job_index += 1

        # Check if the ready queue has jobs ready for CPU process
        # Job with I/O operation as the current operation will never make it into the ready queue
        if not ready_queue.empty():
             # Get the next job from the ready queue
            job = ready_queue.get()

            # Handle context switch when it occurs after the job finishes its I/O cycle
            # but there are no other jobs in the ready queue
            if job.remaining_context_switch == 1:
                # Simulate the time spent on context switching
                current_time += 1
                
                # Iterate over I/O jobs using a shallow copy to avoid modification issues
                for j in io_jobs[:]:  
                    
                    # Progress one I/O operation for the jobs in I/O jobs list
                    j.progress_io()

                     # Check if the I/O operation for the job is complete
                    if j.io_time_remaining == 0:
                        # Get the next operation after I/O completion
                        after_job_IO_cycle = j.get_current_operation()

                        # If the job has a valid operation, determine its type
                        if after_job_IO_cycle:
                            OP_type, _ = after_job_IO_cycle

                            # If the next operation is CPU
                            if OP_type == 'CPU':
                                io_jobs.remove(j)  # Remove the job from I/O jobs
                                ready_queue.put(j)  # Re-add the job to the ready queue
                                continue  # Continue to process the next job in the I/O list
                            
                            # If the next operation is another I/O cycle, start its I/O cycle.
                            elif OP_type == 'I/O':
                                j.start_io_operation()
                                continue  

                        # If no further operations exist, mark the job as completed
                        else:
                            j.completed = True  # Mark the job as completed
                            j.completion_time = current_time  # Record the completion time
                            j.turnaround_time = j.completion_time - j.arrival_time  # Calculate turnaround time
                            io_jobs.remove(j)  # Remove the job from I/O jobs
                            continue  # Continue to process the next job in the I/O list
                
                # End the context switch after one CPU cycle
                job.remaining_context_switch -= 1

            # Retrieve the current operation of the job from ready queue
            current_op = job.get_current_operation()

            # If the job has a valid operation, determine its type
            if current_op:
                op_type, _ = current_op

                # If the next operation is CPU
                if op_type == 'CPU':
                    # Perform CPU operation with the defined time quantum
                    cycles_processed = job.perform_cpu_operation(time_quantum)

                    # For each CPU cycle_processed of the job
                    for _ in range(cycles_processed):
                        current_time += 1  # Increment current time for each CPU cycle

                        # Add jobs arriving at the current time to the ready queue
                        while job_index < len(jobs) and jobs[job_index].arrival_time <= current_time:

                            # Directly access the current job
                            arriving_job = jobs[job_index] 
                            current_operation = arriving_job.get_current_operation()

                            if current_operation:
                                type_of_op, _ = current_operation

                                 # Add job to the ready queue if its operation is CPU
                                if type_of_op == 'CPU':
                                    ready_queue.put(arriving_job)

                                # If the job's first operation is I/O, start it immediately
                                elif type_of_op == 'I/O':       
                                    arriving_job.start_io_operation()
                                    arriving_job.first_op_type_io = True  # Arrive job first operation is I/O
                                    io_jobs.append(arriving_job)  # Add job to the io_jobs list

                                job_index += 1  # Move to the next job in the list
                            else:
                                print("Error: Job has no operation")
                                job_index += 1
                        
                        # Handle I/O jobs
                        for j in io_jobs[:]: 
                            # Skip processing if the job's first operation was I/O and hasn't been processed yet
                            if j.first_op_type_io == True:
                                j.first_op_type_io = False
                                continue
                            
                            # Progress the I/O operation
                            j.progress_io()

                            # Check if the I/O operation is complete
                            if j.io_time_remaining == 0:
                                after_job_IO_cycle = j.get_current_operation()

                                if after_job_IO_cycle:
                                    OP_type, _ = after_job_IO_cycle

                                     # If the next operation is CPU, move the job back to the ready queue
                                    if OP_type == 'CPU':
                                        io_jobs.remove(j)  # Remove from I/O jobs
                                        ready_queue.put(j)  # Re-add to ready queue
                                        continue  # Continue to the next I/O job
                                    
                                    # If the next operation is another I/O cycle, start it
                                    elif OP_type == 'I/O':
                                        j.start_io_operation() 
                                        continue

                                # If no further operations exist, mark the job as completed
                                else:
                                    j.completed = True  # Mark the job as completed
                                    j.completion_time = current_time  # Record completion time
                                    j.turnaround_time = j.completion_time - j.arrival_time  # Calculate turnaround time
                                    io_jobs.remove(j)  # Remove the job from I/O jobs
                                    continue

                    # After the job run finish its CPU cycle
                    after_job_CPU_cycle = job.get_current_operation()

                    # If the job has a valid operation, determine its type
                    if after_job_CPU_cycle:
                        after_job_Op_type, _ = after_job_CPU_cycle

                        # If the current job CPU cycle haven't finish running
                        if after_job_Op_type == 'CPU':

                            # Check if the ready queue is empty
                            if ready_queue.empty():
                                ready_queue.put(job)  # Re-add the job to the ready queue
                            # Context switch occurs when the ready queue is not empty
                            else: 
                                # Interrupt occur to switch the running job to the ready_queue job
                                job.total_interrupts += 1
                                ready_queue.put(job) # Re-add the current job to the ready queue

                                 # Simulate context switch overhead by incrementing the current time
                                current_time += 1

                                # Iterate through all I/O jobs and progress their I/O operations
                                for j in io_jobs[:]: 
                                    j.progress_io()  # Progress the I/O operation for the job in io_jobs list

                                    # If the job's I/O operation is completed
                                    if j.io_time_remaining == 0:
                                        # Determine the job's next operation
                                        after_job_IO_cycle = j.get_current_operation()

                                        if after_job_IO_cycle:
                                            OP_type, _ = after_job_IO_cycle

                                            # If the next operation is a CPU cycle
                                            if OP_type == 'CPU':
                                                io_jobs.remove(j)  # Remove the job from I/O jobs
                                                ready_queue.put(j)  # Add the job to the ready queue
                                                continue  # Move to the next I/O job in the list
                                            
                                            # If the next operation is another I/O cycle
                                            elif OP_type == 'I/O':
                                                j.start_io_operation() # Restart the I/O operation
                                                continue

                                        # If the job's last operation is completed and there are no more operations
                                        else:
                                            j.completed = True  # Mark the job as completed
                                            j.completion_time = current_time  # Record the job's completion time
                                            j.turnaround_time = j.completion_time - j.arrival_time  # Calculate turnaround time
                                            io_jobs.remove(j)  # Remove the job from the I/O jobs list
                                            continue

                        # Job completed its current CPU cycle and next is I/O operation
                        elif after_job_Op_type == 'I/O':
                            # Check if a context switch will occur by checking if the ready queue is empty
                            if ready_queue.empty():
                                job.start_io_operation()  # Start the I/O operation for the job
                                io_jobs.append(job)   # Add the job to io_jobs list

                            # Context switch occurs because the ready queue is not empty
                            else:
                                job.start_io_operation()  # Start the I/O operation for the job
                                io_jobs.append(job)  # Add the job to the list of I/O jobs

                                # Simulate context switch overhead by incrementing the current time
                                current_time += 1

                                # Every time a context switch occurs, progress the I/O cycles for all jobs in the I/O queue
                                for j in io_jobs[:]: 
                                    # Progress the I/O operation for the jobs in io_jobs list
                                    j.progress_io()

                                    # If the I/O operation is completed
                                    if j.io_time_remaining == 0:
                                        # Determine the job's next operation
                                        after_job_IO_cycle = j.get_current_operation()

                                        if after_job_IO_cycle:
                                            OP_type, _ = after_job_IO_cycle

                                            # If the next operation is a CPU cycle
                                            if OP_type == 'CPU':
                                                io_jobs.remove(j)  # Remove the job from the I/O jobs list
                                                ready_queue.put(j)  # Add the job to the ready queue
                                                continue  # Continue to the next I/O job in the list
                                            
                                             # If the next operation is another I/O cycle
                                            elif OP_type == 'I/O':
                                                j.start_io_operation()  # Restart the I/O operation
                                                continue

                                        # If the job's last operation is completed and there are no more operations
                                        else:
                                            j.completed = True  # Mark the job as completed
                                            j.completion_time = current_time   # Record the job's completion time
                                            j.turnaround_time = j.completion_time - j.arrival_time  # Calculate turnaround time
                                            io_jobs.remove(j)  # Remove the job from the I/O jobs list
                                            continue
                        # If the job's operation type is unrecognized, log an error
                        else:
                            print("Error: job's operation not found")

                    # If no valid operations are left for the job after the job finish its CPU cycle
                    else:
                        job.completed = True  # Mark the job as completed
                        job.completion_time = current_time  # Record the job's completion time
                        job.turnaround_time = job.completion_time - job.arrival_time  # Calculate turnaround time

            # If the job loaded into ready_queue doens't have operation
            else:
                print("Error: The job has no operation")

        # if no job is in the ready queue
        else:
            # Increment the current time to simulate CPU idle time
            current_time += 1  

            # Flag to indicate if a context switch will occur due to the first job in io_jobs moving to the ready queue
            first_job_for_next_op_is_CPU = False

            # Handle I/O jobs
            for job in io_jobs[:]:  
                # Progress the I/O operation for the job
                job.progress_io()

                # Check if the job's I/O operation is completed
                if job.io_time_remaining == 0:

                    # Get the job's next operation after I/O completion
                    after_job_IO_cycle = job.get_current_operation()

                    # If there is a subsequent operation
                    if after_job_IO_cycle:
                        OP_type, _ = after_job_IO_cycle

                        # If the next operation is a CPU cycle
                        if OP_type == 'CPU':
                            # If this is the first job causing a context switch
                            if first_job_for_next_op_is_CPU == False:
                                io_jobs.remove(job)  # Remove the job from the I/O queue
                                ready_queue.put(job)  # Add the job to the ready queue

                                # This Context Switch will occur when the job enqueue into the ready queue and wanting to get the CPU
                                job.remaining_context_switch += 1
                                first_job_for_next_op_is_CPU = True  # Update the flag to indicate a context switch has occurred

                                continue  # Exit the loop for this job
                            else:
                                # If not the first job to move to ready_queue, simply move it to the ready queue
                                io_jobs.remove(job)  
                                ready_queue.put(job)  
                                continue  # Exit the loop for this job
                        
                        # If the next operation is another I/O cycle
                        elif OP_type == 'I/O':
                            job.start_io_operation()  # Start the new I/O operation
                            continue

                     # If the job's last operation is completed (no more operations)
                    else:
                        job.completed = True  # Mark the job as completed
                        job.completion_time = current_time  # Record the completion time
                        job.turnaround_time = job.completion_time - job.arrival_time  # Calculate turnaround time
                        io_jobs.remove(job)  # Remove the job from the I/O queue
                        continue

    # Calculate the total turnaround time, waiting time and number of interrupt for the jobs
    for job in jobs:

        # Calculated the total turnaround time
        total_turnaround_time += job.turnaround_time

        # Calculate the waiting time by total up all the operation cycle and minus with turnaround time
        total_exec_time = sum(op[1] for op in job.operations)
        job.waiting_time = job.turnaround_time - total_exec_time
        total_waiting_time += job.waiting_time # Calculate the total waiting time

        # Calculate the total number of interrupt 
        total_interrupts += job.total_interrupts

    # Calculating the average turnaround time of the jobs
    average_turnaround_time = total_turnaround_time / len(jobs)

    # Calculating the average waiting time of the jobs
    average_waiting_time = total_waiting_time / len(jobs)

    return jobs, average_turnaround_time, average_waiting_time, total_interrupts

# main user interface and function of the program
def main():
    while True:
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display the title of the program
        print("Round Robin Scheduling Algorithm")
        print("================================")
        
        try:
             # Prompt the user to input the time quantum
            time_quantum = int(input("Enter a time quantum (or type -1 to exit): "))

            # Check if the user wants to exit the scheduler
            if time_quantum == -1:
                print(f"Exiting the scheduler. Goodbye!\n")
                break  # Exit the loop and end the program
            
             # Validate that the time quantum is a positive integer
            if time_quantum <= 0:
                print(f"Invalid input. Time quantum must be a positive integer.\n")
                input("Press Enter to try again...")
                continue

            # Reset job data to its initial state before starting the round-robin scheduling
            reset_jobs_data(jobs_data)
            
            # Execute the round-robin scheduling algorithm
            scheduled_jobs, average_turnaround_time, average_waiting_time, total_interrupts = round_robin(jobs_data, time_quantum)
            
            # Clear the console again before displaying output
            os.system('cls' if os.name == 'nt' else 'clear')

            # Display the results
            print("Job Summary")

            # Print table headers
            print(f"{'Job ID':<10}{'Arrival Time':<15}{'Completion Time':<20}{'Turnaround Time':<20}{'Waiting Time':<15}{'Total Interrupts':<15}")

             # Loop through and display the details of each job
            for job in scheduled_jobs:
                print(f"{job.job_id:<10}{job.arrival_time:<15}{job.completion_time:<20}{job.turnaround_time:<20}{job.waiting_time:<15}{job.total_interrupts:<15}")
            
            # Display summary statistics for all jobs
            print(f"\nAverage Turnaround Time: {average_turnaround_time:.2f}")
            print(f"Average Waiting Time: {average_waiting_time:.2f}")
            print(f"Total Interrupts: {total_interrupts}")
            input("\nPress Enter to continue...")

         # Handle invalid input if the user enters a non-integer value
        except ValueError:
            print(f"Invalid input. Please enter a valid integer.\n")
            input("Press Enter to try again...")

# Driver code
if __name__ == "__main__":
    main()

