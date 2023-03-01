from deampy.random_variats import Exponential

import DESInputData as D


class Parameters:
    # class to contain the parameters of the urgent care model
    def __init__(self):
        self.hoursOpen = D.HOURS_OPEN
        self.nPhysicians = D.N_PHYSICIANS
        self.nMHSpecialist = D.N_MENTAL_HEALTH_SPECIALIST
        self.arrivalTimeDist = Exponential(scale=D.MEAN_ARRIVAL_TIME)
        self.examTimeDistPhysician = Exponential(scale=D.MEAN_EXAM_DURATION_PHYSICIAN)
        self.examTimeDistMHSpecialist = Exponential(scale=D.MEAN_EXAM_DURATION_MENTAL_HEALTH)
        self.propDepressedPatients = D.PROP_DEPRESSED_PATIENTS
