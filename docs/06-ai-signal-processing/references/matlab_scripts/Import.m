clc;clear;tic
% Read data from two separate EMG files
folderPath = 'D:\EMG - Muscle Faritue\Project3\Data\Fatigue\Sujet_5';

% Lấy danh sách các file trong thư mục
fileList = dir(fullfile(folderPath, '*.csv'));

Fs = 2000;
windowSize = 2000; % Kích thước cửa sổ
overlap = 0; % Độ chồng lắp giữa các cửa sổ
nfft = 2^nextpow2(windowSize); % Kích thước FFT (có thể là lũy thừa của 2 gần nhất)

for i = 1:length(fileList)
    fileName = fullfile(folderPath, fileList(i).name);
    table =   readtable(fileName);
    emg_file = table2array(table(:,2:65));
    selection = true(1, size(emg_file, 2));
    
for e = 1:size(emg_file, 2)
     if all(emg_file(:,e) == 0);
         selection(e) = false;  % đánh dấu cột không có giá trị
     end
    end
    EMG = emg_file(:,selection);
 for j = 1:size(EMG,2);
            %Time feature
            rms1(j) = rms(EMG(:,j));
            mav1(j) = mean(abs(EMG(:,j)));
            skewness1(j) = skewness(EMG(:,j));
            kurtosis1(j) = kurtosis(EMG(:,j));
            max1(j) = max(EMG(:,j));
            min1(j) = min(EMG(:,j));
            std1(j) = std(EMG(:,j));
            mean1(j) = mean(EMG(:,j));
            %Frequency feature
            EMG_fft1 = fft(EMG(:,j), nfft);
            EMG_PSD1 = abs(EMG_fft1).^2/nfft;
            spectral_min1(j) = min(EMG_PSD1);
            spectral_max1(j) = max(EMG_PSD1);
            spectral_std1(j) = std(EMG_PSD1);
            mdf1(j) = medfreq(EMG(:,j) ,Fs);
            mnf1(j) = meanfreq(EMG(:,j),Fs);
            %Spectral Entropy
            se1(j) = se(EMG(:,j));
 end
            data1_rms{i} = rms1;
            data1_mav{i} = mav1;
            data1_skewness{i} = skewness1;
            data1_kurtosis{i} = kurtosis1;
            data1_max{i} = max1;
            data1_min{i} = min1;
            data1_std{i} = std1;
            data1_mean{i} = mean1;
            data1_spectral_min{i} = spectral_min1;
            data1_spectral_max{i} = spectral_max1;
            data1_spectral_std{i} = spectral_std1;
            data1_mdf{i} = mdf1;
            data1_mnf{i} = mnf1;
            data1_se{i} = se1;
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


% Combine features and labels into a matrix
Subject1_F = [A1' A2' A3' A4' A5' A6' A7' A8' A9' A10' A11' A12' A13' A14'];
save('Subject1_F', 'Subject1_F');
toc