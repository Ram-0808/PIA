from django.db import models

from LeadManagement.models import Lead

from Masters.models import   Item, MiscellaneousTypes,  Unit, Account , SourcePortal,  Document, Stage 

from Core.Users.models import CoreModel, CodeModel
from Users.models import User




class TenderManager(models.Manager):
    
    def get_filter(self, *args, **kwargs):
       
        queryset = super().filter(*args, **kwargs)
        queryset = queryset.filter(is_deleted=False,screen_type = 1)
 
        return queryset
    
class BudgetEnquiryManager(models.Manager):
    
    def get_filter(self, *args, **kwargs):
       
        queryset = super().filter(*args, **kwargs)
        queryset = queryset.filter(is_deleted=False,screen_type = 2)
 
        return queryset



class TenderItemMaster(CodeModel):
    name = models.TextField(default='', blank=True, null=True, unique=True)
    
    CODE_PREFIX = 'TDM'
    
    class Meta:
        verbose_name = "TenderItemMaster"
        verbose_name_plural = "TenderItemMasters"

    def __str__(self):
        return self.code
    

class TenderItemMasterItem(CodeModel):

    tenderitemmaster = models.ForeignKey(TenderItemMaster, related_name='tendermasteritems', on_delete=models.RESTRICT, null=True)
    item = models.ForeignKey(Item, related_name='tendermasteritems', on_delete=models.RESTRICT, null=True)
    quantity = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    
    CODE_PREFIX = 'TDM'
    
    class Meta:
        verbose_name = "TenderItemMasterItem"
        verbose_name_plural = "TenderItemMasterItems"

    def __str__(self):
        return self.code
    

    

class TenderAbstract(CoreModel):

    OPENTENDER = 1
    LIMITEDTENDER = 2
    SBC = 3

    TENDERTYPE_CHOICES = (
            (OPENTENDER, 'OpenTender'),
            (LIMITEDTENDER, 'LimitedTender'),
            (SBC, 'SBC')
    )

    SUPPLY = 1
    SERVICE = 2
    BOTH = 3

    PRODUCTTYPE_CHOICES = (
            (SUPPLY, 'Supply'),
            (SERVICE, 'Service'),
            (BOTH, 'Both'),
    )

    TENDER = 1
    BUDGETENQUIRY = 2
    PLAZOTENDER = 3

    SCREENTYPE_CHOICES = (
            (TENDER, 'Tender'),
            (BUDGETENQUIRY, 'BudgetEnquiry'),
            (PLAZOTENDER, 'PlazoTender')
    )

    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    CANCELLED = 4
    CONVERTEDTOPROJECT = 5


    STATUS_CHOICES = (
            (PENDING, 'Pending'),
            (APPROVED, 'Approved'),
            (REJECTED, 'Rejected'),
            (CANCELLED, 'Cancelled'),
            (CONVERTEDTOPROJECT, 'Converted To Project'),
    )

    name = models.CharField(max_length=300, null=True, blank=True)
    assigned_on = models.DateTimeField(null=True,blank=True) #bid assigned on date
    project = models.ForeignKey('ProjectManagement.Project', related_name='tender_project', on_delete=models.RESTRICT, null=True)
    is_lead_required = models.BooleanField(default=False, blank=True, null=True)
    lead = models.ForeignKey(Lead, related_name='tender', on_delete=models.RESTRICT, null=True, blank =True)
    tender_no = models.CharField(max_length=20, db_index=True, blank=True,null=True)
    tender_type = models.SmallIntegerField(choices = TENDERTYPE_CHOICES, blank=True, null=True)
    screen_type = models.SmallIntegerField(choices = SCREENTYPE_CHOICES, blank=True, null=True)
    product_type = models.SmallIntegerField(choices = PRODUCTTYPE_CHOICES, blank=True, null=True)
    status = models.SmallIntegerField(choices = STATUS_CHOICES, blank=True, null=True, default=1) #status
    department_name = models.CharField(max_length=180,  blank=True,null=True)
    sourceportal = models.ForeignKey(SourcePortal, related_name='tender', on_delete=models.RESTRICT, null=True) 
    company = models.ForeignKey('DynamicDjango.Company', related_name='tender', on_delete=models.RESTRICT, null=True) 
    location = models.ForeignKey('DynamicDjango.Location', related_name='tender', on_delete=models.RESTRICT, null=True) 
    customer = models.ForeignKey(Account, related_name='tender', on_delete=models.RESTRICT, null=True) 
    order_placing_authority = models.ForeignKey(Account, related_name='tenders_op', on_delete=models.RESTRICT, null=True) 
    tender_datetime = models.DateTimeField(null=True,blank=True) #tender End date
    tender_extension_datetime = models.DateTimeField(null=True,blank=True)
    pre_bid_place = models.CharField(max_length=180,  blank=True,null=True) #pre_bid_meet place
    pre_bid_meet_address = models.CharField(max_length=180, null=True, blank=True)
    tender_open_datetime = models.DateTimeField(null=True,blank=True)
    pre_bid_date = models.DateField(null=True,blank=True) #pre bidmeet date
    ministry = models.CharField(max_length=180, null=True, blank=True) #ministry/state
    annual_turnover = models.TextField(default='', blank=True, null=True) #annual_turnover income
    years_of_experiance = models.DecimalField( max_digits=30, decimal_places=2,default=0, null=True)
    is_reverse_auction = models.BooleanField(default=False, blank=True, null=True)
    is_mss_exemption = models.BooleanField(default=False, blank=True, null=True)
    is_start_exemption = models.BooleanField(default=False, blank=True, null=True) # startup exemption
    documents_required_seller = models.TextField(default='', blank=True, null=True)
    time_allowed_clarification_days = models.TextField(default='', blank=True, null=True)
    is_inspection = models.BooleanField(default=False, blank=True, null=True)
    is_order_placing_authority = models.BooleanField(default=False, blank=True, null=True)
    evaluation_method = models.CharField(max_length=180, null=True, blank=True)
    tender_stage = models.ForeignKey(Stage, related_name='tender', on_delete=models.RESTRICT, null=True) 
    description = models.TextField(default='', blank=True, null=True)

    CODE_PREFIX = 'TDR'
    
    class Meta:
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"
        abstract = True

        permissions = (
            ("can_assign", "Can Assign Tender"),
            ("can_view_cst_overview", "Can View CST Overview"),
            ("can_view_be_cst_overview", "Can View Budget Enquiry CST Overview"),
            ("view_budget_enquiry", "Can View Budget Enquiry"),
            ("add_budget_enquiry", "Can Add Budget Enquiry"),
            ("change_budget_enquiry", "Can Change Budget Enquiry"),
            ("delete_budget_enquiry", "Can Delete Budget Enquiry"),
        )

    def __str__(self):
        return self.code
    

