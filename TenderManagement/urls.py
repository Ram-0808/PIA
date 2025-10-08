from django.urls import include, path
from . import views

urlpatterns = [

    path('tenderitemmaster/', views.TenderItemMasterList.as_view()),
    path('tenderitemmaster/mini/', views.TenderItemMasterMiniList.as_view()),
    path('tenderitemmaster/create/', views.TenderItemMasterCreate.as_view()),
    path('tenderitemmaster/<str:pk>/', views.TenderItemMasterDetail.as_view()),


    path('tenders/', views.TenderList.as_view()),
    path('tenders/create/', views.TenderCreate.as_view()),
    path('tenders/<str:pk>/', views.TenderDetail.as_view()),
    # path('tenderassign/<str:pk>/', views.TenderAssign.as_view()),
    path('tenderstage/<str:pk>/', views.TenderStageView.as_view()),
    path('mini/tender/', views.TenderMini.as_view()),
    path('minirtender/tender/', views.TenderStatusMini.as_view()),

    # path('tenderapprove/<str:pk>/', views.TenderApproval.as_view()),

    path('comments/', views.TenderCommentsList.as_view()),
    path('comments/create/', views.TenderCommentsCreate.as_view()),
    path('comments/<str:pk>/', views.TenderCommentsDetail.as_view()),


    path('tenderitemassignes/create/', views.TenderItemAssignCreate.as_view()),
    path('tenderitemassignes/', views.TenderItemAssignList.as_view()),
    path('tenderitemassignes/<str:pk>/', views.TenderItemAssignDetail.as_view()),


    path('tenderattachments/', views.TenderAttachmentsList.as_view()),
    path('tenderattachments/create/', views.TenderAttachmentsCreate.as_view()),
    path('tenderattachments/<str:pk>/', views.TenderAttachmentsDetail.as_view()),


    path('casesheets/list/<str:tender_id>/', views.CaseSheetList.as_view()),
    path('casesheets/create/', views.CaseSheetCreate.as_view()),
    path('casesheets/<str:pk>/', views.CaseSheetDetail.as_view()),
    path('casesheetsupdate/<str:pk>/', views.CaseSheetUpdate.as_view()),


    path('reverseauction/list/<str:tender_id>/', views.ReverseAuctionList.as_view()),
    path('reverseauction/create/', views.ReverseAuctionCreate.as_view()),
    path('reverseauction/<str:pk>/', views.ReverseAuctionDetail.as_view()),
    path('l1priceupdate/<str:pk>/', views.L1PriceUpdate.as_view()),


    path('tenderdocuments/list/<str:tender_id>/', views.TenderDocumentsList.as_view()),

    path('tenderdocuments/create/', views.TenderDocumentsCreate.as_view()),
    path('tenderdocuments/<str:pk>/', views.TenderDocumentsDetail.as_view()),


    # path('bidamounts/', views.BidAmountList.as_view()),
    path('bidamounts/list/<str:tender_id>/', views.BidAmountList.as_view()),

    path('bidamounts/create/', views.BidAmountCreate.as_view()),
    path('bidamounts/<str:pk>/', views.BidAmountDetail.as_view()),
    path('bidamounts/l1priceupdate/<str:pk>/', views.BidAmountL1PriceUpdate.as_view()),


    path('file-workflow/', views.FileWorkflowAPIView.as_view(), name='file-workflow'),
    path('file-workflow/status/<str:pk>/', views.CheckFileWorkflowView.as_view()),

    path('costingsheet/mini/', views.CostingSheetMini.as_view()),
    path('costingsheet/list/<str:tender_id>/', views.CostingSheetList.as_view()),
    path('costingsheet/create/', views.CostingSheetList.as_view()),
    path('costingsheet/<str:pk>/', views.CostingSheetDetail.as_view()),

    path('service/', views.ServiceList.as_view()),
    path("service/<str:pk>", views.ServiceDetail.as_view()),
    path('service/mini/', views.ServiceMini.as_view()),

    path('consumable/', views.ConsumableList.as_view()),
    path('consumable/mini/', views.ConsumableMini.as_view()),
    path("consumable/<str:pk>", views.ConsumableDetail.as_view()),

    path('othercharges/', views.OtherChargesList.as_view()),
    path('othercharges/mini/', views.OtherChargesMini.as_view()),
    path("othercharges/<str:pk>", views.OtherChargesDetail.as_view()),

    path('rawmaterial/', views.RawMaterialList.as_view()),
    path('rawmaterial/mini/', views.RawMaterialMini.as_view()),
    path("rawmaterial/<str:pk>", views.RawMaterialDetail.as_view()),

    path('cst_overview/<str:tender_id>/<str:is_margin_value>/', views.TenderDataView.as_view(), name='tender-data'),

    path('plazotender/list/', views.PlazoTenderList.as_view()),
    path('plazotender/create/', views.PlazoTenderCreate.as_view()),
    path("plazotender/<str:pk>", views.PlazoTenderDetail.as_view()),
    path('plazotender/mini/', views.PlazoTenderMiniList.as_view()),

    path('plazotenderattachments/', views.PlazoTenderAttachmentList.as_view()),
    path('plazotenderattachments/create/', views.PlazoTenderAttachmentCreate.as_view()),
    path('plazotenderattachments/<str:pk>/', views.PlazoTenderAttachmentDetail.as_view()),

    # TenderCheckListItems URLs
    path('tenderchecklistitems/', views.TenderCheckListItemsList.as_view()),
    path('tenderchecklistitems/list/<str:tender_id>/', views.TenderCheckListItemsList.as_view()),
    path('tenderchecklistitems/create/', views.TenderCheckListItemsCreate.as_view()),
    path('tenderchecklistitems/<str:pk>/', views.TenderCheckListItemsDetail.as_view()),

    # BudgetEnquiry URLs for BOQ Integration
    path('budgetenquiries/', views.BudgetEnquiryList.as_view(), name='budget-enquiry-list'),
    path('budgetenquiries/create/', views.BudgetEnquiryCreate.as_view(), name='budget-enquiry-create'),
    path('budgetenquiries/mini/', views.BudgetEnquiryMini.as_view(), name='budget-enquiry-mini'),
    path('budgetenquiries/<str:pk>/', views.BudgetEnquiryDetail.as_view(), name='budget-enquiry-detail'),
    path('budgetenquiries/<str:budget_enquiry_id>/items/', views.BudgetEnquiryItems.as_view(), name='budget-enquiry-items'),
    path('budgetenquiries/<str:budget_enquiry_id>/rfq-items/', views.BudgetEnquiryRFQItems.as_view(), name='budget-enquiry-rfq-items'),

    path('security-deposit/', views.SecurityDepositListCreateView.as_view(), name='security-deposit-list-create'),
    path('security-deposit/<str:pk>/', views.SecurityDepositDetailView.as_view(), name='security-deposit-detail'),
    path('security-deposit/project/<str:project_id>/', views.SecurityDepositByProjectView.as_view(), name='security-deposit-by-project'),

    # Letter of Award URLs
    path('letter-of-award/', views.LetterOfAwardListCreateView.as_view(), name='letter-of-award-list-create'),
    path('letter-of-award/<str:pk>/', views.LetterOfAwardDetailView.as_view(), name='letter-of-award-detail'),
    path('letter-of-award/<str:pk>/upload-document/', views.LetterOfAwardDocumentUploadView.as_view(), name='letter-of-award-document-upload'),
    path('letter-of-award/mini/', views.LetterOfAwardMiniView.as_view(), name='letter-of-award-mini'),
    path('letter-of-award/tender/<str:tender_id>/', views.LetterOfAwardByTenderView.as_view(), name='letter-of-award-by-tender'),

    # Order URLs
    path('order/', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('order/<str:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order/mini/', views.OrderMiniView.as_view(), name='order-mini'),
    path('order/tender/<str:tender_id>/', views.OrderByTenderView.as_view(), name='order-by-tender'),
] 
    