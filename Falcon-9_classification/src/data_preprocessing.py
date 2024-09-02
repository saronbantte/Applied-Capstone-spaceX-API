# -*- coding: utf-8 -*-
"""Space X Falcon 9 First Stage Landing Prediction .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1o5goOeA1hOmFvGyutolxwpxI9yKn18zP
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, log_loss, f1_score

def plot_confusion_matrix(y, y_hat):
  from sklearn.metrics import confusion_matrix
  cm=confusion_matrix(y,y_hat)
  sns.heatmap(cm,annot=True)
  plt.xlabel('predicated')
  plt.ylabel('actual')
  plt.title('confusion_matrix')
  plt.xticks(ticks=[0, 1], labels=['Did Not Land', 'Land'])
  plt.yticks(ticks=[0, 1], labels=['Did Not Land', 'Land'])
  plt.show()

data=pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_1.csv")
data.head()

"""Create a landing outcome label from outcome column."""

landing_outcomes=data['Outcome'].value_counts()
landing_outcomes

"""Anything that starts with True is a successful mission and with false and none is unsuccessful mission."""

for i,outcome in enumerate(landing_outcomes.keys()):
    print(i,outcome)

bad_outcomes=set(landing_outcomes.keys()[[1,3,5,6,7]])
landing_class=[]
for outcome in data['Outcome']:
  if outcome in bad_outcomes:
    landing_class.append(0)
  else:
    landing_class.append(1)
data['Class']=landing_class
data.head()

"""EDA and Preparing data Feature Engineering.

Now let's do some data analysis:
looking at the FlightNumber indicating the continous launch attempts and varaibales that would affect the launch outcome.

Payload vs FlightNumber
"""

sns.scatterplot(x='FlightNumber', y= 'PayloadMass',hue='Class', data= data )
plt.xlabel('FlightNumber')
plt.ylabel('PayloadMass')
plt.title('Payload vs FlightNumber')
plt.show()

"""The plot shows as the flightnumber increases, the first stage is more likely to land successfully. Looking at the payload mass as it increases, the less likely the first stage to land successfully.

Compare the success rates of different launch sites.
"""

sns.barplot(x='LaunchSite', y='FlightNumber', hue='Class', data =data)
plt.xlabel('LauchSite')
plt.ylabel('FlightNumber')
plt.title('Compare the success rates of different launch sites')
plt.show()

"""There is a major difference in the success rate of these launch sites. The VAFB SLC 4E has the lowest faliur of landing.

The relationship between playloadMass and LaunchSites
"""

sns.catplot(x='PayloadMass', y='LaunchSite',hue='Class', data=data)
plt.xlabel(' Payload')
plt.ylabel('Launch site ')
plt.title('The relationship between Payload and launch site')

"""observed form the data Payload Vs. Launch Site scatter point chart we see  for the VAFB-SLC launchsite there are no rockets launched for heavypayload mass(greater than 10000).

The success rate sof each orbits.
"""

success_rate= data.groupby(['Orbit'])['Class'].mean()*100
orbit_success=pd.DataFrame(success_rate).reset_index()
orbit_success.columns=['orbit', 'success_rate']
orbit_success.head()
plt.barh(orbit_success['orbit'], orbit_success['success_rate'])
plt.xlabel('Success Rate(%)')
plt.ylabel('Orbit')
plt.title('The success rate of each orbit')
plt.show()

"""Four of the given orbits have a 100 % success rate. The orbit SO has 0% success rate.

The relationship between flight number and orbit type.
"""

sns.catplot(x='FlightNumber', y='Orbit', hue='Class', data=data)
plt.xlabel('FlightNumber')
plt.ylabel('Orbit')
plt.title('The relationship between flight number and orbit type')
plt.show()

"""Looking at the LEO orbit the success appears to be related to the flight number; on the other hand, there seems the flight number has no raltionship with orbit type when in orbit GTO."""

sns.scatterplot(x='PayloadMass', y='Orbit',hue= 'Class', data=data)
plt.xlabel('Payload')
plt.ylabel('Orbit')
plt.title('The relationship between Payload and Orbit')

"""When looking at the orbits LEO and ISS there are successful landings with heavy playloads. But for GTO it is hard to distinguish since there are both successful and failed missions around the same payload."""

year=[]
for i in data['Date']:
  year.append(i.split("-")[0])
data['Date']=year

data.head()

"""Find the annual landing success rate."""

success_rate=data.groupby(['Date'])['Class'].mean()*100
year_success=pd.DataFrame(success_rate).reset_index()
year_success.columns=['year', 'success_rate']
year_success.head()

sns.lineplot(x='year', y= 'success_rate', data=year_success)
plt.xlabel('Year')
plt.ylabel('Success Rate(%)')
plt.title('The annual landing success rate')

"""This graph shows there is a consistent increase in the landing success rate of the Falcon 9 throughout the years.

