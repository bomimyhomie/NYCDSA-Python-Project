# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 20:14:44 2024

@author: vlad7
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns
plt.style.use('ggplot')

os.chdir('C:/Users/vlad7/NYCDSA-Python-Project/Raw Data')

#Import data files as dataframes.
df_customers = pd.read_csv('olist_customers_dataset.csv')
df_geolocation = pd.read_csv('olist_geolocation_dataset.csv')
df_states = pd.read_csv('BR_State_Abbrevs.csv')
df_order_items = pd.read_csv('olist_order_items_dataset.csv')
df_order_payments = pd.read_csv('olist_order_payments_dataset.csv')
df_order_reviews = pd.read_csv('olist_order_reviews_dataset.csv')
df_orders = pd.read_csv('olist_orders_dataset.csv')
df_products = pd.read_csv('olist_products_dataset.csv')
df_sellers = pd.read_csv('olist_sellers_dataset.csv')
df_product_translations = pd.read_csv('product_category_name_translation.csv')

#Rename state column.
df_customers.rename(columns={'customer_state': 'state'}, inplace=True)
df_sellers.rename(columns={'seller_state': 'state'}, inplace=True)

#Merge customers and state abbreviation dfs to get state names
df_customers = pd.merge(df_customers, df_states, on = 'state')
df_sellers = pd.merge(df_sellers, df_states, on = 'state')

#Merge products and product category translations to obtain english categories.
df_products = pd.merge(df_products, df_product_translations, on = 'product_category_name', how='left')

#Calculate total price/average review for each order as there are duplicate order IDs
df_order_items_price_agg = df_order_items.groupby('order_id').agg({'price': 'sum'}).reset_index()
df_order_reviews_avg = df_order_reviews.groupby('order_id').agg({'review_score': 'mean'}).reset_index()

#Merge order items and reviews
df_order_items = pd.merge(df_order_items, df_order_reviews_avg, on = 'order_id', how = 'left')

#Merge aggregate price, product name, and state data into the Orders dataframe.
df_order_items = pd.merge(df_order_items, df_products[['product_id', 'product_category_name_english']], on='product_id', how='left')
df_orders = pd.merge(df_orders, df_order_items_price_agg[['order_id', 'price']], on='order_id', how='left')
df_orders = pd.merge(df_orders, df_customers[['customer_id','state_name']], on = 'customer_id', how='left')
df_orders = pd.merge(df_orders, df_order_reviews_avg[['order_id','review_score']], on = 'order_id', how='left')

#Create order/deliver year, delivery time, and diff between estimate and actual delivery columns
df_orders['order_purchase_year'] = pd.to_datetime(df_orders['order_purchase_timestamp']).dt.year
df_orders['deliver_year'] = pd.to_datetime(df_orders['order_delivered_customer_date']).dt.year
df_orders['deliver_time'] = (pd.to_datetime(df_orders['order_delivered_customer_date']) - pd.to_datetime(df_orders['order_approved_at'])).dt.days
df_orders['estimate_delta'] = (pd.to_datetime(df_orders['order_delivered_customer_date']) - pd.to_datetime(df_orders['order_estimated_delivery_date'])).dt.days

#Group purchases
state_price_sum = df_orders.groupby(['state_name'])['price'].sum().reset_index().sort_values(by='price', ascending=False)
orders_by_state_year = df_orders.groupby(['state_name', 'order_purchase_year']).size().reset_index(name='order_count')

#Calculate average delivery by state and by state/year
delivery_by_state = df_orders.groupby(['state_name'])['deliver_time'].mean().reset_index()
delivery_by_state_year = df_orders.groupby(['state_name', 'deliver_year'])['deliver_time'].mean().unstack(fill_value=0).reset_index()

#Calculate number of orders and reviews
num_reviews = df_orders['review_score'].count()
num_orders = df_orders.shape[0]
percent_orders_with_reviews = num_reviews / num_orders
print(f'Percent of orders with reviews: {percent_orders_with_reviews:.2%}')

#Find distribution of customers by state for top 10 states.
customer_state_counts = df_customers['state_name'].value_counts()
customer_state_counts.head(10).sort_values(ascending=True).plot(kind='barh')
plt.title('Top 10 States by Customers')
plt.xlabel('State')
plt.ylabel('Customer Count')
plt.show()

#Find distribution of sellers by state for top 10 states.
seller_state_counts = df_sellers['state_name'].value_counts()
seller_state_counts.head(10).sort_values(ascending=True).plot(kind='barh')
plt.title('Top 10 States by Sellers')
plt.xlabel('State')
plt.ylabel('Seller Count')
plt.show()

#Find distribution of reviews
reviews = df_order_reviews['review_score'].value_counts()

ax = reviews.head(10).sort_values(ascending=True).plot(kind='bar', color='skyblue')
plt.title('Number of Reviews')
plt.xlabel('Review Score')
plt.ylabel('Number of Reviews')
plt.xticks(rotation=0)
plt.grid(False)
plt.gcf().set_facecolor('white')
ax.set_facecolor('white')
plt.show()

reviews.plot(kind='pie', figsize = (10,10), fontsize = 10, autopct='%1.1f%%')
plt.title('Distribution of Reviews')
plt.xlabel('')
plt.ylabel('')
plt.show()

