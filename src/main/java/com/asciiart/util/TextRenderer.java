package com.asciiart.util;

import com.asciiart.model.CharacterSet;
import org.bytedeco.opencv.opencv_core.Mat;
import org.bytedeco.opencv.opencv_core.Rect;
import org.bytedeco.opencv.opencv_core.Scalar;
import org.bytedeco.opencv.global.opencv_core;


import java.awt.*;
import java.awt.image.BufferedImage;

public class TextRenderer {
    private final boolean color;
    private final String chars;
    private final Font font;
    // private final boolean isPortrait; // 未被实际使用，注释掉
    private final int cellWidth;
    private final int cellHeight;

    public TextRenderer(boolean color, String language, String customText) {
        this.color = color;
        this.chars = CharacterSet.getChars(language, customText);
        this.font = CharacterSet.getDefaultFont(language, language.equals("chinese") ? 12 : 12);
        // 动态测量字体实际宽高，保证紧凑且清晰
        BufferedImage tmpImg = new BufferedImage(1, 1, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = tmpImg.createGraphics();
        g2d.setFont(this.font);
        FontMetrics metrics = g2d.getFontMetrics();
        int realCellWidth = metrics.charWidth('江'); // 用常用汉字测量宽度
        int realCellHeight = metrics.getHeight();
        g2d.dispose();
        this.cellWidth = language.equals("chinese") ? realCellWidth : 8;
        this.cellHeight = language.equals("chinese") ? realCellHeight : 12;
    }

    public BufferedImage render(Mat image, int numColumns) {
        int cols = numColumns;
        int rows = image.rows() * cols / image.cols();
        int imgWidth = cols * cellWidth;
        int imgHeight = rows * cellHeight;

        BufferedImage result = new BufferedImage(imgWidth, imgHeight, color ? BufferedImage.TYPE_INT_RGB : BufferedImage.TYPE_BYTE_GRAY);
        Graphics2D g = result.createGraphics();
        g.setFont(font);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, imgWidth, imgHeight);

        int blockW = image.cols() / cols;
        int blockH = image.rows() / rows;

        for (int y = 0; y < rows; y++) {
            for (int x = 0; x < cols; x++) {
                int px = x * blockW;
                int py = y * blockH;
                int w = Math.min(blockW, image.cols() - px);
                int h = Math.min(blockH, image.rows() - py);
                Rect roi = new Rect(px, py, w, h);
                Scalar mean = opencv_core.mean(new Mat(image, roi));
                double brightness = mean.get(0) * 0.299 + mean.get(1) * 0.587 + mean.get(2) * 0.114; // 只用 mean，不用 Core
                int charIndex = (y * cols + x) % chars.length();
                char c = chars.charAt(charIndex);
                boolean isColor = false;
try {
    mean.get(2);
    isColor = true;
} catch (Exception e) {
    isColor = false;
}
if (color && isColor) {
                    Color colorVal = new Color((int)mean.get(0), (int)mean.get(1), (int)mean.get(2));
                    g.setColor(colorVal);
                } else {
                    int grayValue = 255 - (int)brightness;
                    g.setColor(new Color(grayValue, grayValue, grayValue));
                }
                int drawX = x * cellWidth;
                int drawY = y * cellHeight + cellHeight - 2;
                g.drawString(String.valueOf(c), drawX, drawY);
            }
        }
        g.dispose();
        return result;
    }
}
