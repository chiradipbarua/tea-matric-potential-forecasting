"""Figure scripts; empirical values are read from aggregate CSV tables.

No logger records, forecast paths or experiment metric values are embedded here.
"""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Rectangle
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

BLUE='#2569A5'; ORANGE='#D96A29'; INK='#263746'; GREEN='#447A5A'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,
 'axes.titlesize':10,'legend.fontsize':8.5,'xtick.labelsize':8.5,'ytick.labelsize':8.5,
 'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})

def export(fig,directory,name):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    for suffix in ['pdf','svg','png','tiff']:
        options={'dpi':600} if suffix in ['png','tiff'] else {}
        if suffix=='tiff':options['pil_kwargs']={'compression':'tiff_lzw'}
        fig.savefig(directory/(name+'.'+suffix),bbox_inches='tight',pad_inches=.06,**options)
    plt.close(fig)

def arrow(ax,a,b,color=INK,lw=1):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,color=color,lw=lw))

def card(ax,xy,w,h,title,body,colour=BLUE):
    x,y=xy
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.009,rounding_size=.015',
      facecolor='#F5F7F8',edgecolor='#C7D0D7',lw=.8))
    ax.text(x+.025,y+h-.055,title,fontsize=9.3,fontweight='bold',color=colour,va='top')
    ax.text(x+.025,y+h-.14,body,fontsize=7.7,color=INK,va='top',linespacing=1.4)

def application_context(out):
    fig=plt.figure(figsize=(7.1,3.1));gs=fig.add_gridspec(1,3,wspace=.21)
    axes=[fig.add_subplot(gs[0,i]) for i in range(3)]
    for ax in axes:ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    a,b,c=axes
    for ax,label,title in zip(axes,['a','b','c'],['Measure soil conditions','Forecast matric potential','Assess new drying onset']):
        ax.text(0,1.01,label,fontweight='bold',fontsize=11,color=INK)
        ax.text(.09,1.01,title,fontsize=9,fontweight='bold',color=INK)
    # Schematic tea canopy and two sensors. Horizontal distances are not surveyed.
    a.add_patch(Rectangle((.02,.12),.96,.51,facecolor='#F5EEE4',edgecolor='none'))
    a.plot([.02,.98],[.63,.63],color='#8D7E65',lw=1)
    a.plot([.49,.49],[.63,.82],color='#745A40',lw=2)
    for x,y,angle in [(.33,.85,25),(.48,.9,-5),(.65,.84,-25),(.43,.81,15),(.58,.8,-10)]:
        a.add_patch(Ellipse((x,y),.29,.14,angle=angle,facecolor=GREEN,edgecolor='white',lw=.6))
    a.text(.08,.68,'Tea bush',fontsize=8,color=GREEN)
    for y,x,lab,dep in [(.48,.34,'P3','5 cm'),(.24,.65,'P5','20 cm')]:
        a.plot([.08,.9],[y,y],ls=':',lw=.6,color='#AAA095')
        a.scatter([x],[y],s=42,color=BLUE,zorder=3)
        a.text(x+.07,y,lab,va='center',fontsize=8,fontweight='bold',color=INK)
        a.text(.04,y-.07,dep,fontsize=8,color=INK)
    a.text(.5,.025,'Two depths in each plot',ha='center',fontsize=8.3,color=INK)
    b.text(.5,.82,'Hourly target',ha='center',fontsize=9,color=INK)
    b.text(.5,.67,r'$\psi_t=(\psi_{P3,t}+\psi_{P5,t})/2$',ha='center',fontsize=11,color=BLUE)
    b.plot([.05,.95],[.4,.4],lw=1,color=INK)
    for x,h in zip([.2,.5,.8],[24,48,72]):
        b.scatter(x,.4,s=27,color=BLUE,zorder=4);b.text(x,.3,f'{h} h',ha='center',fontsize=8.5)
    b.text(.5,.14,'Point forecasts and\npointwise intervals',ha='center',va='center',fontsize=8.5,linespacing=1.5,color=INK)
    c.text(.5,.81,'Operational threshold',ha='center',fontsize=9,color=INK)
    c.text(.5,.65,'−100 kPa',ha='center',fontsize=15,color=ORANGE,fontweight='bold')
    c.plot([.12,.88],[.48,.48],color=ORANGE,ls='--',lw=1.1)
    c.text(.5,.34,'Currently above threshold',ha='center',fontsize=8.2,color=INK)
    arrow(c,(.5,.29),(.5,.22),color=ORANGE)
    c.text(.5,.12,'Forecast a sustained\nthreshold crossing',ha='center',va='center',fontsize=8.5,linespacing=1.5,color=INK)
    fig.subplots_adjust(top=.88,bottom=.07,left=.025,right=.99)
    export(fig,out,'CEA-Figure-1-Application-context')

