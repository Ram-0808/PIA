from django.apps import apps
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from Masters.models import Account, Item, SourcePortal, Tax, Unit
from ProjectManagement.models import Project, ProjectItem, Stock
from TenderManagement.models import Tender, TenderItemMaster
from Users.models import User
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget, DecimalWidget
from import_export.fields import Field


Company = apps.get_model('DynamicDjango', 'Company')
WareHouse = apps.get_model('DynamicDjango', 'WareHouse')


class ProjectResource(resources.ModelResource):
    company = fields.Field(
        column_name='company',
        attribute='company',
        widget=ForeignKeyWidget(Company, 'name')  # Assuming `name` is the identifier for Company
    )
    sourceportal = fields.Field(
        column_name='sourceportal',
        attribute='sourceportal',
        widget=ForeignKeyWidget(SourcePortal, 'name')  # Assuming `name` is the identifier for SourcePortal
    )
    customer = fields.Field(
        column_name='customer',
        attribute='customer',
        widget=ForeignKeyWidget(Account, 'name')  # Assuming `name` is the identifier for Customer
    )
    manager = fields.Field(
        column_name='manager',
        attribute='manager',
        widget=ForeignKeyWidget(User, 'username')  # Assuming `username` is the identifier for User
    )
    tax = fields.Field(
        column_name='tax',
        attribute='tax',
        widget=ForeignKeyWidget(Tax, 'name')  # Assuming `name` is the identifier for Tax
    )
    start_date = fields.Field(
        column_name='start_date',
        attribute='start_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    due_date = fields.Field(
        column_name='due_date',
        attribute='due_date',
        widget=DateWidget(format='%Y-%m-%d')
    )

    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'project_no', 'start_date', 'due_date', 'amount', 'gst_percentage', 'total_value',
            'taxtype', 'taxamount', 'warrenty_period', 'tender', 'tender_no', 'company', 'tender_type', 'product_type',
            'sourceportal', 'department_name', 'customer', 'manager', 'status', 'tender_datetime', 'tender_due_datetime',
            'deliver_terms', 'financial_terms', 'remarks', 'is_performace_bank_guarantee', 'is_pre_dispatch_inspection',
            'is_inspection_agency', 'inspection_agency', 'delivery_in_lots',
        ]
        export_order = [
            'id', 'code', 'name', 'project_no', 'start_date', 'due_date', 'amount', 'gst_percentage', 'total_value',
            'taxtype', 'taxamount', 'warrenty_period', 'tender', 'tender_no', 'company', 'tender_type', 'product_type',
            'sourceportal', 'department_name', 'customer', 'manager', 'status', 'tender_datetime', 'tender_due_datetime',
            'deliver_terms', 'financial_terms', 'remarks', 'is_performace_bank_guarantee', 'is_pre_dispatch_inspection',
            'is_inspection_agency', 'inspection_agency', 'delivery_in_lots',
        ]


class ProjectItemResource(resources.ModelResource):
    code = Field(column_name='Code', attribute='project__code')
    project = fields.Field(
        column_name='Project',
        attribute='project',
        widget=ForeignKeyWidget(Project, 'name')  # Assuming `name` is the identifier for Project
    )
    tender = Field(column_name='Tender', attribute='project__tender', widget=ForeignKeyWidget(Tender, 'name'))
    company = Field(column_name='Company', attribute='project__company', widget=ForeignKeyWidget(Company, field='name'))
    location = Field(column_name='Company', attribute='project__location', widget=ForeignKeyWidget(Company, field='name'))
    sourceportal = Field(column_name='SourcePortal', attribute='project__sourceportal', widget=ForeignKeyWidget(SourcePortal , field='name'))
    cutomer = Field(column_name='Customer', attribute='project__customer', widget=ForeignKeyWidget(Account, field='name'))

    tenderitemmaster = fields.Field(
        column_name='Item',
        attribute='tenderitemmaster',
        widget=ForeignKeyWidget(TenderItemMaster, 'name')  # Assuming `name` is the identifier for TenderItemMaster
    )

    quantity = fields.Field(
        column_name='Quantity',
        attribute='quantity',
        widget=DecimalWidget()  # Handles decimal conversion for quantity
    )

    class Meta:
        model = ProjectItem
        fields = [
            'code', 'project', 'tender', 'company', 'location', 'cutomer', 'sourceportal','tenderitemmaster', 'quantity',
        ]
        export_order = [
            'code', 'project', 'tender', 'company', 'location', 'cutomer', 'sourceportal','tenderitemmaster', 'quantity',
        ]


# class StockResource(resources.ModelResource):
#     code = fields.Field(column_name='Code', attribute='code')

#     screen_name = fields.Field(
#         column_name='Screen Name',
#         attribute='screen_name',
#     )

#     project = fields.Field(
#         column_name='project',
#         attribute='project',
#         widget=ForeignKeyWidget(Project, 'name')  
#     )
#     warehouse = fields.Field(
#         column_name='Warehouse',
#         attribute='warehouse',
#         widget=ForeignKeyWidget(WareHouse, 'name') 
#     )
#     item = fields.Field(
#         column_name='item',
#         attribute='item',
#         widget=ForeignKeyWidget(Item, 'name') 
#     )
#     batch = fields.Field(
#         column_name='Batch',
#         attribute='batch',
#         widget=ForeignKeyWidget(Batch, 'name')  
#     )
#     quantity = fields.Field(
#         column_name='quantity',
#         attribute='quantity',
#         widget=DecimalWidget() 
#     )

#     class Meta:
#         model = Stock
#         fields = [
#             'code', 'screen_name', 'project', 'warehouse', 'item', 'batch', 'quantity',
#         ]
#         export_order = fields
#         import_fields = fields
#         import_id_fields = ('code',)

# class StockResource(resources.ModelResource):
#     doc_code = Field(column_name='Document Code', )
#     screen_name = Field(column_name='Screen Name', )
#     date = Field(column_name = 'Date',attribute = 'created_on',widget=DateWidget('%Y-%m-%d'))
#     project = Field(column_name='Project',)
#     warehouse = Field(column_name='Warehouse',)
#     batch = Field(column_name='Batch',)
#     item_code = Field(column_name='Item Code', )
#     item = Field(column_name='Item', )
#     quantity = Field(column_name='Quantity', )

#     class Meta:
#         model = Stock
#         fields = ('doc_code', 'screen_name', 'date', 'project', 'warehouse','batch', 'item_code', 'item',
#                   'quantity',
#                  )
#         export_order = fields

#     def dehydrate_doc_code(self, obj):
#         return obj.get('os_doc_code', '')
    
#     def dehydrate_screen_name(self, obj):
#         return obj.get('os_screen_name', '')
    
#     def dehydrate_date(self, obj):
#         return obj.get('os_date', '')
    
#     def dehydrate_project(self, obj):
#         return obj.get('os_project_name', '')
    
#     def dehydrate_warehouse(self, obj):
#         return obj.get('os_warehouse_name', '')
    
#     def dehydrate_batch(self, obj):
#         return obj.get('os_batch_name', '')
    
#     def dehydrate_item_code(self, obj):
#         return obj.get('os_item_code', '')
    
#     def dehydrate_item(self, obj):
#         return obj.get('os_item_name','')
    
#     def dehydrate_quantity(self, obj):
#         return obj.get('os_quantity',0)


class StockResource(resources.Resource):
    doc_code = fields.Field(column_name='Document Code')
    date = fields.Field(column_name='Date')
    item = fields.Field(column_name='Item Name')
    warehouse = fields.Field(column_name='Warehouse Name')
    project = fields.Field(column_name='Project Name')
    quantity = fields.Field(column_name='Received Quantity')

    class Meta:
        fields = ('doc_code', 'date', 'item', 'warehouse','quantity')
        export_order = fields

    def dehydrate_doc_code(self, obj):
        return obj.get('os_doc_code', '')

    def dehydrate_date(self, obj):
        date = obj.get('os_date')
        return date.strftime('%d-%m-%Y') if date else ''

    def dehydrate_item(self, obj):
        return obj.get('os_item_name', '')

    def dehydrate_warehouse(self, obj):
        return obj.get('os_warehouse_name', '')

    def dehydrate_project(self, obj):
        return obj.get('os_project_name', '')

    def dehydrate_quantity(self, obj):
        return obj.get('os_quantity', 0)




