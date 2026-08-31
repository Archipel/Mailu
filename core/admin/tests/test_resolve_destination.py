from mailu.models import User


def test_forwarding_user_resolves_to_the_local_mailbox_only(app, make_user):
    make_user(
        "fwd", "example.com",
        forward_enabled=True,
        forward_destination=["outside@gmail.com"],
        forward_keep=True,
    )
    assert User.resolve_destination("fwd", "example.com") == ["fwd@example.com"]


def test_forwarding_user_without_keep_still_resolves_locally(app, make_user):
    make_user(
        "nokeep", "example.com",
        forward_enabled=True,
        forward_destination=["outside@gmail.com"],
        forward_keep=False,
    )
    assert User.resolve_destination("nokeep", "example.com") == ["nokeep@example.com"]


def test_non_forwarding_user_is_unchanged(app, make_user):
    make_user("plain", "example.com")
    assert User.resolve_destination("plain", "example.com") == ["plain@example.com"]
