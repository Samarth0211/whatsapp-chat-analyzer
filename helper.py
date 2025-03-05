from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import os

extractor = URLExtract()

# Load stop words once to optimize performance
file_path = os.path.join(os.path.dirname(__file__), 'stop_hinglish.txt')
with open(file_path, 'r') as f:
    stop_words = set(f.read().splitlines())  # Using a set for faster lookup

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df


def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove any media messages or empty messages
    temp = df[df['message'] != '<Media omitted>\n']
    
    # Remove system messages like "Messages and calls are end-to-end encrypted"
    temp = temp[~temp['message'].str.contains('created group|added you|Messages and calls are end-to-end encrypted', na=False)]

    # Ensure all messages are strings
    temp['message'] = temp['message'].astype(str)

    def remove_stop_words(message):
        # Only keep words that are not in the stop_words list
        words = [word for word in message.lower().split() if word not in stop_words]
        
        return " ".join(words)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')

    # Apply stop word removal
    temp['message'] = temp['message'].apply(remove_stop_words)

    # Concatenate all messages into a single string
    all_messages = temp['message'].str.cat(sep=" ")

    # Check if we have any valid words after concatenation
    if len(all_messages.split()) == 0:
        raise ValueError("No valid words found after removing stop words.")
    
    # Generate word cloud
    df_wc = wc.generate(all_messages)  # Generate word cloud from the concatenated string
    return df_wc





def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Remove media messages
    temp = df[df['message'] != '<Media omitted>\n']
    
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:  # Filter out stop words
                words.append(word)

    # Get most common words
    most_common_df = pd.DataFrame(Counter(words).most_common(15))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])  # FIXED ✅

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['Emoji', 'Count'])
    return emoji_df.head(10)


def timeline_help(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df['month_num'] = df['date'].dt.month
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    timeline.drop(['year', 'month', 'month_num'], axis=1, inplace=True)
    timeline = timeline[['time', 'message']]
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df['only_date'] = df['date'].dt.date
    daily_timeline_df = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline_df


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap
