from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def register(request):
    return render(request, "register.html")

def registration(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        new_user = User.objects.create(
            username=username,
            email=email,
        )
        new_user.set_password(password)
        new_user.save()

        messages.success(request, "Cadastro realizado com sucesso! Agora você pode fazer login.")
        return redirect('loginpage')

    return render(request, 'register.html')

def loginpage(request):
    return render(request, "login.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        elif request.user.is_authenticated:
            return redirect("loginpage")
        else:
            messages.success(request, "error credentials")
            return render(request, 'index.html')
    else:
        return render(request, 'login.html')
    
def index(request):
 chamados = Chamados.objects.order_by('-created_at')[:5]
 return render(request,'index.html', {'chamados': chamados})


def chamado_by_id(request, chamado_id):
 chamado = get_object_or_404(Chamados, pk=chamado_id)
 return render(request, 'detalhe_chamado.html', {'chamado':chamado})

@login_required(login_url='loginpage')
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("loginpage")

@login_required(login_url='loginpage')
def chamado(request):
    return render(request, "abrir_chamado.html")

@login_required(login_url='loginpage')
def abrir_chamado(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        setor = request.POST.get('setor')
        user = request.user
   
        new_query = Chamados.objects.create(
            titulo=titulo,
            descricao=descricao,
            setor=setor,
            user=user
        )
        new_query.save()

        return redirect("/")
    else:
        return render(request, 'abrir_chamado.html')