class Tender(TenderAbstract):
    objects = TenderManager()
    pass


class TenderItem(CoreModel):

    tender = models.ForeignKey(Tender, related_name='tender_items', on_delete=models.RESTRICT, null=True)
    tenderitemmaster = models.ForeignKey(Item, related_name='tender_items', on_delete=models.RESTRICT, null=True)
    is_rfq_required = models.BooleanField(default=False, null=True, blank=True)
    item_specifications = models.TextField(default='', blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT, related_name="tender_items", null=True, blank=True)
    quantity = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    
    CODE_PREFIX = 'TDRI'
    
    class Meta:
        verbose_name = "TenderItem"
        verbose_name_plural = "TenderItems"
        permissions = (
            ("view_budget_enquiry_item", "Can View Budget Enquiry Item"),
            ("add_budget_enquiry_item", "Can Add Budget Enquiry Item"),
            ("change_budget_enquiry_item", "Can Change Budget Enquiry Item"),
            ("delete_budget_enquiry_item", "Can Delete Budget Enquiry Item"),
        )


    def __str__(self):
        return self.code
    
    
class TenderItemAssign(CoreModel):

    tender = models.ForeignKey(Tender, related_name='tender_items_assign', on_delete=models.RESTRICT, null=True)
    tender_item = models.ForeignKey(TenderItem, related_name='tender_items_assign', on_delete=models.RESTRICT, null=True)
    tenderitemmaster = models.ForeignKey(Item, related_name='tender_items_assign', on_delete=models.RESTRICT, null=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT,related_name='tender_items_assign',blank=True, null=True)
    
    CODE_PREFIX = 'TDRIA'
    
    class Meta:
        verbose_name = "TenderItemAssign"
        verbose_name_plural = "TenderItemAssignies"


    def __str__(self):
        return self.code

    
