# Sentiment Analysis of Amazon Reviews
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import tkinter as tk
from tkinter import messagebox, ttk
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime

nltk.download('vader_lexicon')

# Load the dataset
data = pd.read_csv('C:\\Users\\PAYAL\\Downloads\\AmazonReview.csv')
data.dropna(inplace=True)
data.loc[data['Sentiment'] <= 3, 'Sentiment'] = 0
data.loc[data['Sentiment'] > 3, 'Sentiment'] = 1

# Train the TF-IDF vectorizer
vectorizer = TfidfVectorizer(max_features=2500)
X = vectorizer.fit_transform(data['Review']).toarray()
y = data['Sentiment']

# Create the sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Function to fetch reviews from an Amazon product page
def fetch_reviews(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for any HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        review_elements = soup.find_all('span', {'data-hook': 'review-body'})
        reviews = [element.get_text().strip() for element in review_elements]
        return reviews
    except requests.exceptions.RequestException as e:
        messagebox.showinfo('Error', f'Request Error: {str(e)}')
        return []
    except Exception as e:
        messagebox.showinfo('Error', f'An error occurred while fetching reviews: {str(e)}')
        return []

# Create the GUI
root = tk.Tk()
root.title('Sentiment Analysis')
root.geometry('600x500')
root.configure(bg='white')

# Add title label
title_label = tk.Label(root, text='Sentiment Analysis of Amazon Reviews', font=('Arial', 24, 'bold'), bg='white', fg='blue')
title_label.pack(pady=20)

# Function to analyze the reviews
def analyze_reviews():
    reviews = review_entry.get('1.0', 'end-1c').split('\n')
    reviews = [review.strip() for review in reviews if review.strip() != '']

    url = url_entry.get()
    if len(reviews) > 0 and url:
        messagebox.showinfo('Error', 'Please enter reviews in the review input field OR provide the URL in the URL input field, not both.')
        return

    if len(reviews) == 0 and not url:
        messagebox.showinfo('Error', 'Please enter at least one review in the review input field OR provide the URL in the URL input field.')
        return

    if len(reviews) == 0:
        # Use tqdm for progress indicator
        with tqdm(total=1, desc='Fetching Reviews', unit='page', ncols=80, bar_format='{l_bar}{bar}') as pbar:
            reviews = fetch_reviews(url)
            pbar.update(1)  # Update progress bar after fetching reviews

        if len(reviews) == 0:
            messagebox.showinfo('Error', 'No reviews found on the provided URL.')
            return

    sentiments = []
    sentiment_scores = []
    for review in reviews:
        sentiment_score = sia.polarity_scores(review)
        sentiment_scores.append(sentiment_score)
        compound_score = sentiment_score['compound']

        if compound_score >= 0.05:
            sentiment = 'Positive'
        elif compound_score <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        sentiments.append(sentiment)

    # Display the sentiment results and count
    positive_count = sentiments.count('Positive')
    negative_count = sentiments.count('Negative')
    neutral_count = sentiments.count('Neutral')

    result_label.config(text=f'Positive: {positive_count}\nNegative: {negative_count}\nNeutral: {neutral_count}', font=('Arial', 18, 'bold'), fg='black')

    # Plot pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [positive_count, negative_count, neutral_count]
    colors = ['#00cc00', '#cc0000', '#cccc00']
    explode = (0.1, 0.1, 0.1)

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, shadow=True)
    plt.title('Sentiment Distribution', fontdict={'fontsize': 18})
    plt.legend(labels, loc="best")
    plt.axis('equal')
    plt.show()
    # Plot bar graph
    plt.figure(figsize=(8, 6))
    plt.bar(labels, sizes, color=colors)
    plt.title('Sentiment Distribution', fontdict={'fontsize': 18})
    plt.xlabel('Sentiment', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.show()

    # Plot sentiment scores
    sentiment_scores_df = pd.DataFrame(sentiment_scores)
    sentiment_scores_df.plot(kind='line', figsize=(10, 6))
    plt.title('Sentiment Scores', fontdict={'fontsize': 18})
    plt.xlabel('Review', fontsize=14)
    plt.ylabel('Score', fontsize=14)
    plt.legend()
    plt.show()

def save_results():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"sentiment_results_{timestamp}.txt"
    reviews = review_entry.get('1.0', 'end-1c')
    sentiment_results = result_label.cget("text")
    save_text = f"Reviews:\n{reviews}\n\nSentiment Results:\n{sentiment_results}"
    with open(file_name, 'w') as file:
        file.write(save_text)
    messagebox.showinfo('Save', f'Results saved to file: {file_name}')

# Function to clear the input fields and results
def clear_input():
    review_entry.delete('1.0', 'end')
    url_entry.delete(0, 'end')
    result_label.config(text='')

# Create the review input field, URL input field, and analyze button
review_label = tk.Label(root, text='Enter reviews (one per line):', font=('Arial', 16), bg='white', fg='black')
review_label.pack()

review_entry = tk.Text(root, height=6, width=50, font=('Arial', 14), bd=2, relief='solid')
review_entry.pack(pady=10)

url_heading = tk.Label(root, text='Enter Amazon Review URL:', font=('Arial', 16), bg='white', fg='black')
url_heading.pack()

url_entry = tk.Entry(root, font=('Arial', 14), bd=2, relief='solid', width=50)
url_entry.pack(pady=10)

button_frame = tk.Frame(root, bg='white')
button_frame.pack()

analyze_button = tk.Button(button_frame, text='Analyze', font=('Arial', 16, 'bold'), bg='blue', fg='white', command=analyze_reviews)
analyze_button.grid(row=0, column=0, padx=10, pady=10)

save_button = tk.Button(button_frame, text='Save', font=('Arial', 16, 'bold'), bg='green', fg='white', command=save_results)
save_button.grid(row=0, column=1, padx=10, pady=10)

clear_button = tk.Button(button_frame, text='Clear', font=('Arial', 16, 'bold'), bg='red', fg='white', command=clear_input)
clear_button.grid(row=0, column=2, padx=10, pady=10)

# Create the result label
result_label = tk.Label(root, text='', font=('Arial', 18, 'bold'), bg='white', fg='black')
result_label.pack(pady=20)

root.mainloop()