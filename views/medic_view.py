"""View del medico."""

from dash import html, dcc
from models.model import Paziente, Medico, Utente
from pony.orm import db_session, select

# ── Stili ─────────────────────────────────────────────────────────────────────
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
SECTION_TITLE = {
    'fontSize': '18px', 'fontWeight': '700',
    'color': '#4748AC', 'marginBottom': '4px',
}
SECTION_SUBTITLE = {
    'fontSize': '13px', 'color': '#9ca3af', 'marginBottom': '16px',
}
BADGE_SI = {
    'background': '#fee2e2', 'color': '#991b1b',
    'borderRadius': '6px', 'padding': '2px 10px',
    'fontSize': '12px', 'fontWeight': '600',
}
BADGE_NO = {
    'background': '#f0fdf4', 'color': '#166534',
    'borderRadius': '6px', 'padding': '2px 10px',
    'fontSize': '12px', 'fontWeight': '600',
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _table_row(cells: list, style: dict) -> html.Div:
    return html.Div(
        [html.Div(c, style={'flex': '1', 'minWidth': '0'}) for c in cells],
        style={**style, 'display': 'flex', 'gap': '12px',
               'borderBottom': '1px solid #f3f4f6', 'width': 'max-content',
               'minWidth': '100%'},
    )

def _badge(val: bool) -> html.Span:
    return html.Span('Sì' if val else 'No', style=BADGE_SI if val else BADGE_NO)


# ── Schede ────────────────────────────────────────────────────────────────────
@db_session
def my_patients_tab(pazienti: list) -> html.Div:
    headers = ['Nome', 'Cognome', 'Cod. Fiscale', 'Fumatore', 'Ex-fumatore',
               'Obesità', 'Alcolista', 'Stupefacenti']
    rows = []
    for i, p in enumerate(pazienti):
        style = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        rows.append(_table_row([
            p['nome'],
            p['cognome'],
            p['codice_fiscale'],
            _badge(p['fumatore']),
            _badge(p['ex-fumatore']),
            _badge(p['obesita']),
            _badge(p['problemi_alcol']),
            _badge(p['problemi_stupefacenti']),
        ], style))
    return html.Div([
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                        'alignItems': 'flex-end', 'marginBottom': '4px'}, children=[
            html.Div([
                html.Div('I tuoi Pazienti', style=SECTION_TITLE),
                html.Div(f'{len(pazienti)} pazienti assegnati', style=SECTION_SUBTITLE),
            ]),
            dcc.Input(placeholder='🔍  Cerca paziente…',
                      style={**INPUT_STYLE, 'width': '220px', 'marginBottom': '0'}),
        ]),
        html.Div([
            _table_row(headers, TABLE_HEADER),
            *(rows if rows else [
                html.Div('Nessun paziente assegnato.',
                         style={'padding': '20px', 'color': '#9ca3af',
                                'fontSize': '14px', 'textAlign': 'center'}),
            ]),
        ], style={'borderRadius': '12px', 'overflowX': 'auto', 'minWidth': '0',
                  'border': '1px solid #e5e7eb'}),
    ], style=CARD)


# ── Layout principale ─────────────────────────────────────────────────────────
def medic_layout(session: dict) -> html.Div:
    name = session['display_name']
    
    return html.Div([
        # Header
        html.Div([
            html.H3('Diabetes Control Center - Sezione Medico', style={'margin': '0'}),
            html.Div([
                html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Button('Logout', id='btn-logout', n_clicks=0,
                            style={'padding': '6px 16px', 'borderRadius': '8px'}),
            ]),
        ], style=HEADER),

        # Corpo
        html.Div([
            dcc.Tabs(id='m-main-tabs', value='patients', children=[
                dcc.Tab(label='I tuoi Pazienti', value='patients'),
            ]),
            html.Div(id='m-tab-content'),
        ], style=CONTAINER),

        # Store per passare l'email al controller senza rifare il login
        dcc.Store(id='medic-email', data=session.get('email')),
    ])