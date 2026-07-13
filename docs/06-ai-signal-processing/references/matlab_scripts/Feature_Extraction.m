clc;clear;tic
% Read data from two separate EMG files
folderPath1 = 'D:\EMG - Muscle Faritue\Project3\Train_Data\Normal';
folderPath2 = 'D:\EMG - Muscle Faritue\Project3\Train_Data\Fatigue';

folderPath3 = 'D:\EMG - Muscle Faritue\Project3\Test_Data\Normal';
folderPath4 = 'D:\EMG - Muscle Faritue\Project3\Test_Data\Fatigue';
% Lấy danh sách các file trong thư mục
fileList1 = dir(fullfile(folderPath1, '*.csv'));
fileList2 = dir(fullfile(folderPath2, '*.csv'));
fileList3 = dir(fullfile(folderPath3, '*.csv'));
fileList4 = dir(fullfile(folderPath4, '*.csv'));

Fs = 2000;

windowSize = 2000; % Kích thước cửa sổ
overlap = 0; % Độ chồng lắp giữa các cửa sổ
nfft = 2^nextpow2(windowSize); % Kích thước FFT (có thể là lũy thừa của 2 gần nhất)

for i1 = 1:length(fileList1)
    fileName1 = fullfile(folderPath1, fileList1(i1).name);
    fileName2 = fullfile(folderPath2, fileList2(i1).name);
    table1 =   readtable(fileName1);
    table2 =   readtable(fileName2);
    emg_file1 = table2array(table1(:,2:65));
    emg_file2 = table2array(table2(:,2:65));
    selection1 = true(1, size(emg_file1, 2));
    selection2 = true(1, size(emg_file2, 2));
    
for e1 = 1:size(emg_file1, 2)
     if all(emg_file1(:,e1) == 0);
        all(emg_file2(:,e1) == 0);
         selection1(e1) = false;  % đánh dấu cột không có giá trị
         selection2(e1) = false;
     end
    end
    EMG1 = emg_file1(:,selection1);
    EMG2 = emg_file2(:,selection2);

 for j1 = 1:size(EMG1,2);
            %Time feature
            rms1(j1) = rms(EMG1(:,j1));
            mav1(j1) = mean(abs(EMG1(:,j1)));
            skewness1(j1) = skewness(EMG1(:,j1));
            kurtosis1(j1) = kurtosis(EMG1(:,j1));
            max1(j1) = max(EMG1(:,j1));
            min1(j1) = min(EMG1(:,j1));
            std1(j1) = std(EMG1(:,j1));
            mean1(j1) = mean(EMG1(:,j1));
            %Frequency feature
            EMG_fft1 = fft(EMG1(:,j1), nfft);
            EMG_PSD1 = abs(EMG_fft1).^2/nfft;
            spectral_min1(j1) = min(EMG_PSD1);
            spectral_max1(j1) = max(EMG_PSD1);
            spectral_std1(j1) = std(EMG_PSD1);
            mdf1(j1) = medfreq(EMG1(:,j1) ,Fs);
            mnf1(j1) = meanfreq(EMG1(:,j1),Fs);
            %Spectral Entropy
            se1(j1) = se(EMG1(:,j1));
 end 

 for j2 = 1:size(EMG2,2);
            %Time feature
            rms2(j2) = rms(EMG2(:,j2));
            mav2(j2) = mean(abs(EMG2(:,j2)));
            skewness2(j2) = skewness(EMG2(:,j2));
            kurtosis2(j2) = kurtosis(EMG2(:,j2));
            max2(j2) = max(EMG2(:,j2));
            min2(j2) = min(EMG2(:,j2));
            std2(j2) = std(EMG2(:,j2));
            mean2(j2) = mean(EMG2(:,j2));
            %Frequency feature
            EMG_fft2 = fft(EMG2(:,j2), nfft);
            EMG_PSD2 = abs(EMG_fft2).^2/nfft;
            spectral_min2(j2) = min(EMG_PSD2);
            spectral_max2(j2) = max(EMG_PSD2);
            spectral_std2(j2) = std(EMG_PSD2);
            mdf2(j2) = medfreq(EMG2(:,j2) ,Fs);
            mnf2(j2) = meanfreq(EMG2(:,j2),Fs);
            %Spectral Entropy
            se2(j2) = se(EMG2(:,j2));
 end
            data1_rms{i1} = rms1(j1);
            data1_mav{i1} = mav1(j1);
            data1_skewness{i1} = skewness1(j1);
            data1_kurtosis{i1} = kurtosis1(j1);
            data1_max{i1} = max1(j1);
            data1_min{i1} = min1(j1);
            data1_std{i1} = std1(j1);
            data1_mean{i1} = mean1(j1);
            data1_spectral_min{i1} = spectral_min1(j1);
            data1_spectral_max{i1} = spectral_max1(j1);
            data1_spectral_std{i1} = spectral_std1(j1);
            data1_mdf{i1} = mdf1(j1);
            data1_mnf{i1} = mnf1(j1);
            data1_se{i1} = se1(j1);
            
            
            data2_rms{i1} = rms2;
            data2_mav{i1} = mav2;
            data2_skewness{i1} = skewness2;
            data2_kurtosis{i1} = kurtosis2;
            data2_max{i1} = max2;
            data2_min{i1} = min2;
            data2_std{i1} = std2;
            data2_mean{i1} = mean2;
            data2_spectral_min{i1} = spectral_min2;
            data2_spectral_max{i1} = spectral_max2;
            data2_spectral_std{i1} = spectral_std2;
            data2_mdf{i1} = mdf2;
            data2_mnf{i1} = mnf2;
            data2_se{i1} = se2;
