# MECEE
Multi-round Error Correction with Ensemble Enhancement
## Data Description ##

| 文件名     | 内容 |每一行数据格式|行数|
| ----------- | ----------- |
| train_no_Aug.src      | 从数据集中得到的训练数据      |**id**\t**句子**|1000235|
| train_no_Aug.trg     | 从数据集中得到的标记数据      |**id**\t**句子**|1000235|
| train_Aug.src      | 从数据集中得到的训练数据和我们的增强数据       |**id**\t**句子**|1490918|
| train_Aug.trg      | 从数据集中得到的训练数据和我们的增强数据       |**id**\t**句子**|1490918|
| train_Aug.txt      | 数据集中不符合CSC任务的标记数据，作为我们增强数据的原始数据       |**句子**|1192788|
|augmentation.csv|增强数据|**id**\t**标签句子**\t**错误句子**|490685|
| val_1.src      | 处理后的验证集待修改的句子      |**id**\t**句子**|1000|
| val.lbl      | 处理后的验证集标签      |**句子id**, **错误字符1位置**, **正确字符1**, **错误字符2位置**, **正确字符2** ……  (如果是正确句子，则格式为**句子id**, 0)|1000|
| test_1.src      | 处理后的测试集      |**id**\t**句子**|15000|
| test.txt     | 处理后的测试集       |**句子**|15000|

lbl文件中，错误字符位置从1开始计算，不是从0开始。我们在model_integration.py中给出了construct_trg_file函数用来将trg文件转换为lbl文件，也提供了save_parallel_data.py文件用来将lbl文件转换为trg文件  
train_no_Aug.src和train_no_Aug.trg 文件中的每一行句子是一一对应的，train_Aug.src和train_Aug.trg 也是  
数据下载链接：  
链接：https://pan.baidu.com/s/15_K4IdxF7UGQau7tdxIZjw?pwd=0r4u  
提取码：0r4u  
模型数据代码下载链接：  
链接：https://pan.baidu.com/s/1zC3zn2vxL5HrMHl1Sa7Tvw?pwd=age6  
提取码：age6
  
## Data sets and data cleansing strategies ##
我们使用的数据集有**CGED,CTC2021,HSK,Lang8,MuCGEC,YACLC,SIGNHAN14,SIGNHAN15,hybrid,WANG27**数据集。  
我们对数据集进行了清洗，通过清洗的句子作为我们的训练数据，未通过清洗的句子的标记数据被我们用来作为我们数据增强的原始数据。  
数据清洗的策略分为两步：  
第一步，将数据全部转换为简体中文，并去除非中英文和数字字符  
第二步，检测标签的长度是否与原始句子的长度相同，并且检测是否存在不一样的中文字符以排除语序错误问题  
不符合要求的句子的标签保存为train_Aug.data用于数据增强  
最终有1000235句符合要求的句子和1192788句不符合要求的句子，最终使用了其中490685条句子用于数据增强
  
拼写任务数据生成策略使用了音似和形似混淆集替换，参数设置如下  

|   参数     |  参数值   |    参数说明    |
|:---------:|:---------:|:------------:|
|  prob_all |  0.05   | 句子中字符替换的比例 |
| pinyin_prob |  0.72       | 音似的替换比例 |
| shape_prob |   0.08       | 形似的替换比例 |
| random_prob | 0.2         | 随机的替换比例 |

在数据生成的过程中，我们利用生僻字、停用词等策略保证生成过程中操作的字符为中文且随机替换策略且不引入生僻字。  
```
python ./data_augmentation/data_generator.py --data_path ./data/train_Aug.txt --save_path ./data/augmentation.csv
```
## Code reproduction ##
我们一共训练了四种模型  
1，由train_no_Aug.src和train_no_Aug.trg训练得来。  
2，由train_Aug.src和train_Aug.trg训练得到  
3，先由train_Aug.src和train_Aug.trg训练一个epoch，再由train_no_Aug.src和train_no_Aug.trg训练得来  
4，先由train_no_Aug.src和train_no_Aug.trg训练，再在验证数据上微调10个epoch
我们的训练过程集成在pipeline.sh文件中  
## Model integration ##
我们最后通过不同的随机数种子，训练了两个模型1，一个模型2，四个模型3，一个模型4  
我们的集成策略为：  
给前三种不同的模型赋予不同的权重，若某一个模型对句子中的一个字符作出修改，则该字符的权重对应增加模型的权重，最终如果该字符的权重超过阈值，则保留该修改。  
在投票之后，得到的结果与模型4的结果进行集成。如果投票结果对字符有修改，则保留投票的结果，若投票结果无修改，模型4结果修改，也保留修改。
## Code repetition process ##
在配置好环境之后，将数据存放在data目录下，然后运行pipeline.sh和decode.sh来训练不同的模型  
最后运行model_intergration.sh来集成模型的结果
