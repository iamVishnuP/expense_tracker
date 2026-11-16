from django.shortcuts import render,get_object_or_404

from rest_framework.views import APIView
from rest_framework import authentication 
from rest_framework  import  permissions
from rest_framework.response import Response

from django.db.models import Sum

from datetime import datetime

from transactions.serializers import ExpenseSerializer

from transactions.models import Expense
from transactions.permissions import IsOwner

# Create your views here.

class ExpenseListCreateView(APIView):

    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):

        auth_user= request.user

        qs= Expense.objects.filter(owner=auth_user)
        serializer_instance= ExpenseSerializer(qs,many=True)
        return Response(serializer_instance.data)

    def post(self,request):

        form_data=request.data
        auth_user=request.user

        serializer_instance=ExpenseSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(owner=auth_user)
            return Response(serializer_instance.data)
        else:
            return Response(serializer_instance.errors)

class ExpenseRetreieveUpdateDeleteView(APIView):
    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[IsOwner]

    def get(self,request,pk=None):
        qs=get_object_or_404(Expense,id=pk)

        self.check_object_permissions(request,qs)

        serializer_instance=ExpenseSerializer(qs)
        return Response(serializer_instance.data)

    def put(self,request,pk=None):

        instance=get_object_or_404(Expense,id=pk)
        form_data=request.data

        self.check_object_permissions(request,instance)

        serializer_instance=ExpenseSerializer(data=form_data, instance=instance)

        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(serializer_instance.data)
        else:
            return Response(serializer_instance.error)

    def delete(self,request,pk=None):
        instance=get_object_or_404(Expense,id=pk)

        self.check_object_permissions(request,instance)

        instance.delete()
        return Response({"message":"deleted"})


class ExpenseSummaryView(APIView):

    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):

        auth_user_expense=Expense.objects.filter(owner=request.user)
        response_data={
            "todays_total":0,
            "monthly_total":0
        }
        curr_date=datetime.today().date()
        todays_total= auth_user_expense.filter(created_at=curr_date).values("amount").aggregate(total=Sum("amount")).get("total")
        response_data["todays_total"]=todays_total
        return Response(response_data)
