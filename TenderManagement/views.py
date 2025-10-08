from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from Core.Core.drf import generics
from django.contrib.auth import get_user_model
from django.apps import apps

from .services import start_extract_pdf
# from PurchaseEnquiry.models import PurchaseEnquiry
from TenderManagement.models import Consumable, Service, TenderCheckListItems
# from CompareQuotation.models import CompareQuotation

User = get_user_model()
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import DateRangeFilter,DateFilter
from django_filters.filters import Filter
from Core.Core.permissions.permissions import GetPermission 

from django.shortcuts import get_object_or_404

import django_filters

from collections import defaultdict
from decimal import Decimal


from .serializers import *

from Masters.models import *




from .models import BudgetEnquiry, TenderAbstract, TenderItem, SecurityDeposit, LetterOfAward, Order
from .serializers import (
    BudgetEnquiryListSerializer, 
    BudgetEnquiryDetailSerializer,
    BudgetEnquiryMiniSerializer,
    BudgetEnquiryItemSerializer,
    SecurityDepositSerializer, 
    SecurityDepositCreateSerializer, 
    SecurityDepositUpdateSerializer, 
    LetterOfAwardSerializer, 
    LetterOfAwardMiniSerializer,
    OrderSerializer,
    OrderMiniSerializer
)

class ListFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        self.lookup_expr = 'in'
        values = value.split(',')
        return super(ListFilter, self).filter(qs, values)
    

class TenderItemMasterFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = TenderItemMaster
        fields = ['start_date','end_date','date_range',]


class TenderItemMasterCreate(generics.CreateAPIView):
    serializer_class = TenderItemMasterSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = ['name', 'code',]
    filterset_class = TenderItemMasterFilter


class TenderItemMasterList(generics.ListAPIView):
    serializer_class = TenderItemMasterSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = ['name', 'code',]
    filterset_class = TenderItemMasterFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        user = self.request.user

        queryset = TenderItemMaster.objects.filter(is_deleted=False,  )
        
        return queryset.order_by('-created_on')



class TenderItemMasterMiniList(generics.ListAPIView):
    serializer_class = TenderItemMasterMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = ['name', ]
    filterset_class = TenderItemMasterFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        user = self.request.user

        queryset = TenderItemMaster.objects.filter(is_deleted=False,  )
        
        # if not user.is_superuser and not user.has_perm('System.all_data'):
        #     if user.has_perm('System.all_company_dataa'):
        #         # queryset = queryset.filter(user__organization=user.organization)
        #         queryset = queryset.filter(user=user)
        #     else:
        #         queryset = queryset.filter(user = self.request.user)
            
        return queryset.order_by('-created_on')
    

class TenderItemMasterDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TenderItemMasterSerializer
    queryset = TenderItemMaster.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = TenderItemMaster.objects.filter(is_deleted=False,)
        return queryset


    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()


