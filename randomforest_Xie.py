# -*- coding: utf-8 -*-
"""“Biohack-Yijia”

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jT3GS3psxIa9WcNXK-gc8veqBWnhLx4c
"""

import pandas as pd
from sklearn.utils import shuffle
import numpy as np
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

"""## 1. Check the number of wildtype porteins in single and multiple mutation files"""

## "single_protein_name.csv" and "multiple_protein_name.csv" from preprocessing from excel
single_protein_name = pd.read_csv("single_protein_name.csv", sep=",")
single_protein_name["name2"] = single_protein_name["name2"].str.replace(r"rd[1-3]_", "")

single_number = single_protein_name.drop_duplicates(subset="name2", keep='first', inplace=False)
single_protein = list(single_number["name2"])
print(len(single_protein))  ## 14 proteins

multiple_protein_name = pd.read_csv("multiple_protein_name.csv", sep=",")
multiple_number = multiple_protein_name.drop_duplicates(subset="protein name", keep='first', inplace=False)
multiple_protein = list(multiple_number["name2"])
print(len(multiple_protein))  ## 1830 proteins

set(single_protein) & set(multiple_protein)  ## No intersection

"""##2. Convert protein sequence and secondary structure to "two" hot vector"""

# see feng's py file

"""## 3. Prepare data"""

multi_train = pd.read_csv('twohot_multi.csv')
single_train = pd.read_csv('twohot_single.csv')
all_train = pd.concat([multi_train, single_train])

cleaned_train = all_train.dropna(axis=0,how='any')

shuffled_train = shuffle(cleaned_train)
shuffled_train.to_csv("shuffled_train.csv")

"""## 4. Random forest"""

shuffled_train = pd.read_csv('shuffled_train.csv')
shuffled_train = shuffled_train.drop(columns=['Unnamed: 0'])

train_data = shuffled_train.sample(n=30165, random_state= 1)  ## 80% training set
test_data = pd.concat([shuffled_train, train_data]).drop_duplicates(keep=False) ## 20% test set
Xtrain = train_data.iloc[:, 1:-1].values
Ytrain = train_data.iloc[:, -1].values

Xtest = test_data.iloc[:, 1:-1].values
Ytest = test_data.iloc[:, -1].values
Ytest_mean = np.mean(Ytest)

"""### 4.1 Grid Search 
Too slow for Random Forest
"""

# tuned_parameters = [{
#     'n_estimator': np.arrange(1,1000,100),
#     'max_depth': np.arange(10,100,10),
#     'max_features': np.arange(10,100,10)
#     }]
#
# grid = GridSearchCV(RandomForestRegressor(random_state = 0), tuned_parameters, scoring= "neg_mean_squared_error", cv = 5)
# grid.fit(Xtrain, Ytrain)
# print("The best parameters are %s with a score of %f" % (grid.best_params_, grid.best_score_))
#
# #CV grid-search --> mean(mse) and std(mse)
# means = grid.cv_results_['mean_test_score']
# stds = grid.cv_results_['std_test_score']
# for mean, std, params in zip(means, stds, grid.cv_results_['params']):
#   print("%f (+/-%0.03f) for %r" % (mean, std * 2, params))

"""### 4.2 n-estimator"""

def RFtrain(estimator=100, features="auto", depth=None):
  start = time.time()
  regressor = RandomForestRegressor(n_estimators = estimator, random_state = 0, max_features = features, max_depth = depth)
  # n_estimators: numbers of trees
  regressor.fit(Xtrain, Ytrain)
  Ypredict = regressor.predict(Xtest)
  correlation_score = np.corrcoef(Ytest, Ypredict)[0, 1]
  default_score = regressor.score(Xtest,Ytest)
  mse_score = ((Ypredict - Ytest_mean)**2).sum()/len(Ytest)
  end = time.time()
  print(end-start)
  return correlation_score, default_score, mse_score

