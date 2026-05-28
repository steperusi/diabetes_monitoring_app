"""View del segretario"""

from dash import html, dcc
from models.model import Paziente, Medico
from pony.orm import db_session, select

# ── Stili base ──────────────────────────────────────────────────────────────
HEADER = {
    'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
    'padding': '16px 32px',
    'background': 'linear-gradient(90deg, #8284D9 0%, #3C3CEC 100%)',
    'color': 'white', 'fontFamily': '"Inter", "Segoe UI", sans-serif',
    'fontSize': '16px', 'fontWeight': '600',
    'borderRadius': '18px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.12)',
    'minHeight': '70px', 'letterSpacing': '0.3px',
}
CONTAINER = {
    'maxWidth': '960px', 'margin': '30px auto', 'padding': '24px',
    'fontFamily': '"Inter", "Segoe UI", sans-serif', 'color': '#1f2937',
}
CARD = {
    'background': '#ffffff', 'borderRadius': '16px',
    'padding': '24px', 'marginTop': '20px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.07)',
    'border': '1px solid #e5e7eb',
}
TABLE_HEADER = {
    'background': 'linear-gradient(90deg, #4748AC 0%, #5E60CE 100%)',
    'color': 'white', 'padding': '10px 16px', 'fontWeight': '600',
    'fontSize': '13px', 'letterSpacing': '0.5px', 'overflow': 'auto',
}
TABLE_ROW_EVEN = {
    'background': '#f9fafb', 'padding': '10px 16px',
    'fontSize': '14px', 'color': '#374151',
}
TABLE_ROW_ODD = {
    'background': '#ffffff', 'padding': '10px 16px',
    'fontSize': '14px', 'color': '#374151',
}
INPUT_STYLE = {
    'width': '100%', 'padding': '10px 14px',
    'border': '1px solid #d1d5db', 'borderRadius': '10px',
    'fontSize': '14px', 'color': '#1f2937',
    'outline': 'none', 'boxSizing': 'border-box',
    'marginBottom': '14px',
}
LABEL_STYLE = {
    'fontWeight': '600', 'fontSize': '13px',
    'color': '#6b7280', 'marginBottom': '4px',
    'display': 'block', 'letterSpacing': '0.4px',
}
BTN_PRIMARY = {
    'background': 'linear-gradient(90deg, #4748AC 0%, #5E60CE 100%)',
    'color': 'white', 'border': 'none', 'borderRadius': '10px',
    'padding': '10px 28px', 'fontWeight': '600', 'fontSize': '14px',
    'cursor': 'pointer', 'marginTop': '8px',
}
SECTION_TITLE = {
    'fontSize': '18px', 'fontWeight': '700',
    'color': '#4748AC', 'marginBottom': '4px',
}
SECTION_SUBTITLE = {
    'fontSize': '13px', 'color': '#9ca3af', 'marginBottom': '16px',
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _table_row(cells: list, style: dict) -> html.Div:
    return html.Div(
        [html.Div(c, style={'flex': '1', 'minWidth': '0', 'whiteSpace': 'nowrap'}) for c in cells],
        style={**style, 'display': 'flex', 'gap': '0',
               'borderBottom': '1px solid #f3f4f6', 'width': 'max-content',
               'minWidth': '100%'},
    )


def _field(label: str, input_id: str, placeholder: str = '',
           type_: str = 'text', options: list = None) -> html.Div:
    if options:
        ctrl = dcc.Dropdown(
            id=input_id,
            options=[{'label': o['label'], 'value': o['value']} for o in options],
            placeholder=placeholder,
            style={**INPUT_STYLE, 'padding': '2px 4px'},
            clearable=True,
        )
    else:
        ctrl = dcc.Input(
            id=input_id, type=type_, placeholder=placeholder,
            style=INPUT_STYLE, debounce=False,
        )
    return html.Div([
        html.Label(label, style=LABEL_STYLE),
        ctrl,
    ])


# ── Schede ────────────────────────────────────────────────────────────────────
@db_session
def patients_tab():
    pazienti = Paziente.select()[:]

    headers = ['Nome', 'Cognome', 'Cod. Fiscale', 'Medico Curante', 'Email']
    rows = []
    for i, p in enumerate(pazienti):
        style = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        rows.append(_table_row([
            p.utente.nome,
            p.utente.cognome,
            p.codice_fiscale,
            f"{p.medico_riferimento.utente.nome} {p.medico_riferimento.utente.cognome}",
            p.utente.email,
        ], style))

    return html.Div([
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                        'alignItems': 'flex-end', 'marginBottom': '4px'}, children=[
            html.Div([
                html.Div('Lista Pazienti', style=SECTION_TITLE),
                html.Div(f'{len(pazienti)} pazienti registrati', style=SECTION_SUBTITLE),
            ]),
            dcc.Input(placeholder='🔍  Cerca paziente…',
                      style={**INPUT_STYLE, 'width': '220px', 'marginBottom': '0'}),
        ]),
        html.Div([
            _table_row(headers, TABLE_HEADER),
            *(rows if rows else [
                html.Div('Nessun paziente registrato.',
                         style={'padding': '20px', 'color': '#9ca3af',
                                'fontSize': '14px', 'textAlign': 'center'}),
            ]),
        ], style={'borderRadius': '12px', 'overflowX': 'auto', 'minWidth': '0',
                  'border': '1px solid #e5e7eb'}),
    ], style=CARD)