class TenderComments(CodeModel):

    tender = models.ForeignKey(Tender, related_name='tedner_comments', on_delete=models.RESTRICT, null=True)
    comment = models.CharField(max_length=300, null=True, blank=True)

    CODE_PREFIX = 'CMT'
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

        permissions = (
            ("view_be_comments", "Can View BE Comments"),
            ("add_be_comments", "Can Add BE Comments"),
            ("change_be_comments", "Can Change BE Comments"),
            ("delete_be_comments", "Can Delete BE Comments"),            
            )
    
    
    def __str__(self):
        return str(self.code)
    

    

class TenderAttachments(CodeModel):

    tender = models.ForeignKey(Tender, related_name='tedner_attachments', on_delete=models.RESTRICT, null=True)
    file = models.FileField(upload_to="", null=True, blank=True)

    CODE_PREFIX = 'TDA'
    
    class Meta:
        verbose_name = "TenderAttachment"
        verbose_name_plural = "TenderAttachments"

    
    def __str__(self):
        return str(self.code)
    



class CaseSheet(CoreModel):
    
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    CANCELLED = 4

    STATUS_CHOICES = (
            (PENDING, 'Pending'),
            (APPROVED, 'Approved'),
            (REJECTED, 'Rejected'),
            (CANCELLED, 'Cancelled'),
    )

    tender = models.ForeignKey(Tender, related_name='casesheet', on_delete=models.RESTRICT, null=True)
    pre_bid_date = models.DateTimeField(null=True,blank=True)
    pre_bid_subject = models.TextField(default='', blank=True, null=True)
    contact_person = models.CharField(max_length=300, null=True, blank=True)
    phone = models.CharField(max_length=15, db_index=True, blank=True, null=True,)
    email = models.EmailField(max_length=255, db_index=True, blank=True, null=True)
    last_tender_rate = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) #last purchase price
    last_tender_date  = models.DateField(null=True, blank=True) # Last PurchaseDate
    estimate_bid_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    oem_challenges = models.TextField(default='', blank=True, null=True)
    documents_not_submitted_evaluation_matrix = models.TextField(default='', blank=True, null=True)
    pendingdocumentsOEM = models.TextField(default='', blank=True, null=True)
    is_reverse_auction = models.BooleanField(default=False, blank=True, null=True)
    department_name = models.CharField(max_length=300, null=True, blank=True)
    department_challenges = models.TextField(default='', blank=True, null=True)
    is_extension_request = models.BooleanField(default=False, blank=True, null=True)
    is_site_visit = models.BooleanField(default=False, blank=True, null=True)
    costing_remarks = models.TextField(default='', blank=True, null=True) #Points to be Considered in Costing
    remarks = models.TextField(default='', blank=True, null=True)

    
    CODE_PREFIX = 'CST'
    
    class Meta:
        verbose_name = "Casesheet"
        verbose_name_plural = "Casesheets"


        permissions = (
            ("view_be_casesheet", "Can View BE CaseSheet"),
            ("add_be_casesheet", "Can Add BE CaseSheet"),
            ("change_be_casesheet", "Can Change BE CaseSheet"),
            ("delete_be_casesheet", "Can Delete BE CaseSheet"),            
            )

    def __str__(self):
        return self.code
    


class ReverseAuction(CodeModel):
    
    tender = models.ForeignKey(Tender, related_name='reverse_auction', on_delete=models.RESTRICT, null=True)
    tender_item_master = models.ForeignKey(Item, related_name='reverse_auction', on_delete=models.RESTRICT, null=True)
    tender_item = models.ForeignKey(TenderItem, related_name='reverse_auction', on_delete=models.RESTRICT, null=True)
    landing_cost = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    discount_landing_cost = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) 
    landing_cost_margin = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) #margin percentage from discount_landing_cost  like 30%
    landing_cost_margin_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) 
    landing_cost_total = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) # (discount_landing_cost + landing_cost_margin_amount)
    landing_cost_gst = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) # gst persentage like 30%
    landing_cost_gst_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    total = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) # (landing_cost_gst_amount + landing_cost_total)
    l1_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) # (landing_cost_gst_amount + landing_cost_total)
    diff_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True) # (total - l1_price)
    remarks = models.TextField(default='', blank=True, null=True) 

    
    CODE_PREFIX = 'RAU'
    
    class Meta:
        verbose_name = "ReverseAuction"
        verbose_name_plural = "ReverseAuctions"

        permissions = (
            ("can_l1_price_add", "Can Add L1price"),
            ("view_be_reverseauction", "Can View BE ReverseAuction"),
            ("add_be_reverseauction", "Can Add BE ReverseAuction"),
            ("change_be_reverseauction", "Can Change BE ReverseAuction"),
            ("delete_be_reverseauction", "Can Delete BE ReverseAuction"),            
            )
        

    def __str__(self):
        return self.code


