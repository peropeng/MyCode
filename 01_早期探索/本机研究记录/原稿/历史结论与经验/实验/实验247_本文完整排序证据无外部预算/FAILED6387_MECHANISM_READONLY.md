# 6387：公开失败机制与下一项通用改进

前三步的主要缺口是跨文件接口没有补全。排名前三的合法编辑均位于 `models.py`；现有关系检索虽然在第二、三步提到了 `responses.py`，给出的却只有第 6 行 import，没有给出 `CloudFrontResponse.create_invalidation` 的当前函数体。第四步首次纳入该文件的真实编辑及当前上下文后，模型修正了 XML 解析层到 backend 之间的嵌套容器接口，实际公开 G/O 随后全部通过。这支持该补丁解决了本题的公开失败；不能据此断言“多尝试一次”或某个新检索策略已经普遍优于 Agentless。

本分析仅使用原前三次请求/响应、原公开 native 结果、真实公开编辑、当前业务源码，以及新增第四步请求/补丁和公开验收记录。没有读取 private/Gold，也没有执行新的模型请求或测试。共同前瞻比较仍固定五题，本文件只诊断其中的 6387，不改变分母。

## 实际发生了什么

| 步骤 | 直接排序证据 | 实际补充源码 | 生成与公开结果 |
|---|---|---|---|
| 1 | `models.py`，原 step 15 | backend 方法 349–364 行，687 字节；5 条关系 | 声称当前代码已正确，返回空 edits；未形成候选 |
| 2 | 再加入 `models.py`，step 28 | 上述方法 + `responses.py:6` import，共 746 字节；10 条关系 | 再次声称当前已通过，返回空 edits；未形成候选 |
| 3 | 再加入 `models.py`，step 20 | 与第二步相同的两个源码片段、10 条关系 | 增加 `Invalidation.__init__` 对非 dict 参数的兼容；O PASS，G 仍 FAIL |
| 4 | 加入 `responses.py`，step 16 | 该编辑的 before/after/current 对照直接覆盖当前 79–143 行，包含请求解析与 backend 调用 | 提取 `Paths.Items.Path`、统一为 list，再包装成 backend 需要的 dict；G/O 实际全 PASS |

前三步实际输入分别为 142503、144544、145800 tokens；第四步为 155630。前三次没有调用已经开放的当前源码读取工具。关系上下文只用了几百字节，因此不能把本次缺口归因于 32 KiB 附加上下文上限不够。

完整公共历史中仍可能存在该文件的历史片段，所有合法业务源码也可通过 reader 读取。因此准确说法是“聚焦检索没有提供关键调用者的当前接口”，不是“模型完全没有权限或任何途径看到该文件”。

## 容器层级为什么错

公开失败明确给出：期望 `Items=['/path1','/path2']、Quantity=2`，实际为 `Items=['Path']、Quantity=1`。业务源码能解释这个结果：

```text
XML 解析结果：Paths = {Items: {Path: [实际路径…]}, Quantity: …}
responses.create_invalidation：直接把整个 Paths 传给 backend
backend.create_invalidation：paths.get("Items") 得到 {Path: […]}，仍是 dict
Invalidation.__init__：继续保留这个 dict 为 self.paths
模板：len(dict) == 1；遍历 dict 得到键 "Path"
```

第三步只处理了最外层 `paths` 是 dict 还是 list，没有展开内层 `Items.Path`，所以没有改变这个失败机制。模型前三次的解释还把真实当前 C0 失败说成“历史已拒绝状态”，把“被接纳为 incumbent”误读为“目标测试已通过”；实际上共同 C0 证据清楚表明 G FAIL、O PASS。接受合法状态与取得恢复进展是两件事。

真实编辑顺序也支持这一解释：合法编辑排序为 `models.py` 的 step 15、28、20，然后才是 `responses.py` 的 step 16、21。step 16 的 after-image包含内层 `Items.Path` 规范化；step 21 后来删除了这段规范化，当前 C0 正是删除后的版本。第四步的 `after_current_diff` 因而已揭示缺失的规范化，即使尚未把第五条编辑作为直接证据。第四步补丁重新建立了与当前 backend 匹配的容器接口，而不是机械地把整个文件回滚。

这能定位一个具体的公开机制缺口，但本分析没有读取责任 Gold，不能据此把 RQ1 排序的责任预测准确率判为错误。

## 为什么已有 closure 没补到接口

