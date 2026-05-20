"""Controller — callbacks del paziente."""

from dash import Output, Input, State, ctx, html, no_update
import plotly.express as px
from models.model import model

SHOW = {'display': 'block'}
HIDE = {'display': 'none'}


def _health_figure(model, patient_id, metric):
    """Crea la figura Plotly per una metrica di salute."""
    tpl = 'plotly_white'
    if metric == 'calories':
        df = model.get_daily_calories(patient_id)
        return px.line(df, x='date', y='calories', title='Calorie giornaliere',
                       labels={'date': 'Data', 'calories': 'kcal'}, template=tpl)
    if metric == 'steps':
        df = model.get_daily_steps(patient_id)
        return px.line(df, x='date', y='steps', title='Passi giornalieri',
                       labels={'date': 'Data', 'steps': 'Passi'}, template=tpl)
    if metric == 'exercise':
        df = model.get_exercise(patient_id)
        return px.bar(df, x='date', y='duration', title='Durata esercizio',
                      labels={'date': 'Data', 'duration': 'Minuti'}, template=tpl)
    if metric == 'sleep':
        df = model.get_sleep(patient_id)
        return px.box(df, y='efficiency', title='Efficienza sonno',
                      labels={'efficiency': 'Efficienza (%)'}, template=tpl)
    return px.line(title='Seleziona una metrica')


def _render_chat(messages, me):
    """Genera la lista HTML dei messaggi."""
    if not messages:
        return html.P('Nessun messaggio.', style={'color': '#888'})
    children = []
    for m in messages:
        is_mine = m['from_user'] == me
        align = 'right' if is_mine else 'left'
        bg = '#DCF8C6' if is_mine else '#FFFFFF'
        label = 'Tu' if is_mine else m['from_user']
        children.append(html.Div([
            html.Small(f'{label} — {m["timestamp"]}',
                       style={'color': '#888'}),
            html.P(m['text'], style={'margin': '2px 0'}),
        ], style={'textAlign': align, 'backgroundColor': bg,
                  'padding': '6px 10px', 'borderRadius': '8px',
                  'marginBottom': '6px', 'maxWidth': '70%',
                  'marginLeft': 'auto' if is_mine else '0',
                  'marginRight': '0' if is_mine else 'auto'}))
    return html.Div(children)


def register_callbacks(app):

    # ---- switch tab ---------------------------------------------------------
    @app.callback(
        Output('p-tab-health', 'style'),
        Output('p-tab-doctor', 'style'),
        Output('p-tab-messages', 'style'),
        Input('p-main-tabs', 'value'),
    )
    def switch_tab(tab):
        return (SHOW if tab == 'health' else HIDE,
                SHOW if tab == 'doctor' else HIDE,
                SHOW if tab == 'messages' else HIDE)

    # ---- grafico salute -----------------------------------------------------
    # 
    # #da revisionare perchè non è il paziente a scegliersi il medico
    
    @app.callback(
        Output('p-health-graph', 'figure'),
        Input('p-health-metric', 'value'),
        State('session', 'data'),
    )
    def update_health(metric, session):
        if not session or not metric:
            return no_update
        return _health_figure(model, session['username'], metric)


    # ---- messaggi -----------------------------------------------------------
    @app.callback(
        Output('p-conv-select', 'options'),
        Output('p-chat-area', 'children'),
        Output('p-msg-input', 'value'),
        Output('p-send-status', 'children'),
        Input('p-btn-send', 'n_clicks'),
        Input('p-conv-select', 'value'),
        Input('p-refresh', 'n_intervals'),
        State('p-msg-input', 'value'),
        State('session', 'data'),
    )
    def update_messages(send_n, conv, _, msg_text, session):
        if not session:
            return [], '', no_update, ''
        trigger = ctx.triggered_id
        status = ''

        # Invia messaggio
        if trigger == 'p-btn-send' and conv and msg_text:
            model.send_message(session['username'], conv, msg_text)
            status = 'Inviato.'

        # Opzioni inbox: medico accettato + conversazioni esistenti
        partners = set()
        doc = model.get_my_doctor(session['username'])
        if doc and doc['status'] == 'accepted':
            partners.add(doc['doctor_id'])
        for c in model.get_inbox(session['username']):
            partners.add(c['username'])
        options = []
        for p in sorted(partners):
            u = model.get_user(p)
            options.append({'label': u['display_name'] if u else p, 'value': p})

        # Chat
        if conv:
            msgs = model.get_conversation(session['username'], conv)
            chat = _render_chat(msgs, session['username'])
        else:
            chat = html.P('Seleziona una conversazione.', style={'color': '#888'})

        new_input = '' if trigger == 'p-btn-send' else no_update
        return options, chat, new_input, status
