from django.contrib import admin
from import_export.admin import ImportExportMixin

from Core.Core.admin.CoreAdmin import CoreAdmin
from ProjectManagement.models import PerformanceBankGuarantee, PerformanceBankGuaranteeHistory, Project, ProjectItem,ProjectGroup,ProjectGroupUser
from ProjectManagement.resources import ProjectResource, ProjectItemResource

from Core.Core.utils.utils import ac_filter

# Register your models here.
class ProjectAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    resource_class = ProjectResource
    user_related_fields = ['created_by', 'modified_by']
    fields = [
        'name', 'project_no', 'start_date', 'due_date', 'amount', 'gst_percentage', 'total_value', 
        'tax', 'taxtype', 'taxamount', 'taxable_amount', 'warrenty_period', 'tender', 'tender_no', 
        'company', 'tender_type', 'product_type', 'sourceportal', 'department_name', 'customer', 
        'manager', 'status', 'tender_datetime', 'tender_due_datetime', 'tender_open_datetime', 
        'deliver_terms', 'financial_terms', 'remarks', 'is_performace_bank_guarantee', 
        'is_pre_dispatch_inspection', 'is_inspection_agency', 'is_stagewise_inspection', 
        'inspection_agency', 'delivery_in_lots'
    ]

    list_display = (
        'code', 'name', 'project_no', 'start_date', 'due_date', 'amount', 'gst_percentage', 'total_value', 
        'tax', 'taxtype', 'taxamount', 'taxable_amount', 'warrenty_period', 'tender', 'tender_no', 
        'company', 'tender_type', 'product_type', 'sourceportal', 'department_name', 'customer', 
        'manager', 'status', 'tender_datetime', 'tender_due_datetime', 'tender_open_datetime', 
        'deliver_terms', 'financial_terms', 'remarks', 'is_performace_bank_guarantee', 
        'is_pre_dispatch_inspection', 'is_inspection_agency', 'is_stagewise_inspection', 
        'inspection_agency', 'delivery_in_lots'
    )

    list_filter = ['company', 'customer',]
    search_fields = ['code', 'project_no', 'name']
    list_per_page = 25


class ProjectItemAdmin(ImportExportMixin, CoreAdmin, admin.ModelAdmin):
    resource_class = ProjectItemResource
    user_related_fields = ['created_by', 'modified_by']
    fields = [
        'project', 'tenderitemmaster', 'price', 'quantity', 
    ]

    list_display = (
        'code', 'project', 'tenderitemmaster', 'price', 'quantity', 
        'created_on', 'created_by', 'modified_on', 'modified_by'
    )

    list_filter = [
        ac_filter('project'), ac_filter('tenderitemmaster'), 
    ]

    ordering = ('created_on',)
    search_fields = ['code', 'project__name', 'tenderitemmaster__name', ]
    list_per_page = 25

    readonly_fields = ['code', 'created_on', 'created_by', 'modified_on', 'modified_by']

    def has_delete_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        obj.save()



admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectItem, ProjectItemAdmin)
admin.site.register(ProjectGroup)
admin.site.register(ProjectGroupUser)
admin.site.register(PerformanceBankGuarantee)
admin.site.register(PerformanceBankGuaranteeHistory)




