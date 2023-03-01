
#  trace
TRACE_ON = True   # set to true to trace a simulation replication
DECI = 5          # the decimal point to round the numbers to in the trace file

# simulation settings
SIM_DURATION = 100000   # (hours) a large number to make sure the simulation will be terminated eventually but
                        # the simulation continues as long as there is a patient in the urgent care.
WARM_UP = 0
HOURS_OPEN = 20                   # hours the urgent cares open
N_PHYSICIANS = 10                 # number of physicians
N_MENTAL_HEALTH_SPECIALIST = 5    # number of mental health specialist
MEAN_ARRIVAL_TIME = 1/60          # mean patients inter-arrival time (hours)
MEAN_EXAM_DURATION_PHYSICIAN = 10/60       # mean of exam duration for physician (hours)
MEAN_EXAM_DURATION_MENTAL_HEALTH = 20/60   # mean of exam duration for mental health specialist (hours)
PROP_DEPRESSED_PATIENTS = 0.2              # proportion of patients with depression