class TenderDocuments(CodeModel):

    COMMON = 1
    INDIVIDUAL = 2

    TYPE_CHOICES = (
            (COMMON, 'Common'),
            (INDIVIDUAL, 'Individual')
            
    )

    tender = models.ForeignKey(Tender, related_name='tedner_documents', on_delete=models.RESTRICT, null=True)
    document = models.ForeignKey(Document, related_name='tedner_documents', on_delete=models.RESTRICT, null=True)
    document_name = models.CharField(max_length=300, null=True, blank=True)
    is_submitted = models.BooleanField(default=False, blank=True, null=True)
    type = models.SmallIntegerField(choices = TYPE_CHOICES, blank=True, null=True, default=1)
    file = models.FileField(upload_to="tedner_documents/", null=True, blank=True)

    CODE_PREFIX = 'TDS'
    
    class Meta:
        verbose_name = "TenderDocuments"
        verbose_name_plural = "TenderDocuments"

        permissions = (
            ("view_be_documents", "Can View BE Documents"),
            ("add_be_documents", "Can Add BE Documents"),
            ("change_be_documents", "Can Change BE Documents"),
            ("delete_be_documents", "Can Delete BE Documents"),            
            )

    
    def __str__(self):
        return str(self.code)





class BidAmount(CodeModel):
  
    tender = models.ForeignKey(Tender, related_name='bidamount', on_delete=models.RESTRICT, null=True)
    amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    l1_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    
    CODE_PREFIX = 'BAT'
    
    class Meta:
        verbose_name = "BidAmount"
        verbose_name_plural = "BidAmounts"

        permissions = (
            ("view_be_bidamounts", "Can View BE BidAmounts"),
            ("add_be_bidamounts", "Can Add BE BidAmounts"),
            ("change_be_bidamounts", "Can Change BE BidAmounts"),
            ("delete_be_bidamounts", "Can Delete BE BidAmounts"),            
            )


    def __str__(self):
        return self.code

    


class PDFExtraction(CodeModel):
    
    status = models.SmallIntegerField(blank=True, choices=[(1, 'Pending'), (2, 'Complete'), (3, 'Failed')], default=1, null=True)
    file = models.FileField(upload_to="pdfextraction/", null=True, blank=True)
    extarct_data = models.TextField(default='', blank=True, null=True)

    CODE_PREFIX = 'PET'
    
    __str__ = lambda self: str(self.code)


        
class CostingSheet(CoreModel):
    tender = models.ForeignKey(Tender, related_name='costingsheet', on_delete=models.RESTRICT, null=True)
    project = models.ForeignKey('ProjectManagement.Project', related_name='costingsheet', on_delete=models.RESTRICT, null=True)
    description = models.TextField(default='', blank=True, null=True)


    class Meta:
        verbose_name = "CostingSheet"
        verbose_name_plural = "CostingSheets"

    CODE_PREFIX = 'CS'

    __str__ = lambda self: str(self.code)

class Service(CodeModel):
    costingsheet = models.ForeignKey(CostingSheet, related_name='services', on_delete=models.RESTRICT, null=True)
    tender = models.ForeignKey(Tender, related_name='services', on_delete=models.RESTRICT, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="services", null= True, blank=True)
    days = models.IntegerField(default=1, blank =True, null= True)
    qty = models.DecimalField(max_digits=18, decimal_places=3,default=0, null=True)
    price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    total_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    duration = models.IntegerField(default=1, blank =True, null= True)
    margin_percent = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    overtime_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    remarks = models.TextField(default='', blank=True, null=True)

    class Meta:

        permissions = (
            ("view_be_service", "Can View BE Service"),
            ("add_be_service", "Can Add BE Service"),
            ("change_be_service", "Can Change BE Service"),
            ("delete_be_service", "Can Delete BE Service"),            
            )
        

    CODE_PREFIX = 'SER'

    __str__ = lambda self: str(self.code)


