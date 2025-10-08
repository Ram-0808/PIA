from django.utils import timezone
from rest_framework import serializers

from Core.Core.serializers.ModelSerializers import ModelSerializerPermissionMixin
from Core.Users.models import AuthorizationDefinition
from django.contrib.contenttypes.models import ContentType

from .models import  Project, ProjectDueDateDocument,ProjectItem, ProjectDocuments , PerformanceBankGuarantee,  ProjectGroup, ProjectGroupUser, Stock, PerformanceBankGuaranteeHistory

from Users.serializers import *
from Masters.serializers import *
from TenderManagement.serializers import *
from decimal import Decimal




class ProjectMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'name', 'company','created_on',]




class ProjectItemSerializer(ModelSerializerPermissionMixin):
    id = serializers.UUIDField(required=False)

    tenderitemmaster = ItemMiniSerializer(many=False, read_only=True)
    tenderitemmaster_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tenderitemmaster', queryset=Item.objects.filter(is_deleted=False))

    tax = TaxSerializer(many=False, read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="tax", queryset=Tax.objects.filter(is_deleted=False)
    )

    taxtype = serializers.ChoiceField(choices=Project.TAXTYPE_CHOICES)
    taxtype_name = serializers.SerializerMethodField()
    # tender_item = TenderItemSerializer(many=False, read_only=True)
    # tender_item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender_item', queryset=TenderItem.objects.filter(is_deleted=False))

    dodelete = serializers.BooleanField(write_only=True, required=False, default=False)

    def get_taxtype_name(self, obj):
        return obj.get_taxtype_display()


    class Meta:
        model = ProjectItem
        list_serializer_class = FilteredListSerializer
        data_validate_fields = ['tenderitemmaster_id',]
        read_only_fields = ['id', 'code', 'created_on', 'project']
        fields = ['id', 'project', 'tenderitemmaster', 'tenderitemmaster_id', 'tax', 'tax_id', 'taxtype', 'taxtype_name', 'quantity', 'price', 'discount', 'dodelete', 'created_on']


