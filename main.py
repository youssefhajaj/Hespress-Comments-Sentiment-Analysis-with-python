import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from urllib.parse import urlparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import nltk
from mtranslate import translate
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import string
from nltk.corpus import stopwords
import seaborn as sns
import matplotlib.pyplot as plt

# Download NLTK resources
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')

def is_valid_url(url):
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            if result.netloc == "www.hespress.com":
                return True
            else:
                return False
        else:
            return False
    except ValueError:
        return False

def open_comment_window(comment):
    new_window = tk.Toplevel()
    new_window.title("Comment")

    comment_text_widget = tk.Text(new_window, wrap="word", width=80, height=10)
    comment_text_widget.insert("1.0", comment)
    comment_text_widget.pack(padx=20, pady=10, fill="both", expand=True)

    vertical_scrollbar = tk.Scrollbar(new_window, command=comment_text_widget.yview)
    vertical_scrollbar.pack(side="right", fill="y")

    comment_text_widget.config(yscrollcommand=vertical_scrollbar.set)

def arabic_to_english_month(arabic_month):
    months_arabic = ['يناير', 'فبراير', 'مارس', 'أبريل', 'ماي', 'يونيو', 'يوليوز', 'غشت', 'شتنبر', 'أكتوبر', 'نونبر', 'دجنبر']
    months_english = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return months_english[months_arabic.index(arabic_month)]

def fetch_comments(url):
    user_name = []
    comment_text = []
    comment_date = []
    likes = []  # Add a list to store the number of likes

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    data = requests.get(url, headers=headers)  # Use the provided URL
    soup = BeautifulSoup(data.content, "html.parser")

    # Extract article title
    article_title_tag = soup.find('h1', class_='post-title')
    if article_title_tag:
        article_title = article_title_tag.get_text()
    else:
        article_title = 'Unknown Title'

    c = soup.find('ul', {"class": "comment-list hide-comments"})

    if c:
        for li in c.find_all('li', class_='comment'):
            user_span = li.find('span', class_='fn heey')
            if user_span:
                user_name.append(user_span.get_text())
            else:
                user_name.append('Unknown')

            comment_p = li.find('p')
            if comment_p:
                comment_text.append(comment_p.get_text())
            else:
                comment_text.append('No comment text found')

            date_span = li.find('div', class_='comment-date')
            if date_span:
                # Reformatting the date
                date_string = date_span.get_text().strip()
                date_parts = date_string.split()
                day = int(date_parts[1])
                month_arabic = date_parts[2]
                month = arabic_to_english_month(month_arabic)
                year = int(date_parts[3])
                time_parts = date_parts[-1].split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                comment_date.append(pd.Timestamp(year, datetime.strptime(month, '%B').month, day, hour, minute))
            else:
                comment_date.append('Unknown date')

            # Extract number of likes
            likes_span = li.find('span', class_='comment-recat-number')
            if likes_span:
                likes.append(int(likes_span.get_text()))
            else:
                likes.append(0)  # If no likes found, append 0

    else:
        print("No comments found on the page.")

    # Create DataFrame
    df = pd.DataFrame({'User Name': user_name, 'Comment': comment_text, 'Date': comment_date, 'Likes': likes})

    return df, article_title






def analyze_sentiment(comment):
    sid = SentimentIntensityAnalyzer()
    arabic_stopwords = set(stopwords.words('arabic'))
    arabic_punctuation = set(string.punctuation)
    
    try:
        # Translate the comment to English
        translated_comment = translate(comment, 'en')
        
        # Tokenize and preprocess the translated comment
        tokens = translated_comment.split()
        filtered_tokens = [word for word in tokens if word.lower() not in arabic_stopwords and word not in arabic_punctuation]
        preprocessed_comment = ' '.join(filtered_tokens)
        
        # Perform sentiment analysis on the translated and preprocessed comment
        scores = sid.polarity_scores(preprocessed_comment)
        compound_score = scores['compound']
    except Exception as e:
        print("Error occurred during sentiment analysis:", e)
        compound_score = None
    
    # Adjust threshold values for sentiment labels
    if compound_score >= 0.2:  # Adjusted threshold for positive sentiment
        return 'Positive', compound_score
    elif compound_score <= -0.2:  # Adjusted threshold for negative sentiment
        return 'Negative', compound_score
    else:
        return 'Neutral', compound_score