class StockAgainstBatchResource(resources.ModelResource):
    warehouse = fields.Field(attribute='warehouse', column_name='Warehouse')
    item = fields.Field(attribute='item', column_name='item')
    batch = fields.Field(attribute='batch', column_name='Batch')
    total_quantity = fields.Field(attribute='quantity', column_name='quantity')

    class Meta:
        model = Stock
        fields = ('warehouse', 'item', 'batch', 'quantity')
        export_order = fields
        import_fields = fields
        import_id_fields = ('code',)
    
    def dehydrate_warehouse(self, obj):
        return obj.get('warehouse', '') or ''
    def dehydrate_item(self, obj):
        return obj.get('item', '') or ''
    def dehydrate_batch(self, obj):
        return obj.get('batch', '') or ''
    def dehydrate_total_quantity(self, obj):
        return obj.get('quantity', 0) or 0


class StockAgainstWareHouseResource(resources.ModelResource):
    warehouse = fields.Field(attribute='warehouse', column_name='Warehouse')
    item = fields.Field(attribute='item', column_name='item')
    total_quantity = fields.Field(attribute='quantity', column_name='quantity')

    class Meta:
        model = Stock
        fields = ('warehouse', 'item', 'quantity')
        export_order = fields
        import_fields = fields
        import_id_fields = ('code',)


    def dehydrate_warehouse(self, obj):
        return obj.get('warehouse', '') or ''
    def dehydrate_item(self, obj):
        return obj.get('item', '') or ''
    def dehydrate_total_quantity(self, obj):
        return obj.get('quantity', 0) or 0
    

       
class StockMovementResource(resources.ModelResource):
    doc_code = Field(column_name='Document Code', attribute='doc_code')
    item = Field(column_name='Item', attribute='item__name')
    warehouse = Field(column_name='Warehouse', attribute='warehouse__name')
    project = Field(column_name='Project', attribute='project__name')
    opening_quantity = Field(column_name='Opening Quantity', attribute='opening_quantity')
    mrn_quantity = Field(column_name='MRN Quantity', attribute='mrn_quantity')
    mrn_return_quantity = Field(column_name='MRN Return Quantity', attribute='mrn_return_quantity')
    mi_quantity = Field(column_name='Material Issue Quantity', attribute='mi_quantity')
    production_quantity = Field(column_name='Production Quantity', attribute='production_quantity')
    closing_balance = Field(column_name='Closing Balance', attribute='closing_balance')

    class Meta:
        model = Stock
        fields = ('doc_code','item','warehouse', 'project','opening_quantity','mrn_quantity','mrn_return_quantity','mi_quantity','production_quantity','closing_balance',)
        export_order = fields
        import_fields = fields
        import_id_fields = ('code',)
    
    def dehydrate_warehouse(self, obj):
        return obj['warehouse__name'] or ''
    
    def dehydrate_project(self, obj):
        return obj['project__name'] or ''
    
    def dehydrate_doc_code(self, obj):
        return obj['doc_code'] or ''
    
    def dehydrate_item(self, obj):
        return obj['item__name'] or ''
    
    def dehydrate_opening_quantity(self, obj):
        return obj.get('opening_quantity',0)
    
    def dehydrate_mrn_quantity(self, obj):
        return obj.get('mrn_quantity',0)
    
    def dehydrate_mrn_return_quantity(self, obj):
        return obj.get('mrn_return_quantity',0)
    
    def dehydrate_mi_quantity(self, obj):
        return obj.get('mi_quantity',0)
    
    def dehydrate_production_quantity(self, obj):
        return obj.get('production_quantity',0)
    
    def dehydrate_closing_balance(self, obj):
        return obj.get('closing_balance',0)
    


