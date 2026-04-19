"""
Payments App - Razorpay Integration
"""
from django.db import models
from django.conf import settings
from players.models import Player
from tournaments.models import Tournament


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Payment Pending'),
        ('SUCCESS', 'Payment Successful'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    # ─── LAYER 3: Payment bound to player + tournament ─────────────────
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    # ──────────────────────────────────────────────────────────────────

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=256, blank=True)

    amount = models.IntegerField(help_text='Amount in paise (INR × 100)')
    currency = models.CharField(max_length=5, default='INR')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    # Receipt
    receipt = models.CharField(max_length=100, blank=True)

    # ── Retry & failure tracking ───────────────────────────────────────────────
    retry_count = models.IntegerField(default=0, help_text='Number of payment attempts')
    failure_reason = models.TextField(blank=True, help_text='Razorpay failure description if failed')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        # ─── LAYER 3 DB CONSTRAINT: One payment per player-tournament ──
        unique_together = [('player', 'tournament')]
        # ──────────────────────────────────────────────────────────────
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.player.ign} | {self.tournament.title} | {self.status}"

    @property
    def amount_inr(self):
        return self.amount / 100

    def mark_failed(self, reason=''):
        self.status = 'FAILED'
        self.failure_reason = reason
        self.save(update_fields=['status', 'failure_reason'])

    def increment_retry(self):
        self.retry_count += 1
        self.status = 'PENDING'
        self.save(update_fields=['retry_count', 'status'])
