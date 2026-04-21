"""Teams Views"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q
from .models import Team, TeamMember, TeamInvite, TeamJoinRequest
from players.models import Player
from .forms import TeamCreateForm, TeamInviteForm


def team_list(request):
    teams = Team.objects.prefetch_related('members').all()
    game = request.GET.get('game', '')
    search = request.GET.get('search', '')
    if game:
        teams = teams.filter(game=game)
    if search:
        teams = teams.filter(Q(name__icontains=search) | Q(tag__icontains=search))
    context = {
        'teams': teams,
        'game_choices': Team.GAME_CHOICES,
        'filters': {'game': game, 'search': search},
    }
    return render(request, 'teams/list.html', context)


def team_detail(request, slug):
    team = get_object_or_404(Team, slug=slug)
    members = team.members.select_related('player__user').all()
    return render(request, 'teams/detail.html', {
        'team': team,
        'members': members,
    })


@login_required
def create_team(request):
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        messages.error(request, 'Create your player profile first!')
        return redirect('players:create_profile')

    # Check if player already has a team
    if hasattr(player, 'team_membership'):
        messages.warning(request, 'You are already in a team. Leave your current team to create a new one.')
        return redirect('teams:detail', slug=player.team_membership.team.slug)

    if request.method == 'POST':
        form = TeamCreateForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(commit=False)
            team.captain = player
            team.slug = slugify(team.name)
            team.save()
            # Auto-add captain as member
            TeamMember.objects.create(team=team, player=player, role='CAPTAIN')
            messages.success(request, f'🎮 Team [{team.tag}] {team.name} created! You are the captain.')
            return redirect('teams:detail', slug=team.slug)
    else:
        form = TeamCreateForm()

    return render(request, 'teams/create_team.html', {'form': form})


@login_required
def invite_player(request, slug):
    team = get_object_or_404(Team, slug=slug)
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        return redirect('players:create_profile')

    if team.captain != player:
        messages.error(request, 'Only the team captain can invite players.')
        return redirect('teams:detail', slug=slug)

    if request.method == 'POST':
        form = TeamInviteForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.team = team
            invite.invited_by = player
            invite.save()
            messages.success(request, f'Invitation sent to {invite.invited_player.ign}!')
            return redirect('teams:detail', slug=slug)
    else:
        form = TeamInviteForm()

    return render(request, 'teams/invite.html', {'form': form, 'team': team})


@login_required
def respond_invite(request, invite_id, action):
    invite = get_object_or_404(TeamInvite, id=invite_id)
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        return redirect('players:create_profile')

    if invite.invited_player != player:
        messages.error(request, 'This invite is not for you.')
        return redirect('players:dashboard')

    if action == 'accept':
        if hasattr(player, 'team_membership'):
            messages.warning(request, 'Leave your current team first!')
        else:
            TeamMember.objects.create(team=invite.team, player=player, role=invite.role)
            invite.status = 'ACCEPTED'
            invite.save()
            messages.success(request, f'🎉 You joined [{invite.team.tag}] {invite.team.name}!')
    elif action == 'reject':
        invite.status = 'REJECTED'
        invite.save()
        messages.info(request, 'Invite rejected.')

    return redirect('players:dashboard')


@login_required
def leave_team(request):
    try:
        membership = TeamMember.objects.get(player=request.user.player_profile)
        if membership.role == 'CAPTAIN':
            messages.error(request, 'Transfer captaincy before leaving the team.')
        else:
            membership.delete()
            messages.success(request, 'You have left the team.')
    except TeamMember.DoesNotExist:
        messages.info(request, 'You are not in any team.')
    return redirect('players:dashboard')


@login_required
def request_join(request, slug):
    """Player sends a join request to a team."""
    team = get_object_or_404(Team, slug=slug, is_recruiting=True)

    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        messages.error(request, 'Create your player profile first!')
        return redirect('players:create_profile')

    if hasattr(player, 'team_membership'):
        messages.warning(request, 'Leave your current team first before joining another.')
        return redirect('teams:detail', slug=slug)

    if TeamJoinRequest.objects.filter(team=team, player=player, status='PENDING').exists():
        messages.warning(request, 'You already have a pending request for this team.')
        return redirect('teams:detail', slug=slug)

    if request.method == 'POST':
        role = request.POST.get('role', 'MEMBER')
        message = request.POST.get('message', '').strip()

        TeamJoinRequest.objects.create(
            team=team,
            player=player,
            role=role,
            message=message,
        )
        messages.success(request, f'✅ Join request sent to [{team.tag}] {team.name}! Wait for captain approval.')
        return redirect('teams:detail', slug=slug)

    return render(request, 'teams/request_join.html', {
        'team': team,
        'role_choices': TeamMember.ROLE_CHOICES,
    })


@login_required
def respond_join_request(request, request_id, action):
    """Captain accepts or rejects a join request."""
    join_request = get_object_or_404(TeamJoinRequest, id=request_id)

    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        return redirect('players:dashboard')

    # Only captain can respond
    if join_request.team.captain != player:
        messages.error(request, 'Only the team captain can respond to join requests.')
        return redirect('players:dashboard')

    if action == 'accept':
        if hasattr(join_request.player, 'team_membership'):
            messages.warning(request, f'{join_request.player.ign} is already in a team.')
        else:
            TeamMember.objects.create(
                team=join_request.team,
                player=join_request.player,
                role=join_request.role,
            )
            join_request.status = 'ACCEPTED'
            join_request.save()
            messages.success(request, f'✅ {join_request.player.ign} added to your team!')

    elif action == 'reject':
        join_request.status = 'REJECTED'
        join_request.save()
        messages.info(request, f'Join request from {join_request.player.ign} rejected.')

    return redirect('teams:detail', slug=join_request.team.slug)