@db_session
def medics_tab():
    medici = Medico.select()[:]

    headers = ['Nome', 'Cognome', 'Email', 'Matricola']
    rows = []
    for i, m in enumerate(medici):
        style = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        rows.append(_table_row([
            m.utente.nome,
            m.utente.cognome,
            m.utente.email,
            m.matricola,
        ], style))

    return html.Div([
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                        'alignItems': 'flex-end', 'marginBottom': '4px'}, children=[
            html.Div([
                html.Div('Lista Medici', style=SECTION_TITLE),
                html.Div(f'{len(medici)} medici registrati', style=SECTION_SUBTITLE),
            ]),
            dcc.Input(placeholder='🔍  Cerca medico…',
                      style={**INPUT_STYLE, 'width': '220px', 'marginBottom': '0'}),
        ]),
        html.Div([
            _table_row(headers, TABLE_HEADER),
            *(rows if rows else [
                html.Div('Nessun medico registrato.',
                         style={'padding': '20px', 'color': '#9ca3af',
                                'fontSize': '14px', 'textAlign': 'center'}),
            ]),
        ], style={'borderRadius': '12px', 'overflowX': 'auto', 'minWidth': '0',
                  'border': '1px solid #e5e7eb'}),
    ], style=CARD)


@db_session
def inserting_tab():
    medici_options = [
        {'label': f"{m.utente.nome} {m.utente.cognome}", 'value': m.utente.email}
        for m in list(Medico.select())
    ]

    return html.Div([
        html.Div('Inserimento', style=SECTION_TITLE),
        html.Div('Aggiungi un nuovo paziente o un nuovo medico al sistema.', style=SECTION_SUBTITLE),

        dcc.Tabs(id='insert-sub-tabs', value='new-patient', children=[
            dcc.Tab(label='➕  Nuovo Paziente', value='new-patient'),
            dcc.Tab(label='➕  Nuovo Medico',   value='new-medic'),
        ]),

        # ── Form Paziente ────────────────────────────────────────────────────
        html.Div(id='insert-patient-form', children=[
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                            'gap': '0 24px', 'marginTop': '20px'}, children=[
                _field('Nome *',           'inp-p-nome',    'es. Mario'),
                _field('Cognome *',        'inp-p-cognome', 'es. Rossi'),
                _field('Codice Fiscale *', 'inp-p-cf',      'es. RSSMRA80A01H501Z'),
                _field('Email *',          'inp-p-email',   'es. paziente@email.it', type_='email'),
                _field('Medico Curante *', 'inp-p-medico',  'Seleziona…', options=medici_options),
                _field('Password *',       'inp-p-password', '', type_='password'),
            ]),

            html.Div([
                html.Label('Fattori di rischio', style={**LABEL_STYLE, 'marginBottom': '10px'}),
                dcc.Checklist(
                    id='inp-p-flags',
                    options=[
                        {'label': '  Fumatore',                   'value': 'fumatore'},
                        {'label': '  Ex fumatore',                'value': 'ex_fumatore'},
                        {'label': '  Obesità',                    'value': 'obesita'},
                        {'label': '  Problemi con alcol',         'value': 'problemi_alcol'},
                        {'label': '  Dipendenza da stupefacenti', 'value': 'problemi_stupefacenti'},
                    ],
                    value=[],
                    inputStyle={'marginRight': '8px'},
                    labelStyle={'display': 'flex', 'alignItems': 'center',
                                'fontSize': '14px', 'color': '#374151', 'padding': '6px 0'},
                ),
            ], style={'marginTop': '16px', 'marginBottom': '16px',
                      'padding': '16px', 'borderRadius': '10px',
                      'border': '1px solid #e5e7eb', 'backgroundColor': '#f9fafb'}),

            html.Div(id='msg-patient', style={'marginTop': '8px', 'fontSize': '13px'}),
            html.Button('Salva Paziente', id='btn-save-patient', n_clicks=0, style=BTN_PRIMARY),
        ]),

        # ── Form Medico ──────────────────────────────────────────────────────
        html.Div(id='insert-medic-form', children=[
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                            'gap': '0 24px', 'marginTop': '20px'}, children=[
                _field('Nome *',      'inp-m-nome',      'es. Luca'),
                _field('Cognome *',   'inp-m-cognome',   'es. Bianchi'),
                _field('Email *',     'inp-m-email',     'es. medico@pmdata.it', type_='email'),
                _field('Matricola *', 'inp-m-matricola', 'es. MAT001'),
                _field('Password *',  'inp-m-password',  '', type_='password'),
            ]),
            html.Div(id='msg-medic', style={'marginTop': '8px', 'fontSize': '13px'}),
            html.Button('Salva Medico', id='btn-save-medic', n_clicks=0, style=BTN_PRIMARY),
        ]),
    ], style=CARD)


# ── Layout principale ─────────────────────────────────────────────────────────
def secretary_layout(session: dict) -> html.Div:
    name = session['display_name']

    return html.Div([
        html.Div([
            html.Img(src='/assets/full_logo.png', alt='Logo',
                    style={'height': '50px', 'borderRadius': '8px', 'marginRight': '16px'}),
            html.H3('Amministrazione', style={'margin': '0', 'color': 'white'}),
            html.Div([
                html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Button('Logout', id='btn-logout', n_clicks=0,
                            style={'padding': '6px 16px', 'borderRadius': '8px'}),
            ]),
        ], style=HEADER),

        html.Div([
            dcc.Tabs(id='p-main-tabs', value='patients', children=[
                dcc.Tab(label='Lista Pazienti', value='patients'),
                dcc.Tab(label='Lista Medici',   value='medics'),
                dcc.Tab(label='Inserimento',    value='inserting'),
            ]),
            html.Div(id='tab-content'),
        ], style=CONTAINER),
    ])
