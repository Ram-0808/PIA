

from import_export import resources
from import_export.widgets import ForeignKeyWidget, DateWidget, DateTimeWidget, DecimalWidget
from import_export.fields import Field

from Core.Users.models import Assignee


from .models import *
from Core.Core.imports_exports.resources import ModelImportExportResource
from import_export.widgets import ForeignKeyWidget,  DateTimeWidget

from Masters.models import  *
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import Group, Permission 
from django.db.models import Count, Q
from ProjectManagement.models import Project
from django.db.models import Count

from django.apps import apps
Location = apps.get_model('DynamicDjango','Location')
Company = apps.get_model('DynamicDjango','Company')

class TenderSummaryResource(resources.ModelResource):
    assign_to = Field(
        column_name='Assigned To'
    )
    total_tender_count = Field(
        column_name='Total Tender Count'
    )

    def dehydrate_total_tender_count(self, tender):
        assignees = Assignee.objects.filter(
            screen__app_label='TenderManagement',
            screen__model='tender',
            instance_id=str(tender.id)
        ).values('user')

        user_tender_count = Assignee.objects.filter(
            screen__app_label='TenderManagement',
            screen__model='tender'
        ).values('user').annotate(tender_count=Count('user'))

        tender_user_ids = [user['user'] for user in assignees]
        count = 0

        for user in user_tender_count:
            if user['user'] in tender_user_ids:
                count = user['tender_count']
                break

        return count
    
    def dehydrate_assign_to(self, tender):
        assignees = Assignee.objects.filter(
            screen__app_label='TenderManagement',
            screen__model='tender',
            instance_id=str(tender.id)
        ).values('user')

        assigned_users = [user['user'] for user in assignees]
        return ', '.join([user.username for user in User.objects.filter(id__in=assigned_users)])

    
    class Meta:
        model = Tender
        fields = ('assign_to', 'total_tender_count',)
        export_order = ('assign_to', 'total_tender_count',)