class TenderItemFilter(FilterSet):
    date_range = DateRangeFilter(field_name='tender__created_on')
    start_date = DateFilter(field_name='tender__created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='tender__created_on',lookup_expr=('lte'))

    company = django_filters.ModelChoiceFilter(
        field_name='tender__company',
        queryset=apps.get_model('DynamicDjango', 'Company').objects.all()
    )

    customer = django_filters.ModelChoiceFilter(
        field_name='tender__customer',
        queryset=Account.objects.filter(is_deleted=False)
    )

    project = django_filters.ModelChoiceFilter(
        field_name='tender__project',
        queryset=Project.objects.filter(is_deleted=False)
    )

    sourceportal = django_filters.ModelChoiceFilter(
        field_name='tender__sourceportal',
        queryset=SourcePortal.objects.filter(is_deleted=False)
    )

    tender_type = django_filters.ChoiceFilter(
        field_name='tender__tender_type',
        choices=Tender.TENDERTYPE_CHOICES
    )

    product_type = django_filters.ChoiceFilter(
        field_name='tender__product_type',
        choices=Tender.PRODUCTTYPE_CHOICES
    )

    class Meta:
        model = TenderItem
        fields = ['start_date','end_date','date_range','tender', 'project', 'customer', 'tenderitemmaster',
                  'tender_type', 'product_type', 'sourceportal',
                  ]



class TenderFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    company = django_filters.ModelChoiceFilter(
        queryset=apps.get_model('DynamicDjango', 'Company').objects.all()
    )

    location = django_filters.ModelChoiceFilter(
        queryset=apps.get_model('DynamicDjango', 'Location').objects.all()
    )
    class Meta:
        model = Tender
        fields = ['start_date','end_date','date_range','tender_stage','project','tender_type','company','location', 'product_type','screen_type','sourceportal', 'customer','authorized_status']


class TenderCreate(generics.CreateAPIView):
    serializer_class = TenderSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code','mobile',]
    filterset_class = TenderFilter


class TenderMini(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TenderMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ,).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['code','tender_no','department_name','customer__name','pre_bid_place','pre_bid_meet_address','ministry']
    filterset_class = TenderFilter
    ordering_fields = ['code','created_on']


class TenderStatusMini(generics.ListAPIView): #only tender status projects
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TenderMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ,status = Tender.PENDING ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['code','tender_no','department_name','customer__name','pre_bid_place','pre_bid_meet_address','ministry']
    filterset_class = TenderFilter
    ordering_fields = ['code','created_on']
    


class TenderList(generics.ListAPIView):
    permission_classes = [GetPermission('TenderManagement.view_tender')]
    serializer_class = TenderSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['code','tender_no','department_name','customer__name','pre_bid_place','pre_bid_meet_address','ministry']
    filterset_class = TenderFilter
    ordering_fields = ['code','created_on']

    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
    

class TenderDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GetPermission('TenderManagement.view_tender') | GetPermission('TenderManagement.delete_tender') | GetPermission('TenderManagement.change_tender')]
    serializer_class = TenderSerializer
    queryset = Tender.objects.filter().order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()

        

class TenderStageView(generics.UpdateAPIView):
    serializer_class = TenderStageSerializer
    queryset = Tender.objects.filter(is_deleted=False).order_by('-created_on')


class TenderCommentsFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = TenderComments
        fields = ['start_date','end_date','date_range','tender',]


class TenderCommentsCreate(generics.CreateAPIView):
    serializer_class = TenderCommentSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = TenderCommentsFilter



class TenderCommentsList(generics.ListAPIView):
    serializer_class = TenderCommentSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = TenderCommentsFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
    
class TenderCommentsDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TenderCommentSerializer
    queryset = TenderComments.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()


class TenderItemAssignFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = TenderItemAssign
        fields = ['start_date','end_date','date_range','tender','tender_item','tenderitemmaster','user']


class TenderItemAssignCreate(generics.CreateAPIView):
    serializer_class = TenderItemAssignSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = TenderItemAssignFilter


class TenderItemAssignList(generics.ListAPIView):
    serializer_class = TenderItemAssignSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = TenderItemAssignFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
    
class TenderItemAssignDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TenderItemAssignSerializer
    queryset = TenderItemAssign.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()



class TenderAttachmentsFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = TenderAttachments
        fields = ['start_date','end_date','date_range','tender',]



class TenderAttachmentsCreate(generics.CreateAPIView):
    permission_classes = [GetPermission('TenderManagement.add_tender') ]
    serializer_class = TenderAttachmentsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = TenderAttachmentsFilter



class TenderAttachmentsList(generics.ListAPIView):
    permission_classes = [GetPermission('TenderManagement.view_tender') ]

    serializer_class = TenderAttachmentsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = TenderAttachmentsFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
    

class TenderAttachmentsDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TenderAttachmentsSerializer
    queryset = TenderAttachments.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()




class CasesheetFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = CaseSheet
        fields = ['start_date','end_date','date_range','tender','authorized_status',] #'tender__assign_to'


class CaseSheetCreate(generics.CreateAPIView):
    serializer_class = CaseSheetSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code','oem_challenges','department_challenges','email']
    filterset_class = CasesheetFilter



class CaseSheetList(generics.ListAPIView):
    serializer_class = CaseSheetSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'oem_challenges', 'department_challenges', 'email']
    filterset_class = CasesheetFilter
    ordering_fields = ['code','created_on']

    
    def get_queryset(self):
        tender_id = self.kwargs.get('tender_id')
        
        queryset = super().get_queryset()
        queryset=queryset.filter(tender_id = tender_id)
        return queryset.order_by('-created_on')



class CaseSheetDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaseSheetSerializer
    queryset = CaseSheet.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        
        queryset = super().get_queryset()
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()


