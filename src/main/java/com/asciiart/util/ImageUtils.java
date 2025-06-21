package com.asciiart.util;

import org.bytedeco.opencv.opencv_core.Mat;

import org.bytedeco.opencv.global.opencv_core;
import org.bytedeco.opencv.global.opencv_imgcodecs;
import org.bytedeco.opencv.global.opencv_imgproc;

import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;

public class ImageUtils {
    // Bytedeco 不需要手动 loadLibrary，自动加载 native
    

    public static Mat loadImage(String path, boolean color) {
        Mat image = opencv_imgcodecs.imread(path);
        if (image.empty()) {
            throw new RuntimeException("无法加载图片: " + path);
        }
        if (!color) {
            opencv_imgproc.cvtColor(image, image, opencv_imgproc.COLOR_BGR2GRAY);
        }
        return image;
    }

    public static BufferedImage matToBufferedImage(Mat mat) {
        int type = mat.channels() > 1 ? BufferedImage.TYPE_3BYTE_BGR : BufferedImage.TYPE_BYTE_GRAY;
        BufferedImage image = new BufferedImage(mat.cols(), mat.rows(), type);
        byte[] data = ((DataBufferByte) image.getRaster().getDataBuffer()).getData();
        mat.data().get(data);
        return image;
    }

    public static void rotateIfNeeded(Mat image, boolean isPortrait) {
        if (isPortrait && image.cols() > image.rows()) {
            opencv_core.rotate(image, image, opencv_core.ROTATE_90_CLOCKWISE);
        }
    }
}