class TenderResource(ModelImportExportResource):
    code = Field(column_name='Code', attribute='code')

    # assign_to = Field(column_name='Assigned To', attribute='assign_to', widget=ForeignKeyWidget(User, field='username'))
    project = Field(column_name='Project Name', attribute='project', widget=ForeignKeyWidget(Project, field='name'))
    project_code = Field(column_name='Project Code', attribute='project', widget=ForeignKeyWidget(Project, field='code'))

    tender_no = Field(column_name='Tender Number', attribute='tender_no')
    tender_type = Field(column_name='Tender Type', attribute='tender_type')
    product_type = Field(column_name='Product Type', attribute='product_type')
    authorized_status = Field(column_name='Status', attribute='authorized_status')

    sourceportal = Field(column_name='Source Portal', attribute='sourceportal', widget=ForeignKeyWidget(SourcePortal, field='name'))
    # company = Field(column_name='Company Name', attribute='company', widget=ForeignKeyWidget(Company, field='name'))
    # company_code = Field(column_name='Company Code', attribute='company', widget=ForeignKeyWidget(Company, field='code'))

    customer = Field(column_name='Customer Name', attribute='customer', widget=ForeignKeyWidget(Account, field='name'))
    customer_code = Field(column_name='Customer Code', attribute='customer', widget=ForeignKeyWidget(Account, field='code'))

    tender_datetime = Field(column_name='Tender Date & Time', attribute='tender_datetime', widget=DateTimeWidget())
    department_name = Field(column_name='Department Name', attribute='department_name')

    is_documents_attached = Field(column_name='Is Documents Attached')
    is_reverse_auction = Field(column_name='Is Reverse Auction')

    created_on = Field(column_name='Created On', attribute='created_on', widget=DateTimeWidget())
    modified_on = Field(column_name='Modified On', attribute='modified_on', widget=DateTimeWidget())
    created_by = Field(column_name='Created By', attribute='created_by', widget=ForeignKeyWidget(User, field='username'))
    modified_by = Field(column_name='Modified By', attribute='modified_by', widget=ForeignKeyWidget(User, field='username'))

    class Meta:
        model = Tender
        fields = (
            'code', 'tender_no', 'tender_type', 'product_type', 'authorized_status',  'project', 'project_code', 'sourceportal',
            'customer', 'customer_code', 'department_name', 'tender_datetime',
            'is_reverse_auction', 'is_documents_attached','created_by', 'created_on', 'modified_by', 'modified_on'
        ) # 'company', 'company_code','assign_to',
        export_order = (
            'code', 'tender_no', 'tender_type', 'product_type', 'authorized_status',  'project', 'project_code', 'sourceportal',
             'customer', 'customer_code', 'department_name', 'tender_datetime',
            'is_reverse_auction', 'is_documents_attached','created_by', 'created_on', 'modified_by', 'modified_on'
        ) #  'company', 'company_code','assign_to',
        import_fields = (
            'tender_no', 'tender_type', 'product_type', 'authorized_status', 'project', 'project_code', 'sourceportal', 'customer', 'customer_code', 'department_name', 'tender_datetime',
            'is_reverse_auction'
        ) #  'company', 'company_code', 'assign_to',
        import_id_fields = ('code',)


    def dehydrate_is_documents_attached(self, obj):
        return 'True'

        # if obj.documents.exists():
        #     return 'True'
        # else:
        #     return 'False'


    def dehydrate_is_reverse_auction(self, obj):

        if obj.is_reverse_auction == 1:
            return 'True'
        else:
            return 'False'

    def dehydrate_tender_type(self, obj):

        if obj.tender_type == obj.OPENTENDER:
            return 'OpenTender'
        elif obj.tender_type == obj.LIMITEDTENDER:
            return 'LimitedTender'
        else:
            return 'SBC'


    def dehydrate_product_type(self, obj):

        if obj.product_type == obj.SUPPLY:
            return 'Supply'
        elif obj.product_type == obj.SERVICE:
            return 'Service'
        elif obj.product_type == obj.BOTH:
            return 'Both'


    def dehydrate_authorized_status(self, obj):

        if obj.authorized_status == obj.PENDING:
            return 'Pending'
        elif obj.authorized_status == obj.APPROVED:
            return 'Approved'
        elif obj.authorized_status == obj.REJECTED:
            return 'Rejected'
        elif obj.authorized_status == obj.CANCELLED:
            return 'Cancelled'



class TenderItemResource(ModelImportExportResource):
    code = Field(column_name='Code', attribute='tender__code')
    tender = Field(column_name='Name', attribute='tender__name')
    tende_no = Field(column_name='Tender No', attribute='tender__tender_no')
    company = Field(column_name='Company', attribute='tender__company', widget=ForeignKeyWidget(Company, field='name'))
    sourceportal = Field(column_name='SourcePortal', attribute='tender__sourceportal', widget=ForeignKeyWidget(SourcePortal , field='name'))
    cutomer = Field(column_name='Customer', attribute='tender__customer', widget=ForeignKeyWidget(Account, field='name'))
    tenderitemmaster = Field(column_name='Item', attribute='tenderitemmaster', widget=ForeignKeyWidget(TenderItemMaster, field='name'))
    unit = Field(column_name='Unit', attribute='unit', widget=ForeignKeyWidget(Unit, field='uom__name'))
    quantity = Field(column_name='Quantity', attribute='quantity', widget=DecimalWidget())


    class Meta:
        model = TenderItem
        fields = (
            'code', 'tender', 'tende_no', 'company', 'sourceportal', 'cutomer','tenderitemmaster', 'unit','quantity',
        )
        export_order = (
            'code', 'tender', 'tende_no', 'company', 'sourceportal', 'cutomer','tenderitemmaster', 'unit','quantity',
        )
        import_fields = (
            'code', 'tender', 'tende_no', 'company', 'sourceportal', 'cutomer','tenderitemmaster', 'unit','quantity',
        )
        import_id_fields = ('code',)




