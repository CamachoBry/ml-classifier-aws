#Imports
import numpy as np
import pandas as pd

#Importing the dataset from Sci-kit learn
from sklearn import datasets

#Iris dataset can be loaded directly from sklearn or imported as csv 
#for DataFrame manipulation; chose through csv to see data better
data = pd.read_csv('./IRIS.csv')
# data.head(10)

#Data columns
data_columns = data.columns
# print(data_columns)



#Dividing the dataset into X and Y
#Attribute data
X = data.drop(['species'], axis=1)

#Label/target data
y = data['species']



#Split the data set
from sklearn.model_selection import train_test_split

#Splits the X and y data into training and testing for prediction analysis
#%60 training - %40 testing
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.4, random_state=10)

#Building the models
#There are two models that can be used here: DecisionTree and KNeighbors
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

#Instatiate DTC
dtc = DecisionTreeClassifier()
#Fit training data to the model
dtc.fit(X_train, y_train)
#Predict using test data
dtc_predictions = dtc.predict(X_test)


#Instantiating KNC
knc = KNeighborsClassifier()
#Fit training data to KNC
knc.fit(X_train, y_train)
#Predict using test data
knc_predictions = knc.predict(X_test)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score


print('---------------Decision Tree Model-----------------------')
print('Accuracy score:', accuracy_score(y_test, dtc_predictions))
print('CFM: \n', confusion_matrix(y_test, dtc_predictions))
print('Classification Report: \n', classification_report(y_test, dtc_predictions))

print('---------------KNeighbors Model-----------------------')
print('Accuracy score:', accuracy_score(y_test, knc_predictions))
print('CFM: \n', confusion_matrix(y_test, knc_predictions))
print('Classification Report: \n', classification_report(y_test, knc_predictions))

