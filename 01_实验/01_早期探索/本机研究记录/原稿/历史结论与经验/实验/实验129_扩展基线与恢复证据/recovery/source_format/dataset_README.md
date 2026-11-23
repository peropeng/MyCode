---
dataset_info:
  features:
  - name: messages
    list:
    - name: content
      dtype: string
    - name: role
      dtype: string
  splits:
  - name: train.success.oss
    num_bytes: 31805636
    num_examples: 491
  download_size: 10379409
  dataset_size: 31805636
configs:
- config_name: default
  data_files:
  - split: train.success.oss
    path: data/train.success.oss-*
license: mit
---