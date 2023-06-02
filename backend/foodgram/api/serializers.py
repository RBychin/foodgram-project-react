from djoser.serializers import UserCreateSerializer as DUCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(DUCreateSerializer):
    class Meta(DUCreateSerializer.Meta):
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'email': representation['email'],
            'id': representation['id'],
            'username': representation['username'],
            'first_name': representation['first_name'],
            'last_name': representation['last_name'],
        }

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        password = validated_data.get('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')

        user = User.objects.create_user(email=email,
                                        username=username,
                                        password=password,
                                        first_name=first_name,
                                        last_name=last_name)

        return user