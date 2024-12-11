# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 20:14:44 2024

@author: vlad7
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

#Merge products product category translations to obtain english categories.
df_products = pd.merge(df_products, df_product_translations, on = 'product_category_name')

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

#Filter out 'not_defined' payment types.
df_order_payments['payment_type'] = df_order_payments['payment_type'].str.strip().str.lower()
df_order_payments = df_order_payments[df_order_payments['payment_type'] != 'not_defined']
#Find proportion of payment types
df_order_payments['payment_type'].value_counts().plot(kind='pie', figsize = (10,10), fontsize = 10, autopct='%1.1f%%')
plt.title('Proportion of Payment Types')
plt.ylabel('')
plt.xlabel('')
plt.show()

#Merge order_items, products on product_id
df_order_items = pd.merge(df_order_items, df_products[['product_id', 'product_category_name_english']], on='product_id', how='left')

#merge orders and customers on order_id
df_orders = pd.merge(df_orders, df_customers[['state_name']], on = 'customer_id', how='left')




