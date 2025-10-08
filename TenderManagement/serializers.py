import json
from django.utils import timezone
from decimal import Decimal
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.apps import apps as django_apps


from Core.Core.serializers.ModelSerializers import ModelSerializerPermissionMixin
from Core.Users.models import Assignee, AuthorizationDefinition
from ProjectManagement.models import ProjectDocuments, ProjectItem
from LeadManagement.serializers import LeadMiniSerializer2



from .models import BudgetEnquiry,  Consumable, CostingSheet, OtherCharges, PlazoTender, PlazoTenderAttachment, PlazoTenderItem, RawMaterial, Service, TenderAttachments, TenderItemAssign, TenderItemMaster, TenderItemMasterItem, Item, Tender, TenderItem,  TenderComments, Lead, CaseSheet, ReverseAuction, TenderDocuments , BidAmount , PDFExtraction, TenderCheckListItems, SecurityDeposit, Order


from ProjectManagement.models import Project

from Users.serializers import *
from Masters.serializers import *
from Masters.models import TenderCheckList

from decimal import Decimal

from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers
from BOQ.services import create_boq_from_tender

class ProjectMini3Serializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'name', 'company']

class FilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if hasattr(data, 'filter'):
            data = data.filter(is_deleted=False)
        else:
            data = [item for item in data if not getattr(item, 'is_deleted', False)]
        return super().to_representation(data)

class TenderItemMasterItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    item = ItemSerializer(many=False, read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='item', queryset=Item.objects.filter(is_deleted=False))
    dodelete = serializers.BooleanField(write_only=True, required=False)
    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], read_only=True)
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    class Meta:
        model = TenderItemMasterItem
        list_serializer_class = FilteredListSerializer
        read_only_fields = ['id', 'code', 'created_on', 'tenderitemmaster', 'created_by']
        fields = ['id', 'tenderitemmaster', 'item', 'item_id', 'quantity', 'dodelete', 'created_on', 'created_by']

class TenderItemMasterSerializer(serializers.ModelSerializer):
    tendermasteritems = TenderItemMasterItemSerializer(many=True, required=False)
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    class Meta:
        model = TenderItemMaster
        fields = ['id', 'name', 'tendermasteritems', 'created_on', 'created_by']

    def create(self, validated_data):
        items_data = validated_data.pop('tendermasteritems', [])
        tenderitemmaster = TenderItemMaster.objects.create(**validated_data)
        
        for item_data in items_data:
            dodelete = item_data.pop('dodelete', None)
            if not dodelete:
                item = item_data.pop('item')
                quantity = item_data.get('quantity', 1)
                TenderItemMasterItem.objects.create(tenderitemmaster=tenderitemmaster, item=item, quantity=quantity)

        return tenderitemmaster

    def update(self, instance, validated_data):
        items_data = validated_data.pop('tendermasteritems', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Update or create items
        existing_items = {item.id: item for item in instance.tendermasteritems.all()}
        for item_data in items_data:
            item_id = item_data.get('id', None)
            dodelete = item_data.pop('dodelete', None)

            if item_id and item_id in existing_items:
                # Update or delete existing item
                existing_item = existing_items.pop(item_id)
                if dodelete:
                    existing_item.is_deleted = True,
                    existing_item.save()

                else:
                    existing_item.item = item_data.get('item', existing_item.item)
                    existing_item.quantity = item_data.get('quantity', existing_item.quantity)
                    existing_item.save()
            else:
                # Create new item if not marked for deletion
                if not dodelete:
                    item = item_data.pop('item')
                    quantity = item_data.get('quantity', 1)
                    TenderItemMasterItem.objects.create(tenderitemmaster=instance, item=item, quantity=quantity)

        return instance
    


class TenderItemMasterMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenderItemMaster
        fields = ['id', 'name',]



class TenderMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tender
        fields = ['id','code', 'name','tender_no','product_type', ]


class TenderItemAssign1Serializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = TenderItemAssign
        fields = ['id', 'user']


class TenderCheckListItemsSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    tender_checklist = TenderCheckListMiniSerializer(many=False, read_only=True)
    tender = TenderMiniSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False), required= False)
    created_by = UserRelatedField(user_field='created_by', read_only=True)

    class Meta:
        model = TenderCheckListItems
        list_serializer_class = FilteredListSerializer
        read_only_fields = ['id', 'code', 'created_on', 'tender', 'created_by']
        fields = ['id', 'name','tender', 'tender_id', 'tender_checklist', 'tender_condition', 'deviation_from_pia_norms', 'pia_remarks', 'cost_implication', 'created_on', 'created_by']


class TenderItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    tenderitemmaster = ItemMiniSerializer(many=False, read_only=True)
    tenderitemmaster_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tenderitemmaster', queryset=Item.objects.filter(product_type = Item.PRODUCT,is_deleted=False))

    
    unit = UnitMiniSerializer(many=False, read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(write_only=True, source='unit',required = False, queryset=Unit.objects.filter(is_deleted=False))

    dodelete = serializers.BooleanField(write_only=True, required=False, default=False)
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    assignes = TenderItemAssign1Serializer(source='tender_items_assign', many=True, read_only=True)

    def validate(self, data):
        item = data.get('item')
        unit = data.get('unit')
        
        if item and unit:
            if not Unit.objects.filter(id=unit.id, item=item, is_deleted=False).exists():
                raise serializers.ValidationError(
                    {"unit_id": "The selected unit is not valid for the specified item."}
                )
            
        return super().validate(data)

    class Meta:
        model = TenderItem
        list_serializer_class = FilteredListSerializer
        read_only_fields = ['id', 'code', 'created_on', 'tender', 'created_by']
        fields = ['id', 'tender', 'tenderitemmaster', 'tenderitemmaster_id', 'is_rfq_required','unit', 'unit_id','item_specifications','quantity', 'dodelete', 'created_on', 'created_by', 'assignes']


class TenderStageSerializer(serializers.ModelSerializer):
    tender_stage = StageSerializer(many=False, read_only=True)
    tender_stage_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender_stage', queryset=Stage.objects.filter(is_deleted=False))


    class Meta:
        model = Tender
        # list_serializer_class = FilteredListSerializer
        # read_only_fields = ['id', 'code', 'created_on', 'tender']
        fields = ['id',  'tender_stage', 'tender_stage_id','created_on', ]





class TenderSerializer(ModelSerializerPermissionMixin):
    tender_items = TenderItemSerializer(many=True)
    tender_checklist_items = TenderCheckListItemsSerializer(many=True, required=False)
    tender_stage = StageSerializer(many=False, read_only=True)

    lead = LeadMiniSerializer2(many=False, read_only=True)
    lead_id = serializers.PrimaryKeyRelatedField(write_only=True, source='lead',required = False, queryset=Lead.objects.filter(is_deleted=False, authorized_status__in = [Lead.APPROVED, Lead.SKIPPED]))

    project = ProjectMini3Serializer(many=False, read_only=True)

    sourceportal = SourcePortalMiniSerializer(many=False, read_only=True)
    sourceportal_id = serializers.PrimaryKeyRelatedField(write_only=True, source='sourceportal',required =False, queryset=SourcePortal.objects.filter(is_deleted=False))

    company = CompanyMiniSerializer(many=False, read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(write_only=True, source='company', required =False, queryset=Company.objects.filter(is_deleted=False))

    location = LocationMiniSerializer(many=False, read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(write_only=True, source='location', required =False, queryset=Location.objects.filter(is_deleted=False))

    customer = AccountMiniSerializer(many=False, read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, source='customer', required= False, queryset=Account.objects.filter(is_deleted=False, account_type = Account.CUSTOMER))

    order_placing_authority = AccountMiniSerializer(many=False, read_only=True)
    order_placing_authority_id = serializers.PrimaryKeyRelatedField(write_only=True, required=False, source='order_placing_authority', queryset=Account.objects.filter(is_deleted=False, account_type = Account.CUSTOMER))

    tender_datetime = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)

    tender_open_datetime = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)

    tender_extension_datetime = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required=False)
    # pre_bid_date = serializers.DateTimeField(format='%Y-%m-%d %I:%M %p', input_formats=['%Y-%m-%d %I:%M %p'],required=False)

    tender_type = serializers.ChoiceField(choices=Tender.TENDERTYPE_CHOICES, required = False)
    tender_type_name = serializers.SerializerMethodField()
    
    product_type = serializers.ChoiceField(choices=Tender.PRODUCTTYPE_CHOICES)
    product_type_name = serializers.SerializerMethodField()

    authorized_status = serializers.ChoiceField(choices=Tender.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    screen_type = serializers.ChoiceField(choices=[Tender.TENDER, Tender.BUDGETENQUIRY], required=False)

    current_authorized_by = UserRelatedField(user_field= 'current_authorized_by', read_only=True)

    comments = serializers.SerializerMethodField()

    documents = serializers.SerializerMethodField()
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    def get_documents(self, obj):
        documents = TenderAttachments.objects.filter(tender = obj, is_deleted= False)
        serializer = TenderAttachmentsSerializer(instance = documents, many=True, context = self.context)

        return serializer.data
    

    def get_comments(self, obj):
        comments = TenderComments.objects.filter(tender=obj, is_deleted=False)
        serializer = TenderCommentSerializer(instance=comments, many=True, context=self.context)
        return serializer.data

    def get_tender_type_name(self, obj):
        return obj.get_tender_type_display()

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()

    def get_product_type_name(self, obj):
        return obj.get_product_type_display()

    class Meta:
        model = Tender
        # data_validate_fields = ['customer_id','lead_id']
        read_only_fields = ['id', 'code', 'created_on',  'assigned_on','authorized_status', 'authorized_status_name', 'created_by','current_authorized_level','current_authorized_by','current_authorized_on' ]
        fields = ['id','code', 'name', 'assigned_on', 'project', 'is_lead_required', 'lead', 'lead_id', 'tender_no', 'tender_type', 'tender_type_name', 'tender_stage', 'authorized_status', 'authorized_status_name', 'product_type', 'product_type_name', 'department_name',  'company', 'company_id', 'location', 'location_id',  'customer', 'customer_id','documents', 'tender_datetime', 'tender_items', 'tender_checklist_items', 'comments', 'is_reverse_auction','pre_bid_place','pre_bid_meet_address', 'tender_extension_datetime', 'tender_open_datetime','pre_bid_date','ministry','annual_turnover','years_of_experiance','is_mss_exemption','is_start_exemption','documents_required_seller','time_allowed_clarification_days','is_inspection','evaluation_method','description','sourceportal','sourceportal_id', 'screen_type', 'is_order_placing_authority', 'order_placing_authority', 'order_placing_authority_id', 'created_by','created_on','current_authorized_level','current_authorized_by','current_authorized_on' ] # 'project_id',


    def create(self, validated_data):
        items_data = validated_data.pop('tender_items', [])
        checklist_items_data = validated_data.pop('tender_checklist_items', [])

        tender_ct = ContentType.objects.get_for_model(
            Tender if validated_data['screen_type'] == 1 else BudgetEnquiry
        )

        authrizationdef_obj = AuthorizationDefinition.objects.filter(
            screen=tender_ct, is_deleted=False
        ).first()

        if authrizationdef_obj:
            validated_data['authorized_status'] = Tender.PENDING
        else:
            validated_data['authorized_status'] = Tender.SKIPPED

        tender = Tender.objects.create(**validated_data)

        project = Project.objects.create(
            name=tender.code,
            tender_no=tender.tender_no,
            status=Project.TENDER,
            tender=tender,
            tender_type=tender.tender_type,
            product_type=tender.product_type,
            sourceportal=tender.sourceportal,
            customer=tender.customer,
            order_placing_authority=tender.order_placing_authority,
            company=tender.company,
            location=tender.location,
            department_name=tender.department_name,
            tender_due_datetime=tender.tender_datetime,
        )

        for item_data in items_data:
            item_data.pop('id', None)
            dodelete = item_data.pop('dodelete', None)

            if not dodelete:
                tender_item = TenderItem.objects.create(tender=tender, **item_data)

                ProjectItem.objects.create(
                    project=project,
                    tenderitemmaster=item_data['tenderitemmaster'],
                    quantity=item_data['quantity']
                )

                if tender.lead:
                    lead_ct = ContentType.objects.get_for_model(Lead)
                    assignees = Assignee.objects.filter(
                        screen=lead_ct,
                        instance_id=str(tender.lead.id),
                        user_identifier__isnull=False,
                        user_type__isnull=False,
                    )
                    for assignee in assignees:
                        user_model = django_apps.get_model(lead_ct, require_ready=False)

                        user = user_model.objects.filter(id=assignee.user_identifier).first()
                        TenderItemAssign.objects.create(
                            tender=tender,
                            tender_item=tender_item,
                            tenderitemmaster=tender_item.tenderitemmaster,
                            user=user
                        )

        # Create TenderCheckListItems
        for checklist_item_data in checklist_items_data:
            checklist_item_data.pop('id', None)
            dodelete = checklist_item_data.pop('dodelete', None)
            
            if not dodelete:
                TenderCheckListItems.objects.create(tender=tender, **checklist_item_data)

        try:
            checklists = TenderCheckList.objects.filter(is_deleted=False, is_active=True)
            for checklist in checklists:
                TenderCheckListItems.objects.create(tender=tender, tender_checklist=checklist, name=checklist.name)
        except Exception as e:
            print(f"Error creating TenderCheckListItems: {e}")

        try:
            project.tender_open_datetime = tender.tender_open_datetime
            project.tender_datetime = tender.tender_datetime
            project.save()
        except:
            pass

        tender.project = project
        tender.save()
        
        # Mark lead as converted based on screen_type
        if tender.lead:
            if tender.screen_type == Tender.BUDGETENQUIRY:
                tender.lead.is_converted_to_budget_enquiry = True
                tender.lead.save(update_fields=['is_converted_to_budget_enquiry'])
            elif tender.screen_type == Tender.TENDER:
                tender.lead.is_converted_to_tender = True
                tender.lead.save(update_fields=['is_converted_to_tender'])

        if tender.lead:
            # Get ContentType for Lead model
            lead_ct = ContentType.objects.get_for_model(Lead)

            screen_type_model_map = {
                Tender.TENDER: Tender,
                Tender.BUDGETENQUIRY: BudgetEnquiry,
                Tender.PLAZOTENDER: PlazoTender,
            }

            target_model = screen_type_model_map.get(tender.screen_type)
            
            if not target_model:
                raise ValueError(f"Invalid screen_type: {tender.screen_type}")

            target_ct = ContentType.objects.get_for_model(target_model)

            lead_assignees = Assignee.objects.filter(
                screen=lead_ct,
                instance_id=str(tender.lead.id),
                user_identifier__isnull=False,
                user_type__isnull=False,
            )

            for lead_assignee in lead_assignees:
                user_model = django_apps.get_model(lead_ct, require_ready=False)

                user = user_model.objects.filter(id=lead_assignee.user_identifier).first()
                Assignee.objects.get_or_create(
                    screen=target_ct,
                    instance_id=str(tender.id),
                    user_identifier=lead_assignee.user_identifier,
                    user_type=lead_assignee.user_type,
                    defaults={
                        "description": lead_assignee.description or ""
                    }
                )
        boq = create_boq_from_tender(tender)
        print(f"BOQ created: {boq}")
        return tender


    def update(self, instance, validated_data):
        print("Updating Tender instance...")
        request = self.context.get('request')
        requestuser = request.user
        print(f"Request user: {requestuser}")

        items_data = validated_data.pop('tender_items', [])
        checklist_items_data = validated_data.pop('tender_checklist_items', [])
        print(f"Received {len(items_data)} items for update.")
        print(f"Received {len(checklist_items_data)} checklist items for update.")

        # Update tender fields
        for field in [
            'tender_no', 'customer', 'location', 'order_placing_authority',
            'tender_type', 'product_type', 'sourceportal',
            'department_name', 'tender_datetime', 'tender_open_datetime'
        ]:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        instance.save()
        print("Tender instance updated.")

        # Project creation or update
        project, created = Project.objects.get_or_create(
            tender=instance,
            defaults={
                "name": instance.code,
                "tender_no": instance.tender_no,
                "status": Project.TENDER,
                "tender_type": instance.tender_type,
                "product_type": instance.product_type,
                "sourceportal": instance.sourceportal,
                "company": instance.company,
                "location": instance.location,
                "department_name": instance.department_name,
                "tender_due_datetime": instance.tender_datetime,
                "customer": instance.customer,
                "order_placing_authority": instance.order_placing_authority,
            }
        )

        if not created:
            print(f"Updating existing Project: {project.name}")
            for attr in [
                'name', 'tender_no', 'status', 'tender_type', 'product_type', 'sourceportal',
                'company', 'location', 'department_name', 'tender_datetime',
                'tender_open_datetime', 'customer', 'order_placing_authority'
            ]:
                setattr(project, attr, getattr(instance, attr))
            project.save()
        else:
            print(f"Created new Project: {project.name}")

        existing_item_ids = []

        for item_data in items_data:
            item_id = item_data.get('id')
            dodelete = item_data.pop('dodelete', False)

            if item_id:
                try:
                    item_instance = TenderItem.objects.get(id=item_id, tender=instance, is_deleted=False)
                    print(f"Updating TenderItem ID: {item_id}")
                except TenderItem.DoesNotExist:
                    print(f"Error: TenderItem ID {item_id} not found.")
                    raise serializers.ValidationError({"detail": f"TenderItem with id {item_id} does not exist."})

                if dodelete:
                    print(f"Marking TenderItem ID {item_id} as deleted.")
                    item_instance.is_deleted = True
                    item_instance.save()
                    continue

                item_instance.tenderitemmaster = item_data.get('tenderitemmaster', item_instance.tenderitemmaster)
                item_instance.quantity = item_data.get('quantity', item_instance.quantity)
                item_instance.item_specifications = item_data.get('item_specifications', item_instance.item_specifications)
                item_instance.is_rfq_required = item_data.get('is_rfq_required', item_instance.is_rfq_required)
                item_instance.save()
                print(f"Updated TenderItem ID {item_id}.")

                ProjectItem.objects.update_or_create(
                    project=project,
                    tenderitemmaster=item_data['tenderitemmaster'],
                    defaults={"quantity": item_data['quantity']}
                )
                print(f"Updated ProjectItem for TenderItem ID {item_id}.")

                existing_item_ids.append(item_id)

            else:
                if not dodelete:
                    print("Creating new TenderItem.")
                    new_tender_item = TenderItem.objects.create(tender=instance, **item_data)
                    print(f"Created TenderItem ID {new_tender_item.id}.")

                    ProjectItem.objects.create(
                        project=project,
                        tenderitemmaster=item_data['tenderitemmaster'],
                        quantity=item_data['quantity']
                    )
                    print(f"Created ProjectItem linked to TenderItem ID {new_tender_item.id}.")

                    # Assign users based on lead
                    if instance.lead:
                        from django.contrib.contenttypes.models import ContentType
                        lead_ct = ContentType.objects.get_for_model(Lead)
                        assignees = Assignee.objects.filter(
                            screen=lead_ct,
                            instance_id=str(instance.lead.id),
                            user__isnull=False
                        )

                        for assignee in assignees:
                            TenderItemAssign.objects.create(
                                tender=instance,
                                tender_item=new_tender_item,
                                tenderitemmaster=new_tender_item.tenderitemmaster,
                                user=assignee.user
                            )
                            print(f"Assigned TenderItem ID {new_tender_item.id} to user {assignee.user.username}")

        # Handle TenderCheckListItems update
        existing_checklist_item_ids = []
        
        for checklist_item_data in checklist_items_data:
            checklist_item_id = checklist_item_data.get('id')
            dodelete = checklist_item_data.pop('dodelete', False)
            
            if checklist_item_id:
                try:
                    checklist_item_instance = TenderCheckListItems.objects.get(id=checklist_item_id, tender=instance, is_deleted=False)
                    print(f"Updating TenderCheckListItems ID: {checklist_item_id}")
                except TenderCheckListItems.DoesNotExist:
                    print(f"Error: TenderCheckListItems ID {checklist_item_id} not found.")
                    raise serializers.ValidationError({"detail": f"TenderCheckListItems with id {checklist_item_id} does not exist."})
                
                if dodelete:
                    print(f"Marking TenderCheckListItems ID {checklist_item_id} as deleted.")
                    checklist_item_instance.is_deleted = True
                    checklist_item_instance.save()
                    continue
                
                checklist_item_instance.tender_checklist = checklist_item_data.get('tender_checklist', checklist_item_instance.tender_checklist)
                checklist_item_instance.tender_condition = checklist_item_data.get('tender_condition', checklist_item_instance.tender_condition)
                checklist_item_instance.deviation_from_pia_norms = checklist_item_data.get('deviation_from_pia_norms', checklist_item_instance.deviation_from_pia_norms)
                checklist_item_instance.pia_remarks = checklist_item_data.get('pia_remarks', checklist_item_instance.pia_remarks)
                checklist_item_instance.cost_implication = checklist_item_data.get('cost_implication', checklist_item_instance.cost_implication)
                checklist_item_instance.save()
                print(f"Updated TenderCheckListItems ID {checklist_item_id}.")
                
                existing_checklist_item_ids.append(checklist_item_id)
            
            else:
                if not dodelete:
                    print("Creating new TenderCheckListItems.")
                    new_checklist_item = TenderCheckListItems.objects.create(tender=instance, **checklist_item_data)
                    print(f"Created TenderCheckListItems ID {new_checklist_item.id}.")

        print("Update process completed.")
        return instance    
        


    

class TenderCommentSerializer(ModelSerializerPermissionMixin):

    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False,))

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], read_only=True)

    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    class Meta:
        model = TenderComments
        # data_validate_fields = ['tender_id']
        read_only_fields = ['id','code','created_by','created_on']
        fields = ('id',  'tender_id', 'comment', 'created_on','created_by' ) 




    