三次输入中的 `public_business_frames=[]`、`public_missing_attributes=[]`、`fallback_to_ranked_only=true` 完全相同。失败发生在测试的值断言与断言库中，没有可用的业务异常栈帧。因此只把“失败业务 frame”置顶，对本例不会产生新锚点。

`relations240.Index.visit_Call` 将 `self.backend.create_invalidation(...)` 记成未限定的 `create_invalidation`；`build` 又明确排除无法精确匹配类名的限定方法，源码注释说明未实现 receiver type inference。实际上当前业务源码已给出 `backend(self) -> CloudFrontBackend`，这条可解析的类型证据没有进入索引。于是 backend 方法与 response 调用者之间没有连边。

现有源码还只从当前 anchors 构造一轮 provider→consumer 关系，再提取消费者的包围函数；被提取的函数并不会继续作为方法接口向上追索调用者。Python AST 索引也没有把模板字符串中的 `invalidation.paths` 当成 Python 属性消费者。前三步的 10 条关系集中在 `Invalidation → backend 构造调用` 和 `CloudFrontBackend → import`，并不等于完整的解析→backend→对象→模板数据通路。

## SET 接纳第三步、最终却选 C0，是规则的预期结果

本题初始目标 PASS 集为空。第三步 O 全 PASS，候选的目标 PASS 集仍为空，因此 `F ⊆ PASS(candidate)` 成立，候选被接纳为可继续搜索的状态，但没有新增任何保护目标，也没有减少失败数。

最终选择只在覆盖最终 frontier 的已观察快照中，依次最小化“公开失败数、改动行数、尝试编号”。旧路径中 C0 的键是 `(1,0,0)`，第三步候选是 `(1,5,3)`，所以选择 C0。不能把“SET accepted”当作修复成功，也不能把最终回退误解为丢弃已经取得的目标 PASS。

第四步 G/O 实际全 PASS 后，frontier 扩大为该 G 节点，C0 和第三步均不再覆盖 frontier；原规则已自然选定第四步快照 `c496fbb2ed8a82044ded3857e68476070381edf4ab8c01b2b301c8e0155cad2d`。独立保留性终验由 Root 对这份冻结源码执行，本分析不预判或读取其结果。

## 建议的一项通用改进：类型可解析的调用者补全

保留 RQ1 的根证据排序与 SET/普通行为保护。改变附加证据检索单元：对已选中的业务定义，优先补全“调用者实际传参 → 被调方法实际消费”的接口片段，再考虑扩大到下一个独立排名根。

具体可固定为一个可审计规则：从当前根及其已找到的包围方法出发，仅用当前源码中明确的 import、参数类型、`@property` 返回注解解析 receiver；对可唯一绑定的方法迭代反向补全调用者，直到没有新节点，或到达无法解析的接口边界。先呈现最近的传参/消费接口，再呈现更远的关系；在原附加上下文上限内按整函数选取片段，未呈现项列入可读取清单，不静默截断。并附带与这些函数范围相交的真实历史编辑对照。历史编辑保留原 RQ1 顺序，不按本题结果重新打分；无法唯一绑定的 receiver 记为未知，不能仅靠同名方法虚构关系，也不宣称得到完整动态因果图。

本例 `backend -> CloudFrontBackend` 的返回注解已经足以把 backend 的 `create_invalidation` 连接到 `responses.py` 的真实调用处。由此可在已有根的接口补全中取回这个函数及其被删除的规范化，而不必先消耗三个高度重叠的 `models.py` 前缀。它增加的是一条有源码依据的关系和必要接口证据，不是增加相同证据上的 seed 重采样。

该机制相对 Agentless 的潜在价值是减少定位与补丁尝试：RQ1 提供修复根，跨文件接口补全提供具体的传参与消费约束，而非依赖扩大文件范围或增加候选数量来碰到正确组合。这个优势目前只是待验证假设，不能写成已超过 AL 的结论。

验证应先做无 API 的源码覆盖审计，确认规则确实补到缺失调用者且没有引入无关大范围扩展；再固定版本，用未参与规则开发的失败样例做小规模前瞻验证。比较时保持调用数、seed、模型、G/O/独立终验和分母一致，报告首次 PASS 所需调用及成本。第四步同时改变了证据、当前反馈和阶段 seed，不能把这一次成功当作该新规则的受控消融。对完全相同且已结算的请求继续复用，不反复重跑已完成的相同输入。

证据文件、SHA 与事实/推断区分见同目录 `FAILED6387_MECHANISM_READONLY.json`。相关实现位置：原 `ranked_repair240.py:191,294,448,466`，`relations240.py:69,140,151,173`，`progress_guard240.py:122`。
