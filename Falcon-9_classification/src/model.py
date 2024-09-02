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