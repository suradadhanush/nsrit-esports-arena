from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamJoinRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('CAPTAIN', 'Captain'), ('IGL', 'In-Game Leader'), ('FRAGGER', 'Fragger'), ('SUPPORT', 'Support'), ('SCOUT', 'Scout'), ('SNIPER', 'Sniper'), ('SUBSTITUTE', 'Substitute'), ('MEMBER', 'Member')], default='MEMBER', max_length=15)),
                ('message', models.TextField(blank=True, max_length=300)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='teams.team')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='players.player')),
            ],
            options={
                'verbose_name': 'Team Join Request',
                'db_table': 'team_join_requests',
                'unique_together': {('team', 'player')},
            },
        ),
    ]