class TenderAttachmentsSerializer(ModelSerializerPermissionMixin):
    tender = TenderMiniSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    class Meta:
        model = TenderAttachments
        # data_validate_fields = ['tender_id']
        fields = ('id', 'created_on', 'tender', 'tender_id', 'file')

    def create(self, validated_data):
        ta_obj = TenderAttachments.objects.create(**validated_data)
        try:
            pa_obj = ProjectDocuments.objects.create(project=ta_obj.tender.project, file=ta_obj.file)
        except Exception as e:
            print('Failed to create ProjectDocuments: ', str(e))
        return ta_obj


    
class TenderItemAssignSerializer(ModelSerializerPermissionMixin):
    tender = TenderMiniSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    tender_item = TenderItemSerializer(many=False, read_only=True)
    tender_item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender_item', queryset=TenderItem.objects.filter(is_deleted=False))

    tenderitemmaster = ItemMiniSerializer(many=False, read_only=True)
    tenderitemmaster_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tenderitemmaster', queryset=Item.objects.filter(is_deleted=False))

    user = UserMiniSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(write_only=True, required =False,source="user", queryset=User.objects.filter(is_active=True))

    class Meta:
        model = TenderItemAssign
        fields = ('id', 'created_on', 'tender', 'tender_id','tender_item', 'tender_item_id','tenderitemmaster','tenderitemmaster_id', 'user', 'user_id', )

    def validate(self, attrs):
        tender_item = attrs.get('tender_item')
        user = attrs.get('user')

        queryset = TenderItemAssign.objects.filter(
            tender_item = tender_item, user=user, is_deleted = False
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["A record with this item and user combination already exists."]}
            )

        return super().validate(attrs)

    def create(self, validated_data):

        instance = TenderItemAssign.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CaseSheetSerializer(ModelSerializerPermissionMixin):
    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    authorized_status = serializers.ChoiceField(choices=CaseSheet.STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    current_authorized_by = UserRelatedField(user_field= 'current_authorized_by', read_only=True)


    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], read_only=True)

    pre_bid_date = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], required =False)
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()
    


    class Meta:
        model = CaseSheet
        # data_validate_fields = ['tender_id']
        read_only_fields = ['id', 'code', 'created_on','costing_remarks','remarks', 'authorized_status', 'authorized_status_name','created_by','current_authorized_level','current_authorized_by','current_authorized_on']
        fields = [
            'id', 'tender', 'tender_id', 'pre_bid_date', 'pre_bid_subject', 'contact_person','department_name', 'phone', 'email', 'authorized_status',
            'authorized_status_name', 'last_tender_rate', 'last_tender_date', 'estimate_bid_price', 'oem_challenges','is_reverse_auction','pendingdocumentsOEM','documents_not_submitted_evaluation_matrix',
            'department_challenges', 'is_extension_request', 'is_site_visit', 'costing_remarks', 'remarks','current_authorized_level','current_authorized_by','current_authorized_on', 'created_on','created_by'
        ]

    def create(self, validated_data):

        case_sheet = super().create(validated_data)

        return case_sheet


    def update(self, instance, validated_data):

        instance.pre_bid_date = validated_data.get('pre_bid_date', instance.pre_bid_date)
        instance.pre_bid_subject = validated_data.get('pre_bid_subject', instance.pre_bid_subject)
        instance.contact_person = validated_data.get('contact_person', instance.contact_person)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.authorized_status = validated_data.get('authorized_status', instance.authorized_status)
        instance.last_tender_rate = validated_data.get('last_tender_rate', instance.last_tender_rate)
        instance.last_tender_date = validated_data.get('last_tender_date', instance.last_tender_date)
        instance.estimate_bid_price = validated_data.get('estimate_bid_price', instance.estimate_bid_price)
        instance.oem_challenges = validated_data.get('oem_challenges', instance.oem_challenges)
        instance.department_challenges = validated_data.get('department_challenges', instance.department_challenges)
        instance.is_extension_request = validated_data.get('is_extension_request', instance.is_extension_request)
        instance.department_name = validated_data.get('department_name', instance.department_name)
        instance.is_reverse_auction = validated_data.get('is_reverse_auction', instance.is_reverse_auction)
        instance.pendingdocumentsOEM = validated_data.get('pendingdocumentsOEM', instance.pendingdocumentsOEM)
        instance.documents_not_submitted_evaluation_matrix = validated_data.get('documents_not_submitted_evaluation_matrix', instance.documents_not_submitted_evaluation_matrix)
        instance.is_site_visit = validated_data.get('is_site_visit', instance.is_site_visit)
        
        instance.save()

        return instance


class CaseSheetUpdateSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = CaseSheet
        read_only_fields = ['id', 'code',  ]
        fields = ['id', 'created_on', 'costing_remarks', 'remarks', ]


    def update(self, instance, validated_data):

        instance.costing_remarks = validated_data.get('costing_remarks', instance.costing_remarks)
        instance.remarks = validated_data.get('remarks', instance.remarks)

        instance.save()
        instance.tender.save() 

        return instance

        
    
class ReverseAuctionSerializer(ModelSerializerPermissionMixin):
    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    tender_item_master = ItemMiniSerializer(many=False, read_only=True)
    tender_item_master_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender_item_master', queryset=Item.objects.filter(product_type = Item.PRODUCT,is_deleted=False))

    tender_item = TenderItemSerializer(many=False, read_only=True)
    tender_item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender_item', queryset=TenderItem.objects.filter(is_deleted=False))

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], read_only=True)

    class Meta:
        model = ReverseAuction
        # data_validate_fields = ['tender_id','tender_item_id','tender_item_master_id']
        read_only_fields = [
            'id', 'code', 'created_on', 'landing_cost_margin_amount',
            'landing_cost_total', 'landing_cost_gst_amount', 'total', 'l1_price', 'diff_amount'
        ]
        fields = [
            'id','tender', 'tender_id', 'tender_item_master', 'tender_item_master_id', 
            'tender_item', 'tender_item_id', 'landing_cost', 'discount_landing_cost', 
            'landing_cost_margin', 'landing_cost_margin_amount', 'landing_cost_total', 
            'landing_cost_gst', 'landing_cost_gst_amount', 'total', 'l1_price', 'diff_amount','created_on'
        ]

    

    def validate(self, data):

        if data.get('landing_cost') is None:
            raise serializers.ValidationError({'landing_cost': 'This field is required.'})

        if data.get('discount_landing_cost') is None:
            raise serializers.ValidationError({'discount_landing_cost': 'This field is required.'})

        if data.get('landing_cost_margin') is None:
            raise serializers.ValidationError({'landing_cost_margin': 'This field is required.'})

        return data


    def create(self, validated_data):
        reverseauction = ReverseAuction.objects.create(**validated_data)

        return reverseauction

    def update(self, instance, validated_data):


        return instance
    

class ReverseAuctionL1PriceSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ReverseAuction
        read_only_fields = ['id', 'code','diff_amount',  ]
        fields = ['id', 'l1_price', 'diff_amount' , ]


    def update(self, instance, validated_data):
        instance.l1_price = validated_data.get('l1_price', instance.l1_price)
        
        total = instance.total if instance.total is not None else 0
        l1_price = instance.l1_price if instance.l1_price is not None else 0

        instance.diff_amount = total - l1_price

        instance.save()

        return instance
    


