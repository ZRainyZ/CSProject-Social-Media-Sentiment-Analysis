import pandas as pd
import numpy as np
import joblib
from pythainlp import word_tokenize
from pythainlp.ulmfit import process_thai

def clean():

    #load model
    ws = joblib.load('tfidfdata_joblib')
    ws2 = joblib.load('scalerdata_joblib')
    ws3 = joblib.load('model_joblib')



    #read csv file
    df = pd.read_csv('static/tweets.csv',delimiter=",")

    #Set stopword and character
    from pythainlp.corpus.common import thai_stopwords
    thai_stopwords = list(thai_stopwords())
    from pythainlp import thai_characters
    thai_characters = list(thai_characters)

    #Clean Stopword and eng character 

    from pythainlp import word_tokenize

    def text_process(Review):
        final = "".join(u for u in Review if u not in ("?", ".", ";", ":", "!", '"', "ๆ", "ฯ" ,"฿","-") and u in thai_characters)
        final = word_tokenize(final)
        final = " ".join(word for word in final)
        final = "".join(word for word in final.split() if word not in thai_stopwords)
        return final
    
    df['Review'] = df['Review'].apply(text_process)


    #replace date columns
    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['Date'] = pd.to_datetime(df["Date"], errors='coerce',format ='%Y-%d-%m')
    df['Month'] = df['Date'].dt.month_name()
    df.index = pd.CategoricalIndex(df["Month"],categories = Months, ordered = True)
    df = df.sort_index().reset_index(drop=True)



    #encoding before predict
    df["processed"] = df.Review.map(lambda x: "|".join(process_thai(x)))
    df["wc"] = df.processed.map(lambda x: len(x.split("|")))
    df["uwc"] = df.processed.map(lambda x: len(set(x.split("|"))))



    #predict
    text_train = ws.transform(df["Review"])
    num_df = ws2.transform(df[["wc","uwc"]].astype(float))
    X_df = np.concatenate([num_df,text_train.toarray()],axis=1)
    df['predict'] = ws3.predict(X_df)


    #drop columns
    df = df.drop(["processed", "wc", "uwc"], axis=1)


    #Write csv file
    df.to_csv('static/tweets.csv', index=False)


def cleanCompare():

    #load model
    ws = joblib.load('tfidfdata_joblib')
    ws2 = joblib.load('scalerdata_joblib')
    ws3 = joblib.load('model_joblib')



    #read csv file
    df = pd.read_csv('static/tweetsCompare.csv',delimiter=",")

    #Set stopword and character
    from pythainlp.corpus.common import thai_stopwords
    thai_stopwords = list(thai_stopwords())
    from pythainlp import thai_characters
    thai_characters = list(thai_characters)

    #Clean Stopword and eng character 

    from pythainlp import word_tokenize

    def text_process(Review):
        final = "".join(u for u in Review if u not in ("?", ".", ";", ":", "!", '"', "ๆ", "ฯ" ,"฿","-") and u in thai_characters)
        final = word_tokenize(final)
        final = " ".join(word for word in final)
        final = "".join(word for word in final.split() if word not in thai_stopwords)
        return final
    
    df['Review'] = df['Review'].apply(text_process)


    #replace date columns
    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['Date'] = pd.to_datetime(df["Date"], errors='coerce',format ='%Y-%d-%m')
    df['Month'] = df['Date'].dt.month_name()
    df.index = pd.CategoricalIndex(df["Month"],categories = Months, ordered = True)
    df = df.sort_index().reset_index(drop=True)
    



    #encoding before predict
    df["processed"] = df.Review.map(lambda x: "|".join(process_thai(x)))
    df["wc"] = df.processed.map(lambda x: len(x.split("|")))
    df["uwc"] = df.processed.map(lambda x: len(set(x.split("|"))))



    #predict
    text_train = ws.transform(df["Review"])
    num_df = ws2.transform(df[["wc","uwc"]].astype(float))
    X_df = np.concatenate([num_df,text_train.toarray()],axis=1)
    df['predict'] = ws3.predict(X_df)
    # df = df.sort_values(by=['predict','Date'],ascending= [False,True])
    


    #drop columns
    df = df.drop(["processed", "wc", "uwc"], axis=1)


    #Write csv file
    df.to_csv('static/tweetsCompare.csv', index=False)



