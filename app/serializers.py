from rest_framework import serializers
from .models import Chamados, Comentarios, Avaliacao, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class ChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamados
        fields = '__all__'

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentarios
        fields = '__all__'

class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = '__all__'