const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const distAssetsPath = path.join(__dirname, 'dist', 'assets');
const distPath = path.join(__dirname, 'dist');

// 创建 assets 文件夹
if (!fs.existsSync(distAssetsPath)) {
    fs.mkdirSync(distAssetsPath, { recursive: true });
}

// 复制图片文件到 assets 文件夹
execSync('cp -r src/assets/*.{svg,jpg,png,gif} dist/assets/ || true');

// 复制 JSON 和 JS 文件到 dist 根目录
execSync('cp -r *.json dist/ || true');
execSync('cp -r *.js dist/ || true');

console.log('Files moved successfully!');