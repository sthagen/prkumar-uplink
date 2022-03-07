# Standard library imports
import collections

# Local imports.
import uplink

# Constants
BASE_URL = "https://api.github.com/"

# Schemas
User = collections.namedtuple("User", "id name")
Repo = collections.namedtuple("Repo", "owner name")

# Converters


@uplink.loads(User)
def user_reader(cls, response):
    return cls(**response.json())


@uplink.loads.from_json(Repo)
def repo_json_reader(cls, json):
    return cls(**json)


@uplink.dumps.to_json(Repo)
def repo_json_writer(_, repo):
    return {"owner": repo.owner, "name": repo.name}


# Service


class GitHub(uplink.Consumer):
    @uplink.returns(User)
    @uplink.get("/users/{user}")
    def get_user(self, user):
        pass

    @uplink.returns.from_json(type=Repo)
    @uplink.get("/users/{user}/repos/{repo}")
    def get_repo(self, user, repo):
        pass

    @uplink.returns.from_json(key="data")
    @uplink.returns.schema(uplink.types.List[Repo])
    @uplink.get("/users/{user}/repos")
    def get_repos(self, user):
        pass

    @uplink.returns.from_json(key=("data", 0, "size"))
    @uplink.get("/users/{user}/repos")
    def get_first_repo_size(self, user):
        pass

    @uplink.returns.from_json(key=("data", 0, "stars"), type=int)
    @uplink.get("/users/{user}/repos")
    def get_first_repo_stars(self, user):
        pass

    @uplink.json
    @uplink.post("/users/{user}/repos", args={"repo": uplink.Body(Repo)})
    def create_repo(self, user, repo):
        pass

    @uplink.returns(object)
    @uplink.get("/users")
    def list_users(self):
        pass


@uplink.returns.json
class GitHubV2(uplink.Consumer):
    @uplink.get("/users/{user}/repos/{repo}")
    def get_repo(self, user, repo):
        pass


# Tests
def test_returns_json_on_class(mock_client, mock_response):
    # Setup
    mock_response.with_json({"owner": "prkumar", "name": "uplink"})
    mock_client.with_response(mock_response)
    github = GitHubV2(
        base_url=BASE_URL, client=mock_client, converters=repo_json_reader
    )

    # Run
    repo = github.get_repo("prkumar", "uplink")

    # Verify
    assert repo == {"owner": "prkumar", "name": "uplink"}


def test_returns_response_when_type_has_no_converter(
    mock_client, mock_response
):
    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_response(mock_response)
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=user_reader
    )

    # Run
    response = github.list_users()

    # Verify
    assert response == mock_response


def test_returns_with_type(mock_client, mock_response):
    # Setup
    mock_response.with_json({"id": 123, "name": "prkumar"})
    mock_client.with_response(mock_response)
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=user_reader
    )

    # Run
    user = github.get_user("prkumar")

    # Verify
    assert User(id=123, name="prkumar") == user


def test_returns_json_with_type(mock_client, mock_response):
    # Setup
    mock_response.with_json({"owner": "prkumar", "name": "uplink"})
    mock_client.with_response(mock_response)
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=repo_json_reader
    )

    # Run
    repo = github.get_repo("prkumar", "uplink")

    # Verify
    assert Repo(owner="prkumar", name="uplink") == repo


def test_returns_json_with_list(mock_client, mock_response):
    # Setup
    mock_response.with_json(
        {
            "data": [
                {"owner": "prkumar", "name": "uplink"},
                {"owner": "prkumar", "name": "uplink-protobuf"},
            ],
            "errors": [],
        }
    )
    mock_client.with_response(mock_response)
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=repo_json_reader
    )

    # Run
    repo = github.get_repos("prkumar")

    # Verify
    assert [
        Repo(owner="prkumar", name="uplink"),
        Repo(owner="prkumar", name="uplink-protobuf"),
    ] == repo


def test_returns_json_by_key(mock_client, mock_response):
    # Setup
    mock_response.with_json(
        {
            "data": [
                {"owner": "prkumar", "name": "uplink", "size": 300},
                {"owner": "prkumar", "name": "uplink-protobuf", "size": 400},
            ],
            "errors": [],
        }
    )
    mock_client.with_response(mock_response)
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    size = github.get_first_repo_size("prkumar")

    # Verify
    assert size == 300


def test_returns_json_with_key_and_type(mock_client, mock_response):
    # Setup
    mock_response.with_json(
        {
            "data": [
                {"owner": "prkumar", "name": "uplink", "stars": "300"},
                {"owner": "prkumar", "name": "uplink-protobuf", "stars": "400"},
            ],
            "errors": [],
        }
    )
    mock_client.with_response(mock_response)
    github = GitHub(base_url=BASE_URL, client=mock_client)

    # Run
    stars = github.get_first_repo_stars("prkumar")

    # Verify
    assert stars == 300


def test_post_json(mock_client):
    # Setup
    github = GitHub(
        base_url=BASE_URL, client=mock_client, converters=repo_json_writer
    )
    github.create_repo("prkumar", Repo(owner="prkumar", name="uplink"))
    request = mock_client.history[0]
    assert request.json == {"owner": "prkumar", "name": "uplink"}