class CaseSheetUpdate(generics.UpdateAPIView):
    # permission_classes = [GetPermission('TenderManagement.can_approve_casesheet')]
    serializer_class = CaseSheetUpdateSerializer
    queryset = CaseSheet.objects.filter(is_deleted=False, authorized_status = CaseSheet.PENDING).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = CaseSheet.objects.filter(is_deleted=False, authorized_status = CaseSheet.PENDING )

        # queryset = check_tender_permission(queryset,user)

        return queryset


class ReverseAuctionFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = ReverseAuction
        fields = ['start_date','end_date','date_range','tender','tender_item_master','tender_item'] #'tender__assign_to',



class ReverseAuctionCreate(generics.CreateAPIView):
    serializer_class = ReverseAuctionSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code']
    filterset_class = ReverseAuctionFilter

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        tender_item_id = validated_data.get('tender_item_id')

        reverse_auction = self.model.objects.filter(tender_item_id=tender_item_id).first()

        if reverse_auction:
            serializer = self.get_serializer(reverse_auction, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

        # Step 1: Calculate landing_cost_margin_amount
        discount_landing_cost = validated_data.get('discount_landing_cost', 0) or 0
        landing_cost_margin = validated_data.get('landing_cost_margin', 0) or 0
        landing_cost_margin_amount = discount_landing_cost * (landing_cost_margin / 100)

        # Step 2: Calculate landing_cost_total
        landing_cost_total = discount_landing_cost + landing_cost_margin_amount

        # Step 3: Calculate landing_cost_gst_amount
        landing_cost_gst = validated_data.get('landing_cost_gst', 0)
        landing_cost_gst_amount = landing_cost_total * (landing_cost_gst / 100)

        # Step 4: Calculate total
        total = landing_cost_gst_amount + landing_cost_total

        # Update the serializer with the calculated fields before saving
        serializer.save(
            landing_cost_margin_amount=landing_cost_margin_amount,
            landing_cost_total=landing_cost_total,
            landing_cost_gst_amount=landing_cost_gst_amount,
            total=total
        )

        return Response(serializer.data, status=status.HTTP_200_OK if reverse_auction else status.HTTP_201_CREATED)



        
class ReverseAuctionList(generics.ListAPIView):
    serializer_class = ReverseAuctionSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted = False, ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = ReverseAuctionFilter
    ordering_fields = ['code','created_on']

    
    def get_queryset(self):
        tender_id = self.kwargs.get('tender_id')
        
        queryset = super().get_queryset()
        queryset=queryset.filter(tender_id = tender_id)
        return queryset.order_by('-created_on')
        


class ReverseAuctionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReverseAuctionSerializer
    queryset = ReverseAuction.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = ReverseAuction.objects.filter(is_deleted=False,)
        # queryset = check_tender_permission(queryset,self.request.user)
        return queryset


    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()




class L1PriceUpdate(generics.UpdateAPIView):
    permission_classes = [GetPermission('TenderManagement.can_l1_price_add')]
    serializer_class = ReverseAuctionL1PriceSerializer
    queryset = ReverseAuction.objects.filter(is_deleted=False,).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = ReverseAuction.objects.filter(is_deleted=False)
        return queryset


class TenderDocumentsFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = TenderDocuments
        fields = ['start_date','end_date','date_range','tender','is_submitted', 'type']#'tender__assign_to',


class TenderDocumentsCreate(generics.CreateAPIView):
    serializer_class = TenderDocumentsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code','document_name']
    filterset_class = TenderDocumentsFilter


class TenderDocumentsList(generics.ListAPIView):
    serializer_class = TenderDocumentsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code']
    filterset_class = TenderDocumentsFilter
    ordering_fields = ['code','created_on']


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
        

    

class TenderDocumentsDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TenderDocumentsSerializer
    queryset = TenderDocuments.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = TenderDocuments.objects.filter(is_deleted=False,)
        # queryset = check_tender_permission(queryset,self.request.user)
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()



class BidAmountFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = BidAmount
        fields = ['start_date','end_date','date_range','tender',] #'tender__assign_to'


class BidAmountCreate(generics.CreateAPIView):
    serializer_class = BidAmountSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = BidAmountFilter


class BidAmountList(generics.ListAPIView):
    serializer_class = BidAmountSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = BidAmountFilter
    ordering_fields = ['code','created_on']

    
    def get_queryset(self):
        tender_id = self.kwargs.get('tender_id')
        
        queryset = super().get_queryset()
        queryset=queryset.filter(tender_id = tender_id)
        return queryset.order_by('-created_on')
        



class BidAmountDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidAmountSerializer
    queryset = BidAmount.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = BidAmount.objects.filter(is_deleted=False,)
        # queryset = check_tender_permission(queryset,self.request.user)
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()




class BidAmountL1PriceUpdate(generics.UpdateAPIView):
    serializer_class = BidAmountL1PriceSerializer
    queryset = BidAmount.objects.filter(is_deleted=False,).order_by('-created_on')

    def get_queryset(self):
        user = self.request.user
        queryset = BidAmount.objects.filter(is_deleted=False)
        # queryset = check_tender_permission(queryset,self.request.user)
        return queryset


class FileWorkflowAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PDFExtractionSerializer
    model = serializer_class.Meta.model

    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')

    def perform_create(self, serializer):
        obj=serializer.save() 
        start_extract_pdf(obj.id)




class CheckFileWorkflowView(APIView,):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        
        request_id = kwargs['pk']

        try:
            obj=PDFExtraction.objects.filter(id=request_id).first()
            print("obj",obj)
            if obj.status != 1:
                obj_data = PDFExtractionSerializer(obj).data  
                return JsonResponse({'message': "Report is Completed",'status': True, 'result': obj_data}, status=201)
            else:
                return JsonResponse({'message': "Report is generating", 'status': False}, status=202)

        except Exception as e:
            return JsonResponse({'message': "ID Does Not Exist",'status': False, 'error': str(e)}, status=404)
        



class CostingSheetFilter(FilterSet):
    authorized_status = ListFilter(field_name='authorized_status')
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))

    class Meta:
        model = CostingSheet
        fields = ['start_date', 'end_date', 'date_range', 'tender','project','authorized_status']


