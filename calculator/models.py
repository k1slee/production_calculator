from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
class Material(models.Model):
    """Справочник материалов"""
    name = models.CharField('Название материала', max_length=100)
    density = models.DecimalField('Плотность (г/см³)', max_digits=5, decimal_places=2)
    
    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
    
    def __str__(self):
        return self.name

class PartName(models.Model):
    """Справочник наименований деталей"""
    name = models.CharField('Наименование детали', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Наименование детали'
        verbose_name_plural = 'Наименования деталей'
    
    def __str__(self):
        return self.name

class StockItem(models.Model):
    """Справочник сортамента на складе"""
    SECTION_TYPE_CHOICES = [
        ('sheet', 'Лист'),
        ('round', 'Кругляк'),
        ('hexagon', 'Шестигранник'),
    ]
    
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Материал')
    section_type = models.CharField('Тип сортамента', max_length=20, choices=SECTION_TYPE_CHOICES)
    
    # Параметры для листа - только ширина
    width = models.DecimalField('Ширина (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Параметры для кругляка - только диаметр
    diameter = models.DecimalField('Диаметр (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Параметры для шестигранника - только размер под ключ
    key_size = models.DecimalField('Размер под ключ (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Сортамент на складе'
        verbose_name_plural = 'Сортамент на складе'
    
    def __str__(self):
        if self.section_type == 'sheet':
            return f"{self.material} - Лист {self.width} мм"
        elif self.section_type == 'round':
            return f"{self.material} - Кругляк Ø{self.diameter} мм"
        else:  # hexagon
            return f"{self.material} - Шестигранник S{self.key_size} мм"

class Order(models.Model):
    """Модель заказа"""
    order_number = models.CharField('Номер заказа', max_length=50)
    order_name = models.CharField('Наименование заказа', max_length=200)
    drawing_number = models.CharField('Номер чертежа', max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    coefficient = models.DecimalField(
        'Коэффициент массы', 
        max_digits=2, 
        decimal_places=1, 
        default=1.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(2.0)]
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f"Заказ №{self.order_number} - {self.order_name}"
    
    @property
    def total_weight_g(self):
        """Общий вес заказа в граммах"""
        return sum(item.total_weight_g for item in self.items.all())
    
    @property
    def total_weight(self):
        """Общий вес заказа в килограммах"""
        return self.total_weight_g / 1000
    
    @property
    def total_items_count(self):
        """Общее количество деталей в заказе"""
        return sum(item.quantity for item in self.items.all())
    @property
    def materials_count(self):
        """Количество уникальных материалов в заказе"""
        return self.items.values('material').distinct().count()
    
    @property
    def total_items_count(self):
        """Общее количество деталей в заказе"""
        return sum(item.quantity for item in self.items.all())
class Profile(models.Model):
    """Профиль пользователя с отчеством"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    patronymic = models.CharField('Отчество', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.patronymic}".strip()
    
    @property
    def full_name(self):
        """Полное имя с отчеством"""
        return f"{self.user.last_name} {self.user.first_name} {self.patronymic}".strip()
    
    @property
    def initials(self):
        """Инициалы"""
        last_name = self.user.last_name
        first_name = self.user.first_name[0] if self.user.first_name else ''
        patronymic = self.patronymic[0] if self.patronymic else ''
        return f"{last_name} {first_name}.{patronymic}." if patronymic else f"{last_name} {first_name}."

# Сигнал для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль только при создании пользователя и только если его нет"""
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль если он существует"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Если профиля нет, создаем его
        Profile.objects.get_or_create(user=instance)

class OrderItem(models.Model):
    """Детали заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    sequence_number = models.CharField('Порядковый номер', max_length=20)
    part_name = models.ForeignKey(PartName, on_delete=models.PROTECT, verbose_name='Наименование детали')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name='Марка материала', null=True, blank=True)
    quantity = models.IntegerField('Количество деталей', validators=[MinValueValidator(1)])
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, verbose_name='Сортамент со склада', null=True, blank=True)
    
    # Замеры детали
    length = models.DecimalField('Длина (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    width = models.DecimalField('Ширина (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    height = models.DecimalField('Высота (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    diameter = models.DecimalField('Диаметр (мм)', max_digits=8, decimal_places=2, null=True, blank=True)  # Исправлено
    key_size = models.DecimalField('Размер под ключ (мм)', max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Особая запись
    is_special = models.BooleanField('Особая запись', default=False)
    
    class Meta:
        verbose_name = 'Деталь заказа'
        verbose_name_plural = 'Детали заказа'
        ordering = ['sequence_number']
    
    def __str__(self):
        return f"{self.sequence_number}. {self.part_name} - {self.quantity} шт."
    
    @property
    def volume(self):
        """Расчёт объёма детали в мм³"""
        if self.is_special or not self.stock_item:
            return 0
        section_type = self.stock_item.section_type
        
        if section_type == 'sheet':
            return float(self.length or 0) * float(self.width or 0) * float(self.height or 0)
        elif section_type == 'round':
            d = float(self.diameter or 0)
            return 3.14159 * (d/2)**2 * float(self.length or 0)
        else:  # hexagon
            a = float(self.key_size or 0)
            return (3 * 1.73205 / 2) * a**2 * float(self.length or 0)
    
    @property
    def volume_cm3(self):
        """Объём детали в см³"""
        return self.volume / 1000
    
    @property
    def weight_g(self):
        """Вес одной детали в граммах"""
        if self.is_special or not self.material:
            return 0
        return self.volume_cm3 * float(self.material.density)
    
    @property
    def weight(self):
        """Вес одной детали в килограммах"""
        return self.weight_g / 1000
    
    @property
    def total_weight_g(self):
        """Общий вес с учётом количества и коэффициента в граммах"""
        if self.is_special:
            return 0
        return self.weight_g * self.quantity * float(self.order.coefficient)
    
    @property
    def total_weight(self):
        """Общий вес с учётом количества и коэффициента в килограммах"""
        return self.total_weight_g / 1000