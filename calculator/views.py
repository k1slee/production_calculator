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
from django.db import models

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
    """Список материалов"""
    materials = Material.objects.all().order_by('name')
    return render(request, 'calculator/material_list.html', {'materials': materials})

@login_required
def material_create(request):
    """Создание материала"""
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
    """Редактирование материала"""
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
    """Удаление материала"""
    material = get_object_or_404(Material, pk=pk)
    
    # Проверяем, используется ли материал в заказах или на складе
    if StockItem.objects.filter(material=material).exists():
        messages.error(request, 'Невозможно удалить материал, так как он используется в сортаменте на складе')
        return redirect('material_list')
    
    if OrderItem.objects.filter(material=material).exists():
        messages.error(request, 'Невозможно удалить материал, так как он используется в заказах')
        return redirect('material_list')
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Материал успешно удален')
        return redirect('material_list')
    
    return render(request, 'calculator/material_confirm_delete.html', {'object': material})

# Справочник наименований деталей
@login_required
def part_list(request):
    """Список наименований деталей"""
    parts = PartName.objects.all().order_by('name')
    return render(request, 'calculator/part_list.html', {'parts': parts})

@login_required
def part_create(request):
    """Создание наименования детали"""
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
    """Редактирование наименования детали"""
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
    """Удаление наименования детали"""
    part = get_object_or_404(PartName, pk=pk)
    
    # Проверяем, используется ли наименование детали в заказах
    if OrderItem.objects.filter(part_name=part).exists():
        messages.error(request, 'Невозможно удалить наименование детали, так как оно используется в заказах')
        return redirect('part_list')
    
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

