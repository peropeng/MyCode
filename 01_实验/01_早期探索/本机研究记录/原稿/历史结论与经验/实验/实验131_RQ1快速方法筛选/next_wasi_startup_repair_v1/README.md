# WASI 运行时资产准备

固定两资产已核对原始字节数和 SHA256，并安全解包到本执行 worktree 的 `scratch/exp131/wasi_runtime/`：Wasmtime 49.0.0 Windows wheel 与 Brett Cannon 发布的 CPython WASI 3.13.15 / SDK24。下载及解包共6.969s；下载22107246B，解包62085629B，均在600s / 100MB边界内。559个文件的路径、类型、大小、CRC和完整SHA均已检查，无符号链接或越界成员。

目标目录中的 Wasmtime Python binding 导入成功，17个静态API的签名和源码已保存在 `runtime_metadata.json`。只改了该检查进程的 `sys.path`，未安装包或修改既有venv、系统、WSL、Docker和网络服务。本版只读目录映射接口为 `WasiConfig.preopen_dir(path, guest_path, fs_mutable=False)`。

CPython资产包含29250800B的 `python.wasm` 与515个stdlib文件，模块8字节头仅作静态读取。未构造Config、Engine、Store、Module、Linker或WasiConfig，未解析、编译、实例化或执行任何WASM / guest程序；未读取真实P0源码、Gold或模型。

两个逐资产receipt保存固定origin、下载hash、目标目录与全部成员hash；原始压缩包和解包结果留在scratch，不进入普通git。这个阶段仅说明资产和静态binding可用，不能证明隔离行为或科学观察有效。后续纯合成测试及真实代码执行需另行前瞻合同。旧科学资产保持原样，最新方法结果仍为P8 AB22/32；RQ1继续，RQ2暂停。
