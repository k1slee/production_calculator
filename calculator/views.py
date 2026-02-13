from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone 
from django.db.models import Count, Sum
from django.http import JsonResponse
from .models import Material, PartName, StockItem, Order, OrderItem
from .forms import (LoginForm, MaterialForm, PartNameForm, StockItemForm, 
                   OrderForm, OrderItemForm, OrderCoefficientForm)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.last_name} {user.first_name}!')
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'calculator/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')

@login_required
def index(request):
    context = {
        'material_count': Material.objects.count(),
        'part_count': PartName.objects.count(),
        'stock_count': StockItem.objects.count(),
        'order_count': Order.objects.filter(user=request.user).count(),
    }
    return render(request, 'calculator/index.html', context)

# Справочник материалов
@login_required
def material_list(request):
    materials = Material.objects.all().order_by('name')
    return render(request, 'calculator/material_list.html', {'materials': materials})

@login_required
def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Материал успешно добавлен')
            return redirect('material_list')
    else:
        form = MaterialForm()
    return render(request, 'calculator/material_form.html', {'form': form, 'title': 'Добавить материал'})

@login_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Материал успешно обновлен')
            return redirect('material_list')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'calculator/material_form.html', {'form': form, 'title': 'Редактировать материал'})

@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Материал успешно удален')
        return redirect('material_list')
    return render(request, 'calculator/material_confirm_delete.html', {'object': material})

# Справочник наименований деталей
@login_required
def part_list(request):
    parts = PartName.objects.all().order_by('name')
    return render(request, 'calculator/part_list.html', {'parts': parts})

@login_required
def part_create(request):
    if request.method == 'POST':
        form = PartNameForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Наименование детали успешно добавлено')
            return redirect('part_list')
    else:
        form = PartNameForm()
    return render(request, 'calculator/part_form.html', {'form': form, 'title': 'Добавить наименование детали'})

@login_required
def part_edit(request, pk):
    part = get_object_or_404(PartName, pk=pk)
    if request.method == 'POST':
        form = PartNameForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, 'Наименование детали успешно обновлено')
            return redirect('part_list')
    else:
        form = PartNameForm(instance=part)
    return render(request, 'calculator/part_form.html', {'form': form, 'title': 'Редактировать наименование детали'})

@login_required
def part_delete(request, pk):
    part = get_object_or_404(PartName, pk=pk)
    if request.method == 'POST':
        part.delete()
        messages.success(request, 'Наименование детали успешно удалено')
        return redirect('part_list')
    return render(request, 'calculator/part_confirm_delete.html', {'object': part})

# Справочник сортамента на складе
@login_required
def stock_list(request):
    stock_items = StockItem.objects.all().order_by('material__name', 'section_type')
    return render(request, 'calculator/stock_list.html', {'stock_items': stock_items})

@login_required
def stock_create(request):
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сортамент успешно добавлен на склад')
            return redirect('stock_list')
    else:
        form = StockItemForm()
    return render(request, 'calculator/stock_form.html', {'form': form, 'title': 'Добавить сортамент на склад'})

@login_required
def stock_edit(request, pk):
    stock_item = get_object_or_404(StockItem, pk=pk)
    if request.method == 'POST':
        form = StockItemForm(request.POST, instance=stock_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сортамент успешно обновлен')
            return redirect('stock_list')
    else:
        form = StockItemForm(instance=stock_item)
    return render(request, 'calculator/stock_form.html', {'form': form, 'title': 'Редактировать сортамент'})

@login_required
def stock_delete(request, pk):
    stock_item = get_object_or_404(StockItem, pk=pk)
    if request.method == 'POST':
        stock_item.delete()
        messages.success(request, 'Сортамент успешно удален со склада')
        return redirect('stock_list')
    return render(request, 'calculator/stock_confirm_delete.html', {'object': stock_item})

# Заказы
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'calculator/order_list.html', {'orders': orders})

@login_required
@transaction.atomic
def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, f'Заказ №{order.order_number} успешно создан')
            return redirect('order_detail', order_id=order.id)
    else:
        order_form = OrderForm()
    return render(request, 'calculator/order_form.html', {'form': order_form, 'title': 'Создать заказ'})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    total_weight = sum(item.total_weight for item in items)
    return render(request, 'calculator/order_detail.html', {
        'order': order, 
        'items': items,
        'total_weight': total_weight
    })

