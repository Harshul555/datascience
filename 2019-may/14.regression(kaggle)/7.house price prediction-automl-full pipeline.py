#with log transformation of target and rf ensembling
import sys
path = 'E://utils'
sys.path.append(path)

import common_utils  as utils
import regression_utils as rutils
from sklearn import metrics, ensemble, model_selection, neighbors, linear_model, decomposition, manifold
import math
import pandas as pd
import os
import seaborn as sns
import numpy as np
import tpot

def log_rmse(y_orig, y_pred):
    return math.sqrt(metrics.mean_squared_log_error(y_orig,y_pred) )

def rmse(y_orig, y_pred):
    return math.sqrt(metrics.mean_squared_error(y_orig,y_pred) )


path = 'E://'
house_train = pd.read_csv(os.path.join(path,"house_train.csv"))
house_train.shape
house_train.info()

house_test = pd.read_csv(os.path.join(path,"house_test.csv"))
house_test.shape
house_test.info()

house = pd.concat((house_train, house_test), axis = 0)
house.shape
house.info()

print(utils.get_continuous_features(house))
print(utils.get_non_continuous_features(house))

sns.countplot(x='YearBuilt',data=house_train)
sns.jointplot(x="SalePrice", y="YearBuilt", data=house_train)
sns.FacetGrid(house_train, hue="YearBuilt",size=8).map(sns.kdeplot, "SalePrice").add_legend()

sns.countplot(x='YrSold',data=house_train)
sns.jointplot(x="SalePrice", y="YrSold", data=house_train)
sns.FacetGrid(house_train, hue="YrSold",size=8).map(sns.kdeplot, "SalePrice").add_legend()

features_to_cast = ['MSSubClass']
utils.cast_to_cat(house, features_to_cast)

features_to_drop = ['Id']
missing_features_above_th = utils.get_features_to_drop_on_missingdata(house, 0.25)
features_to_drop.extend(missing_features_above_th)
house1 = utils.drop_features(house, features_to_drop)
house1.info()

imputable_cat_features = utils.get_non_continuous_features(house1)
cat_imputer = utils.get_categorical_imputers(house1, imputable_cat_features)
house1[imputable_cat_features] = cat_imputer.transform(house1[imputable_cat_features])

imputable_cont_features = utils.get_continuous_features(house1)
cont_imputer = utils.get_continuous_imputers(house1, imputable_cont_features)
house1[imputable_cont_features] = cont_imputer.transform(house1[imputable_cont_features])
house1.info()

house2 = utils.ohe(house1, imputable_cat_features)

scaler = utils.get_scaler(house2)
house3 = scaler.transform(house2)
house3 = pd.DataFrame(house3, columns=house2.columns)

X_train = house3[:house_train.shape[0]]
y_train = house_train['SalePrice']

lasso_selector = linear_model.Lasso()
lasso_selector.fit(X_train, y_train)
print(lasso_selector.coef_)
utils.plot_feature_importances(lasso_selector, X_train, 40)

X_train1 = utils.select_features(lasso_selector, X_train)

utils.corr_heatmap(X_train1)
lpca = decomposition.PCA(0.95)
lpca.fit(X_train1)
print(np.cumsum(lpca.explained_variance_ratio_))
pca_data = lpca.transform(X_train1)
print(pca_data.shape)

tsne = manifold.TSNE(n_components=2)
tsne_data = tsne.fit_transform(pca_data)
rutils.plot_data_3d_regression(tsne_data, y_train)

scoring = metrics.make_scorer(log_rmse, greater_is_better=False)

sns.distplot(y_train)
y_trans = np.log1p(y_train)
sns.distplot(y_trans)

regressor_config_dict = {

    'sklearn.linear_model.ElasticNetCV': {
        'l1_ratio': np.arange(0.0, 1.01, 0.05),
        'tol': [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    },

    'sklearn.ensemble.ExtraTreesRegressor': {
        'n_estimators': [100],
        'max_features': np.arange(0.05, 1.01, 0.05),
        'min_samples_split': range(2, 21),
        'min_samples_leaf': range(1, 21),
        'bootstrap': [True, False]
    },

    'sklearn.ensemble.GradientBoostingRegressor': {
        'n_estimators': [100],
        'loss': ["ls", "lad", "huber", "quantile"],
        'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
        'max_depth': range(1, 11),
        'min_samples_split': range(2, 21),
        'min_samples_leaf': range(1, 21),
        'subsample': np.arange(0.05, 1.01, 0.05),
        'max_features': np.arange(0.05, 1.01, 0.05),
        'alpha': [0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
    },

    'sklearn.ensemble.AdaBoostRegressor': {
        'n_estimators': [100],
        'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
        'loss': ["linear", "square", "exponential"]
    },

    'sklearn.tree.DecisionTreeRegressor': {
        'max_depth': range(1, 11),
        'min_samples_split': range(2, 21),
        'min_samples_leaf': range(1, 21)
    },

    'sklearn.neighbors.KNeighborsRegressor': {
        'n_neighbors': range(1, 101),
        'weights': ["uniform", "distance"],
        'p': [1, 2]
    },

    'sklearn.linear_model.LassoLarsCV': {
        'normalize': [True, False]
    },

    'sklearn.svm.LinearSVR': {
        'loss': ["epsilon_insensitive", "squared_epsilon_insensitive"],
        'dual': [True, False],
        'tol': [1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
        'C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20., 25.],
        'epsilon': [1e-4, 1e-3, 1e-2, 1e-1, 1.]
    },

    'sklearn.ensemble.RandomForestRegressor': {
        'n_estimators': [100],
        'max_features': np.arange(0.05, 1.01, 0.05),
        'min_samples_split': range(2, 21),
        'min_samples_leaf': range(1, 21),
        'bootstrap': [True, False]
    },

    'sklearn.linear_model.RidgeCV': {
    },

    'xgboost.XGBRegressor': {
        'n_estimators': [100],
        'max_depth': range(1, 11),
        'learning_rate': [1e-3, 1e-2, 1e-1, 0.5, 1.],
        'subsample': np.arange(0.05, 1.01, 0.05),
        'min_child_weight': range(1, 21),
        'nthread': [1],
        'objective': ['reg:squarederror']
    }
    
}

tpot_estimator = tpot.TPOTRegressor(generations=5, population_size=100,
                                offspring_size=250,
                                verbosity=2, early_stop=3, 
                                config_dict=regressor_config_dict,
                                cv = 5, scoring = scoring)
tpot_estimator.fit(X_train, y_train)
print(tpot_estimator.score(X_train, y_train))
print(tpot_estimator.fitted_pipeline_)
print(tpot_estimator._optimized_pipeline)
print(tpot_estimator.evaluated_individuals_)
X_test = house3[house_train.shape[0]:]
X_test1 = utils.select_features(lasso_selector, X_test)
pca_test_data = lpca.transform(X_test1)
pca_test_data.shape

house_test['SalePrice'] = np.expm1(final_rf_model.predict(pca_test_data))
house_test.to_csv("C:\\Users\\Algorithmica\\Downloads\\submission.csv", columns=["Id", "SalePrice"], index=False)
