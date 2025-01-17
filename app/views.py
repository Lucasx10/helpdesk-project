from django.shortcuts import redirect, render, get_object_or_404
from .models import User, Profile, Chamados, Comentarios
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ComentarioForm
from django.contrib.messages import constants
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def loginpage(request):
    if request.user.is_authenticated:  # Verifica se o usuário já está autenticado
        return redirect('index')
    return render(request, "login.html")

# Create your views here.
def register(request):
    return render(request, "register.html")

def registration(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuarios com esse username')
            return redirect('register')

        if password != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'A senha e confirmar senha devem ser iguais')
            return redirect('register')

        if len(password) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve possuir pelo menos 6 caracteres')
            return redirect('register')

        # Criação do usuário
        user = User.objects.create_user(username=username, email=email, password=password)

        # Criação do perfil e associação com o usuário
        profile = Profile.objects.create(
            user=user,
            nome=nome
        )
        # Salvar o perfil
        profile.save()

        messages.success(request, "Cadastro realizado com sucesso! Agora você pode fazer login.")
        return redirect('loginpage')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember')  # Captura o valor do checkbox "Lembrar-me"
        
        try:
            user = authenticate(request, username=User.objects.get(email=username), password=password)
        except:
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configura a duração da sessão se "Lembrar-me" estiver ativado
            if remember_me:
                request.session.set_expiry(5 * 24 * 60 * 60)  # 5 dias em segundos
            else:
                request.session.set_expiry(0)  # Sessão termina ao fechar o navegador
            if request.user.is_superuser:
                return redirect('admin')
            else:
                return redirect('index')
        else:
            messages.error(request, "Email ou senha inválidos.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

@login_required(login_url='loginpage')
def index(request):
    # Verifica se o perfil do usuário existe antes de acessar
    if not hasattr(request.user, 'profile'):
        messages.error(request, "Usuário não possui perfil associado.")
        return redirect('loginpage')  # Ou outra página de erro ou redirecionamento
    
    # Agora você pode acessar o perfil sem problemas
    if request.user.profile.equipe_ti:
        # Se o usuário for da equipe TI, mostra todos os chamados
        chamados_list = Chamados.objects.order_by('created_at')
    else:
        # Se o usuário for comum, mostra apenas os chamados que ele abriu
        chamados_list = Chamados.objects.filter(user=request.user).order_by('created_at')
    
    # Paginação - definindo o número de chamados por página
    paginator = Paginator(chamados_list, 10)  # 10 chamados por página
    
    # Pegando o número da página a partir da URL (parâmetro ?page=1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Retorna somente o conteúdo da lista de chamados para atualização
        return JsonResponse({
            'html': render_to_string('index.html', {'page_obj': page_obj})
        })

    return render(request, 'index.html', {'page_obj': page_obj})


@login_required(login_url='loginpage')
def chamado_by_id(request, chamado_id):
    chamado = get_object_or_404(Chamados, pk=chamado_id)
    equipe_ti = Profile.objects.filter(equipe_ti=True)  # Filtra apenas membros da equipe TI
    # Adicionar comentário
    if request.method == 'POST':
        comentario_form = ComentarioForm(request.POST)
        if comentario_form.is_valid():
            comentario = comentario_form.save(commit=False)
            comentario.chamado = chamado
            comentario.usuario = request.user
            comentario.save()
            
            # Notifique o grupo "chamados"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'chamados',
                {
                    'type': 'send_update',
                    'message': f'Novo comentário no chamado: N°{chamado.id}',
                }
            )
            return redirect('chamado_by_id', chamado_id=chamado.id)
    else:
        comentario_form = ComentarioForm()

    return render(request, 'detalhe_chamado.html', {
        'chamado': chamado,
        'equipe_ti': equipe_ti,
        'comentario_form': comentario_form,
    })

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
        tipo_equipamento = request.POST.get('tipo_equipamento')
        user = request.user
   
        new_query = Chamados.objects.create(
            titulo=titulo,
            descricao=descricao,
            setor=setor,
            user=user,
            tipo_equipamento=tipo_equipamento
        )
        new_query.save()
        
        # Notifique o grupo "chamados"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chamados',
            {
                'type': 'send_update',
                'message': f'Novo chamado foi criado: {titulo}/{setor}',
            }
        )
        messages.success(request, "Chamado Aberto com sucesso!")
        return redirect("abrir_chamado")
    else:
        return render(request, 'abrir_chamado.html')

    
@login_required(login_url='loginpage')
def editar_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamados, id=chamado_id)

    # Verificar se o usuário tem permissão para atender ou finalizar o chamado
    if request.user.profile.equipe_ti:
        if request.method == 'POST':
            # Modifica o status do chamado com base no valor enviado
            novo_status = request.POST.get('status')
            ti_chamado = request.user
            if novo_status:
                chamado.status = novo_status
                chamado.responsavel_ti = ti_chamado
                chamado.save()
                
                        # Notifique o grupo "chamados"
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'chamados',
                    {
                        'type': 'send_update',
                        'message': 'Status alterado',
                    }
                )
                
                # Adiciona mensagens para feedback ao usuário
                messages.success(request, "Chamado atualizado com sucesso.")
                return redirect('chamado_by_id', chamado_id=chamado.id)

    # Se o método não for POST, apenas renderize o template com o chamado
    return render(request, 'detalhe_chamado.html', {'chamado': chamado})


@login_required
def transferir_chamado(request, chamado_id):
    if request.method == "POST":
        chamado = get_object_or_404(Chamados, pk=chamado_id)
        novo_responsavel_id = request.POST.get('responsavel_ti')
        
        try:
            novo_responsavel = User.objects.get(pk=novo_responsavel_id)
            chamado.responsavel_ti = novo_responsavel
            chamado.save()
            
            messages.success(request, "Chamado transferido com sucesso!")
        except User.DoesNotExist:
            messages.error(request, "O responsável selecionado não existe.")
        
        return redirect('chamado_by_id', chamado_id=chamado.id)
    else:
        messages.error(request, "Método inválido.")
        return redirect('index')

@login_required(login_url='loginpage')
def confirmar_finalizacao(request, chamado_id):
    chamado = get_object_or_404(Chamados, id=chamado_id)

    if chamado.user != request.user:
        # O usuário que está tentando confirmar não é o dono do chamado
        return redirect('chamado_by_id', chamado_id=chamado.id)
    
    if request.method == 'POST':
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                    'chamados',
                    {
                        'type': 'send_update',
                        'message': 'Status alterado',
                    }
        )
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

def custom_handler404(request, exception=None):
    return render(request, 'error-404.html')