class ProjectSerializer(ModelSerializerPermissionMixin):

    project_items =  ProjectItemSerializer(many =True, required=False)

    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', required=False, queryset=Tender.objects.filter(is_deleted=False))

    company = CompanyMiniSerializer(many=False, read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(write_only=True, source='company', queryset=Company.objects.filter(is_deleted=False))

    location = LocationMiniSerializer(many=False, read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(write_only=True, source='location', queryset=Location.objects.filter(is_deleted=False))

    customer = AccountMiniSerializer(many=False, read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, source='customer', queryset=Account.objects.filter(is_deleted=False, account_type = Account.CUSTOMER))
 
    order_placing_authority = AccountMiniSerializer(many=False, read_only=True)
    order_placing_authority_id = serializers.PrimaryKeyRelatedField(write_only=True, required=False, source='order_placing_authority', queryset=Account.objects.filter(is_deleted=False, account_type = Account.CUSTOMER))

    inspection_agency = InspectionAgencySerializer(many=False, read_only=True)
    inspection_agency_id = serializers.PrimaryKeyRelatedField(write_only=True, required=False, source='inspection_agency', queryset=InspectionAgency.objects.filter(is_deleted=False))

    manager = UserMiniSerializer(many=False, read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(write_only=True, source='manager', queryset=User.objects.filter(is_active=True,))

    tender_open_datetime = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)
    tender_due_datetime = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)
    tender_datetime = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)
    
    start_date = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)
    due_date = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)

    tender_type = serializers.ChoiceField(choices=Tender.TENDERTYPE_CHOICES)
    tender_type_name = serializers.SerializerMethodField()
    product_type = serializers.ChoiceField(choices=Tender.TENDERTYPE_CHOICES)
    product_type_name = serializers.SerializerMethodField()

    sourceportal = SourcePortalMiniSerializer(many=False, read_only=True)
    sourceportal_id = serializers.PrimaryKeyRelatedField(write_only=True, source='sourceportal', queryset=SourcePortal.objects.filter(is_deleted=False))


    status = serializers.ChoiceField(choices=Project.STATUS_CHOICES, required = False)
    status_name = serializers.SerializerMethodField()

    documents = serializers.SerializerMethodField()
    due_date_documents = serializers.SerializerMethodField()

    tax = TaxSerializer(many=False, read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="tax", required=False, queryset=Tax.objects.filter(is_deleted=False)
    )

    taxtype = serializers.ChoiceField(choices=Project.TAXTYPE_CHOICES, required=False)
    taxtype_name = serializers.SerializerMethodField()

    created_by = UserRelatedField(user_field= 'created_by', read_only=True)
    
    current_authorized_by = UserRelatedField(user_field= 'current_authorized_by', read_only=True)

    def get_taxtype_name(self, obj):
        return obj.get_taxtype_display()
    

    def get_documents(self, obj):
        documents = ProjectDocuments.objects.filter(project = obj, is_deleted= False)
        serializer = ProjectDocumentsSerializer(instance = documents, many=True, context = self.context)

        return serializer.data
    
    def get_due_date_documents(self, obj):
        documents = ProjectDueDateDocument.objects.filter(project = obj, is_deleted= False)
        serializer = ProjectDueDateDocumentSerializer(instance = documents, many=True, context = self.context)

        return serializer.data
    

    team = serializers.SerializerMethodField()

    def get_team(self, obj):
        users = ProjectGroupUser.objects.filter(group__project=obj, is_deleted=False)
        serializer = ProjectGroupUserSerializer(instance=users, many=True)
        return serializer.data


    def get_tender_type_name(self, obj):
        return obj.get_tender_type_display()

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_product_type_name(self, obj):
        return obj.get_product_type_display()
    
    authorized_status = serializers.ChoiceField(choices=Project.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()
    
    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], read_only=True)


  

    class Meta:
        model = Project
        data_validate_fields = ['company_id','sourceportal_id','tender_id', 'customer_id']
        read_only_fields = ['id', 'code', 'created_on', 'documents','team','gst_percentage','created_by','authorized_status','authorized_status_name','current_authorized_level','current_authorized_by','current_authorized_on']
        fields = ['id','code','name', 'project_no',  'project_items', 'amount','tender','tender_id','tender_no',
                  'company','company_id','location','location_id','sourceportal','sourceportal_id','manager','manager_id','tender_datetime','deliver_terms',
                  'financial_terms','tender_type', 'tender_type_name', 'status', 'status_name', 'product_type', 'product_type_name', 
                  'documents', 'team', 'created_on', 'due_date_documents', 'department_name','tender_due_datetime','tender_open_datetime','remarks',
                  'start_date', 'due_date', 'total_value', 'gst_percentage', 'taxable_amount', 'tax', 'tax_id', 'taxtype', 'taxtype_name', 'taxamount', 
                  'warrenty_period', 'customer', 'customer_id', 'order_placing_authority','order_placing_authority_id', 'is_performace_bank_guarantee',
                  'is_pre_dispatch_inspection', 'is_inspection_agency', 'is_stagewise_inspection', 'inspection_agency', 'inspection_agency_id', 'delivery_in_lots','authorized_status','authorized_status_name','current_authorized_level','current_authorized_by','current_authorized_on','created_by'
                  ]
        

    def validate(self, data):
        if data.get('is_inspection_agency') and not data.get('inspection_agency'):
            raise serializers.ValidationError({"inspection_agency": "Inspection Agency is required when is_inspection_agency is True."})

       
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user

        tender = validated_data.get('tender')

        project_ct = ContentType.objects.get_for_model(Project)

        authrizationdef_obj = AuthorizationDefinition.objects.filter(screen=project_ct, is_deleted = False).first()

        if authrizationdef_obj:
            validated_data['authorized_status'] = Project.PENDING
        else:
            validated_data['authorized_status'] = Project.SKIPPED

        project_items_data = validated_data.pop('project_items', [])
        tax = validated_data.get('tax', None)
        taxtype = validated_data.get('taxtype', None)
        amount = validated_data.get('amount')
        gst_percentage = validated_data.get('gst_percentage', 0)
        project_instance = super().create(validated_data)
        project_instance.created_on = timezone.now()

        total_price = 0.00
        tax_amount = 0.00

        try:
            try:
                if taxtype == 2:
                    tax_amount = (amount * tax.tax) / 100
                    total_price = tax_amount
            except:
                total_price = 0.00

            try:
                if gst_percentage:
                    gst_amount = (amount * gst_percentage) / 100
            except:
                gst_amount = 0.00

            taxamount = total_price if total_price else 0.00
            total_value = (amount + Decimal(taxamount) + Decimal(gst_amount))

            project_instance.taxamount = taxamount
            project_instance.total_value = total_value
        except:
            pass

        if tender:
            project_instance.department_name = tender.department_name
            project_instance.tender_no = tender.tender_no
            project_instance.tender_due_datetime = tender.tender_datetime
            project_instance.status = Project.PROJECT
            project_instance.save()

            tender.status = Tender.CONVERTEDTOPROJECT
            tender.save()

            # tender_items = TenderItem.objects.filter(tender=tender)
            # for item in tender_items:
            #     ProjectItem.objects.create(
            #         project=project_instance,
            #         tenderitemmaster=item.tenderitemmaster,
            #         quantity=item.quantity
            #     )

        for item_data in project_items_data:

            ProjectItem.objects.create(
                project=project_instance,
                tenderitemmaster=item_data['tenderitemmaster'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                tax=item_data['tax'],
                taxtype=item_data['taxtype'],
                discount=item_data['discount']
            )

            

            try:
                quantity=item_data['quantity']
                price=item_data['price']
                tax=item_data['tax']
                taxtype=item_data['taxtype']
                discount=item_data['discount']

                if taxtype == 2:
                    tax_amount = ((price * quantity)-discount) * tax.tax / 100
                    total_price = tax_amount
                    

                elif taxtype == 1:
                    amount_decimal = Decimal(price) * quantity
                    tax_rate_decimal = Decimal(tax.tax)

                    basicValue = amount_decimal/ (Decimal(1) + tax_rate_decimal / Decimal(100))

                    tax_amount = basicValue * (tax_rate_decimal / Decimal(100))

                    total_price = amount_decimal

            except Exception as e:
                total_price = Decimal("0.00")
                tax_amount = Decimal("0.00")

            total_price += item_data['price']
            tax_amount += item_data['price']

        project_instance.total_value = total_price + project_instance.taxable_amount
        project_instance.taxamount = tax_amount
        project_instance.status = Project.PROJECT
        project_instance.save()

        return project_instance


    def update(self, instance, validated_data):

        user = self.context['request'].user

        instance.name = validated_data.get('name', instance.name)
        instance.project_no = validated_data.get('project_no', instance.project_no)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.deliver_terms = validated_data.get('deliver_terms', instance.deliver_terms)
        instance.financial_terms = validated_data.get('financial_terms', instance.financial_terms)
        instance.department_name = validated_data.get('department_name', instance.department_name)
        instance.tender_due_datetime = validated_data.get('tender_due_datetime', instance.tender_due_datetime)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.status = Project.PROJECT
        instance.is_stagewise_inspection = validated_data.get('is_stagewise_inspection',instance.is_stagewise_inspection)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.gst_percentage = validated_data.get('gst_percentage', instance.gst_percentage)
        instance.tax = validated_data.get('tax', instance.tax)
        instance.taxtype = validated_data.get('taxtype', instance.taxtype)
        instance.taxable_amount = validated_data.get('taxable_amount', instance.taxable_amount)
        instance.warrenty_period = validated_data.get('warrenty_period', instance.warrenty_period)
        instance.tender = validated_data.get('tender', instance.tender)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.is_performace_bank_guarantee = validated_data.get('is_performace_bank_guarantee', instance.is_performace_bank_guarantee)
        instance.is_pre_dispatch_inspection = validated_data.get('is_pre_dispatch_inspection', instance.is_pre_dispatch_inspection)
        instance.is_inspection_agency = validated_data.get('is_inspection_agency', instance.is_inspection_agency)
        instance.inspection_agency = validated_data.get('inspection_agency', instance.inspection_agency)
        instance.delivery_in_lots = validated_data.get('delivery_in_lots', instance.delivery_in_lots)
        instance.sourceportal = validated_data.get('sourceportal', instance.sourceportal)
        instance.company = validated_data.get('company', instance.company)
        instance.manager = validated_data.get('manager', instance.manager)
        instance.save()

        if instance.tender:
            instance.tender.status = Tender.CONVERTEDTOPROJECT
            instance.tender.save()

        total = Decimal(0)
        total_tax_amount = Decimal(0)

        

        if instance.tender:
            tender_items = TenderItem.objects.filter(tender=instance.tender)
            for item in tender_items:
                # Check if there's an existing ProjectItem with the same project and tenderitemmaster
                existing_items = ProjectItem.objects.filter(project=instance, tenderitemmaster=item.tenderitemmaster)
                
                if existing_items.exists():
                    existing_item = existing_items.first()
                    existing_item.quantity = item.quantity
                    
                    existing_item.save()
                else:
                    pro_item_obj = ProjectItem.objects.create(
                        project=instance,
                        tenderitemmaster=item.tenderitemmaster,
                        quantity=item.quantity
                       
                    )
                    
        if 'project_items' in validated_data:
            project_items_data = validated_data.pop('project_items')
            for item_data in project_items_data:
                item_id = item_data.get('id', None)
                dodelete = item_data.pop('dodelete', None)
                if dodelete and item_id:
                    ProjectItem.objects.filter(id=item_id).update(is_deleted=True)
                    continue                

                quantity = item_data.get('quantity', None)
                taxtype = item_data.get('taxtype', None)
                tax = item_data.get('tax', None)
                price = item_data.get('price', None)
                discount = item_data.get('discount', None)
                quantity = item_data.get('quantity', None)

                try:
                    if taxtype == 2:
                        tax_amount = ((price * quantity)-discount) * tax.tax / 100
                        total_price = tax_amount
                        

                    elif taxtype == 1:
                        amount_decimal = Decimal(price) * quantity
                        tax_rate_decimal = Decimal(tax.tax)

                        basicValue = amount_decimal/ (Decimal(1) + tax_rate_decimal / Decimal(100))

                        tax_amount = basicValue * (tax_rate_decimal / Decimal(100))

                        total_price = amount_decimal
                    else:
                        tax_amount = Decimal("0.00")
                        total_price = Decimal("0.00")

                except Exception as e:
                    total_price = Decimal("0.00")
                    tax_amount = Decimal("0.00")

                if item_id:
                    # Update existing ProjectItem if item_id is provided
                    item_instance = ProjectItem.objects.get(id=item_id)
                    item_instance.quantity = item_data.get('quantity', item_instance.quantity)
                    item_instance.price = item_data.get('price', item_instance.price)
                    item_instance.tax = item_data.get('tax', item_instance.tax)
                    item_instance.taxtype = item_data.get('taxtype', item_instance.taxtype)
                    item_instance.discount = item_data.get('discount', item_instance.discount)
                    item_instance.discount = item_data.get('discount', item_instance.discount)
                    item_instance.save()
                    
                else:
                    ProjectItem.objects.create(project=instance, **item_data)

                total += total_price
                total_tax_amount += tax_amount

        instance.taxamount = tax_amount if tax_amount else 0.00
        instance.total_value = total + total_tax_amount + instance.taxable_amount# (instance.amount + Decimal(instance.taxamount) + Decimal(gst_amount))
        instance.save()

        return instance


class ProjectMiniSerializer(serializers.ModelSerializer):
    company = CompanyMiniSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'company','created_on', 'code', 'company']


class ProjectUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        read_only_fields = ['id', 'code',]
        fields = ['id', 'code', 'department_name','tender_due_datetime','remarks','created_on',]


class ProjectDocumentsSerializer(serializers.ModelSerializer):
    
    project = ProjectMiniSerializer(many = False,read_only = True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project', queryset=Project.objects.filter(is_deleted = False,))

    class Meta:
        model = ProjectDocuments
        fields = ('id', 'project', 'project_id', 'file','created_on',)

    def create(self, validated_data):

        project = validated_data.get('project')
        file = validated_data.get('file')

        project_document = ProjectDocuments.objects.create(
            project=project,
            file=file
        )

        return project_document



class ProjectDueDateDocumentSerializer(serializers.ModelSerializer):
    
    project = ProjectMiniSerializer(many = False,read_only = True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project', queryset=Project.objects.filter(is_deleted = False,))

    extended_due_date = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'])


    class Meta:
        model = ProjectDueDateDocument
        read_only_fields = ['id', 'code',]
        fields = ('id', 'code', 'project', 'project_id', 'extended_due_date', 'file','created_on',)

    def create(self, validated_data):

        project = validated_data.get('project')
        file = validated_data.get('file')
        extended_due_date = validated_data.get('extended_due_date')

        project_document = ProjectDueDateDocument.objects.create(
            project=project,
            extended_due_date=extended_due_date,
            file=file
        )

        return project_document



class ProjectGroupSerializer(serializers.ModelSerializer):
    project = ProjectMiniSerializer(many=False, read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        write_only=True, 
        source='project',
        queryset=Project.objects.filter(is_deleted=False),
    )


    class Meta:
        model = ProjectGroup
        read_only_fields = ['id', 'code', ]
        fields = ['id', 'code', 'project', 'project_id', 'name','created_on',]

class ProjectGroupMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectGroup
        read_only_fields = ['id', 'code', ]
        fields = ['id', 'code', 'name']



class ProjectGroupUserSerializer(serializers.ModelSerializer):
    group = ProjectGroupSerializer(many=False, read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        write_only=True, 
        source='group',
        queryset=ProjectGroup.objects.filter(is_deleted=False),
    )

    user = UserMiniSerializer(many=False, read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True, 
        source='user',
        queryset=User.objects.filter(is_active=True,)
    )

    class Meta:
        model = ProjectGroupUser
        read_only_fields = ['id', 'code',]
        fields = ['id', 'code', 'group', 'group_id', 'user', 'user_id','created_on',]



class ProjectGroupUserMiniSerializer(serializers.ModelSerializer):
    group = ProjectGroupMiniSerializer(many=False, read_only=True)
    user = UserMiniSerializer(many=False, read_only=True)

    class Meta:
        model = ProjectGroupUser
        read_only_fields = ['id', 'code',]
        fields = ['id', 'code', 'group', 'user', ]


class PerformanceBankGuaranteeSerializer(serializers.ModelSerializer):
    project = ProjectMiniSerializer(many=False, read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project', queryset=Project.objects.filter(is_deleted=False))

    authorized_status = serializers.ChoiceField(choices=Lead.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    current_authorized_status = serializers.ChoiceField(choices=Lead.AUTHORIZED_STATUS_CHOICES, required=False)
    current_authorized_status_name = serializers.SerializerMethodField()

    current_authorized_by = UserRelatedField(user_field= 'current_authorized_by', read_only=True)
    authorized_by = UserRelatedField(user_field= 'authorized_by', read_only=True)

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()

    def get_current_authorized_status_name(self, obj):
        return obj.get_current_authorized_status_display()


    class Meta:
        model = PerformanceBankGuarantee
        read_only_fields = ['code', 'created_on', 'modified_on', 'authorized_status', 'authorized_status_name','current_authorized_level', 'current_authorized_by','current_authorized_on', 'current_authorized_status', 'current_authorized_status_name','authorized_by']
        fields = (
            'id', 'code', 'project', 'project_id' , 'number', 'value', 'issuedate', 
            'expirydate', 'claimdate', 'remarks', 'file', 'authorized_status', 'authorized_status_name','current_authorized_level', 'current_authorized_by','current_authorized_on', 'current_authorized_status', 'current_authorized_status_name','authorized_by','created_on', 'modified_on'
        )


class PerformanceBankGuaranteeMiniSerializer(serializers.ModelSerializer):
    authorized_status = serializers.ChoiceField(choices=Lead.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    current_authorized_status = serializers.ChoiceField(choices=Lead.AUTHORIZED_STATUS_CHOICES, required=False)
    current_authorized_status_name = serializers.SerializerMethodField()

    current_authorized_by = UserRelatedField(user_field= 'current_authorized_by', read_only=True)
    
    authorized_by = UserRelatedField(user_field= 'authorized_by', read_only=True)

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()

    def get_current_authorized_status_name(self, obj):
        return obj.get_current_authorized_status_display()
    
    class Meta:
        model = PerformanceBankGuarantee
        fields = ('id', 'code', 'number', 'value', 'authorized_status', 'authorized_status_name','current_authorized_level', 'current_authorized_by','current_authorized_on', 'current_authorized_status', 'current_authorized_status_name','authorized_by')



class PBGExtendedUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PerformanceBankGuarantee
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = (
            'id', 'code','issuedate', 'expirydate', 'claimdate', 'remarks', 'file', 'created_on', 'modified_on'
        )

    def update(self, instance, validated_data):

        instance.issuedate = validated_data.get('issuedate', instance.issuedate)
        instance.expirydate = validated_data.get('expirydate', instance.expirydate)
        instance.claimdate = validated_data.get('claimdate', instance.claimdate)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.file = validated_data.get('file', instance.file)
        instance.save()
        PerformanceBankGuaranteeHistory.objects.create(
            pbg=instance,
            project=instance.project,
            issuedate=instance.issuedate,
            expirydate=instance.expirydate,
            claimdate=instance.claimdate,
            remarks=instance.remarks,
            file=instance.file
        )
        
        return super().update(instance, validated_data)


class PerformanceBankGuaranteeHistorySerializer(serializers.ModelSerializer):
    project = ProjectMiniSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='project',
        queryset=Project.objects.filter(is_deleted=False)
    )

    class Meta:
        model = PerformanceBankGuaranteeHistory
        read_only_fields = ['id', 'code', 'created_on', 'modified_on']
        fields = (
            'id', 'code', 'project', 'project_id',
            'issuedate', 'expirydate', 'claimdate',
            'remarks', 'file', 'created_on', 'modified_on'
        )


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['code', 'date', 'doc_code', 'screen_name', 'project', 'warehouse', 'item', 'batch', 'quantity']


class StockWithoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['code', 'date', 'screen_name', 'project', 'warehouse', 'item', 'quantity']


class StockAgainstBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['item', 'batch', 'quantity']

        
        