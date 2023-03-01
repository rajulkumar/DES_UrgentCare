from deampy.format_functions import format_number
from deampy.sample_path import PrevalenceSamplePath

import DESInputData as D


class SimOutputs:
    # to collect the outputs of a simulation run

    def __init__(self, sim_cal, warm_up_period, trace_on=False):
        """
        :param sim_cal: simulation calendar
        :param warm_up_period: warm up period (hours)
        :param trace_on: set to True to report patient summary
        """

        self.simCal = sim_cal           # simulation calendar (to know the current time)
        self.warmUpPeriod = warm_up_period     # warm up period
        self.traceOn = trace_on         # if should prepare patient summary report
        self.nPatientsArrived = 0       # number of patients arrived
        self.nPatientsServed = 0        # number of patients served
        self.nMHPatientsServed = 0      # number of depressed patients served
        self.patientTimeInSystem = []   # observations on patients time in urgent care
        self.patientTimeInWaitingRoom = []  # observations on patients time in the waiting room
        self.patientTimeInMHWaitingRoom = []  # observations on patients time in the mental health waiting room

        self.patientSummary = []    # id, tArrived, tLeft, duration waited, duration in the system
        if self.traceOn:
            self.patientSummary.append(
                ['Patient', 'Time Arrived', 'Time Left', 'Time Waited(Physician)',
                 'Time Waited(MH Specialist)', 'Time In the System'])

        # sample path for the patients waiting for Physician
        self.nPatientsWaiting = PrevalenceSamplePath(
            name='Number of patients waiting for physician', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the patients waiting for MH Specialist
        self.nMHPatientsWaiting = PrevalenceSamplePath(
            name='Number of patients waiting for MH Specialist', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the patients in system
        self.nPatientInSystem = PrevalenceSamplePath(
            name='Number of patients in the urgent care', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the number of physicians busy
        self.nPhysiciansBusy = PrevalenceSamplePath(
            name='Number of physicians busy', initial_size=0, warm_up_period=warm_up_period)

        # sample path for the number of MH Specialist busy
        self.nMHSpecialistBusy = PrevalenceSamplePath(
            name='Number of MH Specialist busy', initial_size=0, warm_up_period=warm_up_period)

    def collect_patient_arrival(self, patient):
        """ collects statistics upon arrival of a patient
        :param patient: the patient who just arrived
        """

        # increment the number of patients arrived
        if self.simCal.time > self.warmUpPeriod:
            self.nPatientsArrived += 1

        # update the sample path of patients in the system
        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=+1)

        # store arrival time of this patient
        patient.tArrived = self.simCal.time

    def collect_patient_joining_waiting_room(self, patient):
        """ collects statistics when a patient joins the waiting room
        :param patient: the patient who is joining the waiting room
        """

        # store the time this patient joined the waiting room
        patient.tJoinedWaitingRoom = self.simCal.time

        # update the sample path of patients waiting
        self.nPatientsWaiting.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_leaving_waiting_room(self, patient):
        """ collects statistics when a patient leave the waiting room
        :param patient: the patient who is leave the waiting room
        """

        # store the time this patient leaves the waiting room
        patient.tLeftWaitingRoom = self.simCal.time

        # update the sample path
        self.nPatientsWaiting.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_joining_mh_waiting_room(self, patient):
        """ collects statistics when a patient joins the mental health waiting room
        :param patient: the patient who is joining the mental health waiting room
        """

        # store the time this patient joined the waiting room
        patient.tJoinedMHWaitingRoom = self.simCal.time

        # update the sample path of patients waiting
        self.nMHPatientsWaiting.record_increment(time=self.simCal.time, increment=1)

    def collect_patient_leaving_mh_waiting_room(self, patient):
        """ collects statistics when a patient leave the mental health waiting room
        :param patient: the patient who leaves the mental health waiting room
        """

        # store the time this patient leaves the waiting room
        patient.tLeftMHWaitingRoom = self.simCal.time

        # update the sample path
        self.nMHPatientsWaiting.record_increment(time=self.simCal.time, increment=-1)

    def collect_patient_departure_from_physician(self, patient):
        """ collect statistics for patient departing from physician
        :param patient: the departing patient
        """
        if patient.tJoinedWaitingRoom is None:
            time_waiting = 0
        else:
            time_waiting = patient.tLeftWaitingRoom - patient.tJoinedWaitingRoom

        self.nPhysiciansBusy.record_increment(time=self.simCal.time, increment=-1)

        if self.simCal.time > self.warmUpPeriod:
            self.nPatientsServed += 1
            self.patientTimeInWaitingRoom.append(time_waiting)

    def collect_patient_departure_from_mh_specialist(self, patient):
        """ collect statistics for patient departing from mental health specialist
        :param patient: the departing patient
        """
        if patient.tJoinedMHWaitingRoom is None:
            time_waiting = 0
        else:
            time_waiting = patient.tLeftMHWaitingRoom - patient.tJoinedMHWaitingRoom

        self.nMHSpecialistBusy.record_increment(time=self.simCal.time, increment=-1)

        if self.simCal.time > self.warmUpPeriod:
            self.nMHPatientsServed += 1
            self.patientTimeInMHWaitingRoom.append(time_waiting)

    def collect_patient_departure_from_system(self, patient):
        """ collect statistics for patient departing from the urgent care
        :param patient: the departing patient
        """
        time_in_system = self.simCal.time - patient.tArrived

        self.nPatientInSystem.record_increment(time=self.simCal.time, increment=-1)

        if self.simCal.time > self.warmUpPeriod:
            self.patientTimeInSystem.append(time_in_system)

        # determine time spent in waiting rooms for patient summary
        time_waiting_for_physician = patient.tLeftWaitingRoom - patient.tJoinedWaitingRoom \
            if patient.tJoinedWaitingRoom is not None else 0
        time_waiting_for_mh_specialist = patient.tLeftMHWaitingRoom - patient.tJoinedMHWaitingRoom \
            if patient.tJoinedMHWaitingRoom is not None else 0

        # build the patient summary
        if self.traceOn:
            self.patientSummary.append([
                str(patient),  # name
                format_number(patient.tArrived, deci=D.DECI),  # time arrived
                format_number(self.simCal.time, deci=D.DECI),  # time left
                format_number(time_waiting_for_physician, deci=D.DECI),  # time waiting for
                format_number(time_waiting_for_mh_specialist, deci=D.DECI),  # time waiting
                format_number(time_in_system, deci=D.DECI)]  # time in the system
            )

    def collect_patient_starting_physician_exam(self):
        """ collects statistics for a patient who just started the physician exam """

        self.nPhysiciansBusy.record_increment(time=self.simCal.time, increment=+1)

    def collect_patient_starting_mental_health_exam(self):
        """ collects statistics for a patient who just started the mental health exam """

        self.nMHSpecialistBusy.record_increment(time=self.simCal.time, increment=+1)

    def collect_end_of_simulation(self):
        """
        collects the performance statistics at the end of the simulation
        """

        # update sample paths
        self.nPatientsWaiting.close(time=self.simCal.time)
        self.nPatientInSystem.close(time=self.simCal.time)
        self.nPhysiciansBusy.close(time=self.simCal.time)
        self.nMHPatientsWaiting.close(time=self.simCal.time)
        self.nMHSpecialistBusy.close(time=self.simCal.time)

    def get_ave_patient_time_in_system(self):
        """
        :return: average patient time in system
        """

        return sum(self.patientTimeInSystem)/len(self.patientTimeInSystem)

    def get_ave_patient_waiting_time_for_physician(self):
        """
        :return: average patient waiting time for physician
        """

        return sum(self.patientTimeInWaitingRoom)/len(self.patientTimeInWaitingRoom)

    def get_ave_patient_waiting_time_for_mh_specialist(self):
        """
        :return: average patient waiting time for mental health specialist
        """

        return sum(self.patientTimeInMHWaitingRoom)/len(self.patientTimeInMHWaitingRoom)
