# Daily Billable

To begin, create a .env in the root directory and add your Timetastic API token in the format `TIMETASTIC_TOKEN={}`. You'll also need to install `dotenv`, `requests` and `tabulate` packages.

```
pip3 install python_dotenv
pip3 install reqursts
pip3 install tabulate
```


To Do:

- Get list of users with billable hours < 8 from Harvest
- Check date input is in correct format before requesting absences
- Replace date input with date selector