"""View — pagina di login."""

from dash import html, dcc

STYLE_CARD = {
    'maxWidth': '400px', 'margin': '80px auto', 'padding': '30px',
    'border': '1px solid #e5e7eb', 'borderRadius': '8px',
    'backgroundColor': '#ffffff',
    'boxShadow': '0 10px 30px rgba(0, 0, 0, 0.08)', 'fontFamily': '"Inter", "Segoe UI", sans-serif',
    'color': '#1f2937', 'display': 'flex', 'flexDirection': 'column', 'gap': '9px',
}


def login_layout():
    return html.Div([
        html.H2('Diabetes Control Center', style={'textAlign': 'center'}),
        html.P('Inserisci credenziali per accedere', style={'textAlign': 'center', 'color': '#666'}),
        html.Hr(),

        html.Label('Email', style={'fontWeight': 'bold'}),
        dcc.Input(id='input-user', type='text', placeholder='email',
                  style={'width': '100%', 'marginBottom': '12px', 'padding': '8px'}),

        html.Label('Password', style={'fontWeight': 'bold'}),
        dcc.Input(id='input-pass', type='password', placeholder='password',
                  style={'width': '100%', 'marginBottom': '16px', 'padding': '8px'}),

        html.Button('Login', id='btn-login', n_clicks=0,
                    style={'width': '100%', 'padding': '10px', 'fontSize': '16px',
                           'backgroundColor': "#2E30A8", 'color': 'white',
                           'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'
                           ''}),

        html.Div(id='login-error', style={'color': 'red', 'marginTop': '10px',
                                           'textAlign': 'center'}),
    ], style=STYLE_CARD)