#Filter out 'not_defined' payment types. Strip leading and trailing white space, replace underscore with blank space
df_order_payments['payment_type'] = df_order_payments['payment_type'].str.strip().str.title()
df_order_payments['payment_type'] = df_order_payments['payment_type'].str.replace('_', ' ')
df_order_payments = df_order_payments[df_order_payments['payment_type'] != 'not_defined']

df_order_items['product_category_name_english'] = df_order_items['product_category_name_english'].str.strip().str.title()
df_order_items['product_category_name_english'] = df_order_items['product_category_name_english'].str.replace('_', ' ')

#Find proportion of payment types
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'pink']
df_order_payments['payment_type'].value_counts().plot(kind='pie', colors=colors, figsize = (10,10), fontsize = 10, autopct='%1.1f%%')
plt.title('Proportion of Payment Types')
plt.ylabel('')
plt.xlabel('')
plt.show()

#Box plot of delivery times for each state
sns.boxplot(x='state_name', y='deliver_time', data=df_orders)
plt.title('Delivery Time by State')
plt.xlabel('State')
plt.ylabel('Delivery Time (Days)')
plt.xticks(rotation=90)
plt.grid(False)
plt.show()

#Box plot of differnce between delivery estimate and actual delivery times for each state
sns.boxplot(x='state_name', y='estimate_delta', data=df_orders)
plt.title('Delivery Estimate Delta by State')
plt.xlabel('State')
plt.ylabel('Actual Delivery Minus Estimate (Days)')
plt.xticks(rotation=90)
plt.grid(False)
plt.show()

#Calculate correlation between delivery delta and review score.
correlation = df_orders['estimate_delta'].corr(df_orders['review_score'])
corr_text = f'Pearson R: {correlation:.2f}'

sns.regplot(x='estimate_delta', y='review_score', data=df_orders, line_kws={'color': 'teal'},scatter_kws={'s': 10, 'alpha': 0.5})
plt.xlabel('Actual Delivery Minus Estimate (Days)')
plt.ylabel('Review Score')
plt.ylim(0, 10)
plt.xlim(-200,200)
plt.title('Review Score vs Actual Delivery Minus Estimate')
plt.grid(False)
plt.text(x=0.05, y=9.5, s=corr_text, fontsize=12, color='teal')
plt.show()

#Calculate correlation between delivery time and review score.
correlation2 = df_orders['deliver_time'].corr(df_orders['review_score'])
corr_text2 = f'Pearson R: {correlation2:.2f}'

sns.regplot(x='deliver_time', y='review_score', data=df_orders, line_kws={'color': 'green'},scatter_kws={'s': 10, 'alpha': 0.5})
plt.xlabel('Delivery Time')
plt.ylabel('Review Score')
plt.ylim(0, 10)
plt.title('Review Score vs. Delivery Time')
plt.grid(False)
plt.text(x=0.05, y=9.5, s=corr_text2, fontsize=12, color='teal')
plt.show()

#Calculate correlation between price and review score.
correlation3 = df_orders['price'].corr(df_orders['review_score'])
corr_text3 = f'Pearson R: {correlation3:.2f}'

sns.regplot(x='price', y='review_score', data=df_orders, line_kws={'color': 'purple'},scatter_kws={'s': 10, 'alpha': 0.5})
plt.xlabel('Price')
plt.ylabel('Review Score')
plt.ylim(0, 10)
plt.title('Review Score vs. Price Time')
plt.grid(False)
plt.text(x=0.05, y=9.5, s=corr_text3, fontsize=12, color='teal')
plt.show()

#Calculate number of orders and reviews for each product category
category_order_counts = df_order_items.groupby('product_category_name_english').size().reset_index(name='order_count')
category_review_counts = df_order_items.groupby('product_category_name_english')['review_score'].count().reset_index(name='review_count')
category_review_counts = pd.merge(category_review_counts, category_order_counts, on = 'product_category_name_english')
category_review_counts['percent_reviewed'] = category_review_counts['review_count'] / category_review_counts['order_count']
category_review_counts['percent_not_reviewed'] = 1 - category_review_counts['percent_reviewed']

#Plot top 25 number of orders by category
category_order_counts.sort_values(ascending=False, by = 'order_count').head(25).plot(kind='barh', x='product_category_name_english', y='order_count', color='orange', legend =  False)
plt.title('Top 25 Number of Orders by Category')
plt.xlabel('Number of Orders')
plt.ylabel('Product Category')
plt.xticks(rotation=0)
plt.grid(False)
plt.show()

#Plot bottom 25 number of orders by category
category_order_counts.sort_values(ascending=False, by = 'order_count').tail(25).plot(kind='barh', x='product_category_name_english', y='order_count', color='orange', legend =  False)
plt.title('Bottom 25 Number of Orders by Category')
plt.xlabel('Number of Orders')
plt.ylabel('Product Category')
plt.xticks(rotation=0)
plt.grid(False)
plt.show()

#Plot number of reviews by category
category_review_counts.sort_values(by='order_count', ascending=False).head(25).set_index('product_category_name_english')[['percent_reviewed', 'percent_not_reviewed']].plot(
    kind='barh', 
    stacked=True, 
    color=['blue', 'red'], 
    legend=False
)
plt.title('Top 25 Product Categories: Percentage of Orders Reviewed')
plt.xlabel('Percentage of Orders Reviewed(%)')
plt.ylabel('Product Category')
plt.xticks(rotation=0)
plt.gca().xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
plt.show()