@login_required
def order_list(request):
    """Список всех заказов для всех пользователей"""
    # Все пользователи видят все заказы
    orders = Order.objects.all()
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            models.Q(order_number__icontains=search_query) |
            models.Q(order_name__icontains=search_query) |
            models.Q(drawing_number__icontains=search_query)
        )
    
    # Сортировка по дате создания (сначала новые)
    orders = orders.order_by('-created_at')
    
    # Подсчет статистики
    total_orders = orders.count()
    total_weight = sum(order.total_weight for order in orders)
    total_items = sum(order.total_items_count for order in orders)
    
    context = {
        'orders': orders,
        'search_query': search_query,
        'total_orders': total_orders,
        'total_weight': total_weight,
        'total_items': total_items,
    }
    return render(request, 'calculator/order_list.html', context)

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
    """Детали заказа с поиском по наименованию детали"""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Поиск по наименованию детали
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(part_name__name__icontains=search_query)
    
    # Преобразуем в список для кастомной сортировки
    items_list = list(items)
    
    # Сортировка с учетом числовых значений
    sort_by = request.GET.get('sort', 'sequence_number')
    if sort_by == 'sequence_number':
        # Кастомная сортировка по числовому значению
        items_list.sort(key=lambda x: x.sort_key)
    elif sort_by == 'part_name__name':
        items_list.sort(key=lambda x: x.part_name.name)
    elif sort_by == 'material__name':
        items_list.sort(key=lambda x: x.material.name if x.material else '')
    elif sort_by == 'quantity':
        items_list.sort(key=lambda x: x.quantity)
    
    return render(request, 'calculator/order_detail.html', {
        'order': order, 
        'items': items_list,
        'search_query': search_query,
        'sort_by': sort_by
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
    """Печатная форма - детальный отчет"""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Сортируем с использованием sort_key
    items_list = list(items)
    items_list.sort(key=lambda x: x.sort_key)
    
    total_weight_kg = order.total_weight
    
    context = {
        'order': order,
        'items': items_list,
        'total_weight_kg': total_weight_kg,
        'date': timezone.now().strftime('%d.%m.%Y'),
        'user': request.user
    }
    
    return render(request, 'calculator/print_order_report.html', context)


@login_required
@transaction.atomic
def update_order_coefficient(request, order_id):
    """Обновление коэффициента массы в заказе (любой пользователь может менять)"""
    # Убираем фильтр по user, любой может менять коэффициент
    order = get_object_or_404(Order, id=order_id)
    
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
    """Печатная форма - группированный отчет"""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Сортируем детали для группировки
    items_list = list(items)
    items_list.sort(key=lambda x: x.sort_key)
    
    # Группируем по материалу и сортаменту
    grouped_data = {}
    for item in items_list:
        key = (item.material.id, item.stock_item.id) if not item.is_special else ('special', item.id)
        if key not in grouped_data:
            grouped_data[key] = {
                'material': item.material,
                'stock_item': item.stock_item,
                'total_weight': 0,
                'quantity': 0,
                'weight_per_item': item.weight,
                'items': [],
                'is_special': item.is_special,
                'part_name': item.part_name if item.is_special else None
            }
        grouped_data[key]['total_weight'] += item.total_weight
        grouped_data[key]['quantity'] += item.quantity
        grouped_data[key]['items'].append(item)
    
    # Сортируем группы
    grouped_list = sorted(grouped_data.values(), 
                         key=lambda x: (x['material'].name if x['material'] else 'zzz', 
                                      x['stock_item'].id if x['stock_item'] else 0))
    
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
    """Печатная форма - задание на заготовку"""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('part_name', 'material', 'stock_item')
    
    # Сортируем все детали
    items_list = list(items)
    items_list.sort(key=lambda x: x.sort_key)
    
    # Группируем по типу сортамента
    grouped_by_section = {
        'sheet': [],  # Лист
        'round': [],  # Кругляк
        'hexagon': [] # Шестигранник
    }
    
    for item in items_list:
        if item.is_special:
            # Особые запижи можно добавить в отдельную группу или пропустить
            continue
        section_type = item.stock_item.section_type
        if section_type in grouped_by_section:
            grouped_by_section[section_type].append(item)
    
    # Внутри каждой группы сортируем по номеру
    for section_type in grouped_by_section:
        grouped_by_section[section_type].sort(key=lambda x: x.sort_key)
    
    context = {
        'order': order,
        'sheet_items': grouped_by_section['sheet'],
        'round_items': grouped_by_section['round'],
        'hexagon_items': grouped_by_section['hexagon'],
        'date': timezone.now().strftime('%d.%m.%Y'),
        'user': request.user
    }
    
    return render(request, 'calculator/print_cutting_task.html', context)


@login_required
@transaction.atomic
def copy_order(request, order_id):
    """Копирование заказа с новым номером (можно копировать любой заказ)"""
    # Убираем фильтр по user, можно копировать любой заказ
    original_order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_order_number = request.POST.get('new_order_number')
        new_order_name = request.POST.get('new_order_name')
        
        if not new_order_number:
            messages.error(request, 'Необходимо указать номер нового заказа')
            return redirect('order_list')
        
        # Создаем новый заказ от имени текущего пользователя
        new_order = Order.objects.create(
            order_number=new_order_number,
            order_name=new_order_name or original_order.order_name,
            drawing_number=original_order.drawing_number,
            user=request.user,  # Новый заказ создается от имени текущего пользователя
            coefficient=original_order.coefficient
        )
        
        # Копируем все детали
        for item in original_order.items.all():
            OrderItem.objects.create(
                order=new_order,
                sequence_number=item.sequence_number,
                part_name=item.part_name,
                material=item.material,
                quantity=item.quantity,
                stock_item=item.stock_item,
                length=item.length,
                width=item.width,
                height=item.height,
                diameter=item.diameter,
                key_size=item.key_size,
                is_special=item.is_special
            )
        
        messages.success(request, f'Заказ успешно скопирован. Новый номер: {new_order_number}')
        return redirect('order_detail', order_id=new_order.id)
    
    return render(request, 'calculator/copy_order_modal.html', {'order': original_order})


@login_required
@transaction.atomic
def edit_order_item(request, order_id, item_id):
    """Редактирование детали в заказе"""
    order = get_object_or_404(Order, id=order_id)
    item = get_object_or_404(OrderItem, id=item_id, order=order)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST, instance=item)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Деталь успешно обновлена')
                return redirect('order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = OrderItemForm(instance=item)
    
    return render(request, 'calculator/edit_order_item.html', {
        'form': form, 
        'order': order,
        'item': item
    })

@login_required
def get_stock_items_by_material_and_type(request):
    """API для получения сортамента по материалу и типу"""
    material_id = request.GET.get('material_id')
    section_type = request.GET.get('section_type')
    
    stock_items = StockItem.objects.all()
    
    if material_id:
        stock_items = stock_items.filter(material_id=material_id)
    if section_type:
        stock_items = stock_items.filter(section_type=section_type)
    
    data = []
    for item in stock_items:
        data.append({
            'id': item.id,
            'text': str(item),
            'section_type': item.section_type,
            'width': str(item.width) if item.width else None,
            'diameter': str(item.diameter) if item.diameter else None,
            'key_size': str(item.key_size) if item.key_size else None,
        })
    
    return JsonResponse({'results': data})


@login_required
def search_part_names(request):
    """API для поиска наименований деталей"""
    query = request.GET.get('q', '')
    if query:
        parts = PartName.objects.filter(name__icontains=query)[:10]
    else:
        parts = PartName.objects.all()[:10]
    
    data = [{'id': part.id, 'text': part.name} for part in parts]
    return JsonResponse({'results': data})

@login_required
def search_materials(request):
    """API для поиска материалов"""
    query = request.GET.get('q', '')
    if query:
        materials = Material.objects.filter(name__icontains=query)[:10]
    else:
        materials = Material.objects.all()[:10]
    
    data = [{'id': m.id, 'text': f"{m.name} ({m.density} г/см³)"} for m in materials]
    return JsonResponse({'results': data})
@login_required
@transaction.atomic
def add_order_item(request, order_id):
    """Добавление детали в заказ"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Копируем POST данные
        post_data = request.POST.copy()
        
        # Получаем выбранный сортамент
        stock_item_id = post_data.get('stock_item')
        if stock_item_id:
            try:
                stock_item = StockItem.objects.get(id=stock_item_id)
                section_type = stock_item.section_type
                
                # Устанавливаем правильное поле length
                if section_type == 'sheet':
                    post_data['length'] = post_data.get('sheet_length', '')
                elif section_type == 'round':
                    post_data['length'] = post_data.get('round_length', '')
                elif section_type == 'hexagon':
                    post_data['length'] = post_data.get('hex_length', '')
                    
            except StockItem.DoesNotExist:
                pass
        
        form = OrderItemForm(post_data)
        
        if form.is_valid():
            try:
                item = form.save(commit=False)
                item.order = order
                item.save()
                
                # Сохраняем в сессию (ОДИН КЛЮЧ - 'last_item_params')
                request.session['last_item_params'] = {
                    'part_name_id': item.part_name_id,
                    'material_id': item.material_id if item.material else None,
                    'quantity': item.quantity,
                    'stock_item_id': item.stock_item_id if item.stock_item else None,
                    'length': float(item.length) if item.length else None,
                    'width': float(item.width) if item.width else None,
                    'height': float(item.height) if item.height else None,
                    'diameter': float(item.diameter) if item.diameter else None,
                    'key_size': float(item.key_size) if item.key_size else None,
                    'is_special': item.is_special,
                    'section_type': item.stock_item.section_type if item.stock_item else None,
                    'sequence_number': item.sequence_number,
                }
                
                messages.success(request, 'Деталь успешно добавлена')
                return redirect('order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        last_item = order.items.order_by('-id').first()
        next_number = order.items.count() + 1
        
        initial_data = {'sequence_number': str(next_number)}
        last_section_type = None
        last_measurements = {}
        if last_item:
            if last_item.part_name_id:
                initial_data['part_name'] = last_item.part_name_id
            if last_item.material_id:
                initial_data['material'] = last_item.material_id
            if last_item.quantity:
                initial_data['quantity'] = last_item.quantity
            if last_item.stock_item_id:
                initial_data['stock_item'] = last_item.stock_item_id
            initial_data['is_special'] = last_item.is_special
            if last_item.length:
                initial_data['length'] = float(last_item.length)
                last_measurements['length'] = str(last_item.length)
            if last_item.width:
                initial_data['width'] = float(last_item.width)
                last_measurements['width'] = str(last_item.width)
            if last_item.height:
                initial_data['height'] = float(last_item.height)
                last_measurements['height'] = str(last_item.height)
            if last_item.diameter:
                initial_data['diameter'] = float(last_item.diameter)
                last_measurements['diameter'] = str(last_item.diameter)
            if last_item.key_size:
                initial_data['key_size'] = float(last_item.key_size)
                last_measurements['key_size'] = str(last_item.key_size)
            last_section_type = last_item.stock_item.section_type if last_item.stock_item else None
        else:
            last_params = request.session.get('last_item_params', {})
            if last_params:
                if 'part_name_id' in last_params and last_params['part_name_id']:
                    initial_data['part_name'] = last_params['part_name_id']
                if 'material_id' in last_params and last_params['material_id']:
                    initial_data['material'] = last_params['material_id']
                if 'quantity' in last_params and last_params['quantity']:
                    initial_data['quantity'] = last_params['quantity']
                if 'stock_item_id' in last_params and last_params['stock_item_id']:
                    initial_data['stock_item'] = last_params['stock_item_id']
                if 'is_special' in last_params:
                    initial_data['is_special'] = last_params['is_special']
                if 'length' in last_params and last_params['length']:
                    initial_data['length'] = last_params['length']
                    last_measurements['length'] = str(last_params['length'])
                if 'width' in last_params and last_params['width']:
                    initial_data['width'] = last_params['width']
                    last_measurements['width'] = str(last_params['width'])
                if 'height' in last_params and last_params['height']:
                    initial_data['height'] = last_params['height']
                    last_measurements['height'] = str(last_params['height'])
                if 'diameter' in last_params and last_params['diameter']:
                    initial_data['diameter'] = last_params['diameter']
                    last_measurements['diameter'] = str(last_params['diameter'])
                if 'key_size' in last_params and last_params['key_size']:
                    initial_data['key_size'] = last_params['key_size']
                    last_measurements['key_size'] = str(last_params['key_size'])
            last_section_type = last_params.get('section_type')
        form = OrderItemForm(initial=initial_data)
    
    return render(request, 'calculator/order_item_form.html', {
        'form': form,
        'order': order,
        'last_section_type': last_section_type,
        'last_measurements': last_measurements,
    })
@login_required
def clear_last_item_params(request):
    """Очистка сохраненных параметров последней детали"""
    if 'last_item_params' in request.session:
        del request.session['last_item_params']
    messages.success(request, 'Настройки по умолчанию сброшены')
    return redirect(request.META.get('HTTP_REFERER', 'order_list'))

@login_required
@transaction.atomic
def create_part_name(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    form = PartNameForm(request.POST)
    if form.is_valid():
        part = form.save()
        return JsonResponse({'success': True, 'id': part.id, 'name': part.name})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@transaction.atomic
def create_material(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    form = MaterialForm(request.POST)
    if form.is_valid():
        m = form.save()
        return JsonResponse({'success': True, 'id': m.id, 'name': m.name, 'density': str(m.density)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@transaction.atomic
def create_stock_item(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    form = StockItemForm(request.POST)
    if form.is_valid():
        si = form.save()
        return JsonResponse({
            'success': True,
            'id': si.id,
            'text': str(si),
            'section_type': si.section_type,
            'material_id': si.material_id,
            'width': str(si.width) if si.width else None,
            'diameter': str(si.diameter) if si.diameter else None,
            'key_size': str(si.key_size) if si.key_size else None,
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
