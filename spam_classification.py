# -*- coding: utf-8 -*-
"""spam_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1inxJzzDTX5tSNxauJO5TnQI5F96vbNE2

# Import Libraries

Masukan library yang akan digunakan untuk menganalisa dataset dengan menggunakan metode Deep Learning
"""

# Commented out IPython magic to ensure Python compatibility.
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import wordcloud
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import LSTM, Activation, Dense, Dropout, Input, Embedding
from tensorflow.keras.layers import MaxPooling1D
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
# %matplotlib inline

"""## Load Dataset dengan Google Drive

Sambungkan google drive dengan import drive yang sudah terintregasi dengan Google Colaboratory. Kemudian, ekstraksi dataset format **.csv** dengan menggunakan library Pandas.
"""

from google.colab import drive
drive.mount('/content/drive')

spam_data = pd.read_csv('drive/My Drive/Dataset/spam_dataset.csv', delimiter=',', encoding='latin-1')
spam_data.head()

"""## Check data NaN

Sebelum dianalisa pastikan dataset harus diperiksa dengan **feature list** agar mengetahui apakah data sudah bersih atau masih kotor? Tidak semua, dataset bersih ada yang harus diperhatikan dalam menganalisa suatu data yaitu menghilangkan beberapa isi kolom dan baris dalam data.
"""

feat_list = list(spam_data.columns.values)

for feat in feat_list:
  print(feat, ': ',sum(pd.isnull(spam_data[feat])))

spam_data.isnull().any().sum()

"""Jumlah data NaN yang diketahui ada 3 label. Maka dari itu data NaN harus dihapus agar tidak terjadi noise pada dataset.

## Menghapus data NaN

Setelah mengatahui dataset yang berisikan **NaN** atau **Not a Number**. Maka, hilangkan data yang berisikan NaN tersebut agar memudahkan dalam menganalisa suatu data. Setelah menghapus data NaN, tahapan selanjutnya mengubah nama dataset tersebut berdasarkan kolom yang awalnya **v1** menjadi **label** dan **v2** menjadi **text**.
"""