class TenderDocumentsSerializer(ModelSerializerPermissionMixin):
    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    document = DocumentMiniSerializer(many=False, read_only=True)
    document_id = serializers.PrimaryKeyRelatedField(write_only=True, source='document', required=False, queryset=Document.objects.filter(is_deleted=False))

    type = serializers.ChoiceField(choices=TenderDocuments.TYPE_CHOICES)
    type_name = serializers.SerializerMethodField()

    def get_type_name(self, obj):
        return obj.get_type_display()

    def validate(self, attrs):
        type = attrs.get('type')
        is_submitted = attrs.get('is_submitted')
        document_id = attrs.get('document')
        document_name = attrs.get('document_name')

        if type == TenderDocuments.COMMON:
            if is_submitted is None:
                raise serializers.ValidationError({
                    'is_submitted': 'This field is required for Common documents.'
                })
            if document_id is None:
                raise serializers.ValidationError({
                    'document_id': 'This field is required for Common documents.'
                })
            

        elif type == TenderDocuments.INDIVIDUAL:
            if is_submitted is None:
                raise serializers.ValidationError({
                    'is_submitted': 'This field is required for Individual documents.'
                })
            if document_name is None:
                raise serializers.ValidationError({
                    'document_name': 'This field is required for Individual documents.'
                })

        return super().validate(attrs)

    class Meta:
        model = TenderDocuments
        # data_validate_fields = ['tender_id','document_id']
        read_only_fields = ['id', 'code']
        fields = [
            'id', 'tender', 'tender_id', 'type', 'type_name', 
            'document', 'document_id', 'document_name', 'file', 'is_submitted', 'created_on', 
        ]

    def create(self, validated_data):
        document_id = validated_data.pop('document_id', None)
        tender = validated_data.get('tender', None)
        obj = super().create(validated_data)



        return obj

    def update(self, instance, validated_data):
        document_id = validated_data.pop('document_id', None)
        tender_document = super().update(instance, validated_data)

        if document_id is not None:
            tender_document.document_id = document_id

        tender_document.save()


        return tender_document


class BidAmountSerializer(ModelSerializerPermissionMixin):

    tender = TenderSerializer(many=False, read_only=True)  
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'], read_only=True)

    class Meta:
        model = BidAmount
        # data_validate_fields = ['tender_id',]
        read_only_fields = ['id', 'code', 'created_on', 'l1_price' ]
        fields = ['id', 'tender', 'tender_id', 'amount',  'l1_price', 'created_on' ] 
  


class BidAmountL1PriceSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = BidAmount
        read_only_fields = ['id', 'code',  ]
        fields = ['id', 'l1_price',  ]


    def update(self, instance, validated_data):
        instance.l1_price = validated_data.get('l1_price', instance.l1_price)
        
        instance.save()

        return instance
   


class PDFExtractionSerializer(serializers.ModelSerializer):
    extraction_json_data = serializers.SerializerMethodField(source= 'extarct_data',read_only=True)

    def get_extraction_json_data(self, obj):
        if obj.extarct_data:
            try:
                return json.loads(obj.extarct_data)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON format"}
        return None
    
    class Meta:
        model = PDFExtraction
        read_only_fields = ['id', 'code', 'created_on', 'status', 'extarct_data', 'extraction_json_data']
        fields = ['id', 'file',  'status',  'extarct_data','extraction_json_data', 'created_on' ] 

class CostingSheetSerializer(ModelSerializerPermissionMixin):
    tender = TenderMiniSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender',required = False, queryset=Tender.objects.filter(is_deleted=False))

    project = ProjectMini3Serializer(many=False, read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project',required = False, queryset=Project.objects.filter(is_deleted=False))

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    modified_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)

    authorized_status = serializers.ChoiceField(choices=CostingSheet.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    created_by = UserRelatedField(user_field= 'created_by', read_only=True)
    authorized_by = UserRelatedField(user_field= 'authorized_by', read_only=True)

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()
    
    
    class Meta:
        model = CostingSheet
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = ('id', 'code', 'tender', 'tender_id', 'project','project_id','description', 'created_on', 'modified_on','created_by', 'authorized_status', 'authorized_status_name','authorized_by')

    def create(self, validated_data):
        obj = super().create(validated_data)
        
        return obj

class CostingSheetMiniSerializer(serializers.ModelSerializer):
    tender = TenderMiniSerializer(many=False, read_only=True)
    project = ProjectMini3Serializer(many=False, read_only=True)

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    modified_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)

    authorized_status = serializers.ChoiceField(choices=CostingSheet.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    created_by = UserRelatedField(user_field= 'created_by', read_only=True)
    authorized_by = UserRelatedField(user_field= 'authorized_by', read_only=True)

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()
    
    
    class Meta:
        model = CostingSheet
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = ('id', 'code', 'tender', 'project','description', 'created_on', 'modified_on','created_by', 'authorized_status', 'authorized_status_name','authorized_by')


class ServiceSerializer(serializers.ModelSerializer):
    costingsheet = CostingSheetMiniSerializer(many=False, read_only=True)
    costingsheet_id = serializers.PrimaryKeyRelatedField(write_only=True, source='costingsheet', queryset=CostingSheet.objects.filter(is_deleted=False))

    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    item = ItemSerializer(many=False, read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source='item', queryset=Item.objects.filter(is_deleted=False, type=Item.SERVICE)
    )

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    modified_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    
    class Meta:
        model = Service
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = ('id', 'code', 'costingsheet', 'costingsheet_id','tender', 'tender_id', 'item','item_id','days', 'qty', 'price', 'duration', 'overtime_amount', 'total_price', 'margin_percent', 'margin_amount', 'remarks','created_on', 'modified_on')

    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.total_price = obj.qty * obj.price * obj.days
        obj.margin_amount = (obj.total_price * obj.margin_percent) / 100
        obj.total_price += Decimal(obj.duration) + Decimal(obj.margin_amount) + Decimal(obj.overtime_amount)
        obj.save()
        return obj


class ServiceMiniSerializer(serializers.ModelSerializer):
    item = ItemMiniSerializer(many=False, read_only=True)


    class Meta:
        model = Service
        fields = ('id','code','item')



class ServiceMini2Serializer(serializers.ModelSerializer):
    item = ItemMiniSerializer(many=False, read_only=True)


    class Meta:
        model = Service
        fields = ('id','code','item','qty', 'days', 'price', 'total_price','margin_percent', 'overtime_amount', 'margin_amount', )



class ConsumableSerializer(serializers.ModelSerializer):

    costingsheet = CostingSheetMiniSerializer(many=False, read_only=True)
    costingsheet_id = serializers.PrimaryKeyRelatedField(write_only=True, source='costingsheet', queryset=CostingSheet.objects.filter(is_deleted=False))

    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    item = ItemSerializer(many=False, read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source='item', queryset=Item.objects.filter(is_deleted=False, type=Item.MATERIAL)
    )

    
    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    modified_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    
    class Meta:
        model = Consumable
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = ('id', 'code', 'costingsheet', 'costingsheet_id', 'tender', 'tender_id',  'item','item_id','qty', 'price', 'total_price', 'margin_percent', 'margin_amount',  'remarks','created_on', 'modified_on')
        
    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.total_price = (obj.qty * obj.price)
        obj.margin_amount = (obj.total_price * obj.margin_percent) / 100
        obj.total_price += obj.margin_amount
        obj.save()
        
        return obj
    

class ConsumableMiniSerializer(serializers.ModelSerializer):
    item = ItemMiniSerializer(many=False, read_only=True)


    class Meta:
        model = Consumable
        fields = ('id','code','item')


class ConsumableMini2Serializer(serializers.ModelSerializer):
    item = ItemMiniSerializer(many=False, read_only=True)


    class Meta:
        model = Consumable
        fields = ('id','code','item','qty', 'price', 'total_price','margin_percent', 'margin_amount', )


class OtherChargesSerializer(serializers.ModelSerializer):
    costingsheet = CostingSheetMiniSerializer(many=False, read_only=True)
    costingsheet_id = serializers.PrimaryKeyRelatedField(write_only=True, source='costingsheet', queryset=CostingSheet.objects.filter(is_deleted=False))

    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))

    miscellaneoustype = MiscellaneousTypesMiniSerializer(many=False, read_only=True)
    miscellaneoustype_id = serializers.PrimaryKeyRelatedField(write_only=True, source='miscellaneoustype', queryset=MiscellaneousTypes.objects.filter(is_deleted=False))

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    modified_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    
    class Meta:
        model = OtherCharges
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = ('id', 'code', 'costingsheet', 'costingsheet_id','tender', 'tender_id', 'miscellaneoustype','miscellaneoustype_id', 'name', 'price', 'margin_percent', 'margin_amount', 'total_price', 'remarks','created_on', 'modified_on')
        

    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.margin_amount = (obj.price * obj.margin_percent) / 100
        obj.total_price = obj.price + obj.margin_amount
        obj.save()
        
        return obj
    

class OtherChargesMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = OtherCharges
        fields = ('id', 'name', 'price', 'margin_percent', 'margin_amount', 'total_price')




class RawMaterialSerializer(serializers.ModelSerializer):

    costingsheet = CostingSheetMiniSerializer(many=False, read_only=True)
    costingsheet_id = serializers.PrimaryKeyRelatedField(write_only=True, source='costingsheet', queryset=CostingSheet.objects.filter(is_deleted=False))

    tender = TenderSerializer(many=False, read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False))
    
    item = ItemSerializer(many=False, read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source='item', queryset=Item.objects.filter(is_deleted=False, type=Item.MATERIAL)
    )

    created_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)
    modified_on = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p', input_formats=['%d-%m-%Y %I:%M %p'],read_only=True)

    type = serializers.ChoiceField(choices=RawMaterial.TYPE_CHOICES, required=False,)
    type_name = serializers.SerializerMethodField()

    def get_type_name(self, obj):
        return obj.get_type_display()
    
    class Meta:
        model = RawMaterial
        read_only_fields = ['code', 'created_on', 'modified_on']
        fields = ('id', 'code', 'costingsheet', 'costingsheet_id', 'tender', 'tender_id', 'type', 'type_name', 'item','item_id','qty', 'price', 'total_price', 'margin_percent', 'margin_amount',  'remarks','created_on', 'modified_on')
        
    def create(self, validated_data):
        validated_data['type'] = RawMaterial.RAWITEM
        obj = super().create(validated_data)
        obj.total_price = obj.qty * obj.price
        obj.margin_amount = (obj.total_price * obj.margin_percent) / 100
        obj.total_price += obj.margin_amount
        obj.save()
        
        return obj

class PlazoTenderItemSerializer(ModelSerializerPermissionMixin):

    id = serializers.UUIDField( required=False)

    item = ItemSerializer(many=False, read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='item', required = False, queryset=Item.objects.filter(is_deleted = False, product_type = Item.PRODUCT))
   
    dodelete = serializers.BooleanField(write_only=True, required=False)

    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

        
    class Meta:
        model = PlazoTenderItem
        list_serializer_class = FilteredListSerializer
        # data_validate_fields = ['item_id',]
        read_only_fields = [ 'id','code', 'created_on', 'plazotender','created_by',]
        fields = ('id', 'code', 'item', 'item_id', 'quantity','dodelete', 'created_on', 'created_by',)



class PlazoTenderSerializer(ModelSerializerPermissionMixin):
    project = ProjectMini3Serializer(many=False, read_only=True)

    customer = AccountMiniSerializer(many=False, read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, required=False, source='customer', queryset=Account.objects.filter(is_deleted=False, account_type = Account.CUSTOMER))

    authorized_by = UserRelatedField(user_field= 'authorized_by', read_only=True)
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)
    current_authorized_by = UserRelatedField(user_field= 'current_authorized_by', read_only=True)

    plazo_tender_items = PlazoTenderItemSerializer(many=True)

    authorized_status = serializers.ChoiceField(choices=PlazoTender.AUTHORIZED_STATUS_CHOICES, required=False)
    authorized_status_name = serializers.SerializerMethodField()

    documents = serializers.SerializerMethodField()

    def get_authorized_status_name(self, obj):
        return obj.get_authorized_status_display()

    def get_documents(self, obj):
        documents = PlazoTenderAttachment.objects.filter(plazo_tender = obj, is_deleted= False)
        serializer = PlazoTenderAttachmentSerializer(instance = documents, many=True, context = self.context)

        return serializer.data
    
    class Meta:
        model = PlazoTender
        # data_validate_fields = ['project_id',]
        read_only_fields = ['code', 'created_on', 'created_by', 'authorized_by','authorized_level','authorized_status', 'authorized_status_name', 'current_authorized_level','current_authorized_by','current_authorized_on' ]
        fields = ('id', 'code', 'name',  'tender_no', 'project', 'assigned_on', 'status', 'customer','customer_id', 'plazo_tender_items', 'documents', 'description','authorized_level','authorized_status', 'authorized_status_name', 'current_authorized_level','current_authorized_by','current_authorized_on', 'created_on', 'created_by','authorized_by')


    def validate(self, data):
        name = data.get("name")
        tender_no = data.get("tender_no")

        if not self.instance:
            if PlazoTender.objects.filter(name=name, is_deleted=False).exists():
                raise serializers.ValidationError(
                    f"An entry with name: {name} already exists."
                )

            if PlazoTender.objects.filter(tender_no=tender_no, is_deleted=False).exists():
                raise serializers.ValidationError(
                    f"An entry with tender number: {tender_no} already exists."
                )
           
        return data
    

    def create(self, validated_data):
        now_date = timezone.now().date()
        # validated_data['date'] = now_date
        pt_items_data = validated_data.pop('plazo_tender_items', [])
            
        plazotender = PlazoTender.objects.create(**validated_data)

        project = Project.objects.create(
            name=plazotender.code,
            tender_no=plazotender.tender_no,
            status=Project.TENDER,  
            plazo_tender=plazotender,    
        )

        for item_data in pt_items_data:
            if item_data.get('dodelete', False):
                continue
            
            item_data.pop('dodelete', None)
            
            PlazoTenderItem.objects.create(
                plazo_tender=plazotender,
                **item_data
            )

            ProjectItem.objects.create(
                project=project,
                quantity=item_data['quantity']
            )

        plazotender.project = project
        plazotender.save()

        return plazotender


    def update(self, instance, validated_data):
        pt_items_data = validated_data.pop('plazo_tender_items', [])
        instance.name = validated_data.get('name', instance.name)
        instance.tender_no = validated_data.get('tender_no', instance.tender_no)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        project, created = Project.objects.get_or_create(
            plazo_tender=instance,
            defaults={
                "name": instance.code,
                "tender_no": instance.tender_no,
                "status": Project.TENDER,
            }
        )

        if created:
            print(f"Created new Project: {project.name}")
        else:
            print(f"Updating existing Project: {project.name}")
            project.name = instance.code
            project.tender_no = instance.tender_no
            project.status = Project.TENDER
            project.save()


        for item_data in pt_items_data:
            item_id = item_data.get('id')
            dodelete = item_data.get('dodelete', False)
            item_data.pop('required_date', None)
            if item_id:
                try:
                    item_instance = PlazoTenderItem.objects.get(id=item_id, plazo_tender=instance)
                except:
                    raise serializers.ValidationError({"detail": f"PlazoTenderItem with id {item_id} does not exist for this request."})
                if item_data.get('dodelete', False):
                    item_instance.is_deleted = True
                    item_instance.save()
                    continue

                item_instance.quantity = Decimal(item_data.get('quantity', item_instance.quantity))
                item_instance.save()

                ProjectItem.objects.update_or_create(
                    project=project,
                    defaults={"quantity": item_data['quantity']}
                )
                print(f"Updated ProjectItem for TenderItem ID {item_id}.")

            else:
                if not dodelete:
                    quantity = Decimal(item_data.get('quantity', 0))

                    PlazoTenderItem.objects.create(
                        plazo_tender=instance,
                        quantity=quantity,
                        item=item_data.get('item'),
                    )

                    ProjectItem.objects.create(
                        project=project,
                        quantity=item_data['quantity']
                    )
                    print(f"Created ProjectItem linked to TenderItem ID.")

        return instance
    


