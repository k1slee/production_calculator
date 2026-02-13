from django import forms
from .models import Material, PartName, StockItem, Order, OrderItem
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Фамилия и инициалы', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'density']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'density': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PartNameForm(forms.ModelForm):
    class Meta:
        model = PartName
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['material', 'section_type', 'width', 'diameter', 'key_size']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-select'}),
            'section_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_section_type'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ширина листа'}),
            'diameter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Диаметр круга'}),
            'key_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Размер под ключ'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        section_type = cleaned_data.get('section_type')
        
        if section_type == 'sheet':
            if not cleaned_data.get('width'):
                self.add_error('width', 'Обязательное поле для листа')
            cleaned_data['diameter'] = None
            cleaned_data['key_size'] = None
        elif section_type == 'round':
            if not cleaned_data.get('diameter'):
                self.add_error('diameter', 'Обязательное поле для кругляка')
            cleaned_data['width'] = None
            cleaned_data['key_size'] = None
        elif section_type == 'hexagon':
            if not cleaned_data.get('key_size'):
                self.add_error('key_size', 'Обязательное поле для шестигранника')
            cleaned_data['width'] = None
            cleaned_data['diameter'] = None
        
        return cleaned_data

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_number', 'order_name', 'drawing_number', 'coefficient']
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'order_name': forms.TextInput(attrs={'class': 'form-control'}),
            'drawing_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: ДМ-123-2024'}),
            'coefficient': forms.Select(attrs={'class': 'form-select'}, 
                                       choices=[(x/10, x/10) for x in range(10, 21)]),
        }

class OrderCoefficientForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['coefficient']
        widgets = {
            'coefficient': forms.Select(
                attrs={'class': 'form-select'},
                choices=[(1.0, '1.0'), (1.1, '1.1'), (1.2, '1.2'), (1.3, '1.3'), 
                        (1.4, '1.4'), (1.5, '1.5'), (1.6, '1.6'), (1.7, '1.7'), 
                        (1.8, '1.8'), (1.9, '1.9'), (2.0, '2.0')]
            ),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['sequence_number', 'part_name', 'material', 'quantity', 
                 'stock_item', 'length', 'width', 'height', 'diameter', 'key_size']
        widgets = {
            'sequence_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'part_name': forms.Select(attrs={'class': 'form-select'}),
            'material': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'stock_item': forms.Select(attrs={'class': 'form-select'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'diameter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'key_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем все сортаменты без фильтрации
        self.fields['stock_item'].queryset = StockItem.objects.all()
        self.fields['stock_item'].label = 'Сортамент со склада'
        self.fields['stock_item'].empty_label = '---------'
        
        # Делаем поля необязательными
        self.fields['length'].required = False
        self.fields['width'].required = False
        self.fields['height'].required = False
        self.fields['diameter'].required = False
        self.fields['key_size'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        stock_item = cleaned_data.get('stock_item')
        
        if stock_item:
            section_type = stock_item.section_type
            
            if section_type == 'sheet':
                if not cleaned_data.get('length'):
                    self.add_error('length', 'Обязательное поле для листа')
                if not cleaned_data.get('width'):
                    self.add_error('width', 'Обязательное поле для листа')
                if not cleaned_data.get('height'):
                    self.add_error('height', 'Обязательное поле для листа')
                # Очищаем ненужные поля
                cleaned_data['diameter'] = None
                cleaned_data['key_size'] = None
                    
            elif section_type == 'round':
                if not cleaned_data.get('diameter'):
                    self.add_error('diameter', 'Обязательное поле для кругляка')
                if not cleaned_data.get('length'):
                    self.add_error('length', 'Обязательное поле для кругляка')
                # Очищаем ненужные поля
                cleaned_data['width'] = None
                cleaned_data['height'] = None
                cleaned_data['key_size'] = None
                    
            elif section_type == 'hexagon':
                if not cleaned_data.get('key_size'):
                    self.add_error('key_size', 'Обязательное поле для шестигранника')
                if not cleaned_data.get('length'):
                    self.add_error('length', 'Обязательное поле для шестигранника')
                # Очищаем ненужные поля
                cleaned_data['width'] = None
                cleaned_data['height'] = None
                cleaned_data['diameter'] = None
        
        return cleaned_data