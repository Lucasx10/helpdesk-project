from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.
def register(request):
    return render(request, "register.html")

def registration(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Criação do usuário
        user = User.objects.create_user(username=username, email=email, password=password)

        # Criação do perfil e associação com o usuário
        profile = Profile.objects.create(
            user=user,
        )

        # Salvar o perfil
        profile.save()

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
            return render(request, 'login.html')
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
    
@login_required(login_url='loginpage')
def editar_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamados, id=chamado_id)

    # Verificar se o usuário tem permissão para atender ou finalizar o chamado
    if request.user.profile.equipe_ti:
        if request.method == 'POST':
            # Modificar o status do chamado com base no valor enviado
            novo_status = request.POST.get('status')
            if novo_status:
                chamado.status = novo_status
                chamado.save()
                return redirect('chamado_by_id', chamado_id=chamado.id)

    # Se o método não for POST, apenas renderize o template com o chamado
    return render(request, 'detalhe_chamado.html', {'chamado': chamado})

@login_required(login_url='loginpage')
def confirmar_finalizacao(request, chamado_id):
    chamado = get_object_or_404(Chamados, id=chamado_id)

    if chamado.user != request.user:
        # O usuário que está tentando confirmar não é o dono do chamado
        return redirect('chamado_by_id', chamado_id=chamado.id)
    
    if request.method == 'POST':
        # O usuário confirmou a finalização
        if 'confirmar' in request.POST:
            chamado.status = 'Concluído'
            chamado.save()
            messages.success(request, "Chamado finalizado com sucesso!")
            return redirect('chamado_by_id', chamado_id=chamado.id)
        # O usuário não confirmou, então o chamado permanece em andamento
        elif 'nao_confirmar' in request.POST:
            chamado.status = "Em andamento"
            chamado.save()
            messages.warning(request, "O problema não foi resolvido. O chamado permanece em andamento.")
            return redirect('chamado_by_id', chamado_id=chamado.id)

    return render(request, 'detalhe_chamado.html', {'chamado': chamado})