class Consumable(CodeModel):
    tender = models.ForeignKey(Tender, related_name='consumables', on_delete=models.RESTRICT, null=True)
    costingsheet = models.ForeignKey(CostingSheet, related_name='consumables', on_delete=models.RESTRICT, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="consumables", null= True, blank=True)
    qty = models.DecimalField(max_digits=18, decimal_places=3,default=0, null=True)
    price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    total_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_percent = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    remarks = models.TextField(default='', blank=True, null=True)

    class Meta:
        permissions = (
            ("view_be_consumable", "Can View BE Consumable"),
            ("add_be_consumable", "Can Add BE Consumable"),
            ("change_be_consumable", "Can Change BE Consumable"),
            ("delete_be_consumable", "Can Delete BE Consumable"),            
            )
        

    CODE_PREFIX = 'CON'

    __str__ = lambda self: str(self.code)


class OtherCharges(CodeModel):
    tender = models.ForeignKey(Tender, related_name='othercharges', on_delete=models.RESTRICT, null=True)
    costingsheet = models.ForeignKey(CostingSheet, related_name='othercharges', on_delete=models.RESTRICT, null=True)
    miscellaneoustype = models.ForeignKey(MiscellaneousTypes, on_delete=models.RESTRICT, related_name="rawmaterials", null= True, blank=True)
    name = models.CharField(max_length=180, unique=True)
    price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_percent = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    total_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    remarks = models.TextField(default='', blank=True, null=True)

    class Meta:
        permissions = (
            ("view_be_othercharges", "Can View BE OtherCharges"),
            ("add_be_othercharges", "Can Add BE OtherCharges"),
            ("change_be_othercharges", "Can Change BE OtherCharges"),
            ("delete_be_othercharges", "Can Delete BE OtherCharges"),            
            )
        

    CODE_PREFIX = 'OCH'

    __str__ = lambda self: str(self.code)


class RawMaterial(CodeModel):
    RAWITEM = 1
    CQITEM = 2

    TYPE_CHOICES = (
            (RAWITEM, 'Rawitem'),
            (CQITEM, 'Cqitem')
            
    )

    tender = models.ForeignKey(Tender, related_name='rawmaterials', on_delete=models.RESTRICT, null=True)
    costingsheet = models.ForeignKey(CostingSheet, related_name='rawmaterials', on_delete=models.RESTRICT, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="rawmaterials", null= True, blank=True)
    vendor = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="rawmaterials", null= True, blank=True)
    type = models.SmallIntegerField(choices = TYPE_CHOICES, blank=True, null=True, default=1)
    qty = models.DecimalField(max_digits=18, decimal_places=3,default=0, null=True)
    price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    total_price = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_percent = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    margin_amount = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    remarks = models.TextField(default='', blank=True, null=True)

    class Meta:
        permissions = (
            ("view_be_rawmaterial", "Can View BE RawMaterials"),
            ("add_be_rawmaterial", "Can Add BE RawMaterials"),
            ("change_be_rawmaterial", "Can Change BE RawMaterials"),
            ("delete_be_rawmaterial", "Can Delete BE RawMaterials"),            
            )
        
    CODE_PREFIX = 'RM'

    __str__ = lambda self: str(self.code)