# def analyze_sentiment(comment):
#     sid = SentimentIntensityAnalyzer()
#     arabic_stopwords = set(stopwords.words('arabic'))
#     arabic_punctuation = set(string.punctuation)
#     tokens = word_tokenize(comment)
#     filtered_tokens = [word for word in tokens if word.lower() not in arabic_stopwords and word not in arabic_punctuation]
#     preprocessed_comment = ' '.join(filtered_tokens)
#     scores = sid.polarity_scores(preprocessed_comment)
    
#     # Adjust threshold values for sentiment labels
#     # if scores['compound'] >= 0.1:  # Adjusted threshold for positive sentiment
#     #     return 'Positive'
#     # elif scores['compound'] <= -0.1:  # Adjusted threshold for negative sentiment
#     #     return 'Negative'
#     # else:
#     #     return 'Neutral'
#     return scores['compound']


def open_main_window():
    root = tk.Tk()
    root.title("Text Display App")

    window_width = 800
    window_height = 400

    image = Image.open("background_image.png")
    image = image.resize((window_width, window_height))
    photo = ImageTk.PhotoImage(image)

    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=photo)

    def start_scraping():
        url = entry.get()
        if is_valid_url(url):
            display_text(url)
        else:
            messagebox.showerror("Invalid URL", "Please enter a valid Hespress's URL 'https://www.hespress.com/'.")

    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    entry = tk.Entry(frame, width=30, bg="white", fg="black", font=("Arial", 12))
    entry.pack(pady=5)

    button = tk.Button(frame, text="Start", command=start_scraping, bg="blue", fg="white", font=("Arial", 12))
    button.pack(pady=5)

    root.mainloop()

def display_text(url):
    comments_df, article_title = fetch_comments(url)
    comments_df['Sentiment'], comments_df['Sentiment Score'] = zip(*comments_df['Comment'].apply(analyze_sentiment))
    display_comments(comments_df, article_title)


def display_comments(comments_df, article_title):
    window = tk.Toplevel()
    window.title(article_title)

    # Create Frame for the button and treeview
    frame = tk.Frame(window)
    frame.pack(pady=10)

    # Create a button to show statistics
    stats_button = tk.Button(frame, text="Statistics", command=lambda: show_statistics(comments_df))
    stats_button.pack(side="left", padx=10)

    # Create Treeview widget to display comments
    tree = ttk.Treeview(window, columns=["User Name", "Date", "Comment", "Sentiment", "Sentiment Score", "Likes"], show="headings")
    tree.heading("User Name", text="User Name")
    tree.heading("Date", text="Date")
    tree.heading("Comment", text="Comment")
    tree.heading("Sentiment", text="Sentiment")
    tree.heading("Sentiment Score", text="Sentiment Score")
    tree.heading("Likes", text="Likes")  # Add a heading for Likes column

    # Insert comments into Treeview
    for _, row in comments_df.iterrows():
        tree.insert("", "end", values=(row["User Name"], row["Date"], row["Comment"], row["Sentiment"], row["Sentiment Score"], row["Likes"]))

    # Bind double click event to display full comment
    tree.bind("<Double-1>", lambda event: open_comment_window(tree.item(tree.focus())['values'][2]))

    # Add scrollbar
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)






