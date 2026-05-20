"""Controller — autenticazione (login / logout)."""

from dash import Output, Input, State, no_update
from models.model import model


def register_callbacks(app):

    @app.callback(
        Output('session', 'data'),
        Output('login-error', 'children'),
        Input('btn-login', 'n_clicks'),
        State('input-user', 'value'),
        State('input-pass', 'value'),
        prevent_initial_call=True,
    )
    def do_login(n, email, password):
        if not n:
            return no_update, no_update
        user = model.authenticate(email or '', password or '')
        if user:
            return user, ''
        return no_update, 'Credenziali non valide.'

    @app.callback(
        Output('session', 'clear_data'),
        Input('btn-logout', 'n_clicks'),
        prevent_initial_call=True,
    )
    def do_logout(n):
        if not n:
            return no_update
        return True
