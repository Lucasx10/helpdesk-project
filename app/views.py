from django.shortcuts import redirect, render, get_object_or_404
from .models import User, Profile, Chamados, Comentarios, Avaliacao
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ComentarioForm
from django.contrib.messages import constants
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models.functions import ExtractMonth, TruncMonth, TruncDay
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from .models import Chamados, Avaliacao
import json
import calendar
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

@login_required(login_url='loginpage')
def dashboard(request):
    if request.user.profile.equipe_ti:
        ano_atual = datetime.now().year
        mes_selecionado = request.GET.get('mes', '')

        chamados = Chamados.objects.filter(created_at__year=ano_atual)

        if mes_selecionado:
            chamados = chamados.filter(created_at__year=ano_atual, created_at__month=mes_selecionado)

        chamados_concluidos = chamados.filter(status="Concluído")
        chamados_com_5_estrelas = Avaliacao.objects.filter(nota=5, chamado__in=chamados).count()

        # Chamados por setor
        setores_chamados = chamados.values('setor').annotate(total=Count('id')).order_by('-total')[:5]

        # Chamados por tempo (mês ou dia)
        if mes_selecionado:
            chamados_por_tempo = chamados.annotate(dia=TruncDay('created_at')).values('dia').annotate(total=Count('id')).order_by('dia')
            labels_tempo = [item['dia'].strftime('%d') for item in chamados_por_tempo]  # Pegar dias do mês
        else:
            chamados_por_tempo = chamados.filter(created_at__year=ano_atual).annotate(mes=TruncMonth('created_at')).values('mes').annotate(total=Count('id')).order_by('mes')
            labels_tempo = [item['mes'].strftime('%b') for item in chamados_por_tempo]  # Pegar meses do ano

        dados_tempo = [item['total'] for item in chamados_por_tempo]


        # Criar dicionário com todos os meses do ano, mesmo que não haja chamados
        meses_ano = [calendar.month_abbr[i+1] for i in range(12)]  # Meses abreviados, ex: 'Jan', 'Fev'
        
        # Inicializar o dicionário de chamados por mês
        chamados_por_mes_dict = {mes: 0 for mes in meses_ano}
        
        # Preencher o dicionário com os dados dos chamados, substituindo os valores com dados reais
        for chamado in chamados_por_tempo:
            mes = chamado.get('mes')  # Evita KeyError
            if mes:
                mes_nome = mes.strftime('%b')  # Ex: 'Jan', 'Feb', etc.
                chamados_por_mes_dict[mes_nome] = chamado['total']

        # Reorganizar os dados para exibição no gráfico
        dados_mes = [chamados_por_mes_dict[mes] for mes in meses_ano]

        # Quantidade de resmas de papel
        quantidade_resmas = chamados.filter(status="Concluído").aggregate(Sum('quantidade_resma'))['quantidade_resma__sum'] or 0

        # Chamados atendidos por cada técnico dentro do mês
        usuarios_ti = (
            User.objects.filter(profile__equipe_ti=True)
            .annotate(total_chamados=Count('chamados_atendidos', filter=Q(chamados_atendidos__in=chamados)))
            .values("id", "username", "total_chamados")
        )

        # Chamado mais atendido por técnico dentro do mês
        chamados_por_usuario = (
            chamados.filter(status="Concluído")
            .values("responsavel_ti__id", "responsavel_ti__username", "titulo")
            .annotate(total=Count("id"))
            .order_by("responsavel_ti__id", "-total")
        )

        # Criar dicionário com o total de chamados atendidos por cada técnico
        usuarios_chamados = {user["id"]: {
            "username": user["username"],
            "total_chamados": user["total_chamados"],
            "titulo_mais_atendido": None,
            "total_titulo": 0
        } for user in usuarios_ti}

        # Preencher com os títulos mais atendidos
        for chamado in chamados_por_usuario:
            user_id = chamado["responsavel_ti__id"]
            if user_id in usuarios_chamados and usuarios_chamados[user_id]["titulo_mais_atendido"] is None:
                usuarios_chamados[user_id]["titulo_mais_atendido"] = chamado["titulo"]
                usuarios_chamados[user_id]["total_titulo"] = chamado["total"]

        lista_usuarios_chamados = list(usuarios_chamados.values())

        # Criar dicionário de meses para o filtro
        meses_disponiveis = {str(i): calendar.month_name[i] for i in range(1, 13)}
        
        print(labels_tempo, dados_tempo)

        context = {
            "chamados": chamados,
            "chamados_concluidos": chamados_concluidos,
            "chamados_com_5_estrelas": chamados_com_5_estrelas,
            "chamados_solicito_resma_papel": quantidade_resmas,
            'setores_chamados': json.dumps(list(setores_chamados)),
            "usuarios_chamados": lista_usuarios_chamados,
            "meses_disponiveis": meses_disponiveis,
            "mes_selecionado": mes_selecionado,
        }

        # Se um mês foi selecionado, enviamos os DIAS
        if mes_selecionado:
            context["labels_tempo"] = json.dumps(labels_tempo)  # Dias do mês
            context["dados_tempo"] = json.dumps(dados_tempo)    # Dados do mês
        else:
            context["labels_tempo"] = json.dumps(meses_ano)  # Meses do ano
            context["dados_tempo"] = json.dumps(dados_mes)   # Dados anuais

        return render(request, 'dashboard.html', context)
    else:
        return redirect('index')

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