class TenderItemMasterResource(resources.ModelResource):
    code = Field(column_name='Code', attribute='code')
    name = Field(column_name='Name', attribute='name')

    class Meta:
        model = TenderItemMasterItem
        fields = ('code', 'name',)
        export_order = ('code', 'name',)
        import_id_fields = ('code',)


class TenderCommentsResource(resources.ModelResource):
    code = Field(column_name='Code', attribute='code')
    tender = Field(column_name='Tender', attribute='tender', widget=ForeignKeyWidget(Tender, field='code'))
    comment = Field(column_name='Comment', attribute='comment')

    class Meta:
        model = TenderComments
        fields = ('code', 'tender', 'comment')
        export_order = ('code', 'tender', 'comment')
        import_id_fields = ('code',)


class TenderItemMasterItemResource(resources.ModelResource):
    code = Field(column_name='Code', attribute='code')
    tenderitemmaster = Field(column_name='TenderItem', attribute='tenderitemmaster', widget=ForeignKeyWidget(TenderItemMaster, 'code'))
    item = Field(column_name='Item', attribute='item', widget=ForeignKeyWidget(Item, 'name'))
    quantity = Field(column_name='Quantity', attribute='quantity')

    class Meta:
        model = TenderItemMasterItem
        fields = ('code', 'tenderitemmaster',  'item', 'quantity')
        export_order = ('code', 'tenderitemmaster', 'item', 'quantity')
        import_id_fields = ('code',)



class CaseSheetResource(resources.ModelResource):
    code = Field(column_name='Code', attribute='code')
    tender = Field(column_name='Tender',attribute='tender',widget=ForeignKeyWidget(Tender, field='code'))
    pre_bid_date = Field(column_name='Pre-Bid Date',attribute='pre_bid_date', widget=DateTimeWidget())
    contact_person = Field(column_name='Contact Person', attribute='contact_person')
    phone = Field(column_name='Phone', attribute='phone')
    email = Field(column_name='Email', attribute='email')
    authorized_status = Field(column_name='Status', attribute='authorized_status')
    last_tender_rate = Field(column_name='Last Tender Rate', attribute='last_tender_rate')
    last_tender_date = Field(column_name='Last Tender Date',attribute='last_tender_date', widget=DateWidget())
    estimate_bid_price = Field(column_name='Estimate Bid Price', attribute='estimate_bid_price')
    oem_challenges = Field(column_name='OEM Challenges', attribute='oem_challenges')
    department_challenges = Field(column_name='Department Challenges', attribute='department_challenges')
    is_extension_request = Field(column_name='Is Extension Request', attribute='is_extension_request')
    is_site_visit = Field(column_name='Is Site Visit', attribute='is_site_visit')
    costing_remarks = Field(column_name='Costing Remarks', attribute='costing_remarks')
    remarks = Field(column_name='Remarks', attribute='remarks')

    created_on = Field(column_name='Created On', attribute='created_on', widget=DateTimeWidget())
    modified_on = Field(column_name='Modified On', attribute='modified_on', widget=DateTimeWidget())
    created_by = Field(column_name='Created By', attribute='created_by', widget=ForeignKeyWidget(User, field='username'))
    modified_by = Field(column_name='Modified By', attribute='modified_by', widget=ForeignKeyWidget(User, field='username'))
   
    class Meta:
        model = CaseSheet
        fields = ( 'code', 'tender', 'pre_bid_date', 'pre_bid_subject', 'contact_person', 'phone', 'email', 'authorized_status',
            'last_tender_rate', 'last_tender_date', 'estimate_bid_price', 'oem_challenges', 'department_challenges',
            'is_extension_request', 'is_site_visit', 'costing_remarks', 'remarks', 'created_on', 'modified_on',
            'created_by', 'modified_by'
        )
        export_order = fields
        import_id_fields = ('code',)

    def dehydrate_authorized_status(self, obj):
        # Custom display for authorized_status choices
        return dict(CaseSheet.STATUS_CHOICES).get(obj.authorized_status, 'Unknown')