import flask


def render(user):
    return flask.render_template("default.sieve", user=user)


def test_forwarding_user_gets_a_redirect_after_the_spam_stage(app, make_user):
    user = make_user(
        "fwd", "example.com",
        forward_enabled=True,
        forward_destination=["outside@gmail.com"],
        forward_keep=False,
    )
    out = render(user)
    assert 'redirect "outside@gmail.com";' in out
    assert out.index('fileinto :create "Junk"') < out.index('redirect "outside@gmail.com"')
    assert "keep;" not in out


def test_every_destination_gets_its_own_redirect(app, make_user):
    user = make_user(
        "many", "example.com",
        forward_enabled=True,
        forward_destination=["a@x.com", "b@y.com", "c@z.com"],
        forward_keep=True,
    )
    out = render(user)
    for dest in ("a@x.com", "b@y.com", "c@z.com"):
        assert f'redirect "{dest}";' in out
    assert "keep;" in out


def test_non_forwarding_user_gets_no_redirect(app, make_user):
    user = make_user("plain", "example.com")
    assert "redirect" not in render(user)