class CostingSheetMini(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CostingSheetMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = CostingSheetFilter
    search_fields = ['code','tender__code',]
    ordering_fields = ['code','created_on']




class CostingSheetList(generics.ListCreateAPIView):
    # permission_classes = [GetPermission('Masters.View')]
    serializer_class = CostingSheetSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = CostingSheetFilter
    search_fields = ['code','tender__code',]
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        tender_id = self.kwargs.get('tender_id')
        
        queryset = super().get_queryset()
        queryset=queryset.filter(tender_id = tender_id)
        return queryset.order_by('-created_on')


class CostingSheetDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CostingSheetSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted = False)

        
    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()
        

class ServiceFilter(FilterSet):

    class Meta:
        model = Service
        fields = ['item','tender']

class ServiceMini(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['item__name','code','tender__code' ]
    ordering_fields = ['code','created_on']




class ServiceList(generics.ListCreateAPIView):
    # permission_classes = [GetPermission('Masters.View')]
    serializer_class = ServiceSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['item__name','code','tender__code' ]
    ordering_fields = ['code','created_on']


class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted = False)

        
    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()



class ConsumableFilter(FilterSet):

    class Meta:
        model = Consumable
        fields = ['item','tender']

class ConsumableMini(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConsumableMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = ConsumableFilter
    search_fields = ['item__name','code','tender__code' ]
    ordering_fields = ['code','created_on']




class ConsumableList(generics.ListCreateAPIView):
    # permission_classes = [GetPermission('Masters.View')]
    serializer_class = ConsumableSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = ConsumableFilter
    search_fields = ['code', 'item__name','tender__code']
    ordering_fields = ['code','created_on']


class ConsumableDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConsumableSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted = False)

        
    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()



class OtherChargesFilter(FilterSet):

    class Meta:
        model = OtherCharges
        fields = ['tender','miscellaneoustype']


class OtherChargesMini(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OtherChargesMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).only('id','name',).order_by('name')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = OtherChargesFilter
    search_fields = ['name','code','tender__code','miscellaneoustype__name']
    ordering_fields = ['code','created_on']




class OtherChargesList(generics.ListCreateAPIView):
    # permission_classes = [GetPermission('Masters.View')]
    serializer_class = OtherChargesSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = OtherChargesFilter
    search_fields = ['name','code','tender__code','miscellaneoustype__name']
    ordering_fields = ['code','created_on']


class OtherChargesDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OtherChargesSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted = False)

        
    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()


class RawMaterialFilter(FilterSet):

    class Meta:
        model = RawMaterial
        fields = ['tender','item', 'type', 'costingsheet']


class RawMaterialMini(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RawMaterialMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_class = RawMaterialFilter
    search_fields = ['code','tender__code' ]
    ordering_fields = ['code','created_on']




class RawMaterialList(generics.ListCreateAPIView):
    serializer_class = RawMaterialSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['code','tender__code' ]
    ordering_fields = ['code','created_on']



class RawMaterialDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RawMaterialSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted = False)

        
    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()




class TenderDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tender_id, is_margin_value):
        try:
            tender = Tender.objects.get(id=tender_id, is_deleted=False)
        except Tender.DoesNotExist:
            return Response({'error': 'Tender not found'}, status=status.HTTP_404_NOT_FOUND)

        is_margin = is_margin_value.lower() == 'true'
        tender_data = TenderMiniSerializer(tender).data

        # Calculate raw materials
        raw_materials_data = self._calculate_raw_materials(tender, is_margin)
        
        # Calculate services
        services_data = self._calculate_services(tender, is_margin)
        
        # Calculate consumables
        consumables_data = self._calculate_consumables(tender, is_margin)
        
        # Calculate other charges
        other_charges_data = self._calculate_other_charges(tender, is_margin)

        # Calculate total bid value
        bid_value_total = (
            Decimal(raw_materials_data["total"]) +
            Decimal(services_data["total"]) +
            Decimal(consumables_data["total"]) +
            Decimal(other_charges_data["total"])
        )

        tender_data["bid_value"] = str(bid_value_total)

        response_data = {
            "tender": tender_data,
            "raw_materials": raw_materials_data,
            "services": services_data,
            "consumables": consumables_data,
            "other_charges": other_charges_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def _calculate_raw_materials(self, tender, is_margin):
        """Calculate raw materials with proper grouping and totals"""
        # enquiries = PurchaseEnquiry.objects.filter(
        #     project=tender.project,
        #     project__status=Project.TENDER,
        #     is_deleted=False
        # )
        enquiries = []

        grouped_items = defaultdict(lambda: {
            "name": "",
            "total": Decimal("0.00"),
            "items": []
        })

        # Process raw materials
        rawmaterials = RawMaterial.objects.filter(
            tender=tender, 
            is_deleted=False
        ).prefetch_related('item__parent')
        
        for rawmaterial in rawmaterials:
            item = rawmaterial.item
            group = item.parent
            group_id = str(group.id) if group else "ungrouped"
            group_name = group.name if group else "Ungrouped"

            # Calculate item value
            base_value = Decimal(rawmaterial.total_price or "0.00")
            margin = Decimal(rawmaterial.margin_amount or "0.00")
            item_value = base_value if is_margin else (base_value - margin)

            item_data = {
                "id": str(item.id),
                "name": item.name,
                "price": rawmaterial.price,
                "qty": rawmaterial.qty,
                "total_price": item_value
            }

            grouped_items[group_id]["name"] = group_name
            grouped_items[group_id]["total"] += item_value
            grouped_items[group_id]["items"].append(item_data)

        # Process quotations
        # quotations = CompareQuotation.objects.filter(
        #     purchase_enquiry__in=enquiries,
        #     is_deleted=False
        # ).prefetch_related('comparequotationitems__item__parent')

        quotations = []

        for quotation in quotations:
            for item in quotation.comparequotationitems.all():
                group = item.item.parent
                group_id = str(group.id) if group else "ungrouped"
                group_name = group.name if group else "Ungrouped"

                # Calculate item value
                base_value = Decimal(item.total_price or "0.00")
                margin = Decimal(item.margin_value or "0.00")
                item_value = base_value if is_margin else (base_value - margin)

                item_data = {
                    "id": str(item.item.id),
                    "name": item.item.name,
                    "price": item.price,
                    "qty": item.qty,
                    "total_price": item_value,
                }

                grouped_items[group_id]["name"] = group_name
                grouped_items[group_id]["total"] += item_value
                grouped_items[group_id]["items"].append(item_data)

        # Calculate grand total from grouped items
        grand_total = sum(group_data["total"] for group_data in grouped_items.values())

        # Convert to response format
        item_groups = [
            {
                "id": group_id,
                "name": group_data["name"],
                "total": str(group_data["total"]),
                "items": group_data["items"]
            }
            for group_id, group_data in grouped_items.items()
        ]

        return {
            "total": str(grand_total),
            "item_groups": item_groups
        }

    def _calculate_services(self, tender, is_margin):
        """Calculate services total"""
        services = Service.objects.filter(tender=tender, is_deleted=False)
        services_serialized = ServiceMini2Serializer(services, many=True).data
        
        total = services.aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
        margin = services.aggregate(total=Sum("margin_amount"))["total"] or Decimal("0.00")
        services_total = total if is_margin else (total - margin)

        return {
            "total": str(services_total),
            "data": services_serialized
        }

    def _calculate_consumables(self, tender, is_margin):
        """Calculate consumables total"""
        consumables = Consumable.objects.filter(tender=tender, is_deleted=False)
        consumables_serialized = ConsumableMini2Serializer(consumables, many=True).data
        
        total = consumables.aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")
        margin = consumables.aggregate(total=Sum("margin_amount"))["total"] or Decimal("0.00")
        consumables_total = total if is_margin else (total - margin)

        return {
            "total": str(consumables_total),
            "data": consumables_serialized
        }

    def _calculate_other_charges(self, tender, is_margin):
        """Calculate other charges total"""
        other_charges = OtherCharges.objects.filter(tender=tender, is_deleted=False)
        other_charges_serialized = OtherChargesMiniSerializer(other_charges, many=True).data
        
        total = other_charges.aggregate(total=Sum("price"))["total"] or Decimal("0.00")
        margin = other_charges.aggregate(total=Sum("margin_amount"))["total"] or Decimal("0.00")
        other_charges_total = total if is_margin else (total - margin)

        return {
            "total": str(other_charges_total),
            "data": other_charges_serialized
        }



class PlazoTenderFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))

    class Meta:
        model = PlazoTender
        fields = ['start_date','end_date','date_range','customer', 'status']



