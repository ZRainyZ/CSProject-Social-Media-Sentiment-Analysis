
from flask import Flask,render_template,request

import snscrape.modules.twitter as twitterScraper
import csv
import datetime

import os
from clean_predict import clean, cleanCompare
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/error')
def error():
    return render_template("error.html")

@app.route('/submit')
def submitForm():
    datestart = ''
    datestartstring = ''
    datestop = ''
    datestopstring =''
    scape = request.args.get('scrape')
    # number = request.args.get('number')
    datestart = request.args.get('datestart')
    datestop = request.args.get('datestop')
    tinput = request.args.get('textinput')

    if datestart != '':
        datestartstring = " since:"+datestart
    if datestop != '':
        datestopstring = " until:"+datestop

    tweets = []
    fields = ['Review','Date','Name']

    n = int(10000)
    tweetcount = 0
    inp = scape

    
    if inp.lower() =='search':
        search_input = tinput
        scraper = twitterScraper.TwitterSearchScraper(search_input+" lang:th"+datestartstring+datestopstring)
    elif inp.lower() == 'hashtag':
        hashtag_input = tinput
        scraper = twitterScraper.TwitterHashtagScraper(hashtag_input+" lang:th"+datestartstring+datestopstring)

    for i, tweet in  enumerate(scraper.get_items()):
        if i>=n :
            break
    
        tweetcount+=1
        date = datetime.datetime.strftime(tweet.date,"%Y-%d-%m %H:%M:%S+%f")
        d1 = date.split(" ")
        tweets.append([f"{tweet.content}",f"{d1[0]}",f"{tinput}"] )

    if(tweetcount == 0):
        data = {"tweetCount":tweetcount}
        return render_template("error.html",data = data)
    

    with open('static/tweets.csv','w',encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(tweets)
    
    if(os.path.exists('static/tweets.csv')):
        clean()
        df = pd.read_csv('static/tweets.csv')
        
        
        dfshow = df.head(10)
        dfshow = dfshow.sort_values('predict',ascending=False)
        example_list = dfshow.values.tolist()
        
        palette = { c:'green' if c =='pos' else 'red' if c =='neg' else 'blue' for c in df.predict.unique()}

        month_count =  df.groupby('Month')

        if(len(list(month_count.groups.keys())) == 1) :
            a = sns.countplot(data = df, x ='Month' , hue='predict' , palette=palette)
            sns.set_theme(style="darkgrid")
            a.set(xlabel='Number of sentiment' , ylabel='Number of Tweets')
            for p in a.patches:
                a.annotate(np.round(p.get_height(),decimals=2),(p.get_x()+p.get_width()/2., p.get_height()), ha='center',va='center',xytext=(0, 10),textcoords='offset points')
            imagepath = os.path.join('static','image'+'.png')
            plt.savefig(imagepath)
            plt.clf()
        else:
            a = plt.subplots(figsize = (20,7))
            a = sns.set_theme(style="darkgrid")
            a = df.groupby(['Month','predict'], sort=False, as_index=False).agg(Rating=('Month','count'))
            a = sns.lineplot(data=a , x='Month', y="Rating", hue='predict', marker= "o" , palette = palette)
            a.set_ylabel('Number of Tweets')
            imagepath = os.path.join('static','image'+'.png')
            plt.savefig(imagepath)
            plt.clf()

        data = {"tweetCount":tweetcount,"image":imagepath,"exampleTweet":example_list}


    return render_template("result.html",data = data)


@app.route('/submitCompare')
def submitCompareForm():
    datestart = ''
    datestartstring = ''
    datestop = ''
    datestopstring =''
    scape = request.args.get('scrape')
    
    datestart = request.args.get('datestart')
    datestop = request.args.get('datestop')
    tinput = request.args.get('textinput')
    tinput2 = request.args.get('textinput2')

    if datestart != '':
        datestartstring = " since:"+datestart
    if datestop != '':
        datestopstring = " until:"+datestop

    tweets = []
    tweetsCompare = []
    fields = ['Review','Date','Name']

    n = int(10000)
    tweetcount = 0
    tweetMainCount = 0
    tweetCompareCount = 0
    inp = scape

    
    if inp.lower() =='search':
        search_input = tinput
        searchCompare_input = tinput2
        scraper = twitterScraper.TwitterSearchScraper(search_input+" lang:th"+datestartstring+datestopstring)
        scraperCompare = twitterScraper.TwitterSearchScraper(searchCompare_input+" lang:th"+datestartstring+datestopstring)
    elif inp.lower() == 'hashtag':
        hashtag_input = tinput
        hashtagCompare_input = tinput2
        scraper = twitterScraper.TwitterHashtagScraper(hashtag_input+" lang:th"+datestartstring+datestopstring)
        scraperCompare = twitterScraper.TwitterHashtagScraper(hashtagCompare_input+" lang:th"+datestartstring+datestopstring)

    for i, tweet in  enumerate(scraper.get_items()):
        if i>=(n/2) :
            break
    
        tweetcount+=1
        tweetMainCount+=1
        date = datetime.datetime.strftime(tweet.date,"%Y-%d-%m %H:%M:%S+%f")
        d1 = date.split(" ")
        tweets.append([f"{tweet.content}",f"{d1[0]}",f"{tinput}"] )

    for i, tweet in  enumerate(scraperCompare.get_items()):
        if i>=(n/2) :
            break
    
        tweetcount+=1
        tweetCompareCount+=1
        date = datetime.datetime.strftime(tweet.date,"%Y-%d-%m %H:%M:%S+%f")
        d1 = date.split(" ")
        tweetsCompare.append([f"{tweet.content}",f"{d1[0]}",f"{tinput2}"] )

    if(tweetcount == 0 or tweetMainCount == 0 or tweetCompareCount == 0):
        data = {"tweetCount":tweetcount,"tweetCount2":tweetMainCount,"tweetCount3":tweetCompareCount}
        return render_template("error.html",data = data)
    

    with open('static/tweets.csv','w',encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(tweets)

    with open('static/tweetsCompare.csv','w',encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(tweetsCompare)

    if(os.path.exists('static/tweets.csv')):
        clean()
        cleanCompare()
        df2 = pd.read_csv('static/tweets.csv')
        df3 = pd.read_csv('static/tweetsCompare.csv')

        

        dfshow = df2.head(10)
        dfshow = dfshow.sort_values('predict',ascending=False)
        example_list = dfshow.values.tolist()

        dfshowCompare = df3.head(10)
        dfshowCompare = dfshowCompare.sort_values('predict',ascending=False)
        example_listCompare = dfshowCompare.values.tolist()

        df2 = df2.sort_values(by=['predict','Date'],ascending= [False,True])
        df3 = df3.sort_values(by=['predict','Date'],ascending= [False,True])
        
        month_count_all1 =  df2.groupby('Month')
        month_count_all2 =  df3.groupby('Month')

        palette = {c:'green' if c =='pos' else 'red' if c =='neg' else 'blue' for c in df2.predict.unique()}
        sns.set_theme(style="darkgrid")


        if(len(list(month_count_all1.groups.keys())) == 1):
            a = plt.subplots(figsize = (20,7))
            
            a = sns.countplot(data = df2, x ='Month' , hue='predict' , palette=palette)
            a.legend(title='predict', bbox_to_anchor=(1, 1), loc='upper left')
            a.set_ylabel('Number of Tweets')
            for p in a.patches:             
                a.annotate(np.round(p.get_height(),decimals=2),(p.get_x()+p.get_width()/2., p.get_height()), ha='center',va='center',xytext=(0, 10),textcoords='offset points')
            imagepath = os.path.join('static','image'+'.png')
            plt.savefig(imagepath)
            plt.clf()
        else:
            a = plt.subplots(figsize = (20,7))
            a = df2.groupby(['Month','predict'], sort=False, as_index=False).agg(Rating=('Month','count'))
            a = sns.histplot(data = a ,x='Month', weights ='Rating' , hue='predict' , palette = palette , multiple = 'stack' , shrink = 0.8)
            #a.set_title('Tips by Day and Gender')
            a.set_ylabel('Number of Tweets')
            for p in a.patches:
                height = int(p.get_height())
                width = p.get_width()
                x = p.get_x()
                y = p.get_y()
                label_text = f'{height}'
                label_x = x + width / 2
                label_y = y + height / 2
                if height > 0:
                    a.text(label_x, label_y, label_text, ha='center', va='center', fontsize=12)
            imagepath = os.path.join('static','image'+'.png')
            plt.savefig(imagepath)
            plt.clf()


            
        if(len(list(month_count_all2.groups.keys())) == 1):
            b = plt.subplots(figsize = (20,7))
            
            b = sns.countplot(data = df3, x ='Month' , hue='predict' , palette=palette)
            b.legend(title='predict', bbox_to_anchor=(1, 1), loc='upper left')
            b.set_ylabel('Number of Tweets')
            for p in b.patches:             
                b.annotate(np.round(p.get_height(),decimals=2),(p.get_x()+p.get_width()/2., p.get_height()), ha='center',va='center',xytext=(0, 10),textcoords='offset points')
            imagepathCompare = os.path.join('static','imageCompare'+'.png')
            plt.savefig(imagepathCompare)
            plt.clf()
        else:
            b = plt.subplots(figsize = (20,7))
            b = df3.groupby(['Month','predict'], sort=False, as_index=False).agg(Rating=('Month','count'))
            b = sns.histplot(data = b ,x='Month', weights ='Rating' , hue='predict' , palette = palette , multiple = 'stack' , shrink = 0.8 )
            #b.set_title('Tips by Day and Gender')
            b.set_ylabel('Number of Tweets')
            for p in b.patches:
                height = int(p.get_height())
                width = p.get_width()
                x = p.get_x()
                y = p.get_y()
                label_text = f'{height}'
                label_x = x + width / 2
                label_y = y + height / 2
                if height > 0:
                    b.text(label_x, label_y, label_text, ha='center', va='center', fontsize=12)
            imagepathCompare = os.path.join('static','imageCompare'+'.png')
            plt.savefig(imagepathCompare)
            plt.clf()
        
    
    data = {"tweetCount":tweetcount,"tweetMainCount":tweetMainCount,"tweetCompareCount":tweetCompareCount,"image":imagepath,"imageCompare":imagepathCompare,"exampleTweet":example_list,"exampleTweet2":example_listCompare}
    return render_template("result_compare.html",data = data)

    

        

@app.route('/result')
def result():
    return render_template("result.html")

@app.route('/resultCompare')
def image():
    return render_template("result_compare.html")


if __name__ == "__main__":
    app.run()

