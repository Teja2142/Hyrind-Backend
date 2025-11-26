from django.shortcuts import render
from django.views import View


class HomeView(View):
    """Homepage view"""
    def get(self, request):
        return render(request, 'home.html')
