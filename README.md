# tasoller-ios-bridge

TASOLLERをiOSアプリで使用するためのツールです。\
M1 Mac macOS Ventura 13.5.2での動作確認済みです。

## 構成

![tasoller-ios-bridge drawio](https://github.com/PurplePalette/tasoller-ios-bridge/assets/16555696/6a7846f6-e1dc-448f-b86c-219142fec72c)

## 使い方

### 準備物

以下のものを用意する必要があります。

1. decrypted IPA(復号済みIPA)\
   入手する方法は大きく分けて3つあります。
   1. 自分で脱獄してdecrypted IPAを取得する
      [iGameGod](https://igamegod.app/)のダンプ機能が一番安定していると思います。
   2. decrypted IPA Storeから入手する
      安全性は保証されないので注意してください。\
      [ArmConverter](https://armconverter.com/decryptedappstore/jp)\
      [Decrypt.day](https://decrypt.day/)
   3. 暗号化されたIPAを復号する(動作せず)
      [appdecrypt](https://github.com/paradiseduo/appdecrypt)というSIPが有効化されたMac上で暗号化されたIPAを復号するツールもあるみたいですが、こちらの環境では動作しませんでした。\
      暗号化されたIPAはiTunesから取得できます。
2. TASOLLERのカスタムファームウェア\
   「TASOLLER Firmware, driver and chuniio for HID on V2.0 with AMD support!」を入手してください。\
   Cons\&Stuffで配布されています。chunithmチャンネルのピン留めされているメッセージにリンクがあります。\
   入手できたらTASOLLERにインストールしておいてください。
   AMDに対応していないCFWだとTASOLLERがMacで認識しませんでした。
3. Gitの実行環境\
   Gitをインストールしておいてください。\
   brew install git
4. Pythonの実行環境\
   3.9以上を推奨します。
5. poetryの実行環境\
   Pythonのパッケージ管理ツールであるpoetryをインストールしておいてください。\
   https://python-poetry.org/docs/
6. Node.jsの実行環境\
   node -v\
   v20.8.0
7. PlayCover\
   Apple Silicon製のMacでiOSアプリを動かすためのツールです。
   https://playcover.io/

### IPAの改造

decrypted IPAに[patch\_ipa](https://github.com/PurplePalette/patch_ipa)を使用してCydia SubstrateとFridaを組み込みます。

```bash
git clone git@github.com:PurplePalette/patch_ipa.git
cd patch_ipa
poetry install
poetry shell
python patch.py <decrypted IPAのパス> -c FridaGadget.config
```

patched.ipaが生成されたら、PlayCoverにインストールしてください。

### tasoller-ios-bridgeの導入

```bash
git clone git@github.com:PurplePalette/tasoller-ios-bridge.git
cd tasoller-ios-bridge
yarn install
yarn build
poetry install
poetry shell
```

### PlayCoverの設定

PlayCover上でアプリのアイコンを右クリックして、グラフィック設定を以下のように変更してください。\
適応解像度: 1080p\
アスペクト比: 16:9

### tasoller-ios-bridgeの実行

PlayCoverでアプリを起動します。\
TASOLLERをMacに接続し、次のコマンドを実行します。

```bash
python main.py
```

### オプションの詳細

```
usage: main.py [-h] [--frida-host FRIDA_HOST] [--frida-port FRIDA_PORT] [--base-color BASE_COLOR] [--bar-color BAR_COLOR] [--touch-color TOUCH_COLOR] [--touch-screen-x-area TOUCH_SCREEN_X_AREA] [--touch-screen-y TOUCH_SCREEN_Y] [--reverse]

optional arguments:
  -h, --help            show this help message and exit
  --frida-host FRIDA_HOST
                        Frida host(default: localhost)
  --frida-port FRIDA_PORT
                        Frida port(default: 27042)
  --base-color BASE_COLOR
                        TASOLLER LED color(r:g:b) when untouched(default: 16:00:16). Max: 255:255:255
  --bar-color BAR_COLOR
                        TASOLLER LED bar color(r:g:b) (default: 32:00:32). Max: 255:255:255
  --touch-color TOUCH_COLOR
                        TASOLLER LED color(r:g:b) when touched(default: 255:00:00). Max: 255:255:255
  --touch-screen-x-area TOUCH_SCREEN_X_AREA
                        Width of X coordinate of screen to touch(default: 200:1720)
  --touch-screen-y TOUCH_SCREEN_Y
                        Y coordinate of screen to touch(default: 800)
  --reverse             Reverse of touch screen(default: False)
```
