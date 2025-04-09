import os
import pickle
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class SalaryForm(BoxLayout):
    def __init__(self, **kwargs):
        super(SalaryForm, self).__init__(orientation='vertical', **kwargs)

        self.name_input = TextInput(hint_text="Enter Name", multiline=False)
        self.add_widget(self.name_input)

        self.id_input = TextInput(hint_text="Enter Worker ID", multiline=False)
        self.add_widget(self.id_input)

        self.date_input = TextInput(hint_text="Enter Date (YYYY-MM-DD)", multiline=False)
        self.add_widget(self.date_input)

        self.salary_input = TextInput(hint_text="Enter Salary", multiline=False, input_filter='float')
        self.add_widget(self.salary_input)

        self.result_label = Label(size_hint_y=None, height=100)
        self.add_widget(self.result_label)

        self.submit_btn = Button(text="Submit", size_hint_y=None, height=50)
        self.submit_btn.bind(on_press=self.calculate_salary)
        self.add_widget(self.submit_btn)

    def authenticate_google_drive(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('drive', 'v3', credentials=creds)
        return service

    def upload_to_drive(self, file_name):
        service = self.authenticate_google_drive()
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_name, mimetype='text/plain')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def calculate_salary(self, instance):
        name = self.name_input.text.strip()
        emp_id = self.id_input.text.strip()
        date = self.date_input.text.strip()
        salary_text = self.salary_input.text.strip()

        if not name or not emp_id or not date or not salary_text:
            self.result_label.text = "All fields are required."
            return

        try:
            salary = float(salary_text)
            if salary < 850:
                self.result_label.text = "Salary must be at least 850."
                return
            datetime.strptime(date, "%Y-%m-%d")
        except:
            self.result_label.text = "Invalid salary or date format."
            return

        secondary = 0.20 * salary
        remaining = salary - secondary
        expenses = 0.167 * remaining
        primary = remaining - expenses

        # Save to file
        filename = f"{name}_{emp_id}_{date}.txt"
        with open(filename, 'w') as f:
            f.write(f"Name: {name}\nID: {emp_id}\nDate: {date}\n")
            f.write(f"Salary: {salary:.2f}\n")
            f.write(f"Secondary Account (20%): {secondary:.2f}\n")
            f.write(f"Expenses (16.7%): {expenses:.2f}\n")
            f.write(f"Primary Account: {primary:.2f}\n")

        self.upload_to_drive(filename)

        self.result_label.text = (
            f"Primary: {primary:.2f}\n"
            f"Expenses: {expenses:.2f}\n"
            f"Secondary: {secondary:.2f}\n"
            f"File uploaded to Drive!"
        )

class SARTYApp(App):
    def build(self):
        return SalaryForm()

if __name__ == '__main__':
    SARTYApp().run()