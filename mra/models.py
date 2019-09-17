from django.db import models

# Create your models here.

from django.urls import reverse

class MRA_List(models.Model):
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
    adf = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    adf_pv = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    adf_one = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    adf_five = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    hurst = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    half_life = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    sd = models.DecimalField(max_digits=20,decimal_places=3, null=True)
    mean = models.DecimalField(max_digits=20,decimal_places=3, null=True)
    volume = models.DecimalField(max_digits=20, decimal_places=3, null=True)
    quantile_q1 = models.IntegerField(null=True)
    quantile_q2 = models.IntegerField(null=True)
    quantile_q3 = models.IntegerField(null=True)
    quantile_path = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        created = self.created.strftime("%Y-%m-%d, %H:%M:%S")
        start_date = self.start_date.strftime("%Y-%m-%d")
        end_date = self.end_date.strftime("%Y-%m-%d")

        return self.name+" / "+created+" / "+start_date+"~"+end_date

    def get_absolute_url(self):
        return reverse('mra:mra_list_detail', kwargs={'pk': self.pk})
