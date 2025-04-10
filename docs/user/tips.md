# Tips, Tricks, & Extras

Here are a few ways to simplify consumer definitions.

## Decorating All Request Methods in a Class

To apply a decorator of this library across all methods of a
`uplink.Consumer` subclass, you can simply decorate the class rather
than each method individually:

``` python
@uplink.timeout(60)
class GitHub(uplink.Consumer):
    @uplink.get("/repositories")
    def get_repos(self):
        """Dump every public repository."""

    @uplink.get("/organizations")
    def get_organizations(self):
        """List all organizations."""
```

Hence, the consumer defined above is equivalent to the following,
slightly more verbose definition:

``` python
class GitHub(uplink.Consumer):
    @uplink.timeout(60)
    @uplink.get("/repositories")
    def get_repos(self):
        """Dump every public repository."""

    @uplink.timeout(60)
    @uplink.get("/organizations")
    def get_organizations(self):
        """List all organizations."""
```

## Adopting the Argument's Name

Several function argument annotations accept a `name` parameter on
construction. For instance, the `uplink.Path` annotation uses the
`name` parameter to associate the function argument to a URI path
parameter:

``` python
class GitHub(uplink.Consumer):
    @uplink.get("users/{username}")
    def get_user(self, username: uplink.Path("username")): pass
```

For such annotations, you can omit the `name` parameter to have the
annotation adopt the name of its corresponding method argument.

For instance, from the previous example, we can omit naming the
`uplink.Path` annotation since the corresponding argument's name,
`username`, matches the intended URI path parameter.

``` python
class GitHub(uplink.Consumer):
    @uplink.get("users/{username}")
    def get_user(self, username: uplink.Path): pass
```

Some annotations that support this behavior include: `uplink.Path`,
`uplink.Field`, `uplink.Part` `uplink.Header`, and `uplink.Query`.

## Annotating Your Arguments

There are several ways to annotate arguments. Most examples in this
documentation use function annotations. Alternatively, you can use the
method annotation `uplink.args` or the optional `args` parameter of the
HTTP method decorators (e.g., `uplink.get`).

### Using `uplink.args`

The method annotation `uplink.args` arranges annotations in the same
order as their corresponding function arguments (again, ignore `self`):

``` python
class GitHub(uplink.Consumer):
    @uplink.args(uplink.Url, uplink.Path)
    @uplink.get
    def get_commit(self, commits_url, sha): pass
```

### The `args` argument

The HTTP method decorators (e.g., `uplink.get`) support an optional
positional argument `args`, which accepts a list of annotations,
arranged in the same order as their corresponding function arguments,

``` python
class GitHub(uplink.Consumer):
    @uplink.get(args=(uplink.Url, uplink.Path))
    def get_commit(self, commits_url, sha): pass
```

or a mapping of argument names to annotations:

``` python
class GitHub(uplink.Consumer):
    @uplink.get(args={"commits_url": uplink.Url, "sha": uplink.Path})
    def get_commit(self, commits_url, sha): pass
```

### Function Annotations

You can use these classes as function annotation (`3107`):

``` python
class GitHub(uplink.Consumer):
    @uplink.get
    def get_commit(self, commit_url: uplink.Url, sha: uplink.Path):
        pass
```

Annotations receiving a `str` or a `type` can be also initialized by
using [generic types
emulation](https://docs.python.org/3/reference/datamodel.html#emulating-generic-types):

``` python
class GitHub(uplink.Consumer):
    @uplink.get("user")
    def get_user(self, authorization: Header["Authorization"]):
        """Get an authenticated user."""
```

## Annotating `__init__` Arguments

Function annotations like `Query` and `Header` can be used with
constructor arguments of a `uplink.Consumer` subclass. When a new
consumer instance is created, the value of these arguments are applied
to all requests made through that instance.

For example, the following consumer accepts the API access token as the
constructor argument `access_token`:

``` python
class GitHub(uplink.Consumer):

    def __init__(self, access_token: uplink.Query):
        ...

    @uplink.post("/user")
    def update_user(self, **info: Body):
        """Update the authenticated user"""
```

Now, all requests made from an instance of this consumer class will be
authenticated with the access token passed in at initialization:

``` python
github = GitHub("my-github-access-token")

# This request will include the `access_token` query parameter set from
# the constructor argument.
github.update_user(bio="Beam me up, Scotty!")
```

## The Consumer's `_inject` Method

As an alternative to `annotating constructor arguments` and `session`,
you can achieve a similar behavior with more control by using the
`Consumer._inject` method. With this method, you can calculate request
properties within plain old python methods.

``` python
class TodoApp(uplink.Consumer):

    def __init__(self, base_url, username, password):
       super(TodoApp, self).__init__(base_url=base_url)

        # Create an access token
        api_key = create_api_key(username, password)

        # Inject it.
        self._inject(uplink.Query("api_key").with_value(api_key))
```

Similar to the annotation style, request properties added with
`uplink.Consumer._inject` method are applied to all requests made
through the consumer instance.

## Extend Consumer Methods to Reduce Boilerplate

v0.9.0

**Consumer methods** are methods decorated with Uplink's HTTP method
decorators, such as `@get <uplink.get>` or `@post <uplink.post>` (see
`here <making-a-request>` for more background).

Consumer methods can be used as decorators to minimize duplication
across similar consumer method definitions.

For example, you can define consumer method templates like so:

``` python
from uplink import Consumer, get, json, returns

@returns.json
@json
@get
def get_json():
    """Template for GET request that consumes and produces JSON."""

class GitHub(Consumer):
    @get_json("/users/{user}")
    def get_user(self, user):
         """Fetches a specific GitHub user."""
```

Further, you can use this technique to remove duplication across
definitions of similar consumer methods, whether or not the methods are
defined in the same class:

``` python
from uplink import Consumer, get, params, timeout

class GitHub(Consumer):
    @timeout(10)
    @get("/users/{user}/repos")
    def get_user_repos(self, user):
        """Retrieves the repos that the user owns."""

    # Extends the above method to define a variant:
    @params(type="member")
    @get_user_repos
    def get_repos_for_collaborator(self, user):
        """
        Retrieves the repos for which the given user is
        a collaborator.
        """

class EnhancedGitHub(Github):
    # Updates the return type of an inherited method.
    @GitHub.get_user_repos
    def get_user_repos(self, user) -> List[Repo]:
        """Retrieves the repos that the user owns."""
```
