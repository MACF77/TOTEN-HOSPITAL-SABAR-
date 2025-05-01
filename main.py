from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView

class TotemApp(App):
    fila = []

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(text="[b]Bem-vindo ao Totem do Hospital Sabará[/b]", font_size='24sp',
                      size_hint=(1, 0.2), markup=True)
        layout.add_widget(title)

        self.name_input = self.create_input("Nome completo")
        layout.add_widget(self.center_widget(self.name_input))

        self.dob_input = self.create_input("Data de nascimento (DD/MM/AAAA)")
        self.dob_input.bind(text=self.format_dob)
        layout.add_widget(self.center_widget(self.dob_input))

        self.rg_input = self.create_input("Número do RG")
        layout.add_widget(self.center_widget(self.rg_input))

        self.contact_input = self.create_input("Número de contato")
        layout.add_widget(self.center_widget(self.contact_input))

        button1 = Button(text="Iniciar Autoavaliação de Sintomas", size_hint=(None, None),
                         size=(300, 50), background_color=(0.2, 0.6, 0.8, 1), color=(1,1,1,1))
        button1.bind(on_press=self.start_symptom_assessment)
        layout.add_widget(self.center_widget(button1))

        button2 = Button(text="Sair", size_hint=(None, None),
                         size=(300, 50), background_color=(1, 0.2, 0.2, 1), color=(1,1,1,1))
        button2.bind(on_press=self.exit_app)
        layout.add_widget(self.center_widget(button2))

        return layout

    def create_input(self, hint):
        return TextInput(hint_text=hint, size_hint=(None, None), size=(300, 50), multiline=False)

    def center_widget(self, widget):
        anchor = AnchorLayout(anchor_x='center')
        anchor.add_widget(widget)
        return anchor

    def format_dob(self, instance, value):
        digits = ''.join(filter(str.isdigit, value))
        formatted = ''
        if len(digits) > 0:
            formatted += digits[:2]
        if len(digits) > 2:
            formatted += '/' + digits[2:4]
        if len(digits) > 4:
            formatted += '/' + digits[4:8]
        instance.text = formatted

    def format_temperature(self, instance, value):
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) == 3:
            instance.text = digits[:2] + '.' + digits[2]

    def create_yes_no_toggle(self, label_text):
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        layout.add_widget(Label(text=f"[b]{label_text}[/b]", font_size='18sp', markup=True))
        toggle_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes_button = ToggleButton(text='Sim', group=label_text, font_size='16sp')
        no_button = ToggleButton(text='Não', group=label_text, state='down', font_size='16sp')
        toggle_layout.add_widget(yes_button)
        toggle_layout.add_widget(no_button)
        layout.add_widget(toggle_layout)
        return layout, yes_button

    def start_symptom_assessment(self, instance):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        dor_layout, self.pain_toggle = self.create_yes_no_toggle("Está com dor?")
        layout.add_widget(dor_layout)
        layout.add_widget(Label(text="Grau da dor (1 a 10):", font_size='16sp'))
        self.pain_level_input = TextInput(hint_text="Ex: 7", input_filter='int')
        layout.add_widget(self.pain_level_input)

        febre_layout, self.fever_toggle = self.create_yes_no_toggle("Está com febre?")
        layout.add_widget(febre_layout)
        layout.add_widget(Label(text="Temperatura (Celsius até 42):", font_size='16sp'))
        self.temperature_input = TextInput(hint_text="Ex: 38.5", input_filter='float')
        self.temperature_input.bind(text=self.format_temperature)
        layout.add_widget(self.temperature_input)

        nausea_layout, self.nausea_toggle = self.create_yes_no_toggle("Está com náusea?")
        layout.add_widget(nausea_layout)
        vomito_layout, self.vomiting_toggle = self.create_yes_no_toggle("Está com vômito?")
        layout.add_widget(vomito_layout)

        submit_button = Button(text="Ver resultado", size_hint=(None, None),
                               size=(300, 50), background_color=(0.2, 0.7, 0.3, 1), color=(1,1,1,1))
        submit_button.bind(on_press=self.process_assessment)
        layout.add_widget(self.center_widget(submit_button))

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        scroll.add_widget(layout)

        self.assessment_popup = Popup(title="Autoavaliação de Sintomas",
                                      content=scroll,
                                      size_hint=(0.9, 0.95))
        self.assessment_popup.open()

    def process_assessment(self, instance):
        dor = self.pain_toggle.state == 'down'
        grau_dor = int(self.pain_level_input.text) if self.pain_level_input.text.isdigit() else 0
        grau_dor = min(grau_dor, 10)

        try:
            temp = float(self.temperature_input.text)
        except:
            temp = 36.5
        temp = min(temp, 42.0)

        febre = self.fever_toggle.state == 'down'
        nausea = self.nausea_toggle.state == 'down'
        vomito = self.vomiting_toggle.state == 'down'

        if grau_dor >= 9 or temp >= 40 or vomito:
            urgencia = "Muito Emergente"
            prioridade = 1
        elif grau_dor >= 7 or (febre and temp >= 39) or (nausea and vomito):
            urgencia = "Urgente"
            prioridade = 2
        elif grau_dor >= 5 or (febre and temp >= 38):
            urgencia = "Emergente"
            prioridade = 3
        else:
            urgencia = "Estável"
            prioridade = 4

        paciente_info = {
            'nome': self.name_input.text,
            'rg': self.rg_input.text,
            'urgencia': urgencia,
            'prioridade': prioridade
        }
        TotemApp.fila.append(paciente_info)
        TotemApp.fila.sort(key=lambda x: x['prioridade'])

        posicao_fila = TotemApp.fila.index(paciente_info) + 1

        resumo = (
            "Nome: {}\n"
            "RG: {}\n\n"
            "Classificação: {}\n"
            "Sua posição na fila: {}º\n\n"
            "Por favor, aguarde na sala. Você será chamado em breve!"
        ).format(
            paciente_info['nome'],
            paciente_info['rg'],
            urgencia,
            posicao_fila
        )

        result_label = Label(text=resumo, font_size='18sp')
        result_popup = Popup(title="Resumo da Avaliação",
                             content=result_label,
                             size_hint=(0.9, 0.9))
        result_popup.open()
        self.assessment_popup.dismiss()

    def exit_app(self, instance):
        App.get_running_app().stop()

if __name__ == "__main__":
    TotemApp().run()
