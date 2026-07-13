% clc, clear;
% % Thư mục chứa các tệp tin
% folderPath = 'D:\EMG - Muscle Faritue\Project3';
% % Số lượng tệp tin và định dạng tên tệp tin
% load('Data.mat');
% 
% TrainNF = [Subject1_NF;Subject2_NF;Subject3_NF;Subject4_NF;Subject5_NF;Subject6_NF;Subject7_NF;Subject8_NF;Subject9_NF];
% TrainF  = [Subject1_F ;Subject2_F ;Subject3_F ;Subject4_F ;Subject5_F ;Subject6_F ;Subject7_F; Subject8_F ;Subject9_F];
% 
% TestNF = Subject10_NF;
% TestF  = Subject10_F;
% 
% Xtrain = [TrainNF;TrainF];
% Ytrain = [zeros(size(TrainNF,1),14); ones(size(TrainF,1),14)];
% 
% Xtest = [TestNF;TestF];
% Ytest = [zeros(size(TestNF,1),14); ones(size(TestF,1),14)];

% Split data into training and test sets (80% training, 20% testing)
% % Giả sử X là ma trận dữ liệu của bạn
% [coeff, score, latent] = pca(X);
% % Trọng số của mỗi đặc trưng gốc trong thành phần chính đầu tiên
% firstPCWeights = coeff(:,1);
% 
% % Sắp xếp trọng số theo giá trị tuyệt đối và lấy chỉ số
% [sortedWeights, sortedIndices] = sort(abs(firstPCWeights), 'descend');
% 
% % Lấy 3 đặc trưng hàng đầu theo trọng số
% top3Features = sortedIndices(1:3);
Xtrain = table2array(Train_Data(:,2:15));
Ytrain = table2array(Train_Data(:,16));

Xtest = table2array(Test_Data(:,2:15));
Ytest = table2array(Test_Data(:,16));

% % PCA
% % Giả sử X là ma trận dữ liệu của bạn, mỗi hàng là một mẫu và mỗi cột là một đặc trưng
% [coeff, score, ~] = pca(Xtrain);
% 
% % Feature Selection Algorithms
% % Giả sử X là ma trận dữ liệu và y là vector nhãn
[ranked, weights] = fscmrmr(Xtrain, Ytrain);

% Lấy 3 đặc trưng hàng đầu
top3Features = ranked(1:3);

Xtrain = Xtrain(:,top3Features);
Xtest = Xtest(:,top3Features);

SVMModel = fitcsvm(Xtrain,Ytrain,'KernelFunction', 'linear', ...
    'PolynomialOrder', [], ...
    'KernelScale', 1, ...
    'BoxConstraint', 1, ...
    'Standardize', true);
% Label prediction for test set
predicted_labels = predict(SVMModel,Xtest);

% error = svmClassify(Xtrain, Ytrain, Xtest, Ytest);
% opts = statset('display','iter');  % Hiển thị tiến trình
% fun = @(Xtrain, Ytrain, Xtest, Ytest) error;
% [selectedFeatures, history] = sequentialfs(fun, X1, Y1(:,1), 'options', opts, 'cv', 'none');  % 'cv', 'none' ngăn việc sử dụng cross-validation


% Tính Confusion Matrix
C = confusionmat(Ytest, predicted_labels);
cu
% confusionchart(C);
TP = C(1,1);
FN = C(2,1);
FP = C(1,2);
TN = C(2,2);
% Accuracy
accuracy = (TP + TN) / (TP + TN + FP + FN);
disp([ num2str(accuracy)]);

% Tính Precision
precision = TP / (TP + FP);
disp([num2str(precision)]);

% Tính Recall
recall = TP / (TP + FN);
disp([num2str(recall)]);

% Tính F1 macro
f1_score = 2 * TP / (2 * TP + FP + FN);
disp([num2str(f1_score)]);