spam_data.drop(['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], axis=1, inplace=True)
spam_data = spam_data.rename(columns={"v1":"label", "v2":"text"})
spam_data.info()

"""## Distribusi Target Data Variabel

Dalam dataset memiliki 4825 pada data pesan **Ham** dan 747 pada data pesan **Spam**.
"""

spam_data.describe()

spam_data.groupby('label').describe()

"""## Mengetahui Class Dataset

Dalam dataset ini, data SMS Spam harus menggunakan label class agar memudahkan dalam menganalisis suatu data. Ada berapa class dalam tiap data?
"""

spam_data.label.value_counts()

"""## Visualisasi Data

Setelah data dianalisa untuk mengetahui jumlah data yang akan dianalisis. Maka, lakukan visualisasi agar memudahkan dalam analisis data. Visualisasi yang dipakai menggunakan plot Bar yang terdapat dalam library **Seaborn** dan **Matplotlib**.
"""

sns.countplot(spam_data.label)
plt.xlabel('Label')
plt.title('Number of Ham and Spam Message')

"""Visualisasi diatas membuktikan bahwa label Ham memiliki nilai yang sangat tinggi dibandingkan dengan spam.

## Menambahkan Label Numberik pada Spam

Target data harus dalam bentuk numerik untuk model klasifikasi menggunakan metode Deep Learning.
"""

spam_data['spam'] = spam_data['label'].map( {'spam': 1, 'ham': 0} ).astype(int)
spam_data.head(20)

spam_data['length'] = spam_data['text'].apply(len)
spam_data.head(10)

"""## Gunakan Visualisasi WordCloud

Dalam kasus NLP atau Natural Language Processing, Wordcloud sangat membantu user untuk mengetahui kata-kata apa saja yang paling banyak dalam dataset tersebut. Apakah data Ham lebih banyak dibandingkan dengan Spam atau sebaliknya?
"""

data_ham  = spam_data[spam_data['spam'] == 0].copy()
data_spam = spam_data[spam_data['spam'] == 1].copy()

def show_wordcloud(data_spam_or_ham, title):
    text = ' '.join(data_spam_or_ham['text'].astype(str).tolist())
    stopwords = set(wordcloud.STOPWORDS)
    
    fig_wordcloud = wordcloud.WordCloud(stopwords=stopwords,background_color='lightgrey',
                    colormap='viridis', width=800, height=600).generate(text)
    
    plt.figure(figsize=(10,7), frameon=True)
    plt.imshow(fig_wordcloud)  
    plt.axis('off')
    plt.title(title, fontsize=20)
    plt.show()

show_wordcloud(spam_data, "Ham Messages")

show_wordcloud(spam_data, "Spam Messages")

"""Jika dilihat dari segi visualisasi *wordcloud* Ham dengan Spam. Ada beberapa kata-kata yang hampir sama dalam penyebutan text dan paling besar karena penyebutan kata tersebut sering dipakai.

Setelah mengetahui visualisasi text dengan library **WordCloud**. Maka tambahkan berapa jumlah text data pesan Spam pada pesan yang akan dianalisa.
"""

spam_data[spam_data.length == 200].text.iloc[0]

"""# Text Preprocessing

Pengolahan dasar untuk tugas NLP termasuk dalam konversi teks ke *lowercase* dan menghapuskan punctuation dan **stopwords**.
Step yang akan dijalankan, khususnya pada tugas Klasifikasi Teks, adalah:

*  **Tokenization**

Ayo mulai untuk analisa pesan text!.
"""

vocab_size = 500
oov_token = "<OOV>"
max_length = 250
embedding_dim = 25

encode = ({'ham': 0, 'spam': 1})
spam_data = spam_data.replace(encode)

spam_data.head()

X = spam_data['text']
y = spam_data['label']

le = LabelEncoder()
y = le.fit_transform(y)
y = y.reshape(-1,1)

"""## Tokenizer

Dalam kasus NLP, Tokenizer berguna untuk mengetahui teks yang akan dibaca berdasarkan jumlah kalimat atau kata-kata dalam data pesan tersebut.
"""

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(X)

X = tokenizer.texts_to_sequences(X)

X = np.array(X)
y = np.array(y)

X = pad_sequences(X, maxlen=max_length)

"""# Split the Data"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)

print('Data Train : {shape}'.format(shape=X_train.shape))
print('Data Test : {shape}'.format(shape=X_test.shape))
print('Data Train (label) : {shape}'.format(shape=y_train.shape))
print('Data Test (label) : {shape}'.format(shape=y_test.shape))

import keras.callbacks
from timeit import default_timer as timer

class TimingCallback(keras.callbacks.Callback):
    def __init__(self, logs={}):
        self.logs=[]
    def on_epoch_begin(self, epoch, logs={}):
        self.starttime = timer()
    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(timer()-self.starttime)

cb = TimingCallback()

"""# Recurrent Neural Network 

Setelah tahapan pembagian dataset langkah selanjutnya menggunakan metode RNN dengan layer LSTM (Long Short Time Memory). Kemudian, kompilasi model dengan optimasi menggunakan Adam atau RMSprop dan gunakan loss '**binary_crossentropy**' dikarenakan dataset memiliki 2 kelas.
"""

import tensorflow as tf

model = tf.keras.Sequential([
                             tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=250),
                             tf.keras.layers.MaxPooling1D(pool_size=2),
                             tf.keras.layers.Dense(64, activation='relu'),
                             tf.keras.layers.LSTM(64, dropout=0.4, recurrent_dropout=0.4),
                             tf.keras.layers.Dense(1, activation='sigmoid')
                             ])

model.summary()
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

EPOCHS = 10
BATCH_SIZE = 64

history = model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
                    validation_data=(X_test, y_test), validation_split=0.2,
                    callbacks=[EarlyStopping(monitor='val_loss', patience=5, min_delta=0.001), cb])

print(cb.logs)

print(sum(cb.logs))

"""## Evaluasi Model

Setelah menjalankan model fitting. Selanjutnya evaluasi model untuk melihat hasil akurasi dari model RNN tersebut.
"""

result = model.evaluate(X_test, y_test)
print('Test set')

loss = result[0]
accuracy = result[1]

print(f'Loss: {loss*100:.2f}%')
print(f'Accuracy: {accuracy*100:.2f}%')

"""## Visualisasi Plot Grafik Model

Setelah mengetahui hasil akurasi dan loss. Langkah selanjutnya adalah visualisasikan plot grafik apakah terjadi underfitting atau overfitting pada model tersebut.
"""

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(EPOCHS)

plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Train')
plt.plot(epochs_range, val_acc, label='Validation')
plt.legend(loc='lower right')
plt.title('Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Train')
plt.plot(epochs_range, val_loss, label='Validation')
plt.legend(loc='upper right')
plt.title('Loss')
plt.show()

"""# Prediksi Model Data

Setelah model berhasil dijalankan dan akurasi mendukung. Maka, gunakan prediksi teks apakah pesan tersebut mengandung spam atau tidak?
"""

def get_predictions(texts):
    texts = tokenizer.texts_to_sequences(texts)
    texts = sequence.pad_sequences(texts, maxlen=max_length)
    preds = model.predict(texts)
    if(preds[0] > 0.5):
        print("SPAM MESSAGE")
    else:
        print('NOT SPAM')

# Spam Message
texts=["Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005"]
get_predictions(texts)

#Not Spam Message
texts = ["Hi man, I was wondering if we can meet tomorrow."]
get_predictions(texts)