"""Controller — callbacks del segretario."""

from dash import Output, Input, State
from models.model import model
from views.secretary_view import patients_tab, medics_tab, inserting_tab


def register_callbacks(app):

    #rendering delle tab principali
    @app.callback(
        Output('tab-content', 'children'),
        Input('p-main-tabs', 'value'),
    )
    def render_tab(tab):
        if tab == 'patients':
            return patients_tab()
        if tab == 'medics':
            return medics_tab()
        return inserting_tab()

    #mostra il form di inserimento paziente o medico a seconda della tab secondaria selezionata
    @app.callback(
        Output('insert-patient-form', 'style'),
        Output('insert-medic-form', 'style'),
        Input('insert-sub-tabs', 'value'),
    )
    def toggle_insert_form(sub):
        show = {'display': 'block'}
        hide = {'display': 'none'}
        if sub == 'new-patient':
            return show, hide
        return hide, show

    #salvataggio paziente
    @app.callback(
        Output('msg-patient', 'children'),
        Output('msg-patient', 'style'),
        Input('btn-save-patient', 'n_clicks'),
        State('inp-p-nome', 'value'),
        State('inp-p-cognome', 'value'),
        State('inp-p-cf', 'value'),
        State('inp-p-email', 'value'),
        State('inp-p-medico', 'value'),
        State('inp-p-password', 'value'),
        State('inp-p-flags', 'value'),
        prevent_initial_call=True,
    )
    def save_patient(n, nome, cognome, cf, email, medico, password, flags):
        if not n:
            return '', {}
        missing = [f for f, v in [('Nome', nome), ('Cognome', cognome),
                                   ('Cod. Fiscale', cf), ('Email', email),
                                   ('Medico', medico), ('Password', password)] if not v]
        if missing:
            return (f'⚠️ Campi obbligatori mancanti: {", ".join(missing)}.',
                    {'color': '#dc2626', 'fontSize': '13px'})
        flags = flags or []
        try:
            model.crea_paziente(
                nome=nome, cognome=cognome, email=email, cf=cf,
                medico_id=medico, password=password,
                fumatore='fumatore' in flags,
                ex_fumatore='ex_fumatore' in flags,
                obesita='obesita' in flags,
                problemi_alcol='problemi_alcol' in flags,
                problemi_stupefacenti='problemi_stupefacenti' in flags,
            )
            return (f'✅ Paziente {nome} {cognome} salvato con successo.',
                    {'color': '#16a34a', 'fontSize': '13px'})
        except Exception as e:
            return (f'❌ Errore: {str(e)}',
                    {'color': '#dc2626', 'fontSize': '13px'})


    #salvataggio medico
    @app.callback(
        Output('msg-medic', 'children'),
        Output('msg-medic', 'style'),
        Input('btn-save-medic', 'n_clicks'),
        State('inp-m-nome', 'value'),
        State('inp-m-cognome', 'value'),
        State('inp-m-email', 'value'),
        State('inp-m-matricola', 'value'),
        State('inp-m-password', 'value'),
        prevent_initial_call=True,
    )
    def save_medic(n, nome, cognome, email, matricola, password):
        if not n:
            return '', {}
        missing = [f for f, v in [('Nome', nome), ('Cognome', cognome),
                                   ('Email', email), ('Matricola', matricola), ('Password', password)] if not v]
        if missing:
            return (f'⚠️ Campi obbligatori mancanti: {", ".join(missing)}.',
                    {'color': '#dc2626', 'fontSize': '13px'})
        try:
            model.crea_medico(nome=nome, cognome=cognome,
                              email=email, matricola=matricola, password=password)
            return (f'✅ Medico {nome} {cognome} salvato con successo.',
                    {'color': '#16a34a', 'fontSize': '13px'})
        except Exception as e:
            return (f'❌ Errore: {str(e)}',
                    {'color': '#dc2626', 'fontSize': '13px'})