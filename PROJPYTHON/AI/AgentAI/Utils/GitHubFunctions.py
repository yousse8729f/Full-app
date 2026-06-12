import base64
from os import getenv

from github import Github,Auth
from dotenv import load_dotenv
from github.ContentFile import ContentFile
from github.Repository import Repository

load_dotenv()
GIT_TOKEN = getenv("GITHUB_TOKEN")
auth = Auth.Token(GIT_TOKEN)
g = Github(auth=auth,lazy=True,retry=3,pool_size=30)

repo = g.get_repo(full_name_or_id="yousse8729f/langchain_projects_agent")


def search_Repository_by_language(query:str):

    return [repo for repo in g.get_user().get_repos() for ln in repo.get_languages().keys() if ln.lower()==query.lower()]


def search_Repository_by_name(name:str):
    return g.get_user().get_repo(name=name)


def edit_Repository(name:str,new_name:str,new_discription:str,private):
    repo = g.get_user().get_repo(name=name)

    repo.edit(name=new_name,description=new_discription,private=private)
    repo.get_branches()
def repo_Info(repo:Repository):
    topic = repo.get_topics()
    starts = repo.stargazers_count
    open_issues =[]
    closed_issues=[]
    for open,close in zip(repo.get_issues(state="open"),repo.get_issues(state="close")):
        open_issues.append(open)
        closed_issues.append(close)
    files=[]
    contents = repo.get_contents("")
    for file in contents:
        files.append(file)
    return {
        "name":repo.name,
        "topics":topic,
        "stargazers_count":starts,
        "open_issues":open_issues,
        "close_issues":closed_issues,
        "files":files
    }
def get_file(repo:Repository,file:ContentFile):
    return repo.get_contents(file.path)
def create_file(repo:Repository,file:str,branch:str,txt:str,commit:str):
    repo.create_file(file,commit,txt,branch=branch)
def Update_file(repo:Repository,file:ContentFile,branch:str,txt:str,commit:str):
    repo.update_file(file.path,commit,txt,sha=file.sha,branch=branch)
def Update_file(repo:Repository,file:ContentFile,branch:str,txt:str,commit:str):
    repo.update_file(file.path,commit,txt,sha=file.sha,branch=branch)








