from ModelEvents import Arrival, EndOfExam, EndOfMentalHealthCare


class Patient:
    def __init__(self, id, if_with_depression):
        """ create a patient
        :param id: (integer) patient ID
        :param if_with_depression: (boolean) patient has depression or not
        """
        self.id = id
        self.if_with_depression = if_with_depression  # patient mental health status
        self.tArrived = None  # time the patient arrived
        self.tJoinedWaitingRoom = None  # time the patient joined the waiting room
        self.tLeftWaitingRoom = None  # time the patient left the waiting room
        self.tJoinedMHWaitingRoom = None  # time the patient joined the mental health waiting room
        self.tLeftMHWaitingRoom = None  # time the patient left the mental health waiting room

    def __str__(self):
        return "Patient " + str(self.id)

class WaitingRoom:
    def __init__(self, sim_out, trace):
        """ create a waiting room
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.patientsWaiting = []   # list of patients in the waiting room for physician
        self.depressedPatientsWaiting = []  # list of patients with depression in the waiting room\
                                            # for mental health specialist
        self.simOut = sim_out        # simulation output
        self.trace = trace           # simulation trace

    def add_patient(self, patient):
        """ add a patient to the waiting room
        :param patient: a patient to be added to the waiting room
        """

        # add the patient to the list of patients waiting
        self.patientsWaiting.append(patient)

        # update statistics for the patient who joins the waiting room
        self.simOut.collect_patient_joining_waiting_room(patient=patient)

        # trace
        self.trace.add_message(
            str(patient) + ' joins the waiting room (physician). Number waiting = '
            + str(len(self.patientsWaiting)) + '.')

    def add_mh_patient(self, patient):
        """ add a patients with depression to the waiting room
        :param patient: a patient with depression to be added to the waiting room
        """

        # add the patient to the list of patients waiting
        self.depressedPatientsWaiting.append(patient)

        # update statistics for the patient who joins the mental health waiting room
        self.simOut.collect_patient_joining_mh_waiting_room(patient=patient)

        # trace
        self.trace.add_message(
            str(patient) + ' joins the waiting room (MH specialist). Number waiting = ' + str(
                len(self.depressedPatientsWaiting)) + '.')

    def get_next_patient(self):
        """
        :returns: the next patient in line
        """
        # update statistics for the patient who leaves the waiting room
        self.simOut.collect_patient_leaving_waiting_room(patient=self.patientsWaiting[0])

        # trace
        self.trace.add_message(
            str(self.patientsWaiting[0]) + ' leaves the physician waiting room. Number waiting = '
            + str(len(self.patientsWaiting) - 1) + '.')

        # pop the patient
        return self.patientsWaiting.pop(0)

    def get_next_mh_patient(self):
        """
        :returns: the next patient with depression in line
        """
        # update statistics for the patient who leaves the MH waiting room
        self.simOut.collect_patient_leaving_mh_waiting_room(patient=self.depressedPatientsWaiting[0])

        # trace
        self.trace.add_message(
            str(self.depressedPatientsWaiting[0]) + ' leaves the MH waiting room. Number waiting = '
            + str(len(self.depressedPatientsWaiting) - 1) + '.')

        # pop the patient
        return self.depressedPatientsWaiting.pop(0)

    def get_num_patients_waiting(self):
        """
        :return: the number of patient waiting in the waiting room
        """
        return len(self.patientsWaiting)

    def get_num_mh_patients_waiting(self):
        """
        :return: the number of patient with depression waiting in the waiting room
        """
        return len(self.depressedPatientsWaiting)


class Physician:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create a physician
        :param id: (integer) the physician ID
        :param service_time_dist: distribution of service time
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.id = id
        self.serviceTimeDist = service_time_dist
        self.urgentCare = urgent_care
        self.simCal = sim_cal
        self.simOut = sim_out
        self.trace = trace
        self.isBusy = False
        self.patientBeingServed = None  # the patient who is being served

    def __str__(self):
        """ :returns (string) the physician id """
        return "Physician " + str(self.id)

    def exam(self, patient, rng):
        """ starts examining the patient
        :param patient: a patient
        :param rng: random number generator
        """

        # the physician is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # collect statistics
        self.simOut.collect_patient_starting_physician_exam()

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            EndOfExam(time=exam_completion_time,
                      physician=self,
                      urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ remove the patient that was being served """

        # collect statistics
        self.simOut.collect_patient_departure_from_physician(patient=self.patientBeingServed)

        if not self.patientBeingServed.if_with_depression:
            self.simOut.collect_patient_departure_from_system(patient=self.patientBeingServed)

        # trace
        self.trace.add_message(str(self.patientBeingServed) + ' leaves ' + str(self) + '.')

        # store the patient to be returned
        returned_patient = self.patientBeingServed

        # set the patient being served to none
        self.patientBeingServed = None

        # the physician is idle now
        self.isBusy = False

        # return the patient that was being served
        return returned_patient


