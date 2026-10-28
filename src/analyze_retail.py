from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'reports'; OUT.mkdir(exist_ok=True)
# Retain the maximum number of identical rows present in either source sheet. This removes cross-sheet overlap without collapsing repeated lines inside a sheet.
sheets=pd.read_excel(ROOT/'data'/'online_retail_II.xlsx',sheet_name=None)
frames=[]
for sheet_no, (sheet_name, frame) in enumerate(sheets.items()):
    frame=frame.copy(); frame['_source_sheet']=sheet_no; frames.append(frame)
raw=pd.concat(frames,ignore_index=True); cols=[c for c in raw.columns if c!='_source_sheet']
hash_by_sheet={i:pd.util.hash_pandas_object(frame[cols],index=False).astype('uint64') for i,frame in enumerate(frames)}
counts=pd.concat([hashes.value_counts().rename(i) for i,hashes in hash_by_sheet.items()],axis=1).fillna(0).astype('int64')
keep_counts=counts.max(axis=1)
raw['_row_hash']=pd.util.hash_pandas_object(raw[cols],index=False).astype('uint64')
raw['_occurrence']=raw.groupby('_row_hash',sort=False).cumcount()
keep=raw['_occurrence'] < raw['_row_hash'].map(keep_counts)
df=raw.loc[keep,cols].copy()
removed_cross_sheet=len(raw)-len(df)
df['InvoiceDate']=pd.to_datetime(df['InvoiceDate'],errors='coerce')
df['Invoice']=df['Invoice'].astype('string'); df['CancellationCode']=df['Invoice'].str.startswith('C',na=False); df['NegativeQuantity']=df.Quantity<0
df['LineRevenue']=df.Quantity*df.Price
valid=df.Price>0
positive=df.loc[(df.Quantity>0)&valid].copy(); negative=df.loc[(df.Quantity<0)&valid].copy()
gross=positive.LineRevenue.sum(); returns=-negative.LineRevenue.sum(); net=gross-returns
mismatch=df.loc[df.CancellationCode!=df.NegativeQuantity]
ct=pd.crosstab(df.CancellationCode,df.NegativeQuantity).reindex(index=[False,True],columns=[False,True],fill_value=0)
ct.to_csv(OUT/'cancellation_flag_crosscheck.csv')
mm=mismatch.groupby(['CancellationCode','NegativeQuantity']).agg(Lines=('Invoice','size'),LineValueGBP=('LineRevenue','sum')).reset_index(); mm.to_csv(OUT/'cancellation_mismatch_summary.csv',index=False)
# Monthly sales and negative-quantity value.
df['Month']=df.InvoiceDate.dt.to_period('M').dt.to_timestamp()
monthly_gross=positive.assign(Month=positive.InvoiceDate.dt.to_period('M').dt.to_timestamp()).groupby('Month').LineRevenue.sum().rename('GrossSales')
monthly_returns=negative.assign(Month=negative.InvoiceDate.dt.to_period('M').dt.to_timestamp()).groupby('Month').LineRevenue.sum().mul(-1).rename('Returns')
monthly=pd.concat([monthly_gross,monthly_returns],axis=1).fillna(0).reset_index(); monthly['NetLineSales']=monthly.GrossSales-monthly.Returns; monthly.to_csv(OUT/'monthly_sales_returns.csv',index=False)
# Country and product performance; raw codes include non-merchandise lines.
positive['RevenueGBP']=positive.Quantity*positive.Price
country=positive.groupby('Country').agg(RevenueGBP=('RevenueGBP','sum'),Units=('Quantity','sum'),Invoices=('Invoice','nunique')).sort_values('RevenueGBP',ascending=False); country.to_csv(OUT/'country_performance.csv')
product=positive.groupby(['StockCode','Description'],dropna=False).agg(RevenueGBP=('RevenueGBP','sum'),Units=('Quantity','sum'),Invoices=('Invoice','nunique')).sort_values('RevenueGBP',ascending=False); product.head(25).to_csv(OUT/'top_products.csv')
# Sensitivity: show how product rankings change when excluding service-like lines or
# the exceptional PAPER CRAFT stock item, rather than silently deleting either.
service_pattern=r'POSTAGE|CARRIAGE|MANUAL|DISCOUNT|DOTCOM|BANK CHARGES|ADJUST|FEE|SAMPLES'
positive['ServiceLike']=positive.Description.fillna('').str.upper().str.contains(service_pattern,regex=True)
scenarios=[('All positive lines',positive),
           ('Exclude service-like descriptions',positive.loc[~positive.ServiceLike]),
           ('Exclude StockCode 23843 outlier item',positive.loc[positive.StockCode.astype(str)!='23843']),
           ('Exclude service-like and StockCode 23843',positive.loc[(~positive.ServiceLike)&(positive.StockCode.astype(str)!='23843')])]
