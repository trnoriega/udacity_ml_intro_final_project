""" a basic script for importing POI identifier,
    and checking the results from it
    requires that the algorithm, dataset, and features list
    be written to my_classifier.pkl, my_dataset.pkl, and
    my_feature_list.pkl, respectively.
"""

import pickle
from sklearn.model_selection import StratifiedShuffleSplit
from tools.feature_format import featureFormat, targetFeatureSplit
import os

PERF_FORMAT_STRING = '\
Accuracy: {:>0.{display_precision}f}\
\nPrecision: {:>0.{display_precision}f}\
\nRecall: {:>0.{display_precision}f}\
\nF1: {:>0.{display_precision}f}'

RESULTS_FORMAT_STRING = '\
Total predictions: {:4d}\
\nTrue positives: {:4d}\
\nFalse positives: {:4d}\
\nFalse negatives: {:4d}\
\nTrue negatives: {:4d}'

def test_classifier(clf, dataset, feature_list, folds=1000):
    data = featureFormat(dataset, feature_list, sort_keys=True)
    labels, features = data[:, 0], data[:, 1:]
    cv = StratifiedShuffleSplit(n_splits=folds, random_state=42)
    true_negatives = 0
    false_negatives = 0
    true_positives = 0
    false_positives = 0

    # progress indicator counters
    print 'Testing splits: '
    count_i = 0
    total_i = float(len(list(cv.split(features, labels))))

    for train_idx, test_idx in cv.split(features, labels):
        features_train = []
        features_test = []
        labels_train = []
        labels_test = []
        for ii in train_idx:
            features_train.append(features[ii])
            labels_train.append(labels[ii])
        for jj in test_idx:
            features_test.append(features[jj])
            labels_test.append(labels[jj])

        ### fit the classifier using training set, and test on test set
        clf.fit(features_train, labels_train)
        predictions = clf.predict(features_test)
        for prediction, truth in zip(predictions, labels_test):
            if prediction == 0 and truth == 0:
                true_negatives += 1
            elif prediction == 0 and truth == 1:
                false_negatives += 1
            elif prediction == 1 and truth == 0:
                false_positives += 1
            elif prediction == 1 and truth == 1:
                true_positives += 1
            else:
                print "Warning: Found a predicted label not == 0 or 1."
                print "All predictions should take value 0 or 1."
                print "Evaluating performance for processed predictions:"
                break

        # Progress indicator display
        count_i += 1
        if (count_i/total_i)*100%5 == 0:
            print '.', str(count_i/total_i*100), '%',
    
    print ''
    try:
        total_predictions = true_negatives + false_negatives + false_positives + true_positives
        accuracy = 1.0*(true_positives + true_negatives)/total_predictions
        precision = 1.0*true_positives/(true_positives+false_positives)
        recall = 1.0*true_positives/(true_positives+false_negatives)
        f1 = 2.0 * true_positives/(2*true_positives + false_positives+false_negatives)
        f2 = (1+2.0*2.0) * precision*recall/(4*precision + recall)
        print 'ESTIMATOR:'
        print clf
        print 'RESULTS:'
        print RESULTS_FORMAT_STRING.format(total_predictions, true_positives, false_positives,
                                           false_negatives, true_negatives)
        print 'PERFORMANCE:'
        print PERF_FORMAT_STRING.format(accuracy, precision, recall, f1, display_precision=5)

    except:
        print "Got a divide by zero when trying out:", clf
        print "Precision or recall may be undefined due to a lack of true positive predicitons."


#EXTRA_PATH specifies where to save the data
HOME_PATH = os.path.expanduser('~')
EXTRA_PATH = os.path.join(HOME_PATH, 'Desktop', 'raw_data', 'ml')

CLF_PICKLE_FILENAME = os.path.join(EXTRA_PATH, 'my_classifier.pkl')
DATASET_PICKLE_FILENAME = os.path.join(EXTRA_PATH, 'my_dataset.pkl')
FEATURE_LIST_FILENAME = os.path.join(EXTRA_PATH, 'my_feature_list.pkl')

def dump_classifier_and_data(clf, dataset, feature_list):
    with open(CLF_PICKLE_FILENAME, "w") as clf_outfile:
        pickle.dump(clf, clf_outfile, protocol=pickle.HIGHEST_PROTOCOL)
    with open(DATASET_PICKLE_FILENAME, "w") as dataset_outfile:
        pickle.dump(dataset, dataset_outfile, protocol=pickle.HIGHEST_PROTOCOL)
    with open(FEATURE_LIST_FILENAME, "w") as featurelist_outfile:
        pickle.dump(feature_list, featurelist_outfile, protocol=pickle.HIGHEST_PROTOCOL)

def load_classifier_and_data():
    with open(CLF_PICKLE_FILENAME, "r") as clf_infile:
        clf = pickle.load(clf_infile)
    with open(DATASET_PICKLE_FILENAME, "r") as dataset_infile:
        dataset = pickle.load(dataset_infile)
    with open(FEATURE_LIST_FILENAME, "r") as featurelist_infile:
        feature_list = pickle.load(featurelist_infile)
    return clf, dataset, feature_list

def main():
    ### load classifier, dataset, and feature_list
    print 'Loading data'
    clf, dataset, feature_list = load_classifier_and_data()
    print 'Done loading'
    ### Run testing script
    print 'Start testing'
    test_classifier(clf, dataset, feature_list)
    print 'Done testing'

if __name__ == '__main__':
    main()