class PlazoTenderList(generics.ListAPIView):
    serializer_class = PlazoTenderSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = [ 'code','name','tender_no','customer__code',]
    filterset_class = PlazoTenderFilter
    ordering_fields = ['code','created_on']

    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
    

class PlazoTenderCreate(generics.CreateAPIView):
    serializer_class = PlazoTenderSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code','name','tender_no','customer__code',]
    filterset_class = PlazoTenderFilter


class PlazoTenderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlazoTenderSerializer
    queryset = PlazoTender.objects.filter().order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()



class PlazoTenderMiniList(generics.ListAPIView):
    serializer_class = PlazoTenderMiniSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = [ 'code','name','tender_no','customer__code',]
    filterset_class = PlazoTenderFilter
    ordering_fields = ['code','created_on']

    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
        


class PlazoTenderAttachmentFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = PlazoTenderAttachment
        fields = ['start_date','end_date','date_range','plazo_tender',]



class PlazoTenderAttachmentCreate(generics.CreateAPIView):
    permission_classes = [GetPermission('TenderManagement.add_plazotender') ]
    
    serializer_class = PlazoTenderAttachmentSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = PlazoTenderAttachmentFilter


class PlazoTenderAttachmentList(generics.ListAPIView):
    permission_classes = [GetPermission('TenderManagement.view_plazotender') ]

    serializer_class = PlazoTenderAttachmentSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False ).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    search_fields = [ 'code',]
    filterset_class = PlazoTenderAttachmentFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_on')
    

class PlazoTenderAttachmentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlazoTenderAttachmentSerializer
    queryset = PlazoTenderAttachment.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()


class TenderCheckListItemsFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on',lookup_expr=('gte'),)
    end_date = DateFilter(field_name='created_on',lookup_expr=('lte'))
    class Meta:
        model = TenderCheckListItems
        fields = ['start_date','end_date','date_range','tender','tender_checklist']


