
# BC4: Cryptocurrency Dashboard


## General Context

This dashboard has been developed for a university course, and its main 
aim it's to help the user with making the best decisions for trading 
with cryptocurrencies.
It uses real time data, downloaded mainly using yfinance library.
In the file requirements.txt it's possible to see all libraries needed
to run the file. 
The dashboard has been deployed also online, and it's possible
to see it using this link: https://crypto-dashboard-group-i.onrender.com
It is preferable however to download the code and run it due to the 
low RAM allocation present in the free trial in render.com
The dashboard contains three main sectors: the first one is the leaderboard, 
containing informations and visualization about 20 different coins.
It is possible to select the time interval to create this leaderboard.
The second part contains the technical analysis for a single coin;
it is possible to select the coin, the time range and the indicators 
to be shown.
The last part contains price predictions for two days in the future and an
indicator that suggests the best strategy (buy/sell/keep).
It is important to point out the volatility of this market, and
the difficulty of predicting such prices: for this reason, invest only after 
having a good knowledge of the market. This dashboard should be an 
addictional tool and not a magic money generator.


## Business Situation

Warner Buffer and Gil Bates, partners of Investments4Some, after looking into
the work you did during your last project, decided to hire you once again.
They are asking you to develop a dashboard for their financial analysts.
However, they expect a flexible dashboard, that fetches daily updated data
about any arbitrary financial asset. They expect to use this dashboard to
inform the investment decisions of their internal financial team and external
stakeholders.

Your client expects you to create a dashboard that will be available for as
many assets as possible. They prefer to have a generalistic dashboard to
analyse and compare any type of asset. However, if the latter is not possible,
they would like to get (as a fallback) a dashboard primarily focused on the
cryptocurrencies used in the last project.
