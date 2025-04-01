from django.urls import path
from .views import ItemListCreateView, ItemDetailView, PurchaseDetailAPIView, PurchaseHeaderDetailView, SellDetailViewSet, SellView, StockReportView

urlpatterns = [
    path('items/', ItemListCreateView.as_view(), name='items-list'),
    path('items/<str:code>/', ItemDetailView.as_view(), name='item-detail'),
    path('purchase/<str:code>/', PurchaseHeaderDetailView.as_view(), name='purchase-header-detail'),
    path('purchase/<str:header_code>/details/', PurchaseDetailAPIView.as_view(), name='purchase_details'),
    path('sell/', SellView.as_view(), name='sell_list_create'),
    path('sell/<str:code>/', SellView.as_view(), name='sell_detail_update_delete'),
    path('sell/<str:header_code>/details/', SellDetailViewSet.as_view({'get': 'list', 'post': 'create'}), name='sell_detail_list_create'),
    path('report/<str:item_code>/', StockReportView.as_view(), name='stock_report'),
]
