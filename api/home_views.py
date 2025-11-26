from django.shortcuts import render


def home(request):
    """
    Home page view showing API documentation and project information.
    """
    return render(request, 'home.html')