class MHSpecialist:
    def __init__(self, id, service_time_dist, urgent_care, sim_cal, sim_out, trace):
        """ create a mental health specialist
        :param id: (integer) the mental health specialist ID
        :param service_time_dist: distribution of service time
        :param urgent_care: urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """
        self.id = id
        self.serviceTimeDist = service_time_dist
        self.urgentCare = urgent_care
        self.simCal = sim_cal
        self.simOut = sim_out
        self.trace = trace
        self.isBusy = False
        self.patientBeingServed = None  # the patient who is being served

    def __str__(self):
        """ :returns (string) the MH Specialist  id """
        return "MH Specialist " + str(self.id)

    def exam(self, patient, rng):
        """ starts examining the patient with depression
        :param patient: a patient
        :param rng: random number generator
        """

        # the mental health specialist is busy
        self.patientBeingServed = patient
        self.isBusy = True

        # trace
        self.trace.add_message(str(patient) + ' starts service in ' + str(self))

        # collect statistics
        self.simOut.collect_patient_starting_mental_health_exam()

        # find the exam completion time (current time + service time)
        exam_completion_time = self.simCal.time + self.serviceTimeDist.sample(rng=rng)

        # schedule the end of exam
        self.simCal.add_event(
            EndOfMentalHealthCare(time=exam_completion_time,
                                  mh_specialist=self,
                                  urgent_care=self.urgentCare)
        )

    def remove_patient(self):
        """ remove the patient with depression that was being served """

        # collect statistics
        self.simOut.collect_patient_departure_from_mh_specialist(patient=self.patientBeingServed)

        self.simOut.collect_patient_departure_from_system(patient=self.patientBeingServed)

        # trace
        self.trace.add_message(str(self.patientBeingServed) + ' leaves ' + str(self) + '.')

        # the mental health specialist is idle now
        self.isBusy = False

        # remove the patient
        self.patientBeingServed = None


