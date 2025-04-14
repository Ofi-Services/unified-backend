from django.urls import path
"""
URL configuration for the API.
This module defines the URL patterns for the API endpoints and maps them to the corresponding views.
Endpoints:
- cases/ : List and create cases.
- activities/ : List and create activities.
- activities/<int:id>/ : Retrieve, update, and destroy a specific activity by ID.
- activity-list/ : List all activities.
- meta-data/ : Retrieve distinct activity data.
- variants/ : List all variants.
- KPI/ : List all KPIs.
- bills/ : List all bills.
- reworks/ : List all reworks.
"""
from . import views

urlpatterns = [
    path("activity/", views.ActivityList.as_view(), name="activity-list"),
    path('metadata/', views.DistinctActivityData.as_view(), name='distinct-activity-data'),
    path('variant/', views.VariantList.as_view(), name='variant-list'),
    path('kpi/', views.KPIList.as_view(), name='KPI-list'),
    path('invoice/', views.InvoiceList.as_view(), name='invoice-list'),
    path('group/', views.GroupList.as_view(), name='group-list'),
    path('case/', views.CaseList.as_view(), name='case-list'),
    path('inventory/', views.InventoryList.as_view(), name='inventory'),
]