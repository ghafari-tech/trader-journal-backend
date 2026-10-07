from rest_framework import serializers

from app_admin.models import Api_Ai
from app_ai_analysis.models import AIModel
from app_setting.models import Subscription, SubscriptionFeature
from app_user.models import User


class UserAdminSerializer(serializers.ModelSerializer):
    subscription_type = serializers.CharField(
        source="plan.type",
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "subscription_type",
            "status",
            "created_at",
        ]


class SubscriptionFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionFeature
        fields = ["id", "value"]


class SubscriptionSerializer(serializers.ModelSerializer):
    features = SubscriptionFeatureSerializer(
        source="feature",
        many=True
    )

    class Meta:
        model = Subscription
        fields = ["id", "name", "price", "features"]

    def update(self, instance, validated_data):
        features_data = validated_data.pop("feature", [])

        instance.name = validated_data.get("name", instance.name)
        instance.price = validated_data.get("price", instance.price)
        instance.save()

        existing_features = {
            feature.id: feature
            for feature in instance.feature.all()
        }

        sent_feature_ids = set()

        for feature_data in features_data:
            feature_id = feature_data.get("id")

            if feature_id:
                feature = existing_features.get(feature_id)

                if feature:
                    feature.value = feature_data.get(
                        "value",
                        feature.value
                    )
                    feature.save()

                    sent_feature_ids.add(feature_id)

            else:
                SubscriptionFeature.objects.create(
                    subscription=instance,
                    **feature_data
                )

        for feature_id, feature in existing_features.items():
            if feature_id not in sent_feature_ids:
                feature.delete()

        return instance

class ApiSerializer(serializers.Serializer):
    class Meta:
        model = Api_Ai
        fields = "__all__"


class AIModelAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = [
            "id",
            "name",
            "model",
            "description",
            "api_key",
            "url",
            "is_default",
            "used_tokens",
        ]
        read_only_fields = ["id", "used_tokens"]