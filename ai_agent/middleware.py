class CorsMiddleware:
    """
    Middleware to add Access-Control-Allow-Origin and Access-Control-Allow-Headers headers to responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response