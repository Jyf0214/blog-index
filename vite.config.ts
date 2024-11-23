import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";
import path from "path";
import { defineConfig } from "vite";
import viteCompression from "vite-plugin-compression";
import eslintPlugin from "vite-plugin-eslint";
import { promises as fs } from "fs";

// https://vitejs.dev/config/
export default () => {
  return defineConfig({
    plugins: [vue(), vueJsx(), eslintPlugin(), viteCompression()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src/"),
      },
    },
    envDir: "./",
    build: {
      rollupOptions: {
        plugins: [
          {
            name: "move-files", // 自定义 Rollup 插件
            async generateBundle() {
              const sourceDir = path.resolve(__dirname, "src/assets");
              const destDir = path.resolve(__dirname, "dist/assets");

              // 确保目标目录存在
              await fs.mkdir(destDir, { recursive: true });

              // 递归移动文件
              async function moveFilesRecursive(src, dest) {
                const items = await fs.readdir(src, { withFileTypes: true });
                for (const item of items) {
                  const srcPath = path.resolve(src, item.name);
                  const destPath = path.resolve(dest, item.name);

                  if (item.isDirectory()) {
                    // 跳过 css 文件夹
                    if (item.name === "css") {
                      console.log(`Skipped folder: ${item.name}`);
                      continue;
                    }
                    // 如果是文件夹，递归创建目标文件夹并继续处理
                    await fs.mkdir(destPath, { recursive: true });
                    await moveFilesRecursive(srcPath, destPath);
                  } else {
                    // 如果是文件，直接复制
                    await fs.copyFile(srcPath, destPath);
                    console.log(`Moved: ${item.name} -> ${dest}`);
                  }
                }
              }

              // 执行文件移动
              await moveFilesRecursive(sourceDir, destDir);
            },
          },
        ],
      },
    },
  });
};