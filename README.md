# Sakuard Homebrew Tap

```sh
brew install Sakuard/tap/tbx
```

升級：

```sh
brew update
brew upgrade tbx
```

`tbx --version` 自 toolbox v0.1.1 起提供。

## 一鍵更新

到本 repo 的 **Actions → Update toolbox → Run workflow**，保留 main 並按執行，不用填版本或修改配方。

workflow 自動取得 toolbox 最新正式 Release，驗證 SHA-256，更新 `Formula/tbx.rb`，實際安裝並執行 `brew test`，成功後直接 commit 回 main。已是最新版就不修改；下載或測試失敗不提交。失敗後可再次按同一按鈕重試。

使用本 repo 內建 GITHUB_TOKEN，不需額外 secret 或跨 repo token。workflow 必須先合併 main，且 repo 政策需允許 Actions 寫入 main。沒有排程，也不會建立更新 PR。

`tbx.rb` 跟隨正式版；`tbx@0.1.0.rb` 保留歷史固定版。

toolbox 的版本分支合併發版流程見[發版指南](https://github.com/Sakuard/toolbox/blob/main/docs/releasing.md)。

## 維護者測試

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```

`bash scripts/test-install.sh` 會建立本機 tap 並安裝套件，主要供乾淨的 CI runner 使用。
