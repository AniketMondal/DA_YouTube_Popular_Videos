[a]:#youtube-popular-videos-analysis
[b]:YouTube_Popular_Videos_Analysis_1.ipynb
[c]:YouTube_Popular_Videos_Analysis_2.ipynb


# YouTube Popular Videos Analysis

This project tries to extract insights and patterns of YouTube's current most popular videos of a specific region (Country; here INDIA). 
Over **20** important attributes of each video is analyzed using **Pandas, NumPy,** etc. and insights are presented in vizualizations
using **Matplotlib** and **Seaborn**.

This project starts with understanding the resources, methods, request parameters, structure of requested data, etc.
for **YouTube Data API v3**. Then, for robust analysis, there is a need of **Database** to store data, collected at different timestamps over a long period
(like 1 month or more).
Here, I have explored the opportunity of using a **Cloud Database**, levaraging the benefits of
**Google Cloud Platform** *( using its free-tier/always-free products only!! )*.
I utilized their **Compute Engine** as virtual machine to install and set-up the database (*NOTE: The Cloud SQL of GCP is not included in the free tier*).

This analysis may help anyone strategize their YouTube journey by understanding
**user preferences, current trends,** improvement scopes etc.

## Outline

- [Some Vizualizations](#some-vizualizations)
- [Required Pyhton libraries and modules](#required-pyhton-libraries-and-modules)
- [Setting-up Compute Engine on Google Cloud Platform](#setting-up-compute-engine-on-google-cloud-platform)
- [Setting-up PostgreSQL on Compute Engine](#setting-up-postgresql-on-compute-engine)
- [Creating Firewall rule for VM](#creating-firewall-rule-for-vm)
- [Enabling YouTube Data API v3](#enabling-youtube-data-api-v3)
- [Understanding YouTube Data API v3](#understanding-youtube-data-api-v3)
- [Storing all credentials as Environment Variables](#storing-all-credentials-as-environment-variables)
- [Data Transformation for efficient memory usage](#data-transformation-for-efficient-memory-usage)
    - [Transformed Columns](#transformed-columns)
        - [](#)
        - [](#)
        - [](#)
        - [](#)
- [Method used to efficiently load data into Database](#method-used-to-efficiently-load-data-into-database)
- [Interacting with Database](#interacting-with-database)
- [Closing Database Connections](#closing-database-connections)
- [](#)
- [](#)

## Some Vizualizations

![Live-Stream vs Uploaded](popular_vid_type.png)
![Shorts vs Normal vs Long](duration_tag_counts.png)
![Correlation Heatmap](correlation.png)
![Peak Hour for publishing Videos](peak_hour.png)

**[Go back :top:][a]**

## Required Pyhton libraries and modules

Install with your python package manager, ex.- **pip**, if not already installed,
as these need to be imported. Like - `pip install package_name`.
- datetime
- dotenv
    ```shell
    pip install python-dotenv
    ```
- io
- matplotlib
- numpy
- os
- pandas
- pprint
- psycopg2
- random
- requests
- seaborn

**[Go back :top:][a]**

## Setting-up Compute Engine on Google Cloud Platform

You first need a google billing account and a normal google account ( *which can be same* ). But don't worry, as Google will **not** charge anything if you are within limits.
Also, turn off the auto payments of your billing account so that even if you cross free usage limits,
you will not be charged ( *your service will be terminated if you don't pay* ).

Then go to [Google Cloud Console](https://console.cloud.google.com/)
by logging in with the google account and create a new project. Then go to **Compute Engine** and create a new VM instance.
You will need to add the billing account here.
While choosing the right specifications, follow this [free tier usage limits](https://cloud.google.com/free/docs/gcp-free-tier/#compute)
to avoid any billing.

For any further guides or queries, please follow Google's
[Documentation](https://cloud.google.com/compute/docs).

**[Go back :top:][a]**

## Setting-up PostgreSQL on Compute Engine

Please follow the detailed
[Google Cloud Community Tutorial](https://cloud.google.com/community/tutorials/setting-up-postgres)
contributed by Google employees to set up a PostgreSQL database in your virtual machine
and configure it for remote connections.

**Note:** The guide uses CIDR suffix `/32`, which means a single IPV4 address.
Which is OK for static ip addresses.
But it is most likely that you have dynamic ip address and for that you need
to identify right CIDR suffix by knowing the subnet mask of your network.
Ex.- For 255.255.255.0 types, it should be `/24`.

**[Go back :top:][a]**

## Creating Firewall rule for VM

Now, in order to remotely connect with VM and then the database, we need to create a firewall rule on our compute engine. The previous [Tutorial](https://cloud.google.com/community/tutorials/setting-up-postgres) includes that but here also, remember to replace the CIDR suffix with the right one as applicable.

**[Go back :top:][a]**

## Enabling YouTube Data API v3

From the navigation menu of google cloud console, go to **APIs & Services**. Then follow the path below:

**Library** :arrow_forward: **YouTube Data API v3** :arrow_forward: **Enable**

Now from the dashboard, you need to create **Credentials** for the API as the **API Key** is required. Note that the usage of this API is free with limitation / ***Quota*** of **1000** units per day. And our each API call costs **1** unit.

**[Go back :top:][a]**

## Understanding YouTube Data API v3

One really needs to understand the different methods of the call, calling parameters and the description of output parameters to implement what is intended. For this, please refer to the **Guides** and **Reference** section of [Official Documentation](https://developers.google.com/youtube/v3).

Here, we can play around with all the parameters ( *check hidden parameters also!* ) without spending our daily quotas. One can also see what the response will look like and verify whether the API call was right or incomplete/wrong. The response data will generally be in a nested **JSON** format.

After ensuring the all the parameters are set properly and the call is giving back response with status code 200, you need to choose **SHOW CODE** and grab the **https** URL, automatically generated against your specified parameters. For more info about setting parameters, and slicing parts of some parameters, please follow
[this guide](https://developers.google.com/youtube/v3/getting-started#partial)

In this project, the region is set to **IN** which is the ISO 3166-1 alpha-2 code for my country **India**. But you can change it to any other country code as [acceptable](https://developers.google.com/youtube/v3/docs/i18nRegions) by YouTube, by simply changing the variable `region_code` in [1st Notebook][b]. Also, I have collected 100 videos ( *50 videos in 2 times each* ) although there could be more videos available, upto 200. The process to extract all of them using **loop** is explained in [1st Notebook][b].

**[Go back :top:][a]**

## Storing all credentials as Environment Variables

So, we have to use few credentials for the entire project. These includes your API key for pulling data and database credentials for connecting to the cloud database. These are secrets and should not be published in public. Also, it is better, **not** to hard code these variables, following one of the [12-factor](http://12factor.net/) principles.

Python `dotenv` library provides a good solution. It reads key-value pairs from a `.env` file and can set them as environment variables. Then we can directly use `os.getenv()` to get the environment variables.

This repository contains a sample [.env file](.env_example) which provides a template for the `.env` key-value pairs. Please insert the actual values and then remove the *'_example'* part from the name of the file.

For more info and advanced configuration, please [visit here](https://pypi.org/project/python-dotenv/).

**[Go back :top:][a]**

## Data Transformation for efficient memory usage

After normalizing `JSON` data using `pandas.json_normalize()`, we need to drop redundant columns after extracting useful information from them. Then applying appropriate datatypes we can achieve around **50%** reduced memory usage per column ( *as there is need for additional data wrangling which changes the no. of columns* ) . This is because, `pandas` often store data as objects and our data is mostly in string format even for numeric columns. Also declaring proper categorical column helps a lot!

This might not be that useful in our situation but it is implemented for scalability. Also, we are using the fastest `copy_from(StringIO,...)`  method to load data into database. But it uses high memory proportional to the memory usage of the `DataFrame`. So it is better to perform **data transformation** which also makes possible to run a quick analysis on the small recently collected data if required.

The same is done extensively on the [2nd Notebook][c], as we will be analyzing much bigger dataset ( *currently **5000** rows* ), collected from our database.

**[Go back :top:][a]**

## Method used to efficiently load data into Database

There are many methods to load a `DataFrame` into a database but not all perform the same way.
One should **not** use any loops and execute one insert query at a time unless absolute necessary, as this is highly inefficient/slow. Now for bulk inserts, there are multiple options available. As the no. of rows in our `DataFrame` increases, the performance varries greatly.

![Performance Graph](benchmark-1.png)

Here are two great articles ( **[Article-1](https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/), [Article-2](https://hakibenita.com/fast-load-data-python-postgresql)** ) that provide detailed comparison between these methods and the code template for each method. I used one of the *fastest* methods here. Though fastest, this method is not highly memory efficient. Our data transformation will help us in this regard and also there is an excellent work-around mentioned in **[Article-2](https://hakibenita.com/fast-load-data-python-postgresql)**.

**[Go back :top:][a]**

## Interacting with Database

The `psycopg2` wrapper provides `connection` ( *[doc](https://www.psycopg.org/docs/connection.html)* ) and `cursor` ( *[doc](https://www.psycopg.org/docs/cursor.html)* ) classes to execute SQL commands, queries from the python code in a database session.

We also need to follow PostgreSQL [documentation](https://www.postgresql.org/docs/current/index.html), to understand its extention to the standard SQL. Like, declaring `enum` datatypes, inserting arrays as values, acceptable time-zone aware timestamp datatype formats, timedelta/interval formats etc.

**[Go back :top:][a]**

## Closing Database Connections

After executing SQL queries, we need to `commit` for the changes to take effect in the database. Also, if there occurs any error while executing SQL queries, the transaction will be aborted and all commands will be ignored until you use `rollback`.

It is important to close `cursor()`s after completing interactions with the database for safety reasons. Finally, the `connection()` should also be closed.

**[Go back :top:][a]**

## Transformed Columns

Here are the description of few DataFrame columns transformed from the raw data.

### (Title/Audio)_Language_Name
Obtained by matching language codes from the API response data of YouTube's **[I18nLanguages](https://developers.google.com/youtube/v3/docs/i18nLanguages)**. In some cases, the code provided by the owner is **not listed** in the API response though the code is valid. But as we are specifically analyzing YouTube related data, 
it has not been decoded going outside the defined scope.

Now for all such cases ( *e.g. bihari dialects, explicitely mentioned **zxx*** ), the code has been changed to `zxx` which according to [ISO639](https://iso639-3.sil.org/code/zxx) stands for **Not Applicable**.

**[Go back :top:][a]**

### Topics
Converted from: ***Topics_Links :arrow_right: Topics***

The API response contains the **Links** of wikipedia pages for specific topics. The name of the topic has been extracted from the **Topics_Llinks** and joined into a comma seperated string for easier insertion into database

**[Go back][a]**:top:

### Entry_Timestamp

### 1. hola
1. Hello
2. Hi
### 2. arigato
he he not bad
### 3. nice g
