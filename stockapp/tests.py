from django.test import TestCase
from django.urls import reverse
from .models import FinancialData
import datetime

class StockAppTest(TestCase):
    def setUp(self):
        # Set up initial data
        FinancialData.objects.create(
            stock_symbol='AAPL', 
            date=datetime.date(2023, 1, 1), 
            open_price=150.00, 
            close_price=152.00, 
            high_price=153.00, 
            low_price=149.00, 
            volume=12000
        )
        FinancialData.objects.create(
            stock_symbol='AAPL', 
            date=datetime.date(2023, 1, 2), 
            open_price=152.00, 
            close_price=155.00, 
            high_price=156.00, 
            low_price=150.00, 
            volume=15000
        )

    def test_fetch_financial_data(self):
        response = self.client.get(reverse('fetch_financial_data', args=['AAPL']))
        self.assertEqual(response.status_code, 200)

    def test_backtest_strategy(self):
        response = self.client.get(reverse('backtest_strategy', args=['AAPL', 10000]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_return', response.json())
        self.assertIn('max_drawdown', response.json())
        self.assertIn('number_of_trades', response.json())
