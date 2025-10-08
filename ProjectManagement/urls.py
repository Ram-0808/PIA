from django.urls import include, path
from . import views

urlpatterns = [

    path('projects/', views.ProjectList.as_view()),
    path('projects/mini/', views.ProjectMiniList.as_view()),
    path('projects/create/', views.ProjectCreate.as_view()),
    path('projects/<str:pk>/', views.ProjectDetail.as_view()),
    # path('projects/update/<str:pk>/', views.ProjectUpdateView.as_view()),

    path('assignprojects/mini/', views.AssigneeProjectMiniList.as_view()),

    path('projectduedatedocument/create/', views.ProjectDueDateDocumentCreate.as_view(), name='ProjectDocumentsCreate'),
    path('projectduedatedocument/list/', views.ProjectDueDateDocumentList.as_view(), name='ProjectDocumentsList'),

    path('projectdocuments/', views.ProjectDocumentsCreate.as_view(), name='ProjectDocumentsCreate'),
    path('projectdocumentsList/', views.ProjectDocumentsList.as_view(), name='ProjectDocumentsList'),

    path('projectgroup/create/', views.ProjectGroupCreate.as_view(),),
    path('projectgroup/list/', views.ProjectGroupList.as_view(),),
    path('projectgroup/mini/', views.ProjectGroupMiniList.as_view(),),
    path('projectgroup/<str:pk>/', views.ProjectGroupDetail.as_view(),),
    
    path('projectgroupuser/create/', views.ProjectGroupUserCreate.as_view(),),
    path('projectgroupuser/list/', views.ProjectGroupUserList.as_view(),),
    path('projectgroupuser/mini/', views.ProjectGroupUserMiniList.as_view(),),
    path('projectgroupuser/<str:pk>/', views.ProjectGroupUserDetail.as_view(),),
    
    path('performancebankguarantees/', views.PerformanceBankGuaranteeList.as_view(), name='performance_bank_guarantee_list'),
    path('performancebankguarantees/<str:pk>/', views.PerformanceBankGuaranteeDetail.as_view(), name='performance_bank_guarantee_detail'),
    path('performancebankguarantees/mini/', views.PerformanceBankGuaranteeMiniList.as_view(), name='performance_bank_guarantee_mini_list'),

    path('pbgextendedduedate/<str:pk>/', views.PBGExtendedDuedateUpdate.as_view(), name='pbgextendedduedate'),

    path('performancebankguaranteehistories/', views.PerformanceBankGuaranteeHistoryList.as_view(), name='performance_bank_guaranteehistory_list'),

    path('stock/<str:project_id>/<str:warehouse_id>/<str:item_id>/<str:batch_id>/', views.StockView.as_view(), name='stock'), #overall stock against batch agaist warehouse
    path('stockwithoutbatch/<str:project_id>/<str:warehouse_id>/<str:item_id>/', views.StockWithoutBatchView.as_view(), name='stockwithoutbatch'), #overall stock without batch
    path('stockagainstbatch/<str:project_id>/<str:warehouse_id>/<str:item_id>/', views.StockAgainstBatchView.as_view(), name='stockagainstbatch'), #overall stock against batch without warehouse
    path('stockitemview/<str:project_id>/<str:warehouse_id>/', views.StockItemView.as_view(), name='stockitemview'),


    path('stockledger/report', views.StockLedgerView.as_view(), name='stock-ledgeer'),
    
    path('project-items/<str:project_id>/', views.ProjectItemsByProjectView.as_view(), name='project-items-by-project'),
    
   
]
