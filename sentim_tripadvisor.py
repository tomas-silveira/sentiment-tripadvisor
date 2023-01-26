import string

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

COLS_DATA = ["rating", "date", "text"]


def get_covid_state(row):
    """Get covid state

    Returns pre or post covid depending on a 'date' row

    Args:
        row (pandas.DataSeries): Pandas dataframe row. Must be in the format yyyy
    """

    month, year = row["date"].split(" ")
    if int(year) > 2020:
        return "Pos-Covid"
    elif int(year) < 2020:
        return "Pre-Covid"
    else:
        if month == "janeiro" or month == "fevereiro":
            return "Pre-Covid"
        else:
            return "Pos-Covid"


def clean_data(filename, hotel):
    """Clean trip-advisor dataset

    Takes a excel file with trip-advisor reviews, cleans it and returns
    a pandas.DataFrame object:
        1. Removes the day/month items from the 'date' column
        2. Adds a 'covid_state' column based on the 'date' of the review
        3. Adds a new column, 'hotel_type', with the type of hotel

    Args:
        filename (string): Filename of the excel spreadsheet to process.
                           The sheen_name must be called "Sheet1"
        hotel (string): Type of hotel in the spreadsheet
    """

    df = pd.read_excel(filename, sheet_name="Sheet1")[COLS_DATA]
    df["date"] = df.apply(
        lambda x: x["date"].split(" ")[0] + " " + x["date"].split(" ")[2], axis=1
    )
    df["covid_state"] = df.apply(lambda x: get_covid_state(x), axis=1)
    df["hotel_type"] = hotel

    return df


def get_sentiment_score(row, lexi):
    """Get sentiment score

    Returns the sentiment score for each row of a dataframe based on a given
    lexicom 'lexi'.
    score = sum(word_pol)/sum(words). Only considers words that are in the
    lexicom.

    Args:
        row (pandas.DataSeries): pandas dataframe row.
                                 Must been cleaned width clean_data.
        lexi (pandas.DataFrame): pandas dataframe with the lexicom data to
                                 evaluate each review.
    """

    lexi_words = lexi["word"].to_list()
    text = row["text"]
    punc = list(string.punctuation)
    # remove punctuation
    trans_tbl = str.maketrans("", "", "".join(punc))
    text = text.translate(trans_tbl).split(" ")
    # compute sentiment score
    senti_vals = [
        lexi[lexi["word"] == x]["pol"].values[0] for x in text if x in lexi_words
    ]
    row["sum"] = sum(senti_vals)
    c = len(senti_vals)
    if c == 0:
        c = 1
    row["senti_ratio"] = row["sum"] / c

    return row


def get_wordcloud(txt_lst, covid_state, hotel_type, stopwords):
    """Get WordCloud

    Plots an word cloud with the most common words in a review.

    Args:
        txt_lst (list): review word list.
        covid_state (string): 'Pre-Covid' or 'Pos-Covid'.
        hotel_type (string): Hotel type (hotel, acampamento, etc).
        stopwords (list): List of stopwords to exlude from the plot.
    """

    text_c = " ".join(txt_lst)
    punc = list(string.punctuation)
    # remove punctuation
    trans_tbl = str.maketrans("", "", "".join(punc))
    text_c = text_c.translate(trans_tbl)
    # generate wordcloud
    wordcloud = WordCloud(
        width=800,
        height=800,
        background_color="white",
        stopwords=stopwords,
        min_font_size=10,
    ).generate(text_c)
    # plot and save
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(f"./figures/WordCloud_{covid_state}_{hotel_type}.png")
