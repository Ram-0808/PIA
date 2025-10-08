from django.contrib import admin

# Register your models here.
from django.contrib import admin
from import_export.admin import ImportExportMixin


from Core.Core.admin.CoreAdmin import CoreAdmin
from Core.Core.utils.utils import ac_filter
from TenderManagement.resources import TenderItemMasterResource, TenderItemMasterItemResource, TenderCommentsResource, CaseSheetResource

# from .resources import *
from .models import *





class TenderItemMasterAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    resource_class = TenderItemMasterResource
    user_related_fields = ['created_by', 'modified_by']
    fields = ['name']
    list_display = ('id','code','name','created_on','created_by','modified_on','modified_by')
    
    ordering=('created_on',)

    search_fields = ['code']
    list_per_page=25

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()


class TenderItemMasterItemAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    resource_class = TenderItemMasterItemResource
    fields = ['tenderitemmaster','item','quantity',]
    list_display = ('id','code','tenderitemmaster','item','quantity','created_on','created_by','modified_on','modified_by')
    list_filter =[(ac_filter('tenderitemmaster',)),
                  (ac_filter('item',))
                  
                ]
    user_related_fields = ['created_by', 'modified_by']
    ordering=('created_on',)

    search_fields = ['code']
    list_per_page=25

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()


class TenderAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    fields = ['project','is_lead_required','lead','tender_no','tender_type','product_type','authorized_status','department_name','sourceportal','company','location','tender_datetime','is_reverse_auction','pre_bid_place','pre_bid_meet_address', 'tender_open_datetime','pre_bid_date','ministry','annual_turnover','years_of_experiance','is_mss_exemption','is_start_exemption','documents_required_seller','time_allowed_clarification_days','is_inspection','evaluation_method','description','screen_type',] #'assign_to',
    list_display = ('id','code','project','is_lead_required','lead','tender_no','tender_type','product_type','authorized_status','department_name','sourceportal','company','location','tender_datetime','is_reverse_auction','pre_bid_place','pre_bid_meet_address', 'tender_open_datetime','pre_bid_date','ministry','annual_turnover','years_of_experiance','is_mss_exemption','is_start_exemption','documents_required_seller','time_allowed_clarification_days','is_inspection','evaluation_method', 'screen_type', 'created_on','created_by','modified_on','modified_by')
    list_filter =[(ac_filter('project',)),
                  ]
    user_related_fields = ['created_by', 'modified_by']
    ordering=('created_on',)

    search_fields = ['code']
    list_per_page=25

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()




class TenderCommentsAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    resource_class = TenderCommentsResource
    user_related_fields = ['created_by', 'modified_by']
    fields = ['tender','comment']
    list_display = ('id','code', 'tender', 'comment', 'created_on', 'created_by', 'modified_on', 'modified_by')
    
    list_filter =[(ac_filter('tender',)),
                 ]
   
    ordering=('created_on',)

    search_fields = ['code']
    list_per_page=25

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()


class TenderAttachmentsAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    # resource_class = TenderCommentsResource
    user_related_fields = ['created_by', 'modified_by']
    fields = ['tender','file']
    list_display = ('id','code', 'tender', 'file', 'created_on', 'created_by', 'modified_on', 'modified_by')
    list_filter =[(ac_filter('tender',)),
                 ]
    ordering=('created_on',)

    search_fields = ['code']
    list_per_page=25

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()



class CasesheetAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    resource_class = CaseSheetResource
    user_related_fields = ['created_by', 'modified_by']
    fields = ['tender','pre_bid_date','pre_bid_subject', 'contact_person', 'phone', 'email', 'authorized_status', 'last_tender_rate', 'last_tender_date', 'estimate_bid_price', 'oem_challenges', 'department_challenges', 'is_extension_request', 'is_site_visit', 'costing_remarks', 'remarks']
    list_display = ('id','code', 'tender','pre_bid_date','pre_bid_subject', 'contact_person', 'phone', 'email', 'authorized_status', 'last_tender_rate', 'last_tender_date', 'estimate_bid_price', 'oem_challenges', 'department_challenges', 'is_extension_request', 'is_site_visit', 'costing_remarks', 'remarks', 'created_on', 'created_by', 'modified_on', 'modified_by')
    
    ordering=('created_on',)

    search_fields = ['code']
    list_per_page=25

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()



admin.site.register(TenderItemMaster, TenderItemMasterAdmin)
admin.site.register(TenderItemMasterItem, TenderItemMasterItemAdmin)
admin.site.register(Tender, TenderAdmin)
admin.site.register(TenderComments, TenderCommentsAdmin)
admin.site.register(TenderAttachments,TenderAttachmentsAdmin )
admin.site.register(CaseSheet,CasesheetAdmin )
admin.site.register(BudgetEnquiry )
admin.site.register(PDFExtraction)
admin.site.register(TenderItem)
admin.site.register(TenderItemAssign)


admin.site.register(RawMaterial)
from .models import SecurityDeposit

@admin.register(SecurityDeposit)
class SecurityDepositAdmin(admin.ModelAdmin):
    list_display = ['customer', 'project', 'type', 'amount', 'status', 'received_on', 'due_expiry_date']
    list_filter = ['type', 'status', 'received_on', 'due_expiry_date']
    search_fields = ['customer__name', 'project__name']
    ordering = ['-received_on']