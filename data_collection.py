import os
import random
import requests
import numpy as np
import pandas as pd
import psycopg2 as spg
from io import StringIO
from pprint import pprint
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
api_key = os.getenv("API_KEY")

region_code = "IN"
url1 = ("https://youtube.googleapis.com/youtube/v3/videos?"
       "key="+api_key+
       "&part=snippet%2CcontentDetails%2Cstatistics%2Cstatus%2CliveStreamingDetails%2CtopicDetails"
       "&chart=mostPopular"
       "&maxResults=50"
#      "&pageToken="  This token value is not required for the 1st call, we will update it later for each subsequent api calls.
       "&regionCode="+region_code+
       "&fields="
                "items("
                       "id%2C%20"
                       "snippet(publishedAt%2C%20channelId%2C%20title%2C%20channelTitle%2C%20tags%2C%20categoryId%2C%20defaultLanguage%2C%20defaultAudioLanguage)%2C%20"
                       "contentDetails(duration%2C%20definition%2C%20caption)%2C%20"
                       "status(embeddable%2C%20madeForKids)%2C%20"
                       "statistics(viewCount%2C%20likeCount%2C%20dislikeCount%2C%20commentCount)%2C%20"
                       "topicDetails%2FtopicCategories%2C%20"
                       "liveStreamingDetails(actualStartTime%2CactualEndTime%2CscheduledStartTime%2CscheduledEndTime%2CconcurrentViewers))%2C%20"
                "nextPageToken%2C%20"
                "pageInfo"
)

data1 = requests.get(url1).json()
page2_token = data1["nextPageToken"]
url2 = url1+"&pageToken="+page2_token
data2 = requests.get(url2).json()

current_timestamp = pd.Timestamp.utcnow()
current_timestamp

data = data1["items"]+data2["items"]

temp_df = pd.json_normalize(data)

df = pd.DataFrame(columns=["Entry_Timestamp","Video_ID","Title","Channel_Name","Channel_ID","Published_At",
                           "Title_Language","Audio_Language","Duration","Quality","Views","Likes","Dislikes",
                           "Comments","Live_Start_Real","Live_End_Real","Live_Start_Scheduled","Live_End_Scheduled",
                           "Live_Viewers","CC","Tags","Category_ID","Embeddable","Made_for_Kids","Topic_Links"])

temp_df = temp_df.rename(columns={
                                    'id':'Video_ID',
                                    'snippet.publishedAt':'Published_At','snippet.channelId':'Channel_ID','snippet.title':'Title',
                                    'snippet.channelTitle':'Channel_Name', 'snippet.tags':'Tags', 'snippet.categoryId':'Category_ID',
                                    'snippet.defaultAudioLanguage':'Audio_Language', 'contentDetails.duration':'Duration',
                                    'contentDetails.definition':'Quality', 'contentDetails.caption':'CC',
                                    'status.embeddable':'Embeddable', 'status.madeForKids':'Made_for_Kids', 'statistics.viewCount':'Views',
                                    'statistics.likeCount':'Likes', 'statistics.dislikeCount':'Dislikes',
                                    'statistics.commentCount':'Comments', 'topicDetails.topicCategories':'Topic_Links',
                                    'liveStreamingDetails.actualStartTime':'Live_Start_Real',
                                    'liveStreamingDetails.actualEndTime':'Live_End_Real',
                                    'liveStreamingDetails.scheduledStartTime':'Live_Start_Scheduled', 'snippet.defaultLanguage':'Title_Language'
})

df = df.append(temp_df,ignore_index=True)

df["Entry_Timestamp"] = current_timestamp

df1 = df.copy()

def count_tags(lst):
    if type(lst) is list:
        return len(lst)
    elif lst is np.nan:
        return pd.NA
    else:
        print(lst,type(lst),'This Tag item is not a list or NaN', sep='\n')

df.insert(df.columns.get_loc("Tags")+1,"No_of_Tags", df["Tags"].apply(count_tags))

def list_to_text(lst):
    if type(lst) is list:
        return ("{"+"}, {".join([i for i in lst])+"}")
    elif lst is np.nan:
        return pd.NA
    else:
        print(lst,type(lst),'This Tag item is not a list or NaN', sep='\n')

df["Tags"] = df["Tags"].apply(list_to_text)

def get_links(lst):
    if type(lst) is list:
        return (", ".join([i.replace("https://en.wikipedia.org/wiki/","") for i in lst]))
    elif lst is np.nan:
        return pd.NA
    else:
        print(lst,type(lst),'This Topic_Links item is not a list or NaN', sep='\n')

df["Topics"] = df["Topic_Links"].apply(get_links)

df.insert(0,"Rank",range(1,101))

df.drop(columns=["Topic_Links"],inplace=True)

df["Published_At"]          = pd.to_datetime(df["Published_At"],errors="coerce",utc=True)
df["Live_Start_Real"]       = pd.to_datetime(df["Live_Start_Real"],errors="coerce",utc=True)
df["Live_End_Real"]         = pd.to_datetime(df["Live_End_Real"],errors="coerce",utc=True)
df["Live_Start_Scheduled"]  = pd.to_datetime(df["Live_Start_Scheduled"],errors="coerce",utc=True)
df["Live_End_Scheduled"]    = pd.to_datetime(df["Live_End_Scheduled"],errors="coerce",utc=True)

