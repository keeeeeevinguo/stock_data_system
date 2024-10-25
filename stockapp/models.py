# models.py
from django.db import models
from django.utils import timezone

# Model for storing financial data
class FinancialData(models.Model):
    stock_symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("stock_symbol", "date")
        indexes = [
            models.Index(fields=["stock_symbol", "date"]),
        ]

    def __str__(self):
        return f"{self.stock_symbol} - {self.date}"
    
# Model for storing predicted financial data
class PredictedFinancialData(models.Model):
    stock_symbol = models.CharField(max_length=10)
    date = models.DateField()
    predicted_close_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("stock_symbol", "date")
        indexes = [
            models.Index(fields=["stock_symbol", "date"]),
        ]

    def __str__(self):
        return f"Prediction for {self.stock_symbol} - {self.date}"