class PlazoTenderMiniSerializer(serializers.ModelSerializer):
    created_by = UserRelatedField(user_field= 'created_by', read_only=True)

    class Meta:
        model = PlazoTender
        fields = ('id', 'code', 'name', 'tender_no', 'created_on', 'created_by')


    
class PlazoTenderAttachmentSerializer(ModelSerializerPermissionMixin):
    plazo_tender = PlazoTenderMiniSerializer(many=False, read_only=True)
    plazo_tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='plazo_tender', queryset=PlazoTender.objects.filter(is_deleted=False))

    class Meta:
        model = PlazoTenderAttachment
        # data_validate_fields = ['tender_id']
        fields = ('id', 'created_on', 'plazo_tender', 'plazo_tender_id', 'file')

    def create(self, validated_data):
        pta_obj = PlazoTenderAttachment.objects.create(**validated_data)
        try:
            pa_obj = ProjectDocuments.objects.create(project=pta_obj.tender.project, file=pta_obj.file)
        except Exception as e:
            print('Failed to create ProjectDocuments: ', str(e))

        return pta_obj


    

class RawMaterialMini2Serializer(serializers.ModelSerializer):
    item = ItemMiniSerializer(many=False, read_only=True)


    class Meta:
        model = RawMaterial
        fields = ('id','code','item','qty', 'price', 'total_price','margin_percent', 'margin_amount', )


class RawMaterialMiniSerializer(serializers.ModelSerializer):
    item = ItemMiniSerializer(many=False, read_only=True)


    class Meta:
        model = RawMaterial
        fields = ('id','code','item')


# BudgetEnquiry Serializers for BOQ Integration
class BudgetEnquiryItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(source='tenderitemmaster', read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tenderitemmaster', queryset=Item.objects.filter(is_deleted=False))
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = TenderItem  # BudgetEnquiry uses same structure as Tender for items
        fields = ['id', 'code', 'item', 'item_id', 'unit', 'unit_name', 'quantity', 'is_rfq_required', 'item_specifications']


class BudgetEnquiryListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    sourceportal_name = serializers.CharField(source='sourceportal.name', read_only=True)
    tender_stage_name = serializers.CharField(source='tender_stage.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by = UserRelatedField(user_field='created_by', read_only=True)
    modified_by = UserRelatedField(user_field='modified_by', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetEnquiry
        fields = [
            'id', 'code', 'name', 'tender_no', 'tender_type', 'product_type', 'status',
            'department_name', 'description', 'customer', 'customer_name', 'company', 
            'company_name', 'location', 'location_name', 'sourceportal', 'sourceportal_name',
            'tender_stage', 'tender_stage_name', 'project', 'project_name', 'tender_datetime',
            'tender_open_datetime', 'ministry', 'annual_turnover', 'years_of_experiance',
            'evaluation_method', 'is_lead_required', 'lead', 'created_on', 'modified_on',
            'created_by', 'modified_by', 'item_count'
        ]
        
    def get_item_count(self, obj):
        return obj.tender_items.filter(is_deleted=False).count()


class BudgetEnquiryDetailSerializer(serializers.ModelSerializer):
    customer = AccountMiniSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, source='customer', queryset=Account.objects.filter(is_deleted=False))
    company = CompanyMiniSerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(write_only=True, source='company', queryset=Company.objects.filter(is_deleted=False))
    location = LocationMiniSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(write_only=True, source='location', queryset=Location.objects.filter(is_deleted=False))
    sourceportal = SourcePortalMiniSerializer(read_only=True)
    sourceportal_id = serializers.PrimaryKeyRelatedField(write_only=True, source='sourceportal', queryset=SourcePortal.objects.filter(is_deleted=False))
    tender_stage = StageMiniSerializer(read_only=True)
    tender_stage_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender_stage', queryset=Stage.objects.filter(is_deleted=False))
    project = ProjectMini3Serializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project', queryset=Project.objects.filter(is_deleted=False))
    lead = LeadMiniSerializer2(read_only=True)
    lead_id = serializers.PrimaryKeyRelatedField(write_only=True, source='lead', queryset=Lead.objects.filter(is_deleted=False))
    tender_items = BudgetEnquiryItemSerializer(many=True, read_only=True)
    created_by = UserRelatedField(user_field='created_by', read_only=True)
    modified_by = UserRelatedField(user_field='modified_by', read_only=True)
    
    class Meta:
        model = BudgetEnquiry
        fields = [
            'id', 'code', 'name', 'tender_no', 'tender_type', 'product_type', 'status',
            'department_name', 'description', 'customer', 'customer_id', 'company', 
            'company_id', 'location', 'location_id', 'sourceportal', 'sourceportal_id',
            'tender_stage', 'tender_stage_id', 'project', 'project_id', 'tender_datetime',
            'tender_open_datetime', 'tender_extension_datetime', 'ministry', 'annual_turnover', 
            'years_of_experiance', 'evaluation_method', 'is_lead_required', 'lead', 'lead_id',
            'is_inspection', 'documents_required_seller', 'tender_items', 'created_on', 
            'modified_on', 'created_by', 'modified_by'
        ]


class BudgetEnquiryMiniSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = BudgetEnquiry
        fields = ['id', 'code', 'name', 'tender_no', 'customer_name']

from .models import SecurityDeposit, LetterOfAward

class LetterOfAwardSerializer(ModelSerializerPermissionMixin):
    tender = TenderMiniSerializer(read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False), required=False)
    
    project = ProjectMini3Serializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project', queryset=Project.objects.filter(is_deleted=False), required=False)
    
    customer = AccountMiniSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, source='customer', queryset=Account.objects.filter(is_deleted=False, account_type=Account.CUSTOMER), required=False)
    
    status = serializers.ChoiceField(choices=LetterOfAward.STATUS_CHOICES, required=False)
    status_display = serializers.SerializerMethodField()
    
    created_by = UserRelatedField(user_field='created_by', read_only=True)
    
    class Meta:
        model = LetterOfAward
        fields = [
            'id', 'code', 'loa_number', 'tender', 'tender_id', 'project', 'project_id', 'customer', 'customer_id',
            'award_amount', 'contract_duration', 'commencement_date', 'completion_date',
            'issue_date', 'acceptance_date',
            'scope_of_work', 'payment_terms', 'performance_security_required', 
            'performance_security_amount', 'performance_security_percentage',
            'bank_guarantee_required', 'bank_guarantee_percentage',
            'status', 'status_display', 'remarks', 'conditions_precedent',
            'loa_document', 'acceptance_document', 'created_on', 'created_by'
        ]
        read_only_fields = ['code', 'created_on', 'created_by', 'completion_date', 'performance_security_amount']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def create(self, validated_data):
        from datetime import timedelta
        from django.utils import timezone
        
        # Set customer from tender if not provided
        if not validated_data.get('customer') and validated_data.get('tender'):
            validated_data['customer'] = validated_data['tender'].customer
        
        # Set project from tender if not provided
        if not validated_data.get('project') and validated_data.get('tender'):
            validated_data['project'] = validated_data['tender'].project
        
        # Create LOA instance
        loa = super().create(validated_data)
        
        # Create SecurityDeposit records based on checkboxes
        self._create_security_deposits(loa)
        
        return loa
    
    def update(self, instance, validated_data):
        # Update LOA instance
        loa = super().update(instance, validated_data)
        
        # Delete existing SecurityDeposit records for this LOA
        SecurityDeposit.objects.filter(
            tender=loa.tender,
            project=loa.project,
            customer=loa.customer
        ).delete()
        
        # Create new SecurityDeposit records based on updated checkboxes
        self._create_security_deposits(loa)
        
        return loa
    
    def _create_security_deposits(self, loa):
        from datetime import timedelta
        from django.utils import timezone
        
        # Calculate due date (30 days from issue date or today)
        due_date = loa.issue_date + timedelta(days=30) if loa.issue_date else timezone.now().date() + timedelta(days=30)
        
        # Create Security Deposit record if checked
        if loa.performance_security_required and loa.performance_security_percentage and loa.award_amount:
            sd_amount = (loa.award_amount * loa.performance_security_percentage) / 100
            SecurityDeposit.objects.create(
                tender=loa.tender,
                project=loa.project,
                customer=loa.customer,
                type='SD',
                amount=sd_amount,
                due_expiry_date=due_date,
                status='Pending'
            )
        
        # Create Bank Guarantee record if checked
        if loa.bank_guarantee_required and loa.bank_guarantee_percentage and loa.award_amount:
            bg_amount = (loa.award_amount * loa.bank_guarantee_percentage) / 100
            SecurityDeposit.objects.create(
                tender=loa.tender,
                project=loa.project,
                customer=loa.customer,
                type='BG',
                amount=bg_amount,
                due_expiry_date=due_date,
                status='Pending'
            )


class LetterOfAwardMiniSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LetterOfAward
        fields = ['id', 'code', 'loa_number', 'customer_name', 'award_amount', 'status', 'status_display', 'issue_date', 'completion_date']


class OrderSerializer(ModelSerializerPermissionMixin):
    tender = TenderMiniSerializer(read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False), required=False)
    
    project = ProjectMini3Serializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(write_only=True, source='project', queryset=Project.objects.filter(is_deleted=False), required=False)
    
    customer = AccountMiniSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, source='customer', queryset=Account.objects.filter(is_deleted=False, account_type=Account.CUSTOMER), required=False)
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=False)
    status_display = serializers.SerializerMethodField()
    
    created_by = UserRelatedField(user_field='created_by', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'code', 'order_number', 'tender', 'tender_id', 'project', 'project_id', 'customer', 'customer_id',
            'order_amount', 'contract_duration', 'commencement_date', 'completion_date',
            'issue_date', 'acceptance_date',
            'scope_of_work', 'payment_terms', 'performance_security_required', 
            'performance_security_amount', 'performance_security_percentage',
            'bank_guarantee_required', 'bank_guarantee_percentage',
            'status', 'status_display', 'remarks', 'conditions_precedent',
            'order_document', 'acceptance_document', 'created_on', 'created_by'
        ]
        read_only_fields = ['code', 'created_on', 'created_by', 'completion_date', 'performance_security_amount']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class OrderMiniSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'code', 'order_number', 'customer_name', 'order_amount', 'status', 'status_display', 'issue_date', 'completion_date']


class SecurityDepositSerializer(serializers.ModelSerializer):
    customer = AccountMiniSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(write_only=True, source='customer', queryset=Account.objects.filter(is_deleted=False, account_type=Account.CUSTOMER))
    
    tender = TenderMiniSerializer(read_only=True)
    tender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tender', queryset=Tender.objects.filter(is_deleted=False), required=False)
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SecurityDeposit
        fields = '__all__'
        read_only_fields = ['code', 'created_on', 'created_by']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['type_display'] = instance.get_type_display()
        representation['status_display'] = instance.get_status_display()
        return representation
        
    def create(self, validated_data):
        tender = validated_data.get('tender')
        if tender and not validated_data.get('customer'):
            validated_data['customer'] = tender.customer
        if 'status' not in validated_data:
            validated_data['status'] = 'Pending'
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        print(f"Update - New status: {new_status}, Current status: {instance.status}")
        if new_status == 'Received' and instance.status != 'Received':
            validated_data['received_on'] = timezone.now().date()
            print(f"Setting received_on to: {validated_data['received_on']}")
        if new_status == 'Refunded' and instance.status != 'Refunded':
            validated_data['refunded_on'] = timezone.now().date()
            print(f"Setting refunded_on to: {validated_data['refunded_on']}")
        new_due_date = validated_data.get('due_expiry_date')
        if new_due_date and new_due_date != instance.due_expiry_date:
            validated_data['extended_on'] = timezone.now().date()
            print(f"Setting extended_on to: {validated_data['extended_on']}")
        return super().update(instance, validated_data)

class SecurityDepositCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityDeposit
        fields = ['project', 'customer', 'type', 'amount', 'received_on', 'due_expiry_date', 'status']

class SecurityDepositUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityDeposit
        fields = ['due_expiry_date', 'status', 'refunded_on', 'remarks']
        
    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        print(f"Update - New status: {new_status}, Current status: {instance.status}")
        if new_status == 'Received' and instance.status != 'Received':
            validated_data['received_on'] = timezone.now().date()
            print(f"Setting received_on to: {validated_data['received_on']}")
        if new_status == 'Refunded' and instance.status != 'Refunded':
            validated_data['refunded_on'] = timezone.now().date()
            print(f"Setting refunded_on to: {validated_data['refunded_on']}")
        new_due_date = validated_data.get('due_expiry_date')
        if new_due_date and new_due_date != instance.due_expiry_date:
            validated_data['extended_on'] = timezone.now().date()
            print(f"Setting extended_on to: {validated_data['extended_on']}")
        return super().update(instance, validated_data)