import requests
import psycopg2
import os
import json


FIELDS = {
    "id": "INT NOT NULL PRIMARY KEY",
    "name": "CHAR(150)",
    "full_name": "CHAR(150)",
    "private": "CHAR(150)",
    "html_url": "CHAR(150)",
    "description": "CHAR(250)",
    "git_url": "CHAR(150)",
    "languages_url": "CHAR(150)",
    "ssh_url": "CHAR(150)",
    "tags_url": "CHAR(150)",
    "clone_url": "CHAR(150)",
    "homepage": "CHAR(150)",
    "language": "CHAR(150)",
    "pushed_at": "CHAR(150)",
    "created_at": "CHAR(150)",
    "updated_at": "CHAR(150)"
}


class APILimitError(Exception):
    pass


def fields_str():
    fields_str = "".join(f'{field} {FIELDS[field]}, ' for field in FIELDS)
    fields_str = fields_str[:-2]
    return fields_str


def table_builder(cur):
    table_maker = f"CREATE TABLE IF NOT EXISTS repos ({fields_str()});"
    try:
        cur.execute(table_maker)
    except Exception as e:
        print(f"Error while creating table {e}")


def fetch_repos():
    # Fetch the repos from GitHub using unauthenticated requests
    repos = requests.get('https://api.github.com/users/trjahnke/repos')
    repos = repos.json()
    return repos


def insert_repo(repo, cur, conn):
    data = [repo[field] for field in FIELDS]
    cur.execute(
        "INSERT INTO repos VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", data)
    print(f"Inserted {repo['name']}")
    conn.commit()


def update_row(repo, cur, conn):
    desc = repo['description']
    if desc is not None:
        desc = desc.replace("'", "")

    cur.execute(f"UPDATE repos SET id = {repo['id']}, name = \'{repo['name']}\', full_name = \'{repo['full_name']}\', private = \'{repo['private']}\', html_url = \'{repo['html_url']}\', description = \'{desc}\', git_url = \'{repo['git_url']}\', languages_url = \'{repo['languages_url']}\', ssh_url = \'{repo['ssh_url']}\', tags_url = \'{repo['tags_url']}\', clone_url = \'{repo['clone_url']}\', homepage = \'{repo['homepage']}\', language = \'{repo['language']}\', pushed_at = \'{repo['pushed_at']}\', created_at = \'{repo['created_at']}\', updated_at = \'{repo['updated_at']}\' WHERE id={repo['id']}")
    conn.commit()


def get_repos():
    # Connect to the database
    conn = psycopg2.connect(database=os.environ['DJANGO_DB_NAME'], user=os.environ['DB_USER'],
                            password=os.environ['DB_PASSWORD'], host=os.environ['DB_HOST'], port=os.environ['DB_PORT'])

    # Save repos to database
    cur = conn.cursor()

    repos = fetch_repos()

    # try:
    #     repos = fetch_repos()
    #     import re
    #     message = re.search('^API', repos[0])
    #     if (message is not None):
    #         raise APILimitError(repos['message'])
    # except APILimitError as e:
    #     print(e)
    #     conn.close()

    # Create the table if it doesn't exist
    table_builder(cur)

    cur.execute("SELECT * FROM repos")
    db_repos = cur.fetchall()
    db_repo_ids = [repo[0] for repo in db_repos]

    for repo in repos:
        if (repo['id'] not in db_repo_ids):
            print(f"{repo['name']} not found in database, Inserting...")
            insert_repo(repo, cur, conn)
        else:
            print(f"{repo['name']} found in database, Updating...")
            update_row(repo, cur, conn)

    conn.commit()
    conn.close()

    return repos

get_repos()