def workflow(out):
    fig,ax=plt.subplots(figsize=(7.1,4.55));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    ax.text(.005,.975,'a',fontweight='bold',fontsize=11,color=INK)
    ax.text(.04,.975,'Chronological partitions',fontweight='bold',fontsize=10,color=INK)
    stages=[(.025,BLUE,'Training','4 Dec 2023–16 May 2025\nFitting; blocked rolling folds'),
            (.365,GREEN,'Validation','25 Aug–30 Sep 2025\nSelection; interval expansion'),
            (.705,ORANGE,'Locked test','1 Oct–21 Nov 2025\nCommon eligible origins')]
    for x,col,title,body in stages:card(ax,(x,.69),.27,.22,title,body,col)
    arrow(ax,(.307,.8),(.346,.8));arrow(ax,(.647,.8),(.686,.8))
    ax.text(.5,.642,'Validation is shared by model selection and post-hoc calibration',ha='center',fontsize=8,color=INK)
    ax.text(.005,.565,'b',fontweight='bold',fontsize=11,color=INK)
    ax.text(.04,.565,'Forecast comparison',fontweight='bold',fontsize=10,color=INK)
    card(ax,(.025,.2),.20,.29,'Prepare records','Sensor provenance\nFault quarantine\nValid hourly contexts',INK)
    # Three branches share the same eligible origin keys, not identical information.
    branches=[(.414,'Local baselines','Model-specific inputs and fitting',GREEN),
              (.286,'Frozen foundation models','336-h target history; no local fitting',BLUE),
              (.158,'Chronos-2 LoRA','336-h target history; local adaptation',ORANGE)]
    for y,title,body,col in branches:
        ax.add_patch(FancyBboxPatch((.31,y),.38,.105,boxstyle='round,pad=.008,rounding_size=.01',facecolor='#F5F7F8',edgecolor='#CAD3DA',lw=.7))
        ax.text(.325,y+.073,title,fontsize=8.7,fontweight='bold',color=col,va='center')
        ax.text(.325,y+.027,body,fontsize=7.5,color=INK,va='center')
        ax.plot([.265,.265],[.21,.466],color='#84939D',lw=.7)
        arrow(ax,(.265,y+.05),(.303,y+.05),lw=.7)
        ax.plot([.729,.729],[.21,.466],color='#84939D',lw=.7)
        ax.plot([.698,.729],[y+.05,y+.05],color='#84939D',lw=.7)
    ax.plot([.233,.265],[.345,.345],color='#84939D',lw=.7)
    arrow(ax,(.729,.345),(.77,.345),lw=.7)
    card(ax,(.78,.2),.195,.29,'Evaluate','Point errors\nInterval scores\nNew-onset alerts\nHydrologic strata',INK)
    ax.text(.5,.065,'Common endpoints • 24, 48 and 72 h • Dependence-aware uncertainty',ha='center',fontsize=8,color=INK)
    fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.01)
    export(fig,out,'CEA-Figure-3-Evaluation-workflow')

def coverage_width(frame,out):
    f=frame[(frame.model=='Chronos-2 LoRA')&(frame.block_hours==72)]
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.45));handles=[]
    for ax,metric,title,ylabel,factor in zip(axes,['coverage','width'],['a  Pointwise coverage','b  Interval width'],['Coverage (%)','Mean width (kPa)'],[100,1]):
        for variant,label,col,marker in [('raw','Raw',BLUE,'o'),('validation_expanded','Validation-expanded',ORANGE,'s')]:
            g=f[(f.metric==metric)&(f.interval==variant)].sort_values('horizon_h')
            if len(g)!=3:raise ValueError('Expected exactly three horizons per interval and metric')
            y=g.value.to_numpy()*factor;lo=g.lower.to_numpy()*factor;hi=g.upper.to_numpy()*factor
            ax.errorbar(g.horizon_h,y,yerr=np.vstack([y-lo,hi-y]),color=col,marker=marker,lw=1.4,markersize=4.6,capsize=3,elinewidth=.9,label=label)
        ax.set_title(title,loc='left',pad=9,fontweight='bold');ax.set_xlabel('Forecast horizon (h)');ax.set_ylabel(ylabel)
        ax.set_xticks([24,48,72]);ax.set_xlim(21,75);ax.grid(axis='y',color='#DBE0E4',lw=.55);ax.set_axisbelow(True)
    axes[0].axhline(80,color='#707070',ls=(0,(4,3)),lw=1)
    axes[0].set_ylim(0,102);axes[1].set_ylim(bottom=0)
    handles=[Line2D([0],[0],color=BLUE,marker='o',lw=1.4,label='Raw'),Line2D([0],[0],color=ORANGE,marker='s',lw=1.4,label='Validation-expanded'),Line2D([0],[0],color='#707070',ls='--',lw=1,label='Nominal 80% coverage')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,1.02),ncol=3,frameon=False,columnspacing=1.6,handlelength=2.3)
    fig.subplots_adjust(top=.8,left=.085,right=.99,bottom=.16,wspace=.32)
    export(fig,out,'CEA-Figure-6-Coverage-and-width')

def alert_f1(frame,out):
    f=frame[(frame.block_hours==72)&(frame.metric=='F1')&(frame.rule=='q10_path')&(frame.setting=='default')]
    fig,ax=plt.subplots(figsize=(6.5,3.7));x=np.arange(3);width=.31
    for k,(model,label,col) in enumerate([('Chronos-2','Chronos-2',BLUE),('Chronos-2 LoRA','Chronos-2 LoRA',ORANGE)]):
        g=f[f.model==model].sort_values('horizon_h')
        if len(g)!=3:raise ValueError('Expected three horizon rows per model')
        y=g.value.to_numpy();lo=g.lower.to_numpy();hi=g.upper.to_numpy()
        xx=x+(k-.5)*width
        ax.bar(xx,y,width,color=col,label=label,zorder=3)
        ax.errorbar(xx,y,yerr=np.vstack([y-lo,hi-y]),fmt='none',ecolor=INK,capsize=3,lw=.9,zorder=4)
    ax.set_xticks(x,['24','48','72']);ax.set_xlabel('Forecast horizon (h)');ax.set_ylabel('New-onset warning F1');ax.set_ylim(0,1.03);ax.set_yticks(np.arange(0,1.01,.2));ax.set_xlim(-.6,2.6)
    ax.grid(axis='y',color='#DBE0E4',lw=.55);ax.set_axisbelow(True)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),ncol=2,frameon=False,columnspacing=2,handlelength=1.5)
    fig.subplots_adjust(top=.79,left=.12,right=.99,bottom=.15)
    export(fig,out,'CEA-Figure-7-New-episode-alert-F1')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--coverage-csv',type=Path);p.add_argument('--alert-csv',type=Path);a=p.parse_args()
    application_context(a.output_dir);workflow(a.output_dir)
    if a.coverage_csv:coverage_width(pd.read_csv(a.coverage_csv),a.output_dir)
    if a.alert_csv:alert_f1(pd.read_csv(a.alert_csv),a.output_dir)
