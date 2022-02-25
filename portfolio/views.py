from django.shortcuts import render
import requests
from datetime import datetime


def landing(request):
    pinned_repos = ['corgi_texter', 'trjahnke', 'homelab']
    excluded_repos = ['']

    repos = requests.get('https://api.github.com/users/trjahnke/repos')
    repos = repos.json()

    for repo in repos:
        if repo['name'] in excluded_repos:
            repos.remove(repo)
            break

        repo['updated_at'] = datetime.strptime(
            repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')

        if repo['name'] in pinned_repos:
            temp = repo
            repos.insert(0, repos.pop(repos.index(repo)))

    return render(request, 'landing.html', {'repos': repos})