end

for i2 = 1:length(fileList3)
    fileName3 = fullfile(folderPath3, fileList3(i2).name);
    fileName4 = fullfile(folderPath4, fileList4(i2).name);
    table3 =   readtable(fileName3);
    table4 =   readtable(fileName4);
    emg_file3 = table2array(table3(:,2:65));
    emg_file4 = table2array(table4(:,2:65));
    selection3 = true(1, size(emg_file3, 2));
    selection4 = true(1, size(emg_file4, 2));
for e2 = 1:64
     if all(emg_file3(:,e2) == 0);
        all(emg_file4(:,e2) == 0);
        selection3(e2) = false;  % đánh dấu cột không có giá trị
        selection4(e2) = false;
     end
    end
    EMG3 = emg_file3(:,selection3);
    EMG4 = emg_file4(:,selection4);

 for j3 = 1:size(EMG3,2);
%Time feature
            rms3(j3) = rms(EMG3(:,j3));
            mav3(j3) = mean(abs(EMG3(:,j3)));
            skewness3(j3) = skewness(EMG3(:,j3));
            kurtosis3(j3) = kurtosis(EMG3(:,j3));
            max3(j3) = max(EMG3(:,j3));
            min3(j3) = min(EMG3(:,j3));
            std3(j3) = std(EMG3(:,j3));
            mean3(j3) = mean(EMG3(:,j3));
            %Frequency feature
            EMG_fft3 = fft(EMG3(:,j3), nfft);
            EMG_PSD3 = abs(EMG_fft3).^2/nfft;
            spectral_min3(j3) = min(EMG_PSD3);
            spectral_max3(j3) = max(EMG_PSD3);
            spectral_std3(j3) = std(EMG_PSD3);
            mdf3(j3) = medfreq(EMG3(:,j3) ,Fs);
            mnf3(j3) = meanfreq(EMG3(:,j3),Fs);
            %Spectral Entropy
            se3(j3) = se(EMG3(:,j3));
 end

 for j4 = 1:size(EMG4,2);
            %Time feature
            rms4(j4) = rms(EMG4(:,j4));
            mav4(j4) = mean(abs(EMG4(:,j4)));
            skewness4(j4) = skewness(EMG4(:,j4));
            kurtosis4(j4) = kurtosis(EMG4(:,j4));
            max4(j4) = max(EMG4(:,j4));
            min4(j4) = min(EMG4(:,j4));
            std4(j4) = std(EMG4(:,j4));
            mean4(j4) = mean(EMG4(:,j4));
            %Frequency feature
            EMG_fft4 = fft(EMG4(:,j4), nfft);
            EMG_PSD4 = abs(EMG_fft4).^4/nfft;
            spectral_min4(j4) = min(EMG_PSD4);
            spectral_max4(j4) = max(EMG_PSD4);
            spectral_std4(j4) = std(EMG_PSD4);
            mdf4(j4) = medfreq(EMG4(:,j4) ,Fs);
            mnf4(j4) = meanfreq(EMG4(:,j4),Fs);
            %Spectral Entropy
            se4(j4) = se(EMG4(:,j4));
 end
            data3_rms{i2} = rms3;
            data3_mav{i2} = mav3;
            data3_skewness{i2} = skewness3;
            data3_kurtosis{i2} = kurtosis3;
            data3_max{i2} = max3;
            data3_min{i2} = min3;
            data3_std{i2} = std3;
            data3_mean{i2} = mean3;
            data3_spectral_min{i2} = spectral_min3;
            data3_spectral_max{i2} = spectral_max3;
            data3_spectral_std{i2} = spectral_std3;
            data3_mdf{i2} = mdf3;
            data3_mnf{i2} = mnf3;
            data3_se{i2} = se3;
            
            
            data4_rms{i2} = rms4;
            data4_mav{i2} = mav4;
            data4_skewness{i2} = skewness4;
            data4_kurtosis{i2} = kurtosis4;
            data4_max{i2} = max4;
            data4_min{i2} = min4;
            data4_std{i2} = std4;
            data4_mean{i2} = mean4;
            data4_spectral_min{i2} = spectral_min4;
            data4_spectral_max{i2} = spectral_max4;
            data4_spectral_std{i2} = spectral_std4;
            data4_mdf{i2} = mdf4;
            data4_mnf{i2} = mnf4;
            data4_se{i2} = se4;
