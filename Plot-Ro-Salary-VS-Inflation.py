from cProfile import label
from numpy import true_divide
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
import re

# Read NET Average Earnings Data
df = pd.read_csv('net_monthly_average_earnings.csv')

### Need to sort values so that we have the info chronologically
months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
df['Month'] = pd.Categorical(df['Month'], categories=months, ordered=True)
df.sort_values(by=['Year', 'Month'], inplace=True)
df['Date'] =  df['Month'].astype('str') + df['Year'].astype('str')
df['Inflation'] = np.nan
df['EarningsIncrease'] = np.nan

### Reset DF index:
df.reset_index(drop=True, inplace=True)

# Read Inflation Data
infl = pd.read_csv('Inflation.csv')

# Cross match and insert inflation into the main DataFrame: 
for inflationDate in infl['Date']:
        df.loc[df['Date'] == inflationDate, 'Inflation'] = float(infl[infl['Date'] == inflationDate]['Inflation'])

# Calculate the salary increase (yearly, to overlap with inflation data):
for index in range(11, len(df)):
        if df.loc[index, 'Month'] == 'December':
                if df.loc[index, 'Date'] == 'December1991':
                        # The first situation is a bit different as we do not have data for December1990
                        salary_delta = df.loc[index, 'Earnings'] - df.loc[index - 11, 'Earnings']
                        salary_percentage_increase = salary_delta * 100 / df.loc[index - 11, 'Earnings']
                        df.loc[index, 'EarningsIncrease'] = salary_percentage_increase
                elif df.loc[index, 'Date'] == 'December2005':
                        # For December2004 - December2005 we handle differently due to ROL->RON change:
                        salary_delta = df.loc[index, 'Earnings'] - (df.loc[index - 12, 'Earnings'] / 10000)
                        salary_percentage_increase = salary_delta * 100 / df.loc[index - 12, 'Earnings']
                        df.loc[index, 'EarningsIncrease'] = salary_percentage_increase
                else: 
                        # Regular calculation:
                        salary_delta = df.loc[index, 'Earnings'] - df.loc[index - 12, 'Earnings']
                        salary_percentage_increase = salary_delta * 100 / df.loc[index - 12, 'Earnings']
                        df.loc[index, 'EarningsIncrease'] = salary_percentage_increase


# Split df into 2 sets (ROL and RON)
ROL = df[df['Year'] < 2005]
ROL['Earnings'].fillna(method='ffill', inplace=True)
RON = df[df['Year'] >= 2005]
RON['Earnings'].fillna(method='ffill', inplace=True)

#region Start plot for ROL:
fig, ax = plt.subplots(nrows=2, ncols=1)
fig.suptitle('Evolution of avg NET salary in Romania (ROL and RON)')
fig.subplots_adjust(hspace=0.5)

ax[0].plot('Date', 'Earnings', data=ROL, color='black', linestyle='-', label='NET Income')
xticks = ticker.MaxNLocator(nbins=40)
ax[0].xaxis.set_major_locator(xticks)
ax[0].xaxis.set_tick_params(rotation=30)
ax[0].ticklabel_format(axis='y', style='plain')
ax[0].set_title("Avg salary before ROL -> RON change")

# Annotate the first and last value:
ax[0].annotate(f"{ROL.iloc[0]['Date']}: {ROL.iloc[0]['Earnings']} ROL", xy=(ROL.iloc[0]['Date'], ROL.iloc[0]['Earnings']), 
                xytext=(ROL.iloc[0]['Date'], ROL.iloc[0]['Earnings'] + 3000000), arrowprops=dict(facecolor='red'))
ax[0].annotate(f"{ROL.iloc[-1]['Date']}: {ROL.iloc[-1]['Earnings']} ROL", xy=(ROL.iloc[-1]['Date'], ROL.iloc[-1]['Earnings']), 
                xytext=(ROL.iloc[-48]['Date'], ROL.iloc[-1]['Earnings'] - 500000), arrowprops=dict(facecolor='green'))

ax[0].set_ylabel('Avg NET salary [ROL]')
# Put some stats on graph: 
# earnings_delta = ROL.iloc[-1]['Earnings'] - ROL.iloc[0]['Earnings']
# percentage_increase = earnings_delta * 100 / ROL.iloc[0]['Earnings']
# years = ROL.iloc[-1]['Year'] - ROL.iloc[0]['Year']
# avg_yearly_increase = percentage_increase / years
# ax[0].text(x=ROL.iloc[int(len(ROL)/2)]['Date'], y=ROL['Earnings'].max() - 1500000, 
#        s=f"-Years: {years} \n-Increase: {int(percentage_increase)} %\n-Avg Increase:{int(avg_yearly_increase)} % / year")

ax2nd = ax[0].twinx()
ax2nd.plot(ROL['Date'], ROL['Inflation'], 'o-', color='red', label='Inflation', alpha=0.4)
ax2nd.plot(ROL['Date'], ROL['EarningsIncrease'], 'o', color='blue', label='EarningsIncrease', alpha=0.4)
ax2nd.set_ylabel('Inflation & Earnings Increase [%]')
ax[0].grid()
ax[0].legend()
ax2nd.legend(loc='right')
#endregion

#region start plot for RON
ax[1].plot('Date', 'Earnings', data=RON, linestyle='-', color='black')
ax[1].xaxis.set_major_locator(xticks)
ax[1].xaxis.set_tick_params(rotation=30)
ax[1].ticklabel_format(axis='y', style='plain')
ax[1].set_title("Avg salary after ROL -> RON change")

# Annotate the starting and ending value
ax[1].annotate(f"{RON.iloc[0]['Date']}: {RON.iloc[0]['Earnings']} RON", xy=(RON.iloc[0]['Date'], RON.iloc[0]['Earnings']), 
                xytext=(RON.iloc[0]['Date'], RON.iloc[0]['Earnings'] + 350), arrowprops=dict(facecolor='red'))
ax[1].annotate(f"{RON.iloc[-1]['Date']}: {RON.iloc[-1]['Earnings']} RON", xy=(RON.iloc[-1]['Date'], RON.iloc[-1]['Earnings']), 
                xytext=(RON.iloc[-60]['Date'], 3000), arrowprops=dict(facecolor='green', alpha = 0.5))
earnings_delta = RON.iloc[-1]['Earnings'] - RON.iloc[0]['Earnings']

# Print some stats:
# percentage_increase = earnings_delta * 100 / RON.iloc[0]['Earnings']
# years = RON.iloc[-1]['Year'] - RON.iloc[0]['Year']
# vg_yearly_increase = percentage_increase / years
#ax[1].text(x=RON.iloc[int(len(RON)/2)]['Date'], y=RON['Earnings'].max() - 500, 
#        s=f"-Years: {years} \n-Increase: {int(percentage_increase)} %\n-Avg Increase:{int(avg_yearly_increase)} % / year")
ax[1].grid()
ax[1].set_ylabel('Avg NET salary [RON]')

ax3rd = ax[1].twinx()
ax3rd.plot(RON['Date'], RON['Inflation'], color='red', label='Inflation', marker='o', alpha=0.4)
ax3rd.plot(RON['Date'], RON['EarningsIncrease'], 'o', color='blue', label='EarningsIncrease', alpha=0.4)
ax2nd.set_ylabel('Inflation & Earnings Increase [%]')

ax[1].legend()
ax3rd.legend(loc='right')

#


plt.show()


"""
MAKE IT EASIER:
- Split the DF into 2 DFs (easier to search for min and max)
- Plot them sepparately as now
- Plot arrows, annotations, etc

"""