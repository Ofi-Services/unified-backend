from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Case, Activity, Variant, Inventory, OrderItem, Invoice
from .serializers import CaseSerializer, ActivitySerializer, VariantSerializer, InvoiceSerializer, InventorySerializer, OrderItemSerializer
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
from django.db.models import Sum



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
            page_size = request.query_params.get('page_size', 50)
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
           

            attributes = [
                {'name': 'case', 'type': 'number', 'distincts': distinct_cases},
                {'name': 'timestamp', 'type': 'date', 'distincts': []},  # Assuming no distinct values for timestamp
                {'name': 'name', 'type': 'str', 'distincts': distinct_names},
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
        page_size = request.query_params.get('page_size', 50)  # Default page size is 10 if not provided
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

            activities = Activity.objects.all()

            if startdate:
                activities = activities.filter(timestamp__gte=startdate)
            if enddate:
                activities = activities.filter(timestamp__lte=enddate)

            case_quantity = activities.values("case").distinct().count()
            variant_quantity = variants.count()
            return Response(
                {
                    "case_quantity": case_quantity,
                    "variant_quantity": variant_quantity,
                }
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class InvoiceList(APIView):
    """
    API view to retrieve a list of invoices with optional filtering and pagination.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve and paginate the list of invoices.
    Query Parameters:
        - case (list[str]): List of case IDs to filter invoices (optional).
        - page_size (int): Number of invoices per page (default: 100000).
        - A paginated response containing the serialized list of invoices.
    """
    def get(self, request, format=None):
        """
        Handle GET request to list invoices with optional filtering and pagination.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of invoices.
        """
        case_ids = request.query_params.getlist('case')
        page_size = request.query_params.get('page_size', 50)  # Default page size is 10 if not provided
        invoices = Invoice.objects.all()
        if case_ids:
            invoices = invoices.filter(case__id__in=case_ids)
            
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_invoices = paginator.paginate_queryset(invoices, request)
        serializer = InvoiceSerializer(paginated_invoices, many=True)
        return paginator.get_paginated_response(serializer.data)
    


class GroupList(APIView):
    """
    API view to retrieve a paginated list of invoice groups with aggregated data.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve a list of invoice groups with their
            aggregated data, including overpaid amount, item count, date, region,
            pattern, open status, confidence, and serialized invoice items.
    Attributes:
        None
    GET Parameters:
        - page_size (int, optional): The number of groups to display per page. Defaults to 20.
    Aggregated Data for Each Group:
        - group_id (int): The unique identifier of the group.
        - amount_overpaid (float): The total overpaid amount for the group, calculated
          as the sum of invoice values minus the value of the first invoice in the group.
        - itemCount (int): The total number of invoices in the group.
        - date (datetime): The date of the earliest invoice in the group.
        - region (str): The region of the first invoice in the group.
        - pattern (str): The pattern associated with the first invoice in the group.
        - open (bool): The open status of the first invoice in the group.
        - confidence (float): The confidence level of the first invoice in the group.
        - items (list): A serialized list of all invoices in the group.
    Returns:
        Response: A paginated response containing the aggregated group data or an error message
        with a 500 status code in case of an exception.
    Exceptions:
        - Handles any exceptions during processing and returns a 500 status code with an error message.
    """
    def get(self, request, format=None):
        try:
            group_list = Invoice.objects.values_list('group_id', flat=True).distinct()
            group_data = []

            for group_id in group_list:
                group_invoices = Invoice.objects.filter(group_id=group_id)
                group_value = group_invoices.aggregate(Sum('value'))['value__sum']
                first_invoice_value = group_invoices.first().value if group_invoices.exists() else 0
                group_value -= first_invoice_value
                group_invoices_count = group_invoices.count()
                serialized_invoices = InvoiceSerializer(group_invoices, many=True).data

                group_data.append({
                    'group_id': group_id,
                    'amount_overpaid': group_value,
                    'itemCount': group_invoices_count,
                    'date': group_invoices.order_by('date').first().date if group_invoices.exists() else None,
                    'pattern': group_invoices.first().pattern if group_invoices.exists() else None,
                    'open': group_invoices.first().open if group_invoices.exists() else None,
                    'confidence': group_invoices.first().confidence if group_invoices.exists() else None,
                    'items': serialized_invoices,
                })

            paginator = PageNumberPagination()
            page_size = request.query_params.get('page_size', paginator.page_size)
            if not page_size:
                page_size = 50
            paginator.page_size = page_size
            paginated_group_data = paginator.paginate_queryset(group_data, request)
            return paginator.get_paginated_response(paginated_group_data)

        except Exception as e:
            print(f"Error processing request: {e}")
            return Response({"error": str(e)}, status=500)
        
class InventoryList(APIView):
    """
    API view to retrieve a list of inventory items with optional filtering and pagination.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve and paginate the list of inventory items.
    Query Parameters:
        - page_size (int): Number of inventory items per page (default: 100000).
        - A paginated response containing the serialized list of inventory items.
    """
    def get(self, request, format=None):
        """
        Handle GET request to list inventory items with optional filtering and pagination.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of inventory items.
        """
        page_size = request.query_params.get('page_size', 50)  # Default page size is 10 if not provided
        inventories = Inventory.objects.all()
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_inventories = paginator.paginate_queryset(inventories, request)
        serializer = InventorySerializer(paginated_inventories, many=True)
        return paginator.get_paginated_response(serializer.data)

class CaseList(APIView):
    """
    API view to retrieve a list of cases with optional filtering and pagination.
    Methods:
        get(request, format=None):
            Handles GET requests to retrieve and paginate the list of cases.
    Query Parameters:
        - page_size (int): Number of cases per page (default: 100000).
        - A paginated response containing the serialized list of cases.
    """
    def get(self, request, format=None):
        """
        Handle GET request to list cases with optional filtering and pagination.

        Args:
            request: The HTTP request object.
            format: The format of the response.

        Returns:
            Response: The paginated list of cases.
        """
        page_size = request.query_params.get('page_size', 100000)  # Default page size is 10 if not provided
        cases = Case.objects.all()
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_cases = paginator.paginate_queryset(cases, request)
        serializer = CaseSerializer(paginated_cases, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class OrderItemList(APIView):
    """
    API view to list the order items with optional filtering and pagination.
    This view handles GET requests to retrieve a list of order items.
    Methods:
        get(request, format=None):
    GET Method:
    """


    def get(self, request, format=None):
        """
        Handles GET requests to retrieve a list of order items.

        Query Parameters:
            material_code (list of str): List of material codes to filter order items.

        Returns:
            Response: Paginated response with serialized order item data.
        """

        # Filter order items by material code
        order_items = OrderItem.objects.all()

        paginator = PageNumberPagination()
        paginated_order_items = paginator.paginate_queryset(order_items, request)
        serializer = OrderItemSerializer(paginated_order_items, many=True)
        return paginator.get_paginated_response(serializer.data)
    