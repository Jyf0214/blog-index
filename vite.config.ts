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

              // 读取源目录并复制文件
              const files = await fs.readdir(sourceDir);
              for (const file of files) {
                const srcFile = path.resolve(sourceDir, file);
                const destFile = path.resolve(destDir, file);
                await fs.copyFile(srcFile, destFile);
                console.log(`Moved: ${file} -> ${destDir}`);
              }
            },
          },
        ],
      },
    },
  });
};