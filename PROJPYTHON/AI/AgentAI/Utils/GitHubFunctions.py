import base64
from os import getenv

from github import Github, Auth, GithubException
from dotenv import load_dotenv
from github.Branch import Branch
from github.ContentFile import ContentFile
from github.Repository import Repository
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Github")

load_dotenv()
GIT_TOKEN = getenv("GITHUB_TOKEN")
auth = Auth.Token(GIT_TOKEN)
g = Github(auth=auth, lazy=True, retry=3, pool_size=30)


# ============ REPOSITORY ============
@mcp.tool()
def get_All_Repo():
    """

    :return: need to get all name of the repository
    """
    try:
        return [repo.name for repo in g.get_user().get_repos()]
    except GithubException as e:
        return {"error":f"somthing wrong happend {e}"}

@mcp.tool()
def create_repo(name: str, des: str, priv: bool, has_issue: bool, has_wiki: bool):
    """
    Create a new GitHub repository for the authenticated user.

    Parameters:
        name (str): The name of the new repository.
        des (str): A short description of the repository.
        priv (bool): If True, the repo is private; if False, it's public.
        has_issue (bool): If True, enables the Issues feature on the repo.
        has_wiki (bool): If True, enables the Wiki feature on the repo.

    Returns:
        dict: A status message indicating success or the error encountered.
    """
    try:
        repo = g.get_user().create_repo(
            name=name,
            description=des,
            private=priv,
            has_wiki=has_wiki,
            has_issues=has_issue,
            auto_init=True
        )
        g.get_user().get_repo().delete()
        return {"status": "success", "repo": repo.full_name}
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def search_Repository_by_language(query: str):
    """
    Search the authenticated user's repositories for ones written in a given
    programming language.

    Parameters:
        query (str): The programming language to search for (e.g. "Python").
                      Matching is case-insensitive.

    Returns:
        list[str] | dict: A list of matching repository full names,
        or a dict with an error message if the request fails.
    """
    try:
        return [
            repo.full_name
            for repo in g.get_user().get_repos()
            for ln in repo.get_languages().keys()
            if ln.lower() == query.lower()
        ]
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def search_Repository_by_name(name: str):
    """
    Find a repository owned by the authenticated user by its exact name.

    Parameters:
        name (str): The exact name of the repository to look up.

    Returns:
        dict: The matching repository's basic info, or an error message dict
        if the repository is not found or the request fails.
    """
    try:
        repo = g.get_user().get_repo(name=name)
        return {"status": "success", "full_name": repo.full_name, "private": repo.private}
    except GithubException as e:
        return {"status": "error", "message": str(e)}


def _get_repo(name: str) -> Repository:
    """Internal helper - returns a Repository object, not exposed as an MCP tool."""
    if "/" in name:
        return g.get_repo(name)
    return g.get_user().get_repo(name=name)


@mcp.tool()
def edit_Repository(name: str, new_name: str, new_discription: str, private: bool):
    """
    Edit the metadata of an existing repository.

    Parameters:
        name (str): The repository name to edit.
        new_name (str): The new name to give the repository.
        new_discription (str): The new description for the repository.
        private (bool): Whether the repository should be private (True) or public (False).

    Returns:
        dict: A status message indicating success or the error encountered.
    """
    try:
        repo = _get_repo(name)
        repo.edit(name=new_name, description=new_discription, private=private)
        return {"status": "success"}
    except GithubException as e:
        return {"status": "error", "message": str(e)}
@mcp.tool()
def delete_repo(name:str):
    """

    :param name: name of the repository
    :return: needed to delete repository
    """
    try:
        g.get_user().get_repo(name).delete()
        return {"status":"success"}
    except GithubException as e :
        return  {"status": "error", "message": str(e)}


