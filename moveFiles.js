const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const srcPath = path.join(__dirname, 'src');
const distPath = path.join(__dirname, 'dist');

// 确保 dist 目录存在
if (!fs.existsSync(distPath)) {
    fs.mkdirSync(distPath, { recursive: true });
}

// 复制图片文件到 assets 文件夹
execSync('cp -r src/assets/*.{svg,jpg,png,gif} dist/assets/ || true');

// 复制 JSON 和 JS 文件到 dist 根目录
execSync('cp -r *.json dist/ || true');
execSync('cp -r *.js dist/ || true');

// 函数：复制以 folk_ 开头的文件夹并重命名
function copyAndRenameFolders(src, dest, prefix) {
    fs.readdirSync(src).forEach(folder => {
        if (folder.startsWith(prefix)) {
            // 获取不带前缀的文件夹名
            const newFolderName = folder.slice(prefix.length);
            // 构建源文件夹和目标文件夹的完整路径
            const srcFolderFullPath = path.join(src, folder);
            const destFolderFullPath = path.join(dest, newFolderName);
            // 确保目标目录存在
            if (!fs.existsSync(destFolderFullPath)) {
                fs.mkdirSync(destFolderFullPath, { recursive: true });
            }
            // 复制文件夹内容到新位置
            execSync(`cp -r ${srcFolderFullPath}/. ${destFolderFullPath}/ || true`);
        }
    });
}

// 调用函数，复制以 folk_ 开头的文件夹到 dist 目录
copyAndRenameFolders(srcPath, distPath, 'folk_');

console.log('Files moved successfully!');
