from deampy.discrete_event_sim import SimulationEvent

import DESInputData as D

""" priority for processing the urgent care simulation events
if they are to occur at the exact same time (low number implies higher priority)"""
ARRIVAL = 2
END_OF_EXAM = 0
END_OF_MH_EXAM = 1
CLOSE = 3


class Arrival(SimulationEvent):
    def __init__(self, time, patient, urgent_care):
        """
        creates the arrival of the next patient event
        :param time: time of next patient's arrival
        :param patient: next patient
        :param urgent_care: the urgent care
        """
        # initialize the base class
        SimulationEvent.__init__(self, time=time, priority=ARRIVAL)

        self.patient = patient
        self.urgentCare = urgent_care

        # trace
        urgent_care.trace.add_message(
            str(patient) + ' will arrive at time {t:.{deci}f}.'.format(t=time, deci=D.DECI))

    def process(self, rng=None):
        """ processes the arrival of a new patient """

        # receive the new patient
        self.urgentCare.process_new_patient(patient=self.patient, rng=rng)


class EndOfExam(SimulationEvent):
    def __init__(self, time, physician, urgent_care):
        """
        create the end of service for a specified physician
        :param time: time of the service completion
        :param physician: the physician
        :param urgent_care: the urgent care
        """
        # initialize the base class
        SimulationEvent.__init__(self, time=time, priority=END_OF_EXAM)

        self.physician = physician
        self.urgentCare = urgent_care

        # trace
        urgent_care.trace.add_message(
            str(physician) + ' will finish physician service at time {t:.{deci}f}.'.format(t=time, deci=D.DECI))

    def process(self, rng=None):
        """ processes the end of service event """

        # process the end of service for this physician
        self.urgentCare.process_end_of_exam(physician=self.physician, rng=rng)


class CloseUrgentCare(SimulationEvent):
    def __init__(self, time, urgent_care):
        """
        create the event to close the urgent care
        :param time: time of closure
        :param urgent_care: the urgent care
        """

        self.urgentCare = urgent_care

        # call the master class initialization
        SimulationEvent.__init__(self, time=time, priority=CLOSE)

        # trace
        urgent_care.trace.add_message(
            'Urgent care will close at time {t:.{deci}f}.'.format(t=time, deci=D.DECI))

    def process(self, rng=None):
        """ processes the closing event """

        # close the urgent care
        self.urgentCare.process_close_urgent_care()


class EndOfMentalHealthCare(SimulationEvent):
    def __init__(self, time, mh_specialist, urgent_care):
        """
        create the end of service for a specified mental health specialist
        :param time: time of the service completion
        :param mh_specialist: the mental health specialist
        :param urgent_care: the urgent care
        """
        SimulationEvent.__init__(self, time=time, priority=END_OF_MH_EXAM)
        self.mhSpecialist = mh_specialist
        self.urgentCare = urgent_care

        # trace
        urgent_care.trace.add_message(
            str(mh_specialist) + ' will finish MH Specialist service at time {t:.{deci}f}.'.format(t=time, deci=D.DECI))

    def process(self, rng=None):
        """process of mental health exam service"""
        self.urgentCare.process_end_of_mh_exam(mhSpecialist=self.mhSpecialist, rng=rng)
