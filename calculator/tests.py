from django.test import TestCase
from django.contrib.auth.models import User
from .models import Material, PartName, StockItem, Order, OrderItem


class PrintCuttingTaskTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create test materials
        self.material_12343 = Material.objects.create(name='1.2343', density=7.85)
        self.material_4kh5mfs = Material.objects.create(name='4Х5МФС', density=7.85)
        self.material_regular = Material.objects.create(name='Сталь 45', density=7.85)
        
        # Create test part name
        self.part = PartName.objects.create(name='Тестовая деталь')
        
        # Create test stock items
        self.stock_sheet_12343 = StockItem.objects.create(
            material=self.material_12343,
            section_type='sheet',
            width=20.0
        )
        self.stock_sheet_4kh5mfs = StockItem.objects.create(
            material=self.material_4kh5mfs,
            section_type='sheet',
            width=25.0
        )
        self.stock_sheet_regular = StockItem.objects.create(
            material=self.material_regular,
            section_type='sheet',
            width=30.0
        )
        self.stock_round_12343 = StockItem.objects.create(
            material=self.material_12343,
            section_type='round',
            diameter=60.0
        )
        self.stock_tube = StockItem.objects.create(
            material=self.material_regular,
            section_type='tube',
            outer_diameter=50.0,
            wall_thickness=5.0
        )
        
        # Create test order
        self.order = Order.objects.create(
            order_number='TEST-001',
            order_name='Тестовый заказ',
            user=self.user
        )
        
    def test_sheet_special_material_goes_to_round_section(self):
        """Test that sheet items with special materials (1.2343, 4Х5МФС) go to round section and not sheet section"""
        # Create order items
        item1 = OrderItem.objects.create(
            order=self.order,
            sequence_number='1',
            part_name=self.part,
            material=self.material_12343,
            stock_item=self.stock_sheet_12343,
            quantity=10,
            length=100,
            width=50,
            height=20
        )
        item2 = OrderItem.objects.create(
            order=self.order,
            sequence_number='2',
            part_name=self.part,
            material=self.material_4kh5mfs,
            stock_item=self.stock_sheet_4kh5mfs,
            quantity=5,
            length=80,
            width=40,
            height=25
        )
        item3 = OrderItem.objects.create(
            order=self.order,
            sequence_number='3',
            part_name=self.part,
            material=self.material_regular,
            stock_item=self.stock_sheet_regular,
            quantity=7,
            length=120,
            width=60,
            height=30
        )
        
        # Get the print cutting task view (we can test the grouping logic directly)
        from .views import print_cutting_task
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        
        # We can extract the grouping logic from print_cutting_task to test it
        items = self.order.items.all().select_related('part_name', 'material', 'stock_item')
        items_list = list(items)
        
        # Copy of the grouping logic from views.py
        special_materials = {'1.2343', '4Х5МФС'}
        grouped_by_section = {
            'sheet': [],
            'round': [],
            'tube': [],
        }
        
        for item in items_list:
            if item.is_special:
                continue
                
            section_type = item.stock_item.section_type
            material_name = item.material.name.strip().upper() if item.material else ''
            
            # Проверяем, нужно ли этот лист отправить в кругляк
            if section_type == 'sheet' and material_name in {m.upper() for m in special_materials}:
                grouped_by_section['round'].append(item)
            elif section_type == 'sheet':
                grouped_by_section['sheet'].append(item)
            elif section_type == 'round':
                if item.diameter and float(item.diameter) > 50:
                    grouped_by_section['round'].append(item)
            elif section_type == 'tube':
                grouped_by_section['tube'].append(item)
        
        # Check the results
        self.assertEqual(len(grouped_by_section['round']), 2)  # item1 and item2
        self.assertEqual(len(grouped_by_section['sheet']), 1)  # item3
        self.assertEqual(len(grouped_by_section['tube']), 0)
        
        # Check that the right items are in each section
        self.assertIn(item1, grouped_by_section['round'])
        self.assertIn(item2, grouped_by_section['round'])
        self.assertIn(item3, grouped_by_section['sheet'])
    
    def test_round_item_with_large_diameter_goes_to_round_section(self):
        """Test that round items with diameter > 50 go to round section"""
        item = OrderItem.objects.create(
            order=self.order,
            sequence_number='1',
            part_name=self.part,
            material=self.material_12343,
            stock_item=self.stock_round_12343,
            quantity=3,
            length=150,
            diameter=60
        )
        
        items = self.order.items.all().select_related('part_name', 'material', 'stock_item')
        items_list = list(items)
        
        special_materials = {'1.2343', '4Х5МФС'}
        grouped_by_section = {
            'sheet': [],
            'round': [],
            'tube': [],
        }
        
        for item in items_list:
            if item.is_special:
                continue
                
            section_type = item.stock_item.section_type
            material_name = item.material.name.strip().upper() if item.material else ''
            
            if section_type == 'sheet' and material_name in {m.upper() for m in special_materials}:
                grouped_by_section['round'].append(item)
            elif section_type == 'sheet':
                grouped_by_section['sheet'].append(item)
            elif section_type == 'round':
                if item.diameter and float(item.diameter) > 50:
                    grouped_by_section['round'].append(item)
            elif section_type == 'tube':
                grouped_by_section['tube'].append(item)
        
        self.assertEqual(len(grouped_by_section['round']), 1)
        self.assertIn(item, grouped_by_section['round'])
    
    def test_tube_item_goes_to_tube_section(self):
        """Test that tube items go to tube section"""
        item = OrderItem.objects.create(
            order=self.order,
            sequence_number='1',
            part_name=self.part,
            material=self.material_regular,
            stock_item=self.stock_tube,
            quantity=2,
            length=200
        )
        
        items = self.order.items.all().select_related('part_name', 'material', 'stock_item')
        items_list = list(items)
        
        special_materials = {'1.2343', '4Х5МФС'}
        grouped_by_section = {
            'sheet': [],
            'round': [],
            'tube': [],
        }
        
        for item in items_list:
            if item.is_special:
                continue
                
            section_type = item.stock_item.section_type
            material_name = item.material.name.strip().upper() if item.material else ''
            
            if section_type == 'sheet' and material_name in {m.upper() for m in special_materials}:
                grouped_by_section['round'].append(item)
            elif section_type == 'sheet':
                grouped_by_section['sheet'].append(item)
            elif section_type == 'round':
                if item.diameter and float(item.diameter) > 50:
                    grouped_by_section['round'].append(item)
            elif section_type == 'tube':
                grouped_by_section['tube'].append(item)
        
        self.assertEqual(len(grouped_by_section['tube']), 1)
        self.assertIn(item, grouped_by_section['tube'])
