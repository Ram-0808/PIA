from django.db import models

from Core.Users.models import CodeModel, CoreModel
from Users.models import User
from Masters.models import Account, InspectionAgency, SourcePortal, Item,  Tax


    

class Project(CoreModel):

    TENDER = 1
    PROJECT = 2

    STATUS_CHOICES = (
            (TENDER, 'Tender'),
            (PROJECT, 'Project')
    )


    OPENTENDER = 1
    LIMITEDTENDER = 2
    SBC = 3

    TENDERTYPE_CHOICES = (
            (OPENTENDER, 'OpenTender'),
            (LIMITEDTENDER, 'LimitedTender'),
            (SBC, 'SBC')
    )

    PRODUCT = 1
    SERVICE = 2

    PRODUCTTYPE_CHOICES = (
            (PRODUCT, 'Product'),
            (SERVICE, 'Service')
    )

    TAXTYPE_CHOICES = (
        ( 1 , "Inclusive"),
        ( 2 , "Exclusive"), 
    )

    name = models.TextField(default='', blank=True, null=True, unique=True)
    project_no = models.CharField(max_length=20, db_index=True, blank=True,null=True)
    start_date = models.DateTimeField(null=True,blank=True)
    due_date = models.DateTimeField(null=True,blank=True)
    amount = models.DecimalField( max_digits=30, decimal_places=2,default=0, null=True)
    # default_value = models.DecimalField( max_digits=30, decimal_places=2,default=0, null=True)
    # gst = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    gst_percentage = models.IntegerField(default=0, null=True)
    total_value = models.DecimalField( max_digits=30, decimal_places=2,default=0, null=True)
    # gst_no = models.CharField(max_length=50, db_index=True, blank=True,null=True)
    tax = models.ForeignKey(Tax, on_delete=models.RESTRICT, related_name="projects", null=True, blank=True)
    taxtype = models.SmallIntegerField(default=1, choices= TAXTYPE_CHOICES, blank=True, null=True, )
    taxamount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    taxable_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    warrenty_period = models.IntegerField(default=0, blank=True, null=True)
    tender = models.ForeignKey('TenderManagement.Tender', related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    plazo_tender = models.ForeignKey('TenderManagement.PlazoTender', related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    tender_no = models.CharField(max_length=20, db_index=True, blank=True,null=True)
    company = models.ForeignKey('DynamicDjango.Company', related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    location = models.ForeignKey('DynamicDjango.Location', related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    tender_type = models.SmallIntegerField(choices = TENDERTYPE_CHOICES, blank=True, null=True)
    product_type = models.SmallIntegerField(choices = PRODUCTTYPE_CHOICES, blank=True, null=True)
    sourceportal = models.ForeignKey(SourcePortal, related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    department_name = models.CharField(max_length=180,  blank=True,null=True)
    # document = models.FileField(upload_to = 'project_doc', default = '', null=True, blank=True )
    customer = models.ForeignKey(Account, related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    order_placing_authority = models.ForeignKey(Account, related_name='projects_op', on_delete=models.RESTRICT, null=True) 
    manager = models.ForeignKey(User, related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    # team = models.ForeignKey(User, related_name='project', )
    status = models.SmallIntegerField(choices = STATUS_CHOICES, blank=True, null=True, default=1)
    tender_datetime = models.DateTimeField(null=True,blank=True)
    tender_due_datetime = models.DateTimeField(null=True,blank=True)
    tender_open_datetime = models.DateTimeField(null=True,blank=True)
    deliver_terms = models.TextField(default='', blank=True, null=True,)
    financial_terms = models.TextField(default='', blank=True, null=True, )
    remarks = models.TextField(default='', blank=True, null=True, )
    # performace_bank_guarantee = models.ForeignKey(PerformanceBankGuarantee, related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    is_performace_bank_guarantee=models.BooleanField(blank=False, default=False, null=True)
    is_pre_dispatch_inspection=models.BooleanField(blank=False, default=False, null=True)
    is_inspection_agency=models.BooleanField(blank=False, default=False, null=True)
    is_stagewise_inspection=models.BooleanField(blank=True, default=False, null=True)
    inspection_agency = models.ForeignKey(InspectionAgency, related_name='projects', on_delete=models.RESTRICT, null=True, blank=True)
    delivery_in_lots = models.IntegerField(default=0, null=True, blank=False,)



    CODE_PREFIX = 'PRJ'
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"


    def __str__(self):
        return self.code
    


    

class ProjectItem(CoreModel):

    TAXTYPE_CHOICES = (
        ( 1 , "Inclusive"),
        ( 2 , "Exclusive"), 
    )
    
    project = models.ForeignKey(Project, related_name='project_items', on_delete=models.RESTRICT, null=True)
    tenderitemmaster = models.ForeignKey(Item, related_name='project_items', on_delete=models.RESTRICT, null=True)
    quantity = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.RESTRICT, related_name="project_items", null=True, blank=True)
    taxtype = models.SmallIntegerField(default=1, choices= TAXTYPE_CHOICES, blank=True, null=True, )
    discount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    
    
    CODE_PREFIX = 'PRJI'
    
    class Meta:
        verbose_name = "ProjectItem"
        verbose_name_plural = "ProjectItems"


    def __str__(self):
        return self.code
    

class ProjectDueDateDocument(CodeModel):
    project = models.ForeignKey(Project, related_name='project_due_date_documents', on_delete=models.RESTRICT, null=True)
    extended_due_date = models.DateTimeField(null=True,blank=True)
    file = models.FileField(upload_to="", null=True, default=None)

    CODE_PREFIX = 'PDDD'
    
    class Meta:
        verbose_name = "ProjectDueDateDocument"
        verbose_name_plural = "ProjectDueDateDocuments"

    def __str__(self):
        return self.code
    



class ProjectDocuments(CodeModel):
    project = models.ForeignKey(Project, related_name='project_document', on_delete=models.RESTRICT, null=True)
    file = models.FileField(upload_to="", null=True, default=None)

    CODE_PREFIX = 'PRDS'
    
    class Meta:
        verbose_name = "ProjectDocuments"
        verbose_name_plural = "ProjectDocuments"

    def __str__(self):
        return self.code
    



class ProjectGroup(CodeModel):
    project = models.ForeignKey(Project, related_name='project_groups', on_delete=models.RESTRICT, null=True)
    name = models.CharField(max_length=20, db_index=True, blank=True,null=True)

    CODE_PREFIX = 'PG'
    
    class Meta:
        verbose_name = "ProjectGroup"
        verbose_name_plural = "ProjectGroups"


    def __str__(self):
        return self.code
    

class ProjectGroupUser(CodeModel):
    group = models.ForeignKey(ProjectGroup, related_name='project_group_users', on_delete=models.RESTRICT, null=True)
    user = models.ForeignKey(User, related_name='project_group_users', on_delete=models.RESTRICT, null=True)

    CODE_PREFIX = 'PGU'
    
    class Meta:
        verbose_name = "ProjectGroupUser"
        verbose_name_plural = "ProjectGroupUsers"


    def __str__(self):
        return self.code
    


class PerformanceBankGuarantee(CoreModel):
    project = models.ForeignKey(Project, related_name='performancebankguarantee', on_delete=models.RESTRICT, null=True)
    number = models.CharField(max_length=100,null=True, blank=True)
    value = models.CharField(max_length=100,null=True, blank=True)
    issuedate = models.DateField(null=True, blank=True)
    expirydate = models.DateField(null=True, blank=True)
    claimdate = models.DateField(null=True, blank=True)
    remarks = models.TextField(default='', blank=True, null=True)
    file = models.FileField(upload_to='pbg_documents', null=True, default=None)

    CODE_PREFIX = 'PBG'

    class Meta:
        permissions = (
            ("can_view_pbg_commonlist", "Can View PBG Common List"),
            ("change_pbg_extended_due_date", "Can Change PBG Extended DueDate"),
            ("add_pbg_commonlist", "Can Add PBG Common List"),
            ("change_pbg_commonlist", "Can Change PBG Common List"),
            ("delete_pbg_commonlist", "Can Delete PBG Common List"),
        )

    __str__ = lambda self: str(self.number)


class PerformanceBankGuaranteeHistory(CoreModel):
    project = models.ForeignKey(Project, related_name='performancebankguaranteehistory', on_delete=models.RESTRICT, null=True)
    pbg = models.ForeignKey(PerformanceBankGuarantee, related_name='performancebankguaranteehistory', on_delete=models.RESTRICT, null=True,blank=True)
    issuedate = models.DateField(null=True, blank=True)
    expirydate = models.DateField(null=True, blank=True)
    claimdate = models.DateField(null=True, blank=True)
    remarks = models.TextField(default='', blank=True, null=True)
    file = models.FileField(upload_to='pbg_documents', null=True, default=None)

    CODE_PREFIX = 'PBGH'

    __str__ = lambda self: str(self.project.name)



class ProjectDocuments(CodeModel):
    project = models.ForeignKey(Project, related_name='project_document', on_delete=models.RESTRICT, null=True)
    file = models.FileField(upload_to="", null=True, default=None)

    CODE_PREFIX = 'PRDS'
    
    class Meta:
        verbose_name = "ProjectDocuments"
        verbose_name_plural = "ProjectDocuments"

    def __str__(self):
        return self.code
    



class Stock(models.Model):
    code = models.CharField(max_length=255, primary_key=True)  # Use 'code' as the primary key
    doc_code = models.CharField(max_length=255,)
    date = models.DateField(null=True, blank=True)
    screen_name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name="stock", null=True, blank=True)
    warehouse = models.ForeignKey('DynamicDjango.WareHouse', on_delete=models.DO_NOTHING, related_name="stock", null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="stock", null=True, blank=True)
    batch = models.ForeignKey('Masters.Batch', on_delete=models.DO_NOTHING, related_name="stock", null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)

    class Meta:
        managed = False
        db_table = "stock_view"
        permissions = (
            ("view_stock_report", "Can View Stock Report"),
            )
        

        