package com.asciiart.model;

import java.awt.*;

public class CharacterSet {
    private static final String ENGLISH_CHARS = "@%#*+=-:. ";
    private static final String CHINESE_CHARS = "江雪利编程艺术字图";

    public static String getChars(String language, String customText) {
        if (customText != null && !customText.isEmpty()) {
            return customText;
        }
        String lang = language.toLowerCase();
        if ("chinese".equals(lang)) {
            return CHINESE_CHARS;
        } else if ("english".equals(lang)) {
            return ENGLISH_CHARS;
        } else {
            return CHINESE_CHARS;
        }
    }

    public static Font getDefaultFont(String language, int size) {
        try {
            if (language.equalsIgnoreCase("chinese")) {
                String os = System.getProperty("os.name").toLowerCase();
                if (os.contains("mac")) {
                    // macOS: 优先苹方，再尝试黑体
                    String[] macFonts = {"/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc"};
                    for (String path : macFonts) {
                        java.io.File f = new java.io.File(path);
                        if (f.exists()) {
                            return Font.createFont(Font.TRUETYPE_FONT, f).deriveFont((float)size);
                        }
                    }
                } else if (os.contains("linux")) {
                    // Linux: 指定 simsun.ttf
                    java.io.File f = new java.io.File("/usr/share/fonts/chinese/simsun.ttf");
                    if (f.exists()) {
                        return Font.createFont(Font.TRUETYPE_FONT, f).deriveFont((float)size);
                    }
                }
                // 兜底：用宋体名字（部分系统可识别）
                return new Font("SimSun", Font.PLAIN, size);
            } else {
                return new Font("Monospaced", Font.PLAIN, size);
            }
        } catch (Exception e) {
            // 兜底：用默认字体
            return new Font("Monospaced", Font.PLAIN, size);
        }
    }
}
