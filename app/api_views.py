from rest_framework import viewsets
from .models import Chamados, Comentarios, Avaliacao
from .serializers import ChamadoSerializer, ComentarioSerializer, AvaliacaoSerializer

class ChamadoViewSet(viewsets.ModelViewSet):
    queryset = Chamados.objects.all()
    serializer_class = ChamadoSerializer

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentarios.objects.all()
    serializer_class = ComentarioSerializer

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer