import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

# 处理训练集,相应数据用大写字母表示
raw_train = pd.read_csv("./data/train.csv")
Y = np.array((raw_train.loc[:, "outcome"]), dtype=np.float64)
# 处理测试集,相应数据用小写字母表示
raw_test = pd.read_csv("./data/test.csv")
human_pred = np.array(raw_test.loc[:, "XXX-Intuition"], dtype=np.float64)
ml_pred = np.array(raw_test.loc[:, "predicted outcome"], dtype=np.float64)
y = np.array(raw_test.loc[:, "outcome (actual)"], dtype=np.float64)
np.save("./processedData/Y/Y.npy", Y)
np.save("./processedData/Y/y.npy", y)
np.save("./processedData/Y/ml_pred.npy", ml_pred)
np.save("./processedData/Y/human_pred.npy", human_pred)

# 处理训练集
rawX = raw_train.loc[:, "XXXinorg1":"purity"]
rawx = raw_test.loc[:, "XXXinorg1":"purity"]

rawXx = pd.concat([rawX, rawx])
featureName = list(rawXx)

# 对非数值类型数据进行转换
X_featureName = []  # 记录每一维数据对应的特征名称
Xx = np.array([],
              dtype=np.float64).reshape(len(rawXx), -1)
boolFeature = []  # 转化为bool型的特征名称
oneHotFeature = []  # 独热编码的特征名称
errorFeature = []  # 转化出错的特征名称
encoders = {}  # 编码器
for i in featureName:
    try:
        feature = np.array(rawXx.loc[:, i],
                           dtype=np.float64).reshape(-1, 1)  # 尝试转化为数值变量
    except:
        featureVal = set(rawXx.loc[:, i])
        if(len(featureVal) == 1):  # 只有一种值的特征，没有帮助
            continue
        elif(featureVal == set(["yes", "no"])):  # bool 型
            feature = np.array(rawXx.loc[:, i] == 'yes',
                               dtype=np.float64).reshape(-1, 1)
            boolFeature.append(i)
        elif(featureVal == set(["yes", "no", "?"])):  # 需要补全的bool 型
            valCnt = rawXx.loc[:, i].value_counts()
            ratio = (valCnt["yes"])/(valCnt['no'])
            feature = np.array((rawXx.loc[:, i] == 'yes')
                               + ((rawXx.loc[:, i] == '?') *
                                  (ratio/(1+ratio))),
                               dtype=np.float64).reshape(-1, 1)
            boolFeature.append(i)
        else:
            ohe = OneHotEncoder()
            feature = ohe.fit_transform(
                np.array(rawXx.loc[:, i], dtype=str)
                .reshape(-1, 1)).toarray()
            if(feature.shape[1] > 200):
                errorFeature.append(i)
                continue
            else:
                oneHotFeature.append(i)
                encoders[i] = ohe
    X_featureName += [i]*(feature.shape[1])
    Xx = np.concatenate((Xx, feature), axis=1)
X = Xx[:len(rawX), :]
x = Xx[len(rawX):, :]

np.save("./processedData/X/X.npy", X)
np.save("./processedData/X/x.npy", x)
np.save("./processedData/X/X_featureName.npy", X_featureName)
np.save("./processedData/X/errorFeature.npy", errorFeature)
np.save("./processedData/X/oneHotFeature.npy", oneHotFeature)
np.save("./processedData/X/boolFeature.npy", boolFeature)
np.save("./processedData/X/encoders.npy", encoders)

# 对数据进行标准化

scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)
x_normalized = scaler.transform(x)
np.save("./processedData/X/X_normalized.npy", X_normalized)
np.save("./processedData/X/x_normalized.npy", x_normalized)

# 去除反应物名称
reactantMask = ["XXXinorg1", "XXXinorg2", "XXXinorg3", "XXXorg1", "XXXorg2"]
mask = [i for i in range(len(X_featureName))
        if X_featureName[i] not in reactantMask]
np.save("./processedData/X/X_masked.npy", X[:, mask])
np.save("./processedData/X/x_masked.npy", x[:, mask])

# 检验是否有异常值
print("error")
for i in range(X_normalized.shape[-1]):
    if max(abs(X_normalized[:, i])) > 3:
        print(i)


# 对数据按反应物进行归类
comb = []
reactantCombination = []
for i in range(0, len(rawX)):
    try:
        id = comb.index(set(rawX.loc[i, reactantMask]))
        reactantCombination[id].append(i)
    except:
        comb.append(set(rawX.loc[i, reactantMask]))
        reactantCombination.append([i])

np.save("./processedData/X/reactComb.npy", reactantCombination,allow_pickle=True)