@mcp.tool()
def repo_Info(name: str):
    """
    Get a summary of information about a repository, including topics, star
    count, open/closed issues, and the files in its root directory.

    Parameters:
        name (str): The repository name to inspect.

    Returns:
        dict: A dictionary containing the repo's name, topics, stargazer count,
        open issues, closed issues, and root-level files. Returns an error
        message dict if the request fails.
    """
    try:
        repo = _get_repo(name)
        try:
            topic = repo.get_topics()
        except GithubException:
            topic = []
        starts = repo.stargazers_count
        open_issues = [{"number": i.number, "title": i.title} for i in repo.get_issues(state="open")]
        closed_issues = [{"number": i.number, "title": i.title} for i in repo.get_issues(state="closed")]
        contents = repo.get_contents("")
        files = []
        while contents:
            file = contents.pop(0)
            if file.type == "dir":
                contents.extend(repo.get_contents(file.path))
            else:
                files.append(file.path)

        return {
            "name": repo.name,
            "topics": topic,
            "stargazers_count": starts,
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "files": files
        }
    except GithubException as e:
        return {"status": "error", "message": str(e)}


# ============ FILES ============
@mcp.tool()
def get_file_content(name: str, file: str, branch: str):
    """
    Retrieve the contents of a file from a specific branch.

    Parameters:
        name (str): The repository name containing the file.
        file (str): The file path whose contents will be fetched.
        branch (str): The branch name to read the file from.

    Returns:
        str | dict: The file's decoded text content, or an error message dict
        if the file or branch is not found.
    """
    try:
        repo = _get_repo(name)
        return base64.b64decode(repo.get_contents(file, ref=branch).content).decode()
    except GithubException as e:
        return {"status": "error", "message": str(e)}


def _get_file(repo: Repository, file: str, branch: str) -> ContentFile:
    """Internal helper - returns a ContentFile object, not exposed as an MCP tool."""
    return repo.get_contents(file, ref=branch)


@mcp.tool()
def create_file(name: str, file: str, branch: str, txt: str, commit: str):
    """
    Create a new file in the repository on a given branch.

    Parameters:
        name (str): The repository to create the file in.
        file (str): The path (including filename) where the new file will be created.
        branch (str): The branch to commit the new file to.
        txt (str): The text content to write into the file.
        commit (str): The commit message describing this change.

    Returns:
        dict: A status message indicating success (with commit info) or the error encountered.
    """
    try:
        repo = _get_repo(name)
        result = repo.create_file(path=file, message=commit, content=txt, branch=branch)
        return {"status": "success", "commit": result["commit"].sha}
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def Update_file(name: str, file: str, branch: str, txt: str, commit: str, rep: bool):
    """
    Update the contents of an existing file in the repository.

    Parameters:
        name (str): The repository containing the file . the name is after the /
        file (str): The path of the file to update.
        branch (str): The branch to commit the update to.
        txt (str): The new text content to add or replace.
        commit (str): The commit message describing this change.
        rep (bool) : if True, replace the file's content entirely with txt;
                      if False, append txt to the existing content.

    Returns:
        dict: A status message indicating success (with commit info) or the error encountered.
    """
    try:
        repo = _get_repo(name)
        f = _get_file(repo, file, branch)
        if rep:
            new_content = txt
        else:
            current = base64.b64decode(f.content).decode()
            new_content = f"{current}\n{txt}"

        result = repo.update_file(path=f.path, message=commit, content=new_content, sha=f.sha, branch=branch)
        return {"status": "success", "commit": result["commit"].sha}
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def delete_file(name: str, file: str, branch: str, commit: str):
    """
    Delete a file from the repository.

    Parameters:
        name (str): The repository containing the file.
        file (str): The path of the file to delete.
        branch (str): The branch to commit the deletion to.
        commit (str): The commit message describing this change.

    Returns:
        dict: A status message indicating success or the error encountered.
    """
    try:
        repo = _get_repo(name)
        f = _get_file(repo, file, branch)
        repo.delete_file(path=f.path, message=commit, sha=f.sha, branch=branch)
        return {"status": "success"}
    except GithubException as e:
        return {"status": "error", "message": str(e)}