class TenderCheckListItemsList(generics.ListAPIView):
    permission_classes = [GetPermission('TenderManagement.view_tender')]
    serializer_class = TenderCheckListItemsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tender__code', 'tender_checklist__name']
    filterset_class = TenderCheckListItemsFilter
    ordering_fields = ['code','created_on']

    def get_queryset(self):
        tender_id = self.kwargs.get('tender_id')
        queryset = super().get_queryset()
        if tender_id:
            queryset = queryset.filter(tender_id=tender_id)
        return queryset.order_by('-created_on')


class TenderCheckListItemsCreate(generics.CreateAPIView):
    permission_classes = [GetPermission('TenderManagement.add_tender')]
    serializer_class = TenderCheckListItemsSerializer
    model = serializer_class.Meta.model
    queryset = model.objects.filter(is_deleted=False).order_by('-created_on')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['tender__code', 'tender_checklist__name']
    filterset_class = TenderCheckListItemsFilter


class TenderCheckListItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GetPermission('TenderManagement.view_tender') | GetPermission('TenderManagement.change_tender') | GetPermission('TenderManagement.delete_tender')]
    serializer_class = TenderCheckListItemsSerializer
    queryset = TenderCheckListItems.objects.filter(is_deleted=False).order_by('-created_on')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()


class BudgetEnquiryFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on', lookup_expr='gte')
    end_date = DateFilter(field_name='created_on', lookup_expr='lte')
    status = django_filters.MultipleChoiceFilter(choices=TenderAbstract.STATUS_CHOICES)
    tender_type = django_filters.MultipleChoiceFilter(choices=TenderAbstract.TENDERTYPE_CHOICES)
    product_type = django_filters.MultipleChoiceFilter(choices=TenderAbstract.PRODUCTTYPE_CHOICES)
    customer = django_filters.ModelMultipleChoiceFilter(queryset=Account.objects.filter(is_deleted=False))
    company = django_filters.ModelMultipleChoiceFilter(queryset=Company.objects.filter(is_deleted=False))
    tender_stage = django_filters.ModelMultipleChoiceFilter(queryset=Stage.objects.filter(is_deleted=False))
    lead = django_filters.ModelMultipleChoiceFilter(queryset=apps.get_model('LeadManagement', 'Lead').objects.filter(is_deleted=False))
    user = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.filter(is_active=True))
    bdm = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.filter(is_active=True))
    
    class Meta:
        model = BudgetEnquiry
        fields = ['status', 'tender_type', 'product_type', 'customer', 'company', 'tender_stage', 'lead', 'user', 'bdm']


class BudgetEnquiryList(generics.ListAPIView):
    serializer_class = BudgetEnquiryListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BudgetEnquiryFilter
    search_fields = ['name', 'tender_no', 'description', 'customer__name', 'company__name']
    ordering_fields = ['created_on', 'modified_on', 'name', 'tender_datetime']
    ordering = ['-created_on']
    
    def get_queryset(self):
        return BudgetEnquiry.objects.get_filter().select_related(
            'customer', 'company', 'location', 'sourceportal', 'tender_stage', 'project'
        ).prefetch_related('tender_items')


class BudgetEnquiryCreate(generics.CreateAPIView):
    queryset = BudgetEnquiry.objects.get_filter()
    serializer_class = BudgetEnquiryDetailSerializer


class BudgetEnquiryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BudgetEnquiry.objects.get_filter()
    serializer_class = BudgetEnquiryDetailSerializer
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class BudgetEnquiryMini(generics.ListAPIView):
    queryset = BudgetEnquiry.objects.get_filter()
    serializer_class = BudgetEnquiryMiniSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'tender_no', 'customer__name']


class BudgetEnquiryItems(generics.ListAPIView):
    serializer_class = BudgetEnquiryItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['tenderitemmaster__name', 'item_specifications']
    
    def get_queryset(self):
        budget_enquiry_id = self.kwargs.get('budget_enquiry_id')
        return TenderItem.objects.filter(
            tender_id=budget_enquiry_id,
            is_deleted=False
        ).select_related('tenderitemmaster', 'unit')


class BudgetEnquiryRFQItems(generics.ListAPIView):
    serializer_class = BudgetEnquiryItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['tenderitemmaster__name', 'item_specifications']
    
    def get_queryset(self):
        budget_enquiry_id = self.kwargs.get('budget_enquiry_id')
        print('budget_enquiry_id', budget_enquiry_id)
        return TenderItem.objects.filter(
            tender_id=budget_enquiry_id,
            is_deleted=False,
            is_rfq_required=True
        ).select_related('tenderitemmaster', 'unit')


class SecurityDepositListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'customer', 'type', 'status']
    search_fields = ['customer__name', 'type']
    ordering_fields = ['received_on', 'due_expiry_date', 'amount']
    ordering = ['-received_on']
    
    def get_queryset(self):
        return SecurityDeposit.objects.select_related('customer', 'project').filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SecurityDepositCreateSerializer
        return SecurityDepositSerializer


class SecurityDepositDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SecurityDeposit.objects.select_related('customer', 'project').filter(is_deleted=False)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SecurityDepositUpdateSerializer
        return SecurityDepositSerializer


class SecurityDepositByProjectView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SecurityDepositSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'type', 'status']
    search_fields = ['customer__name', 'type']
    ordering_fields = ['received_on', 'due_expiry_date', 'amount']
    ordering = ['-received_on']
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return SecurityDeposit.objects.filter(project_id=project_id, is_deleted=False).select_related('customer', 'project')


class LetterOfAwardFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on', lookup_expr='gte')
    end_date = DateFilter(field_name='created_on', lookup_expr='lte')
    status = django_filters.MultipleChoiceFilter(choices=LetterOfAward.STATUS_CHOICES)
    
    class Meta:
        model = LetterOfAward
        fields = ['tender', 'project', 'customer', 'status']


class LetterOfAwardListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LetterOfAwardFilter
    search_fields = ['code', 'customer__name', 'tender__tender_no']
    ordering_fields = ['created_on', 'issue_date', 'award_amount']
    ordering = ['-created_on']
    
    def get_queryset(self):
        return LetterOfAward.objects.select_related('tender', 'project', 'customer').filter(is_deleted=False)
    
    def get_serializer_class(self):
        return LetterOfAwardSerializer


class LetterOfAwardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LetterOfAwardSerializer
    queryset = LetterOfAward.objects.select_related('tender', 'project', 'customer').filter(is_deleted=False)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class LetterOfAwardMiniView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LetterOfAwardMiniSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'customer__name']
    
    def get_queryset(self):
        return LetterOfAward.objects.select_related('customer').filter(is_deleted=False)


class LetterOfAwardByTenderView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LetterOfAwardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'customer__name']
    ordering_fields = ['created_on', 'issue_date']
    ordering = ['-created_on']
    
    def get_queryset(self):
        tender_id = self.kwargs['tender_id']
        return LetterOfAward.objects.filter(tender_id=tender_id, is_deleted=False).select_related('tender', 'project', 'customer')


class LetterOfAwardDocumentUploadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = LetterOfAward.objects.filter(is_deleted=False)
    serializer_class = LetterOfAwardSerializer
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        document_type = request.data.get('document_type')
        
        if document_type not in ['loa_document', 'acceptance_document']:
            return Response({'error': 'Invalid document type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if document_type in request.FILES:
            setattr(instance, document_type, request.FILES[document_type])
            instance.save()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)


class OrderFilter(FilterSet):
    date_range = DateRangeFilter(field_name='created_on')
    start_date = DateFilter(field_name='created_on', lookup_expr='gte')
    end_date = DateFilter(field_name='created_on', lookup_expr='lte')
    status = django_filters.MultipleChoiceFilter(choices=Order.STATUS_CHOICES)
    
    class Meta:
        model = Order
        fields = ['tender', 'project', 'customer', 'status']


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['code', 'customer__name', 'tender__tender_no']
    ordering_fields = ['created_on', 'issue_date', 'order_amount']
    ordering = ['-created_on']
    
    def get_queryset(self):
        return Order.objects.select_related('tender', 'project', 'customer').filter(is_deleted=False)
    
    def get_serializer_class(self):
        return OrderSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related('tender', 'project', 'customer').filter(is_deleted=False)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class OrderMiniView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderMiniSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'customer__name']
    
    def get_queryset(self):
        return Order.objects.select_related('customer').filter(is_deleted=False)


class OrderByTenderView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'customer__name']
    ordering_fields = ['created_on', 'issue_date']
    ordering = ['-created_on']
    
    def get_queryset(self):
        tender_id = self.kwargs['tender_id']
        return Order.objects.filter(tender_id=tender_id, is_deleted=False).select_related('tender', 'project', 'customer')