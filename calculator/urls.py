from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Справочник материалов
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    
    # Справочник наименований деталей
    path('parts/', views.part_list, name='part_list'),
    path('parts/create/', views.part_create, name='part_create'),
    path('parts/<int:pk>/edit/', views.part_edit, name='part_edit'),
    path('parts/<int:pk>/delete/', views.part_delete, name='part_delete'),
    
    # Справочник сортамента на складе
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/create/', views.stock_create, name='stock_create'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    
    # Заказы
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/add-item/', views.add_order_item, name='add_order_item'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('orders/<int:order_id>/item/<int:item_id>/delete/', views.delete_order_item, name='delete_order_item'),
    path('orders/<int:order_id>/update-coefficient/', views.update_order_coefficient, name='update_order_coefficient'),
    
    # Печатные формы - детальный отчет
    path('orders/<int:order_id>/print/', views.print_order_report, name='print_order_report'),
    
    # Печатные формы - группированный отчет
    path('orders/<int:order_id>/print-grouped/', views.print_grouped_report, name='print_grouped_report'),
    #Печатные форма - задание на заготовку
    path('orders/<int:order_id>/print-cutting/', views.print_cutting_task, name='print_cutting_task'),

    path('orders/<int:order_id>/copy/', views.copy_order, name='copy_order'),
    path('orders/<int:order_id>/item/<int:item_id>/edit/', views.edit_order_item, name='edit_order_item'),
    path('api/stock-items-by-material/', views.get_stock_items_by_material_and_type, name='api_stock_items_by_material'),
    # API
    path('api/stock-items/', views.get_stock_items_by_material, name='api_stock_items'),
    path('api/stock-items-by-material/', views.get_stock_items_by_material_and_type, name='api_stock_items_by_material'),
    path('api/search-part-names/', views.search_part_names, name='search_part_names'),
    path('api/search-materials/', views.search_materials, name='search_materials'),
]