class PlazoTender(CoreModel):

    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    CANCELLED = 4
    CONVERTEDTOPROJECT = 5


    STATUS_CHOICES = (
            (PENDING, 'Pending'),
            (APPROVED, 'Approved'),
            (REJECTED, 'Rejected'),
            (CANCELLED, 'Cancelled'),
            (CONVERTEDTOPROJECT, 'Converted To Project'),
    )

    project = models.ForeignKey('ProjectManagement.Project', related_name='plazo_tenders', on_delete=models.RESTRICT, null=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    tender_no = models.CharField(max_length=20, db_index=True, blank=True,null=True)
    assigned_on = models.DateTimeField(null=True,blank=True) #bid assigned on date
    status = models.SmallIntegerField(choices = STATUS_CHOICES, blank=True, null=True, default=1) #status
    customer = models.ForeignKey(Account, related_name='plazo_tenders', on_delete=models.RESTRICT, null=True) 
    description = models.TextField(default='', blank=True, null=True)

    CODE_PREFIX = 'PTD'
    
    class Meta:
        verbose_name = "PlazoTender"
        verbose_name_plural = "PlazoTenders"

    def __str__(self):
        return self.code


class PlazoTenderItem(CoreModel):

    plazo_tender = models.ForeignKey(PlazoTender, related_name='plazo_tender_items', on_delete=models.RESTRICT, null=True)
    item = models.ForeignKey(Item, related_name='plazo_tender_items', on_delete=models.RESTRICT, null=True)
    quantity = models.DecimalField( max_digits=18, decimal_places=2,default=0, null=True)
    
    CODE_PREFIX = 'PTDI'
    
    class Meta:
        verbose_name = "PlazoTenderItem"
        verbose_name_plural = "PlazoTenderItems"

    def __str__(self):
        return self.code



class PlazoTenderAttachment(CodeModel):

    plazo_tender = models.ForeignKey(PlazoTender, related_name='plazo_tender_attachments', on_delete=models.RESTRICT, null=True)
    file = models.FileField(upload_to="", null=True, blank=True)

    CODE_PREFIX = 'PTA'
    
    class Meta:
        verbose_name = "PlazoTenderAttachment"
        verbose_name_plural = "PlazoTenderAttachments"

    
    def __str__(self):
        return str(self.code)
    

class TenderCheckListItems(CodeModel):
    name = models.CharField(max_length=300, null=True, blank=True)
    tender = models.ForeignKey(Tender, related_name='tender_checklist_items', on_delete=models.CASCADE, null=True, blank=True)
    tender_checklist = models.ForeignKey('Masters.TenderCheckList', related_name='tender_checklist_items', on_delete=models.RESTRICT, null=True, blank=True)
    tender_condition = models.TextField(default='', blank=True, null=True)
    deviation_from_pia_norms = models.BooleanField(default=False, null=True, blank=True)
    pia_remarks = models.TextField(default='', blank=True, null=True)
    cost_implication = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True, blank=True, help_text="Cost implication in INR")

    CODE_PREFIX = 'TCLI'

    class Meta:
        verbose_name = "Tender CheckList Item"
        verbose_name_plural = "Tender CheckList Items"
        unique_together = ['tender', 'tender_checklist']

    def __str__(self):
        return f"{self.tender.code if self.tender else 'N/A'} - {self.tender_checklist.name if self.tender_checklist else 'N/A'}"


class BudgetEnquiry(TenderAbstract):
    project = models.ForeignKey('ProjectManagement.Project', related_name='tender_budget_enquiry_project', on_delete=models.RESTRICT, null=True)
    lead = models.ForeignKey(Lead, related_name='tender_budget_enquiry', on_delete=models.RESTRICT, null=True, blank =True)
    sourceportal = models.ForeignKey(SourcePortal, related_name='tender_budget_enquiry', on_delete=models.RESTRICT, null=True) 
    company = models.ForeignKey('DynamicDjango.Company', related_name='tender_budget_enquiry', on_delete=models.RESTRICT, null=True) 
    location = models.ForeignKey('DynamicDjango.Location', related_name='tender_budget_enquiry', on_delete=models.RESTRICT, null=True) 
    customer = models.ForeignKey(Account, related_name='tender_budget_enquiry', on_delete=models.RESTRICT, null=True) 
    order_placing_authority = models.ForeignKey(Account, related_name='tender_budget_enquiry_op', on_delete=models.RESTRICT, null=True) 
    tender_stage = models.ForeignKey(Stage, related_name='tender_budget_enquiry', on_delete=models.RESTRICT, null=True) 

    objects = BudgetEnquiryManager()
    
    class Meta:
        managed = False
        db_table = "TenderManagement_tender"


class SecurityDeposit(CoreModel):
    TYPE_CHOICES = [
        ('BG', 'Bank Guarantee'),
        ('SD', 'Security Deposit'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Received', 'Received'),
        ('Refunded', 'Refunded'),
    ]
    
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='security_deposits', null=True, blank=True)
    project = models.ForeignKey('ProjectManagement.Project', on_delete=models.CASCADE, related_name='security_deposits', null=True, blank=True)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'account_type': Account.CUSTOMER}, related_name='security_deposits', null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    received_on = models.DateField(null=True, blank=True)
    due_expiry_date = models.DateField()
    refunded_on = models.DateField(null=True, blank=True)
    extended_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, null=True)
    
    CODE_PREFIX = 'SD'
    
    class Meta:
        verbose_name = 'Security Deposit'
        verbose_name_plural = 'Security Deposits'
    
    def __str__(self):
        return f"{self.customer.name if self.customer else 'N/A'} - {self.type} - {self.amount}"


