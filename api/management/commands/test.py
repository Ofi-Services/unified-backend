import csv
from django.core.management.base import BaseCommand
from api.models import Case, Activity, Variant, Bill, Rework
from django.conf import settings
import os
from datetime import datetime
from collections import defaultdict
import random
from datetime import timedelta
from django.db import models
from django.db.models import Count, ExpressionWrapper, F, Avg, DurationField, Sum
from ..constants import NAMES, RAMOS, BRANCHES
import json
from django.utils import timezone

class Command(BaseCommand):
   
    def answer(self):
        """
        Calculate the total value of cases with at least 20 recorded activities.
        """
        # Get all cases with more than 20 activities
        activities = Activity.objects.values('case').annotate(
            activity_count=Count('id')
        ).filter(activity_count__gt=24)

        # Get the IDs of the cases with more than 20 activities
        case_ids = [activity['case'] for activity in activities]
        # Get the cases with the specified IDs and sum their values
        cases = Case.objects.filter(id__in=case_ids)
        
        #sum the value of each case
        total_value = 0
        for case in cases:
            total_value += case.value
        # Print the total value
        print(f"Total value of cases with more than 25 activities: {total_value}")
        

    def handle(self, *args, **kwargs):
        """
        Handle the command to add data to the database from the CSV file.
        """

        self.answer()
        