# ============ BRANCH ============
@mcp.tool()
def create_branch(name: str, source_b: str, new_b: str):
    """
    Create a new branch based on the latest commit of an existing branch.

    Parameters:
        name (str): The repository to create the branch in.
        source_b (str): The existing branch to branch off from (its commit sha is used as the starting point).
        new_b (str): The name to give the new branch.

    Returns:
        dict: A status message indicating success or the error encountered.
    """
    try:
        repo = _get_repo(name)
        br = _get_branch(repo, source_b)

        source = br.commit.sha
        repo.create_git_ref(
            ref=f"refs/heads/{new_b}",
            sha=source
        )
        return {"status": "success"}
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def list_branches(name: str):
    """
    List all branches in a repository.

    Parameters:
        name (str): The repository name to list branches for.

    Returns:
        list[str] | dict: A list of branch names, or an error message dict if the request fails.
    """
    try:
        repo = _get_repo(name)
        return [b.name for b in repo.get_branches()]
    except GithubException as e:
        return {"status": "error", "message": str(e)}


def _get_branch(repo: Repository, name: str) -> Branch:
    """Internal helper - returns a Branch object, not exposed as an MCP tool."""
    return repo.get_branch(branch=name)


# ============ PULL REQUESTS ============
@mcp.tool()
def create_Pull_Request(name: str, base: str, head: str, title: str, body: str):
    """
    Create a new pull request.

    Parameters:
        name (str): The repository to create the pull request in.
        base (str): The name of the branch you want the changes pulled into (e.g. "main").
        head (str): The name of the branch where your changes are implemented (e.g. "feature-branch").
        title (str): The title of the pull request.
        body (str): The description/body text of the pull request.

    Returns:
        dict: A status message indicating success (with PR number) or the error encountered.
    """
    try:
        repo = _get_repo(name)
        pr = repo.create_pull(base=base, head=head, title=title, body=body)
        return {"status": "success", "pull_request_number": pr.number}
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_all_Pl(name: str, base: str):
    """
    Get all open pull requests targeting a specific base branch.

    Parameters:
        name (str): The repository to search.
        base (str): The base branch to filter pull requests by (e.g. "main").

    Returns:
        list[dict] | dict: A list of open pull requests with number, title and head branch,
        or an error message dict if the request fails.
    """
    try:
        repo = _get_repo(name)
        return [
            {"number": pr.number, "title": pr.title, "head": pr.head.ref}
            for pr in repo.get_pulls(state='open', sort='created', base=base)
        ]
    except GithubException as e:
        return {"status": "error", "message": str(e)}


# ============ ISSUES ============
@mcp.tool()
def get_labels(name: str):
    """
    List all labels available in a repository (for use when creating issues).

    Parameters:
        name (str): The repository name to list labels for.

    Returns:
        list[str] | dict: A list of label names, or an error message dict.
    """
    try:
        repo = _get_repo(name)
        return [label.name for label in repo.get_labels()]
    except GithubException as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def create_issues(name: str, title: str, body: str, label: list[str]):
    """
    Create a new issue in the repository.

    Parameters:
        name (str): The repository to create the issue in.
        title (str): The title of the issue.
        body (str): The description/body text of the issue.
        label(list[str]) : you will get the list from get_labels and put what the user need

    Returns:
        dict: A status message indicating success (with issue number) or the error encountered.
    """
    try:
        repo = _get_repo(name)
        issue = repo.create_issue(title=title, body=body, labels=label)
        return {"status": "success", "issue_number": issue.number}
    except GithubException as e:
        return {"status": "error", "message": str(e)}

if __name__=="__main__":
     mcp.run(transport="stdio")
# repo = g.get_user().get_repo(name="CinemaFilmProj")
# print(repo.get_contents(""))