class UrgentCare:
    def __init__(self, id, parameters, sim_cal, sim_out, trace):
        """ creates an urgent care
        :param id: ID of this urgent care
        :param parameters: parameters of this urgent care
        :param sim_cal: simulation calendar
        :param sim_out: simulation output
        :param trace: simulation trace
        """

        self.id = id
        self.params = parameters
        self.simCal = sim_cal
        self.simOut = sim_out
        self.trace = trace

        self.ifOpen = True  # if the urgent care is open and admitting new patients

        # model entities
        # waiting room
        self.waitingRoom = WaitingRoom(sim_out=self.simOut, trace=self.trace)

        # physicians
        self.physician = []
        for i in range(self.params.nPhysicians):
            self.physician.append(Physician(id=i,
                                            service_time_dist=self.params.examTimeDistPhysician,
                                            urgent_care=self,
                                            sim_cal=self.simCal,
                                            sim_out=self.simOut,
                                            trace=self.trace))

        # mental health specialist
        self.mhSpecialist = []
        for i in range(self.params.nMHSpecialist):
            self.mhSpecialist.append(MHSpecialist(id=i,
                                                  service_time_dist=self.params.examTimeDistMHSpecialist,
                                                  urgent_care=self,
                                                  sim_cal=self.simCal,
                                                  sim_out=self.simOut,
                                                  trace=self.trace))

    def process_new_patient(self, patient, rng):
        """ receives a new patient
        :param patient: the new patient
        :param rng: random number generator
        """

        # trace
        self.trace.add_message(
            'Processing arrival of ' + str(patient) + '.')

        # do not admit the patient if the urgent care is closed
        if not self.ifOpen:
            self.trace.add_message('Urgent care is closed. ' + str(patient) + ' does not get admitted.')
            return

        # collect statistics on new patient
        self.simOut.collect_patient_arrival(patient=patient)

        # check if anyone is waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:
            # if anyone is waiting, add the patient to the waiting room
            self.waitingRoom.add_patient(patient=patient)
        else:
            # find an idle physician
            idle_physician_found = False
            for physician in self.physician:
                # if this physician is busy
                if not physician.isBusy:
                    # send the last patient to this physician
                    physician.exam(patient=patient, rng=rng)
                    idle_physician_found = True
                    # break the for loop
                    break

            # if no idle physician was found
            if not idle_physician_found:
                # add the patient to the waiting room
                self.waitingRoom.add_patient(patient=patient)

        # find the arrival time of the next patient (current time + time until next arrival)
        next_arrival_time = self.simCal.time + self.params.arrivalTimeDist.sample(rng=rng)

        # schedule the arrival of the next patient
        self.simCal.add_event(
            event=Arrival(
                time=next_arrival_time,
                patient=Patient(id=patient.id + 1,  # id of the next patient = this patient's id + 1
                                if_with_depression=rng.random_sample() < self.params.propDepressedPatients),  # decide if patient is depressed
                urgent_care=self
            )
        )

    def process_end_of_exam(self, physician, rng):
        """ processes the end of exam for this physician
        :param physician: the physician that finished the exam
        :param rng: random number generator
        """
        # trace
        self.trace.add_message('Processing the end of exam for ' + str(physician) + '.')

        # remove the patient
        patient = physician.remove_patient()

        # get the depression status of the patient and process it as a mental health patient
        if patient.if_with_depression:
            self.process_new_mh_patient(patient, rng)

        # check if there is any patient waiting
        if self.waitingRoom.get_num_patients_waiting() > 0:

            # start serving the next patient in line
            physician.exam(patient=self.waitingRoom.get_next_patient(), rng=rng)

    def process_new_mh_patient(self, patient, rng):
        """receives a new depressed patient
        :param patient: the new depressed patient
        :param rng: random number generator
        """
        # trace
        self.trace.add_message(
            'Processing arrival of MH patient' + str(patient) + '.')

        # check if there are depressed patients in waiting room
        if self.waitingRoom.get_num_mh_patients_waiting() > 0:
            self.waitingRoom.add_mh_patient(patient)
        else:
            # find an idle mental health specialist
            idle_mh_specialist_found = False
            for mhSpecialist in self.mhSpecialist:
                # if this mental health specialist is not busy
                if not mhSpecialist.isBusy:
                    # send the patient to this mental health specialist
                    mhSpecialist.exam(patient=patient, rng=rng)
                    idle_mh_specialist_found = True
                    # break the for loop
                    break

            # if no idle mental health specialist was found
            if not idle_mh_specialist_found:
                # add the patient to the waiting room
                self.waitingRoom.add_mh_patient(patient=patient)

    def process_end_of_mh_exam(self, mhSpecialist, rng):
        """proces end of exam for this MH specialist
        :param mhSpecialist: the mental health specialist that finished the exam
        :param rng: random number generator
        """
        # trace
        self.trace.add_message('Processing the end of exam for ' + str(mhSpecialist) + '.')

        # remove the patient
        mhSpecialist.remove_patient()

        # get the new patient from the waiting queue
        if self.waitingRoom.get_num_mh_patients_waiting() > 0:
            mhSpecialist.exam(patient=self.waitingRoom.get_next_mh_patient(), rng=rng)

    def process_close_urgent_care(self):
        """ process the closing of the urgent care """

        # trace
        self.trace.add_message('Processing the closing of the urgent care.')

        # close the urgent care
        self.ifOpen = False
