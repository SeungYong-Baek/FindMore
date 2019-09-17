from django.db import models

# Create your models here.

from django.urls import reverse

class BAH_List(models.Model):
    MARKET = (
            ('KOSPI','KOSPI'),
            ('KOSDAQ','KOSDAQ'),
            ('NASDAQ','NASDAQ'),
            )
    BUY_PERIOD = (
            (20,'Monthly'),
            )
    DIV_PERIOD = (
            (60,'Quarterly'),
            (240,'Yearly'),
            )
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)
    market = models.CharField(max_length=20, choices=MARKET, default='KOSPI')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    buy_quantity = models.IntegerField()
    buy_period = models.IntegerField(choices=BUY_PERIOD, default='Monthly')
    capital_base = models.IntegerField()
    div_period = models.IntegerField(choices=DIV_PERIOD, default='Quarterly')
    expected_dividend = models.IntegerField()
    shares = models.IntegerField(null=True)
    last_pv = models.IntegerField(null=True)
    last_value = models.IntegerField(null=True)
    last_cash = models.IntegerField(null=True)
    capital_used = models.IntegerField(null=True)
    dividend_sum = models.IntegerField(null=True)
    expected_return = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    expected_dividend_return = models.DecimalField(max_digits=20, decimal_places=3, null=True)
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
        return reverse('bah:bah_detail', kwargs={'pk': self.pk})
