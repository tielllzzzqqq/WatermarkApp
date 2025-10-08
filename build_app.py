#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
from pathlib import Path

def convert_svg_to_icns():
    """将SVG图标转换为ICNS格式"""
    print("正在将SVG图标转换为ICNS格式...")
    
    # 确保resources目录存在
    resources_dir = Path("resources")
    if not resources_dir.exists():
        print("Error: resources目录不存在")
        return False
    
    svg_path = resources_dir / "icon.svg"
    if not svg_path.exists():
        print(f"Error: 图标文件 {svg_path} 不存在")
        return False
    
    # 创建临时目录
    iconset_dir = resources_dir / "icon.iconset"
    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    iconset_dir.mkdir(exist_ok=True)
    
    # 使用Inkscape或其他工具将SVG转换为PNG
    # 注意：这需要安装Inkscape或其他SVG转换工具
    try:
        # 生成不同尺寸的图标
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            output_path = iconset_dir / f"icon_{size}x{size}.png"
            
            # 尝试使用Inkscape转换
            try:
                subprocess.run([
                    "inkscape", 
                    "--export-filename", str(output_path),
                    "--export-width", str(size),
                    "--export-height", str(size),
                    str(svg_path)
                ], check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                # 如果Inkscape不可用，尝试使用其他方法
                print("Inkscape不可用，尝试使用其他方法...")
                
                # 尝试使用cairosvg (需要先安装: pip install cairosvg)
                try:
                    import cairosvg
                    cairosvg.svg2png(url=str(svg_path), write_to=str(output_path), output_width=size, output_height=size)
                except ImportError:
                    print("Error: 无法转换SVG图标。请安装Inkscape或cairosvg。")
                    return False
            
            # 为macOS创建所需的图标命名格式
            shutil.copy(output_path, iconset_dir / f"icon_{size}x{size}.png")
            shutil.copy(output_path, iconset_dir / f"icon_{size}x{size}@2x.png")
        
        # 使用iconutil将iconset转换为icns (仅在macOS上可用)
        if sys.platform == 'darwin':
            subprocess.run(["iconutil", "-c", "icns", str(iconset_dir)], check=True)
            print(f"成功创建图标: {resources_dir}/icon.icns")
            return True
        else:
            print("Error: 只能在macOS上创建.icns文件")
            return False
            
    except Exception as e:
        print(f"转换图标时出错: {e}")
        return False
    finally:
        # 清理临时目录
        if iconset_dir.exists():
            shutil.rmtree(iconset_dir)
    
    return False

def build_app():
    """使用PyInstaller打包应用"""
    print("正在打包应用...")
    
    # 检查图标文件
    icon_path = Path("resources/icon.icns")
    if not icon_path.exists():
        if not convert_svg_to_icns():
            # 如果无法创建.icns文件，使用默认图标
            icon_path = None
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--name=WatermarkApp",
        "--windowed",
        "--onefile",
        "--clean",
    ]
    
    # 添加图标
    if icon_path and icon_path.exists():
        cmd.append(f"--icon={icon_path}")
    
    # 添加数据文件
    cmd.extend([
        "--add-data=resources:resources",
    ])
    
    # 添加主脚本
    cmd.append("main.py")
    
    # 执行打包命令
    try:
        subprocess.run(cmd, check=True)
        print("\n打包完成！")
        print(f"应用程序位于: {os.path.abspath('dist/WatermarkApp.app')}")
        return True
    except subprocess.SubprocessError as e:
        print(f"打包应用时出错: {e}")
        return False

def create_dmg():
    """创建DMG安装文件"""
    print("正在创建DMG安装文件...")
    
    app_path = Path("dist/WatermarkApp.app")
    if not app_path.exists():
        print("Error: 应用程序不存在，请先构建应用")
        return False
    
    # 优先使用 create-dmg；若不可用则回退到 hdiutil
    create_dmg_available = False
    try:
        subprocess.run(["create-dmg", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        create_dmg_available = True
    except Exception:
        create_dmg_available = False

    try:
        dmg_path = Path("dist/WatermarkApp.dmg")
        # 若已有旧DMG，先删除避免冲突
        if dmg_path.exists():
            try:
                dmg_path.unlink()
            except Exception:
                pass
        if create_dmg_available:
            print("使用 create-dmg 创建DMG...")
            subprocess.run([
                "create-dmg",
                "--volname", "WatermarkApp",
                "--volicon", "resources/icon.icns" if Path("resources/icon.icns").exists() else "",
                "--window-pos", "200", "100",
                "--window-size", "800", "500",
                "--icon-size", "100",
                "--icon", "WatermarkApp.app", "200", "200",
                "--hide-extension", "WatermarkApp.app",
                "--app-drop-link", "600", "200",
                str(dmg_path),
                str(app_path)
            ], check=True)
        else:
            print("未找到 create-dmg，使用 hdiutil 创建压缩DMG...")
            # hdiutil UDZO 压缩，简单直接
            subprocess.run([
                "hdiutil", "create",
                "-volname", "WatermarkApp",
                "-srcfolder", str(app_path),
                "-ov", "-format", "UDZO",
                str(dmg_path)
            ], check=True)
        print("\nDMG创建完成！")
        print(f"安装文件位于: {os.path.abspath(str(dmg_path))}")
        return True
    except subprocess.SubprocessError as e:
        print(f"create-dmg 创建失败，尝试使用 hdiutil 回退: {e}")
        try:
            dmg_path = Path("dist/WatermarkApp.dmg")
            if dmg_path.exists():
                try:
                    dmg_path.unlink()
                except Exception:
                    pass
            subprocess.run([
                "hdiutil", "create",
                "-volname", "WatermarkApp",
                "-srcfolder", str(app_path),
                "-ov", "-format", "UDZO",
                str(dmg_path)
            ], check=True)
            print("\nDMG回退创建完成！")
            print(f"安装文件位于: {os.path.abspath(str(dmg_path))}")
            return True
        except subprocess.SubprocessError as e2:
            print(f"创建DMG时出错（hdiutil 回退也失败）: {e2}")
            return False

if __name__ == "__main__":
    # 确保resources目录存在
    Path("resources").mkdir(exist_ok=True)
    
    # 构建应用
    if build_app():
        # 创建DMG
        create_dmg()