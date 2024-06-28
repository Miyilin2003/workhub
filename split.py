import pandas as pd
from sklearn.model_selection import train_test_split

# 读取Excel文件
df = pd.read_excel('input.xlsx')

# 按分类进行分组
groups = df.groupby('company_area')

# 初始化列表存储分割后的数据
train_data = []
val_data = []
test_data = []

# 按照8:1:1的比例分割每个分类的数据
for name, group in groups:
    train, temp = train_test_split(group, test_size=0.2, random_state=42)
    val, test = train_test_split(temp, test_size=0.5, random_state=42)
    
    train_data.append(train)
    val_data.append(val)
    test_data.append(test)

# 合并所有分类的数据
train_data = pd.concat(train_data)
val_data = pd.concat(val_data)
test_data = pd.concat(test_data)

# 将数据写入文件
train_data.to_csv('cnews.train.txt', index=False, header=False, sep='\t')
val_data.to_csv('cnews.val.txt', index=False, header=False, sep='\t')
test_data.to_csv('cnews.test.txt', index=False, header=False, sep='\t')
