import os
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)
import joblib


df = pd.read_csv(r"Obesity.csv")

#Classe para Tratamento dos Dados
class DataProcessor:

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    def remove_duplicates(self):
        self.df = self.df.drop_duplicates()
        return self

    def treat_missing_values(self):
        numeric_cols = self.df.select_dtypes(include=["int64", "float64"]).columns

        for col in numeric_cols:
            self.df[col] = self.df[col].fillna(self.df[col].median())

        categorical_cols = self.df.select_dtypes(include=["object"]).columns

        for col in categorical_cols:
            self.df[col] = self.df[col].fillna(self.df[col].mode()[0])

        return self

    def create_bmi_feature(self):
        self.df["BMI"] = self.df["Weight"] / (self.df["Height"] ** 2)
        return self

    def get_processed_data(self):
        return self.df

#Classe do Modelo Preditivo
class ObesityPredictor:

    def __init__(self, dataframe, target_column):
        self.df = dataframe
        self.target_column = target_column
        self.pipeline = None

    def split_features_target(self):

        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]

        return X, y

    def build_pipeline(self, X):

        categorical_features = X.select_dtypes(include=["object"]).columns.tolist()
        numerical_features = X.select_dtypes(exclude=["object"]).columns.tolist()

        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numerical_features),
                ("cat", categorical_transformer, categorical_features)
            ]
        )

        self.pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                n_estimators=300,
                random_state=42
            ))
        ])

    def train(self):

        X, y = self.split_features_target()
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        self.build_pipeline(X)

        self.pipeline.fit(X_train, y_train)

        predictions = self.pipeline.predict(X_test)


        return X_test, y_test, predictions

    def save_model(self, filename="pipeline.pkl"):
        joblib.dump(self.pipeline, filename)
        print(f"Modelo salvo como: {filename}")

#Processamento dos Dados
processor = DataProcessor(df)

processed_df = (
    processor
    .remove_duplicates()
    .treat_missing_values()
    .create_bmi_feature()
    .get_processed_data()
)

predictor = ObesityPredictor(
    dataframe=processed_df,
    target_column="Obesity"
)

X_test, y_test, predictions = predictor.train()

predictor.save_model()

loaded_model = joblib.load("./pipeline.pkl")

sample = processed_df.drop(columns=["Obesity"]).iloc[[0]]

prediction = loaded_model.predict(sample)

model_path = "../api/model_data/pipeline.pkl"
os.makedirs(os.path.dirname(model_path), exist_ok=True)
with open(model_path, "wb") as f:
    pickle.dump(loaded_model, f)
print(f"Modelo salvo comoooo: {model_path}")