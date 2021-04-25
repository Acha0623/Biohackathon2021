# -*- coding: utf-8 -*-
"""cnn_protein.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12PXmSCB5CZGSkNm7XYx0pI0TrP4Njgf-
"""

# import os
# from google.colab import drive
# drive.mount('/content/gdrive')
# root_path = 'gdrive/My Drive'  
# os.chdir(root_path)
# os.getcwd()

X_train= pd.read_csv("X_train.csv")
X_test = pd.read_csv("X_test.csv")
y_train = pd.read_csv("y_train.csv")
y_test = pd.read_csv("y_test.csv")
X=pd.read_csv("X.csv")
y=pd.read_csv("y.csv")

from keras.models import Sequential
from keras.models import *
from keras.layers import *
from keras.optimizers import *
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras import backend as keras

def cnn_model(input_size,lr,dp,fs,ks):
  m = Sequential()
  m.add(Conv1D(filters=fs,kernel_size=ks,input_shape = input_size,padding='same'))
  m.add(LeakyReLU(alpha=0.2))
  m.add(BatchNormalization())
  m.add(Dropout(dp))
  m.add(Conv1D(filters=fs*2,kernel_size=ks,padding='same'))
  m.add(LeakyReLU(alpha=0.2))
  m.add(BatchNormalization())
  m.add(Dropout(dp))
  m.add(Conv1D(filters=fs,kernel_size=ks,padding='same'))
  m.add(LeakyReLU(alpha=0.2))
  m.add(BatchNormalization())
  m.add(Dropout(dp))
  m.add(Flatten())
  m.add(Dense(1))
  m.compile(optimizer = Adam(clipnorm =1,learning_rate= lr),loss = "mean_squared_error", metrics=['mae'])
  return m

# train model
lrs = [0.01,0.001,0.0001]
dps = [0.2,0.3,0.5]
fs = [24,48]
ks = [14,19,21,24]
for i in range(len(lrs)):
  for j in range(len(dps)):
    for k in range(len(fs)):
      for l in range(len(ks)):
        modelt = cnn_model((43,24),lrs[i],dps[j],fs[k],ks[l])
        history =  modelt.fit(X_train.drop("name",1).to_numpy().reshape(30165,43,24),y_train.iloc[:,0].to_numpy(), batch_size = 256, epochs = 50, validation_split = 0.2)
        y_pred = modelt.predict(X_test.drop("name",1).to_numpy().reshape(7541,43,24))
        plt.scatter(y_pred,y_test.iloc[:,0])
        plt.xlabel("y_pred")
        plt.ylabel("y_true")
        df = pd.DataFrame({"y_true":y_test.iloc[:,0],"y_pred":y_pred.flatten()})
        print(df.corr())
        SE=(y_pred-y_test)**2
        print(SE.mean())


# final model
model = Sequential()
model.add(Conv1D(48,24,input_shape = (43,24),padding='same'))
model.add(LeakyReLU(alpha=0.2))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Conv1D(96,24,padding='same'))
model.add(LeakyReLU(alpha=0.2))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Conv1D(48,24,padding='same'))
model.add(LeakyReLU(alpha=0.2))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(1))
model.compile(optimizer = Adam(clipnorm =1,learning_rate= lr),loss = "mean_squared_error", metrics=['mae'])

model = cnn_model((43,24),0.01,0.5,48,24)
history =  model.fit(X_train.drop("name",1).to_numpy().reshape(30165,43,24),y_train.iloc[:,0].to_numpy(), batch_size = 256, epochs = 50, validation_split = 0.2)
y_pred = model.predict(X_test.drop("name",1).to_numpy().reshape(7541,43,24))
plt.scatter(y_pred,y_test.iloc[:,0])
plt.xlabel("y_pred")
plt.ylabel("y_true")
df = pd.DataFrame({"y_true":y_test.iloc[:,0],"y_pred":y_pred.flatten()})
print(df.corr())
SE=(y_pred-y_test)**2
print(SE.mean())

# test for single mutation protein
single_test_dat = pd.read_csv("twohot_single_test.csv")
single_test_dat.drop("name",1).shape

single_test = single_test_dat.drop(['name','stabilityscore'],1).to_numpy().reshape(2138,43,24).astype('float')

single_pred = model.predict(single_test)

SE=(single_pred.flatten()-single_test_dat.loc[:,"stabilityscore"])**2
SE.mean()

plt.scatter(single_pred.flatten(),single_test_dat.loc[:,"stabilityscore"])

df = pd.DataFrame({"y_true":single_test_dat.loc[:,"stabilityscore"],"y_pred":single_pred.flatten()})
df.corr()

# test for multiple mutation protein
multi_test_dat = pd.read_csv("twohot_multi_test.csv")
multi_test_dat.drop("name",1).shape

multi_test = multi_test_dat.drop(['name','stabilityscore'],1).to_numpy().reshape(7290,43,24).astype('float')

multi_pred = model.predict(multi_test)

SE=(multi_pred.flatten()-multi_test_dat.loc[:,"stabilityscore"])**2
SE.mean()

df = pd.DataFrame({"y_true":multi_test_dat.loc[:,"stabilityscore"],"y_pred":multi_pred.flatten()})
df.corr()
# output the results
single_df = pd.DataFrame({"name":single_test_dat.name,
                       "Stability_score":single_test_dat.loc[:,"stabilityscore"],"Prediction":single_pred.flatten()})
single_df.head()

single_df.to_csv('single_CNN.csv')

multi_df = pd.DataFrame({"name":multi_test_dat.name,
                       "Stability_score":multi_test_dat.loc[:,"stabilityscore"],"Prediction":multi_pred.flatten()})
multi_df.head()

multi_df.to_csv('multiple_CNN.csv')