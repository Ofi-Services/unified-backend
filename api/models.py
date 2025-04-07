from django.db import models
from .constants import ACTIVITY_CHOICES

#The models are the representations of the database tables. They are used to interact with the database.
class Case(models.Model):
    """
    A model representing a case.

    Attributes:
        id (int): The primary key for the case.
        insurance (int): The insurance of the case.
        avg_time (float): The time that took the case to complete.
        type (str): The type of the case, it can be Issuance, Policy onboarding or Renewal.
        branch (str): The branch of the case.
        ramo (str): The type of insurance of the case.
        brocker (str): The brocker of the insurance.
        state (str): The final state of the case.
        client (str): The client of the insurance.
        creator (str): The creator of the case.
        value (int): The value of the insurance.
        approved (bool): The final approval status of the case.
        insurance_creation (datetime): The timestamp of the insurance creation.
        insurance_start (datetime): The timestamp of when the insurance coverage starts.
        insurance_end (datetime): The timestamp of when the insurance coverage ends.
    """
    id = models.CharField(max_length=25, primary_key=True)
    insurance = models.IntegerField(default=0)
    avg_time = models.FloatField(default=0)
    type = models.CharField(max_length=25, default='None')
    branch = models.CharField(max_length=25, default='None')
    ramo = models.CharField(max_length=25, default='None')
    brocker = models.CharField(max_length=25, default='None')
    state = models.CharField(max_length=25, default='None')
    client = models.CharField(max_length=25, default='None')
    creator = models.CharField(max_length=25, default='None')
    value = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    insurance_creation = models.DateTimeField()
    insurance_start = models.DateTimeField()
    insurance_end = models.DateTimeField()


    def __str__(self):
        return f"Case {self.id}"

class Activity(models.Model):
    """
    A model representing an activity related to a case.

    Attributes:
        id (int): The primary key for the activity.
        case (Case): The related case of the activity
        timestamp (datetime): The timestamp of the activity.
        name (str): The name of the activity, chosen from ACTIVITY_CHOICES.
        case_index (int): The index of the case, with a default value of 0.
        tpt (float): The time per task of the activity, with a default value of 0.
    """
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, related_name='activities', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=25)
    case_index = models.IntegerField(default=0)
    tpt = models.FloatField(default=0)

    def __str__(self):
        return f"{self.case.id} - {self.name} at {self.timestamp}"
    
class Variant(models.Model):
    """
    A model representing a variant.

    Attributes:
        id (int): The primary key for the variant.
        activities (str): The activities of the variant.
        cases (str): The cases of the variant.
        number_cases (int): The amount of cases of the variant.
        percentage (float): The percentage of cases the variant includes.
        avg_time (float): The average time per case of the variant.
    """
    id = models.AutoField(primary_key=True)
    activities = models.CharField(max_length=50)
    cases = models.CharField(max_length=50)
    number_cases = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    avg_time = models.FloatField(default=0)

    def __str__(self):
        return self.name
    

class Bill(models.Model):
    """
    A model representing a bill.

    Attributes:
        id (int): The primary key for the bill.
        case (Case): The ID of the related case.
        timestamp (datetime): The timestamp of the bill.
        value (int): The value of the bill.
    """

    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, related_name='bills', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.case.id} - {self.value} at {self.timestamp} ({self.payment_frequency})"
    
class Rework(models.Model):
    """
    A model representing a rework.

    Attributes:
        id (int): The primary key for the rework.
        activity (Activity): The related activity where the rework happened.
        cost (int): The cost in seconds of the rework.
        target (str): The target of the return.
        cause (str): The cause of the return.
    """

    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Activity, related_name='reworks', on_delete=models.CASCADE)
    cost = models.IntegerField(default=0)
    target = models.CharField(max_length=250, default='None')
    cause = models.CharField(max_length=250, default='None')

    def __str__(self):
        return f"{self.case.id} - {self.value} at {self.timestamp}"