end

           
%Non-fatigue
A1 = cat(2, data1_rms{:});
A2 = cat(2, data1_mav{:});
A3 = cat(2, data1_skewness{:});
A4 = cat(2, data1_kurtosis{:});
A5 = cat(2, data1_max{:});
A6 = cat(2, data1_min{:});
A7 = cat(2, data1_std{:});
A8 = cat(2, data1_mean{:});
A9 = cat(2, data1_spectral_min{:});
A10 = cat(2, data1_spectral_max{:});
A11 = cat(2, data1_spectral_std{:});
A12 = cat(2, data1_mdf{:});
A13 = cat(2, data1_mnf{:});
A14 = cat(2, data1_se{:});

%Fatigue
B1 = cat(2, data2_rms{:});
B2 = cat(2, data2_mav{:});
B3 = cat(2, data2_skewness{:});
B4 = cat(2, data2_kurtosis{:});
B5 = cat(2, data2_max{:});
B6 = cat(2, data2_min{:});
B7 = cat(2, data2_std{:});
B8 = cat(2, data2_mean{:});
B9 = cat(2, data2_spectral_min{:});
B10 = cat(2, data2_spectral_max{:});
B11 = cat(2, data2_spectral_std{:});
B12 = cat(2, data2_mdf{:});
B13 = cat(2, data2_mnf{:});
B14 = cat(2, data2_se{:});

% Combine features and labels into a matrix
Xtrain = [A1' A2' A3' A4' A5' A6' A7' A8' A9' A10' A11' A12' A13' A14'; B1' B2' B3' B4' B5' B6' B7' B8' B9' B10' B11' B12' B13' B14'];
Ytrain = [zeros(size(A1',1),14); ones(size(B1',1),14)];
save('Xtrain.mat', 'Xtrain');
save('Ytrain.mat', 'Ytrain');

%Non-fatigue
C1 = cat(2, data3_rms{:});
C2 = cat(2, data3_mav{:});
C3 = cat(2, data3_skewness{:});
C4 = cat(2, data3_kurtosis{:});
C5 = cat(2, data3_max{:});
C6 = cat(2, data3_min{:});
C7 = cat(2, data3_std{:});
C8 = cat(2, data3_mean{:});
C9 = cat(2, data3_spectral_min{:});
C10 = cat(2, data3_spectral_max{:});
C11 = cat(2, data3_spectral_std{:});
C12 = cat(2, data3_mdf{:});
C13 = cat(2, data3_mnf{:});
C14 = cat(2, data3_se{:});

%Fatigue
D1 = cat(2, data4_rms{:});
D2 = cat(2, data4_mav{:});
D3 = cat(2, data4_skewness{:});
D4 = cat(2, data4_kurtosis{:});
D5 = cat(2, data4_max{:});
D6 = cat(2, data4_min{:});
D7 = cat(2, data4_std{:});
D8 = cat(2, data4_mean{:});
D9 = cat(2, data4_spectral_min{:});
D10 = cat(2, data4_spectral_max{:});
D11 = cat(2, data4_spectral_std{:});
D12 = cat(2, data4_mdf{:});
D13 = cat(2, data4_mnf{:});
D14 = cat(2, data4_se{:});

% Combine features and labels into a matrix
Xtest = [C1' C2' C3' C4' C5' C6' C7' C8' C9' C10' C11' C12' C13' C14'; D1' D2' D3' D4' D5' D6' D7' D8' D9' D10' D11' D12' D13' D14'];
Ytest = [zeros(size(C1',1),14); ones(size(D1',1),14)];
save('Xtest.mat', 'Xtest');
save('Ytest.mat', 'Ytest');