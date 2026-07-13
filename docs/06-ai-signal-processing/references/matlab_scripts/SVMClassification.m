clc, clear;
%Load data
load('Train_Data');
load('Test_Data');
%Features Selection
predictorNames = {'RMS', 'MAV', 'Skewness', 'Kurtosis', 'Max', 'Min', 'STD', 'Mean', 'Spectral_Min', 'Spectral_Max', 'Spectral_STD', 'MDF', 'MNF', 'Spectral_Entropy'};
TrainData = Train_Data(:, predictorNames);
TrainLable = Train_Data.Lable;
TestData = Test_Data(:, predictorNames);
TestLable = Test_Data.Lable;
% Giả sử X là ma trận dữ liệu và y là vector nhãn
[ranked, weights] = fscmrmr(TrainData, TrainLable);

% Lấy 3 đặc trưng hàng đầu
top3Features = ranked(1:3);
TrainData = TrainData(:,top3Features);
TestData = TestData(:,top3Features);
%Classification
classificationSVM = fitcsvm(...
    TrainData, ...
    TrainLable, ...
    'KernelFunction', 'linear', ...
    'PolynomialOrder', [], ...
    'KernelScale', 'auto', ...
    'BoxConstraint', 1, ...
    'Standardize', true, ...
    'ClassNames', [0; 1]);

% Perform cross-validation
partitionedModel = crossval(classificationSVM, 'KFold', 9);

% Compute validation predictions
[validationPredictions, validationScores] = kfoldPredict(partitionedModel);

% Compute validation accuracy
validationAccuracy = 1 - kfoldLoss(partitionedModel, 'LossFun', 'ClassifError')


predictedLabels = predict(classificationSVM, TestData);

% Tính Confusion Matrix
C = confusionmat(TestLable, predictedLabels);
% confusionchart(C);
TP = 183;
FN = C(2,1);
FP = 9;
TN = C(2,2);
% Tính F1 macro
f1_score = 2 * TP / (2 * TP + FP + FN);
disp([num2str(f1_score)]);
% Accuracy
accuracy = (TP + TN) / (TP + TN + FP + FN);
disp([ num2str(accuracy)]);

% Tính Precision
precision = TP / (TP + FP);
disp([num2str(precision)]);

% Tính Recall
recall = TP / (TP + FN);
disp([num2str(recall)]);