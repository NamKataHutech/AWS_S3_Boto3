from rest_framework import serializers
from .models import Report
class ReportSerializer(serializers.ModelSerializer):
    class  Meta:
        model= Report
        fields =['id','bucket','path', 's3_src']