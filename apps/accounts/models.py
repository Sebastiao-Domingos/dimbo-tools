from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Modelo de utilizador com campos extras para SaaS"""
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    daily_conversions = models.PositiveIntegerField(default=0)
    last_conversion_date = models.DateField(auto_now_add=True)
    
    def can_convert(self):
        """Verifica se o utilizador pode fazer mais conversões hoje"""
        from datetime import date
        from apps.subscriptions.services import get_user_plan
        
        if self.last_conversion_date != date.today():
            self.daily_conversions = 0
            self.last_conversion_date = date.today()
            self.save(update_fields=['daily_conversions', 'last_conversion_date'])
        
        plan = get_user_plan(self)
        if plan == 'premium':
            return True
        # Free: limite de 5 conversões/dia
        return self.daily_conversions < 50
    
    def increment_conversion(self):
        """Incrementa contador diário"""
        from datetime import date
        if self.last_conversion_date != date.today():
            self.daily_conversions = 0
            self.last_conversion_date = date.today()
        self.daily_conversions += 1
        self.save(update_fields=['daily_conversions', 'last_conversion_date'])

    @property
    def plan(self):
        if hasattr(self, 'subscription'):
            return self.subscription.plan
        return 'free'