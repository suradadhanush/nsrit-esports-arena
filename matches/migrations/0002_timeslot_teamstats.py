from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
        ('teams', '0001_initial'),
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_booked', models.BooleanField(default=False)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='tournaments.tournament')),
            ],
            options={'db_table': 'time_slots', 'ordering': ['start_time']},
        ),
        migrations.CreateModel(
            name='TeamStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matches_played', models.IntegerField(default=0)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_stats', to='tournaments.tournament')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_stats', to='teams.team')),
            ],
            options={'db_table': 'team_stats', 'unique_together': {('tournament', 'team')}},
        ),
    ]
