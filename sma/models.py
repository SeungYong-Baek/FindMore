from django.db import models

# Create your models here.

from django.urls import reverse

class SMA_List(models.Model):
    MARKET = (
            ('KOSPI','KOSPI'),
            ('KOSDAQ','KOSDAQ'),
            ('NASDAQ','NASDAQ'),
            )
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)
    market = models.CharField(max_length=20, choices=MARKET, default='KOSPI')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    short_ma = models.IntegerField()
    long_ma = models.IntegerField()
    buy_quantity = models.IntegerField()
    sell_quantity = models.IntegerField()
    capital_base = models.IntegerField()
    shares = models.IntegerField(null=True)
    last_pv = models.IntegerField(null=True)
    last_value = models.IntegerField(null=True)
    last_cash = models.IntegerField(null=True)
    capital_used = models.IntegerField(null=True)
    expected_return = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    bt_path = models.CharField(max_length=100, null=True)
    pv_path = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        created = self.created.strftime("%Y-%m-%d, %H:%M:%S")
        start_date = self.start_date.strftime("%Y-%m-%d")
        end_date = self.end_date.strftime("%Y-%m-%d")

        return self.name+" / "+created+" / "+start_date+"~"+end_date

    def get_absolute_url(self):
        return reverse('sma:sma_detail', kwargs={'pk': self.pk})