class MyPasswordResetConfirm(PasswordResetConfirmView):
    '''
    Requer password_reset_confirm.html
    '''


class MyPasswordResetComplete(PasswordResetCompleteView):
    '''
    Requer password_reset_complete.html
    '''
    ...

# accounts/views.py
class MyPasswordReset(PasswordResetView):
    '''
    Requer
    registration/password_reset_form.html
    registration/password_reset_email.html
    '''
    ...

class MyPasswordResetDone(PasswordResetDoneView):
    '''
    Requer
    registration/password_reset_done.html
    '''
    ...

@login_required(login_url='loginpage')
def index(request):
    # Verifica se o usuário já visualizou a mensagem
    mensagem_exibida = request.session.get('mensagem_exibida', False)

    if not mensagem_exibida:
        mensagem_ti = "Informamos que, devido a problemas de internet no estado, ficamos sem acesso à internet, agradecemos a compreensão de todos!"
    else:
        mensagem_ti = None  # Não envia a mensagem se já foi exibida

    if request.user.profile.equipe_ti:
        chamados_list = Chamados.objects.exclude(status="Concluído").order_by('created_at')
    else:
        chamados_list = Chamados.objects.filter(user=request.user).exclude(status="Concluído").order_by('created_at')

    paginator = Paginator(chamados_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'mensagem_ti': mensagem_ti,
        'mensagem_exibida': mensagem_exibida,
    })

@login_required(login_url='loginpage')
def chamados_concluidos(request):
    # Acessar os chamados concluidos
    if request.user.profile.equipe_ti:
        chamados = Chamados.objects.filter(status="Concluído").order_by('-updated_at')
    else:
        chamados = Chamados.objects.filter(user=request.user, status="Concluído").order_by('-updated_at')
    paginator = Paginator(chamados, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "chamados_concluidos.html", {"page_obj": page_obj})