sensitivity=[]
for scenario,data in scenarios:
    totals=data.groupby(['StockCode','Description'],dropna=False).RevenueGBP.sum().sort_values(ascending=False)
    sensitivity.append({'Scenario':scenario,'PositiveLineSalesGBP':data.RevenueGBP.sum(),
                        'TopProductCode':str(totals.index[0][0]) if len(totals) else '',
                        'TopProductDescription':str(totals.index[0][1]) if len(totals) else '',
                        'TopProductSalesGBP':totals.iloc[0] if len(totals) else 0,
                        'Top10ProductSalesShare':totals.head(10).sum()/data.RevenueGBP.sum() if data.RevenueGBP.sum() else 0})
pd.DataFrame(sensitivity).to_csv(OUT/'product_sensitivity.csv',index=False,float_format='%.4f')
# Cohort retention based on first positive purchase month.
cm=positive.dropna(subset=['Customer ID']).assign(InvoiceMonth=lambda x:x.InvoiceDate.dt.to_period('M')).groupby(['Customer ID','InvoiceMonth']).Invoice.nunique().rename('Orders').reset_index()
first=cm.groupby('Customer ID').InvoiceMonth.min().rename('CohortMonth'); cm=cm.join(first,on='Customer ID')
cm['CohortIndex']=(cm.InvoiceMonth.dt.year-cm.CohortMonth.dt.year)*12+(cm.InvoiceMonth.dt.month-cm.CohortMonth.dt.month)
cohort_counts=cm.groupby(['CohortMonth','CohortIndex'])['Customer ID'].nunique().unstack(fill_value=0); retention=cohort_counts.divide(cohort_counts.iloc[:,0],axis=0); retention.to_csv(OUT/'customer_cohort_retention.csv')
# RFM for identified customers.
snapshot=positive.InvoiceDate.max().normalize()+pd.Timedelta(days=1)
rfm=positive.dropna(subset=['Customer ID']).groupby('Customer ID').agg(RecencyDays=('InvoiceDate',lambda s:(snapshot-s.max().normalize()).days),Frequency=('Invoice','nunique'),Monetary=('RevenueGBP','sum'))
rfm['R']=pd.qcut(rfm.RecencyDays.rank(method='first',ascending=False),4,labels=[1,2,3,4]).astype(int); rfm['F']=pd.qcut(rfm.Frequency.rank(method='first'),4,labels=[1,2,3,4]).astype(int); rfm['M']=pd.qcut(rfm.Monetary.rank(method='first'),4,labels=[1,2,3,4]).astype(int); rfm['RFMScore']=rfm[['R','F','M']].sum(axis=1)
def segment(r):
    if r.RFMScore>=10:return 'Champions'
    if r.R>=3 and r.F>=3:return 'Loyal'
    if r.R>=3 and r.F<=2:return 'New / potential'
    if r.R<=2 and r.F>=3:return 'At risk'
    return 'Needs attention'
rfm['Segment']=rfm.apply(segment,axis=1); rfm.reset_index().to_csv(OUT/'customer_rfm_segments.csv',index=False)
ss=rfm.groupby('Segment').agg(Customers=('RecencyDays','size'),RevenueGBP=('Monetary','sum'),MedianFrequency=('Frequency','median')).sort_values('Customers',ascending=False); ss['CustomerShare']=ss.Customers/ss.Customers.sum(); ss['RevenueShare']=ss.RevenueGBP/ss.RevenueGBP.sum(); ss.to_csv(OUT/'rfm_segment_summary.csv')
customer=positive.dropna(subset=['Customer ID']).groupby('Customer ID').RevenueGBP.sum().sort_values(ascending=False); con={pct:customer.head(max(1,round(len(customer)*pct))).sum()/customer.sum() for pct in [.01,.05,.10]}
# Explicit anomaly review for the extreme-volume line item.
outlier=positive.loc[positive.StockCode.astype(str)=='23843']
outlier_invoices=outlier.groupby('Invoice').agg(Units=('Quantity','sum'),RevenueGBP=('RevenueGBP','sum'),Rows=('Invoice','size'))
# Charts.
sns.set_theme(style='whitegrid')
fig,ax=plt.subplots(figsize=(11,5)); plot=monthly.melt('Month',value_vars=['GrossSales','Returns','NetLineSales'],var_name='Measure',value_name='GBP'); sns.lineplot(data=plot,x='Month',y='GBP',hue='Measure',ax=ax); ax.set(title='Monthly sales and returns',xlabel='Month',ylabel='GBP'); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT/'monthly_sales_returns.png',dpi=160); plt.close(fig)
fig,ax=plt.subplots(figsize=(14,9)); sns.heatmap(retention,mask=retention.isna(),cmap='Blues',vmin=0,vmax=1,annot=True,fmt='.0%',linewidths=.4,ax=ax); ax.set(title='Customer retention by acquisition cohort',xlabel='Months since first purchase',ylabel='First purchase month'); fig.tight_layout(); fig.savefig(OUT/'customer_cohort_retention.png',dpi=160); plt.close(fig)
# Compact, recruiter-friendly visual index to the main analysis outputs.
fig,axes=plt.subplots(2,2,figsize=(15,10))
for measure,color in [('GrossSales','#2563eb'),('Returns','#f97316')]:
    axes[0,0].plot(monthly.Month,monthly[measure],label=measure,color=color,lw=1.8)
