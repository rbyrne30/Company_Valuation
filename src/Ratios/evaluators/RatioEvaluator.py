from sklearn import linear_model
import matplotlib.pyplot as plt
import numpy as np

TEST_SIZE=0.2


def regress(df, targetCol):
    train, test = __splitData(df)
    xtrain = train.drop([targetCol], axis=1)
    ytrain = train[targetCol]
    xtest = test.drop([targetCol], axis=1)
    ytest = test[targetCol]

    regr = __trainRegression(xtrain, ytrain)
    pred = __predict(regr, xtest)
    return xtrain, ytrain, xtest, ytest, pred


def plotRegression(actual, pred, xlabel=None, ticker="Stock", offSet="Unknown"):
    xlabel = xlabel if not xlabel is None else range(len(pred))
    plt.title(f"Prediction of Ratios on Share Price of {ticker} ({offSet} days lagged)")
    plt.plot(xlabel, pred, color='red', label="Prediction")
    plt.plot(xlabel, actual, label="Actual")
    plt.plot(xlabel, np.zeros(len(pred)), color="black")
    plt.legend()
    plt.show()


def __splitDataRandom(df):
    test = df.sample(frac=TEST_SIZE)
    train = df.drop(test.index, axis=0)
    return train, test


def __splitData(df):
    dataLength = df.shape[0]
    train = df.iloc[:-int(dataLength*TEST_SIZE)]
    test = df.iloc[-int(dataLength*TEST_SIZE):]
    return train, test 


def __trainRegression(xtrain, ytrain):
    regr = linear_model.LinearRegression()
    regr.fit(xtrain, ytrain)
    print("Score:", regr.score(xtrain, ytrain))
    return regr


def __predict(regr, vals):
    return regr.predict(vals)
