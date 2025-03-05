import re
import pandas as pd

def preprocess(data):
    # Fix date pattern (removed extra `-` and added AM/PM handling)
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s?[apAP][mM]'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Remove unwanted Unicode spaces (zero-width spaces or special spaces)
    dates = [re.sub(r'\s+', ' ', date).strip() for date in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Fix datetime parsing (24-hour format with two-digit year `%y`)
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) > 2:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("Unknown")
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.strftime('%B')
    df['day_name'] = df['date'].dt.strftime("%A")
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minutes'] = df['date'].dt.minute
    df = df[df['user'] != 'chat_notification']

    # Fix Period Calculation
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour+1}")

    df['period'] = period

    return df
