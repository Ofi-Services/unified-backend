import csv
from django.core.management.base import BaseCommand
from api.models import Case, Activity, Variant, Bill, Rework
from django.conf import settings
import os
from datetime import datetime
from collections import defaultdict
import random
from datetime import timedelta
from ..constants import NAMES, RAMOS, BRANCHES
import json
from django.utils import timezone

class Command(BaseCommand):
    """
    Django management command to add data to the database from a CSV file.
    """
    help = 'Add data to the database from CSV file'
    
    class Case:
        def __init__(self, case_id, case_type, last_timestamp, branch, ramo, brocker, state, client, creator, value, insurance):
            self.case_id = case_id
            self.type = case_type
            self.last_timestamp = last_timestamp
            self.branch = branch
            self.ramo = ramo
            self.brocker = brocker
            self.state = state
            self.client = client
            self.creator = creator
            self.value = value
            self.insurance = insurance

    cases_ids = []

    def new_case_id(self):
        """
        Generate a new unique case ID.

        Returns:
            int: A unique case ID.
        """
        case_id = random.randint(1, 10000)
        while case_id in self.cases_ids:
            case_id = random.randint(1, 10000)
        self.cases_ids.append(case_id)
        return case_id
    
    def write_in_file(self, case: Case, activity):
        """
        Write the data to the CSV file.

        Args:
            case (Case): The Case object.
            activity (str): The activity name.
        """

        #Write in the csv file
        file_exists = os.path.isfile('data.csv')
        with open('data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Case ID', 'Activity', 'Timestamp', 'Case Type', 'Branch', 'Ramo', 'Brocker', 'Client', 'Creator', 'Value', 'Insurance', 'State'])
            writer.writerow([case.case_id, activity, case.last_timestamp, case.type, case.branch, case.ramo, case.brocker, case.client, case.creator, case.value, case.insurance, case.state])
        
        #Get the case and create the activity
        case2 = Case.objects.get(id=case.case_id)

        Activity.objects.create(case = case2, name=activity, timestamp=case.last_timestamp, case_index=case.case_id)


    def update_case(self, case: Case, activity):
        """
        Updates the state and last timestamp of a given case, and synchronizes the changes
        with the corresponding database entry. Additionally, logs the update to a file.
        Args:
            case (Case): The case object to be updated.
            activity: The new state/activity to assign to the case.
        Side Effects:
            - Modifies the `last_timestamp` and `state` attributes of the provided `case` object.
            - Updates the corresponding database entry for the case with the new state.
            - Writes the updated case information and activity to a file.
        Raises:
            Case.DoesNotExist: If no case with the given `case_id` exists in the database.
        """
        case.last_timestamp +=  timedelta(hours=random.expovariate(1/12))
        case.state = activity
        case2 = Case.objects.get(id=case.case_id)
        case2.state = activity
        case2.save()

        self.write_in_file(case, activity)

    def start(self):
        """
        Simulates the creation of a dummy case with randomized attributes and stores it in the database.
        The method generates a case with random attributes such as case type, timestamps, branch, 
        client, creator, and insurance details. It also determines the insurance creation, start, 
        and end dates based on a random condition. The case is then saved to the database, and 
        additional actions are performed based on the case type.
        Actions:
        - If the case type is 'Policy onboarding', the `ingresar_tramite` method is called.
        - If the case type is 'Renewal', there is a 50% chance that the `visado` method is called.
        - The `registro_de_compromiso` method is always called for the case.
        Attributes:
            case_type (str): The type of the case, randomly chosen from 'Renewal', 'Issuance', or 'Policy onboarding'.
            case_id (str): A unique identifier for the case.
            initial_timestamp (datetime): The initial timestamp for the case, randomized within a specific range.
            value (int): The monetary value associated with the case, randomized between 1000 and 10000.
            insurance (str): A randomly generated insurance number.
            insurance_creation (datetime): The timestamp for when the insurance was created.
            insurance_start (datetime): The start date of the insurance.
            insurance_end (datetime): The end date of the insurance.
        Database:
            Creates a `Case` object in the database with the generated attributes.
        Raises:
            None
        Returns:
            None
        """
        case_type = random.choice(['Renewal', 'Issuance', 'Policy onboarding'])
        case_id = self.new_case_id()
        initial_timestamp = timezone.make_aware(datetime(2025, 1, 1, 12, 0, 0) + timedelta(days=random.randint(1, 76), hours=random.randint(1, 24), minutes=random.randint(1, 60), seconds=random.randint(1, 60)))
        value = random.randint(10, 100)*100
        insurance = f"{random.randint(1, 100000):06d}"
        case = self.Case(case_id, case_type, initial_timestamp, branch=random.choice(BRANCHES), ramo=random.choice(RAMOS), brocker=random.choice(NAMES), state = 'Start', client =random.choice(NAMES), creator = random.choice(NAMES), value=value, insurance=insurance)
        rand_num = random.randint(1, 100)
        if rand_num <= 10:
            insurance_creation = initial_timestamp - timedelta(days=random.randint(1, 5))
            insurance_start = initial_timestamp - timedelta(days=random.randint(1, 5))
            insurance_end = insurance_start + timedelta(days=random.choice([180, 365, 730]))
        else:
            insurance_creation = initial_timestamp + timedelta(days=random.randint(1, 5))
            insurance_start = initial_timestamp + timedelta(days=random.randint(1, 5))
            insurance_end = insurance_start + timedelta(days=random.choice([180, 365, 730]))
        

        Case.objects.create(id=case.case_id, type=case.type, avg_time=0, branch=case.branch, ramo=case.ramo, brocker=case.brocker, state=case.state, client=case.client, creator=case.creator, value=case.value, insurance=insurance, insurance_creation=insurance_creation, insurance_start=insurance_start, insurance_end=insurance_end)
        
        if case_type == 'Policy onboarding':
            self.ingresar_tramite(case)
        elif case_type == 'Renewal':
            rand_num = random.randint(1, 100)
            if rand_num <= 50:
                self.visado(case)
      
        self.registro_de_compromiso(case)

    def ingresar_tramite(self, case: Case):
        """
        Add a record of commitment to the database.

        Args:
            case_id (str): The ID of the case.
            initial_timestamp (datetime): The initial timestamp.
            case_type (str): The type of the case.
        """
        self.update_case(case, 'Ingresar tramite')
        
        self.registrar_PO(case)
    
    def registrar_PO(self, case: Case):
        """
        Handles the process of registering a Purchase Order (PO) for a given case. 
        This method updates the case status to 'Registrar PO' and performs a random check 
        to determine the next steps. If the random number is less than or equal to 10, 
        the case is returned to the broker for review, and a rework entry is created 
        with details about the cause and cost of the rework. The method then recursively 
        calls itself to retry the registration process. Otherwise, the case status is 
        updated to 'Enviar a emision', and the emission review process is initiated.
        Args:
            case (Case): The case object for which the PO registration process is being handled.
        Raises:
            Any exceptions raised by the database operations or random module will propagate.
        """
      
        self.update_case(case, 'Registrar PO')
        
        rand_num = random.randint(1, 100)
        if rand_num <= 10:
            self.update_case(case, 'Devolucion al brocker del caso (Revision Brocker)')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name = 'Registrar PO').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target= 'Registrar PO', cause=cause)
            
            self.registrar_PO(case)
        else:
            self.update_case(case, 'Enviar a emision')
            self.revision_emision(case)

    def registro_de_compromiso(self, case: Case):
        """
        Handles the 'Registro de compromiso' process for a given case.
        This method updates the case status to 'Registro de compromiso' and 
        initiates the subscription review process.
        Args:
            case (Case): The case object to be processed.
        """

        self.update_case(case, 'Registro de compromiso')
        self.enviar_revision_suscripcion(case)
    
    def enviar_revision_suscripcion(self, case: Case):
        """
        Handles the process of sending a subscription case for review.
        This method updates the case status to 'Enviar a Revisión suscripción' 
        and randomly determines the next step in the process. If the random 
        number generated is less than or equal to 50, it validates the 
        information sent. Otherwise, it proceeds with the subscription review.
        Args:
            case (Case): The subscription case to be processed.
        """

        self.update_case(case, 'Enviar a Revisión suscripción')
        rand_num = random.randint(1, 100)
        if rand_num <= 50:
            self.validar_info_enviada(case)
        else:
            self.revision_suscripcion(case)
    
    def validar_info_enviada(self, case: Case):
        """
        Validates the information sent for a given case and updates its status accordingly.
        This method performs the following steps:
        1. Updates the case status to 'Validar info enviada'.
        2. Generates a random number to determine the next action:
           - If the random number is less than or equal to 10:
             a. Updates the case status to 'Devolver caso a Comercial'.
             b. Calculates the cost of rework based on the time difference between the last activity 
                and the 'Enviar a Revisión suscripción' activity.
             c. Creates a Rework object with the calculated cost and a randomly chosen cause.
             d. Sends the case back for subscription review by calling `enviar_revision_suscripcion`.
           - Otherwise:
             a. Proceeds with subscription review by calling `revision_suscripcion`.
        Args:
            case (Case): The case object to validate and process.
        Returns:
            None
        """

        self.update_case(case, 'Validar info enviada')
        rand_num = random.randint(1, 100)
        if rand_num <= 10:
            self.update_case(case, 'Devolver caso a Comercial')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name = 'Enviar a Revisión suscripción').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Enviar a Revisión suscripción', cause=cause)

            self.enviar_revision_suscripcion(case)
        else:
            self.revision_suscripcion(case)
    
    def revision_suscripcion(self, case: Case):
        """
        Handles the subscription review process for a given case.
        This method updates the case status through various stages of the subscription
        review process. It includes random branching logic to simulate different outcomes
        such as returning the case for rework, sending it to local subscription, declining
        the request, or approving the subscription.
        Args:
            case (Case): The case object to be processed.
        Workflow:
            1. Updates the case status to 'Revisión en suscripción'.
            2. Randomly determines if the case should be returned for rework (10% chance).
                - If returned, calculates the rework cost and creates a Rework object.
                - Sends the case back for subscription review.
            3. If not returned for rework, sends the case to local subscription (90% chance).
            4. Randomly determines if the case should be declined (10% chance).
                - If not declined, approves the local subscription.
        Note:
            - The random branching logic is based on predefined probabilities.
            - Rework causes are chosen randomly from a predefined list.
        """

        self.update_case(case, 'Revisión en suscripción')
        rand_num = random.randint(1, 50)
        if rand_num <= 10:
            self.update_case(case, 'Realizar devolucion desde suscripcion')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name = 'Enviar a Revisión suscripción').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Enviar a Revisión suscripción', cause=cause)

            self.enviar_revision_suscripcion(case)
        elif rand_num <= 50:
            self.update_case(case, 'Enviar a suscripcion local')
            
        rand_num = random.randint(1, 100)
        if rand_num <= 10:
            self.update_case(case, 'Declinar solicitud en suscripcion')
        else:
            self.aprobar_suscripcion_local(case)

    def aprobar_suscripcion_local(self, case: Case):
        """
        Handles the subscription approval process for a given case.
        This method performs the following steps:
        1. Updates the case with the status 'Aprobar solicitud en suscripcion local'.
        2. Updates the case with the status 'Enviar respuesta al area comercial'.
        3. Generates a random number to determine the next action:
           - If the number is less than or equal to 33, updates the case with the status 
             'Rechazar (perdida) por parte del Brocker'.
           - If the number is less than or equal to 66, updates the case with the status 
             'Declinar por parte del Brocker'.
           - Otherwise, calls the `aceptar_brocker` method to accept the case.
        Args:
            case (Case): The case object to process.
        """

        self.update_case(case, 'Aprobar solicitud en suscripcion local')
        self.update_case(case, 'Enviar respuesta al area comercial')
        
        rand_num = random.randint(1, 100)
        if rand_num <= 33:
            self.update_case(case, 'Rechazar (perdida) por parte del Brocker')
        elif rand_num <= 66:
            self.update_case(case, 'Declinar por parte del Brocker')
        else:
            self.aceptar_brocker(case)

    def aceptar_brocker(self, case: Case):
        """
        Updates the given case to indicate acceptance by the broker and processes it further.
        This method updates the status of the provided case to reflect that it has been 
        accepted (marked as "ganado") by the broker. After updating the case, it proceeds 
        to perform additional processing by invoking the `visado` method.
        Args:
            case (Case): The case object to be updated and processed.
        """

        self.update_case(case, 'Aceptar (ganado) por parte del Brocker')
        self.visado(case)

    def visado(self, case: Case):
        """
        Processes the 'Visado' stage for a given case.
        This method updates the case to the 'Visado' stage and determines whether 
        the case should be returned to the commercial team for rework or proceed 
        to the 'Revision Emision' stage. If the case is returned, a rework entry 
        is created with a randomly selected cause and the cost is calculated based 
        on the time difference between the last activity and the initial 'Visado' 
        activity. The method recursively calls itself to reprocess the case after 
        rework.
        Args:
            case (Case): The case object to process.
        Raises:
            None
        """

        self.update_case(case, 'Visado')
        
        rand_num = random.randint(1, 100)
        if rand_num <= 10:
            self.update_case(case, 'Devolucion a comercial desde visado')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name='Visado').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Visado', cause=cause)

            self.visado(case)
        else:
            self.revision_emision(case)

            
    def revision_emision(self, case: Case):
        """
        Handles the "Revisión en emisión" process for a given case. This method updates the case's status 
        and performs various actions based on a random number to simulate different workflows.
        Args:
            case (Case): The case object to process.
        Workflow:
            - Updates the case status to "Revisión en emisión".
            - Generates a random number to determine the next steps:
                - If the random number is <= 10:
                    - Updates the case status to "Devolucion a comercial desde emisión".
                    - Calculates the cost of rework based on timestamps of activities.
                    - Creates a Rework object with the calculated cost and a randomly chosen cause.
                    - Recursively calls `revision_emision` to repeat the process.
                - If the random number is <= 20:
                    - Updates the case status to "Devolucion a visado desde emisión".
                    - Calculates the cost of rework based on timestamps of activities.
                    - Creates a Rework object with the calculated cost and a randomly chosen cause.
                    - Calls `visado` to handle the next step.
                - If the random number is <= 50:
                    - Updates the case status to "Control de calidad documental".
                    - Updates the case status to "Devolucion a emision de control de calidad".
                    - Calls `iniciar_facturacion` to initiate billing.
                - Otherwise:
                    - Calls `iniciar_facturacion` to initiate billing.
        Notes:
            - The method uses randomization to simulate different scenarios.
            - It interacts with the `Activity` and `Rework` models to log activities and rework details.
            - Recursive calls are made in specific cases, which could lead to deep recursion depending on the random outcomes.
        """

        self.update_case(case, 'Revisión en emisión')
        rand_num = random.randint(1, 100)
        if rand_num <= 10:
            self.update_case(case, 'Devolucion a comercial desde emisión')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name='Revisión en emisión').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Revisión en emisión', cause=cause)

            self.revision_emision(case)
        elif rand_num <= 20:
            self.update_case(case, 'Devolucion a visado desde emisión')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name='Visado').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Visado', cause=cause)

            self.visado(case)
        elif rand_num <= 50:
            self.update_case(case, 'Control de calidad documental')
            self.update_case(case, 'Devolucion a emision de control de calidad')
            self.iniciar_facturacion(case)
        else:
            self.iniciar_facturacion(case)
    
    def iniciar_facturacion(self, case: Case):
        """
        Handles the billing process for a given case by updating its status through
        various stages and generating monthly bills from the last recorded timestamp 
        to the current date.
        Args:
            case (Case): The case object for which the billing process is initiated.
        Workflow:
            1. Updates the case status to 'Iniciar facturación'.
            2. Updates the case status to 'Generar Factura'.
            3. Creates a bill for every month from the last recorded timestamp to the current date.
            4. Updates the case status to 'Contabilizar Factura'.
            5. Updates the case status to 'Generar poliza'.
            6. Updates the case status to 'Enviar factura electronica'.
            7. Updates the case status to 'Respuesta SRI'.
            8. Updates the case status to 'Enviar poliza electronica'.
            9. Updates the case status to 'Firma poliza electronica por parte del cliente'.
            10. Finalizes the policy and invoice process for the client.
        Note:
            - The `update_case` method is used to update the case status at each stage.
            - The `Bill` objects are created for each month starting from the last timestamp.
            - The `finalizar_poliza_factura_cliente` method is called at the end to complete the process.
        """

        self.update_case(case, 'Iniciar facturación')
        self.update_case(case, 'Generar Factura')
        # create a bill for every month from the last timestamp to today
        last_timestamp = case.last_timestamp
        while last_timestamp < timezone.now():
            Bill.objects.create(case=Case.objects.get(id=case.case_id), value=case.value, timestamp=last_timestamp)
            last_timestamp += timedelta(days=30)
        self.update_case(case, 'Contabilizar Factura')
        self.update_case(case, 'Generar poliza')
        self.update_case(case, 'Enviar factura electronica')
        self.update_case(case, 'Respuesta SRI')
        self.update_case(case, 'Enviar poliza electronica')
        self.update_case(case, 'Firma poliza electronica por parte del cliente')
        self.finalizar_poliza_factura_cliente(case)

    def finalizar_poliza_factura_cliente(self, case: Case):
        """
        Handles the process of finalizing the policy and invoice delivery to the client for a given case.
        This method updates the case status based on a random probability distribution:
        - 80% chance: Marks the case as completed, updates the status to "Finalizar proceso de emision" 
          and "Recepcion pago", and sets the case as approved.
        - 10% chance: Returns the case to the emission process for correction, calculates the rework cost, 
          logs the cause of rework, and recursively retries the process.
        - 10% chance: Returns the case to the commercial team for correction, calculates the rework cost, 
          logs the cause of rework, and recursively retries the process.
        Args:
            case (Case): The case object representing the policy and invoice process.
        Raises:
            Any exceptions raised by the database queries or object operations.
        Notes:
            - The method uses random probabilities to determine the flow of the process.
            - Rework costs are calculated based on the time difference between the current activity 
              and the initial "Finalizar envio poliza y factura al cliente" activity.
            - Causes for rework are randomly selected from a predefined list of reasons.
            - Recursive calls are made for cases requiring rework, which could potentially lead to 
              infinite recursion if not handled properly.
        """

        self.update_case(case, 'Finalizar envio poliza y factura al cliente')

        rand_num = random.randint(1, 100)

        if rand_num <= 80:
            self.update_case(case, 'Finalizar proceso de emision')
            self.update_case(case, 'Recepcion pago')
            case2 = Case.objects.get(id=case.case_id)
            case2.approved = True
            case2.save()

        
        elif rand_num <= 90:
            self.update_case(case, 'Devolucion a emision (corregir informacion)')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name='Finalizar envio poliza y factura al cliente').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Finalizar envio poliza y factura al cliente', cause=cause)

            self.finalizar_poliza_factura_cliente(case)
        else:
            self.update_case(case, 'Devolucion a comercial (corregir informacion)')
            activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id)).last()
            return_activity = Activity.objects.filter(case=Case.objects.get(id=case.case_id), name='Finalizar envio poliza y factura al cliente').first()
            if return_activity:
                cost = (activity.timestamp - return_activity.timestamp).total_seconds()
            else:
                cost = 0
            cause = random.choice(['Falta de información', 'Información incorrecta', 'Información incompleta', 'Información duplicada', 'Documentos incorrectos', 'Documentos incompletos', 'Documentos duplicados'])
            Rework.objects.create(activity=activity, cost = cost, target = 'Finalizar envio poliza y factura al cliente', cause=cause)

            self.finalizar_poliza_factura_cliente(case)



    def create_variants(self, *args, **kwargs):
        """
        Creates and stores variants of activity sequences for cases, along with their statistics.
        This method processes activities to group them into variants based on the sequence of 
        activity names for each case. It calculates the number of cases for each variant, the 
        percentage of cases that belong to each variant, and the average time duration for each 
        variant. The results are stored in the `Variant` model.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Workflow:
            1. Retrieve all activities and group them by their associated case IDs.
            2. Track the sequence of activity names for each case and store timestamps for 
               calculating durations.
            3. Group cases into variants based on their activity sequences.
            4. Calculate statistics for each variant:
                - Number of cases in the variant.
                - Percentage of total cases represented by the variant.
                - Average time duration for the variant.
            5. Store the variant data in the `Variant` model.
        Models:
            - `Activity`: Represents individual activities with attributes such as `case` and `timestamp`.
            - `Case`: Represents a case associated with activities.
            - `Variant`: Stores the variant details including activity sequences, associated cases, 
              number of cases, percentage, and average time.
        Raises:
            Any exceptions raised by the ORM methods `get_or_create` or `create` will propagate.
        Note:
            - The method assumes that the `Activity` model has `case`, `timestamp`, and `name` attributes.
            - The `Variant` model must have fields `activities`, `cases`, `number_cases`, `percentage`, 
              and `avg_time`.
        """

        # List of cases to keep track of existing cases and identify case_index
        cases = []
        variants = defaultdict(list)
        timesPerCase = defaultdict(list)
        activities = Activity.objects.all()
    
        for activity in activities:
            case_id = activity.case.id
    
            if case_id not in cases:
                cases.append(case_id)
            case_index = cases.index(case_id)
            timestamp = activity.timestamp
    
            name = activity.name
    
            # Store the timestamp for calculating mean time
            timesPerCase[case_id].append(timestamp)
    
            # Get or create the case
            case, created = Case.objects.get_or_create(id=case_id)
    
            # Append activity name to the variants dictionary
            variants[case_id].append(name)
    
        # Grouping keys by their value lists
        grouped_data = defaultdict(list)
        for key, value in variants.items():
            grouped_data[tuple(value)].append(key)
    
        # Convert defaultdict to a regular dictionary and print the result
        grouped_data = dict(grouped_data)
    
        for key, value in grouped_data.items():
            number_cases = len(value)
            percentage = (number_cases / len(cases)) * 100
    
            # Calculate mean time for the variant
            total_duration = 0
            for case_id in value:
                times = timesPerCase[case_id]
                times.sort()
                duration = (times[-1] - times[0]).total_seconds()
                total_duration += duration
            mean_time = total_duration / number_cases
    
            Variant.objects.create(
                activities=str(key),
                cases=str(value),
                number_cases=number_cases,
                percentage=percentage,
                avg_time=mean_time
            )

    def add_TPT(self):
        """
        Calculates and updates the Time Processing Time (TPT) for each activity in the database.
        This method iterates through all distinct case indices in the `Activity` model, retrieves
        the activities associated with each case index, and calculates the time difference (in seconds)
        between consecutive activities based on their timestamps. The calculated time difference is
        then stored in the `tpt` field of the current activity.
        Steps:
        1. Retrieve a list of distinct `case_index` values from the `Activity` model.
        2. For each `case_index`, fetch and order the associated activities by their `timestamp`.
        3. Iterate through the activities and calculate the time difference between consecutive
           activities.
        4. Update the `tpt` field of the current activity with the calculated time difference.
        Note:
        - The `tpt` field is updated only for activities that have a subsequent activity in the
          ordered list.
        Raises:
            AttributeError: If the `Activity` model does not have the required fields (`case_index`,
                            `timestamp`, `tpt`).
            ValueError: If the `timestamp` field contains invalid or non-datetime values.
        """
        index_list = Activity.objects.values_list('case_index', flat=True).distinct()
        for index in index_list:
            activities = Activity.objects.filter(case_index=index).order_by('timestamp')

            for i in range(len(activities) - 1):
                current_activity = activities[i]
                current_id = current_activity.id
                next_activity = activities[i + 1]

                time_diff = (next_activity.timestamp - current_activity.timestamp).total_seconds()
                Activity.objects.filter(id=current_id).update(tpt=time_diff)
   

    def get_case_activity_time(self):
        """
        Retrieves and organizes activity data grouped by case ID.
        This method fetches all activities from the database, groups them by their associated case ID,
        and returns a dictionary where each key is a case ID and the value is a list of dictionaries
        containing activity details such as the activity name and its timestamp.
        Returns:
            defaultdict: A dictionary where keys are case IDs and values are lists of dictionaries
            with activity details. Each dictionary in the list contains:
                - "ACTIVIDAD": The name of the activity.
                - "TIMESTAMP": The timestamp of the activity.
        """


        timesPerActivity = defaultdict(list)
        activities = Activity.objects.all()
        for activity in activities:
            timesPerActivity[activity.case.id].append({"ACTIVIDAD": activity.name, "TIMESTAMP": activity.timestamp})
        return timesPerActivity

    def get_mean_time_per_activity(self, timesPerActivity):
        """
        Calculate the mean time spent on each activity based on the provided activity timestamps.
        Args:
            timesPerActivity (dict): A dictionary where the keys are case IDs and the values are lists of 
                                     dictionaries representing activities. Each activity dictionary must 
                                     contain the keys "TIMESTAMP" (a datetime object) and "ACTIVIDAD" 
                                     (the name of the activity).
        Returns:
            str: A JSON-formatted string representing the mean time (in seconds) spent on each activity.
                 The JSON object has activity names as keys and their corresponding mean durations as values.
        Example:
            Input:
                timesPerActivity = {
                    "case1": [
                        {"TIMESTAMP": datetime(2023, 1, 1, 10, 0), "ACTIVIDAD": "A"},
                        {"TIMESTAMP": datetime(2023, 1, 1, 10, 30), "ACTIVIDAD": "B"}
                    ],
                    "case2": [
                        {"TIMESTAMP": datetime(2023, 1, 1, 11, 0), "ACTIVIDAD": "A"},
                        {"TIMESTAMP": datetime(2023, 1, 1, 11, 45), "ACTIVIDAD": "B"}
                    ]
                }
            Output:
                {
                    "A": 1800.0,
                    "B": 2700.0
                }
        """
        activity_durations = defaultdict(list)
        for case_id, activities in timesPerActivity.items():
            for i in range(len(activities) - 1):
                current_activity = activities[i]
                next_activity = activities[i + 1]
                current_timestamp = current_activity["TIMESTAMP"]
                next_timestamp = next_activity["TIMESTAMP"]
                duration = abs(next_timestamp - current_timestamp)
                activity_durations[current_activity["ACTIVIDAD"]].append(duration.total_seconds())

        mean_time_per_activity = {}
        for activity, durations in activity_durations.items():
            mean_time_per_activity[activity] = sum(durations) / len(durations)

        mean_time_per_activity_json = json.dumps(mean_time_per_activity, indent=4)
        print(mean_time_per_activity_json)
        return mean_time_per_activity_json
    
    def add_time_to_cases(self):
        """
        Calculates and assigns the average time (in seconds) between the first and last activities
        for each case in the database.

        This method iterates through all cases, retrieves their associated activities ordered
        by timestamp, and computes the time difference between the first and last activities.
        The computed average time is then saved to the `avg_time` field of each case.

        Note:
            - Assumes that the `Case` model has an `avg_time` field to store the calculated value.
            - Assumes that the `Activity` model has a `timestamp` field and a foreign key to `Case`.

        Raises:
            AttributeError: If any case has no associated activities, as `first()` or `last()` 
                            would return `None` and accessing `timestamp` would fail.
        """
        cases = Case.objects.all()
        for case in cases:
            activities = Activity.objects.filter(case=case).order_by('timestamp')
            last_activity = activities.last()
            first_activity = activities.first()
            case.avg_time = (last_activity.timestamp - first_activity.timestamp).total_seconds()
            case.save()


    def handle(self, *args, **kwargs):
        """
        Handle the command to add data to the database from the CSV file.
        """

        for i in range(1000):
            self.start()
            if i % 100 == 0:
                self.stdout.write(self.style.SUCCESS(str(i) + 'instances added successfully'))
        self.stdout.write(self.style.SUCCESS('Adding time to cases'))
        self.add_time_to_cases()
        self.stdout.write(self.style.SUCCESS('Creating variants'))
        self.create_variants()
        self.stdout.write(self.style.SUCCESS('Adding TPT'))
        self.add_TPT()
        self.stdout.write(self.style.SUCCESS('Data added successfully'))

        self.get_mean_time_per_activity(self.get_case_activity_time())
