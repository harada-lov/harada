document.addEventListener('DOMContentLoaded', () => {
    const binaryInput = document.getElementById('binaryInput');
    const runButton = document.getElementById('runButton');
    const status = document.getElementById('status');
    const titleButton = document.getElementById('titleButton');

    // --- タイトルクリック時の切り替え処理 ---
    titleButton.addEventListener('click', () => {
        // 背景のクラスを切り替え
        document.body.classList.toggle('dark-mode');

        // モードに合わせて「タイトル」「入力欄ヒント」「ボタン文字」を切り替え
        if (document.body.classList.contains('dark-mode')) {
            // Decryptionモード
            titleButton.innerText = 'Harada decryption';
            binaryInput.placeholder = 'Not Binary';
            runButton.innerText = 'Decrypt'; // ボタンをDecryptに変更
            binaryInput.value = '';
        } else {
            // Encryptionモード
            titleButton.innerText = 'Harada encryption';
            binaryInput.placeholder = 'Binary';
            runButton.innerText = 'Encrypt'; // ボタンをEncryptに戻す
            binaryInput.value = '';
        }
    });

    // --- 入力制限：Encryptionモードの時だけ「0と1」に制限する ---
    binaryInput.addEventListener('input', function() {
        if (!document.body.classList.contains('dark-mode')) {
            this.value = this.value.replace(/[^01]/g, '');
        }
    });

    // エンターキーで実行
    binaryInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            runButton.click();
        }
    });

    // --- 実行ボタンクリック時の処理 ---
    runButton.addEventListener('click', async () => {
        const val = binaryInput.value;
        if (!val) return alert("数値を入力してください");

        runButton.disabled = true;
        // 計算中の表示もモードによって変えるとさらに親切です
        const originalBtnText = runButton.innerText;
        runButton.innerText = "Processing...";
        status.innerHTML = "計算中...";

        try {
            const response = await fetch('http://127.0.0.1:5000/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ binary_str: val })
            });

            const data = await response.json();

            if (data.success) {
                status.innerHTML = `<strong></strong> ${data.x} <br><strong></strong> ${data.y}`;
            } else {
                status.textContent = "エラー: " + data.error;
            }
        } catch (err) {
            status.textContent = "サーバーに接続できません。PythonのFlaskを実行してください。";
        } finally {
            runButton.disabled = false;
            runButton.innerText = originalBtnText; // ボタンの文字を元に戻す
        }
    });
});