@login_required(login_url='loginpage')
def chamado_by_id(request, chamado_id): # detalhe chamados
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
    titulo = None  # Inicialize as variáveis
    setor = None
    
    if request.method == 'POST':
        tipo_chamado = request.POST.get('categoria_chamado')
        print(request.POST)  # Verifica os dados enviados
        
        if tipo_chamado == 'equipamento':
            titulo = request.POST.get('tipo_chamado')
            descricao = request.POST.get('descricao_equipamento')
            setor = request.POST.get('setor_equipamento')
            tipo_equipamento = request.POST.get('tipo_equipamento_equipamento', '')  # Campo opcional

            chamado = Chamados.objects.create(
                user=request.user,
                titulo=titulo,
                descricao=descricao,
                setor=setor,
                tipo_equipamento=tipo_equipamento,
                status='Aberto',  # Definir o status como "Aberto" ao criar
            )
            chamado.save()
        
        elif tipo_chamado == 'sistema' or tipo_chamado == 'internet':
            titulo = request.POST.get('tipo_chamado')
            descricao = request.POST.get('descricao')
            setor = request.POST.get('setor')
            tipo_equipamento = request.POST.get('tipo_equipamento', '')  # Campo opcional

            chamado = Chamados.objects.create(
                user=request.user,
                titulo=titulo,
                descricao=descricao,
                setor=setor,
                tipo_equipamento=tipo_equipamento,
                status='Aberto',  # Definir o status como "Aberto" ao criar
            )
            chamado.save()
            
        elif tipo_chamado == 'outro':
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao_outro')
            setor = request.POST.get('setor_outro')
            tipo_equipamento = request.POST.get('tipo_equipamento_outro', '')  # Campo opcional

            chamado = Chamados.objects.create(
                user=request.user,
                titulo=titulo,
                descricao=descricao,
                setor=setor,
                tipo_equipamento=tipo_equipamento,
                status='Aberto',  # Definir o status como "Aberto" ao criar
            )
            chamado.save()
        
        elif tipo_chamado == 'solicitacao':
            # Para solicitar resma de papel
            titulo = request.POST.get('tipo_chamado')
            if titulo == 'Solicitar Resma de Papel':
                quantidade_resma = request.POST.get('quantidade_resma')
                setor_papel = request.POST.get('setor_papel')

                chamado = Chamados.objects.create(
                    user=request.user,
                    titulo='Solicito Resma de Papel',
                    quantidade_resma=quantidade_resma,
                    setor=setor_papel,
                    status='Aberto',
                )
                chamado.save()
                setor = setor_papel  # Defina o setor para envio
                print("foi")
                
                # Para solicitar tonner                
            elif titulo == 'Solicitar Tonner Impressora':
                tipo_impressora = request.POST.get('tipo_impressora')
                setor_tonner = request.POST.get('setor_tonner')

                chamado = Chamados.objects.create(
                    user=request.user,
                    titulo='Solicito Tonner impressora',
                    tipo_equipamento=tipo_impressora,
                    setor=setor_tonner,
                    status='Aberto',
                )
                chamado.save()
                setor = setor_tonner  # Defina o setor para envio
                print("foi")

        # Verifique se o título e o setor estão definidos antes de enviar a mensagem
        if titulo and setor:
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
                        'message': f'Status do chamado N°{chamado.id} alterado',
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
        return redirect('chamado_by_id', chamado_id=chamado.id)
    
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao')  # Obtém se foi confirmado ou não
        nota = request.POST.get("avaliacao")
        comentario = request.POST.get("comentario", "")

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chamados',
            {
                'type': 'send_update',
                'message': f'Status do chamado N°{chamado.id} alterado.',
            }
        )

        if confirmacao == 'sim':  # Se o usuário confirmou a finalização
            if nota:  # Se já houver uma avaliação, salva
                avaliacao, created = Avaliacao.objects.get_or_create(chamado=chamado, usuario=request.user)
                avaliacao.nota = int(nota)
                avaliacao.comentario = comentario
                avaliacao.save()
                chamado.status = "Concluído"
                chamado.save()
                messages.success(request, "Chamado finalizado e avaliação enviada com sucesso!")
            else:
                chamado.status = "Concluído"
                chamado.save()
                messages.success(request, "Chamado finalizado com sucesso!")

        elif confirmacao == 'nao':  # Se o usuário NÃO confirmou a finalização
            chamado.status = "Em andamento"
            chamado.save()
            messages.warning(request, "O problema não foi resolvido. O chamado permanece em andamento.")

        return redirect('chamado_by_id', chamado_id=chamado.id)

    return render(request, 'detalhe_chamado.html', {'chamado': chamado})


    return render(request, 'detalhe_chamado.html', {'chamado': chamado})

def custom_handler404(request, exception=None):
    return render(request, 'error-404.html')

# def send_message_to_all_users(message):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         'all_users',
#         {
#             'type': 'chat_message',
#             'message': message
#         }
#     )
    
# def enviar_mensagem_ti(request):
#     if request.user.profile.equipe_ti:
#         mensagem = "Informamos que, devido a falha de internet no estado estamos sem internet, agradecemos a compreensão"
#         send_message_to_all_users(mensagem)
#         return JsonResponse({'status': 'Mensagem enviada!'})

