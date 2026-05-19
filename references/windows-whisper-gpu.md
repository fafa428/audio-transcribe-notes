# Windows faster-whisper GPU setup

Use this reference when setting up or debugging GPU transcription on Windows.

## Recommended versions

- Python: 3.11 64-bit. Avoid Python 3.13 for this workflow unless the installed wheel stack is known-good.
- `faster-whisper==1.2.1`
- `ctranslate2==4.5.0`
- `setuptools<81` because older CTranslate2 imports `pkg_resources`.
- CUDA Toolkit 12.x.
- cuDNN 9.x for CUDA 12. cuDNN 9.11 was verified in one Windows setup.

## Install commands

```powershell
cd D:\SXY\Whisper
py -3.11 -m venv .venv-whisper-gpu
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv-whisper-gpu\Scripts\Activate.ps1

Remove-Item Env:PIP_NO_INDEX -ErrorAction SilentlyContinue
Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue

python -m pip install -U pip wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install "setuptools<81" faster-whisper==1.2.1 ctranslate2==4.5.0 -i https://pypi.tuna.tsinghua.edu.cn/simple --prefer-binary
```

## cuDNN PATH

Download a Windows `cudnn-windows-x86_64-9.x.x.x_cuda12-archive.zip` from NVIDIA and extract it. Add the extracted `bin` folder and the CUDA Toolkit `bin` folder to `PATH` for the current PowerShell:

```powershell
$CUDNN_BIN = "D:\SXY\Whisper\cudnn\cudnn-windows-x86_64-9.11.1.4_cuda12-archive\bin"
$env:PATH = "$CUDNN_BIN;D:\App\NVIDIA GPU Computing Toolkit\CUDA\v12.2\bin;$env:PATH"
```

Verify:

```powershell
where cudnn64_9.dll
where cudnn_ops64_9.dll
where cublas64_12.dll
python -c "import ctranslate2; print(ctranslate2.__version__); print(ctranslate2.get_cuda_device_count()); print(ctranslate2.get_supported_compute_types('cuda'))"
```

Expected CUDA device count is at least `1`, and supported compute types should include `int8_float16`.

## Common failures

- `ModuleNotFoundError: No module named 'pkg_resources'`: install `setuptools<81`.
- `Could not locate cudnn_ops64_9.dll`: add the cuDNN `bin` folder to `PATH`.
- `Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor`: cuDNN DLL set is incomplete or mismatched; ensure all cuDNN 9 CUDA 12 DLLs are from the same archive.
- `Windows fatal exception: access violation` while loading model: use Python 3.11 and try `ctranslate2==4.5.0`; verify model hash and DLL versions.
- Long clip crashes but 60-second clip works: use chunked transcription and automatic bisection.

## Model files

Use faster-whisper converted models, not OpenAI `.pt` models. A local `large-v3` model directory should include:

```text
config.json
model.bin
preprocessor_config.json
tokenizer.json
vocabulary.json
```

For `Systran/faster-whisper-large-v3`, `model.bin` is 3,087,284,237 bytes and SHA256:

```text
69F74147E3334731BC3A76048724833325D2EC74642FB52620EDA87352E3D4F1
```
