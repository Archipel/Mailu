def test_make_user_creates_a_retrievable_user(app, make_user):
    from mailu.models import User
    make_user("alice", "example.com")
    assert User.query.get("alice@example.com") is not None
