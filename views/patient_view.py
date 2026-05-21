from dash import html, dcc

HEADER = {'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
          'padding': '10px 20px', 'backgroundColor': '#E8F4FD', 'fontFamily': 'sans-serif'}
CONTAINER = {'maxWidth': '960px', 'margin': 'auto', 'padding': '15px',
             'fontFamily': 'sans-serif'}
HIDE = {'display': 'none'}
CHAT_BOX = {'height': '300px', 'overflowY': 'auto', 'border': '1px solid #ddd',
            'padding': '10px', 'marginTop': '10px', 'marginBottom': '10px',
            'backgroundColor': '#f9f9f9', 'borderRadius': '4px'}


def patient_layout(session):
    uid = session['email']
    name = session['display_name']

    return html.Div([
        # Header
        html.Div([
            html.H3('PMData Healthcare', style={'margin': '0'}),
            html.Div([
                html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Button('Logout', id='btn-logout', n_clicks=0,
                            style={'padding': '6px 16px'}),
            ]),
        ], style=HEADER),

        # Main
        html.Div([
            dcc.Tabs(id='p-main-tabs', value='health', children=[
                dcc.Tab(label='Stato Salute', value='health'),
                dcc.Tab(label='Medico', value='doctor'),
                dcc.Tab(label='Messaggi', value='messages'),
            ]),

            # ---- TAB Stato Salute ----
            html.Div(id='p-tab-health', children=[
                dcc.Dropdown(id='p-health-metric',
                             options=[{'label': 'Calorie', 'value': 'calories'},
                                      {'label': 'Passi', 'value': 'steps'},
                                      {'label': 'Esercizio', 'value': 'exercise'},
                                      {'label': 'Sonno', 'value': 'sleep'}],
                             value='calories', style={'marginTop': '10px'}),
                dcc.Graph(id='p-health-graph'),
            ]),

            # ---- TAB Medico ----
            html.Div(id='p-tab-doctor', style=HIDE, children=[
                html.H4('Il tuo medico'),
                # Nessun medico
                html.Div(id='p-doc-none', children=[
                    html.P('Non hai un medico assegnato. Seleziona un medico:'),
                    dcc.Dropdown(id='p-doctor-select', placeholder='Seleziona medico...',
                                 style={'marginBottom': '8px'}),
                    html.Button('Richiedi', id='p-btn-request', n_clicks=0,
                                style={'padding': '6px 20px'}),
                ]),
                # In attesa
                html.Div(id='p-doc-pending', style=HIDE, children=[
                    html.P(id='p-doc-pending-text'),
                    html.Button('Annulla richiesta', id='p-btn-cancel', n_clicks=0,
                                style={'padding': '6px 20px'}),
                ]),
                # Accettato
                html.Div(id='p-doc-accepted', style=HIDE, children=[
                    html.P(id='p-doc-accepted-text'),
                    html.Button('Rimuovi medico', id='p-btn-remove', n_clicks=0,
                                style={'padding': '6px 20px', 'backgroundColor': '#ffcccc'}),
                ]),
                html.Div(id='p-doc-status', style={'marginTop': '10px', 'color': 'green'}),
            ]),

            # ---- TAB Messaggi ----
            html.Div(id='p-tab-messages', style=HIDE, children=[
                html.H4('Messaggi'),
                dcc.Dropdown(id='p-conv-select', placeholder='Seleziona conversazione...'),
                html.Div(id='p-chat-area', style=CHAT_BOX),
                html.Div([
                    dcc.Input(id='p-msg-input', type='text',
                              placeholder='Scrivi messaggio...',
                              style={'width': '80%', 'padding': '8px',
                                     'marginRight': '5px'}),
                    html.Button('Invia', id='p-btn-send', n_clicks=0,
                                style={'padding': '8px 16px'}),
                ]),
                html.Div(id='p-send-status', style={'color': 'green', 'marginTop': '5px'}),
            ]),

            # Refresh interval
            dcc.Interval(id='p-refresh', interval=5000),
        ], style=CONTAINER),
    ])