correlation_score1, default_score1, mse_score1 = RFtrain(1)
correlation_score10, default_score10, mse_score10 = RFtrain(10)
correlation_score50, default_score50, mse_score50 = RFtrain(50)  # 0.6571767364779161  0.29949460633418323 time: 274.3146183490753
correlation_score100, default_score100, mse_score100 = RFtrain(100)  # 0.6603234014542797 0.6603234014542797 time: 482.1012399196625
correlation_score1000, default_score1000, mse_score1000 = RFtrain(1000) # 0.6651540556166624 0.2976998820370932 time: 4874.61915397644

"""### 4.3 max_features"""

# max_features
mse_scores_feature = []
default_scores_feature = []
correlation_scores_feature = []
for i in range(1,90,1):
  start = time.time()
  regressor = RandomForestRegressor(n_estimators=50, random_state=0, max_features=i)
  regressor.fit(Xtrain, Ytrain)
  Ypredict = regressor.predict(Xtest)
  correlation_score = np.corrcoef(Ytest, Ypredict)[0,1]
  default_score = regressor.score(Xtest,Ytest)
  mse_score = ((Ypredict - Ytest_mean)**2).sum()/len(Ytest)
  default_scores_feature.append(default_score)
  mse_scores_feature.append(mse_score)
  correlation_scores_feature.append(correlation_score)
  end = time.time()
  print(end-start)

print(max(correlation_scores_feature),([*range(1,90,1)][correlation_scores_feature.index(max(correlation_scores_feature))]))
print(max(mse_scores_feature),([*range(1,90,1)][mse_scores_feature.index(max(mse_scores_feature))]))
print(max(default_scores_feature),([*range(1,90,1)][default_scores_feature.index(max(default_scores_feature))]))
plt.figure(figsize=[20,5])
# plt.plot(range(1,90,1),mse_scores_feature, label = "MSE score", color="red")
plt.plot(range(1,90,1),default_scores_feature, label = "default score", color="blue")
plt.plot(range(1,90,1),correlation_scores_feature, label = "correlation score", color="green")
plt.legend(loc="upper right")
plt.show()

"""### 4.4 max_depth"""

# max_depth
mse_scores_depth = []
default_scores_depth = []
correlation_scores_depth = []
for i in range(1,50,1):
  start = time.time()
  regressor = RandomForestRegressor(n_estimators = 50, random_state = 0, max_features = 84, max_depth = i)
  regressor.fit(Xtrain, Ytrain)
  Ypredict = regressor.predict(Xtest)
  correlation_score = np.corrcoef(Ytest, Ypredict)[0,1]
  default_score = regressor.score(Xtest,Ytest)
  mse_score = ((Ypredict - Ytest_mean)**2).sum()/len(Ytest)
  correlation_scores_depth.append(correlation_score)
  default_scores_depth.append(default_score)
  mse_scores_depth.append(mse_score)
  end = time.time()
  print(end-start)

print(max(correlation_scores_depth),([*range(1,50,1)][correlation_scores_depth.index(max(correlation_scores_depth))]))
print(max(mse_scores_depth),([*range(1,50,1)][mse_scores_depth.index(max(mse_scores_depth))]))
print(max(default_scores_depth),([*range(1,50,1)][default_scores_depth.index(max(default_scores_depth))]))
plt.figure(figsize=[20,5])
# plt.plot(range(1,50,1),mse_scores_depth, label = "MSE score", color="red")
plt.plot(range(1,50,1),default_scores_depth, label = "default score", color="blue")
plt.plot(range(1,50,1),correlation_scores_depth, label = "correlation score", color="green")
plt.legend(loc="upper right")
plt.show()

"""### 4.5 n-estimator check"""

correlation_score60, default_score60, mse_score60 = RFtrain(60, 84, 40)
correlation_score70, default_score70, mse_score70 = RFtrain(70, 84, 40)


"""### Final model: n_estimators = 60, max_features = 84, max_depth = 40"""