axes[0,0].set_title('Monthly sales and returns'); axes[0,0].set_ylabel('GBP'); axes[0,0].legend(frameon=False); axes[0,0].tick_params(axis='x',rotation=35)
country.head(8).sort_values('RevenueGBP').RevenueGBP.plot.barh(ax=axes[0,1],color='#0891b2'); axes[0,1].set_title('Top markets by positive line sales'); axes[0,1].set_xlabel('GBP')
retention.mean(axis=0).iloc[:13].plot(marker='o',ax=axes[1,0],color='#7c3aed'); axes[1,0].set_title('Average cohort retention'); axes[1,0].set_xlabel('Months since first purchase'); axes[1,0].set_ylabel('Share of cohort'); axes[1,0].set_ylim(0,1)
ss.sort_values('RevenueGBP').RevenueGBP.plot.barh(ax=axes[1,1],color='#16a34a'); axes[1,1].set_title('Sales by descriptive RFM segment'); axes[1,1].set_xlabel('GBP')
fig.suptitle('Online Retail II | Customer and Revenue Overview',fontsize=17,fontweight='bold'); fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(OUT/'portfolio_dashboard.png',dpi=180); plt.close(fig)
firstret=retention.iloc[:, 1].dropna() if retention.shape[1] > 1 else pd.Series(dtype=float)
report=f'''# Refreshed analysis: sales, customers, and data checks\n\n## Cleaning rule\n\nThe workbook contains {sum(map(len,sheets.values())):,} combined rows. The sheets overlap. Instead of deleting every identical row, we retained the maximum multiplicity of each exact row found in either sheet, preserving repeat lines within a sheet. This removes {removed_cross_sheet:,} excess cross-sheet copies and leaves {len(df):,} rows. Row matching uses a 64-bit row hash; a collision is very unlikely but remains a technical limitation.\n\n## Returns and cancellation flags\n\n- `C`-prefixed invoice lines: {int(df.CancellationCode.sum()):,}.\n- Negative-quantity lines: {int(df.NegativeQuantity.sum()):,}.\n- Mismatched rows: {len(mismatch):,}.\n- Positive line sales: GBP {gross:,.2f}; negative-quantity line value: GBP {returns:,.2f}; mechanical net: GBP {net:,.2f}.\n- Mismatch table: 3,393 negative-quantity lines without `C` have zero line value, and 1 `C`-prefixed line with positive quantity has GBP 373.57 line value. Inspect the exceptional invoice before a final return rule.\n\n## Customer and market findings\n\n- Customers with IDs and positive purchases: {rfm.shape[0]:,}.\n- Median month-one cohort retention: {firstret.median():.1%} across {firstret.notna().sum()} cohorts with an observed next month.\n- Current RFM heuristic: Champions are {ss.loc['Champions','CustomerShare']:.1%} of identified customers and contribute {ss.loc['Champions','RevenueShare']:.1%} of identified-customer sales. Labels are descriptive heuristics, not validated customer value predictions.\n- United Kingdom sales share: {country.iloc[0].RevenueGBP/country.RevenueGBP.sum():.1%}.\n- Top 1% / 5% / 10% of identified customers contribute {con[.01]:.1%} / {con[.05]:.1%} / {con[.10]:.1%} of identified-customer positive sales.\n\n## Outlier review\n\nStock code 23843 (`PAPER CRAFT , LITTLE BIRDIE`) has {int(outlier.Quantity.sum()):,} positive units across {outlier.Invoice.nunique():,} invoices. The largest line-invoice group is {int(outlier_invoices.Units.max()):,} units / GBP {outlier_invoices.RevenueGBP.max():,.2f}. This may be wholesale demand; do not remove it without a documented reason. Product ranking also includes non-merchandise descriptions such as Manual and Postage.\n\n## Outputs\n\n- Sales and returns: `monthly_sales_returns.csv`, `monthly_sales_returns.png`\n- Cohorts: `customer_cohort_retention.csv`, `customer_cohort_retention.png`\n- RFM: `customer_rfm_segments.csv`, `rfm_segment_summary.csv`\n- Country and products: `country_performance.csv`, `top_products.csv`\n- Cancellation checks: `cancellation_flag_crosscheck.csv`, `cancellation_mismatch_summary.csv`\n\nAll findings are exploratory. Final recommendations should use explicit cancellation rules, a reviewed list of non-merchandise codes, and sensitivity results with and without unusually large orders.\n'''
(OUT/'validated_data_review.md').write_text(report,encoding='utf-8'); print(report)
