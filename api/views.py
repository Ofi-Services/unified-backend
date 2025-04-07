from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Case, Activity, Variant, Bill, Rework
from .serializers import CaseSerializer, ActivitySerializer, VariantSerializer, BillSerializer, ReworkSerializer
from rest_framework.pagination import PageNumberPagination
from datetime import datetime


class CaseListCreate(generics.ListCreateAPIView):
    """
    API view to retrieve list of cases or create new.
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Optionally restricts the returned cases to a given page size,
        by filtering against a `page_size` query parameter in the URL.
        """
        queryset = super().get_queryset()
        page_size = self.request.query_params.get('page_size')
        if page_size:
            self.pagination_class.page_size = int(page_size)
        return queryset

# View for listing and creating Activity objects
class activityListCreate(generics.ListCreateAPIView):
    """
    API view to retrieve list of activities or create new.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


# Custom view for listing Activity objects with optional filtering and pagination
class ActivityList(APIView):
    """
    ActivityList APIView
    This API view is designed to retrieve a list of activities with optional filtering 
    based on various query parameters. It supports pagination and allows filtering 
    by case IDs, names, and other attributes.
    Methods:
        get(request):
            Handles GET requests to retrieve a filtered and paginated list of activities.
            Query Parameters:
                - case (list[str]): List of case IDs to filter activities.
                - name (list[str]): List of names to filter activities.
                - case_index (str): Case index to filter activities.
                - page_size (int): Number of activities per page (default: 100000).
                - type (str): Case type to filter activities.
                - branch (str): Case branch to filter activities.
                - ramo (str): Case ramo to filter activities.
                - brocker (str): Case brocker to filter activities.
                - state (str): Case state to filter activities.
                - client (str): Case client to filter activities.
                - creator (str): Case creator to filter activities.
                - var (list[str]): List of variant IDs to filter activities.
                - start_date (str): Start date (YYYY-MM-DD) to filter activities.
                - end_date (str): End date (YYYY-MM-DD) to filter activities.
                Response: A paginated response containing the filtered list of activities 
                or an error message in case of failure.
            Raises:
                - 400 Bad Request: If the date format is invalid.
                - 500 Internal Server Error: If an unexpected error occurs.
    
    API view to retrieve list of activities with optional filtering by case IDs and names.
    Supports pagination.
    """
    def get(self, request):
        """
        Handle GET request to list activities with optional filtering and pagination.
    
        Args:
            request: The HTTP request object.

        Returns:
            Response: The paginated list of activities.
        """
        try:
            case_ids = request.query_params.getlist('case')
            names = request.query_params.getlist('name')
            case_index = request.query_params.get('case_index')
            page_size = request.query_params.get('page_size', 100000)
            type = request.query_params.get('type')
            branch = request.query_params.get('branch')
            ramo = request.query_params.get('ramo')
            brocker = request.query_params.get('brocker')
            state = request.query_params.get('state')
            client = request.query_params.get('client')
            creator = request.query_params.get('creator')
            variant_ids = request.query_params.getlist('var')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Validate date format
            try:
                if start_date:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                if end_date:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
            
            activities = Activity.objects.all()
            if case_index:
                activities = activities.filter(case_index=case_index)
            if case_ids:
                activities = activities.filter(case__id__in=case_ids)
            if names:
                activities = activities.filter(name__in=names)
            if type:
                activities = activities.filter(case__type=type)
            if branch:
                activities = activities.filter(case__branch=branch)
            if ramo:
                activities = activities.filter(case__ramo=ramo)
            if brocker:
                activities = activities.filter(case__brocker=brocker)
            if state:
                activities = activities.filter(case__state=state)
            if client:
                activities = activities.filter(case__client=client)
            if creator:
                activities = activities.filter(case__creator=creator)
            if variant_ids:
                variants = Variant.objects.filter(id__in=variant_ids)

                if variants:
                    case_ids = set()
                    for variant in variants:
                        case_ids.update({case_id.strip().replace("'", "") for case_id in variant.cases[1:-1].split(',')})
                        
                    activities = activities.filter(case__id__in=case_ids)
            if start_date:
                activities = activities.filter(timestamp__gte=start_date)
            if end_date:
                activities = activities.filter(timestamp__lte=end_date)

            activities = activities.order_by('timestamp')

            paginator = PageNumberPagination()
            paginator.page_size = page_size
            paginated_activities = paginator.paginate_queryset(activities, request)
            serializer = ActivitySerializer(paginated_activities, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# View for listing all distinct activity names and case IDs
class DistinctActivityData(APIView):
    """
    API view to retrieve a list of all distinct activity names and case IDs.
    """
    def get(self, request, format=None):
        """
        Handle GET request to list all distinct activity names and case IDs.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The list of distinct activity names and case IDs.
        """
        try:
            distinct_names = list(Activity.objects.values_list('name', flat=True).distinct())
            distinct_cases = list(Activity.objects.values_list('case', flat=True).distinct())
            distinct_types = list(Case.objects.values_list('type', flat=True).distinct())
            distinct_branches = list(Case.objects.values_list('branch', flat=True).distinct())
            distinct_ramos = list(Case.objects.values_list('ramo', flat=True).distinct())
            distinct_brockers = list(Case.objects.values_list('brocker', flat=True).distinct())
            distinct_clients = list(Case.objects.values_list('client', flat=True).distinct())
            distinct_creators = list(Case.objects.values_list('creator', flat=True).distinct())

            attributes = [
                {'name': 'case', 'type': 'number', 'distincts': distinct_cases},
                {'name': 'timestamp', 'type': 'date', 'distincts': []},  # Assuming no distinct values for timestamp
                {'name': 'name', 'type': 'str', 'distincts': distinct_names},
                {'name': 'tpt', 'type': 'number', 'distincts': []},  # Assuming no distinct values for tpt
                {'name': 'type', 'type': 'str', 'distincts': distinct_types},
                {'name': 'branch', 'type': 'str', 'distincts': distinct_branches},
                {'name': 'ramo', 'type': 'str', 'distincts': distinct_ramos},
                {'name': 'brocker', 'type': 'str', 'distincts': distinct_brockers},
                {'name': 'state', 'type': 'str', 'distincts': []},  # Assuming no distinct values for state
                {'name': 'client', 'type': 'str', 'distincts': distinct_clients},
                {'name': 'creator', 'type': 'str', 'distincts': distinct_creators},
                {'name': 'value', 'type': 'number', 'distincts': []}  # Assuming no distinct values for
            ]

            return Response({
                'attributes': attributes
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

class VariantList(APIView):
    """
    VariantList API View
    This API view is designed to retrieve a list of all distinct activity names and case IDs. 
    It supports filtering by activity names and provides paginated results.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve and paginate the list of variants.
    Attributes:
        - activities_param: A list of activity names to filter the variants.
        - page_size: The number of items per page for pagination (default is 100,000).
        - variants: A queryset of Variant objects, optionally filtered by activities.
        - paginator: An instance of PageNumberPagination for handling pagination.
        - serializer: A serializer to convert the paginated queryset into JSON format.
    Query Parameters:
        - activities: A list of activity names to filter the variants (optional).
        - page_size: The number of items per page for pagination (optional, default is 100,000).
        - A paginated response containing the serialized list of variants, ordered by percentage in descending order.

    API view to retrieve a list of all distinct activity names and case IDs.
    """

    def get(self, request, format=None):
        """
        Handle GET request to list all distinct activity names and case IDs.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of variants.
        """
        activities_param = request.query_params.getlist('activities')
        page_size = request.query_params.get('page_size', 100000)  # Default page size is 10 if not provided
        variants = Variant.objects.all()
        if activities_param:
            for param in activities_param:
                variants = variants.filter(activities__icontains=param)
                
        variants = variants.order_by('-percentage')
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_variants = paginator.paginate_queryset(variants, request)
        serializer = VariantSerializer(paginated_variants, many=True)
        return paginator.get_paginated_response(serializer.data)

class BillList(APIView):
    """
    BillList APIView
    This view handles GET requests to list all Bill objects with optional filtering 
    by start and end dates. It supports pagination and validates the date format 
    for filtering.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve a paginated list of Bill objects. 
            Allows filtering by `start_date` and `end_date` query parameters in 
            the format 'YYYY-MM-DD'. Returns a paginated response with serialized 
            Bill data.
    Query Parameters:
        - page_size (int, optional): Number of items per page. Defaults to 100000.
        - start_date (str, optional): Filter bills with a timestamp greater than 
          or equal to this date (format: 'YYYY-MM-DD').
        - end_date (str, optional): Filter bills with a timestamp less than or 
          equal to this date (format: 'YYYY-MM-DD').
    Responses:
        - 200 OK: Returns a paginated list of serialized Bill objects.
        - 400 Bad Request: Returned if the date format is invalid.
        - 500 Internal Server Error: Returned if an unexpected error occurs.
    """

    def get(self, request, format=None):
        """
        Query Parameters:
            - page_size (int, optional): Number of bills per page. Defaults to 100000.
            - start_date (str, optional): Filter bills with a timestamp greater than or equal to this date (format: YYYY-MM-DD).
            - end_date (str, optional): Filter bills with a timestamp less than or equal to this date (format: YYYY-MM-DD).
        Returns:
            - 200 OK: A paginated list of bills serialized as JSON.
            - 400 Bad Request: If the date format is invalid.
            - 500 Internal Server Error: If an unexpected error occurs.
        
        Handle GET request to list all Bills with optional filtering by start and end dates.
        """
        try:
            page_size = request.query_params.get('page_size', 100000)
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Validate date format
            try:
                if start_date:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                if end_date:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

            bills = Bill.objects.all()
            if start_date:
                bills = bills.filter(timestamp__gte=start_date)
            if end_date:
                bills = bills.filter(timestamp__lte=end_date)

            paginator = PageNumberPagination()
            paginator.page_size = page_size
            paginated_bills = paginator.paginate_queryset(bills, request)
            serializer = BillSerializer(paginated_bills, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

class ReworkList(APIView):
    """
    ReworkList APIView handles GET requests to retrieve a paginated list of Rework objects 
    with optional filtering by start and end dates.
    Methods:
        get(request, format=None):
            Retrieves a list of Rework objects. Supports filtering by start_date and end_date 
            query parameters in the format 'YYYY-MM-DD'. Results are paginated based on the 
            page_size query parameter (default is 100,000).
    Query Parameters:
        - page_size (int, optional): Number of items per page. Default is 100,000.
        - start_date (str, optional): Filter results to include only those with activity 
          timestamps on or after this date. Format: 'YYYY-MM-DD'.
        - end_date (str, optional): Filter results to include only those with activity 
          timestamps on or before this date. Format: 'YYYY-MM-DD'.
    Responses:
        - 200 OK: Returns a paginated list of serialized Rework objects.
        - 400 Bad Request: Returned if the date format is invalid.
        - 500 Internal Server Error: Returned if an unexpected error occurs.
    Raises:
        - ValueError: If the provided start_date or end_date is not in the correct format.
        - Exception: For any other unexpected errors.

    """
    def get(self, request, format=None):
        """
        Handle GET request to list all Reworks with optional filtering by start and end dates.
        """
        try:
            page_size = request.query_params.get('page_size', 100000)
            startdate = request.query_params.get('start_date')
            enddate = request.query_params.get('end_date')

            # Validate date format
            try:
                if startdate:
                    startdate = datetime.strptime(startdate, "%Y-%m-%d")
                if enddate:
                    enddate = datetime.strptime(enddate, "%Y-%m-%d")
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

            reworks = Rework.objects.all()
            if startdate:
                reworks = reworks.filter(activity__timestamp__gte=startdate)
            if enddate:
                reworks = reworks.filter(activity__timestamp__lte=enddate)

            paginator = PageNumberPagination()
            paginator.page_size = page_size
            paginated_reworks = paginator.paginate_queryset(reworks, request)
            serializer = ReworkSerializer(paginated_reworks, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
class KPIList(APIView):
    """
    API view to retrieve various Key Performance Indicators (KPIs) based on the provided date range.
    Methods:
        get(request, format=None):
            Handles GET requests to calculate and return KPIs.
    KPIs:
        - case_quantity: Total number of distinct cases.
        - variant_quantity: Total number of variants.
        - bill_quantity: Total number of bills.
        - rework_quantity: Total number of reworks.
        - approved_cases: Total number of approved cases.
        - cancelled_by_company: Total number of cases cancelled by the company.
        - cancelled_by_broker: Total number of cases cancelled by the broker.
    Query Parameters:
        - start_date (str, optional): Start date for filtering data in the format 'YYYY-MM-DD'.
        - end_date (str, optional): End date for filtering data in the format 'YYYY-MM-DD'.
    Responses:
        - 200 OK: Returns a dictionary containing the calculated KPIs.
        - 400 Bad Request: Returned if the date format is invalid.
        - 500 Internal Server Error: Returned if an unexpected error occurs.
    Example Response:
            "case_quantity": 100,
            "variant_quantity": 50,
            "bill_quantity": 200,
            "rework_quantity": 10,
            "approved_cases": 80,
            "cancelled_by_company": 10,
            "cancelled_by_broker": 10
    """
    def get(self, request, format=None):
        try:
            startdate = request.query_params.get('start_date')
            enddate = request.query_params.get('end_date')

            # Validate date format
            try:
                if startdate:
                    startdate = datetime.strptime(startdate, "%Y-%m-%d")
                if enddate:
                    enddate = datetime.strptime(enddate, "%Y-%m-%d")
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

            variants = Variant.objects.all()
            bills = Bill.objects.all()
            reworks = Rework.objects.all()
            activities = Activity.objects.all()

            if startdate:
                bills = bills.filter(timestamp__gte=startdate)
                reworks = reworks.filter(activity__timestamp__gte=startdate)
                activities = activities.filter(timestamp__gte=startdate)
            if enddate:
                bills = bills.filter(timestamp__lte=enddate)
                reworks = reworks.filter(activity__timestamp__lte=enddate)
                activities = activities.filter(timestamp__lte=enddate)

            case_quantity = activities.values("case").distinct().count()
            variant_quantity = variants.count()
            bill_quantity = bills.count()
            rework_quantity = reworks.count()
            approved_cases = Case.objects.filter(id__in=activities.values("case").distinct(), approved=True).count()
            cancelled_by_company = activities.filter(case__activities__name="Declinar solicitud en suscripcion").values("case").distinct().count()
            cancelled_by_broker = case_quantity - approved_cases - cancelled_by_company

            return Response(
                {
                    "case_quantity": case_quantity,
                    "variant_quantity": variant_quantity,
                    "bill_quantity": bill_quantity,
                    "rework_quantity": rework_quantity,
                    "approved_cases": approved_cases,
                    "cancelled_by_company": cancelled_by_company,
                    "cancelled_by_broker": cancelled_by_broker
                }
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)