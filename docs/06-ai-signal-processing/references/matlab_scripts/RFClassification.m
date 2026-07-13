clc, clear;
%Load data
load('Train_Data');
load('Test_Data');
%Features Selection
predictorNames = {'RMS', 'MAV', 'Skewness', 'Kurtosis', 'Max', 'Min', 'STD', 'Mean', 'Spectral_Min', 'Spectral_Max', 'Spectral_STD', 'MDF', 'MNF', 'Spectral_Entropy'};
predictors = Train_Data(:, predictorNames);
response = Train_Data.Lable;
%Classification
classificationTree = fitctree(...
    predictors, ...
    response, ...
    'SplitCriterion', 'gdi', ...
    'MaxNumSplits', 20, ...
    'Surrogate', 'off', ...
    'ClassNames', [0; 1]);


% Perform cross-validation
partitionedModel = crossval(classificationTree, 'KFold', 9);

% Compute validation predictions
[validationPredictions, validationScores] = kfoldPredict(partitionedModel);

% Compute validation accuracy
validationAccuracy = 1 - kfoldLoss(partitionedModel, 'LossFun', 'ClassifError')

predictors = Test_Data(:, predictorNames);
response = Test_Data.Lable;
predictedLabels = predict(classificationTree, predictors);

% Tính Confusion Matrix
C = confusionmat(response, predictedLabels);
% confusionchart(C);
TP = C(1,1);
FN = C(2,1);
FP = C(1,2);
TN = C(2,2);
% Accuracy
accuracy = (TP + TN) / (TP + TN + FP + FN);
disp([ num2str(accuracy)]);

%Precision
precision = TP / (TP + FP);
disp([num2str(precision)]);

%Recall
recall = TP / (TP + FN);
disp([num2str(recall)]);

%F1 macro
f1_score = 2 * TP / (2 * TP + FP + FN);
disp([num2str(f1_score)]);
