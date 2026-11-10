import requests
import tarfile
import io
import os
import shutil

url = "https://registry.npmjs.org/npm/-/npm-10.8.2.tgz"
print("Downloading npm tarball from npmjs.org...")
r = requests.get(url, timeout=30)
print(f"Downloaded {len(r.content)} bytes. Extracting...")

target = r"C:\Users\himad\AppData\Local\Programs\nodejs"
node_modules = os.path.join(target, "node_modules")
os.makedirs(node_modules, exist_ok=True)

with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
    tar.extractall(path=node_modules)

pkg_dir = os.path.join(node_modules, "package")
npm_dir = os.path.join(node_modules, "npm")
if os.path.exists(npm_dir):
    shutil.rmtree(npm_dir)
os.rename(pkg_dir, npm_dir)

npm_cmd_content = (
    "@ECHO off\r\n"
    "\"%~dp0node.exe\" \"%~dp0node_modules\\npm\\bin\\npm-cli.js\" %*\r\n"
)
npx_cmd_content = (
    "@ECHO off\r\n"
    "\"%~dp0node.exe\" \"%~dp0node_modules\\npm\\bin\\npx-cli.js\" %*\r\n"
)

with open(os.path.join(target, "npm.cmd"), "w", encoding="utf-8") as f:
    f.write(npm_cmd_content)

with open(os.path.join(target, "npx.cmd"), "w", encoding="utf-8") as f:
    f.write(npx_cmd_content)

print("NPM and NPX installation successfully completed!")
