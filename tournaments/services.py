from django.db import transaction
from django.utils import timezone
from .models import Tournament, Registration


class TournamentService:

    @staticmethod
    @transaction.atomic
    def register_player(player, tournament_id):
        tournament = Tournament.objects.select_for_update().get(id=tournament_id)

        if not tournament.is_registration_open:
            raise ValueError("Registration is closed")

        if tournament.slots_remaining <= 0:
            raise ValueError("No slots available")

        registration, created = Registration.objects.get_or_create(
            player=player,
            tournament=tournament
        )

        if not created:
            raise ValueError("Already registered")

        return registration

    @staticmethod
    def confirm_payment(registration_id, transaction_id=None):
        registration = Registration.objects.get(id=registration_id)

        registration.payment_status = "SUCCESS"
        registration.transaction_id = transaction_id
        registration.status = "CONFIRMED"
        registration.confirmed_at = timezone.now()
        registration.save()

        return registration