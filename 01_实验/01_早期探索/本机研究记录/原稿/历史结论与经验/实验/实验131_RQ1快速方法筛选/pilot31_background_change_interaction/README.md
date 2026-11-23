# P31 原执行窗口：训练前超时

原目标为 UTC20:24。公开特征于20:18:02准备完成，几何与新全局head梯度检查通过；完整源码审查于20:25:00才完成，因此原窗口没有冻结协议、读取私有Gold或启动正式训练。`pretraining_budget_stop.json`永久记录预算失败1、有效新模型0、准确率为空。这不是方法性能结果。

科学设计是同一编码器的背景E0与Joint变化x按坐标乘积，以及x²控制；E0含原task/rawrole和空字段，不代表正常状态。原P29全局linear控制保持同一x/C与1024维ridge profile；原72行无Gold公开scores/orders精确复现。原preflight保存实际执行的runner643b7a版本；随后仅增加冻结/启动/FIT入口时限保护和说明文字，精确v1保留在draft_sources，增补receipt与独立审查记录差异。原preflight和首版审查未覆盖。

公开输入与raw背景产品在四个`shared_public_feature_archive.zip.partNNN`中。按receipt顺序拼接并验证ZIP SHA，再解压、核对两member SHA。`raw_background_products.pt`为156,243,276字节，原文件仍留在此执行目录并由`.gitignore`排除；private输入与共享ZIP仍留在owned scratch。仓库交付的是可逐字节恢复的分片，不含Gold或pycache。压缩归档在原超时之后创建，未伪称时限前完成。

后续`pilot31_background_change_interaction_recovery`是同算法第一次正式训练的独立工程恢复窗口，原20:24未达事实不变。恢复结果单独保存；本目录不将恢复准确率算作原窗口完成。
