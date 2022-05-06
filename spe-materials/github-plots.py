#!/usr/bin/env python

import matplotlib as mpl
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['figure.figsize'] = 20,12
mpl.rcParams['savefig.bbox'] = 'tight'

fontsize_base = 20
rez = 200

# colors from https://colorbrewer2.org/#type=diverging&scheme=RdBu&n=6
colors = ['#b2182b','#ef8a62','#fddbc7','#d1e5f0','#67a9cf','#2166ac']
color_grey = '#969595ff'

import matplotlib.pyplot as plt
plt.style.use('seaborn-deep')

from matplotlib.ticker import MaxNLocator

import pandas as pd
from datetime import date
from os.path import join

# load data exported from WPD
datapath = './figures/'
fname_positive = 'github-data-extract_positive-delta.csv'
fname_negative = 'github-data-extract_negative-delta.csv'

def df_date_loader(datapath, fname):
    with open(join(datapath,fname)) as f:
        df = pd.read_csv(f, names=['date','value'], parse_dates=[0])

    # sort by the dates so that line chart points are ordered correctly
    return df.sort_values('date')

df_positive = df_date_loader(datapath,fname_positive)
df_negative = df_date_loader(datapath,fname_negative)

fig,ax = plt.subplots()
ax.plot(df_positive['date'],df_positive['value'],color=colors[-1])
ax.fill_between(df_positive['date'],df_positive['value'],color=colors[-1])
ax.plot(df_negative['date'],df_negative['value'],c=colors[0])
ax.fill_between(df_negative['date'],df_negative['value'],color=colors[0])

dates = df_positive['date']

# manually add two dates to make the x-ticks even
dates.loc[len(dates)] = date(2020,7,10)
dates.loc[len(dates)] = date(2020,7,3)
dates = dates.sort_values()

ax.set_xticks(dates[0::3])
ax.set_xlim([dates.iloc[0],dates.iloc[len(dates)-1]])

ylim_base = min(df_negative['value'])
ylim_delta = 100
ylim_min = ylim_base - ylim_delta
ylim_max = abs(ylim_base) + ylim_delta

ax.set_ylim([ylim_base - ylim_delta, abs(ylim_base) + ylim_delta])
plt.xticks(fontsize=fontsize_base+4)
plt.yticks(fontsize=fontsize_base+4)

# demarcate regions corresponding to phase 0,1,2
diagramstart = date(2020,6,19)
phase1start = date(2020,8,14)
phase2start = date(2020,9,7)
phase2end = date(2020,10,20)

alpha = 0.1
plt.axvspan(dates[0], phase1start , alpha=alpha, label='Phase 0', color=colors[0],zorder=0)
plt.axvspan(phase1start, phase2start, alpha=alpha, label='Phase 1', color=color_grey,zorder=0)
plt.axvspan(phase2start, phase2end, alpha=alpha, label='Phase 2', color=colors[-1],zorder=0)

# calculate x-axis date positions of the plt.text labels
phase0_label_date = diagramstart + (phase1start - diagramstart)/2 
phase1_label_date = phase1start + (phase2start - phase1start)/2
phase2_label_date = phase2start + (phase2end - phase2start)/2

# mark labels in the center of the phases
bbox_dict = dict(boxstyle='square', facecolor='white', edgecolor='black')
plt.text(phase0_label_date, abs(ylim_base)-50, 'Phase 0', fontsize=fontsize_base+8, color=colors[0],va='center',ha='center',ma='center',bbox=bbox_dict)
plt.text(phase1_label_date, abs(ylim_base)-50, 'Phase 1', fontsize=fontsize_base+8, color=color_grey,va='center',ha='center',ma='center',bbox=bbox_dict)
plt.text(phase2_label_date, abs(ylim_base)-50, 'Phase 2', fontsize=fontsize_base+8, color=colors[-1],va='center',ha='center',ma='center',bbox=bbox_dict)

plt.xlabel('Date',fontsize=fontsize_base+8)
plt.ylabel('Lines of code changed',fontsize=fontsize_base+8)
plt.grid()

# save the figure with good resolution
fpath = '/home/bfc5288/MEGAsync/psu/scimma/SNEWS/writeup/figures'
fname = "snews2-code-delta.png"

plt.savefig(join(fpath, fname), dpi=rez)
plt.show()
plt.close()

## plot per-phase data of commits, issues, epics
phase = [0,1,2]
phase_strings = ['Phase 0','Phase 1', 'Phase 2']

# commit, issue, and PR data were extracted from SNEWS2.0 Github data
commits = [11,29,26]
issues = [0,4,3]
prs = [0,5,8]

# agile metrics (epics, stories created and completed) were extracted from private Github project board
epics = [0,5,6]
stories = [0,10,29]
stories_done = [0,8,15]

fig,ax = plt.subplots()

labels = ['Commits','Issues closed','Pull requests merged','Epics','Stories created','Stories completed']
data = [commits,issues,prs,epics,stories,stories_done]

# compute the x-adjustment factor to ensure the bars don't overlap
width = 0.1
factor = len(data)
i = -2.5 * factor
num_bars = len(data)
x_delta = width/num_bars

for c,l,y in zip(colors,labels,data):
    x_shift = [i*x_delta]*len(phase)
    x = [x_shift[idx]+phase[idx] for idx in range(len(phase))]
    if sum(y) == 0:
        continue
    plt.bar(x, y, width=width, color=c, label=l)
    i += 1 * factor

plt.xticks(phase,phase_strings,fontsize=fontsize_base+4)
plt.yticks(fontsize=fontsize_base+4)
plt.legend(fontsize=fontsize_base+4,loc='upper left')

plt.ylabel('Count',fontsize=fontsize_base+8)

# save the figure with proper resolution
fpath = '/home/bfc5288/MEGAsync/psu/scimma/SNEWS/writeup/figures'
fname = "snews2-agile-metrics.png"

plt.savefig(join(fpath, fname), dpi=rez)
plt.show()
plt.close()