lang_url = "https://youtube.googleapis.com/youtube/v3/i18nLanguages?part=snippet&prettyPrint=true&fields=items%2Fsnippet&key="+api_key
lang_data = requests.get(lang_url).json()
lang_df = pd.json_normalize(lang_data["items"])
lang_df.columns = ["Language_Code","Language"]
lang_df = lang_df.convert_dtypes()

temp_df = df[["Title_Language"]].merge(lang_df,how="left",left_on="Title_Language",right_on="Language_Code")["Language"]
df.insert(df.columns.get_loc("Title_Language")+1,"Title_Language_Name",temp_df)
temp_df = df[["Audio_Language"]].merge(lang_df,how="left",left_on="Audio_Language",right_on="Language_Code")["Language"]
df.insert(df.columns.get_loc("Audio_Language")+1,"Audio_Language_Name",temp_df)

df.loc[(df["Title_Language"].notnull()) & (df["Title_Language_Name"].isnull()),["Title_Language"]] = "zxx"
df.loc[(df["Title_Language"].notnull()) & (df["Title_Language_Name"].isnull()),["Title_Language_Name"]] = "Not Applicable"
df.loc[(df["Audio_Language"].notnull()) & (df["Audio_Language_Name"].isnull()),["Audio_Language"]] = "zxx"
df.loc[(df["Audio_Language"].notnull()) & (df["Audio_Language_Name"].isnull()),["Audio_Language_Name"]] = "Not Applicable"

df = df.convert_dtypes()

df["Duration"] = df["Duration"].apply(pd.Timedelta)

df["CC"] = df["CC"].map({"true":True,"false":False})

df.loc[:,"Views":"Comments"] = df.loc[:,"Views":"Comments"].astype("Int64")
df["No_of_Tags"] = df["No_of_Tags"].astype("UInt16")

df["Live_Viewers"] = df["Live_Viewers"].astype("UInt32")
df["Rank"] = df["Rank"].astype("UInt8")

df["Quality"] = df["Quality"].astype('category')
df.loc[:,"Title_Language":"Audio_Language_Name"] = df.loc[:,"Title_Language":"Audio_Language_Name"].astype('category')
df["Category_ID"] = df["Category_ID"].astype('category')

host_name = os.getenv("HOST_NAME")
db_name = os.getenv("DB_NAME")
port = os.getenv("PORT")
user_name = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")

try:
    connection = spg.connect(host=host_name, database=db_name, port=port, user=user_name, password=password)
except spg.OperationalError as error:
    raise error
else:
    print("Successfully connected to the PostgreSQL database!")

cursor = connection.cursor()

create_table = ("""CREATE TABLE IF NOT EXISTS 
                   YT_POPULAR_VIDEOS (
                      
                      RANK                   SMALLINT     NOT NULL,
                      ENTRY_TIMESTAMP        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      VIDEO_ID               VARCHAR(255) NOT NULL,
                      TITLE                  VARCHAR(255) NOT NULL,
                      CHANNEL_NAME           VARCHAR(255) NOT NULL,
                      CHANNEL_ID             VARCHAR(255) NOT NULL,
                      PUBLISHED_AT           TIMESTAMPTZ  NOT NULL,
                      TITLE_LANGUAGE         LANG,
                      TITLE_LANGUAGE_NAME    LANG_NAME,
                      AUDIO_LANGUAGE         LANG,
                      AUDIO_LANGUAGE_NAME    LANG_NAME,
                      DURATION               INTERVAL,
                      QUALITY                QUALITY      NOT NULL,
                      VIEWS                  BIGINT,
                      LIKES                  BIGINT,
                      DISLIKES               BIGINT,
                      COMMENTS               BIGINT,
                      LIVE_START_REAL        TIMESTAMPTZ,
                      LIVE_END_REAL          TIMESTAMPTZ,
                      LIVE_START_SCHEDULED   TIMESTAMPTZ,
                      LIVE_END_SCHEDULED     TIMESTAMPTZ,
                      LIVE_VIEWERS           INTEGER,
                      CC                     BOOLEAN,
                      TAGS                   TEXT,
                      NO_OF_TAGS             INTEGER,
                      CATEGORY_ID            VARCHAR(255),
                      EMBEDDABLE             BOOLEAN,
                      MADE_FOR_KIDS          BOOLEAN,
                      TOPICS                 VARCHAR(255),

                      CONSTRAINT PK_VID_ENTRY PRIMARY KEY (VIDEO_ID,ENTRY_TIMESTAMP)
                   );
                
                """)

try:
   cursor.execute(create_table)
   cursor.execute("COMMIT")
except (Exception, spg.DatabaseError) as error:
    print(f"Following error(s) occured : {error}")
    cursor.execute("ROLLBACK")

buffer = StringIO()
df.to_csv(buffer, sep="\t", header=False, index=False) 
buffer.seek(0)
try:
    cursor.copy_from(buffer,'yt_popular_videos',sep="\t",null="")
    cursor.execute("COMMIT")
except (Exception, spg.DatabaseError) as error:
    print(f"Following error(s) occured : {error}")
    cursor.execute("ROLLBACK")

cursor.close()
connection.close()