Prepare the data for model traning.

1, dealing with missing data.

2, convert all categorical data to numeric data using encoders.

3, scaling features
"""

data.isnull().sum()

"""I will drop the landing pad column all values are the same and it is numerical value."""

data.drop(['LandingPad'], axis=1, inplace=True)

data.dtypes

from sklearn.preprocessing import OneHotEncoder
OHE=OneHotEncoder(sparse_output=False, drop='first')
for cols in data.columns:
  if data[cols].dtype in ['object', 'bool']:
    transformed_cols=OHE.fit_transform(data[[cols]])
    transformed_cols=pd.DataFrame(transformed_cols, columns=OHE.get_feature_names_out())
    data.drop(cols, axis=1, inplace=True)
    data=pd.concat([data, transformed_cols], axis=1)
data.head()

data.columns

data.dtypes

"""build models and train"""

features, target= data.drop(['Class'], axis=1), data['Class']

train_x, test_x, train_y,test_y= train_test_split(features, target, test_size=0.2,random_state=42 )

scaler=StandardScaler()
train_x=scaler.fit_transform(train_x)
test_x=scaler.transform(test_x)

"""Logistic regression"""

param_grid={'C':[0.01, 0.1, 1, 10], 'penalty': ['l2'], 'solver':['lbfgs'],'max_iter': [200]}
LR=LogisticRegression()
LR_cv=GridSearchCV(LR, param_grid= param_grid, cv=5 , scoring='accuracy')
LR_cv.fit(train_x, train_y)
LR_cv.best_params_
best_LR = LR_cv.best_estimator_
y_hat=best_LR.predict(test_x)
plot_confusion_matrix(test_y, y_hat)
LR_accuracy=accuracy_score(test_y, y_hat)*100
print('The accuracy is ', LR_accuracy, '%')

"""Try KNN"""

param_grid={'n_neighbors': [ 2, 3, 4, 5, 6, 7, 8, 9,10],
            'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
            'p': [1,2]}
KNN=KNeighborsClassifier()
KNN_cv=GridSearchCV(KNN,param_grid=param_grid, cv=5, scoring='accuracy')
KNN_cv.fit(train_x, train_y)
print(KNN_cv.best_params_)
best_KNN=KNN_cv.best_estimator_
y_hat=best_KNN.predict(test_x)
plot_confusion_matrix(test_y, y_hat)
KNN_accuracy=accuracy_score(test_y, y_hat)*100
print('The accuracy is ', KNN_accuracy, '%')

from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier()
rf_cv = GridSearchCV(estimator=rf, param_grid={'n_estimators': [10, 50, 100]}, cv=5, scoring='accuracy')
rf_cv.fit(train_x, train_y)

rf_best = rf_cv.best_estimator_
yhat_rf = rf_best.predict(test_x)
rf_accuracy = accuracy_score(test_y, yhat_rf) * 100
print('Random Forest accuracy: ', rf_accuracy, '%')
plot_confusion_matrix(test_y, yhat_rf)

accuracy_list={'Logistic Regression': LR_accuracy, 'RFC': rf_accuracy, 'KNN': KNN_accuracy}
accuracy_list=pd.DataFrame(list(accuracy_list.items()), columns=['model', 'accuracy'])
accuracy_list

sns.barplot(x='model', y='accuracy', data=accuracy_list)
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.title('Model Accuracy')

"""Comparing all the giving models, LogistRegression has the highest accuracy of 94.44% and KNNeigbor has the lowest accuracy of 83.33%.

The main objective of this project is to be able to classify  Space X Falcon 9 launch first landing success based on important factors like the orbit, payload mass, flight number and launch sites.

Using the LogisticRegrssion model we can tell if Space X Falcon launch first landing will be successful or not with 94.4% accuracy.
"""

import joblib
joblib.dump(best_LR, 'model.pkl')