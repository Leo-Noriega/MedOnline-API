from django.shortcuts import render

def about_us(request):
    return render(request, "aboutUs.html", status=200)

def index(request):
   return render(request,'landingPage.html', status=200)

def notFound(request, exception):
   return render(request,'error404.html', status=404)

def errorServer(request, exception):
   return render(request,'error500.html', status=500)