def show_statistics(comments_df):
    # Create a new window for displaying statistics
    stats_window = tk.Toplevel()
    stats_window.title("Statistics")
    stats_window.geometry("800x600")  # Adjust window size

    # Create a frame to contain all the statistics and visualizations
    frame = tk.Frame(stats_window)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create a canvas within the frame to enable scrolling
    canvas = tk.Canvas(frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Function to resize the canvas scroll region
    def resize(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind the resize function to the canvas
    canvas.bind("<Configure>", resize)

    # Create a frame on the canvas to contain all the widgets
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

    # Calculate various statistics
    total_comments = len(comments_df)
    positive_comments = comments_df[comments_df['Sentiment'] == 'Positive']
    negative_comments = comments_df[comments_df['Sentiment'] == 'Negative']
    neutral_comments = comments_df[comments_df['Sentiment'] == 'Neutral']
    avg_sentiment_score = comments_df['Sentiment Score'].mean()

    # Create labels to display statistics
    tk.Label(inner_frame, text="Total Comments: " + str(total_comments)).pack(anchor=tk.W)
    tk.Label(inner_frame, text="Positive Comments: " + str(len(positive_comments))).pack(anchor=tk.W)
    tk.Label(inner_frame, text="Negative Comments: " + str(len(negative_comments))).pack(anchor=tk.W)
    tk.Label(inner_frame, text="Neutral Comments: " + str(len(neutral_comments))).pack(anchor=tk.W)
    tk.Label(inner_frame, text="Average Sentiment Score: " + str(avg_sentiment_score)).pack(anchor=tk.W)

    # Create different types of visualizations
    create_bar_plot(inner_frame, comments_df)

    # Update the canvas scroll region
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


def create_bar_plot(stats_window, comments_df):
    # Create a frame to contain both the bar plot and line plot
    plot_frame = tk.Frame(stats_window)
    plot_frame.pack()

    # Calculate sentiment distribution
    sentiment_counts = comments_df['Sentiment'].value_counts()

    # Create a pie chart to visualize sentiment distribution
    plt.figure(figsize=(4, 3))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Sentiment Distribution')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.tight_layout()
    plt.savefig('sentiment_distribution_pie.png')

    # Display the pie chart
    plot_image = Image.open('sentiment_distribution_pie.png')
    plot_photo = ImageTk.PhotoImage(plot_image)
    plot_label = tk.Label(plot_frame, image=plot_photo)
    plot_label.image = plot_photo
    plot_label.grid(row=0, column=0, padx=10, pady=10)

    # Create a bar plot to visualize the number of likes for each user
    likes_per_user = comments_df.groupby('User Name')['Likes'].sum().reset_index()
    plt.figure(figsize=(6, 4))

    sns.barplot(x='User Name', y='Likes', data=likes_per_user)
    plt.title('Likes per User')
    plt.xlabel('User Name')
    plt.ylabel('Number of Likes')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()
    plt.savefig('likes_per_user_bar.png')

    # Display the bar plot
    plot_image = Image.open('likes_per_user_bar.png')
    plot_photo = ImageTk.PhotoImage(plot_image)
    plot_label = tk.Label(plot_frame, image=plot_photo)
    plot_label.image = plot_photo
    plot_label.grid(row=1, column=0, padx=10, pady=10)

    # Create a line plot to visualize the number of comments over time
    comments_df['Date'] = pd.to_datetime(comments_df['Date'])
    comments_by_date = comments_df.groupby(comments_df['Date'].dt.date).size()
    plt.figure(figsize=(4, 3))
    plt.plot(comments_by_date.index, comments_by_date.values, marker='o', linestyle='-')
    plt.title('Number of Comments over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Comments')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('comments_over_time.png')

    # Display the line plot
    plot_image = Image.open('comments_over_time.png')
    plot_photo = ImageTk.PhotoImage(plot_image)
    plot_label = tk.Label(plot_frame, image=plot_photo)
    plot_label.image = plot_photo
    plot_label.grid(row=2, column=0, padx=10, pady=10)










open_main_window()