start = time.time()
regressor = RandomForestRegressor(n_estimators = 60, random_state = 0, max_features = 84, max_depth = 40)
regressor.fit(Xtrain, Ytrain)
Ypredict = regressor.predict(Xtest)
correlation_score = np.corrcoef(Ytest, Ypredict)[0,1]
print(correlation_score)
default_score = regressor.score(Xtest,Ytest)
print(default_score)
mse_score = ((Ypredict - Ytest_mean)**2).sum()/len(Ytest)
print(mse_score)
end = time.time()
print(end-start)

plt.scatter(Ypredict,Ytest, c = "", marker = "o", edgecolors='mediumpurple', alpha = 0.5)
plt.plot([-1, 1.5], [-1.5, 2], ls="--", c=".3", alpha = 0.8)
plt.xlabel("Predicted stability score")
plt.ylabel("True stability score")
plt.title("Correlation coefficient -- Random Forest\n Train")
plt.show()

feature_importance = regressor.feature_importances_
plt.plot(feature_importance)
plt.show()

"""### 4.6. Prediction"""

single_test = pd.read_csv("twohot_single_test.csv")
Xsingle_test = single_test.iloc[:, 1:-1].values
Ysingle_test = single_test.iloc[:, -1].values
Ysingle_test_mean = np.mean(Ysingle_test)

multiple_test = pd.read_csv("twohot_multi_test.csv")
Xmultiple_test = multiple_test.iloc[:, 1:-1].values
Ymultiple_test = multiple_test.iloc[:, -1].values
Ymultiple_test_mean = np.mean(Ymultiple_test)

all_test = pd.concat([single_test, multiple_test])
Xall_test = all_test.iloc[:, 1:-1].values
Yall_test = all_test.iloc[:, -1].values
Yall_test_mean = np.mean(Yall_test)


def RFprediction(Xtest, Ytest):
  start = time.time()
  Ytest_mean = np.mean(Ytest)
  Ypredict = regressor.predict(Xtest)
  correlation_prediction = np.corrcoef(Ytest, Ypredict)[0,1]
  default_prediction = regressor.score(Xtest,Ytest)
  mse_prediction = ((Ypredict - Ytest_mean)**2).sum()/len(Ytest)
  end = time.time()
  print(end-start)
  return correlation_prediction, default_prediction, mse_prediction, Ypredict

correlation_all_prediction, default_all_prediction, mse_all_prediction, Yall_predict = RFprediction(Xall_test, Yall_test)
correlation_single_prediction, default_single_prediction, mse_single_prediction, Ysingle_predict = RFprediction(Xsingle_test, Ysingle_test)
correlation_multiple_prediction, default_multiple_prediction, mse_multiple_prediction, Ymultiple_predict = RFprediction(Xmultiple_test, Ymultiple_test)


plt.scatter(Yall_predict,Yall_test, c = "", marker = "o", edgecolors='mediumpurple', alpha = 0.5)
plt.plot([-1, 1.5], [-1.5, 2], ls="--", c=".3", alpha = 0.8)
plt.xlabel("Predicted stability score")
plt.ylabel("True stability score")
plt.title("Corelation coefficient -- Random Forest\n All Test")
plt.show()

## all_test
prediction_result = all_test
prediction_result["Random Forest"] = Yall_predict
prediction_result = pd.DataFrame(prediction_result, columns = ["name", "stabilityscore", "Random Forest"])
prediction_result.to_csv("Random_Forest.csv")

## single test
prediction_single_result = single_test
prediction_single_result["Random Forest"] = Ysingle_predict
prediction_single_result = pd.DataFrame(prediction_single_result, columns = ["name", "stabilityscore", "Random Forest"])
prediction_single_result.to_csv("single_Random_Forest.csv")

## multiplee test
prediction_multiple_result = multiple_test
prediction_multiple_result["Random Forest"] = Ymultiple_predict
prediction_multiple_result = pd.DataFrame(prediction_multiple_result, columns = ["name", "stabilityscore", "Random Forest"])
prediction_multiple_result.to_csv("multiple_Random_Forest.csv")
