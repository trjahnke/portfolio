from django.shortcuts import render
import requests
from datetime import datetime
from .cron import get_repos
import psycopg2.extras
import os


def landing(request):
    # Pull repos from database
    # Connect to the database
    conn = psycopg2.connect(database=os.environ['DJANGO_DB_NAME'], user=os.environ['DB_USER'],
                            password=os.environ['DB_PASSWORD'], host=os.environ['DB_HOST'], port=os.environ['DB_PORT'])

    # Save repos to database
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Fetch the repos table from the database and convert it to a list
    cur.execute("SELECT * FROM repos")
    db_repos = cur.fetchall()
    repos = []

    for repo in db_repos:
        updated_at = repo['updated_at'].strip()
        repo['updated_at'] = datetime.strptime(
            updated_at, '%Y-%m-%dT%H:%M:%SZ')

        repos.append(repo)

    conn.close()

    return render(request, 'landing.html', {'repos': repos})
