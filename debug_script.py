
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "production_calculator.settings")
django.setup()

from calculator.models import Order, OrderItem, Material

# Write output to a UTF-8 file so we can see all characters correctly
with open('debug_output.txt', 'w', encoding='utf-8') as f:
    f.write("=== Список всех материалов в базе данных ===\n")
    materials = Material.objects.all()
    for mat in materials:
        f.write(f"  ID: {mat.id}, name: {repr(mat.name)}, name.upper(): {repr(mat.name.upper())}\n")

    f.write("\n=== Проверка существующих заказов ===\n")
    orders = Order.objects.all()
    for order in orders:
        f.write(f"\nЗаказ №{order.order_number}, ID: {order.id}:\n")
        items = order.items.all().select_related('part_name', 'material', 'stock_item')
        for item in items:
            mat_name = repr(item.material.name) if item.material else "None"
            f.write(f"  - Деталь №{item.sequence_number}:\n")
            f.write(f"    Материал: {mat_name}, (name.upper(): {repr(item.material.name.upper()) if item.material else ''})\n")
            f.write(f"    Сортамент тип: {item.stock_item.section_type if item.stock_item else '—'}\n")
            f.write(f"    is_special: {item.is_special}\n")

    f.write("\n\n=== Тестирование логики группировки ===\n")
    if orders.exists():
        test_order = orders.first()  # Берем первый заказ для теста
        f.write(f"Тестируем заказ: {test_order}\n")

        items = test_order.items.all().select_related('part_name', 'material', 'stock_item')
        items_list = list(items)

        special_materials = {'1.2343', '4Х5МФС'}

        f.write(f"\nОсобые материалы (list): {[repr(m) for m in special_materials]}\n")
        f.write(f"Особые материалы (upper list): {[repr(m.upper()) for m in special_materials]}\n")
        grouped_by_section = {
            'sheet': [],
            'round': [],
            'tube': [],
        }

        for item in items_list:
            f.write(f"\nОбрабатываем деталь №{item.sequence_number}\n")
            if item.is_special:
                f.write("  is_special = True → пропускаем\n")
                continue

            section_type = item.stock_item.section_type
            material_name = item.material.name.strip().upper() if item.material else ''

            f.write(f"  section_type: {repr(section_type)}\n")
            f.write(f"  material_name (stripped upper): {repr(material_name)}\n")

            # Also check if material name contains any of the special substrings!
            found_special = False
            for sm in special_materials:
                if sm.upper() in material_name:
                    found_special = True
                    break

            if section_type == 'sheet' and found_special:
                f.write("  → добавляем в 'round'\n")
                grouped_by_section['round'].append(item)
            elif section_type == 'sheet':
                f.write("  → добавляем в 'sheet'\n")
                grouped_by_section['sheet'].append(item)
            elif section_type == 'round':
                if item.diameter and float(item.diameter) > 50:
                    f.write("  → добавляем в 'round' (diameter >50)\n")
                    grouped_by_section['round'].append(item)
                else:
                    f.write("  → не добавляем (diameter ≤50)\n")
            elif section_type == 'tube':
                f.write("  → добавляем в 'tube'\n")
                grouped_by_section['tube'].append(item)

        f.write("\nИтог:\n")
        f.write(f"  sheet items: {[item.sequence_number for item in grouped_by_section['sheet']]}\n")
        f.write(f"  round items: {[item.sequence_number for item in grouped_by_section['round']]}\n")
        f.write(f"  tube items: {[item.sequence_number for item in grouped_by_section['tube']]}\n")

print("Debug output written to debug_output.txt! Please check that file!")

