# proyecto_reservas/middleware.py

from django.shortcuts import redirect

class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host == "tucancha.com.do":
            new_url = f"https://www.tucancha.com.do{request.get_full_path()}"
            return redirect(new_url, permanent=True)
        return self.get_response(request)