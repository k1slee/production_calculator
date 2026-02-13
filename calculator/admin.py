from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import Material, PartName, StockItem, Order, OrderItem, Profile

# Inline для профиля в админке пользователя
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Отчество'
    fields = ['patronymic']
    extra = 0
    max_num = 1

# Кастомная админка пользователя
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:
            # Для создания пользователя
            fieldsets[0][1]['fields'] = ('username', 'password1', 'password2', 
                                         'last_name', 'first_name', 'email')
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Профиль создается сигналом, но на всякий случай проверяем
        Profile.objects.get_or_create(user=obj)

# Переопределяем админку пользователя
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Регистрируем профиль отдельно (опционально)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'patronymic']
    search_fields = ['user__username', 'user__last_name', 'user__first_name', 'patronymic']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Остальные админ-классы без изменений...
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'density']
    search_fields = ['name']
    list_filter = ['density']

@admin.register(PartName)
class PartNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'material', 'section_type', 'get_size']
    list_filter = ['section_type', 'material']
    search_fields = ['material__name']
    
    def get_size(self, obj):
        if obj.section_type == 'sheet':
            return f"{obj.width} мм"
        elif obj.section_type == 'round':
            return f"Ø{obj.diameter} мм"
        elif obj.section_type == 'hexagon':
            return f"S{obj.key_size} мм"
        return "-"
    get_size.short_description = 'Размер'
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (None, {
                    'fields': ('material', 'section_type')
                }),
            )
        
        if obj.section_type == 'sheet':
            return (
                (None, {
                    'fields': ('material', 'section_type', 'width')
                }),
            )
        elif obj.section_type == 'round':
            return (
                (None, {
                    'fields': ('material', 'section_type', 'diameter')
                }),
            )
        elif obj.section_type == 'hexagon':
            return (
                (None, {
                    'fields': ('material', 'section_type', 'key_size')
                }),
            )
        return super().get_fieldsets(request, obj)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'order_name', 'drawing_number', 'user', 'created_at', 'coefficient']
    list_filter = ['created_at', 'user', 'coefficient']
    search_fields = ['order_number', 'order_name', 'drawing_number', 'user__username', 'user__last_name']
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'sequence_number', 'part_name', 'material', 'quantity', 'is_special']
    list_filter = ['order', 'material', 'part_name', 'is_special']
    search_fields = ['order__order_number', 'part_name__name']