class LetterOfAward(CoreModel):
    PENDING = 1
    ISSUED = 2
    ACCEPTED = 3
    REJECTED = 4
    EXPIRED = 5

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ISSUED, 'Issued'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
    )

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='letters_of_award', null=True, blank=True)
    project = models.ForeignKey('ProjectManagement.Project', on_delete=models.CASCADE, related_name='letters_of_award', null=True, blank=True)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='letters_of_award', null=True, blank=True)
    
    # Award Details
    loa_number = models.CharField(max_length=100, null=True, blank=True, help_text="LOA Number")
    award_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    contract_duration = models.IntegerField(null=True, blank=True, help_text="Duration in days")
    commencement_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Timeline
    issue_date = models.DateField(null=True, blank=True)
    acceptance_date = models.DateField(null=True, blank=True)
    
    # Terms & Conditions
    scope_of_work = models.TextField(blank=True, null=True)
    payment_terms = models.TextField(blank=True, null=True)
    performance_security_required = models.BooleanField(default=False)
    performance_security_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    performance_security_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bank_guarantee_required = models.BooleanField(default=False)
    bank_guarantee_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status and Tracking
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    remarks = models.TextField(blank=True, null=True)
    conditions_precedent = models.TextField(blank=True, null=True)
    
    # Document Management
    loa_document = models.FileField(upload_to="letters_of_award/", null=True, blank=True)
    acceptance_document = models.FileField(upload_to="letters_of_award/acceptance/", null=True, blank=True)
    
    CODE_PREFIX = 'LOA'
    
    class Meta:
        verbose_name = "Letter of Award"
        verbose_name_plural = "Letters of Award"
        permissions = (
            ("can_issue_loa", "Can Issue Letter of Award"),
            ("can_approve_loa", "Can Approve Letter of Award"),
            ("can_view_loa", "Can View Letter of Award"),
        )

    def __str__(self):
        return f"LOA-{self.code} - {self.customer.name if self.customer else 'N/A'}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate completion date if commencement_date and contract_duration are set
        if self.commencement_date and self.contract_duration:
            from datetime import timedelta
            self.completion_date = self.commencement_date + timedelta(days=self.contract_duration)
        
        # Auto-calculate performance security amount if percentage is provided
        if self.award_amount and self.performance_security_percentage:
            self.performance_security_amount = (self.award_amount * self.performance_security_percentage) / 100
        
        super().save(*args, **kwargs)


class Order(CoreModel):
    PENDING = 1
    ISSUED = 2
    ACCEPTED = 3
    REJECTED = 4
    EXPIRED = 5

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ISSUED, 'Issued'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
    )

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    project = models.ForeignKey('ProjectManagement.Project', on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    
    # Order Details
    order_number = models.CharField(max_length=100, null=True, blank=True, help_text="Order Number")
    order_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    contract_duration = models.IntegerField(null=True, blank=True, help_text="Duration in days")
    commencement_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Timeline
    issue_date = models.DateField(null=True, blank=True)
    acceptance_date = models.DateField(null=True, blank=True)
    
    # Terms & Conditions
    scope_of_work = models.TextField(blank=True, null=True)
    payment_terms = models.TextField(blank=True, null=True)
    performance_security_required = models.BooleanField(default=False)
    performance_security_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    performance_security_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bank_guarantee_required = models.BooleanField(default=False)
    bank_guarantee_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status and Tracking
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    remarks = models.TextField(blank=True, null=True)
    conditions_precedent = models.TextField(blank=True, null=True)
    
    # Document Management
    order_document = models.FileField(upload_to="orders/", null=True, blank=True)
    acceptance_document = models.FileField(upload_to="orders/acceptance/", null=True, blank=True)
    
    CODE_PREFIX = 'ORD'
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        permissions = (
            ("can_issue_order", "Can Issue Order"),
            ("can_approve_order", "Can Approve Order"),
            ("can_view_order", "Can View Order"),
        )

    def __str__(self):
        return f"ORD-{self.code} - {self.customer.name if self.customer else 'N/A'}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate completion date if commencement_date and contract_duration are set
        if self.commencement_date and self.contract_duration:
            from datetime import timedelta
            self.completion_date = self.commencement_date + timedelta(days=self.contract_duration)
        
        # Auto-calculate performance security amount if percentage is provided
        if self.order_amount and self.performance_security_percentage:
            self.performance_security_amount = (self.order_amount * self.performance_security_percentage) / 100
        
        super().save(*args, **kwargs)