from django.urls import path
"""
URL configuration for the ai_agent app.
This module defines the URL patterns for the ai_agent app, mapping URL paths to their corresponding views.
Routes:
- "alerts/": Maps to the Alerts view, accessible via the name "alerts".
- "ai_assistant/": Maps to the AiAssistant view, accessible via the name "ai-assistant".
Imports:
- path: A function from django.urls used to define URL patterns.
- views: The module containing the view classes for the ai_agent app.
"""
from . import views


urlpatterns = [
    path("alerts/", views.Alerts.as_view(), name="alerts"),
    path("ai_assistant/", views.AiAssistant.as_view(), name="ai-assistant"),
]