@login_required
@transaction.atomic
def add_order_item(request, order_id):
    """Добавление детали в заказ"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Копируем POST данные для модификации
        post_data = request.POST.copy()
        
        # Определяем тип сортамента и очищаем ненужные поля
        stock_item_id = post_data.get('stock_item')
        if stock_item_id:
            try:
                stock_item = StockItem.objects.get(id=stock_item_id)
                
                # Оставляем только нужные поля в зависимости от типа сортамента
                if stock_item.section_type == 'sheet':
                    # Удаляем поля для кругляка и шестигранника
                    post_data.pop('diameter', None)
                    post_data.pop('key_size', None)
                    # Убеждаемся что поля для листа заполнены
                    if not post_data.get('width'):
                        post_data['width'] = '0'
                    if not post_data.get('height'):
                        post_data['height'] = '0'
                        
                elif stock_item.section_type == 'round':
                    # Удаляем поля для листа и шестигранника
                    post_data.pop('width', None)
                    post_data.pop('height', None)
                    post_data.pop('key_size', None)
                    # Переносим длину в правильное поле
                    if post_data.get('length'):
                        post_data['diameter'] = post_data.get('diameter', '0')
                    else:
                        post_data['diameter'] = '0'
                        
                elif stock_item.section_type == 'hexagon':
                    # Удаляем поля для листа и кругляка
                    post_data.pop('width', None)
                    post_data.pop('height', None)
                    post_data.pop('diameter', None)
                    if not post_data.get('key_size'):
                        post_data['key_size'] = '0'
            except StockItem.DoesNotExist:
                pass
        
        form = OrderItemForm(post_data)
        
        if form.is_valid():
            try:
                item = form.save(commit=False)
                item.order = order
                
                # Убеждаемся что установлены правильные значения в зависимости от типа
                if item.stock_item.section_type == 'round':
                    item.length = item.diameter  # Для кругляка используем diameter как длину
                
                item.save()
                messages.success(request, 'Деталь успешно добавлена в заказ')
                return redirect('order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
        else:
            # Выводим ошибки валидации
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # Автоматически устанавливаем следующий порядковый номер
        next_number = order.items.count() + 1
        form = OrderItemForm(initial={'sequence_number': next_number})
    
    return render(request, 'calculator/order_item_form.html', {
        'form': form, 
        'order': order
    })

@login_required
def delete_order_item(request, order_id, item_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    item = get_object_or_404(OrderItem, id=item_id, order=order)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Деталь удалена из заказа')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'calculator/order_item_confirm_delete.html', {'item': item, 'order': order})

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ успешно удален')
        return redirect('order_list')
    
    return render(request, 'calculator/order_confirm_delete.html', {'order': order})

# API endpoints for AJAX
@login_required
def get_stock_items_by_material(request):
    material_id = request.GET.get('material_id')
    section_type = request.GET.get('section_type')
    
    stock_items = StockItem.objects.filter(quantity__gt=0)
    
    if material_id:
        stock_items = stock_items.filter(material_id=material_id)
    if section_type:
        stock_items = stock_items.filter(section_type=section_type)
    
    data = [{
        'id': item.id,
        'text': str(item),
        'section_type': item.section_type
    } for item in stock_items]
    
    return JsonResponse({'results': data})

@login_required
def print_order_report(request, order_id):
    """Печатная форма основного отчета по заказу"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Рассчитываем общий вес в кг
    total_weight_kg = order.total_weight / 1000
    
    # Формируем данные для отчета
    report_data = {
        'order': order,
        'items': items,
        'total_weight_kg': total_weight_kg,
        'date': timezone.now().strftime('%d.%m.%Y'),
        'user': request.user
    }
    
    return render(request, 'calculator/print_order_report.html', report_data)

@login_required
def generate_order_pdf(request, order_id):
    """Генерация PDF отчета по заказу"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    total_weight_kg = order.total_weight / 1000
    
    context = {
        'order': order,
        'items': items,
        'total_weight_kg': total_weight_kg,
        'date': timezone.now().strftime('%d.%m.%Y'),
        'user': request.user
    }
    
    # Загружаем шаблон
    template = get_template('calculator/pdf_order_report.html')
    html = template.render(context)
    
    # Создаем PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.order_number}_{datetime.datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
    
    return HttpResponse('Ошибка при генерации PDF', status=400)

@login_required
@transaction.atomic
def update_order_coefficient(request, order_id):
    """Обновление коэффициента массы в заказе"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        form = OrderCoefficientForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Коэффициент массы успешно изменен на {order.coefficient}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'coefficient': str(order.coefficient),
                    'total_weight': f'{order.total_weight:.3f}'
                })
        else:
            messages.error(request, '❌ Ошибка при изменении коэффициента')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    return redirect('order_detail', order_id=order.id)


@login_required
def print_grouped_report(request, order_id):
    """Печатная форма группированного отчета по материалам и сортаменту"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Группируем детали по материалу и сортаменту
    grouped_data = {}
    for item in items:
        key = (item.material.id, item.stock_item.id)
        if key not in grouped_data:
            grouped_data[key] = {
                'material': item.material,
                'stock_item': item.stock_item,
                'total_weight': 0,
                'quantity': 0,
                'weight_per_item': item.weight,  # Вес одной детали
                'items': []
            }
        grouped_data[key]['total_weight'] += item.total_weight
        grouped_data[key]['quantity'] += item.quantity
        grouped_data[key]['items'].append(item)
    
    # Сортируем по материалу
    grouped_list = sorted(grouped_data.values(), key=lambda x: x['material'].name)
    
    # Общий вес заказа
    total_weight_kg = order.total_weight
    
    context = {
        'order': order,
        'grouped_items': grouped_list,
        'total_weight_kg': total_weight_kg,
        'date': timezone.now().strftime('%d.%m.%Y'),
        'user': request.user
    }
    
    return render(request, 'calculator/print_grouped_report.html', context)


@login_required
def print_cutting_task(request, order_id):
    """Печатная форма - Задание на заготовку"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Группируем детали по типу сортамента
    grouped_by_section = {
        'sheet': [],  # Лист
        'round': [],  # Кругляк
        'hexagon': [] # Шестигранник
    }
    
    for item in items:
        section_type = item.stock_item.section_type
        if section_type in grouped_by_section:
            grouped_by_section[section_type].append(item)
    
    # Сортируем внутри каждой группы по порядковому номеру
    for section_type in grouped_by_section:
        grouped_by_section[section_type] = sorted(
            grouped_by_section[section_type], 
            key=lambda x: x.sequence_number
        )
    
    context = {
        'order': order,
        'sheet_items': grouped_by_section['sheet'],
        'round_items': grouped_by_section['round'],
        'hexagon_items': grouped_by_section['hexagon'],
        'date': timezone.now().strftime('%d.%m.%Y'),
        'user': request.user
    }
    
    return render(request, 'calculator/print_cutting_task.html', context)
