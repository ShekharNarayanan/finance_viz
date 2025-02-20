import json
import numpy as np
import matplotlib.pyplot as plt
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import RandomOverSampler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import cross_val_score

# 1. Load your data
with open("src/labeled_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Prepare text & labels
X, y = [], []
for item in data:
    combined_text = f"{item['company']} {item['summary']}"
    X.append(combined_text)
    y.append(item["label"])



# 3. Define multiple classifiers we want to compare
classifiers = {
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
    "RandomForest": RandomForestClassifier(n_estimators=1000, random_state=42, class_weight='balanced'),
    "NaiveBayes": MultinomialNB(),  # doesn't have class_weight but oversampling helps
    "SVC-linear": SVC(kernel='linear', class_weight='balanced', random_state=42)
}

# 4. Prepare cross-validation
n_folds = 3
skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

# Get dummy classifier scores for chance performance
dummy = DummyClassifier(strategy='stratified', random_state=42)
chance_scores = cross_val_score(dummy, X, y, cv=n_folds, scoring='accuracy')

# We'll store fold-accuracies for each classifier in this dict
results = {}

for clf_name, clf in classifiers.items():
    # Build pipeline: TF-IDF -> OverSampler -> classifier
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words='english', max_features=2000)),
        ("ros", RandomOverSampler(random_state=42)),
        ("clf", clf)
    ])
    
    # Accuracy list for the folds
    accuracies = []
    mean_accuracies = []
    
    for train_idx, test_idx in skf.split(X, y):
        X_train = [X[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        X_test  = [X[i] for i in test_idx]
        y_test  = [y[i] for i in test_idx]
        
        # Train
        pipeline.fit(X_train, y_train)
        # Predict
        y_pred = pipeline.predict(X_test)
        
        # Fold accuracy
        fold_acc = np.mean(y_pred == y_test)
        accuracies.append(fold_acc)
        
    # Store the fold accuracies
    results[clf_name] = accuracies

# 5. Plot each classifier's performance as a separate line
plt.figure(figsize=(11,6))

x = np.arange(n_folds) + 1  # e.g. [1,2,3] if n_folds=3
for clf_name, accuracies in results.items():
    plt.plot(x, accuracies, marker='*', label=f"{clf_name}, avg_acc: {np.mean(results[clf_name]):.2f}")
    

# Plot a dashed line for chance level, e.g. 0.5
plt.axhline(y=np.mean(chance_scores), linestyle='--', color='k', alpha=0.5, label=f'chance, avg_acc:{np.mean(chance_scores):.2f}')

plt.xlabel(f"{n_folds}-fold CV folds")
plt.ylabel("accuracy")
plt.title(f"Text categorization performance")
plt.ylim([0, 1])
plt.legend(bbox_to_anchor=(1,1))
plt.tight_layout()
plt.show()


